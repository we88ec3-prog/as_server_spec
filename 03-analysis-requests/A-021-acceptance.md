# A-021 分階段交付與驗收規則

**目標**：還原「管理員已建帳但沒有角色 → 原 Client 進入角色創建介面 → Client 發送建角意圖 → Client 對回覆的反應」，產出足夠 Server 開發的協定規格。**不把尚不存在的新 Server 實機登入成功列為 A-021 完成條件**。

- 研究身份：台灣版原 Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；profile `TW-seed0-local-v0.1`。
- 起點：C02 serializer `0x5742b0`、C04 serializer `0x574420`、S02 parser `0x57dbc0`、UI handlers、登入完成後的分支。
- 政策：R-025 已確認**Account 僅管理員建立**，Client C02/NewUser 不是建立 Account 的授權來源。要查 C02/C04 對 Character 的真正角色，不可直接按名稱推論。
- **分析交付 A gate**：由 BIN/資源證據列出 (1) UI 呼叫條件與上下文、(2) C02/C04 資料字段、字串編碼/長度/條件，(3) S02 解碼器可觀察的分支與場景判別，(4) 能合理建立的 Client 狀態轉移圖，(5) 證據位址與限制，(6) normal/error/cancel/retry/transfer 情境與未知清單，(7) 可交付的 PKT/SCN 規格和 CT-018 測試腳本。
- **缺證據時**：封包實際 Server 回覆語意、成功畫面/轉服行為若沒有獨立 runtime 證據，標 `unknown`、`handoff_status=partial` 並列具體 follow-up A；不得假裝原服實際回覆已驗證，也不得因「Server 尚未可執行」把整個 A 拒收。
- **下游 DEV gate**：ONB-02 根據已確認的可用子集合實作角色建角、驗證、資料持久化與回覆，進行 unit/integration/fixture 測試。
- **下游 CT gate**：CT-018（與 SCN-008/009）在 Server 可啟動後，以真實 Client 進行預建帳號登入/建角/進入原生教學地圖的端到端驗收。CT failed 時依證據歸因新增 A 或 DEV 缺陷。

A.status=`integrated` 代表「審查後整合了明確範圍的研究結論」而不是 CT-018=`passed`。完整的跨角色規則見 [phase-gates](../00-governance/phase-gates.md)。
