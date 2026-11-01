# 教學主線資源重整與對話回覆接線

> 後續增量：招募員顯示／動畫／頭像已由使用者確認；[在線切圖Host](20261101-world-transfer-transaction.md)
> 及[選職指導員／持久選擇](20261101-tutorial-career-advisor.md)已有Server實作。
> [分職業傳送師及完成交易](20261101-tutorial-town-departure.md)亦已接線，真實教學事件仍待接齊。
> 下文「尚未接線」屬當時範圍，原版地圖綁定及完整教學驗收仍未完成。

## 使用者優先序

使用者最新指定「先以新手教學完成為主」，並補充測試期間可繼續換衣／
獨立衣色開發。管理端切圖是測試用途；技能也可能在正常遊玩觸發切圖。
這是需求與工作排序，不是分析推導的新原服規則。

## 本輪實際持有及核對

直接讀取原始Script目錄的13份nNew資源與Born、Merchant、QuestDialog、
QuestSelDialog、MultiHelpDialog、PaperDialog，共19份。全部存在，不再
沿用舊A-026「本機缺PaperDialog及nNewJoin01」的歷史限制。

對每檔檢查zlib完整性、解壓上限1MiB、BE版本1及UTF16 code-unit長度，
保存原件SHA與嚴格CP950原文字CRC；不重序列化XML再算CRC。公開的
[資源身份索引](tutorial-resource-route-20261101.json)不含原始腳本內容。
key／reply索引採literal掃描，不是完整語法／全程執行分析。

|資源|從該資源可確認的用途／介面|不能據此推定|
|---|---|---|
|Born|歡迎及招募員(31,29)指引；此紙張已實機顯示|原服map_ref、NPC entity綁定、畢業|
|nNewJoin01|學校加入候選對話，STATE=ACCEPT/REFUSE|接受加入就是完成；此檔就是Main入口|
|nNewLife01／nNewWar01|生活／戰鬥說明對話；本輪未在這兩檔找到SendReply|整個教學不需戰鬥，或必須殺固定數量的怪|
|nNewJob01|讀JOBALD/JOBRET，回STATE及JOB；包含五種職業名稱選擇|名稱對應的數字職業代碼、能力／裝備／原服資格|
|nNewTeleport01|讀JOBRET；SUCC走已選職的出發對話，回STATE=OK；否則取消|確切目的地map_ref／xy、原服完成交易時點|
|nNewStartPoint系列|若干JOBRET／SPELL／城鎮等參數與傳送點對話|所有檔案都屬新角必經教學，或檔名直接等於map_ref|
|Merchant|Main(args)建立ServerParam與NPC UI全域；nNew系列提供MerchantTalk等函式|可以獨立啟動沒有Main的nNew檔，或省略所有依賴|

部分Guild／StartPoint資源含嚴格CP950無法編碼的字元，索引CRC記null，
須核對Client原生轉碼／替代字元處理；不得猜CRC後送給真Client。
主要Join／Job／Teleport候選可按嚴格CP950編碼。資源存在不等於原服
NPC／任務規則已找回，也不等於原始Client已執行該段腳本。

## C6C選項回覆

REA原件writer0x575210，證據
`ev_78de5bbeebab4156741f475aa2cced960617a78e69ae64287a9339ab013efe76`，
與既有A-012/A-023一致：subtype1→script:string8→context:BEu32→
count:BEu16→重複key/value兩個string8；不是固定0x400-byte wire row。
原件EXE SHA沿用主線db3df616…，工具Ghidra12.1.4。

私有roy `e12cec2`補對話回覆解析；273項測試通過，包含中文職業值、
所有截斷位置、尾隨bytes、重複key與lifecycle冒充reply。資源上限是
Server設計：body4096bytes、pairs最多16、context非0、key不可空或控制字元。
字典key採Ordinal，值保留原意，不在codec把JOB轉成職業權限。

解析器目前尚未啟用未發出的NPC對話。Host必須先綁issued ScriptRun
至owner／world lease／NPC／map revision／runner name／context及允許
回覆schema，才可消費STATE/JOB。Merchant wrapper的runner name可能
與依賴nNew檔不同，須依實際發出的runner辨識，不能只拿JOB或字串名認領。
C6C(2/4)仍只是關閉，不改tutorial_completed。

## 主線交付順序與完成驗收

1. 讓招募NPC可見、可點選，追通實際C43／C39及Merchant啟動／依賴。
2. 加入對話接受／拒絕、關閉／重開與重播隔離；保存真正已核驗進度。
3. 職業選擇／確認與Server數值職業、資格的映射，未證處標記復原版
   自訂政策，不能把Client回STATE=OK本身當作授權。
4. 傳送員接到已保存選職結果後，經共用World transition載入已驗目的圖；
   完成、獎勵（若有證據／明示自訂）及出圖checkpoint保持交易／冪等。
5. 使用者從新角色實際走完必要互動到下一場景，斷線／重登能接續，
   完成後不回未完成狀態，拒絕／重送不重賞。這才是本輪完整教學目標。

目前只完成資源與reply基礎，尚未宣稱NPC、選職、出圖或整套教學通過。
原服規則未知時繼續分析並明示復原版設計邊界，不要求使用者重傳已有檔案。
