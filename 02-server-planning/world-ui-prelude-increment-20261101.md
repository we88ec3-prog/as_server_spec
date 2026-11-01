# 直接開發增量：先恢復已存角色的可見World

使用者來源：USR-018（直接開發、測試時由使用者操作）與USR-019（參考本地原型並回寫spec）。對應PAR-002、ONB-03、RI-007與CT-108，設計不依賴取得私有roy程式。

公開行為與證據：[UI prelude／C43整合](../04-analysis-integration/world-ui-prelude-c43-20261101.md)。本輪以已存角色C03→S03→C10→Region3 C25為入口，修正S02 UI建立與載圖期間附帶C43造成的中斷；保留owner、Map0/member hash與C35 exact pair。這不是替創角發未證grant，也不恢復舊原型的寬鬆CRC。

交付狀態：source-implemented、248項合成回歸與獨立HTTP/TCP smoke通過；已提供獨立測試入口並要求使用者操作。原始Client畫面仍not-run；使用者的修改副本結果須另記。下一個實際觀察點是是否收到真C35、是否顯示地圖／自身，再根據日誌補未知S15欄位／Client狀態；不要只因S14(2)寫入就宣稱可玩。

移動目前保守stop/rebase；後續按A-005權威碰撞／速度與持久化，外觀按A-006/A-007，音樂按A-019。若原版入圖先前仍缺UI callback，持續分析並在同一開發迭代修正，不再要求使用者轉交給另一位開發者。

## 第二輪回驗與修正

診斷副本收到 C35=00060F90，先前 Server 錯預期00040F90；已追到 MapData 物件／檔案 offset 混淆並修正。詳見[第一欄勘誤](../04-analysis-integration/c35-map-reference-correction-20261101.md)。248項測試與本機TCP smoke通過，畫面仍待使用者重驗。測試入口依使用者需求改為原生預填ID的既有診斷副本，見[ID預填需求](../02-server-planning/test-client-id-prefill-20261101.md)。
