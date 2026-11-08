# 十六槽裝備、互斥替換與多件加成

後續武器／盾牌／頭部接線與不相容衣裝政策見[裝備Human外觀](20261108-equipped-human-visuals.md)；本頁保留前一增量的證據與結果。

使用者要求開發裝備、角色能力、商店及完整Server。本輪擴充原本只有衣裝slot2的限制。**槽位key與UI對應是原件靜態證據；商品名稱、需求、價格、配件選槽、雙手互斥及數值公式是Server重建設計**。原始EXE與素材未修改。物品圖示只是同版素材的視覺候選，不是找到原服物品模板；持握武器、盾牌及頭盔的角色模型尚未接線。

## 原件證據

Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，REA／Ghidra12.1.4。Inventory constructor `0x48b630` 向dialog4註冊UI後，逐一取得control3..18，再把control ID減2交給 `0x45cc40`。後者把key寫入實際control物件+0x258；事件handler `0x45c2a0` 的ECX是+8介面視圖，故讀取的+0x250是同一byte。該key供C3A及C1F使用，並非用skin文字猜wire槽位。

同版[skin.tbl](20261108-native-equipment-stats.md)完整有界解析提供control名。對應如下：

|裝備key|control ID／名稱|本輪用途|
|---:|---|---|
|1|3 Weapon|武器|
|2|4 Armor|衣裝，仍限定已核外觀0..2|
|3|5 Shield|盾牌|
|4|6 Head|頭部|
|5、6|7 Ear1、8 Ear2|雙耳環|
|7|9 Neck|項鏈|
|8..11|10..13 Ring1..4|四戒指|
|12|14 Belt|腰帶|
|13|15 Leg|腿部|
|14|16 Foot|足部|
|15、16|17 Hand1、18 Hand2|雙手套|

S37／S38沿[既有裝備子集](20261107-native-inventory-equipment-subset.md)，不新增未知旗標。`0x45d140`／`0x45d160`分別回傳兩個容器指標，玩家raw-false容器仍沿前者。`0x45ee50`以byte key查找／建立裝備資料，並非只支援slot2；`0x45ef70`按key範圍移除。slot12另有`0x55dc70`回呼，完整附帶用途未還原，不能宣稱已重建所有腰帶Client效果。原生滑鼠操作及實際畫面仍待驗收。

Evidence：`ev_7d44615587ce8df8cfc0708e1406e8eb3933da98f7b6e85e274a3d27dc7f43eb`（constructor／事件／兩容器）；`ev_3d0d92ceed482838078eb93686fb4c2f6d57ed857c2c82591ed40f653e0cca56`（key setter／裝備新增移除）；`ev_b5ab2d388e016fdee7b627ce60599fead05bd6340b176470970d9a3ac339dc2f`（slot12回呼及查找）。最後一批S37入口`0x4f3be0`沒有可反編譯procedure，該項失敗；沿用先前精確指令證據，未修原件函式邊界或冒稱成功反編譯。

## 穿戴與替換規則

物品定義仍分開Server ID／revision與Client icon。裝備slot1..16、最大堆疊必須1；ClothingId只容許slot2且保留0..2。slot2必須有ClothingId，其他槽不能藉此改衣服。舊欄位／定義內容不改，新可選InterchangeableSlots及TwoHanded為null時不寫JSON。

InterchangeableSlots=true只准primary slot5、8、15，分別對應5/6、8/9/10/11、15/16。啟用時由低至高找空槽；全滿才替換primary槽。沒有此欄位則只使用定義指定單槽。此為Server配置政策，不冒稱原生C1C有攜帶指定飾品目的槽。

TwoHanded=true只准武器slot1，與盾slot3互斥。穿雙手武器時同時取下舊武器和盾；穿盾時取下原雙手武器。第一件被替換裝備回到incoming釋出的背包格，第二件使用最低空格。背包沒有足夠格位則整筆BagFull，原裝備、incoming、數量、版本與能力保持；不能先卸一半或丟到地面。一般滿包單件替換仍可利用incoming格成功。

沿既有C1C `[1,bagSlot,0,5]`／C1F `[equipmentSlot,0,0,0]`玩家子集。來源為已投影物品instance／item revision及inventory CAS，並檢查當前owner／World租約／load、死亡、性別、職業與等級。新內容預設Lv1、無職業／性別限制；框架並不代表原版各職業都可裝所有武器。C3A仍保持不變更的安全處理，不宣稱完整原服物品詳情已完成。

穿戴／多件退回／inventory revision／操作收據同交易。資料層以角色、位置、槽位唯一鍵保存，同一instance不重建；故障全回滾。讀取戰鬥加成時再核裝備定義ID／revision、允許槽／數量，拒絕重複槽或雙手／盾非法共存。銀行、背包、地面與交易保管的物品不加成。

## 目錄、來源與保存

目錄 `development-inventory-v4-multi-slot` 共17項，保留v3六項定義及其JSON／revision，新增下列11種。新增商品revision為development-gear-item-v1。每項Quantity1，耳環／戒指／手套可買多個獨立instance填各槽。原本衣服及兩瓶藥水的內容、價格與starter規則不改。

