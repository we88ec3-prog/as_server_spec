# 雙方同意的玩家決鬥與原生攻擊投影

使用者要求持續完成 Server 功能；本輪補上 PvP 的可玩決鬥流程。**決鬥邀請、同意、距離、時間、傷害、最低1HP及不發獎勵，全部是 Server 重建設計。** 沒有找到原服決鬥 UI／同意封包或原版 PvP 公式，不能將本輪規則當成原版還原。原始 EXE／素材未修改，原生 Client GUI 待測。

## 原生界面依據與邊界

沿[玩家指定目標分析](20261108-native-player-targeting.md)、[共享Human生命週期](20261108-native-remote-player-lifecycle.md)與既有傷害投影，不新增猜測 opcode：

|方向／封包|本輪用途|
|---|---|
|C0E kind0＋string8|`/duel` 管理指令；Server命令，非原版決鬥 UI|
|C13 BEu32 ref|對已投影Human的普通攻擊意圖；ref不是角色ID或傷害值|
|C0E kind2＋技能文字|無指定目標技能的一次結算入口；指定技能的前導不結算|
|C65 kind:u8,slot:u8,ref:BEu32|既有mode2指定傷害技能結算；保持Spell／Skill分庫|
|S0A subtype0x11|只向相關角色顯示邀請／開始／勝負公告|
|S11、S13、S08|面向、攻擊及傷害數字、本人資源更新|

原件 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。既有原件分析已證 mode2 可選 Human；S62 Field2=0 不經額外傷害型Human／ALT限制分支。本輪沿現行重建技能的 Field2=0，**由 Server 的雙方同意取代未還原的原服戰鬥區／ALT政策**，並未宣稱接好原版 PvP 陣營旗標。C13 在原生畫面是否需額外按鍵選人，也仍待實測。C65 僅有ref，Server必須自行驗權；可選物件不代表獲准傷害。

## 玩家流程

1. 雙方同圖、同內容revision，距離每軸不超過6格、已完成載圖、HP至少2，且均沒有其他未結束決鬥。
2. A 輸入 `/duel invite 角色名稱`。名稱由 Server 查詢在線角色，與登入帳號名分開。B 收到公告；其他玩家不收到私人邀請。
3. B 於60秒內輸入 `/duel accept` 或 `/duel decline`。只有收件人能同意／拒絕；A 可 `/duel cancel`。發邀請本身不授權攻擊。
4. 同意後最多300秒。雙方可使用普攻、面向／周邊近戰傷害技能，或指定直接傷害／指定範圍傷害技能攻擊唯一對手。範圍技能在此只命中該對手，不波及旁人。持續傷害及怪物專用減益不能傷害玩家；治療／增益仍沿原有自身／隊伍權限，未因決鬥放寬。
5. 受到足以歸零的決鬥傷害時只降到1HP，決鬥結束並記勝負。亦可 `/duel surrender` 認輸。雙方 HP／MP／SP 保留實際剩餘值，不免費補滿。`/duel status` 可查詢當前／最近一場結果。
6. 逾時、任一方離線／租約替換、死亡或生命代次改變、HP不足2、換圖／載圖中、距離超過6格時，撤銷本場同意。回到原地或重新登入不能延續舊同意，須重新邀請。

不發經驗、物品、金錢、技能熟練度或排行分數；沒有死亡損失、墓碑或原地復活操作。此處僅是決鬥傷害不致死，怪物等其他傷害仍使用既有正常死亡流程，不把角色設為全局無敵。

## 可獨立實作的權威模型

Policy revision `reconstructed-consensual-duel-v1`。DuelState 保存：Server生成id、revision、Pending／Active／Finished、雙方角色與帳號、各自精確World generation／connection、各自LifeGeneration、角色名稱快照、map_ref／content_revision、ExpiresAtUtc、winner_character_id及end_reason。每名角色只有一個latest pointer；Finished保留歷史，不能讓任一角色同時參與兩場Pending／Active。

