# A-014 → CT-047 / CT-048 / CT-048 Native E2E extension：聊天、成員與公會驗收

範圍 `R-015`。以上 CT 由後續 DEV/CT Owner 驗收，**計畫不是實際 native pass**；A-014 的原始 BIN static evidence 見 [分析報告](../task_a/roy2/A-014-analysis.md)。

- **CT-047（decoded body + state model）**：C0E type:u8+string8、C19 type:u8+target:string8+text:string8；CP950 長度以 bytes 計；空字串、壞長度、超出 255 bytes、未認證/舊 generation/錯 map epoch 拒絕。只驗 synthetic，不冒稱 wire 完全相容。S0A 是既有系統訊息不能誤當每筆發言。
- **CT-048（群組狀態/離線/重送）**：C2E op0/1 已知 wire layout；邀請、接受、退出、踢人、重複、同時競爭、離線目標、跨群與斷線重登入，均不會未授權更新 membership；S58/S3A 原生 subcode/名單格式不明，Native CT 前要補抓實際封包。
- **CT-048 Native E2E extension（公會/群組頻道 Native E2E）**：驗證 InputShoutToGroup/InputShoutToGuild 對應的 C0E type；讀 S0D type0..4（string8，而非 string16）、S0A 拒絕 UI、GuildListDialog、S58/S3A，記明名字/codepage、原始 owner ID、recipient set、成員變更／角色掉線／重登入。只有從原生 Client + 合法測試 Server 的實際 trace 可標 validated。

### 重現與資料保護

`python -m unittest discover -s task_a/roy2 -p 'test_a014_social.py'`；輸出只有人工合成的短文、無私人聊天內容或原版資產。測試記錄必須分開「observed-static」和「designed」。對未知 opcode subtype 或未知原服權限政策要 fail closed；不能靠組隊 UI 有按鈕就宣稱公會已互通。

### 2026-10-31 合併訂正

共用 CT 編號以最新 main 為準：聊天／密語 CT-047、群組／公會 CT-048；請不要創建其他任務已使用的 CT-041～046。S0D 應讀 **string8**，S0A 才是 **string16**；Native UI group/guild mapping 和原服拒絕仍 not-run／unknown。
