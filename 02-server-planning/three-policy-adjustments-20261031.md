# 三項使用者設計決策：創角 Guard、最高隊伍傷害獎勵、拒絕入學可重問

狀態：2026-10-31 **指定規劃／尚未實作／原版 Client 未驗收**。此檔為最新權威覆蓋；任何既有文件寫「創角必須先 C03」／「傷害與掉落未決」／「拒絕即結束／永久變更」均視為**歷史規劃，不能當新開發需求**。

## 決策一：創角 Guard 不要求登入 Session（R-026）

**兩個入口相互獨立**：管理員預建 Account 後，原版 NewUser UI 可在尚未 C03 登入時送 C02(name, password, region-specific extras)。Server 的 `CredentialVerifier` 用此**次 C02 的帳號＋密碼**核對後端已存在的唯一 Account、狀態及密碼版本。只有成功才建立 `CreationAuthProof(account_id, credential_version, connection_id, generation, expiry)`，僅限創角、不等於已登入 Session，也不可核發 WorldGrant／冒用別帳號。

|情境|Server 契約|
|---|---|
|沒登入 C03，但 C02 正確帳號＋密碼|**允許**建立限創角授權／PendingCharacterIntent，合法 C04 後原子提交 Character|
|已登入或未登入，但 C02 錯帳號、錯密／未知帳號／停權|**拒絕**，不建 Account/角色/草稿，不發 C02 階段 S02(0)，不給 WorldGrant；應使用原版可顯示之失敗回覆，不能編造未知 native status|
|只有 C02 名稱，未驗密碼／Client UI 本地密碼確認而未做 Server 驗證|**拒絕**；Client-side 字串與已登入名稱都不是驗密碼的替代|
|C02 正確後不同 connection/generation、過期／改過密碼才送 C04|拒絕，保護 owner、世代、密碼版本、idempotency；C15 只取消同 owner 未提交 intent|

**已核對私有 Server 目前未實作此新 Guard**：`as_server_roy/main@ad84f9fb11606a318aff6bd67e065aa0ee07cc45` 的 `src/Asgard.Server.Application/CharacterCreationAccountGuard.cs` 仍要求 `AccountIdentity? loggedIn` 且 `RequireMatch(loggedIn, generation, submittedAccount)`；`AuthenticatedCharacterCreation.BeginFromClientAsync` 也據此拒絕未登入。後續 DEV-040 應經確認後改成 `AuthenticateCreationAsync(submittedAccount, submittedPassword, connection, generation)` 與 `BeginFromVerifiedCreationProofAsync` 之類的分離概念，**不可直接刪掉 Guard 或信任 C02 名稱**。尚需 A-027/A-028 證實 field1/field2 原版 UI 意義與錯誤 S02；native C02/C04 未證前 fail-closed。此處為 API 構想，**不是已編碼方法**。

## 決策二：單怪最高「隊伍」總傷害獲得全部經驗與個人掉落判定（R-033）

適用共享地圖同一隻怪物的同一生命 `monster_instance_id + life_generation`。只有 Server 權威確認的**有效 HP 傷害**能計分（以實際扣除、不可超過怪物剩餘 HP，無效/閃避/重送/治療/過量聲稱不計；怪物回復不回扣已記錄傷害，特殊反彈或多段效果需 Server 定義）。

