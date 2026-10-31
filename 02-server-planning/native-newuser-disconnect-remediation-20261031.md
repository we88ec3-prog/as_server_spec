# DEV-040-NATIVE 原版創角送出後 TCP 斷線：根因、修正設計與開發交接
2026-10-31｜只分析與規劃，Server/資料庫/原始 Client 不修改，不建立 Git branch。

## 0. 固定基線與證據分級
Spec main: 6bab003c38ade6122b72adc7a71309ca1d53630c。Server main（唯讀）: ad84f9fb11606a318aff6bd67e065aa0ee07cc45。使用者上傳 Asgard.exe SHA256 = db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145（本輪已與檔案實際 hash 核對一致）。Profile TW-seed0-local-v0.1。
使用者觀察原版創角畫面有 ID/PASSWORD/CONFIRM/NAME/E-MAIL，按送出後看到「連線中斷，您要重新連線嗎？」。這是 user-observed；**沒有本次現場 TCP capture**，不可因訊息就判斷帳密錯誤，或斷線必在 C02 後。

## 1. Server 原始碼已確認的斷線路徑（source-confirmed）

|順序|來源與方法|證據|結論|
|---|---|---|---|
|1|src/Asgard.Server.Host/LoginWireSession.cs, HandleAsync 的 case 0x02 / case 0x04（約 198–202）|不管身份、C02 欄位、連線 state，直接 return Close()；Close() 回 0 frames / CloseConnection=true，**沒有 S02、沒有 AuthenticateAsync、沒有 BeginDraftAsync**|只要 packet 進入這兩個 case，Server 必定主動終止連線。最可能造成這次提示；仍需實機確認這個 packet 是否到達|
|2|src/Asgard.Server.Host/GameTcpProbeService.cs, HandleClientAsync（約 133–150）|AA frame→TwSeed0PacketCodec.Decode→HandleAsync→先寫 replies 再檢查 reply.CloseConnection；true 則 return，using TcpClient 結束|能確認 Server 在收到 C02/C04 時的 TCP close 路徑|
|3|LoginWireSession.cs, case 0x15（約 204–211）|RequireEncrypted、C15 body=0 後同樣 return Close()；**未呼叫 CancelDraftAsync**|若 Client 在 S02(nonzero) 後送 C15，Server 亦會關線；不能倒果為因假定之前就是錯密|
|4|src/Asgard.Server.Application/CharacterCreationAccountGuard.cs, RequireMatch / AuthenticatedCharacterCreation.BeginFromClientAsync|要求非 null loggedIn、generation 不為空、同名；不驗本次 C02 password|與獨立創角規則衝突；**當前 live C02 直接 Close，尚未進此 Guard**，不能把它稱作已證本次立即斷線的呼叫點|
|5|LoginWireSession.cs catch InvalidOperationException/InvalidDataException/WorldRecoveryConflictException...|錯序或無效 frame 也可 Close；default unsupported opcode Close|可能有 C02 以前的封包、region、TCP framing 或 phase 問題|
|6|GameTcpProbeService.cs Accept/Read loop|最多 32 active sockets，60s idle timeout（WorldLoading 20s），ReadAsync=0 / IOException / SocketException / cancel 都退出，部分僅 Debug；另若 server 未啟動、埠被佔用也不能正常握手|如果 C02 根本未到達，優先排除這些前置/Socket 問題；不能歸因帳密|
|7|src/Asgard.Server.Protocol/TwCharacterPackets.cs|DecodeC02(region 2..4 = 四個 string8+u8，其他 region = 三個 string8)、DecodeC04 五個 u8、EncodeS02 status+string8 **已存在但 live Host 不呼叫**|codec 可重用，缺的是原生 routing、region、auth、state、回覆|

本地 C03 LoginFailure 使用 S02 status=3 和自訂文字，**絕非 NewUser 的「密碼錯」已證原生錯誤碼**。Client 已證部分非零狀態只顯示 focus 差異，不得偷渡錯誤原因語意。

