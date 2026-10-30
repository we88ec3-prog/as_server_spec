# A-002 — roy1 / 重複登入、斷線與跨 TCP 交接（BIN-first）

- 日期：2026-10-31；Client：原版 Asgard.exe（PE32/x86，ImageBase 0x400000）
- SHA256：db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145；profile：TW-seed0-local-v0.1
- 新證據 ID：ev_a002_20261031_asgard_login_transfer_static；方法：objdump -D -M intel 原始 BIN 與前述 profile 的對照。
- **分析結果：integrated / handoff_status=partial / implementation_ready=true / native_client_validation=not-run。** 部分原服政策未知不是「缺少實機所以分析失敗」。

## 1. 已核對的原版 Client 函式與資料流（observed-static）

| VA | 觀察 | Server 使用方式 |
|---|---|---|
| 0x573060 | C03 constructor 將 opcode=0x03 傳給 0x578600 | C03 Login 原生物件 |
| 0x573110..0x573152 | 依次用 0x45B1B0 寫 +0x18/+0x218 兩個 string8，0x45AB00 寫 +0x22A 一個 u8 | body = string8 account, string8 password, u8 flag |
| 0x4A7D10..0x4A7DE2 | Login UI 控制 2/3；拷貝輸入至 C03 +0x24/+0x224，設 +0x236 flag 後呼叫 0x5788A0 送包 | UI 複製上限 0xC/0x8 不等於完整 wire 欄位位元組上限 |
| 0x57DBC0..0x57DBDE | S02 parser：讀 u8 status、string8 message | 登入失敗與建角 UI 共用 S02 型別，錯誤語意需要依情境區分 |
| 0x588610 | S03 constructor opcode=0x03（方向 S2C） | 與 C03 同 opcode 但不同方向 |
| 0x5886C0..0x5886F0 | S03 先 read32 至 +0x18、read16 至 +0x1C、read8 至 +0x1E，再依長度 raw read 到 +0x1F | S03 = BE u32 address, BE u16 port, u8 token_length, raw token bytes |
| 0x4A8370..0x4A8698 | S03 交接 handler 對 region 3/4 分支；讀 S03 callback +0x24 addr、+0x28 port、+0x2A token_len、+0x2B token | 設目標 host/port（0x53B300）、連線（0x53B360），複製 token 至 C10 再發包 |
| 0x577330 | C10 constructor opcode=0x10 | World 連線第一階段的 token |
| 0x5773E0..0x5773EE | C10 serializer 按 +0x18 長度將 +0x19 起資料交給 0x45B4C0 | **C10 body = raw token；沒有額外 u8 長度前綴** |
| 0x45B4C0..0x45B50E | raw memory writer：複製指定長度而不加入 size 前綴 | C10 不可當 string8 |
| 0x53C460 | 發送端依原始 profile 將 opcode 0x10 當明文例外 | C10 plain opcode+raw token，無 wire ordinal |

注意：packet +0x0C 的 this/subobject 調整，使 serializer 的 S03 +0x18/+0x1C/+0x1E/+0x1F 對應 callback 的 +0x24/+0x28/+0x2A/+0x2B，**不是兩種不同封包**。C03 的 +0x18/+0x218/+0x22A 與 UI 的 +0x24/+0x224/+0x236 同理。

### 對 A-022 已發現的位址誤標（需修訂）

先前 A-022 報告把 0x4A8370 稱為 C25 region3/4 Metadata 入口。現在沿 0x5886C0 S03 parser 的 addr/port/token 資料流及 0x577330 C10 constructor 驗證，**0x4A8370 實為 S03 交接處理 handler**，不能引用它證明 C25 的欄位。此交叉修正同步記錄於 A-022 分析與 PKT-C25，防止 Server 把 S03 的 host/token 誤塞進 C25。

## 2. 已有 profile 的正常/錯密資訊（prior evidence）

04-analysis-integration/profile-login.md 記錄台灣版 seed0 既有人工測試：raw greeting → C62 → C00/S00 → metadata/list → C03；錯密回 S02(status=3,string8 message) 可重試，成功回 S03 並經新的 World TCP 連線送 C10。這**不是本輪重新執行的 runtime 驗收**；S02 status3 的已知登入畫面含義不能延伸到重複登入、停權或 MakeInfoDialog。

原版 C03 沒有 server-side request_id、session generation；S03 token 長度以 u8 表示但 token 本身為 opaque bytes。原專案示範 token 24 bytes / 60 秒與單一 local World endpoint 是 designed fixture，不是原伺服器已證實的限制。

## 3. 原服重複登入政策仍 unknown，不能從 Client 靜態推論

EXE 可以證明有 S02/S03 及切換連線能力，**無法證明原伺服器收到第二個合法 C03 時究竟踢舊、拒絕新、容許多人，或者使用哪個非零 S02 狀態**。目前無原版 Server 處理程式或兩 Client 捕獲；這是 protocol-policy 的 unknown，而不是讓 A 停工的理由。**不得猜測重複登入一定是 status=某數字**。

