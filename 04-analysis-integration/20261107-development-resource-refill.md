# Development管理工具：補滿測試角色資源

日期：2026-11-07。此工具用來支援技能實測時MP／SP耗盡的情境，屬於管理測試設計，不是從Client分析得到的原版恢復規則，也不代表原服存在免費補滿功能。

## 操作與權威契約

在Web管理的角色衣櫃頁填入帳號ID，按「補滿測試角色HP／MP／SP」。工具先讀目前資源版本，再送帶expected revision與非空request ID的補滿意圖。它只補到各資源既有上限，BP不動；角色死亡時不復活，也不補其他資源。角色等級、能力、經驗、技能、背包、地圖、進度、帳密與管理金鑰不重設。

- GET `/admin/dev/accounts/{id}/resources`：取得在線、已完成載圖的該帳號角色資源與版本。
- POST `/admin/dev/accounts/{id}/resources/refill`：以版本CAS與request ID提交一次管理補滿；回傳結果、目前權威資源及是否重播。
- 必須Development環境、loopback來源及有效X-Admin-Key。Production或非loopback為403；缺少／錯誤金鑰為401，管理金鑰未設定時沿用503鎖定。
- 離線、尚在載圖、owner/current lease不符或版本已變為409，要求在線並重新載入。不能直接對離線資料庫強制補值。

Server於同一交易從帳號關聯目前角色與World lease，鎖定該lease並要求載圖已提交，再沿用權威資源恢復規則與狀態收據。相同request ID重送不再次補滿；即使之後已施放技能消耗資源，舊收據也不覆寫新狀態。回應應帶目前狀態供管理畫面顯示。若新連線替代舊lease，舊交易必須受lease fencing約束。

在線Client沿既有狀態投影更新顯示，HTTP成功不能單獨視為原生畫面驗收。此功能不修改Client，也不恢復死亡角色。

## 定向驗證

獨立HTTP／SQLite整合測試3項通過：Development缺少／錯誤金鑰、Production403；離線／未提交載圖／錯owner／舊版本拒絕；在線補滿保留其他欄位、重送不回補新消耗、死亡不復活、結束World後拒絕。非loopback來源另以相同endpoint handler的request context驗證403，不冒稱外網實測。

測試使用獨立合成資料庫及暫時loopback HTTP服務，未啟動或修改使用者的Server與資料庫；原生畫面顯示仍待集中測試。
