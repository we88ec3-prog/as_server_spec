# 完整教學集中實機測試

日期：2026-11-01。使用者要求完整「接受教學→下一張圖→教學→選職→目的城鎮」
接好後才安排測試。本輪所有Server路線、普通攻擊與職業投影已接入，353項
.NET及五職業真實TCP通過。此清單驗證尚缺的實際Client行為，不是宣告已通過。

背景證據：[五職業TCP](../04-analysis-integration/20261101-tutorial-route-tcp-evidence.md)、
[職業投影](../04-analysis-integration/20261101-native-career-appearance-projection.md)、
[候選地理來源](../04-analysis-integration/20261101-tutorial-geography-and-content-profile.md)。

## 固定測試環境

Server開發端提供獨立的完整路線入口，與舊招募員環境分開保存：
`data/local-tutorial-route`。第一次才設定帳號密碼並建立帳號／金鑰；之後保留
角色、位置與教學進度，不為重登重產金鑰。啟動前確認該測試Server尚未執行；
既有進度與金鑰不覆寫。內容profile固定保存，重跑入口不重新生成／替換。

準備模式已產生明示候選profile及本地測試說明，重複準備逐byte／mtime不改
profile，沒有提前建立DB、帳號或金鑰。正式啟動會建置隔離Host，Server就緒
與帳號準備好才開啟診斷Client；同時保存自開Client PID供追查。

原始EXE／素材及舊data/local-tutorial不修改。使用診斷副本的結果須標記
diagnostic-copy，不自動升級原始未修改Client CT。候選學校／城鎮仍未確認
是原服配置，不要求測試者憑記憶認證地名。

## 一次走完的步驟

|階段|操作|觀察重點|
|---|---|---|
|創角|使用worlddemo、首次設定的密碼，自選名稱／外觀送出|自動進圖，歡迎紙張及成功提示可關閉|
|加入|31,29附近招募員交談，接受|runner結束後自動載入下一張圖，不能停留在無進展的重複對話|
|學校|出生點30,34附近觀察四位講師與訓練目標|場景可見／可走、NPC可見可點、有頭像與正常動畫|
|生活／戰鬥|Life guide(29,35)及Combat guide(31,33)，分別交談並關閉|原始教學頁面能開關，不應空白或卡死|
|選職|Career guide(29,33)，選任一職業並確認|結果對話正確；職業更新不移位、不轉向|
|練習|普通攻擊訓練目標(31,34)兩次，間隔約一秒|能命中／倒下，停著約五秒能看見重生；不需重登|
|出發|Departure guide(31,35)交談並接受|未完成練習時拒絕；條件齊後載入已選職業的候選目的圖|
|重登／退出|目的圖走動，離開遊戲再登入，最後關視窗|目的圖、位置及職業保留；Client能正常關閉|

測試期間不重開Server。要重新打開Client時，用同一環境的launch-client.cmd
或launch-login.cmd。若卡住，保留Client與Server，記錄最後完成階段及畫面文字，
讓本地分析能對上封包／程序狀態；不用另建帳號或清資料重試。

完成後先關遊戲，再於Server視窗按Enter停止該測試Server。

## 目前狀態與成功門檻

使用者已回報入學後到Map7、座標30,34時畫面偏到右下且大部分黑色。
本地校驗與持久位置正常；[S04偏移修正](../04-analysis-integration/20261101-tutorial-camera-offset-correction.md)
已備份更新generated v1→v2，需重啟同一測試環境並以原角色從學校接續。
這項GUI失敗保持待復驗，不把前段傳輸成功當作整段人工通過。

清單其餘項目尚待完整人工結果。先前computer-use視窗存取核准逾時，
只證Client握手到LoginReady，沒有任何本清單的GUI成功證據。
完整測試需逐階段記錄實際通過／失敗，尤其學校切圖、kind2目標攻擊／死亡、
職業名稱與目的場景。TCP成功不能填補缺少的GUI欄位。

一名角色走完只證該職業路線的實機子集；其他職業目的圖、原版地理身份與
未修改原件仍需對應證據。保持正式Native CT及整體目標未完成直到足夠驗證。
