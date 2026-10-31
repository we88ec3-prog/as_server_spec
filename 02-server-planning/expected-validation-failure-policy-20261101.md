# ADR-009／R-036：預期內驗證失敗應回覆原生錯誤而非直接斷線；驗證原因必須留 Log
2026-11-01｜**使用者已決定的 Server 行為政策（designed）**；適用 ONB-01～07、後續所有世界/任務/戰鬥/物品/交易/API 及其他業務驗證。**本次只更新 as_server_spec/main，未修改 as_server_roy 或 Asgard.exe。**

## 1. 現況稽核（來源：as_server_roy/main@71ebd25954386609fa224f3267f7ae5942fd0354）
- `src/Asgard.Server.Host/LoginWireSession.cs`：C02 認證失敗回 `Close("native-c02-credential-rejected-no-verified-s02-error")`，`CharacterCreationDeniedException`／`CharacterCreationConflictException` 也回 `Close(...)`；C04 沒 pending 直接 Close；合法 C15 取消 pending 後亦 Close。上述 `Close` 代表零個 S2C frame、`CloseConnection=true`，TCP loop 寫完（如有）即結束。
- 一般 C03 密碼錯／未知帳號、限流，已回 `S02`／不關閉 socket，但 Host 尚未依驗證結果記錄結構化 `reason_code`，只有 request/response packet meta。
- `GameTcpDiagnosticJournal` 新增的 `[PACKET]`、`[UNEXPECTED_PACKET]` 主要是 opcode、長度、階段和 handler 分類。**不能把 `recognized-close`、`handled`、`expected` 當已記錄「密碼錯／同名／停權」原因**。
- 此源碼現況只證明 Server 的實作，不代表原版 Client GUI 已驗證；原版 C02/S02/C15 目前仍欠 A-030/CT-104～105/107 的動態證據。

## 2. 強制的錯誤分類與回覆策略
**預設：業務驗證失敗是可預期結果，不可直接 Close TCP。** 連線建立中的禁止存取、輸入不合條件、角色重名、缺錢、背包空間、移動被擋、任務條件不符、技能無效／冷卻、隊伍邀請拒絕等：均不應被視為協定異常。應原生回覆並保持（或按原生證據安全回復）相應階段；不可由「失敗」直接推斷要踢玩家。

|分類|範例|Server 操作|記錄|
|---|---|---|---|
|`EXPECTED_VALIDATION_FAILURE`|C02 錯帳密／停權／重名；C04 外觀無效；正常 C03 認證失敗；技能 CD／無目標；NPC 任務未滿足；背包不足|不提交任何被拒絕的資料或獎勵，**發送該 Client profile 已證可理解的失敗 S2C**，保留連線與可重試階段；取消 pending 要冪等|`[VALIDATION_FAILED]`（非 `[UNEXPECTED_PACKET]`）|
|`EXPECTED_CLIENT_CANCEL`|合法 C15、Client 主動取消任務或交易|撤銷本次未提交意圖，不把「取消」視為連線錯誤；同連線是否重開表單按原生 UI/封包實證實作|`[REQUEST_CANCELLED]` 可選或 `[VALIDATION_FAILED]` **不得當成驗證失敗**|
|`PROTOCOL_UNEXPECTED`|未知 opcode、不合法 framing/length、完全錯序的封包、錯誤加密/序號|明確區分是否 Client/Server profile 不相容；視風險拒絕／結束 socket，不亂送原生未知封包|`[UNEXPECTED_PACKET]` + `close_reason`|
|`SECURITY_FATAL`|Grant 竄改／重播，跨帳號套用 proof，權限偽造，超出限流安全閾值，惡意/反覆異常|保護身份及資料的 **fail closed**、必要時終止連線，與一般輸錯密碼分離|`[SECURITY_REJECTED]` 或 `[UNEXPECTED_PACKET]`；去敏原因|
|`TRANSPORT_FATAL`|socket EOF、嚴重 AA codec 錯誤、Server 無法安全恢復之 IO/DB 故障、timeout|可斷線並留完整分類/錯誤階段，不宣稱 Client 有顯示業務錯誤|`[TCP_CLOSE]`／異常原因|

`EXPECTED_VALIDATION_FAILURE` 的前提是**此情境為正規功能驗證，且失敗有合法 Client 接收路徑**。對尚無已證原生錯誤映射的功能：在安全上維持拒絕，不發成功包、不臆造 status/opcode；標記 `NATIVE_ERROR_MAPPING_UNVERIFIED` 作為 **待修補的相容缺口**，不把暫時安全關閉列為 R-036 已完成。應先交 A 分析＋DEV 共同追正確回覆，完成前不開放正式 native 功能。不可採用無回覆永久卡住的無限等待假解法。

**安全優先，但不能無差別踢線：** 密碼錯第一次、輸入名稱重複、餘額不足是正常失敗；持續暴力破解到超過安全閾值或跨帳號竄改是另外一個可關閉的安全情境。客戶端公開文字統一或最小化（避免列舉帳號），內部 reason_code 可以更精確但不包含玩家輸入值。

