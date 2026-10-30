# 邏輯介面與資料責任

本頁定義可替代的語意邊界，不指定函式名稱、程式語言、ORM或資料庫表。下列命令／事件名稱是規劃語彙，**不是已確認的Client封包名稱或新增wire欄位**。

## 命令與結果

|責任域|輸入意圖|裁定與結果|外部投影／待解依賴|
|---|---|---|---|
|Auth|Authenticate、ConsumeTransferGrant|認證結果／一次性交接，禁止重用|S02/S03、C10；重複登入政策A-002|
|Character|CreateDraft、CompleteCreation|唯一性／合法外觀／原子建立|C02/C04、S02；完整選項A-003|
|World|EnterMap、RequestMapChange|載入狀態、實例、可見性、完成定位|S15/S14/C35/S04/S33；錯誤回復A-016|
|Movement|MoveIntent、TurnIntent|位置、方向、速度及障礙驗證|自身S0B與他人廣播分開；A-004/005|
|Appearance|EquipIntent、ChangeAppearance|所有權、槽位、髮色／衣色、面向|S37/S33/S05，正式脫裝A-007|
|Combat/Skill|AttackIntent、CastIntent|目標／距離／資源／冷卻／傷害|Client動畫與狀態更新待A-008..010|
|Economy|Purchase、TradeConfirm、ClaimReward|原子轉移、重送防護、結果保存|各UI及收發待A-012/013/016|
|Admin|AuthorizedAdministrativeCommand|操作者權限、合法狀態、稽核|不直接走未驗證DB寫入；A-017|

內部命令可攜session_generation、actor_id、request_id、expected_state_version等元資料；Client沒有這些欄位時由gateway／application產生，不能擅自加到原生封包。wire錯誤碼由實際Client契約映射，不能把內部enum數字直接發給Client。

## 事件與投影

命令產生角色已進圖、實體移動已裁定、裝備已變更、物品已移轉、傷害已結算等語意事件。輸出層依觀察者／Client版本決定所需封包。不同實作可不用事件框架，但不得混淆「狀態已提交」與「只是準備發封包」。

同一角色與世界實例的因果順序必須可追溯。輸出佇列滿時依策略斷線／重同步，而非無限堆積記憶體。持久經濟操作應在成功回覆前完成原子提交，或採具有同等可觀察保證的可靠提交機制。

## 資料模型責任

|邏輯資料|所有者／責任|不變條件與缺口|
|---|---|---|
|AccountCredential|Auth|帳密機密不入一般log；Client登入限制與Server保存策略分開|
|Session/TransferGrant|Session|連線generation、期限及消耗狀態；不能跨角色重用token|
|Character/Appearance|Character|外觀各欄獨立；原生帳號角色映射仍由A-003確認|
|WorldInstance/Entity|World|ID生命週期／作用域待A-004；離開時清理可見性|
|Position/Facing|World/Movement|world格座標、像素／鏡頭投影分開；不能信任Client結果|
|ItemDefinition|Content|靜態能力與資源ID，不等於實體所有權|
|ItemInstance/Inventory/Equipment|Items|唯一實體、數量、所有者、槽位及版本；交易後只屬一方|
|Stats/Effects/SkillState|Combat/Skill|公式、上限、冷卻及效果過期；原服未知需明示設計|
|Wallet/RewardClaim/Trade|Economy|不可重領、取消／超時可回復、提交點明確|
|Quest/SocialMembership|Quest/Social|進度、成員及權限保存；需原生情境支持|
|ContentManifest|Content|抽取來源、資料版本與校驗；不直接散布原始資產|
|AuditRecord|Operations|可追管理操作與結果，不含密碼／token或完整敏感body|

## 依賴規則

Domain不依賴socket／opcode／管理UI／具體DB；Protocol不直接寫資產；管理UI不繞過命令權限。依賴向內，Infrastructure實作儲存及時鐘等抽象邊界。各實作可選不同技術，但共同驗收應只觀察契約而非內部類別。

## 首次玩家新增內部語意接口（不是原生 wire）

Admin.ProvisionAccount/Suspend/Unsuspend：獨立管理身分、權限、稽核；不能由 Client 命令建立 Account。
Auth.AuthenticateExistingAccount/ConsumeTransferGrant：核對帳號有效、世代與一次性 grant。
Character.CreateDraft/CompleteCreation：只為既有帳號建立合法角色，原子提交；C02/C04/S02 分支待 A-021。
World.SelectInitialSpawn/CommitTutorialEntry：原版教學地圖與坐標待 A-022；tutorial_entry 與 tutorial_completed 分開。參見 [規劃](first-login-onboarding.md)。

## C02 早於 C03 的信任邊界修訂（A-021 roy1）

Game Client C02 可能在 C03 之前送出；C02 region 封包布局已由 BIN 確認，但其帳號名稱／憑證字段仍 unknown。Gateway 可以在 pre-auth 階段**解析**此封包，不代表有權呼叫 `Account.Create` 或 `Character.CompleteCreation`；未經帳號擁有者身份校驗，不得將其當成 `ClaimExistingAccount`，不得發行有效 transfer grant、授權 S02 success 以進入 C04 或寫入 Character。A-027 必須證明身份驗證／綁定時機，A-028 必須證明 C04 final response。詳見 [A-021 roy1 review](../04-analysis-integration/A-021-roy1-review.md)。
