# 原生商店買賣與銀行物品清單契約

2026-11-08。來源為本版不可變 Client EXE 與 Script 原件的靜態解析；不是原服商品表，也不是原生 GUI 通過紀錄。使用者要求可買賣、銀行保存及領回物品；價格、容量、商品身份與交易原子性由 Server 重建設計，應與本文件的 Client 事實分開。

## 入口與封閉依賴

S44 Main 為 `Merchant`。一般商店使用 `nSuAllMarket01` 加 `MerchantDialog`、`ItemsDialog`、`MerchantBuyDialog`、`MerchantSellDialog`；此 adapter 只開 Buy/Sell，Repair/Bank/Identify/Talk 均關閉。GREETING 可覆蓋原商人的自我介紹，不能由此聲稱原服商人售出本次重建商品。

銀行沿用 [貨幣契約](20261108-native-bank-currency-ui-contract.md) 的六項依賴，再加 `MerchantBankDIDialog`、`MerchantBankWIDialog`，共八項。需要把個別腳本加入清單，不能僅提供 MerchantBankDialog。原生 helper `GetStringFromMetaData` 與 `GetDescFromInventory` 是 EXE 全域函式，不是額外 Script 檔。

初次入口不傳 TYPE，可讓原生 MerchantDialog 顯示選單。Server 收到選單回覆後另開可信情境：商店 `TYPE=BUY` 或 `SELL`；銀行 `TYPE=BANK` 並設定 `STATE=DEPOSIT` 或 `WITHDRAW`。銀行的這兩個 STATE 是物品，貨幣另用 DEPOSITGOLD/WITHDRAWGOLD。

## 參數與列數

共用基礎參數：`TILE,MNAME,GREETING,UGOLD,UBAL,UAGOLD,UABAL,UCOLOR`。清單再加 `EMPTYSLOT,EMPTYWEIGHT,ITEMCOUNT`，銀行物品再加 `EMPTYDEPOSITSLOT`。這些顯示值不能取代 Server 的角色、背包、重量、容量或金額檢查。

`ITEMCOUNT=N` 時列索引是 **0 到 N-1**，不是含 N。後綴是十進位、不補零，例如 `T0,N0,U0`。Merchant 腳本外層 `itemCount>0` 保護零列；原生 Simkin for interpreter `0x598310` 正向迴圈以上界不包含的比較執行，不能從一般語言的 to 習慣判斷。

|前綴|Client 欄位／用途|限制|
|---|---|---|
|T|Tile 圖示|原生圖示 selector，不是原服 item key|
|N|NAME 與列表名稱|Server 提供顯示文字|
|L|LEVEL|顯示文字|
|P|PRICE|BUY 逐單位計價；SELL 僅顯示|
|G|GENDER|顯示文字|
|C|CLASS|顯示文字|
|W|WEIGHT|字串轉整數|
|K|HelpString metadata key|空字串仍執行查詢，不是 metadata bypass|
|R/O/E|COLOR/LAYER/EFFECT|保留原生欄位，不能推造效果|
|U|BUNDLE|可選數量上限／持有堆疊數量|
|V|SELL 的 VALUE|實際出售單價，總價為 V × 數量|
|S|DEPOSIT 的背包 slot|GetDescFromInventory 依目前原生背包內容取描述|
|A|DEPOSIT 的 AVAIL|0 可選，1/2 不可選；WITHDRAW 讀取但未存為該 cell 的 AVAIL|
|F|銀行物品 FEE|每次操作固定費，腳本沒有乘數量|
|I|WITHDRAW 的 ATTRIB|有存入 cell，但本輪 ItemsDialog 路徑沒有讀取；可空值，不宣稱已解析其格式|

BUY 的總額為 P × 請求數量；不能因原件註解提到 bundle 就強迫整疊購買。SELL 使用 V 而不是 P。所有金額與容量須以 Server 定義及整數運算再次核對。

## 回覆、數量與關閉

四種物品清單的最終成功請求只加入 `I=列索引`、`U=數量`。初次選單可帶 TYPE/STATE，但新 runner 的最終 I/U 回覆不能假定重帶它們；必須由 Server 已保存的 dialog context 綁定模式、商品／背包物品、版本與一次性操作。不得信任列索引跨清單重放。

BUY/SELL 在 bundle>1 時可進可編輯數量輸入。**本版銀行 DI/WI 的 DoubleClick 卻固定傳 bBundle=false**，NumberDialog 建立空白 StaticText，OK 將單一空格轉為 1。因此原件銀行 GUI 每次點選是單件存取；Server 支援部分堆疊不代表 GUI 已有任意數量輸入。此限制不能透過改寫商品 bundle 欄位假裝解決。

ItemsDialog Cancel 清空 values 後送 `STATE=ABORT`；數量子窗 Cancel 只關子窗，父清單仍在。runner Dispose/C6C 清理沿用貨幣契約。取消不能修改庫存／錢包。重播、過期、拒絕與成功後都須以新權威 snapshot 刷新，避免用歷史 receipt 的舊餘額覆寫當前狀態。

原腳本有樂觀更新：例如 DI 空位計數可能在整疊存入時重複增加，WI 有 UserEmtpySlot 拼字差異。這些是 Client 暫存顯示行為，不能抄為 Server 容量規則。Server 必須把物品移轉、拆合堆疊、費用／買賣金額、容量與操作 receipt 放在同一交易。

## metadata 與圖示

`0x525130` 原生全域函式 dispatcher 的 `0x526c58..0x526d43` 分支把表名、key、index 交給 `0x4ceea0`；其查詢路徑會經 `0x4ced90`，未初始化時可進 `0x4cebc0` lazy load。K 空值仍走此路，不能承諾未修正 metadata 問題的原 Client 一定安全。`GetDescFromInventory` 分支 `0x52710f` 經 `0x489a30(kind=1,slot)` 與 `0x489740` 讀背包項目描述。

Script item cell category0 `0x45cbf8..0x45cc1d` 經 `0x491ba0→0x491330`，使用圖庫2、member3、object=`icon-0x8000`、frame0；category1 的 `0x491d40` 路徑亦用 member3。另有 legacy `0x490f20` 使用 member1，不能混淆。Icon.dat 的 member1 為 item.tw.ypf、member3 為 pitem.tw.ypf；兩者的 object580/586 frame0 都有紅／藍瓶外觀，故可供重建商品採用的圖示候選為 **0x8244／0x824a**。這不證明原服藥水名稱、效果、item ID、堆疊上限或價格。

資產 SHA、預覽界線與既有兩件衣服圖示實為棍／劍外觀，見 [圖示來源審核](20261108-shop-item-visual-sources.md)。目前商品子集不能稱為完整原服商店；任意新增藥水消耗效果仍須另外實作、測試及記錄重建政策。

## 驗收界線

本文件交付可實作 ABI 與來源身份；尚未代表此輪原生畫面測試完成。應集中驗證空清單、購買／出售／金額不足、滿背包、單件與堆疊銀行存取、取消、重登持久、重播與過期情境。未測項目保留待測，不用 synthetic TCP 測試替代原生 GUI 結果。

精選機讀來源與欄位見同名 JSON。原始反編譯與全文腳本只留本地分析區，公開庫不附原 EXE/DAT 或完整腳本。