|新重建物品|slot／附加政策|加成|icon候選|買／賣Gold|
|---|---|---|---|---:|
|training-sword 訓練劍|1|AttackPower+3|8002|300／150|
|training-staff 雙手法杖|1、TwoHanded|INT+3、AttackPower+4|8031|300／150|
|training-shield 訓練盾|3|DamageReduction+2|8063|100／50|
|training-helmet 訓練頭盔|4|CON+1、DamageReduction+1|8181|100／50|
|training-earring 訓練耳環|5、InterchangeableSlots|WIS+1|8210|100／50|
|training-necklace 訓練項鏈|7|WIS+1|81D9|100／50|
|training-ring 訓練戒指|8、InterchangeableSlots|STR+1|81B8|100／50|
|training-belt 訓練腰帶|12|CON+1|81EF|100／50|
|training-leggings 訓練護腿|13|DamageReduction+1|809A|100／50|
|training-boots 訓練靴|14|DEX+1|81C3|100／50|
|training-glove 訓練手套|15、InterchangeableSlots|DEX+1|81AD|100／50|

各ID加前綴development.。圖示為hash鎖定Icon.dat中的item.tw.ypf object index加0x8000；這輪有界檢視0..95及0起每11個的96選樣，涵蓋所用候選，分類只由畫面辨識，非原服ID或裝備規則。新地面投影暫共用既有已核80D7候選，沒有把bag icon跨用到物件數不同的ditem。實際持握／武器動作、帽子與盾牌模型尚未解析接線。

商店 `development-shop-v4-multi-slot` 共15商品（舊四衣裝＋新十一項），藥水商店使用同v4 inventory的獨立revision。新物品可沿既有原子買賣、銀行存取與持久化；裝備中仍不能直接存入。完整匹配內建v1／v2／v3才可升v4；自訂內容不暗改、降版拒絕。升級前SQLite一致性備份一次，標記pre-inventory-v4，順序重跑不再次備份；未強制同步升級競態。再交易內切inventory pointer；保留instance、位置、item／inventory版本及舊starter收據，不重發泳裝／禮服或重產管理金鑰。未進行使用者現有DB遷移；完整還原及PG實例另驗。

## 能力、戰鬥與畫面

單件仍限制五能力各0..40、攻擊／減傷各0..1000；彙總改用獨立寬型別，最多16件，五能力加成可到640、攻擊／減傷到16000。不能為了彙總放寬單件模板限制。base＋裝備＋buff後五能力才255封頂；彙總不寫回永久值或資源上限。普攻／技能使用同一交易內的彙總；怪物來傷使用總減傷，最低1。角色衰弱仍在攻擊公式後套用，持續傷害仍按施放快照。

[已證S08欄位](20261108-native-equipment-stats.md)的DAM body20..21、AC body54現在有值。重建顯示政策：DAM為總AttackPower；AC為總DamageReduction的0..127顯示飽和值，實際減傷仍使用完整總值。HIT／MC／AAR／SAR／負重仍0，不發明未完成的命中／魔防／負重公式。AC高低原服意義及符號政策仍未知，不能拿本輪顯示公式當原版戰鬥證據。

Protocol支援完整已證欄位的signed顯示型別：DAM／HIT int16，SAR／AAR／AC／MC int8，負重兩欄uint16。輸入由可信Server計算，不由Client傳。60-byte full block、current資源起點62、錢包90及尾端欄位長度不變；RESIST仍不可插入wire。

非衣裝裝備變更不重發自身S33，避免無關穿卸重建角色模型；衣裝ClothingId真正改變才更新自身外觀。背包主動排序的既有明示resync仍可發S33，與被動裝備投影分開。S37／S38與S08由交易後狀態投影，重登依持久位置重建所有槽，不把舊收據重新套到當前畫面。

## 驗證與集中待測

新增17項：Domain9、Store6、Host1、Protocol1。涵蓋填滿16槽／卸下守恆、第五枚戒指替換、雙手滿包拒絕與反向裝盾、界線、16件最大加成、舊JSON、三版升級備份讀取／不重發starter／拒降版、首次技能與普攻讀多件加成、兩處多物品交易回滾、全16槽原格式穿卸及重登、S08獨立offset向量。完整.NET回歸1089項通過、0失敗／0跳過，原人工回報不改為新槽GUI已驗收。

真TCP單一合成Client四組通過：在原生Merchant買劍／盾／戒／法杖共800；C1C／S37／S08彙總及雙手退回同instance的武器與盾；C1F卸裝、原生銀行存入／取出法杖保留instance；賣法杖150後餘額350，同Client重登及自有Server重啟保存資產／裝備／位置。全16槽廣度由Host原格式測試覆蓋，未宣稱TCP買齊16件或操作原生GUI。

Host SHA256 `db63fbb379731148604129f698af7742728703db3bc4a5e3f6ef02052b5c965f`，八組件bundle `557e7db8f98f9a388e9d66a0c985421503485b3cf470fe9cd2e1d197621cf5b6`，測試前後一致。

原生集中待測：米魯里斯鐵匠選新物品→填雙耳環／四戒指／雙手套→比較能力與DAM／AC→雙手法杖替換劍盾→包滿拒絕→卸裝與銀行→重登。既有角色／密碼／金鑰可沿用，不需重創。原版裝備需求、耐久／修理、套裝、HP／MP上限加成、武器持握模型／攻擊動作及原生腰帶附帶效果仍未完成。
