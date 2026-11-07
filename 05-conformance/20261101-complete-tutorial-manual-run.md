# 完整教學集中實機測試

**2026-11-02 狀態補充**：使用者後續已回報完成教學到城鎮；只讀持久紀錄對應Mage／Map4001。這是診斷副本單職業路線的人工通過，取代下方早期「沒有本清單GUI成功證據」的歷史狀態；其他職業實機、各快捷鍵／音效逐項結果不能由此一併推定。其後能力窗hover當機另有S08初始化修正，384項Server與五職業TCP通過，修正後GUI仍待既定復驗。五城身分新增[官方地理佐證](../04-analysis-integration/20261102-official-town-geography-corroboration.md)，不直接升級原服出生政策或未修改原件CT。

日期：2026-11-01。使用者要求完整「接受教學→下一張圖→教學→選職→目的城鎮」
接好後才安排測試。本輪所有Server路線、普通攻擊與職業投影已接入，358項
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
|技能／視野|Ctrl+D查看初始普攻；走遠再回學校NPC附近|普攻項目可見；NPC能重新出現，不用重登|
|生活／戰鬥|Life guide(29,35)及Combat guide(31,33)，分別交談並關閉|原始教學頁面能開關，不應空白或卡死|
|選職|Career guide(29,33)，選任一職業並確認|結果對話正確；職業更新不移位、不轉向|
|練習|先用滑鼠攻擊摩斯(31,34)，重生後站相鄰格並面向摩斯，按空白鍵|看見出拳與傷害數字，最後一擊後死亡動作；約五秒重生，不需重登；空白鍵不以游標位置選目標|
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
使用者重啟後回報「學校畫面正常，但後續步驟異常」，因此學校視角修正
已有 diagnostic-copy 人工通過證據；完整路線仍失敗，尚待定位具體後續畫面。

同輪唯讀持久紀錄已見生活／戰鬥對話關閉與普通攻擊命中里程碑，職業選擇
紀錄仍空。封包日誌亦見 S11／S13、S5F、重生 S0E／S07／S1A；這只證明
Server處理及送出，不能代替目標倒下／重生、教學內容或選職介面的人工確認。
不據此認定選職是根因，也不為繼續測試而代填職業或重設角色。
使用者隨後明確回報NPC離開畫面後返回消失、攻擊無動作及傷害顯示；
已按[視野／普攻追查](../04-analysis-integration/20261101-tutorial-visibility-and-basic-attack-followup.md)
分開處理，不能把職業紀錄空白誤判為使用者所指的失敗。

最新集中復驗版本包含[Motion4、S62與死亡時序](../04-analysis-integration/20261101-basic-attack-motion-action-and-death.md)：
原始／診斷EXE不變，Server358項及五職業TCP已過；GUI尚未重測。
沿用同一環境及既有角色接續，generated v2設定會先備份，再升級v3摩斯外觀；
戰鬥契約／角色／帳號／金鑰／里程碑不重設。初始技能是明示重建值，不宣稱原服ID。

清單其餘項目尚待完整人工結果。先前computer-use視窗存取核准逾時，
只證Client握手到LoginReady，沒有任何本清單的GUI成功證據。
完整測試需逐階段記錄實際通過／失敗，尤其學校切圖、kind2目標攻擊／死亡、
職業名稱與目的場景。TCP成功不能填補缺少的GUI欄位。

一名角色走完只證該職業路線的實機子集；其他職業目的圖、原版地理身份與
未修改原件仍需對應證據。保持正式Native CT及整體目標未完成直到足夠驗證。

城鎮身份另依[地圖標題來源](../04-analysis-integration/20261101-map-title-provenance.md)：
S15標題由Server提供，不能只憑顯示名稱把候選城鎮標記為原版綁定已確認。
記錄到達map_ref、實際場景及來源線索，與傳送／重登功能結果分開判定。

空白鍵步驟依[原生預設鍵與面前選取](../04-analysis-integration/20261101-default-space-attack.md)
更正；先前「游標放怪身上」不足以保證面向正確。分開判定S62技能清單、
原生空白鍵C13及技能項目C0E，不能把三者當同一條封包路徑。

[靜態物件分析](../04-analysis-integration/20261101-static-map-town-review.md)已發現
盜賊1001及武道家3001候選與城鎮形態不符。即使流程進圖／重登成功，也不能
將這兩條路線標記為職業城鎮驗收通過；待明確修正目的圖後再驗身份。

後續[v4候選內容](../04-analysis-integration/20261101-town-candidate-v4-migration.md)
將新盜賊／武道家目的地改為7001／6001，整份匹配的舊模板下次正常啟動會先備份
再升級；不改已保存位置。新版五職業TCP通過，但GUI與官方身份仍待核對。
若本次Server在升級前已啟動，其仍使用原載入內容，不必為此中斷NPC視野測試。

NPC邊緣觀察另依[原生窗格修正](../04-analysis-integration/20261101-native-pane-visibility-correction.md)：
向四個方向走動時，確認NPC仍在畫面可見處不會提早消失，返回時能在畫面邊緣
正常出現；不只檢查有沒有重新生成。使用者後續確認南往北返回正常；其他方向與怪物未全部驗收。

最新[實機回報修正](../04-analysis-integration/20261102-client-feedback-guardian-shortcut-audio.md)
需集中確認：南側向北返回NPC、普攻拖入快捷列後數字鍵空揮／命中、空白鍵空揮、
命中與摩斯死亡音效、誤點守護鈴保持連線。守護鈴完整功能仍未完成。

後續[快捷鍵C65與NPC MISS](../04-analysis-integration/20261102-native-shortcut-followup-and-npc-miss.md)：
使用者確認南往北NPC正常，回報空白鍵空揮無效、快捷列1空揮斷線。C0E之後的C65
已加入issued-row驗證且不重複攻擊；教學NPC近身MISS有原生素材及renderer支持。
下輪只需集中確認：快捷列1空揮後仍能走動／再攻擊摩斯、鄰近NPC普攻是否MISS且
不增加打怪進度、命中與死亡音效。空白鍵若仍無效，保留Client／Server給被動讀取；
不能只憑C65修復而把空白鍵列為成功。不必重創、重設金鑰或再重複NPC南往北案例。

最新實機回報：NPC完全沒有揮拳、首次快捷鍵命中依賴先Space命中、學校登入無BGM。
[更正與集中驗收](../04-analysis-integration/20261102-first-shortcut-npc-tail-school-music-and-reconnect.md)
補足未擴充S13必讀尾碼（15B）、C0E依面前格選取、額外地圖音樂繼承與C00起始重連。
下一輪請同時確認面向相鄰新生摩斯直接按1造成第一次傷害、對面前NPC按Space揮拳及MISS，
並聽學校BGM；接著完成Life／War、選職、Departure出發與同Client重登。
當前學校僅接Map7，門／其他室內圖未接線，不能把該重建路線當成原版完整圖數。