狀態轉移必須在驗證目前租約與權威位置後執行。按 character_id 固定順序鎖完整雙方租約，再取決鬥序列化gate；不可先鎖決鬥，再任意鎖第三名角色。挑戰另一個已在決鬥的角色回Busy，不在不完整鎖集合中替第三方清理其舊決鬥。對方或其原對手讀取狀態時才依完整鎖集合撤銷過期狀態。若鎖前／鎖後latest id不同，本次讀取不拼接新對手，留待下次合法讀取。

接受／拒絕／取消／認輸須帶Server已讀到的duel id與revision，核對行為者角色及phase。舊revision不轉移，旁觀者無權查改別人的決鬥。Server API 的operation id與角色為唯一收據key；同意圖重送只回收據，不再施加效果，不同意圖重用同id拒絕。原生C0E／C13／C65沒有此id，由Host為每次獨立輸入生成，不能聲稱可識別任意舊wire重送。

## 傷害、成本與事件同交易

攻擊接收 Host 發出的可視 Human capability：ref、精確對方租約、LifeGeneration及完整位置revision。交易內重新核對雙方目前租約／載圖狀態、Active決鬥、對手、生命、map與當前兩個位置，再核ref的穩定Human配置。舊位置／舊生命、未投影對手、旁人、假ref、跨圖與未同意皆不能扣資源或造成傷害。Host另按既有靜態map格規則核視線，交易核對位置使該視線判斷不套用到另一處位置。

普攻限相鄰一格；重建直接指定魔法最多6格。不能同格傷害，不能把圖上最近玩家當成未經同意的目標。非指定近戰技能只在目前Active對手符合面向／範圍時轉入決鬥；其餘怪物流程保持原規則。

重建普攻基傷=`5＋有效STR/3`取整，再加裝備AttackPower、套角色衰弱減傷，再減對手裝備DamageReduction，最低1。技能基傷沿目前已學rank的Power／ScalingAbility／divisor，與普攻使用同一裝備／buff／衰弱來源。實扣=`min(計算傷害,對方當前HP−1)`。不把加成寫入永久能力。各rank的MP／SP消耗、職業／等級／已學檢查與冷卻沿技能目錄，另有500ms持久化攻擊節流。未命中合法對手不扣費、不啟動技能冷卻。

成功技能只更新ReadyAtUtc及技能狀態revision，**不增加SuccessfulUses／rank／經驗**。角色資源、目標HP、面向／位置revision、冷卻、節流、勝負、操作收據及已提交視覺事件同一交易；任一儲存失敗全回滾。收據重播不重發舊攻擊畫面。

視覺事件為玩家來源與玩家受擊者，均固定租約／生命／位置。攻擊者自己ref=1、對手使用穩定remote ref；受擊者把自己映成1、來源映成已顯示的remote；旁觀者將兩者均映成各自已顯示的remote。只向當前同圖、生命與可視物件相符的觀察者投影S13；不對未spawn ref播放傷害，不用怪物S5F移除Human。目標HP由本人S08與既有隊伍狀態更新，1HP決鬥落敗不觸發死亡姿勢／LifeGeneration改變。

## 持久化與升級

四張獨立表：duels(id,state_json)、duel_latest(character_id唯一,duel_id)、duel_ops(character_id,operation_id唯一,command_json,result_json)、duel_gate(singleton)。既有資產、物品定義、技能catalog及管理金鑰不改。已有帳號的SQLite在新增缺少決鬥表之前一致性備份，單獨本功能升級標記pre-consensual-duel-v1；順序重跑不重複備份。備份讀取須證明原角色狀態仍在，不能只檢查有一個檔案。未遷移使用者現有DB，未重啟使用者遊戲／Server。

SQLite與PostgreSQL沿相同交易與固定角色鎖序，PG取相應row鎖與gate。此為程式設計範圍；本輪只執行SQLite實例，PG實例等價仍待測。Server重啟不能把舊儲存租約當成新Client授權；新租約重連會撤銷舊場次。