## 3. C02／C04／C15 正式規劃流程
```text
Native NewUser C02 (ID, PASSWORD, NAME, E-MAIL, region-tail)
   → verified region/codec + existing Account/password/status/name checks
   ├─ success:
   │    creation-only proof + pending intent
   │    → S02(status0,string8) → Client C04
   │       ├─ C04/DB transaction success → final S02(status0,string8)
   │       │    → ADR-008 原版自動 World 轉場（不人工再次登入）
   │       └─ EXPECTED C04 rejection → S02(verified nonzero status, verified text)
   │            → native Client failure UI/C15 or retry (依原版實證)
   └─ EXPECTED C02 rejection:
         no proof/character/e-mail/World grant
         → S02(verified nonzero status, verified error text)
         → original Client renders error → possible C15(empty)
         → Server clears only this socket's uncommitted pending
         → resume/retry/explicit peer-close according to observed native transition
```
- `S02(status!=0,string8)` **原生格式及部分 Client UI / C15 靜態分支已有證據**；真正「帳密錯／停權／重名／外觀不合法」應用哪個 status、文字顯示行為、C15 後能否在同一 socket 立即再 C02，**仍未經原版 GUI／去敏 trace 核定**。不得套用普通 C03 自訂 `status=3`，不能自造 code。
- `C15` 是原版非零 S02 分支的後續候選 Client 事件，**不是所有失敗都一定送 C15**。伺服器應允許驗證過的合法 C15 清理而不當作攻擊或無條件終止連線；若原版之後自動關 TCP，這是正常 peer close，應和 Server 主動 Close 分開。
- C02 不要求先手動登入 C03；不得 Client 自建 Account；只能用本次帳密驗證 existing Account 並建 creation-only proof。S02(0) 只在身份／條件成功後發；C04 原子提交 `creation_email`。
- 需要獨立的 `NewUserPending`／`NewUserRejectedAwaitC15`／`NewUserRetryReady` 等**Server 設計狀態（名稱非原版 enum）**，與既存 `LoginReady` 和 ADR-008 的 `PostCreateEntryContext` 區分。Client 原生重試路徑未證前，只預留結構，不假設重送次序。

## 4. 全功能適用的診斷事件（Server 實作要求）
每次業務驗證拒絕都必須**額外**記錄一筆受控的結構化 `[VALIDATION_FAILED]`（或等價 JSONL event，不能僅靠封包回應／連線 close 推知）：
- `at_utc`、`trace_id`、`build`、`direction=C2S`、`opcode`、`stage`、`phase_before/after`、`validation_domain`（AUTH/CHAR/WORLD/MOVE/SKILL/QUEST/ITEM/TRADE/...）、`reason_code`（穩定、非自由文字）、`classification=EXPECTED_VALIDATION_FAILURE`、`connection_action=keep-open|client-normal-close|safety-close`。
- `s2c_opcode`、`s2c_status`（**只有已驗證原生碼**）、`response_sent`、`client_profile`、`native_mapping_state=verified|unverified`，必要時 `safe_retry_phase`、`retry_allowed`，與同 TraceId 的 `[PACKET]`／`[TCP_CLOSE]` 相關聯。
- 推薦固定 reason_code（非原服 enum）：`AUTH_INVALID_CREDENTIALS`、`AUTH_ACCOUNT_INACTIVE`、`AUTH_RATE_LIMIT`、`CHAR_NAME_TAKEN`、`CHAR_ALREADY_EXISTS`、`CHAR_APPEARANCE_INVALID`、`CHAR_CREATION_PROOF_EXPIRED`、`WORLD_MAP_ENTRY_DENIED`、`MOVE_BLOCKED`、`SKILL_COOLDOWN`、`QUEST_PRECONDITION`、`ITEM_CAPACITY` 等。例外至少給型別族群及呼叫點／對應拒絕碼；切勿將所有 Exception 攤平成 `invalid-native-protocol-or-state`。
- 不記帳密、帳號／角色原名、E-MAIL、原封包 decoded body、grant/token、SQL／敏感 exception.Message、玩家自由文字。不能把輸入文字塞進 `reason_code` 或 Log 模板。可留匿名 TraceId。
- `[UNEXPECTED_PACKET]` 專用於未預期或異常封包，不應因 `reply.CloseConnection` 就自動把正常驗證拒絕算作異常。`expected rejected` 在 console 可以 warning/info，但仍清楚標記類別，能依 reason_code 查找。

