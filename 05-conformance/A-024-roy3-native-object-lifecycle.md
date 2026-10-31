# A-024 CT-081 — 原版 Client 物件生成移動更新死亡移除驗收

**未執行 native GUI。** 靜態 original Asgard.exe handler 8 組、21 x86 E8 calls、39 byte anchors，合成/原件離線 10 tests PASS 不是 E2E 成功。

|案例|操作|合格所需原生證據|
|---|---|---|
|N01|World loaded 後 S07 kind1/2/4/13/14，其他 kind5..12 配可用素材|S07 key/kind/x/y/image、Client object registry、真實畫面|
|N02|同 key S0C 移動／轉向|0x4EAC30 查物件，vtable+0x34/+0x3C/+0x40 變化與畫面一致|
|N03|同 key S64 路徑|0x47C9C0 及真正 Client 時間/距離/方向值，不以猜測 speed 替代|
|N04|物件先 S5F，暫不 S0E|原版死亡畫面與 registry 狀態，不把 die=remove|
|N05|物件收到 S0E，再有舊 S0C/S64|0x4BA0C0 移除與不產生 ghost object|
|N06|重複 spawn、move-before-spawn、跨 epoch、兩人 AOI|Server designed 不重複產生或跨圖污染；區分 Client 實測|
|N07|真正女性招募員點擊與 Script|C43 是否為 01+BEu32+04、S34/S2F/S44/C6C、map_ref、image ID、nNewJoin01 實際綁定|
|N08|怪物 AI 行動、攻擊、死亡、重生|原生封包及畫面，原服 timing/AI/spawn 若無 source 則 unknown|
|N09|kind 不合法、缺貼圖、S64 過量、舊序號|安全拒絕/斷線復原，不把 synthetic parser 當 native 測試|

紀錄 Asgard.exe SHA、MAP/C35/S15、S07 decoded rows、C43/C13、S0C/S64/S5F/S0E、S34/S2F/S44/C6C、畫面和 Server map epoch。S34/S3C 的其他 Client dispatch phase 要另外追。若需重查 World00.dat/Monster00.dat 只有 repo 已整理的 hash/index metadata；本次檔案環境未載入其 raw bytes。本階段 Client handler 靜態驗證不缺新檔；原版 NPC/Monster 實際綁定需 packet trace/官方 spawn config。
