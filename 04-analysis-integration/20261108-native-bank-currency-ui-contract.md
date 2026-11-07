# 原生銀行存提款UI與權威餘額契約

2026-11-08。本輪先完成銀行存提款的原生UI可開發契約；商店列為後續。使用原始Script既有函式，不新增或修改Client腳本，不從商店類別名推測交易流程。來源SHA、strict CP950 CRC、封包格式、必要參數與狀態表見 [JSON](20261108-native-bank-currency-ui-contract.json)。本文件補充A-012／A-013，沒有宣稱原服價格、帳戶上限或GUI已驗收。

## 開啟銀行的最小依賴

Main為 `Merchant`，textCRC `e9b389cf`；與原唯讀NPC介紹不同，使用 `nSuBanker01` 代替 `nSuInn01`，使DoesBank=true。不要傳Quest旗標。

|依賴Script|CP950 textCRC|用途|
|---|---|---|
|nSuBanker01|3a506b26|銀行掌櫃席茲、BuildMuttering、Does*及LoadDG/WGMessage|
|MerchantDialog|9267d99d|第一層NPC選單與BANK按鈕|
|MerchantBankDialog|1e576517|本地四項銀行選單及Server STATE分派|
|MerchantBankDGDialog|812ccab0|存款金額框／驗證／回覆|
|MerchantBankWGDialog|35bb8dae|提款金額框／驗證／回覆|
|ItemsDialog|ffc38cd1|父視窗、口袋餘額與Cancel|

**必須使用ItemsDialog，不能誤用Dialog。** Dialog裡同名ItemDialog_Create是舊版十參數、不完整的函式；銀行實際呼叫的是ItemsDialog提供的兩參數版本。MerchantWGDialog也有同名提款函式，這次不混載它。SHA與原件檔案身份均在JSON，CRC不是壓縮檔CRC。

首次S44(1,0)的八個參數為 `TILE,MNAME,GREETING,UGOLD,UBAL,UAGOLD,UABAL,UCOLOR`，不傳TYPE。TILE須為實際驗證過的Portrait素材。UGOLD是口袋餘額，UBAL是銀行餘額；UAGOLD／UABAL分別是口袋／銀行還能增加的餘裕。四金額均來自權威快照，以十進位字串傳送；已啟用交易的UI不能再用未使用的零值佔位冒充帳戶。

## 實際UI與C6C流程

1. 點Merchant的BANK：ClientReply加入 `TYPE=BANK`，呼叫SendReply，接著本地開MerchantBank。此時不是等待另一個Server包才出現選單。
2. 四項選單為DEPOSIT／WITHDRAW（物品）、DEPOSITGOLD／WITHDRAWGOLD（金錢）。選金錢後加入相應STATE、SendReply，選單停用等待Server。
3. Server以新context發S44，仍執行Merchant；八個真實參數外加 `TYPE=BANK,STATE=DEPOSITGOLD` 或 `WITHDRAWGOLD`。需保留nSuBanker01，因Main仍會呼叫BuildMuttering，金額函式亦需LoadDG／WGMessage。
4. Client開ItemsDialog父視窗及金額子框。存款預設min(UGOLD,UABAL)，提款預設min(UBAL,UAGOLD)；Client端另檢查正數、餘額與上限。
5. 確認金額後，Client先樂觀變更本地UserGold／UserBalance，再送 `STATE=DEPOSITGOLD或WITHDRAWGOLD,U=金額`。金額子框關閉，父視窗仍存在。
6. 子框Cancel只關閉子框，不送交易。父視窗Cancel先ResetValues，只送 `STATE=ABORT`，再Dispose與client.Dispose。

Merchant.Main每輪建立空ClientReply，**不會把ServerParam.TYPE自動複製進回覆**。因此同runner從BANK進選單時可能保有TYPE，但Server新開金額runner的最終回覆通常只有STATE／U；ABORT亦可能沒有TYPE。路由須依Server保存的銀行context，不可硬要求每包都帶TYPE，也不可讓Client自由選擇任何TYPE獲得權限。

C6C(1)是名稱、context、BEu16 pair count與string8 key/value；client.Dispose對應C6C(4)，未曾SendReply的cleanup另可能C6C(2)。dispose只是生命週期，不是存提款意圖，不可重複轉帳。原生wire沒有交易nonce。

## Server交易與畫面修正

銀行操作須在同一交易檢查目前owner／lease／地圖／NPC互動上下文、預期revision、正數金額、來源資金與目標上限，再一起扣加口袋與銀行。金錢總額守恆。拒絕不得扣款；相同context重放不再轉帳。關閉舊context與晚到Dispose不能清除較新的對話。

Client會樂觀改金額，所以成功與拒絕都應取得**最新權威快照**再更新S08錢包與新S44視窗；不能拿舊receipt內快照覆蓋較新狀態。Server設定的初始0、上限1,000,000,000、免手續費等若使用，皆標示 `development-economy-v1` 重建政策，不是假稱原服數值。

口袋金錢位於S08 flag0x10尾BEu32；修正色彩u24後，全量0x78的body offset是90，單獨0x10則是14。詳見 [S08與HUD更正](20261108-native-status-u24-and-hud-correction.md)。銀行餘額由S44 UBAL投影，不臆造另一個S08銀行欄位。

## 物品倉庫與商店的界線

MerchantBank的物品DEPOSIT／WITHDRAW按鈕目前仍會送出STATE；本次存提款不代表物品倉庫完成。Server需清楚回覆尚未開放、保持不變且不中斷連線，不可開空清單冒充玩家倉庫，也不可進入未載入依賴的物品函式。

藥水商店原件已有Merchant TYPE=BUY、ItemsDialog、MerchantBuyDialog入口。商品參數使用不補零的十進位index，前綴 `T,N,L,P,G,C,W,K,R,O,E,U`，另有ITEMCOUNT／EMPTYSLOT／EMPTYWEIGHT；確認回覆為 `I=列表index,U=數量`。但GetStringFromMetaData的完整依賴、for-loop端點及原版商品／價格仍待接線確認，本輪不將其標記可玩完成，也不把Script C6C買賣與另一條C39／S2F通道混用。

本輪銀行原始XML只留本地分析暫存區，公開Git僅精選metadata及獨立實作契約。後續集中驗收應涵蓋存款、提款、零額／超額拒絕、取消、重放、同Client重登、餘額保存與畫面修正，實機結果與Server合成測試分開記錄。