## 2. 斷點分類（需要實機驗證、非 source-confirmed 本次 packet）

- **H0：C02 前**：Client 本地 UI gate（ID 長度、CONFIRM、NAME/E-MAIL、最後確認）、TCP 前置協定或 timeout。必須同時查 Client 發包和 Server last decoded opcode/phase。
- **H1：C02 後未收 S02**：符合現有 case0x02 的明確 close 路徑。若此時 socket 沒有任何 S02，帳號/密碼根本尚未被查 DB。
- **H2：已收第一 S02(0)、C04 後斷**：符合 case0x04，但**此版 Server 沒有生成創角第一 S02(0)**，需核對是否連到不同 Server binary/其他程序/測試注入。
- **H3：收到 S02(nonzero) → 原版 Client 發 C15 → 關線**：需要先確認非零 S02 實際從哪裡發出，C15 不是密碼錯證據。
- **H4：未收完整合法 AA frame/未知 opcode/peer close/idle/DB exception**：另列 protocol/timeout/peer/exception 類別，不以創角錯誤覆蓋。

後續 Server diagnostic 設計：每 socket 使用 traceId+connectionId、stage、direction/opcode/body_len/region、close_reason（explicit-close, protocol, idle, peer, exception）、回覆 opcode/status、匿名化帳號識別與時間戳。嚴禁寫入明文帳密、EMAIL、CONFIRM、C02 解密 body、hash、token。不同 C02 收送步驟可對照去敏 Wireshark/loopback packet capture 與原 Client 錄影；本次未實際對使用者本機 Server 進行 live capture。

## 3. 已證 Client I/O 與表單未知
依 A-021/027/028 original-BIN observed-static：
- C02 writer 0x574170 / 0x5742B0..0x574352；NewUser Dialog+0x26C → field1、+0x270 → field2；+0x274 是與第二欄比較的暫存字串，**不單獨成為 C02 前兩欄之外的確認欄**。field1 帳號、field2 密碼、+0x274 CONFIRM 為**高可信推論，不是原版欄位標籤或官方語意證實**。
- Region 2..4 為 field1, field2, field3, field4 四個 string8 + u8；其餘 region 三個 string8；region4 的額外 UI widget IDs 0x17/0x18，其他非零地域 0x0F/0x10，region0 第三欄受 ID0x0A 條件影響；**region1 UI 分支與 serializer 不一致**。
- **NAME 的真實來源與 E-MAIL 是否必填，尚未證實**。C04 只有 sex/hair/RGB 五個 u8，無名稱；必須明確證實角色 NAME 在 C02 哪欄／何處，不能猜 field3 或 field4 就是 NAME/E-MAIL。若 E-MAIL 空值使 Client 本地不發 C02，這是 H0，不是 Server 驗證失敗。若有欄位但不存 DB，必須等 Client gate 和產品必要性確認才定型。
- A-003/A-027：原始 Client 地區非 0 時第一欄疑似最低 12（0x91FED0 的本地字串長度 gate），region0 跳過；Admin 帳號允許 3..32 ASCII。兩者可能有**原生 UI 長度不相容**，待 region/profile 實機定位，不可擅自改 Client 或 Admin 帳號政策。
- C02 送出使 Client local state0x1D；此階段 S02(status0)→Client 送 C04 五u8、state0x1E；再 S02(status0)→0x4B206B 本地完成 UI，並**不直接送 C03/S03**。S02(status!=0) → status focus/display、發 C15（encrypted empty body）、state0x1F。已證 status 3/4/18/26/31 focus 第一欄、17 focus 第二欄；**未知對應「帳號不存在/密碼錯/重名」的真正 code**。C15 回覆/連線保持/再次提交、成功 UI 返回登入都待實機 A-028/A-030。
- Client packet 所載是否能覆蓋使用者看到的全部五個表單欄位，各版本 UI 的可選/必填、EMAIL 是否參與 Account 身份驗證，不得以 UI 數量推斷。帳號僅由 Admin 建立，不讓 C02 INSERT Account。

