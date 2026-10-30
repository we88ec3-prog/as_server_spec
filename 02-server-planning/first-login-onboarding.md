# 首次玩家 Server 跨系統規劃（ONB-01～04）

需求 R-025～028。**已確認**：管理員建帳；玩家原生 Client 只登入既有 Account，仍能自行創角。A-021 已靜態分析整合（參考 A-021-followup），僅可實作已核對的 C02/C04 codec/Client 狀態子集；C02 預建帳號認領仍有未確認的身份與權限風險，必須等待 A-027；但沒有證據說 C03 無角色登入後原版 Client 自動轉至創角 UI。原新手教學地圖與座標待 A-022。

|系統|語意命令/持久資料|限制|
|---|---|---|
|Admin / Auth|ProvisionAccount、AccountStatus、Audit、AuthenticateExistingAccount|只有授權後台建 Account；密碼不可明文存儲或記錄；Client 的 C02 不可建 Account|
|Character|CreateDraft、CompleteCreation、Character、Appearance|合法 Session + 既有 owner；C02/C04/S02 真正成功/失敗待 A-021；交易只完成一次|
|Session|IssueTransferGrant、ConsumeTransferGrant、generation|限時、一次性、綁帳號/角色/目的端；停權時不能交接|
|World|SelectInitialSpawn、Loading、InWorld、MapContent|首次教學圖、spawn 與 CRC 行為待 A-022；載圖中禁止一般遊戲操作|
|Persistence|CharacterSpawn、OnboardingProgress、InitialGrantLedger|進入教學與完成教學分離；重送/斷線/crash 不得複製資產|

## 狀態與提交
1. AuthorizedAdmin → AccountProvisioned；遊戲 Client 不接受 ProvisionAccount。
2. LoginReady → C03 Authenticate → CharacterReady 或 NoCharacter（**Server 內部狀態**；不代表原 Client 有無角色選單）。
3. NoCharacter → Client 原生 NewUser UI 的 C02（可能早於 C03；**在 A-027 證明身份與權限前不得認領任何預建 Account**）→ 尚未授權的解析階段／合法身份驗證（待 A-027）→ 授權後才能回應可觸發 C04 的 S02 status0 → C04 → 最終回覆與角色原子提交時機待 A-028 → CharacterReady；C04 無前置/跨 Session/非法資料拒絕。C03 無角色不得直接進 World；是否能自動轉原 UI 仍 unknown，採 NewUser 入口作 designed 暫行流程。
4. CharacterReady → S03 IssueGrant → C10 ConsumeGrant（同一 token 只能使用一次）→ C25 Loading。
5. S02、S05、S15、S14(1)、C35、S04、S33、必要背包裝備、S14(2) → InWorld。教學地圖出生點只用 A-022 證實的設定；C35 超時/CRC 失敗進 Reconcile，不亂標入圖成功。
6. 首次成功提交 tutorial_entry_committed；**不**自動寫 tutorial_completed。重連時用已保存角色/位置/旗標恢復，可能的初始資產以唯一 ledger 防重。

## 開發批次
|批次|範圍|出場門檻|
|---|---|---|
|ONB-01|授權管理建帳、安全登入/停權/稽核|Client 不能建帳；有效的管理員預建帳號能正常登入|
|ONB-02|原 Client 以 C02 認領預建帳號、C04 完成角色及持久化|A-021 靜態契約可開始開發；A-003 合法值待補；原 Client 實測是 CT/BUG 回饋，不是開工前置|
|ONB-03|一次性 World handoff、原生教學地圖與初始定位|待 A-022；正確原 Client 可在教學地圖操作|
|ONB-04|故障、重送、並發、過期/重用 grant、測試整合|CT-011～020；Domain 測試與 Client 實測分開留存|
|ONB-05（後續）|教學怪物、技能、NPC、任務與教學完成|另立需求，不屬本次首次入圖完成條件|

此規劃不依賴特定語言/資料庫；現有 SCN-001 為一般登入/地圖載入已知 profile，不能自動升級為教學驗收。


## A-021 roy1 靜態證據與安全設計更新（2026-10-31）

原始 Client 會在 UI 狀態 0x1d 收到 S02(status0) 後送 C04，進 state 0x1e；此狀態轉移已靜態確認，但不代表 Account 認領已授權或 C04 已完成角色建立。**不可因 C02 早於 C03 就把既有帳號認領改成無密碼操作**。Region-specific C02 layout 已知，字段語意未知；在 A-027/A-028 未完成前只允許 codec/parser 與 Domain 內部模型的部分開發，對外未授權路由 fail closed。見 [roy1 審核](../04-analysis-integration/A-021-roy1-review.md)。

## A-022 merge：通用載圖的可實作邊界

[完整 BIN-first 證據](../03-analysis-requests/A-022-roy1-bin-analysis.md)。進圖由 Server 先綁定 `character_id,map_id,map_revision,loading_epoch,spawn`；S15 → S14(1) → C35 驗兩個 BE u16（本機 MAP header +4 的 word 與 parse 後 structured checksum），只接受當次 epoch 的核對成功後才送 S04/S33/S14(2)。C35 第一欄非 map_id，checksum 不是 raw 檔案 CRC；錯版/超時/重連進 Reconcile，entry committed 不等於 tutorial completed。**A-015 的原生教學 MAP + 出生位置仍 unknown**；不得把 Born 指引座標 (31,29) 當初生點。原生 Client CT 尚未執行。