範例（全為設計示例，**不表示已找到可用原生錯誤 status**）：
```text
[PACKET] C2S trace=... op=0x02 phase=LoginReady
[VALIDATION_FAILED] trace=... domain=AUTH reason=AUTH_INVALID_CREDENTIALS classification=EXPECTED_VALIDATION_FAILURE native_mapping=unverified response_sent=false connection_action=safety-close
[VALIDATION_FAILED] trace=... domain=CHAR reason=CHAR_NAME_TAKEN classification=EXPECTED_VALIDATION_FAILURE native_mapping=verified s2c_op=0x02 s2c_status=<verified> response_sent=true connection_action=keep-open
[UNEXPECTED_PACKET] trace=... op=0xFE reason=unknown-opcode
```
前例 `safety-close` 只描述**映射尚缺的現況/暫行安全拒絕**，不得作為 R-036 的通過情境；真正 Native 完成時應看到 `response_sent=true`、Client UI 可見、按原生流程重試。

## 5. 開發切片（所有狀態先規劃、未實作）
|工作|元件|內容|
|---|---|---|
|**DEV-REJECT-01**|Host `LoginWireSession.cs` + `LoginConversation.cs`|把返回值從只有 `Frames/CloseConnection/CloseReason` 擴成可描述 `Success/BusinessRejected/Cancelled/ProtocolRejected/SecurityRejected` 的結果；不要用 `Close()` 同時表達無帳密與 malformed packet。異常分類在處理器內輸出固定拒絕碼；保留正常 C03 不斷線錯密模式|
|**DEV-REJECT-02**|Application `IndependentCharacterCreation` + Auth/Character Store|C02 失敗、角色重複、停權/重送/外觀無效返回安全的 domain rejection，原子回滾，無 pending／Committed 汙染；外部共用訊息防帳號列舉|
|**DEV-REJECT-03**|Protocol `TwCharacterPackets.cs` + profile response registry|原版已證 S02 `status+string8`；建立按 region/Client state/error kind 的 **verified-only** 錯誤映射；尚未證 status 不能直接啟用。擴充其他功能時依各自 native S2C 進行，不一律發 S02|
|**DEV-REJECT-04**|Host `GameTcpProbeService.cs` / `GameTcpDiagnosticJournal.cs` / `GamePacketExpectation.cs`|在 C2S→Domain rejection→S2C 或 Close 的單一 TraceId 下寫 `[VALIDATION_FAILED]` + stable reason，將業務拒絕和 Unknown opcode 分開；確認順序、一次失敗一次事件及無敏感資料|
|**DEV-REJECT-05**|Auth、World、Scene、Combat、Quest、Inventory、Trade 等各域|逐功能盤點正常失敗情境，與自定義重試狀態、原生 Client 可懂的 S2C 綁定；預期內失敗無法靠泛用 `Close()` 混過驗收|
|**DEV-REJECT-06**|Test / native Client CT|增加 reason_code/safe retry/peer socket/無部分提交/無資訊洩漏測試，附每種原生 UI 的錄影或去敏封包 evidence|

## 6. 動態分析與驗收責任
- **A-030 + A-028（優先）**：Region2/3/4 真實 `S02(status!=0,string8)` UI 顯示/focus、錯密／重名／停權／C04 拒絕候選碼、S02 後是否每次發 C15(empty)，C15 後 TCP 是否保留、可否在同連線重新 C02，還有第二段 S02 失敗分支。A-027 針對 native 帳號欄與 UI 限制補證；C26/一般登入則 A-029/A-002。
- **原 Client CT-112**：C02 錯密、帳號不存在/停權、重名/C04 不合法 → S02 已證非零顯示 → Client C15/cancel/retry → 無 Server 主動踢線；同 socket 再試成功（**若原版支援；否則要記錄實際合法 socket 切換並經驗收**），DB 沒有新增角色、creation_email 沒有錯寫。
- **CT-113**：C03 錯密、一般輸入檢查、其他 Domain 正常拒絕皆須結構化 `reason_code`，不出現 `[UNEXPECTED_PACKET]`；真正 malformed/竄改/過量重試按嚴重級別關閉，日誌準確；多種 DB provider、重送、併發、重登、隱私掃描。
- **出場門檻**：新政策 **已規劃，不代表 Server 已實作，也不代表 status/native GUI 已通過**；規格原生 CT 仍 `planned/not-run`。不得把無證錯碼或「不關 socket 但 Client 永遠無提示」視為功能完成。

## 7. 與現有決策一致
ADR-008 創角成功直接進 World 維持不變。C02 失敗應停留／回到原版可重試的 NewUser 流程而非自動登入或直接給 World grant；錯誤後不能建立 character 或 Account。多人共圖、Server 權威、原版 Client 不修改、不另建 branch，保持不變。

## 2026-11-01 逐包日誌實作回補與分工註記

此前在 `as_server_roy/main` 先實作的 C2S/S2C metadata `[PACKET]`／`[UNEXPECTED_PACKET]` 已獨立登記成 [R-037](game-packet-log-contract-and-backfill-20261101.md) 與 CT-114。此文件 R-036 專門規範**正常驗證拒絕的內部原因**及可回復的原生失敗回覆；兩者不能互相取代。私有 Server 較新版本可能已有 `[VALIDATION_FAILED]` 來源碼，仍不可宣稱原版 UI/CT 已通過。本分析角色之後不可直接修改 Server 程式，僅研究與規劃。
