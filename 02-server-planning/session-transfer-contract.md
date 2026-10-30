# A-002：登入／跨 TCP 的 Server 開發契約（2026-10-31）

目標 Client：`Asgard.exe`，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；R-025 僅管理員創建帳號、玩家原 Client 登入。本頁將 [A-002 的靜態 Client 證據](../03-analysis-requests/A-002-roy1-login-transfer.md) 與 Server designed 行為嚴格分層。

## 原版 Client 已證（observed-static）

- **C03**：`string8 account + string8 password + u8 flag`。兩欄字串是「編碼後 bytes 數」u8 前綴，不是固定 UI 字元數；Server 必須自己驗帳密與停權。
- **S02**：`u8 status + string8 message`；不同 Login/CreateInfo context 對 status 的含義不一定相同。舊 seed0 profile 錯密 status3 屬既有人工紀錄，不能據此臆造 duplicate/ban code。
- **S03**：`u32_be destination_address + u16_be destination_port + u8 token_length + raw token bytes`。Client 以 S03 的 host/port 建立新 TCP。
- **C10**：新 World TCP 送 `raw token bytes`，**body 沒有再寫 u8 token_length**，已知 binary profile 屬 opcode 0x10 明文例外。禁止把它當 string8 解析。
- **位址勘誤**：`0x4A8370` 使用 S03 callback 中的 host/port/token，是 **S03 transfer handler**；A-022 早期將它標成 C25 region parser 是錯誤，已訂正。C25 真正的完整 region 格式另有 unknown。

## Server 設計狀態機（非原服政策）

```text
Login TCP → VersionReady → C03 Authenticate
  ├─ reject → S02，舊合法 World/Grant 不受錯密影響
  └─ valid → Authenticated(account,character,generation)
       → IssueTransferGrant(owner,character,generation,destination,expiry,one_time_nonce)
       → S03(addr,port,opaque token)
       → Login TCP closed does NOT revoke pending valid grant
       → World TCP C10(raw token)
          → AtomicConsumeGrant (one time)
             → WorldBound(generation) → C25 → S02/S05/S15/S14(1)/C35/S04/S33/S14(2)
```

1. `TransferGrant` 只由已認證 Account/Character 產生，需綁 owner、角色、目標 World、generation、期限和一次性 token；資料庫/日誌不記錄可重播的 token 原文。
2. **轉服時登入 TCP 關閉不可立即刪除尚未兌換的 Grant**，否則原版 Client 正常重連會被當成非法斷線。
3. 設計政策採「**最新成功登入**替換舊 World generation」：同帳號合法競爭以交易/CAS 推進 generation；錯密不能踢舊，舊 World 封包和舊 disconnect callback 不可刪除新世代 Session。此為設計選擇，**原服究竟踢舊／拒新未知**，不應寫成靜態 Client 事實。
4. C10 replay、過期、跨帳號／角色／World、未綁定 World 提前 C25 均 fail closed；Server crash 撤銷 volatile grant、不回滾持久角色/教學旗標。
5. **A-027 尚未解的 pre-C03 C02 帳號擁有權安全問題不因 A-002 正常 C03 登入而自動解決**。在 owner proof 未確定前，不以 C02 直接認領管理員預建 Account。

## CT 與交接

`CT-037`：S03/C10 新 TCP、登入 socket 正常關閉、錯密、expiry/replay/錯 owner、提前 C25；`CT-038`：兩個已認證登入的 generation/過期封包／舊 disconnect；二者均 planned、native Client `not-run`。DEV 可先開發 C03/S03/C10 codec、grant/Gateway state、合成測試。待 A-020/A-016 補原服 duplicate policy、非 seed0 region、錯誤 UI；A-027/A-028 負責首次創角權限及終局。

參考 [A-002 合併驗證](../04-analysis-integration/A-002-merge-verification.md)、[A-023 Script lifecycle](script-lifecycle-contract.md)。
