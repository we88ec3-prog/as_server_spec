# 可重複任務、UTC重置與領獎歷史

2026-11-08。延續[一般任務](20261108-town-quests-and-atomic-rewards.md)及[世界目標](20261108-quest-world-objectives.md)。使用者要求持續開發完整Server；本輪重複規則、冷卻／每日重置、次數上限及示範獎勵均為**Server重建政策**，不是主程式解析出的原服日常任務。

## 定義與狀態

QuestDefinition可選Repeat；null時省略序列化，舊任務definition／catalog JSON不變。啟用或變更政策須新key或明確遷移的definition revision，不得在同版規則偷改。

|欄位|約束|
|---|---|
|Schedule|Cooldown或DailyUtc；其他值拒絕|
|CooldownSeconds|Cooldown必須1..2592000秒，ResetUtcHour必須0|
|ResetUtcHour|DailyUtc必須0..23，CooldownSeconds必須0；整點UTC|
|MaximumCompletions|0表示未配置上限，1..65535限制成功領獎次數；系統仍拒絕int計數溢位|
|Repetition|角色可選進度：CompletedCount、LastCompletedAtUtc、NextAvailableAtUtc、CycleId|
|CycleId|每次接取產生非空隨機ID；世界目標ActivationId使用同一值|

未接取初態可以沒有Repetition。第一次接取建立count0及新CycleId；成功領獎增加count並保留本輪ID／完成時間。放棄清本輪ID、接取時間、擊殺baseline及世界目標旗標，保留過往完成次數和冷卻。一次性任務仍只能領一次，無Repetition欄位。

接取新輪把Completed改false、CompletedAtUtc清空，重新捕捉當下擊殺baseline，世界目標全清。上一輪的擊殺、到達或已發對話不能算新輪。前置條件使用「曾成功完成」，因此重複父任務進入下一輪或放棄，不會把已解鎖的子任務再鎖回去。

## 時間政策

冷卻從**成功領獎**開始，不從接取／放棄開始；拒絕、滿背包、錢包上限或交易回滾均不啟動冷卻。Cooldown的下次可接時間為領獎UTC加秒數。

DailyUtc取領獎後嚴格下一個重置整點。例如ResetUtcHour16代表台北午夜：11月8日15:59 UTC領取，下次11月8日16:00；恰好16:00領取，下次11月9日16:00。前一天接取、今天才領獎，歸今天領獎窗口，不能利用跨日接單連領兩次。此規則不是依Client時區、每日曆日或接受當時的窗口計算。

到達NextAvailableAtUtc的瞬間可以重新接取；到期前不行。已完成的任務必須先接新輪，再達標和領獎，不能把CLAIM直接當下一輪。若Server時鐘倒退到前輪下次可接時間之前，已接新輪也暫停領獎。使用權威UTC時鐘；本輪未提供跨節點時鐘同步或營運校時工具。

## 交易、歷史及重送

每次新領獎在同一交易完成交付扣物品、給物品／Gold／EXP、任務狀態、冷卻與次數、操作回執，以及領獎歷史。任一寫入失敗全部回滾。歷史記錄包含角色／任務／輪次、definition revision、唯一reward event、UTC及該次結算結果；主鍵為角色＋任務＋輪次，reward event另唯一。

一次性新領獎也記第1次。舊已完成任務不憑空補造歷史；原quest_ops回執保留，因此升級前已完成但新歷史為空是允許情況。讀歷史需當前擁有者租約與已提交載圖；只讀本人、同任務、大於afterNumber的輪次，升序，預設32筆、最高64筆。此為內部Server查詢契約，尚未宣稱原生任務日誌或公開管理API已接線。

重複任務的操作意圖包含ExpectedQuestRevision。相同舊operation ID及原參數重送，回舊結果而不重發資產；把同一ID配新輪revision拒絕。新輪使用新意圖ID。一次性任務原命令序列化保持不變，舊回執仍可重播。當前位置／租約／已載圖及revision檢查沿用原交易權限。

## 對話與示範內容

不增加opcode，不修改主程式，不變更既有ServerTownQuest模板、名稱或CRC。S44參數顯示已完成次數／上限和下次UTC時間；C6C回覆仍是既有ACCEPT／CLAIM／ABANDON／CANCEL。冷卻到期需重新開NPC視窗，舊窗不自動刷新或自動接取。

同一委託人的選擇順序：進行中→已符合資格的未完成一次性任務→已符合資格的重複任務→尚未符合資格的一次性任務→等待冷卻的重複任務→已達上限的重複任務→最後任務。避免循環補給擋住主線，也避免前置未完成的子任務擋住可接的循環父任務。

明確啟用TownNpcs的QuestsEnabled、AcknowledgeServerAuthoredQuestScript與RepeatQuestsEnabled，五城旅館各追加「重建：循環補給」：完成原第二關後，交1瓶生命藥水，領30Gold、20EXP、1瓶魔力藥水，領後60秒可重接，最多成功3次。可與世界目標第三關同時啟用，循環任務前置始終是第二關，不因開關第三關而改同一definition。

沿用既有固定帳號／金鑰／DB；獨立repeat設定檔不替換原兩關或世界目標設定。此內容只示範完整循環，不代表原服日常、原版旅館委託或新手流程。

## 升級與驗證邊界

新增quest_completions表，FK指向角色任務。已有帳號的SQLite建表前一致性備份，獨立tag `.pre-quest-repeats-v1-*`；暖啟動不重複，舊state／definition JSON不重寫。PostgreSQL有等價DDL；實例及完整還原驗收仍待做。歷史保留不自動截斷；營運歸檔／保留年限尚待規劃。

合成驗證包含政策非法組合、閏日／UTC偏移／精確重置時刻、三輪資產及唯一歷史、冷卻前後、放棄與前置、擊殺baseline、每日跨窗、重送／競爭、歷史或回執故障回滾、舊對話隔離、備份與舊JSON、S44/C6C視窗選擇及冷卻參數。啟動器只用臨時fixture，不啟動使用者環境。

本輪完整960項.NET回歸通過，0失敗／0略過；另4項Python啟動器fixture通過。原生Simkin執行／GUI排版、實際TCP、PostgreSQL實例與備份還原本輪未執行，不能由合成封包測試推定通過。

尚待：原服任務規則與日誌、對話分支／順序／多次計數、現有active definition升版遷移、管理查歷史及歸檔政策。固定秒數及每日窗口已完成本輪後端，不代表任務系統或全部Server完成。
