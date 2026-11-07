# 商店物品圖示來源審核

2026-11-08。使用者要求開發買賣與物品倉庫，本輪先核對可使用的原始視覺素材；沒有由圖案推導原服物品ID、數值或價格。核心商店先沿用既有兩件Development衣服，藥瓶僅列後續候選。

## 有界原件觀察

原始 `Icon.dat` SHA256為 `b80cfdd28b4331bf4012210756bf46196c37d43de1240d70df3cb6480e920dee`。DAT零起算member1為 `item.tw.ypf`，member3為 `pitem.tw.ypf`：

|member|archive位移／長度|member SHA256|
|---|---|---|
|item.tw.ypf|612762／1746893|55ea3a483931ea3ec5e91410f43f1aa07e90a1efb2780414722b0f361822badb|
|pitem.tw.ypf|2751726／3602459|fc7768fdb082077fab8cb36a9686f53e40c68c4215c74c53dde5cab21a109064|

兩者均為YPF17、direct RGB565 primary channel、1046個物件，不能誤讀成1046個同物件動畫frame。本輪先預覽item物件0..95，再作96個每11物件抽樣，最後針對540..635及pitem相同範圍各作96個frame0預覽。解碼保留透明mask及原RGB565顏色，沒有修改來源素材；替代channel未作原生呈現驗收。

- 物件580／physical frame0在兩member中皆是可辨紅色玻璃瓶外觀。
- 物件586／physical frame0在兩member中皆是可辨藍色玻璃瓶外觀。
- 它們可以作為**重建HP／MP消耗品的視覺候選**，顏色不證明原服效果或名稱。原服物品key、堆疊上限、使用kind、回復量、冷卻與買賣價均未知，未因此加入可消耗物品或新目錄遷移。
- 同輪原生映射調查指出icon16bit減0x8000後是YPF物件，而非實體frame；存在item與pitem兩條member路徑。物件580／586對應的候選icon為0x8244／0x824a；兩路同樣有瓶形只消除本次候選的member歧義，仍非原服物品ID證據。完整native呼叫鏈由同輪Script／圖示分析另述。

## 既有兩件衣服的界線

既有 `development.beach-outfit`、`development.formal-outfit` 的衣服外觀1／2是已審呈現子集；模板名稱及身份是Server重建定義。初版圖示0x8001／0x8002在本輪item原件預覽中分別呈木棍、短劍，不能描述為已找回衣服圖示。

同輪後續決定修正呈現，採**獨立presentation override**，不替換已保存物品定義／instance／catalog內容或revision：海灘服的代表圖示選0x8079（object121，紅色衣裝），禮服選0x80f2（object242，白色袍服）。兩個物件在item.tw／pitem.tw均有可辨衣服外觀，frame0已離線預覽；前者是小型全身圖，後者是較大上身圖。這是有原件來源的代表圖示選擇，不宣稱它們原本就綁定clothing1／2。

固定來源／bounds／flags及設計映射見[圖示來源ledger](shop-clothing-presentation-sources-20261108.json)。背包、裝備及商店／倉庫列表應採同一個呈現解析規則；權威交易與保存資料仍使用未修改的物品定義身份。若後續改的是持有物品定義本身，仍須按不可變目錄契約作明示遷移，不能登入覆寫歷史內容。

## metadata排查界線

Basic.dat的38個實際member沒有名為HelpString／MetaData／ItemInfo／ItemTable的表；根目錄可解析DAT索引的member名稱也未命中這些名稱。BasicString及SkinString的UTF16文字有通用HP／MP／體力UI詞，沒有在此有界詞查中發現藥水定義。這**不代表Client完全沒有物品metadata**，更不能排除Server下發的動態metadata或其他命名／位置。

BasicString.txt SHA為 `fa92f7a3cf544ff9e141d98620943b362e2d3dcc6e327878a818ebaa6ac3123b`，SkinString.txt SHA為 `7ba039919300dccf595fc5f5f4e6d79156b8b96c23a56fa3118d1e55847f199c`。GetStringFromMetaData的實際來源／fallback仍以同輪原生分析為準，未由名字臆造本地原服商品表。

這些是靜態解析及素材預覽；原Client商店／倉庫畫面的圖示、清單、數量輸入與交易結果仍須另列原生GUI驗收。
