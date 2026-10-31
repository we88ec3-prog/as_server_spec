# Server 新手教學第二輪：NPC 對話、技能施放及狀態效果

依據 [A-012 Quest / A-010 Skill 交叉整合審查](../04-analysis-integration/merge-review-roy1-roy2-new-quest-skill-20261031.md)；本文件是 Server **新規劃**，未宣稱私有實作或原生 Client CT 完成。原版 Client 不修改。

## ONB-05/06 DEV-090：Quest Dialog 與入學選擇

1. `S44(1,0)` 的 Script start 應只用已驗證的 `client_profile + script_name + CRC + dependencies + context`，像 Born/PaperDialog 等，Script XML 本地顯示與 Server Quest 權威狀態分開。
2. `C6C(1)` 只承載 ScriptReply 選項意圖；解析 `name:string8, context:u32BE, pair_count:u16BE, key/value:string8`，綁定 AuthContext/Character/ConnectionGeneration/WorldEpoch/ScriptRun；禁止無授權、重複鍵、超長、跨角色、stale context、相同鍵不同 body 重播。
3. `C6C(4)` Dispose 和 `C6C(2)` no-reply cleanup 都不可直接完成 Quest、發金幣或升級；與 `C6C(1)` 分別冪等記錄。 `nNewJoin01.dat STATE=ACCEPT/REFUSE` 僅是 AdmissionIntent；`PaperDialog02.dat PAPER02=START/NOT` 是另一套回覆，不能混用。
4. 只有已驗證的 NPC binding/quest authoritative event/獎勵設定/出口地圖，才建立 `QuestCompletionLedger` 與 `ExitCheckpoint`；共享地圖其他玩家的 NPC/怪物狀態不因這個玩家的任務按鈕改變。可以 synthetic 驗安全性，但 Client native CT-093/094 未測。

## ONB-05 DEV-080：SkillCast / LastingSpell 技能系統

1. `C4D` 的 BEu16 僅是 Client 選定的技能值，`C56` 的 u8 仍屬待查的 casting phase；Server 必須驗證該玩家是否已學會、是否同圖/存活、目標/距離、資源/MP/冷卻才可從 `CastIntent` 轉成合法施法，**不能直接信任 Client 說成功**。
2. `S52` 的 `u32+u8` 狀態尚無已證 enum，`S48` 的 `u32` 是原生取消通知；兩種不能憑名字推作全部失敗/完成回覆。成功 HP/傷害 `S08/S13`、死亡 `S5F` 分別驗證與投影。
3. 持續技能 `S2C(0x2C)` AddLastingSpell dynamic string8，`S2D(0x2D)` RemoveLastingSpell。先做 Server 的 `LastingEffect(key,actor,world_generation,source,version,expires_at?)`，應避免在未證原版時基下填入 wire 的兩個 u32；刷新/疊加/重登/過期的 Domain 行為可定義，原版 GUI 顯示由 CT-096 验。
4. 在多人共享的 MapActorRegistry 上，SkillImpact/怪物 HP、死亡與重生必須一致，個人 BUFF/技能/CD 只歸屬個人，斷線不能把全圖怪物重設；對同時施法/取消/攻擊重播保持 epoch/fencing。
5. 未找到正式的 spell-id→單體/AOE/治療/BUFF/召喚映射、耗魔/冷卻或真 tooltip/音效素材之前，不編造原版技能表。可先把 Server 自定訓練 profile 標為 mock，不對正式原版 Client 宣稱完整兼容。

## 開發次序與驗收

|先後|Server 工作|可先完成的 synthetic/offline|仍要原版 Client 驗證|
|---|---|---|---|
|1|DEV-030 遊戲登入密碼 4～8字|管理建帳/重設/登入/限流|原版 C03 完整打4～8字|
|2|DEV-060 地圖和 DEV-070-M 共用場景|494 MAP 解析、共享 actor 狀態、不可推測 walkability|CT-090/091 原生可走、C35、雙 Client 可見|
|3|DEV-090 ScriptReply/AdmissionIntent|C6C(1/2/4) codec, context replay/關閉不發獎|CT-092（離線），CT-093/094（對話 GUI/任務）|
|4|DEV-080 Skill/Status/LastingEffect|C4D/C56/S52/S48/S2C/S2D、權威 MP/CD/效果 ledger mock|CT-095（離線），CT-096（真 Client 技能/BUFF GUI）|
|5|Economy Shop/Trade domain|安全錢包/道具移轉與冪等|CT-087～089 交易原生 UI|

**仍需 A 分析**：A-010 C56 producer、S2C/S2D 持續效果 UI 及 skill-id/official spell resources 的真實定義；A-012 NPC→Script/Quest response callback；A-022 tutorial map/C35；A-027 空角登入可達創角 UI。這些 A 已交付其部分靜態證據，Native Client CT 獨立保持 not-run。

既有使用者政策不變：管理員預建 Account，創角帳號不同拒絕、多人進同一地圖、密碼 **4～8 字**；未授權修改原版 `Asgard.exe`。

## 最新入學選擇：拒絕＝無副作用、可重問（2026-10-31）

使用者已決定 `nNewJoin01.dat STATE=REFUSE` 對應的**不入學**意圖在 Server Quest Domain 是 **no-op**：不給任務／獎勵／角色旗標、不傳送／換圖、不移除 NPC、不封鎖選項。允許本次對話結束，但每次新點 NPC 都可以再次取得全新合法 ScriptRun/context，**反覆拒絕後仍能選入學**。多玩家各自回答互不影響。只有經 A-012/A-023/026 證明 NPC→Script→C6C 選項的原生 UI，才可開 native; `STATE=ACCEPT` 同樣只是意圖，不直接當任務完成。見 [決策文件](three-policy-adjustments-20261031.md) 與 [驗收](../05-conformance/tutorial-refuse-reask-test-plan.md)。

### DEV-080 最新隊伍獎勵

共享怪物一次死亡時，各隊有效傷害累計後**最高傷害隊伍得獎**，該隊全體成員各得**全額經驗**、各自**一套獨立掉落抽選**；其他隊伍零獎，重送不重發。隊伍/傷害/死亡/掉寶都以 Server 自己的 PartyRevision、MonsterLife、個別 RewardLedger 進行權威結算。打平、離線/跨圖、入退隊變動仍待政策確定，不可擅自處理。A-014/009/025/007 為 Client I/O 取證，不是要分析者還原原服獎勵演算法。見 [獎勵驗收](../05-conformance/party-monster-reward-test-plan.md)。
