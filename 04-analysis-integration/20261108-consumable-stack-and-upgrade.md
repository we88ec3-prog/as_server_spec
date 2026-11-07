# 重建藥水、堆疊轉移與舊物品資料安全升級

日期：2026-11-08。關聯：[物品／商店權威](20261108-vault-shop-authority.md)、[錢包銀行](20261108-wallet-bank-authority.md)、[角色成長](20261107-character-growth-authority.md)。本輪延續使用者要求繼續開發功能，完成藥水商店、堆疊、使用恢復與保存的Server能力。

## 原件與重建規則分開

藥水圖示引用已供原生介面投影核對；**圖示不證明原服item ID、效果、價格或堆疊數**。本頁兩種藥水及全部數值為明示重建：

| 內部定義ID | 圖示 | 效果 | 最大堆疊 | 買／賣單價 |
| --- | --- | --- | ---: | ---: |
| development.hp-potion | 0x8244 | 恢復HP40 | 20 | 30／15 |
| development.mp-potion | 0x824A | 恢復MP40 | 20 | 30／15 |

兩藥共用1000ms冷卻，沒有第三種SP藥。恢復不超過角色既有上限，不影響BP、SP、經驗、能力、外觀或其他物品；不提供復活。購買與出售沿既有同交易背包／錢包契約，原有衣服100／200買、50／100賣不變。

## 目錄與效果政策獨立

既有`InventoryCatalog.Development()`仍是兩件服裝的`development-inventory-v1`，原definition ID、revision及JSON內容不變。新增`development-inventory-v2-consumables`為精確superset：原兩件服裝原樣保留，再新增兩個`development-consumable-item-v1`定義。

效果放獨立`ConsumableCatalog`（`development-consumables-v1`），不把HP／MP效果欄位加進既有ItemDefinition以免舊pinned JSON漂移。目錄須對上definition ID／revision；同政策版本改效果或冷卻一律拒絕，合法修改使用新版本。

本輪消耗政策只接受通用、RequiredLevel1、無sex／career限制、非equipment的定義。未實作其他使用資格前，不開放帶額外需求的custom消耗品，避免略過需求驗證。

服裝商店採對應v2價目版本，仍只列衣服；藥水另用`development-potion-shop`／`development-potion-shop-v1`，只列兩種藥。不能把藥水商人掛上衣服價目再宣稱是原版內容。

## 使用一次的原子權威契約

Host僅將已投影且可信消耗目錄對應的原生背包使用意圖送入Store；原生kind／flag／mode等入口另由Protocol／Host核對，不接受Client自訂恢復量。

Store在同一交易驗證目前account／character owner lease、已提交載圖、來源Bag exact ID／slot／item revision、inventory revision與status revision，讀取共享冷卻，再判斷效果。裝備／保管庫或不存在物品不能作為背包消耗來源。

- HP為0：Dead，不消耗、不恢復、不復活。
- 該物品不在可信消耗政策：NotConsumable，不當作藥水。
- 對應資源已滿、恢復不會改變狀態：NoChange，不耗物，也不啟動冷卻。
- 需要恢復但共享冷卻尚未到期：CoolingDown，物品與資源不變。
- 可使用：同交易消耗恰好1、恢復clamp、更新資源版本、inventory版本、共享ReadyAt及使用收據。用完最後1件才刪除該實例。

任一狀態／收據寫入失敗，資源、物品、版本及冷卻全部回滾。收據保留物品Before／After，最後一件消耗的After為空；同operation ID重送不再次耗用或恢復，舊收據不覆寫後續受傷／耗魔。Host投影需重讀目前權威狀態。

## 堆疊轉移不是排序

新增明確quantity的TransferStack操作，與不合併的C30排序分開。要求來源與目的exact expectation、inventory CAS及owner lease：

- 空格、部分量：來源ID保留並減量，建立split ID，取得事件連到本次操作。
- 空格、整件量：移動原ID，不能重新產生整件身分。
- 有相同definition ID及definition revision且有足夠容量的堆疊：轉移指定數量，總量守恆；來源整件合併時原ID退役，保留目的ID，於AssetChanges明記Before／After，不能無聲丟失ID。
- 不同定義／版本、不夠容量、0或超來源數量：完整拒絕，不先合併一部分。
- 來源等於目的：NoChange。

堆疊轉移使用既有inventory收據表但有`stack-transfer:`鍵空間與專用DTO，避免和穿戴／排序收據混讀。不能用Client聲稱的新數量直接覆寫一格。

## 精確舊版升級與Starter防重

只允許完整內容等於可信內建v1、容量32的舊inventory升至完整內容等於內建v2；不能只看revision文字，不能把custom同名v1、任意custom目錄或其他容量默默替換，也不允許降回v1。

升級只改active catalog pointer，保留owned instance ID、slot、數量、取得事件、裝備／Vault位置、容器版本、錢包、角色進度及獨立衣色。新增藥品定義不會自動送藥或補錢。

檔案型SQLite在write transaction之前先作一致備份，實際交易內再重驗owner lease、舊目錄fingerprint與pointer條件。新增消耗目錄、共享冷卻及使用收據三表；既有v6缺此組時備份標記`pre-consumables-v1`。實際v1→v2目錄升級另有`pre-inventory-v2`備份；其他既有World additive升級仍保留原備份路徑。已升級v2再次讀取不重複升級；備份不在持有同DB寫鎖時執行。

開發Starter最容易造成資產重發：若把event換成`dev-starter:development-inventory-v2-consumables`，舊角色會多拿兩件衣服。因此v2專用可信Starter helper沿用**原event `dev-starter:development-inventory-v1`與原樣v1 command內容**，在active v2執行穩定的兩件舊服裝發放集。已有舊收據只重播，不把舊v1 snapshot寫回active v2；新角色也只拿一次兩件服裝，不附送藥水。Host發包前重新讀active狀態。

## 定向驗證與未完成界線

本輪Domain3項、SQLite消耗／堆疊／升級12項全部通過：40點恢復與clamp、共用冷卻、滿資源不耗、死亡不復活、exact source／雙CAS／owner／lease、並行同事件與舊收據不回補、故意令收據失敗時完整回滾、政策固定、舊Starter兼容、裝備／Vault身分與衣色／進度保持、拒絕custom同名舊目錄／任意替換／降版、schema備份tag與重複初始化、整件／部分split／merge及退役ID審計。

既有Inventory Store11項、Commerce Store10項、Economy Store7項回歸通過。這是Server／合成資料庫驗證，沒有修改使用者資料庫或啟動其Server，也不代表原生快捷鍵／動畫／藥水商店畫面已驗收。原生UI、封包數量更新、真正TCP、重登及Server重啟驗收由Host與整合工具結果補充。