## 4. 已交付的 Server 相容策略（designed；不宣稱原服）

採用「一帳號最多一個有效 World generation、合法新登入取代舊 generation」（latest authenticated wins）。只有通過帳密/停權/角色所有權驗證後才能生成新 generation；錯密絕不能撤銷現有玩家。之後由 Auth/Session 原子生成 Grant(account_id,character_id,generation,destination,deadline,nonce)，以 Server 自己的 opaque token 透過 S03 發出，所有 token 原文禁止記錄。

狀態流：Connected → Handshake → VersionReady → LoginReady → C03（合法）→ Authenticated(generation) → S03 GrantIssued → TransferPending → 新 TCP 送 raw C10 → AtomicConsumeGrant → WorldBound(generation) → C25 → Loading → InWorld。

**重要：Login TCP 關閉不能直接撤銷 TransferPending 的合法 grant**。Client 正常轉服會建立新 TCP；若在舊登入 socket 關閉時清 token，將可能必定轉服失敗。grant 到期、被新 generation 取代、或安全撤銷時才不可兌換。World C10 的 token consume 必須原子，只能成功一次；其 owner、character、destination 和 generation 由 Server token mapping 決定，不額外新增 Client wire 欄位。

同帳號兩連線競爭使用 transaction/CAS 推進 generation；新世代成功後舊 socket 命令與舊 token 必須失效。舊 World disconnect 清理需以 account+generation+connection_id 比對，不能刪除新世代的連線/角色；關服或重啟使 volatile grants 失效，角色/背包/教程進度持久資料不回滾。若以後實測證明原版採「拒絕新登入」，可把 duplicate policy 切換 reject-new，但**不能憑想像補 S02 原生錯誤碼**。

## 5. 情境與預期（全部屬 designed，除標明 prior evidence）

| 情境 | 確定或設計結果 | 測試 |
|---|---|---|
| 正確 C03，已有角色 | 發 S03，token 所屬帳號/角色/World 固定 | CT-037 |
| 錯密重試 | prior evidence 為 S02 status3；舊有效 World 不受失敗認證影響 | CT-037 |
| 原版 Client 換 TCP，登入 socket 先結束 | 短效 grant 應在期限內可供 World C10 兌換 | CT-037 |
| C10 token 過期/重用/跨角色/跨 World | 不能建立 World entity，不能修改角色 | CT-015/037 |
| 兩個有效 C03 競爭 | 原子 generation，只有最新仍有效（designed） | CT-038 |
| 舊 World 延遲封包/斷線回呼 | 必須以舊 generation 拒絕，不能清掉新連線 | CT-038 |
| S03 回包丟失 | grant 到期並要求再認證，不暴露舊 token | CT-037 |
| C10 兌換後斷線 | 不能重用 consumed token；必要時重新登入/恢復 | CT-037 |
| 交接進行中 Server crash | 清除 volatile grant/ghost；持久角色/背包狀態不重複 | CT-017 |
| C10 前提前 C25 | 明確拒絕未綁定 World session 的遊戲指令 | CT-011/037 |

## 6. 交付、驗證與未知

- 可直接交 DEV：C03/S02/S03/C10 codec、S03→C10 的 raw token 交接、Auth 代際狀態機、原子 grant、斷線/併發安全邊界。Domain 不直接信任任何 C03 flag，只有合法登入才有 World grant。
- tools/a002_session_model.py 為**設計級合成測試**，涵蓋錯密、World 綁定、跨 owner、重放、斷線、generation、過期與 crash；不宣稱實作了真 Server/Client。
- CT-037、CT-038 在 vectors.json 登記 planned / native_client_validation=not-run；未經實機不可標 passed。
- 待續靜態/原服資料：原伺服器的 duplicate error/status，登入各 status 的 UI 提示、region 非3/4 的 S03 callback、C03 flag 真正語意與原始 Server timeout。移交相關 A-016、A-020 及後續 DEV/CT/BUG。

## 7. 重現命令

sha256sum Asgard.exe
objdump -D -M intel --start-address=0x573060 --stop-address=0x573155 Asgard.exe
objdump -D -M intel --start-address=0x4a7d10 --stop-address=0x4a7e09 Asgard.exe
objdump -D -M intel --start-address=0x57dbc0 --stop-address=0x57dbe0 Asgard.exe
objdump -D -M intel --start-address=0x588610 --stop-address=0x5886f1 Asgard.exe
objdump -D -M intel --start-address=0x4a8370 --stop-address=0x4a8699 Asgard.exe
objdump -D -M intel --start-address=0x577330 --stop-address=0x5773f0 Asgard.exe
objdump -D -M intel --start-address=0x45b4c0 --stop-address=0x45b50f Asgard.exe
python3 tools/a002_session_model.py

只共享去識別分析與合成測試；不提交 EXE、私密帳密、token、原始 dump。
