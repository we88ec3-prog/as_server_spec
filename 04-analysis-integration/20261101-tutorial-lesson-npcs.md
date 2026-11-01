# 生活／戰鬥教學NPC與對話觀察紀錄

## 原件確認與使用者需求

**使用者需求**：完整新手教學主線優先，流程接齊後再安排一次人工測試；
新手場景可能需要普通攻擊打怪。普通攻擊是待完成的玩法，不是關閉對話可替代的條件。

本輪對原始Script重新驗八份資源的SHA、bounded zlib／BE版本與UTF16長度、
嚴格CP950 CRC，並檢視生活／戰鬥callback。公開身份、函式hash及literal控制
分支摘要見[腳本介面索引](tutorial-lesson-script-interface-20261101.json)。
它是靜態索引，沒有執行原件，也不是完整Script語法／動態流程分析。

|原件|SHA256|嚴格CP950 CRC32|
|---|---|---|
|nNewLife01.dat|7caa5c656c7ab50b9701506e0d137f7fb1550f6eb6fd7ceb1bd0b3e72f169414|1256ae8c|
|nNewWar01.dat|3d3590a7f4a346cafa538d8216091a6f6073c6aab146d696d0fb2736100f2453|7bab73a4|

兩者MerchantTalk分別進LifeMessage01／WarMessage01，再使用QuestDialog、
QuestSelDialog及MultiHelpDialog顯示內容。這兩檔沒有literal SendReply呼叫。
初頁CANCEL與後續若干CANCEL都可能Dispose runner；WarMessage05的最後OK
也只Dispose，沒有向Server回報最後一頁或考核完成。MerchantDialog的TALK
回覆仍存在，因為它來自共用wrapper，不能把兩份依賴沒SendReply擴大成沒有C6C。

所以同一C6C Dispose無法區分「初頁取消」「看完部分內容」「最後OK」，也不能
證明發生攻擊／擊殺。本輪沒有改原腳本加新回覆，沒有捏造STATE=OK。

## 復原Server政策與已實作行為

兩種教學以各自獨立NPC ref、精確map/ref與revision、位置及Script CRC配置。
目前使用已確認可顯示的helper4037候選造型與100%動畫速度，放置與NPC身份
仍屬明示復原版設定，不能稱為原版生活／戰鬥講師的位置或外觀。

進圖只生成符合目前地圖及版本的講師。C43近距離點選需當前World owner、
已提交載圖及同revision的持久入學事件；符合才發Merchant主runner，附上
MerchantDialog、QuestDialog、QuestSelDialog、MultiHelpDialog與相應nNew依賴。
每次發行獨立非零context，與招募員、就職指導員、傳送師互斥，不覆寫共用全域。

本run只接受單一reply key TYPE，值只能TALK或ABORT。TALK記錄曾進入教學；
ABORT終止本run，不再允許TALK翻案。STATE／JOB／自訂milestone等欄位拒絕。
處理同context Dispose4時：

- 從未TALK，或已ABORT：只關閉，不記教學事件。
- 已TALK、未ABORT：再次驗owner／來源地圖／距離，以目前已保存的位置及
  version交易寫一筆`life-dialogue-closed`或`war-dialogue-closed`。
- 重送Dispose冪等，不重寫事件。Close2必須在Dispose之後，不能代替它。

事件的正確語意是**Server發行的教學run曾交談後關閉**。使用者可能是在初頁
取消，仍只能據實記「交談後關閉」，不能宣稱讀完每頁或原服考核通過。
以這項觀察作為出圖前置條件，是復原Server政策，需明示其證據上限。

每種事件key由固定Lesson kind產生，配置或Client不能將它改名成
`practice-attack-resolved`。後者仍須真正Server攻擊結算寫入。
此增量不改完成旗標、不發獎勵、不直接傳送；離開遊戲清除對話權限，
事件依角色／key／revision保存。已關閉的舊context只保留最多8個供遲到cleanup，
舊reply不重授權；載圖途中亦只忽略已確認關閉的自有context cleanup。

## 設定與傳送條件

本地Development按Life／War分別啟用並明示來源map、revision、座標、唯一
NPC ref、名稱與Client素材位置。啟動時驗全部依賴及顯示素材hash；未知kind、
重複／跨角色ref、無內容目錄或出生位置不可站立皆拒絕。教學內容revision
包含Script、來源場景／放置、入學版本及`talk-run-closed-v1`觀察政策身份。

傳送條件可用`Lesson=Life`或`Lesson=War`引用對應已配置講師的固定事件與
revision，免手填生成的版本字串；未配置的講師不能被引用，引用時也不能另帶
Key／Revision冒充不同事件。其他真正遊戲事件仍用明示key/revision條件。
實際預設學校／城鎮尚未綁定，不能把這項配置能力當作已完成整段教學。

## 驗證及下一步

329項Server測試通過。既有五職業出圖測試現在經C43/C6C Host處理器產生
兩項教學觀察，不再直接注入它們；仍只對尚未開發的攻擊事件做明示合成注入。
測試也證明兩項教學對話關閉後沒有攻擊事件，缺攻擊條件時仍不能出圖。

另驗證兩種教學未入學、未TALK就Dispose、偽造STATE=OK、ABORT後TALK、
Dispose前Close均不能新增事件；重送、對話互斥、舊context cleanup、移動圖載入
期間的cleanup及設定selector限制都有覆蓋。這些是合成Host／SQLite測試，
不是原始Client已實際顯示全部教學頁或完成戰鬥。

剩餘主線：真正普通攻擊／怪物與攻擊結算事件、學校／城鎮角色綁定、數字
職業投影、完整啟動配置及整段GUI測試。使用者目前不需操作，也不重啟其運行中Server。
