# A-002 roy1 合併後的證據核對（2026-10-31）

最新 roy1 分支 A-002 報告已經兩親 merge commit `d2ac61bf6a44a43324d03fc2e6db5a25654297fb` 納入 main，後續將 PKT-C03/C10/C25/S02/S03、SCN-001/007/010、證據索引、CT-037/038 逐欄整合，不覆蓋此前 roy2 的 S44/C6C／CT-033～035。roy1 隨後只修正本支 manifest 的提交亦已記入 main 血緣，保留 main 追加的多分支資產。

## 原件靜態覆核

本次實際持有 `Asgard.exe` 3,235,840 bytes，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。objdump 顯示：
- `0x573110..0x573152` 連續兩次 string8 writer（`0x45B1B0`）與一次 u8 writer（`0x45AB00`），支持 C03 body 排列。
- `0x5886C0..0x5886F0` 連續 32-bit／16-bit／8-bit／raw read，支持 S03 host/port/token_len/raw_token。
- `0x5773E0..0x5773EE` C10 使用 `0x45B4C0` raw memory writer，**不另寫 length byte**。
- `0x4A8370` 的 region 分支讀 S03 callback +0x24 addr/+0x28 port 再呼叫 `0x53B300` 設目標；應由舊 A-022 C25 handler 誤標改為 S03 handoff。

## 仍然未知

原服重複登入 policy/S02 狀態碼、原服 grant TTL、非特定 region callback、C03 flag 的遊戲語意、原生 Server 端權限及 native Client 完整 E2E，均不能由 Client static 直接證明。`tools/a002_session_model.py` 所示 latest-authenticated-wins／TTL 為 **synthetic designed model**，非原服逆向。A-002 `integrated/handoff_status=partial` 是部分原生封包證據可以交 DEV，不代表 CT pass。

對應 [Server 設計](../02-server-planning/session-transfer-contract.md) 和 [原始 A-002 報告](../03-analysis-requests/A-002-roy1-login-transfer.md)。
