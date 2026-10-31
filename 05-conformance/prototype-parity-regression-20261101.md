# 原型能力恢復：新版 Server 批次驗收

2026-11-01。**本頁全部 planned，未因舊原型通過就算新版通過**。使用既有CT，不新占全域CT編號；下列BATCH是操作順序標籤。來源 [差距表](../04-analysis-integration/prototype-parity-audit-20261101.md)／[交付合約](../02-server-planning/prototype-parity-delivery-plan-20261101.md)。

## 紀錄

每輪指定spec/Server commit與運作build、Client SHA／region／seed／是否修改、DB provider、資源版本、開始時間、匿名trace與case結果。程式存活、TCP、session phase、UI、DB結果各自記錄。合成、修改副本診斷、未修改Client三欄分開；每輪可以連續測多項，失敗後安全可行就繼續下一獨立case，不能把未到達情境填pass。

|操作批次|一次涵蓋的步驟|主要既有CT／預期|
|---|---|---|
|BATCH-A 帳號／創角|錯密→正確既有帳號；另以無角Account直接NewUser→錯密／取消→合法C02/C04→新角直接進World；再測已有角色普通登入|CT-097、103～105、107、112/113。負向結果可讀且不變更被拒絕資料；兩種入World路徑分開，不能用人工第二次C03替代創角直入。|
|BATCH-B 真圖／走停／保存|合法入圖→站立與八向走停→原地轉向→斷線重登→兩端重啟後回到最近已承諾保存的位置；另測錯CRC／舊ACK|CT-108/109、073/074及ONB-04。真MAP/C35、可見人物與權威位置一致；不是只看到S14(2)。正常重登／crash按宣告durability策略分開。|
|BATCH-C 衣服／染色|開背包→同連線換衣A/B→轉向再換→固定衣色改髮色→恢復素材原色→重登及切圖→另一玩家觀察|CT-064～066、073/074。slot/instance有效、穿戴與數量守恆、獨立RGB、面向與位置不跳；未宣稱所有102個資源服裝均可穿。|
|BATCH-D 在線切圖|有效World中管理端選合法圖與座標→不重登切圖→切回→重複同冪等請求／連點→錯CRC／超時／中斷→重登|CT-108/109、ONB-04及管理驗收。新epoch成功才提交；錯誤可解釋；衣服／面向／任務保留，同圖其他玩家未被回收。先兩張已驗圖，候選資源存在不算通過。|
|BATCH-E 聲音／時間同步|入圖聽到BGM→換曲→停止→切圖／重登恢復政策；進World閒置、移動中S66/C75、過期／重送回覆；另在創角表單停留超過60秒|CT-067～069、[CT-115時間同步](time-check-parity-test-plan.md)與RI-005。曲目provenance明示；保留Client音量；時間回覆不授予權威，表單不得被InWorld保活前提誤踢。|
|BATCH-F Web／回報與故障|使用既有P0管理→查角色／狀態→有權操作與越權／舊版本拒絕→一筆fail誤選pass後追加更正→依trace對照封包／validation／close／退出|既有WEBUI規劃、CT-112～114。按鈕需真API；Key不保存到瀏覽器storage／log；回報更正不抹除原件，未回應／手動關閉／socket close不混為crash。|

## 負向與資料責任

- 各DB provider分別做合成／持久化回歸；不能把SQLite通過自動推給PostgreSQL。不得在本次規格稽核中擅自跑現有Server測試或操作正式資料。
- 裝備未知slot、非owner、舊generation、越界／不通行／速度超限、舊epoch C35、重播管理請求都不能留下半更新；按ADR-009及已證native錯誤／校正回應，不因正常業務拒絕一律斷線。
- 原型C35僅長度、無限衣櫃、任意map預設曲目、修改EXE的捷徑不列通過標準。
- 本輪最小單人能力恢復後仍需原版雙人可見／裝備同步、NPC／怪物／教學、戰鬥／獎勵、營運恢復的原CT；不能以BATCH全過宣稱完整遊戲Server完成。