## 4. 交付開發的正常流程（設計，不是已實作）

1. 原版 Client NewUser 獨立入口，完成合法前置 handshake（但**不要求 C03 / LoginSession**），C02 body 按已確認的 region 解析；若不能確認 region/欄位角色，正式 native gate 仍 fail-closed。
2. 以本次 C02 的 **existing Account 名稱＋密碼**呼叫現有 IAccountAuthenticator/Account Store，比對 PBKDF2、停權、原生帳密限制；不創建 Account，不用 ID 字串當作已驗證 owner。per-account/IP 限流，未知帳號與錯密統一公共錯誤。
3. 成功驗證且確認無既存角色、NAME 來源合法後，建立 connection/generation/account_id/credential_version/TTL 綁定的 **creation-only proof** 和 PendingCharacterIntent（不核發 login/WorldGrant）；角色名稱合法性和唯一性檢查不依賴 Client 的本地 gate。現存 IAccountAuthenticator.AuthenticateAsync 回 AccountIdentity **沒有 credential_version**；現有帳號表已有 version，可延伸唯讀驗證結果或其他 fence，不需預設 DB schema 改動。
4. 已有證據支持第一段 **S02(status0,string8)** 通知 Client 繼續（先驗 proof 再送），Client 應進 C04/0x1E。不能將這第一段成功當已保存角色。
5. C04 由同條已驗證 connection 的 pending intent 綁定原 Name/Owner；校驗 five u8 appearance、同一版本/世代/有效時間、角色名/owner 唯一性，單次 DB transaction 保存 Character+Appearance+onboarding進度。
6. DB transaction commit 成功後才送第二段 S02(status0,string8)，Client 走原生 UI 完成，而非直接 S03；登入仍從獨立 Client C03 入口完成。
7. C15(empty) 只取消同 connection/account/generation **未提交** pending，不能撤銷已提交角色；無合法 pending 的 C15 安全拒絕／按已證 native flow 管理 socket，不讓它取消他人 draft。
8. C02 重送同 intent 不得重建；C04 同 intent + same body 的重送/回包丟失，可返回已提交結果，不第二次 INSERT；不同 body/跨 connection/過期拒絕；斷線後未提交 draft TTL 清理，新的連線必須重新 C02 認證。已 commit 但第二 S02 遺失，重登入應取得既有角色，不能回滾已完成角色。
9. **錯密/未知/停權/重名/已有角色/非法資料**：不建立 Account/Character/不合法 draft/proof，不發成功 S02；優先使用原版已證的 S02 非零 + message 和 C15 UI 流程，不直接當普通 TCP failure。若**尚未證實某種 native S02 對應**，保留安全拒絕與分類診斷，但不能冒稱 Client 可顯示該錯誤、也不能隨便猜 status3。

## 5. 必須調整的私有 Server 模組與方法（本次只列設計，不改）

