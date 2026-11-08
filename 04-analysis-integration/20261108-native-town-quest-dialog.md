# 城鎮任務：原件對話與Server自訂原生UI

2026-11-08，延續A-012／A-023。本輪唯讀解包Script原件，不修改或啟動Client／Server。原始EXE SHA256為`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。既有REA證據沿用同SHA的[A-023完整入口契約](../task_a/roy2/A-023-script-entry-contract.md)，本輪未開REA session；原生GUI未測。

## 選擇與界線

**未找到可直接以Server參數替換任意標題、說明及三動作的現成安全任務腳本。** QuestDialog與QuestSelDialog是可用UI helper，但沒有Main；Merchant+nSuInn01只能依旗標選固定Quest01／Quest04文案。不能把「擊退波特」的原件對話當作自訂摩斯任務，或把按領獎視為已完成Server條件。

可行的重建方式是：使用已證S44資源更新與Main入口，提供**全新唯一名稱、Server自寫的Simkin XML**，用原生CreateDialog／StaticText／TextButton／SendReply。這不需要改EXE、覆寫原件Script、猜新opcode或把任務訊息塞成銀行交易。Client會建立新名稱的本地腳本快取；這是新重建內容，必須明示，不是原作任務還原。

已準備私有離線草稿ServerTownQuest_20261108_v1，具有標題、說明、NPC名與接受／領獎／放棄／取消。它使用原件已證native API，尚未在Simkin／原生GUI執行；因此是可開發候選，不能把XML解析成功稱Client已通過。Server任務engine可先獨立驗證，UI需隔離fixture後才一般啟用。

## 原件固定Quest04的最小閉包

S44主腳本Merchant，依賴MerchantDialog、nSuInn01、Quest04、QuestDialog、QuestSelDialog。全部原件壓縮檔SHA與嚴格CP950文字CRC如下：

|script|SHA256|文字CRC32|
|---|---|---|
|Merchant|6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350|e9b389cf|
|MerchantDialog|ed194a77a669cbd8f83fbbd01bb08ed0f800b122695cc204a3a12f002f945095|9267d99d|
|nSuInn01|59fa9643abc3cea4a5ef4ad014b4fd0a0b0d229a46ef559cf87372bcef595b31|bef22702|
|Quest04|73364cfdf4414ebd0da1e72f6edf1bce3a7e5d68e0f5198e1f6aaaa464dd248f|df339db5|
|QuestDialog|13f068d8053ea7e7b0231357c318bc6effae867888b94305820fe483a17a02dc|d4844b07|
|QuestSelDialog|06868b472cf874e08077ef29ee42edd9c0d4aa1cef304699658b091a4b1c8366|c64e29a3|

提供Merchant基本參數TILE、MNAME、GREETING、UGOLD、UBAL、UAGOLD、UABAL、UCOLOR，並設Quest04狀態；不提供TYPE才走初始選單，禁止無關買賣／銀行旗標。nSuInn01.DoesTalk見Quest01或Quest04存在才true；MerchantTalk優先Quest01，否則Quest04，因此本閉包**不可同時提供Quest01**，否則會轉向未附的Quest01函式。參數TILE0可以省略portrait；非0須沿已驗Portrait索引。

原件Quest04接收狀態NOT、DOING、FINISH、ALREADY、LIMIT。點TALK先回C6C1的TYPE=TALK，隨即本地進Quest04，不需要Server再送一次start。後續ClientReply累積TYPE：

|操作|額外回覆值|
|---|---|
|接受最終OK|Quest04=T、Quest04State=ACCEPT|
|拒絕最終OK／選擇頁CANCEL|Quest04=T、Quest04State=REFUSE|
|進行中OK|Quest04=T、Quest04State=CONTINUE|
|FINISH頁OK|Quest04=T、Quest04State=FINISH，並呼叫ShowInventory(true)|
|完成提示OK|Quest04=T、Quest04State=ALREADY|
|限制提示OK|Quest04=T、Quest04State=LIMIT|
|FINISH頁CANCEL|04=1（不是Quest04State=REFUSE）|
|初始選單CANCEL|TYPE=ABORT|

上述都只是意圖。原件沒有提供可從文字直接推出的擊殺數、地圖、掉落率或實際獎勵表。Quest01另有Quest01State=ACCEPT/DONE/REFUSE/SKIP與NPC=Banker/Inn分支；nNewJoin01是固定入學STATE=ACCEPT/REFUSE，不是通用任務API。

## 自訂任務UI的原生通道契約

### 資源與啟動

S44 body，不含opcode/framing：

- start 1/0：u8(1),u8(0),string8 name,BEu32 context,BEu32 textCRC,u8 dependencyCount,dependencies,BEu16 parameterCount,pairs。
- cache update 1/1：u8(1),u8(1),string8 name,BEu16 compressedLength,zlib bytes。
- **update壓縮內容是完整XML的CP950 bytes，不能送原件.dat的version/UTF16容器。** Client解壓、依語系轉Unicode，更新時自己建立本地快取容器。
- 文字CRC=標準CRC32(CP950完整XML，不含NUL)，保留原換行，勿重新序列化後仍用舊CRC。
- 新名稱缺檔時start觸發C6C0(name)，再給精確同名update，既有pending queue齊備後執行Main。不可用錯CRC強迫重抓，也不使用S44(1,3)清快取。
- 名稱只允許固定ASCII字母／數字／底線，拒絕路徑、斜線、..；每次改稿使用全新版本名，遇同名未知既有檔案不覆寫。只發Server內建allowlist內容，不允許使用者提交XML程式。

### 自含草稿

ServerTownQuest_20261108_v1具有Main(args)及TownQuestProc(dialog,control)，**script依賴清單為空**。Main直接使用原件QuestDialog／QuestSelDialog所用的native UI API；沒有未解析MerchantDialog_Prepare，也沒有迴圈端點歧義。

參數：TITLE、TEXT、MNAME、QUESTKEY、CAN_ACCEPT／CAN_CLAIM／CAN_ABANDON，以及ACCEPT_LABEL／CLAIM_LABEL／ABANDON_LABEL。三個CAN只有字串1才建對應按鈕；Cancel始終存在。TITLE、TEXT只作UI文字，不能注入程式。Server應提供可信配置文案，遵守CP950 string8的255byte上限；首次fixture宜用短標題和數行短說明，實際換行／裁切GUI待測。

操作回C6C1(name,context,pairs)：

```text
TYPE=TOWNQUEST
QUESTKEY=<Server已發的任務key>
ACTION=ACCEPT | CLAIM | ABANDON | CANCEL
```

接著dialog.Dispose及client.Dispose，後者C6C4；因SendReply已設replied，不再需要no-reply C6C2。生命周期4/2都不能發獎。Server須驗實際已發按鈕、context角色／lease／NPC／位置／任務revision，拒絕客戶端偽造CAN、條件或獎勵；一次已消耗context不得再次執行，亦不能把另一輪新按鍵當內容hash重播。

離線草稿固定身分（尚未Client測）：

- XML UTF8檔案SHA256：2f0e846df49d33d3faa16afdd6a94a49781b9afa3ff223d8313f2d98c2599aad。
- 同文CP950：2072bytes；CRC8085da9d；zlib751bytes；S44 update body783bytes。
- XML declaration保留原件慣例UTF-16，wire先以CP950送入Client轉Unicode流程，不應按declaration直接把UTF16bytes塞update。
- 具體模板與離線body只存私有raw，非原遊戲素材；部署若調整空白／換行須重算CRC與SHA。

唯一直接資產是Script.dat／QuestFrame.ypf object0/frame0，以及native按鈕object14。Script.dat SHA5307cdc9e8f7f66c55085f29b2718774d4fd7de74c4a92c0c6b70c4f8e0753e0；QuestFrame.ypf member4 offset556084、179316bytes，SHA3b136160fb57f8d04661c344f90165cfd3e02c8f10248d4b4cf261d0706cc4d9。不載入portrait時無Portrait依賴；不是以Merchant nSuInn假裝所有城鎮NPC原版都有任務。

## 有界負例與任務日誌

原件316個Script外層皆按1MiB cap解包，315份可解析XML，NDW為非XML。共找到2499個function名稱。TasksDialog／SortsDialog／TextInput雖有參數式Main，但MerchantDialog_Prepare在這315份XML無定義；Point_GetX/Y、IndexedName、MinMax則確有。未額外證明前者是native builtin，所以不能宣稱TasksDialog目前有安全封閉依賴鏈。YesNoDialog只有helper沒有Main。MerchantExample等存在strictCP950轉碼失敗者，不以替換字元硬湊CRC。

本輪沒有證實獨立原生任務日誌／可追蹤任務清單opcode，不能從TasksDialog名稱捏造。Server可持久化任務並用本輪自訂UI或已證聊天通道列進度，須標重建介面。

## 驗收與來源

XML格式、strictCP950、CRC、zlib／長度與原件閉包檢查已完成；Simkin實際執行、原生GUI與任務獎勵交易仍各自待驗。首次測新名稱缺檔→回覆資源→開窗→取消→重開接受→達標領獎→重播拒絕→重登進度；失敗要保留Client/Server，不能改原件救場後冒稱原生通過。

精選REA ID（均沿既有同SHA A023，並非本輪新產生）：parser ev_cb9fae76509bd4ffa248f653d781ec6c1d9251e4ae1c96392b7e43c2aba71c52；startqueue ev_c401e6ffc5154151aa851abb1f0319e927d966cebe50c892c0384f0ef225d100；Main ev_66d7a0d5a6b9c659c2141fece7535036c69277229dc1cde7b2473d8a399b1947；SendReply ev_4b996827af5f1223e5fcc48e0cad8fb5bad26232f0aaa2409431b088c6524eef；Dispose ev_9a787ea4c7979a2613ada40688897136c0294d3db4d3d6374ae72102ecec93be；CRC ev_b3e310605487e1abb7bdadcbde96afbddc5a8399e25f6ca124362e719459caf5。完整原件SHA／格式與本輪原始XML僅存workspace/anal-roy-temp/town-quests-native-20261108。
