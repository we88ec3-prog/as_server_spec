# R-025～028：管理預建帳號至第一次進入新手教學

日期 2026-10-31；原生台灣版 Asgard Client SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145；最小已知 profile TW-seed0-local-v0.1。本文件是規格規劃，不宣稱原版未知封包已逆向或已實機驗收。

## 需求方已確認：R-025
**由授權管理員在獨立後台/API 建立帳號；玩家只能以既有帳號透過原始 Client 登入。Client 不能自行註冊 Account。**
管理端需認證、權限、操作稽核、唯一帳號、重試安全、密碼帶鹽不可逆雜湊及安全初始憑證交付。遊戲 C03 登入檢查帳號存在、憑證、停權；發行及使用 World grant 均核對狀態。Client 送 C02/NewUser 不等於授權新建 Account。角色建立只可歸屬已存在且有權使用的帳號。管理員重設密碼建議與本需求同一後台責任，具體 UI 可另規劃。驗收含無權管理建帳、重複/並發、Client 冒充創帳、錯密、停權、恢復後舊 token。

## R-026：已預建空角色帳號創角
原版 C02 已知為四個 string8 + flag（partial），C04 為 sex、hair、RGB；S02 有多種會話狀態解讀。**不得由名稱假設 C02 是玩家建帳權限**。A-021 要驗證無角色帳號如何進創角 UI、C02/C04 與 S02 成敗、是否建角後重登或轉服；A-003 補合法名稱/外觀及帳角映射。Server 只允許經認證帳號建 Character，草稿綁 session/generation 並會過期；名字唯一、外觀合法、owner、初始資料原子保存。單一角色是現有 profile 暫行映射，不推稱所有版本一帳一角。驗收須測同名競爭、非法外觀、C04 無 C02、跨連線、C02/C04 重送、提交前後 crash，且重登仍讀得相同角色。

## R-027：首次進原版新手教學
有持久角色及有效一次性 World grant 才允許入圖；不信任 Client 送的 map/出生點。真實教學 map ID、spawn(x,y)、朝向、資源與進圖條件都 **unknown，待 A-022**，不得以一般測試地圖替代。已知 SCN-001 世界順序：S03 交接 → 新連線 C10 → C25 → S02 → S05 → S15 → S14(1) → C35 → S04/S33、必要 S0F/S37 → S14(2)，S19 視 profile。載入中禁止一般世界操作與重入；異常 C35、地圖缺失、逾時、斷線必須有回復。以原 Client 在原版教學圖正常出生、外觀位置正確、loading 結束且可操作為出場條件。**進入教學不等於完成教學**。

## R-028：首次流程提交與故障回復
Account / Character / TransferGrant / CharacterSpawn / OnboardingProgress 具有明確歸屬、冪等與提交邊界；需初始物品時以 InitialGrantLedger 保證唯一，不預設原版發放特定物品。tutorial_entry_committed 與 tutorial_completed 必須分離。舊 generation、過期/重用/跨角色 token 不得取得控制權。建角完成回包丟失、C10/C25/C35 前後斷線或 Server 重啟時，只按持久化成功事實恢復，不出現半角色、重複初始資產、幽靈登入或教學已完成誤判。

## 工作與追蹤
SCN-007 管理建帳與玩家首次登入；SCN-008 原 Client 創角；SCN-009 首次新手教學進圖；SCN-010 中斷回復。A-021 原 Client 創角轉場、A-022 教學地圖出生、A-023 進圖後必要 NPC/Script 均尚待證據。CT-011～020 均為 planned，原生 Client 的測試與 Server 邏輯測試須分開報告。

本批目標到「角色成功進入教學且可操作」為止。怪物 AI、角色技能、NPC 互動、教學完成、任務獎勵等需求不當作本批已完成；將在 ONB-05 後續規劃。
