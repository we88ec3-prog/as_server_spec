# 物品保管與商店買賣的原子資產契約

日期：2026-11-08。關聯：[正式物品與裝備](20261107-owned-inventory-equipment.md)、[錢包與銀行資金](20261108-wallet-bank-authority.md)、[A-013經濟分析](A-013-economy-contract.md)。本頁補足Server可獨立實作的資產規則，不包含私有程式或使用者資料。

## 需求來源與內容歸因

本輪使用者要求完成銀行物品保存／存取與商店買賣。原生Script服務分支及GUI欄位由對應原生分析交付；本頁的32格保管庫、價格、手續費、堆疊策略與交易收據屬**Server重建設計**。不能由Merchant／Bank類別名稱推導原服完整道具目錄、價格、堆疊限制或倉庫容量。

第一版沿用既有兩件重建服裝，不變更`development-inventory-v1`、`development-item-v1`或既有人物資料：

| 商品 | 單價買入 | 單價賣出 | 堆疊上限 |
| --- | ---: | ---: | ---: |
| development.beach-outfit | 100 | 50 | 1 |
| development.formal-outfit | 200 | 100 | 1 |

商店ID為`development-clothing-shop`，價目版本`development-shop-v1`；以上全部是測試價格。買賣與保管無額外手續費，沒有聲稱是原版配方。價目最多64列，配合本輪有界原生列表預算，不宣稱已有分頁。

藥水原服item ID、效果、價格、可堆疊數及使用語意尚未確認，本版不因找到瓶子圖示而加入可飲用物品。未來擴充須版本化目錄及明示資料遷移，不能變更既有同版本定義或免費覆寫角色物品。

## 一件物品只能在一個容器

背包、裝備、保管庫共用同一權威物品實例身分。每個instance ID只有一筆canonical記錄，owner不變，location為Bag／Equipped／Vault之一；不能另複製一筆保管庫物品而把原件留在背包。

保管庫有獨立32格、`development-vault-v1`政策與revision。保管庫物品不加入一般inventory snapshot，也不能混入S0F背包或S37裝備投影；讀保管清單走獨立視圖。一般背包驗證若收到Vault項目必須拒絕，避免顯示為幽靈背包物品。

讀取不grant物品、不grant金錢；既有可信獎勵工具與收據仍是唯一額外發放來源。本輪不改外觀、髮色、衣色、面向、位置或技能。

## 整件與部分堆疊

整件存入／取出保留原instance ID、取得事件及owner，location與slot轉移、item revision增加。目的容器必須有空格；**整件不自動合併入另一個ID**，避免使用者整件保管後原ID被無聲消滅。因此即使別的堆疊有餘裕，滿格時整件轉移仍會拒絕。這是明示重建策略，未宣稱原版倉庫如此運作。

部分轉移必須0＜quantity＜來源數量。來源保留原ID並減量；目的依格位順序補入相同definition／definition revision的堆疊，剩餘量有空格才建立新split ID。新split的取得事件連到本次操作，來源與目的總量守恆。若只能補入一部分、剩餘卻無空格，整筆拒絕，先前嘗試合併也不得保存。

quantity大於來源、0、裝備中物品、滿背包或滿保管庫都不能留下資產變更。裝備必須先卸回背包才能出售或保存。所有操作還要求角色存活；不能利用死亡狀態繼續買賣或搬物。

## 商店必須用可信價目

價目綁定inventory catalog revision與每個definition revision。Server固定同shop ID／revision的內容；若同版本價格漂移就拒絕，合法調價使用新版本。不能接受Client給出的售價、價格總額、物品模板或預期餘額作為權威。

買入先驗證可交易商品、正整數數量、Server單價×數量、錢包資金與背包容量，然後同一交易扣款並建立／合併物品。賣出驗證exact instance／slot／revision及足量後，同一交易消耗該件數量並加款；整件賣完才刪除實例。保管庫物品不能跳過取出直接賣，裝備中物品不能直接賣。

金額遵守既有`development-economy-v1`：單次總價與每個餘額上限皆1,000,000,000。乘法使用有界整數及checked運算；總價超限、付款不足、售後會超錢包上限、背包不足皆業務拒絕，不回假成功也不先動一邊資產。

## 同一交易、三組版本與收據

Host先讀同一權威snapshot：Inventory、Vault、Economy及三組revision。提交必須帶這三組CAS、目前owner lease、有效載圖狀態與exact item expectation；之後的物品列、容器版本、錢包與commerce收據在同一資料庫交易提交。不能先呼叫一個Store扣錢，再開另一個交易發物品；任一寫入失敗全回滾。

收據記錄kind、quantity、來源exact identity、trusted catalog／shop revision、三組原版本、wallet前後值、結果與時間。每個受影響物品另記`InstanceId／Before／After`：可明確追查整件的保管位置轉移、部分split的新ID、堆疊合併的數量變化、買入的新物品或賣出的消耗，不把身分變更藏在總數背後。

同operation ID同內容重送只回歷史收據；不同內容碰撞為衝突。重放不再次買入、出售、存入或取出，也不把歷史snapshot寫回目前資產。Host投影前重讀目前權威狀態；NPC／對話context必須one-shot，避免把同一個原生提交重送換成不同ID。

角色lease鎖及CAS令兩筆同時意圖不能覆寫；舊連線、斷線或未完成載圖，即使帶著既有收據也不能繼續取得資產權限。NPC角色是否提供此服務、可見範圍與context是否仍有效，由Host驗證，Store不接受Client挑owner或任意資料庫角色。

## 資料相容與驗證

新增vault state、trusted shop catalog、commerce receipt三表，沿檔案型SQLite一致備份流程先備份已有資料，再additive初始化；不重建舊物品。canonical物品表既有Bag／Equipped資料原樣保留，新增Vault僅為Server內部位置類別。第二次表已齊全時不再因相同新增內容重複備份。

本輪定向驗證：Commerce domain3項、Commerce SQLite Store10項及既有Inventory Store11項全部通過。涵蓋整件ID與重登持久、partial拆合及失敗守恆、32格滿庫／滿包、價目版本固定、資金／上限／0量／裝備／死亡拒絕、owner／lease／CAS／exact instance、並行同事件與競爭、防止重播覆蓋、故意使收據寫入失敗時物品與錢包全回滾，以及舊世界備份一次且進度不重置。

這些為合成資料庫／domain測試，不代表原生GUI、完整Server回歸或PostgreSQL實測。原生銀行清單、數量輸入、買賣畫面、背包與餘額同步、關窗／取消、Server重啟及實機重登由後續集中驗收補充。

後續Host wire定向13項通過：買賣／保管列表、新context的最終I／U回覆可省TYPE、舊context不重複扣款或移物、非法選項／數量、清單後裝備變動的CAS拒絕、已裝備物品不列入售出／保管、空庫、Vault不混入S0F、重登保管身分保存。另核對ReviewedItemIcons開關下初次S0F、商店T與S37投影一致，持久item definition不受外觀投影改寫；64列Script參數及60000數量的u16背包投影亦通過。既有BankWire回歸10項通過，沒有BankItemDependencies的fixture仍維持物品保管Unavailable，不因新增Host能力自動開放。

上述Script依賴CRC與擺位為合成fixture，只證明Server對原生封包形狀及資產權限的處理；不宣稱原始Script完整GUI已實機通過，也不以占位資產做原版道具目錄背書。
