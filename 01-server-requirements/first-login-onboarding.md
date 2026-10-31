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

## A-021 roy1 合併後新增安全約束（2026-10-31）

已經 BIN-first 核對 C02 可在 C03 之前送出，且 local state 0x1d 在 S02(status0) 後發 C04。然而 **C02 字串的身份/驗證語意仍未知**；R-025「只能管理員建立 Account」不變，任何 Client C02 都不得直接新建 Account、任意認領預建帳號、核發具權限的 Session/World grant 或替他人建立角色。是否可安全綁定已預建 owner 交 A-027，C04 成功/拒絕與重登轉服交 A-028；暫不能宣稱 ONB-02 完整原生相容。審核見 [A-021 review](../04-analysis-integration/A-021-roy1-review.md)。

## 暫行創角帳號比對政策（使用者決策，2026-10-31）

**不修改 Client，也不禁止編輯原生帳號輸入框。** 在原 Client 的 NewUser/C02 第一欄被確認為帳號欄、且存在與此創角會話相同 generation 的 Server 已驗證登入 Account 後，Server 只接受 **輸入帳號與該登入帳號相同** 的創角請求；不符必須失敗，且不得建立 PendingCharacterIntent/Character、改別人帳號、核發 Grant 或送會觸發 C04 的 S02(status0)。帳號相等依現有管理帳號規格使用 3～32 ASCII 字母/數字/底線且大小寫不敏感比較（不 trim、無別名），實際角色 owner 一律使用 Server account_id。

**無有效登入 AuthContext → 一律拒絕**，即使字串剛好相同；匹配成功只通過此檢查，另需帳號未停權、有效 session/generation、角色/外觀唯一性等規則。A-027 仍未確認 C03 無角色→NewUser 原生可達及 C02 第1欄確為既有登入帳號，因此正式 native C02/C04 仍必須 fail closed，直到證據足夠；不得把原服註冊 UI 直接當作新 Server 的角色創建授權。原生錯誤回覆 status 尚未知：拒絕時不得發 S02(status0) 或亂猜 status；目前安全實作可結束未授權連線。這是 **Server designed**，不宣稱原版原本有相同限制。

[完整 Server 比對契約](../02-server-planning/character-account-match-policy.md)。

## P0 原版登入密碼最多 8 字元（2026-10-31 使用者回報）

原版 `Asgard.exe` 登入欄位依使用者觀察最多 8 字元，與目前私有 DEV-030 `Pbkdf2PasswordHasher.ValidatePassword` 的 **10～128 字**政策衝突（已查目前 main 源碼實際是至少10字，不是原先所述至少12字）。**R-025 最新決策**：管理員建立及重設的**遊戲**帳號密碼改為 **4～8 個 ASCII 英數字元，大小寫敏感**；管理員自動產生時建議使用安全亂數 8 字。Admin X-Admin-Key/強憑證不受限，不能截斷舊密碼。DEV-030 要同步修改 SQLite/PostgreSQL 與 Client 驗收，目前只是規劃，私有 Server 程式碼尚未修正。後續**可能**由使用者另行批准修改 `Asgard.exe` 延長輸入限制，目前不修改，須建立獨立 Client profile 後才能改長度。

細節：[Native 8 字相容契約](../02-server-planning/native-game-password-4to8-policy.md)。此為 `reported-client-UI` + `verified-server-source` + `designed-policy` 三種證據分開，原生 C03 GUI/送包 A-020/A-002 仍須實測，CT-019/037/050 仍待執行。