- **歸屬隊伍**：每次有效傷害都記錄當時 Server 認證的 attacker `character_id` 與其 `party_id`（非隊伍的角色按**一人隊伍**計），累加 `party_damage[party_id]`；不按個人最高傷害判斷。必須有可信 party roster / revision，不能只相信 Client 提供的隊伍名稱。多人同一隊伍各自造成的傷害合計。
- **怪死時唯一結算**：Monster death 世界事件鎖定 `life_generation`、傷害帳及 party membership snapshot，選 **總有效傷害最高的一個隊伍**取得獎勵，其他隊伍／單人**不領取經驗或掉落**。傷害與死亡事件都需冪等（同一 damage event 不二次累積、同一 monster life 不二次結算）；空有效傷害時不發獎。
- **完整經驗**：獲勝隊伍**每位符合該次隊伍名冊的成員**各獲得怪物設定的 **100% 基礎經驗值**，不依輸出占比、不平均分割。例如 A隊甲造成60、乙造成40；B隊丙造成90 → A隊總100勝，甲乙每人各領全額經驗，丙零。
- **各自獨立掉寶**：獲勝隊伍的**每一位成員**各以怪物當次 loot table（與已證實的物品資源相容）**執行一次獨立的掉落機率判定**；不代表每人保證一定掉到物品。若怪物表本身按多項 item 做抽選，則「一次」是每位成員**一套完整 loot-table resolution**，不是共用一份隨機結果，也不是各打一下多抽一次。以 `monster_life + character_id + reward_category` 作唯一 Ledger；個人結果與本人角色背包/待領取資料綁定，避免 A 的掉落被 B 偷領。
- **安全／世界模型**：全圖共用 Monster HP/Death/Respawn 一份，經驗/掉落是按獲勝隊伍成員的個別 CharacterLedger 寫入；獎勵應在同一權威死亡結算下 durable，斷線／重啟可補發結果、不重新抽籤。仇恨/最後一擊不是歸屬依據，Client 封包不是掉落發放的權威。
- **尚未經使用者明定的邊界**：兩隊傷害完全相等的勝負、離線成員／不同地圖成員是否仍有資格、打怪中途退隊/入隊、隊伍解散前後傷害如何繼承、怪物等級差與特殊任務專屬掉落。這些需要在實作前有明確政策；**不要擅自把傷害最高的個人當勝者，或把「全員」改成距離內貢獻者**。目前可先設 domain 函式以注入的 eligibility/tie policy 測試，不對原 Client 假發物品包。

## 決策三：新手教學 NPC 選「不入學」＝無進度效果，可再詢問（R-034）

- 在已證明能點擊的招募 NPC 對話中，玩家選 `STATE=REFUSE` 或原版 Client 已證的「不入學」意圖：**不建立入學紀錄、不改 Quest/Onboarding、無任務接受／完成、無經驗／道具／金錢獎勵、不傳送、不切圖、不永久封鎖該 NPC，亦不修改共享 NPC 狀態**。關閉本次對話 UI 是 Client 顯示生命週期，不是遊戲權威狀態變化。
- 玩家稍後（或立即）**再次點同一 NPC**，Server 應可再發起一輪有效 Script/dialog context，顯示同一詢問；可以反覆拒絕，仍可之後選「入學」走合法接受路徑。
- `STATE=ACCEPT` 僅是入學**意圖**，不等於 quest completed、獎勵獲得或新地圖轉場；接受後真正條件、任務資源、學校入口和目的地仍需 A-012/A-023/A-026 對照原生行為；任何原本 `C6C(4/2)` 的 dialog close 不能被當入學/拒絕造成的持久旗標。
- **多人情況**：甲拒絕不應改動乙的任務／NPC 可互動性；每人自己的 dialog run/context 和 onboarding state 分離。拒絕／重開／舊 C6C reply/重送都不應產生不可逆副作用。
- `nNewJoin01.dat` 的 `STATE=ACCEPT/REFUSE` 已從資源取得，但**NPC ID→此 Script 綁定和實際 Dialog 選項 callback 仍未原版 E2E 證實**；設計不可把「使用者決策」包裝成已觀測的原服 Server 策略。

## 交付與驗收

規劃測試 **CT-100（無 C03 創角 Guard）**、**CT-101（最高總傷害隊伍／個別 100% exp／個別一次 drop）**、**CT-102（拒絕入學零副作用＋可再次點 NPC）** 均 `planned/native_client_validation=not-run`。資料模型與 HTTP/遊戲實作都尚未變動；改 Guard、DamageLedger/PartySnapshot、RewardLedger、NPC admission flow 必須先有另一個 Server 實作指令／確認，不用改 `Asgard.exe`，不建立新 branch。

Client 仍需 **A-027/028** C02 field mapping/錯誤；**A-014** party ID/membership UI/protocol，**A-009/025** damage/death，**A-007/013** item/exp 投影，**A-012/023/026** NPC script choice/re-entry。後端分配規則由 Server 設計決定，並非逆向必須還原原服。