## 驗證與剩餘範圍

新增24項測例（Domain7、Store15、Host2），完整.NET回歸 **1126通過、0失敗／0跳過**。涵蓋非致死界線、同意／旁觀者權限、假ref／舊位置、兩階段逾時、租約／生命／距離／載圖失效、重疊邀請、裝備加減傷、遠程首擊／資源／冷卻／不增加熟練、勝負與視覺失敗的整筆回滾，以及備份內容與順序重跑一次。

真TCP使用三個合成玩家，三組情境通過：未同意不扣費後四格C65魔法首擊，三端收到同額傷害且self／remote ref正確；距離拒絕、認輸、拒絕、關閉對手撤銷；自有Server重啟保存資源與已終止同意，新決鬥普攻到1HP勝負且不出墓碑／獎勵。沒有強制TCP併發競爭或原生GUI結果。

Host SHA256 `677c3d9f9934aa7dd399e1d89d697c3d62b33d8614b244da89127f108a47faf1`，八組件bundle `fc0d90f77e93b26c2b92bbaeaae9d75c81636f16d83e75fe2f212bdf76c86bd4`，測試前後與最終核對一致。三份進度表更新38個相關值，無關儲存格變更0；既有人工回報保持原值。原生Client與PG實例驗收仍獨立。

原生集中待測：兩帳號同圖→邀請／拒絕→重新邀請／同意→遠程Spell首擊→相鄰普攻／空白鍵／快捷技能→旁觀者看傷害與動作→1HP結束→禁止繼續傷害→認輸、換圖與同Client重登。沿既有固定開發環境與原帳密，不需重創或換金鑰。

未完成：原版決鬥UI／PK陣營旗標／ALT契約、競技場與公會戰、PvP持續傷害／減益、戰績排行與反刷獎勵、跨服對戰、原服數值與PvP特殊技能平衡。完整Server目標仍持續開發，不能把本輪決鬥當成全部PvP完成。


## 既有資料升級驗證紀錄

F28-01-T02 的舊證據累積已超過Excel單列可讀高度，本輪將進度表改為摘要，以下完整保留更新前原文。這是歷次紀錄，不代表本輪重跑所有舊升級或完成完整還原演練。

> SQLite新增表有備份策略，完整還原演練待補；本輪：新增技能庫升級標記，既有SQLite在補kind前一致性備份一次；已實際讀備份確認舊JSON與未登入角色保留。；本輪：v1或v2精確內建目錄升級v3前SQLite一致性備份，核對備份舊指標；暖讀不重複、不重領、不降級。；本輪：新增quest四表前先備份，交易及故障回滾覆蓋物品／Gold／EXP／完成收據。；本輪：新增quest_dialogues前一致性備份，暖啟動不重複、原JSON不重寫；位置及多目標故障回滾已覆蓋。。後續增量：quest_completions單表升級前備份一次，暖啟動無重複；歷史或操作回執故障時資產與冷卻一併回滾。。後續增量：新增三張拒收表前SQLite備份一次；state／清queue／receipt任處失敗整體回滾，暖啟動不重複。。後續增量：friend_state／friends／friend_ops三表前SQLite一致備份一次，備份內缺新表已驗；增刪故障回滾且暖啟動不重複。；2026-11-08續：舊SQLite缺公會四表時先一致性備份再同交易遷移；測試實讀備份確認無新表，後續啟動不重備份。；2026-11-08續：新增單表periodic_skills及來源/期限索引；舊SQLite加表前一致性備份一次，測試讀備份確認無新表且重開不重備份。；2026-11-08續：新增單一monster_debuffs表及來源／到期索引；舊SQLite缺表時先一致性備份，不重置角色或金鑰。；2026-11-08續：v1／v2／v3精確內建目錄可升v4，先SQLite一致性備份一次；物品ID／位置／版本及舊starter收據保留，拒絕降版。
