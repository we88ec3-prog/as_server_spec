# A-022 Map/CRC 整合：可開發子集

來源：[BIN-first 研究](../03-analysis-requests/A-022-roy1-bin-analysis.md)，證據 `ev_a022_20261031_asgard_map_static`；Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

**observed-static**：S14 `0x57FDD0` body u8：1 請求本地 C35；2 loading callback；3 延時 3000ms 的異常分支。S15 `0x57FF30` body 3×BE u16 + flags u8 + other u8 + string8。第一個 u16 map_ref，flags bit0 invert/bit1/bit5/bit6 被拆出。S04 `0x589990` 連續 4×BE u16。C35 `0x573490` 兩個 BE u16，**第一個來自本地 MAP header file offset+4**（`0x4B4850`），**第二個來自 MapData structured checksum**（`0x4B4890→0x4B3650→0x4B2EC0`）；不能拿 map_id 或檔案 raw CRC 代替。CRC update primitive `0x43E0A0` 查表 `0x664720`；synthetic `01 02 03→0x1222`、`ABC→0x1AA6`，不代表真 MAP 的 C35 值。MapData 末段 record 是 16bytes。**A-002 勘誤：`0x4A8370` 實為 S03 交接 handler（region3/4）、不是 C25 入口**；C25 region/body 仍 partial，須另尋原生 serializer 證據。

**designed**：Server 必須先確定 map/ref/resource_version/epoch，再送 S15/S14(1)，驗證同 epoch、同版本 C35 後送 S04/S33/背包/S14(2) 才 InWorld；超時／錯圖／舊 CRC／斷線進 Reconcile；入圖 committed 與教程 completed 分離，重連不重領資產。

**unknown**：本次僅有 EXE，原版 tutorial map_id、出生 x/y/heading、首次旗標、原版教程圖 CRC 及原 Server 拒絕策略，仍待 A-015 MAP/Script/Born、A-016、A-023。狀態：`A-022=integrated`、`handoff_status=partial`、`implementation_ready=true`（通用世界載入）、`tutorial_content_ready=false`、`native_client_validation=not-run`，不能假稱官方教程出生已驗證。

## A-016：載圖與恢復之身份/epoch 限制（2026-10-31）

[A-016 BIN-first 報告](../03-analysis-requests/A-016-roy1-replay-recovery.md) / [安全恢復契約](A-016-idempotency-recovery.md)：C35 `0x573490` 只輸出 2×BE u16，**沒有 map_id/epoch/request ID**。Server 內部 loading_epoch 可隔離連線/重登狀態，但同 TCP 若舊 epoch C35 與新 epoch 期待相同 checksum pair，**單靠 C35 body 無法辨別**；須單一 pending loading、控制 in-flight/complete 邊界，無法安全判定時 fail closed 並重建連線。S14 control2 `0x4F23B5` 是 Client local loading callback，**不是**已持久化入圖/教程完成的 Server ACK。按最近 durable map/pos 恢復，CT-043/044 planned，Client E2E not-run。


## A-022 追加：MAP 真實幾何、旗標及有效座標區間

原版三份 `Map*.dat` 已收到，詳 [491 份完整 tile 研究](../03-analysis-requests/A-022-roy1-map-geometry-collision.md) / [safe coordinate 與碰撞契約](A-022-map-geometry-contract.md) / [機讀統計](../02-server-planning/map-geometry-evidence.json)。地圖 directory entry36 bytes 的 last4 LE 是 payload end，正常 MAP header 3×u16LE+width/height u8，block table `2*ceil(w/2)*ceil(h/4)` bytes、每 tile raw10B/local17B，尾 7/8/16-byte records；491/494 名稱 map 是完整正常格子資源，3 個 `00000/10000/20000` 不可當可走圖。`0<=x<w,0<=y<h` 僅幾何可索引，Client tile+6 bit0x10 參與線段遮蔽/阻隔，bit0x01 可動態變動，runtime 另有 occupancy grid。**非原 Server 移動/出生可行性證明**；C35 header2 可直接解，但真正 per-MAP structured checksum、tutorial map+spawn、Client blocked-step E2E 未證。CT-069～071 planned；A-005 碰撞 authority 仍 open。
