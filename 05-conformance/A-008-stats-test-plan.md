# A-008／SYS-STATS 原 Client 對接與離線驗收

原件 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145；Client profile TW-seed0-local-v0.1。研究報告：task_a/roy2/A-008-analysis.md。

## CT-061：離線 Binary-first 契約（此研究已執行）
- python task_a/roy2/a008_native_probe.py Asgard.exe
- python -m unittest discover -s task_a/roy2 -p 'test_a008_status.py' -v
- 預期：15 native VA byte patterns / 4 RTTI PASS；10 synthetic tests PASS。
- 測試 S08 的 0x40/0x20/0x10/0x08/0x200 旗標合併與原生順序、61B full 段、32-bit BE/16-bit BE、最大255 bytes 長度及 count、缺少/多出 bytes 拒絕、C47 5 個一熱位元。
- 可重跑離線結果 PASS；**native_client_validation=not-run**，CT 向量可保留 planned，禁止聲稱 GUI 已通過。

## CT-062：Native Client E2E（需有連線可用的相容 Server 時再跑）
1. 成功完成登入 C03/S03/C10、S15/S04 及世界初始化，在狀態窗打開前後收 S08 flags 0x40+0x20，錄製 decoded body（遮蔽帳號和敏感資料）、畫面數值與初始化前後變化。
2. 針對 UI id 0x13..0x17 逐一按下；Client 必發 C47 opcode 0x47、一個 byte，依序 01、02、04、08、10。觀察 S08 是否回覆、何時刷新。**不可預設所有按鍵都有獨立 ACK**。
3. Server 測試（designed）：餘額不足、未登入、無權限、非法 one-hot 值、重送、不同角色 session、加點上限。確保不重複扣點、拒絕不發獎，原版 UI 錯誤碼未知。
4. S08 以 0x20 更新四組 current，覆蓋 0、max、max+1、0xffffffff。對照 native GUI 的無號 clamp/數值顯示；不能認定超限值是原服允許值。
5. 模擬減血至 0、復活、BUFF 及裝備變更。比對 S08 與另行 S5F/技能/裝備包的事件次序、可見性及重登值，不把 S08 結束視為死亡。
6. ExpBarDialog 經驗條及 StatusDialog 值單位逐項拍攝、比對等級/EXP 增減。原版公式、每欄 HP/MP/能力名稱仍 unknown，不能依推測建立完整公式。
7. 需記錄每次 packet raw/decoded body 的 frame 長度、flags、欄位、Client state 與 UI 結果；發現 bug 按 Client evidence 回 A，Server 策略缺陷回 DEV。

**驗收狀態**：CT-062 planned / native Client not-run。A-008 的 Client 靜態 C47/S08 I/O 交接可 ready；DEV 公式、E2E 與玩法驗收獨立。
