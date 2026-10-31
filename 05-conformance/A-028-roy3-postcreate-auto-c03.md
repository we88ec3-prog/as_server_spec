# A-028 Roy3 CT-105/107/108：創角後背景 C03 與 World 原生驗收

目前狀態 planned / native-client-validation=not-run，使用未修改 Asgard.exe SHA db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145，登入敏感資料全遮罩。

|Case|原版操作|必要原生觀測|
|---|---|---|
|A28-01|Region3 新角色 C02→S02(0)→C04→final S02(0)，不按登入|是否真的經 0x4A9617/0x4A8950(4,0)/0x4A8A30 自動發 C03|
|A28-02|Region3 缺第一或第二快取文字欄位|constructor auto 應被 guard 跳過，若有其它登入入口須另紀錄|
|A28-03|Region3 保持快取非空，按住 Ctrl vs 放開|驗 GetAsyncKeyState(VK_CONTROL) 高 bit 判斷、差異僅屬此 constructor auto|
|A28-04|Region3 automatic C03 vs 登入 callback C03|decoded C03 兩個 string8、最後 u8 auto0 vs callback1；只保存長度/hash，永不保存密碼|
|A28-05|Auto C03 → 實際 Server S03|合法帳號與角色 owner/generation，S03 失敗/成功、S02/C15 舊狀態不混淆|
|A28-06|成功 S03→新 TCP C10→C25 Region3|C10 token 必須有 Server grant，C25 三 string8，不得用 C25=01 開 World|
|A28-07|World 首 S2C / S15/S14/C35/S04|原版地圖與位置/viewport，可見 World，進遊戲無手動重新登入|
|A28-08|Region0/1/2/4 首次建角|確認別的 Client native automatic path，不從 Region3 外推|
|A28-09|C04 ACK 遺失/跨帳號/重播/C15/中斷|角色不重建、不重賞、Session與 World grant 不串線；錯誤訊息在原版 GUI 可讀|

保存去敏包 opcode/body_len/seed/ordinal、兩 TCP 連線來源/目的及 FIN/RST、原版 UI 錄影、Region、Ctrl 狀態、原始 EXE SHA、Server 角色提交/World grant trace。任何未完成案例維持 not-run，不能使用 12 項 Python 測試替代原生 CT-105/107/108。
