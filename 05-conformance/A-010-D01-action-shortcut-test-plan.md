# A010-D01 — CT-095/096 技能清單、ID 與快捷列增量驗收

詳細來源：03-analysis-requests/A-010-D01-roy1-action-shortcut-20261102.md。原始遊戲素材不入 Git。

|項目|已取得的離線原件證據|Native GUI/Server 尚未證|
|---|---|---|
|S62 已學動作|reader 0x579020 讀 kind/slot/BEu16/3xu8/4xstring8/u8/BEu16/u8；consumer 0x4F2CD0 建 ActionEntry；原件 opcode0x62|初始 World snapshot 的官方發包時機/技能 ID/完整 name/icon|
|S63 移除|reader 0x585950 兩個 u8，0x4F2F10 刪 row 並清快捷 ref|學習/升級/移除的 Client C2S|
|快捷配置|0x559470 每列10格×12 bytes；Shortcut.IsValid/Type/Slot 本地設定讀寫；0x489E60 類別轉換|跨角色/跨電腦是否持久與真正快捷鍵 GUI|
|C4D 綁定|S62 cast_value→ActionEntry+0x80E→0x401ED0 nonzero C4D BEu16；zero 走 noncast|官方 spell id、C56真 UI producer、技能消耗與施法確認|
|負向驗證|S62 截斷、string8 太短、尾端多餘、S63 長度錯、快捷格缺失均拒絕／不生技能|Native GUI錯誤狀態需實機記錄|

執行：python tools/a010d01_shortcut_probe.py Asgard.exe；python -m unittest discover -s tools -p test_a010d01_shortcut_probe.py -v。

本地原件核對 33/33 VA byte windows、3/3 設定名稱、15/15 tests PASS。**CT-095/096 的正式 Native Client 狀態依然 planned/not-run**。技能圖示深入缺 Icon.dat 的 skill.ypf/spell.ypf。
