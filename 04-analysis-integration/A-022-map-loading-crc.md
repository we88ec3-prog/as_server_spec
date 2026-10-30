# A-022 Map/CRC 整合：可開發子集

來源：[BIN-first 研究](../03-analysis-requests/A-022-roy1-bin-analysis.md)，證據 `ev_a022_20261031_asgard_map_static`；Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

**observed-static**：S14 `0x57FDD0` body u8：1 請求本地 C35；2 loading callback；3 延時 3000ms 的異常分支。S15 `0x57FF30` body 3×BE u16 + flags u8 + other u8 + string8。第一個 u16 map_ref，flags bit0 invert/bit1/bit5/bit6 被拆出。S04 `0x589990` 連續 4×BE u16。C35 `0x573490` 兩個 BE u16，**第一個來自本地 MAP header file offset+4**（`0x4B4850`），**第二個來自 MapData structured checksum**（`0x4B4890→0x4B3650→0x4B2EC0`）；不能拿 map_id 或檔案 raw CRC 代替。CRC update primitive `0x43E0A0` 查表 `0x664720`；synthetic `01 02 03→0x1222`、`ABC→0x1AA6`，不代表真 MAP 的 C35 值。MapData 末段 record 是 16bytes。C25 `0x4A8370` 存在地區 3/4 分支，仍 partial。

**designed**：Server 必須先確定 map/ref/resource_version/epoch，再送 S15/S14(1)，驗證同 epoch、同版本 C35 後送 S04/S33/背包/S14(2) 才 InWorld；超時／錯圖／舊 CRC／斷線進 Reconcile；入圖 committed 與教程 completed 分離，重連不重領資產。

**unknown**：本次僅有 EXE，原版 tutorial map_id、出生 x/y/heading、首次旗標、原版教程圖 CRC 及原 Server 拒絕策略，仍待 A-015 MAP/Script/Born、A-016、A-023。狀態：`A-022=integrated`、`handoff_status=partial`、`implementation_ready=true`（通用世界載入）、`tutorial_content_ready=false`、`native_client_validation=not-run`，不能假稱官方教程出生已驗證。
