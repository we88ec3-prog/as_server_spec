# 已穿裝備點擊斷線：封包時序與卸裝交易界線

日期：2026-11-07。此頁整理本地診斷紀錄的去識別摘要；不包含封包本文、帳密、金鑰或私有實作。

## 使用者回報

使用者表示點擊已穿裝備後斷線，並要求可以脫下裝備。這是使用者需求與操作回報；不能單憑操作描述推定其觸發的是卸裝指令。

## 已觀察的時序

目前兩次戰士測試的連線紀錄均在WorldReady階段收到C3A（opcode 0x3A、本文長度1 byte），被Server分類為`unknown-opcode`，以`closed`處置，隨即以`invalid-native-protocol-or-state`關閉連線。

| UTC時間 | 事件 | 關鍵欄位 |
| --- | --- | --- |
| 2026-11-07 14:12:02.0499121 | C2S C3A | len=1、ordinal=12、WorldReady→WorldReady、Unexpected=true |
| 2026-11-07 14:12:02.0522464 | 關閉連線 | Stage=InWorld、Reason=invalid-native-protocol-or-state |
| 2026-11-07 14:15:14.0334744 | C2S C3A | len=1、ordinal=20、WorldReady→WorldReady、Unexpected=true |
| 2026-11-07 14:15:14.0353032 | 關閉連線 | Stage=InWorld、Reason=invalid-native-protocol-or-state |

對應臺灣時間為22:12:02及22:15:14。兩次關閉前最後一筆S2C均是S1A（0x1A、len=8），紀錄沒有卸裝結果封包。另一個盜賊測試的C1C（len=4）正常處理，最後由C0B離開至LoginReady後peer-eof；該段沒有同類C3A關閉。

此紀錄確認**未支援的C3A緊接著導致關閉連線**。它不能證明C3A的UI語意、1 byte欄位代表哪一種格位，或C3A本來就是卸裝。這些仍須原生UI producer／handler證據；不能以C1E或C1D代替本次實際收到的opcode。

後續REA已確認C3A為CUpdatePartPacket、C1F為CTakeOffPacket，並完成本輪Server修正；見[原生分流與卸裝合約](20261107-equipped-click-and-native-takeoff.md)。上段僅陳述metadata本身的證據界線，不代表後續仍未追到原件。

## Server卸裝合約與保護

正式卸裝是獨立權威操作：鎖定目前角色owner與lease，確認載圖已提交、背包版本、裝備格的實例ID及實例版本、角色存活與可用背包格，再於同一交易將同一件物品移回背包。滿背包或死亡為業務拒絕，保持裝備與資產不動；不能先清Client格位再檢查。

同一operation ID的成功收據可能是歷史snapshot。重放不寫回歷史狀態；Host發送畫面投影前應重讀目前權威狀態，避免已換上另一件後被舊卸裝收據清掉。封包缺乏原生唯一operation ID時，Server不能宣稱可自動辨識任意重送，仍須依單一連線處理順序及投影上下文產生內部意圖。

未知的物品查詢與卸裝入口必須分開辨識。只有原生證據確認的動作才能改資產；對已識別的合法查詢不應以「尚未實作」為由斷線。

## 本輪驗證

正式物品Store定向SQLite整合測試11項全部通過。本輪新增4項，涵蓋死亡卸裝不動產、錯owner／舊lease／未提交載圖的拒絕、錯instance／item revision／inventory CAS不改資料，以及成功卸裝後穿上另一件再重放舊收據仍保留新狀態。既有測例另涵蓋滿背包卸裝拒絕、騰出格位後成功卸裝與收據拒絕重放。

這是交易邊界驗證，不代表Client點擊卸裝已通過，也不代表全套Server回歸或PostgreSQL已驗證。原生C3A語意、實際卸裝入口及畫面清格／外觀更新由後續原生分析與集中實機測試補充。