|工作|路徑／方法|設計修正|
|---|---|---|
|DEV-CREATE-01|src/Asgard.Server.Host/LoginWireSession.cs / HandleAsync cases 0x02,0x04,0x15, Respond/Close|不再對合法 C02/C04 無條件關線，獨立 C02 Auth→proof→S02→C04 commit→S02；處理 C15、失敗映射與連線階段|
|DEV-CREATE-02|src/Asgard.Server.Host/GameTcpProbeService.cs / HandleClientAsync|去敏 traceId/close reason、讀取時序、timeout/Socket peer/error 分類；原生成功及業務錯誤與 protocol-fatal 分開|
|DEV-CREATE-03|src/Asgard.Server.Application/CharacterCreationAccountGuard.cs / RequireMatch, AuthenticatedCharacterCreation.BeginFromClientAsync|把 loggedIn 前置條件換成本次 C02 已驗證 Account/credential 的 creation-only proof，**不能只刪 null guard**|
|DEV-CREATE-04|src/Asgard.Server.Application/LoginConversation.cs / LoginPhase|增加獨立 NewUser 的 phase/state，不混淆 C03 LoginReady 和 WorldGranted；保留握手安全限制|
|DEV-CREATE-05|src/Asgard.Server.Protocol/TwCharacterPackets.cs / DecodeC02, DecodeC04, EncodeS02, IsEmptyC15|沿用已證 codec；實際 Region/profile 選取、NAME/EMAIL 欄位證據和錯誤 status 解碼；不發自造 opcode|
|DEV-CREATE-06|src/Asgard.Server.Application/AccountContracts.cs IAccountAuthenticator + src/Asgard.Server.Infrastructure/SqliteAccountStore.cs / PostgresAccountStore.cs AuthenticateAsync|重用同一帳密資料庫、停權/限流；讀取已有 credential_version 供 creation proof fence；不新建 Account、不變更 DB schema|
|DEV-CREATE-07|src/Asgard.Server.Application/CharacterContracts.cs ICharacterCreationStore + CreationAuthProof/PendingCharacterIntent（新增設計）|owner proof 獨立於 C03 已登入 Session，保留 account_id/credential_version/connection/generation/TTL|
|DEV-CREATE-08|src/Asgard.Server.Infrastructure/CharacterCreationStore.cs / BeginDraftAsync, CompleteDraftAsync, CancelDraftAsync, VerifyOwnerAsync|保留已有一帳一角/normalized_name 唯一、5min draft、DB 原子提交、舊 C15 不撤銷已 commit；需要名稱來源已證，勿擅改 SQL|
|DEV-CREATE-09|src/Asgard.Server.Host/Program.cs / DI/config|視驗證充分的原生 region/profile 逐步啟用 native NewUser，預設未知 fail-closed|
|DEV-CREATE-10|tests + tools|SQLite/PostgreSQL 合成與原版 Asgard.exe GUI E2E 分開驗收|

**產品不需重新決定**：創角和登入獨立；Admin 建 Account；創角直接以 C02 身份/密碼驗證；失敗不得建角；成功後按原版 UI 回登入；不改 Asgard.exe。**待 A-030 實證後可能需要決策**：原版 E-MAIL 若必填要不要保存（本次要求不修改 DB，候選設計可只接收相容 UI 輸入而不持久保存），原版非 region0 第一欄最低 12 的限制是否要配合管理端開新帳號規則。除此之外沒有需要現在重問的決策。

## 6. 優先順序與退出條件

|順序|工作|驗收標準|
|---|---|---|
|P0-0|Baseline trace: 誰關 TCP、C02 前後或 C04 後|能從去敏 trace 及 Client UI 定位 H0/H1/H2/H3，不能只截圖；先排除跑到其他 Server|
|P0-1|A-021/027/028/020 增量 + A-030|有 Region/Name/EMAIL 對照、E-MAIL 必填 gate、可用 native S02 非零顯示/取消/重試、C15 後 UI 與成功回登入證據；沒找到就標 unknown|
|P0-2|DEV-CREATE-01..04 正確 Auth+state|未 C03 且本次正確 C02 帳密可產 creation-only proof；錯密/停權無 draft/角色、Socket 不因普通拒絕被當網路錯誤|
|P0-3|DEV-CREATE-05..08 C04 commit/recovery|S02(stage1)→C04→atomic commit→S02(stage2)，重送/斷線/C15/超時/重登入無重複角|
|P0-4|Client E2E + error negative|原版直接創角成功可回登入，錯密/未知/停權/重名依 Client 支援的失敗顯示；合成與原版 CT 不混用|

原始碼分析不能代表已完成 Server 修正，所有後續 Server 功能修改必須**先向使用者確認實作範圍**。詳細 A-030 / CT-103..105 見同批新增文件。
