# R-025～028：管理預建帳號至第一次進入新手教學

日期 2026-10-31；原生台灣版 Asgard Client SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145；最小已知 profile TW-seed0-local-v0.1。本文件是規格規劃，不宣稱原版未知封包已逆向或已實機驗收。

## 需求方已確認：R-025
**由授權管理員在獨立後台/API 建立帳號；玩家只能以既有帳號透過原始 Client 登入。Client 不能自行註冊 Account。**
管理端需認證、權限、操作稽核、唯一帳號、重試安全、密碼帶鹽不可逆雜湊及安全初始憑證交付。遊戲 C03 登入檢查帳號存在、憑證、停權；發行及使用 World grant 均核對狀態。Client 送 C02/NewUser 不等於授權新建 Account。角色建立只可歸屬已存在且有權使用的帳號。管理端重設密碼保留作管理員救援操作；**玩家正常修改密碼必須透過遊戲內原生更改密碼 UI**，兩者不是同一入口。驗收含無權管理建帳、重複/並發、Client 冒充創帳、錯密、停權、恢復後舊 token。

## R-026：已預建空角色帳號創角
原版 C02 已知為四個 string8 + flag（partial），C04 為 sex、hair、RGB；S02 有多種會話狀態解讀。**不得由名稱假設 C02 是玩家建帳權限**。A-021 要驗證無角色帳號如何進創角 UI、C02/C04 與 S02 成敗、是否建角後重登或轉服；A-003 補合法名稱/外觀及帳角映射。Server 只允許本次創角入口的既有帳號**帳號＋密碼直接驗證成功**後建立 Character；不要求先完成 C03 登入，草稿綁建立時產生的 creation-only proof／連線／generation 並會過期；名字唯一、外觀合法、owner、初始資料原子保存。單一角色是現有 profile 暫行映射，不推稱所有版本一帳一角。驗收須測同名競爭、非法外觀、C04 無 C02、跨連線、C02/C04 重送、提交前後 crash，且重登仍讀得相同角色。

## R-027：首次進原版新手教學
有持久角色及有效一次性 World grant 才允許入圖；不信任 Client 送的 map/出生點。真實教學 map ID、spawn(x,y)、朝向、資源與進圖條件都 **unknown，待 A-022**，不得以一般測試地圖替代。已知 SCN-001 世界順序：S03 交接 → 新連線 C10 → C25 → S02 → S05 → S15 → S14(1) → C35 → S04/S33、必要 S0F/S37 → S14(2)，S19 視 profile。載入中禁止一般世界操作與重入；異常 C35、地圖缺失、逾時、斷線必須有回復。以原 Client 在原版教學圖正常出生、外觀位置正確、loading 結束且可操作為出場條件。**進入教學不等於完成教學**。

## R-028：首次流程提交與故障回復
Account / Character / TransferGrant / CharacterSpawn / OnboardingProgress 具有明確歸屬、冪等與提交邊界；需初始物品時以 InitialGrantLedger 保證唯一，不預設原版發放特定物品。tutorial_entry_committed 與 tutorial_completed 必須分離。舊 generation、過期/重用/跨角色 token 不得取得控制權。建角完成回包丟失、C10/C25/C35 前後斷線或 Server 重啟時，只按持久化成功事實恢復，不出現半角色、重複初始資產、幽靈登入或教學已完成誤判。

## 工作與追蹤
SCN-007 管理建帳與玩家首次登入；SCN-008 原 Client 創角；SCN-009 首次新手教學進圖；SCN-010 中斷回復。A-021 原 Client 創角轉場、A-022 教學地圖出生、A-023 進圖後必要 NPC/Script 均尚待證據。CT-011～020 均為 planned，原生 Client 的測試與 Server 邏輯測試須分開報告。

本批目標到「角色成功進入教學且可操作」為止。怪物 AI、角色技能、NPC 互動、教學完成、任務獎勵等需求不當作本批已完成；將在 ONB-05 後續規劃。

## A-021 roy1 合併後新增安全約束（2026-10-31）

已經 BIN-first 核對 C02 可在 C03 之前送出，且 local state 0x1d 在 S02(status0) 後發 C04。然而 **C02 字串的身份/驗證語意仍未知**；R-025「只能管理員建立 Account」不變，任何 Client C02 都不得直接新建 Account、任意認領預建帳號、核發具權限的 Session/World grant 或替他人建立角色。是否可安全綁定已預建 owner 交 A-027，C04 成功/拒絕與重登轉服交 A-028；暫不能宣稱 ONB-02 完整原生相容。審核見 [A-021 review](../04-analysis-integration/A-021-roy1-review.md)。

## 最新決策：C03 登入與 C02 創角是兩個獨立原生入口

**此段取代先前「創角一定先登入」的暫行假設**。管理員預建 Account 後，玩家可以直接在 NewUser 創角 UI 輸入**同一筆後端 Account 的名稱與密碼**，由 Server 核對已存在 Account、密碼雜湊與停權狀態。錯密／未知帳號必須回原版 UI 能理解的錯誤，不可新增 Account、PendingCharacterIntent、Character 或 issue World grant，也不可回引發 C04 的 S02(0)。正確帳密產生**僅限本次創角**的 AuthProof，再接已有 C02→S02→C04→S02 和持久化唯一性/重放保護；**不要求先 C03**。C02 第一/第二欄只是 Client 靜態研究推定的帳號/密碼欄，還需要 A-027 最後 wire/UI 對應與非零 S02 的錯誤畫面證據；未知時 native 開放仍 fail-closed。玩家正常改密碼走遊戲**原生更改密碼 UI**（A-029），後端同一 credential；管理端重設僅救援。見 [完整契約](../02-server-planning/three-native-account-entry-policy.md) 與 [新版安全設計](../02-server-planning/character-account-match-policy.md)。

## P0 原版登入密碼最多 8 字元（2026-10-31 使用者回報）

原版 `Asgard.exe` 登入欄位依使用者觀察最多 8 字元，與目前私有 DEV-030 `Pbkdf2PasswordHasher.ValidatePassword` 的 **10～128 字**政策衝突（已查目前 main 源碼實際是至少10字，不是原先所述至少12字）。**R-025 最新決策**：管理員建立及重設的**遊戲**帳號密碼改為 **4～8 個 ASCII 英數字元，大小寫敏感**；管理員自動產生時建議使用安全亂數 8 字。Admin X-Admin-Key/強憑證不受限，不能截斷舊密碼。DEV-030 要同步修改 SQLite/PostgreSQL 與 Client 驗收，目前只是規劃，私有 Server 程式碼尚未修正。後續**可能**由使用者另行批准修改 `Asgard.exe` 延長輸入限制，目前不修改，須建立獨立 Client profile 後才能改長度。

細節：[Native 8 字相容契約](../02-server-planning/native-game-password-4to8-policy.md)。此為 `reported-client-UI` + `verified-server-source` + `designed-policy` 三種證據分開，原生 C03 GUI/送包 A-020/A-002 仍須實測，CT-019/037/050 仍待執行。

## 更正後 DEV-030 實況及獨立改密碼 UI

私有 `as_server_roy` 程式目前已將遊戲密碼驗證改為 **4～8 ASCII 英數**；上文舊「10～128 尚未修」為早期程式版本狀態，已不適用。玩家改密碼仍缺原版 native UI opcode/Server handler，**不得**把管理員 `credential-reset` 當作一般玩家的改密碼流程，亦不因此新增 Web 表單。新增 R-032、A-029、CT-097..099（planned/not-run）。
