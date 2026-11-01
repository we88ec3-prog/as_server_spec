# 三層圖塊離線預覽與地理核對界限

日期：2026-11-01。完整人工測試入口已準備，當時尚無新的session／DB或遊玩
回報。本輪繼續以素材核對地理，不重開Server、不改候選profile或既有進度。

## 原件讀取與索引修正

EXE SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，
REA／Ghidra12.1.4；[精選指令](native-tile-layer-selection-20261101.json)。

MapData loader0x4b33a0把每個raw10-byte tile的前三個u16原樣存入本地17-byte
tile。0x4bce70繪製時依序讀三個word，略過0，對非0呼叫0x54cf10。後者依
layer選storage，將word-1交給0x483c50。因此不能直接把raw word當zero-based
影格索引；最初離線假設的直接索引有一格偏差，已更正並保留舊預覽在本地。
Server的MAP存取／C35／移動邏輯沒有套用該錯誤假設，本輪不需改Server封包。

只繪第一層也不足以辨認場景：Map4001第一層幾乎全水面，加入第二、三層
才看到上方的冰雪平台。不得把ground-only圖像當成全部可見地形。

## 有界YPF子集

本輪研究工具只接受已觀察的YPF17、48×32、header kind3／flags1、單group
Tile庫。讀palette256×u16、data base及逐frame descriptor；支持兩個分支：

- frame flags0x0c：無alpha mask，palette stream長度需等於frame像素數。
- frame flags0x04：逐列alpha RLE；每run的高byte為數量、低byte為alpha，
  本批只接受0..248且為8的倍數。每列必須覆蓋精確width，非零alpha數須等於
  palette stream長度。顯示時alpha248縮放為255，原生取整方式仍未驗。

索引、descriptor、mask offsets、palette channel及frame bounds都須在庫內；
不支持的frame以洋紅標記，不能當作透明或直接忽略。最多僅處理48×32範圍。
目前RGB565與MAP三個header word選各層庫的解釋仍需完整loader／renderer
交叉核對，不能把整套離線圖稱為原生畫面。輸出不得位於原遊戲素材目錄。

## 本輪素材結果

對Map6、7、39、1、1001、2001、3001、4001的三層引用逐一解碼，全部沒有
unsupported tile reference。使用五份World Tile庫與已鎖SHA的MAP庫；
[素材身份、尺寸、預覽hash及工具hash](tutorial-tile-preview-metadata-20261101.json)
可供後續比對。預覽PNG、原件與完整REA都只留本地，不提交公開庫。

可見的幾何特徵屬離線分析觀察：

|圖|可見特徵|不能據此推定|
|---|---|---|
|1|圓形草地平台、放射狀步道及長橋|只憑本地World圖的「米魯里斯」標籤就當成原服綁定|
|7|小片長形室內木地板|原版新手學校、教室NPC或招生位置|
|39|更小的室內區域|與Map7的功能或原服傳送先後|
|1001|森林邊緣與分岔土路|盜賊城或任何職業目的地|
|2001|廣場、分岔鋪面及城牆局部|只看城堡風格就推導戰士城編號|
|3001|分散的石質區域，省略物件後有大量空白|不能憑缺少冰雪等特徵直接改判城市，仍缺物件層|
|4001|水面及冰雪平台|冰雪或湖面本身不能唯一確定職業／城名|

靜態／動畫物件、建築、陰影、NPC與UI不在本次輸出內。地圖檔的tile flags
與視覺圖層不同；不可用本工具的圖像／透明區推導Server可走範圍或出生點。
本輪沒有提升五條候選職業城鎮為verified，也沒有更換待測profile。

## 接續

將本批來源hash與幾何特徵用於[完整實機清單](../05-conformance/20261101-complete-tutorial-manual-run.md)
的場景核對；必要時再補物件層及原版地名來源。測試者的操作、Server的持久
進度、Client可見畫面仍要分別記錄。353項既有Server測試與五職業TCP不因
本輪離線研究升級為GUI通過，整體目標保持未完成。
