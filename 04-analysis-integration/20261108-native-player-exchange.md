# 原生玩家物品交換（2026-11-08）

## 來源與範圍

原件 Asgard.exe SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，Ghidra12.1.4，唯讀靜態分析，未操作使用者Client。本頁補[A-013](../03-analysis-requests/A-013-roy1-economy-wire.md)的原生入口、按鈕與receiver；不是原服封包實錄。**GUI交易仍待雙Client集中測試。**

玩家間流程已證為 **C4A／S42 ExchangeDialog**。HumanInfoDialog選其他玩家的交換control0x16 →464040(peerRef)送C4A0；拖物到其他Human的463C90也先送C4A0，再送物品意圖。不能把它當倉庫。

C17／S6E是另一條TradeDialog路徑：已查caller4BF4C0在HumanFlags0x2000及UserObject狀態下送C17 type80(selfRef)，54E260／54F1C0涉及UI1F與mode0／1／2。這不足以把整條通道命名成NPC barter，也不是本輪玩家間交換。此處不接它，不憑類別英文名稱合併協定。

以下為解密後body，不含opcode／framing。string8為CP950編碼後byte數的u8前綴，無尾NUL。

## C4A動作與精確body

|type|body（含type）|原生用途／producer|
|---|---|---|
|0|`00 + peerRef:BEu32`|請求交換；464040、463C90|
|1|`01 + peerRef:BEu32 + inventoryKind:u8 + bagSlot:u8`|從背包拖入物品的初始意圖；463B10／463C90，尚不含數量|
|2|`02 + peerRef:BEu32 + inventoryKind:u8 + bagSlot:u8 + quantity:u8`|數量框回覆；4641A0|
|3|`03 + peerRef:BEu32 + gold:BEu32`|目前金額的**絕對值**，不是差額；463EB0從文字以%u讀取|
|4|`04 + peerRef:BEu32`|拒絕邀請／取消；4B7A20拒絕分支、464FC0 control2、busy fallback|
|5|`05 + peerRef:BEu32`|自己確認；464FC0 control1／4650F6|

共用writer5725F0。peerRef是由S420／本地交換context保存的另一角色ref，不是原生交易revision或Server exchangeId。每個接收者必須使用一致的view ref；Server須把它對回認證角色與活躍交易，不靠Client提供ref授權。

489A90／489AB0把本地背包cell轉成kind與slot；本輪只開已審kind1、合法正值bagSlot。這與交換框顯示的offer格1..9不同。kind2另有全域cell換算，不因serializer支援便開放裝備或另一背包。

C4A2的數量是u8，最大255；S42數量框從既有InventoryEntry的u16總量取上限，因此大量堆疊可能超出這個wire能力。本輪已審物品stack20／衣服1不觸及此界線；不能宣稱任意大型堆疊都能正確交換。

## 邀請與接受：原生沒有立即accept packet

464040保留pending C4A0 packet在ExchangeDialog+70後送出，**尚未先開交換窗**。S420抵達時：
- ExchangeDialog465166先重設本地確認旗與部分控制；pending packet非空時直接464D70開窗，釋放pending。這是發起者自動開窗路徑。
- 無pending時，MapPane4B8F30在沒有其他pending／沒有既有Exchange UI的情況，建立AgreementPane mode1，顯示對方姓名。
- mode1按同意 →4B7A20(1)只呼叫464D70開窗；**沒有立即C4A accept回覆**。EDwf100ms timer只轉spinner，也不送ack。
- 拒絕 →C4A4。既有交換窗／其他pending造成busy時也送C4A4。
- mode1不是組隊mode0；4021E0只替mode0／3設定APct10000，因此不可套用組隊十秒自拒說法。Server自行設邀請期限並以S424關閉是重建政策。

Server可在recipient首次合法offer／money／confirm前將pending交易轉為accepted；這是原生缺少立即ack時的重建設計，不得宣稱原件有一個不存在的accept opcode。

## S42精確格式與效果

|type|body（含type）|原生處理|
|---|---|---|
|0|`00 + peerRef:BEu32 + peerName:string8 + badge:u8`|發起者pending自動開窗，另一方同意框；grid清presence|
|1|`01 + inventoryKind:u8 + bagSlot:u8`|向該物品擁有者開數量框；465213查現有bag entry數量，callback送C4A2|
|2|下列完整item row|往side所屬grid追加一項|
|3|`03 + side:u8 + gold:BEu32`|side0自己的金額control8；side1對方金額control7，覆寫絕對值|
|4|`04 + status:u8 + text:string8`|status非零關窗；status0進等待，停用confirm／money／自己的offer grid|
|5|`05 + side:u8 + text:string8`|side0自己confirmed，side1對方confirmed；兩旗齊才顯text並關窗|

reader57E9F0的六路表57EC0C、ExchangeDialog receiver465130、MapPane4B8F30與grid465520交叉核對。S42 type編號不能直接當C4A回覆一對一配對。

### badge不是角色／邀請旗

