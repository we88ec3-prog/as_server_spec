# 五職業完整教學路線：真實TCP與持久進度驗證

日期：2026-11-01。使用[明示候選內容profile](20261101-tutorial-geography-and-content-profile.md)，
接續[戰鬥TCP投影](20261101-training-combat-transport.md)。本輪以自動化socket
Client執行實際Host與SQLite交易，沒有把模擬操作等同原生GUI驗收。

## 與先前測試的差別

本輪使用三份真實且已鎖SHA的MAP庫、實際腳本CRC與helper素材，啟動獨立
Host、獨立DB及隨機loopback埠。五名角色各從Account建立開始，經原生C02／
C04建立角色，沒有使用管理端角色植入、直接寫入教學事件或直接改完成旗標。
Server設定入口同時啟用加入、學校、兩位講師、練習目標、就職及傳送。

候選profile ID為`isolated-tutorial-route-candidate-v1`，本地生成檔SHA為
`5c8ee3d2abd81edadce8b2653d439410153b8f41344554448c0c0d7b0d6592c4`。
該SHA含本機絕對素材路徑，其他機器應記自己的檔案SHA，不應硬套此值。
350項.NET測試使用的隔離Host快照沿用；這輪僅新增Python驗證工具與入口說明。

## 實際走過的序列

每種職業皆經過下列操作及檢查：

1. C02驗證帳密／名稱、C04外觀建角，收到Server發起的S03轉接，不另送登入。
2. C10／C25進初始Map6，正確C35後收到角色、招募員與Born。關閉Born。
3. 招募員先拒絕、再開啟並接受；關閉issued runner後才收學校S15／S14。
4. 依已核對內容checksum送C35，進候選Map7；核對S04出生點、四位NPC與
   一個kind2練習目標生成。checksum來自member SHA一致的公開目錄。
5. 對Life／War的各自issued Merchant context送TALK及Dispose；再用選職
   context送對應中文JOB，關閉後處理Server另發的結果runner。
6. 同Client送離開遊戲C0B、再C03登入，使用新S03 token重連，仍回到學校。
7. 尚未practice時點傳送師，收到拒絕提示；沒有提早畢業或切圖。
8. 對Server已發出的目標ref送兩次C13，間隔550ms，觀察S11／S13、死亡S5F。
   候選HP3、單擊2，實際audit為2筆、總傷害3，沒有Client指定傷害。
9. 死亡後不送其他Client操作，等待背景S0E及S07／S1A；確認新生命ref不同。
10. 再開傳送師並接受；正確目的圖C35後核對完成旗標、已選職業與位置。
    首次進場checkpoint保持逐欄相同。再次C0B／C03重登，仍進對應目的圖。

每個socket的全部加密S2C ordinal另逐一核對從0開始依序遞增；背景重生與
一般回覆使用同一順序，plaintext不計入。這驗的是本Server單連線輸出設計，
沒有新增Client輸入ordinal單調性的原服主張。

## 結果

|職業|候選目的圖|完整TCP序列|學校／出圖後重登|靜默重生|原生GUI|
|---|---|---|---|---|---|
|戰士|2001|通過|通過|通過|未驗|
|聖職者|1|通過|通過|通過|未驗|
|魔法師|4001|通過|通過|通過|未驗|
|盜賊|1001|通過|通過|通過|未驗|
|武道家|3001|通過|通過|通過|未驗|

五條路線共用同一測試Server與場景內容，目標生命編號持續增加，不為每名
角色重開Server或清空共享表。所有DB核對皆唯讀，教學事件由實際Host處理產生。
測試結束停止自有Host，沒有變更使用者既有Server、帳號或進度。

## 原生嘗試與未完成範圍

另啟動一份獨立診斷Client，實際握手到LoginReady；computer-use視窗存取
回報`Computer Use app approval timed out`，因此沒有取得畫面或操作到創角。
後來FormInput在既有600秒idle期限關閉，這不是創角提交失敗的新證據。
清理該輪自有Client及Server，不把它標成原生通過。

這輪證明五條路線的真實Server／TCP／DB接線；未證明原版學校或城鎮編號、
NPC視覺／對話實際可用、kind2普通攻擊動畫、Client數字職業投影或完整GUI。
正式Native CT與整體目標保持未完成。下一步仍要實際Client核對及必要修正，
之後再安排使用者集中測試完整流程。