S420最後byte交4640E0：0只顯示姓名，非零顯示「[數字]姓名」，並按小於31／51／71／91切文字顏色。沒有用它區分requester／recipient或accept。它是否原服角色等級尚未獨立證明；Server選用權威等級作display badge時須標為重建選擇。

### S422完整item row

`02, side:u8, field0:u8, field1:u8, icon:BEu16, R:u8, G:u8, B:u8, useKind:u8, quantity:BEu16, name:string8, helpKey:string8, helpMode:u8, visualFlag:u8, extraCount:u8, extraCount×(key:string8,value:string8)`

- side0自己可拖入的grid（control6），side1對方grid（control5）。463DF0明確以0／1建構這兩個grid。
- field0／field1有reader欄位，但465520未用它們定位或覆寫。Server可在重建子集echo原bagKind／bagSlot，但**其原版業務語意仍未知**，不可宣稱它們會自動扣背包。
- icon、RGB（A由reader補255）、useKind與quantity由同版既有物品來源投影；中性色用RGB255，不把黑色0當無染色。
- helpMode0使HelpString查詢用模式2，非零用模式1；空helpKey仍會查MetaData，不是避開metadata初始化。visualFlag保留原生renderer參數，保守0。
- extraCount0為最小子集；未知長清單不填入。name、helpKey及pair字串均有各自string8上限；合併tooltip仍有本地固定buffer，不能因每欄合法便送無界總文字。

### grid是append-only，不是snapshot

465520在side符合後直接++counter再填下一格，正常顯示格1..9，無同slot去重／替換／delete分支。重送同一row會再加一列；超過9不可發送。

S420會清grid presence，但不重設append counter；既有ExchangeUI亦會在MapPane busy分支送C4A4。因此**S420不是可安全重置／unready現有視窗的snapshot包**。應每個已授權新增項目各投影一次；修改、減量或移除既有offer需要取消重開，除非未來找到完整原生機制。

背包的權威扣量／退款／完成交換仍需明確S0F／S10同步，不以S422畫面效果代替資料與背包投影。

## 金額只有OK才送出的限制

463EB0的完整直接incoming reference只有465095，也就是ExchangeDialog的OK/control1。OK必先送C4A3目前金額，再送C4A5確認；未找到OnChange／Enter／killfocus另外公布gold的producer。

因此「任一人ready後，對方任何新gold都取消」會讓正常雙方非零gold交易在第二人OK時自動失敗。不能用假unready包掩蓋此限制。

本輪Server選擇**單調利益改善**重建政策：已確認者的支出鎖定；尚未確認一方可增加已確認者將收到的資產，保留其ready，最後仍須自己確認；不得減少對方已確認的所得或修改已確認者支出。新增項目仍遵守append-only與9格，容量／堆疊／所有權／錢包上限在提交前驗證。這是本專案安全設計，不是原服交易規則。

## 確認、結果文字與取消生命週期

S425每方的confirmed旗不代表Server已轉移資產。Server必須先完成權威原子提交，再送會使兩旗齊的結果，否則Client可能先顯示成功關窗而DB未完成。重播不得二次扣加。

S424的text由ChatInput430080→42FA90直接加入history；不需Script／S44。S425的text只有兩旗齊時經442570 MessagePane顯示，再464C80關窗，也不是Script。status0的S424不清confirmed旗，不能當unready。

464C80清peerRef+48、對方gold+6C、關窗、清兩grid counter、解除本機Trading狀態。MapPane對S424另關pending同意框；取消callback可能回送C4A4，因此Server必須接受已關閉交易的冪等取消，不斷線／不重開。

交易期限、距離、同圖、session lease、金額與物品守恆、reservation、離線撤銷、重播receipt及存檔交易邊界，均是Server設計。Client UI沒有提供可直接拿來做持久交易版本的nonce。

## 待測與證據

完整Evidence位於player-exchange-native-20261108；本頁只公開可攜欄位／位址。需原生雙Client驗收：請求／拒絕／接受、拖入與數量框、雙向gold的OK順序、9格邊界、取消／逾時回送、斷線／離場撤銷、完成後背包與錢包、重送不重加row／不二次轉移資產。合成codec或TCP通過不能替代這些畫面驗收。


## 首次確認前的報價檢視保護（Server設計）

recipient同意沒有原生ack，Server不能知道何時已看見目前報價。若recipient第一個動作就是OK（C4A3後C4A5），不可把該次C4A5直接當成已核對所有報價的最終同意。可在此時才建立accepted context並投影目前報價，忽略這次確認，以S0A17要求核對後再按OK；後續同值C4A3為NoChange，第二次C4A5才ready。若先前已經有合法拖入／數量回覆並取得報價，則不必增加這次檢視操作。

原生允許第二次OK：464FC0送C4A5後465107只停用control8金額編輯，未停用control1，也不設定自己confirmed旗。control1被停用是在S424等待／S425自己confirmed的Server回覆後。因此這個檢視保護不需改Client，但不可先送等待／confirmed回覆再要求第二次OK。首次OK後金額可能已不可再改，需取消重開；這個限制應在測試提示說清楚。實際GUI仍待驗收。
