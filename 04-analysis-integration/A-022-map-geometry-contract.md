# A-022 — MAP geometry/collision-like flags and safe-coordinate Server handoff

[原始三個 MAP archive / 原版 Client 逐欄報告](../03-analysis-requests/A-022-roy1-map-geometry-collision.md)；[原通用 C35/載圖契約](A-022-map-loading-crc.md)。Evidence `ev_a022_20261031_map_archive_collision_resource`。Client SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

原件可解：Map0 288 named/287 proper maps，Map1 184/183，Map2 22/21；合計491份 tile resources 解到精確 end。每個 archive directory entry36B，last4B LE 是該 entry payload end，而非 start；第一 start=8+36*count。3份第一個 `00000.map`、`10000.map`、`20000.map` 零維特殊資料不能當 tile 圖。MAP header 三 u16LE + width/height u8；block array u16LE[ceil(w/2)*ceil(h/4)]；tile array records10 bytes each/w×h，Client 記憶體結構 stride17；三段 count:u32LE + record size7/8/16 bytes。 tile indexed `y*width+x`；coord bounds `0<=x<w,0<=y<h`，這**只表示可索引**。

Client 可證：MapData accessor `0x4B2C80` returns local tile17 pointer，`0x4B4BB0` 一條線段判斷按 tile flags offset6 **bit0x10** 決定阻斷；`0x4B2CA0` 設/清 bit0x01；`0x4B2D00` 使用 client runtime +0x258 另一個 u32 occupancy grid 作周邊空值判斷。這不構成全部的原服 walkability/placement/spawn/LOS policy。**Server 不得把 flag0x10 或 flag0x01 單獨轉成全圖 Boolean canWalk**。幾何合法但 blocked/dynamic occupied/高度不可達依 authority 另驗，A-005 碰撞/移動完整政策仍 open。

DESIGNED 資源模型 `MapResource(archive_sha,map_id,header_word,dimensions,block_tiles,tile10,records7/8/16,integrity_verified)`；在解析任何 offsets/counts 前做 length/overflow bounds、禁止無效維度；Server 客戶端定位 S04/S15/C35 與具體 MAP 資源版本對齊。C35 = u16BE original header2 + u16BE **structured** checksum, **不是** raw CRC 與 map ID，且無 epoch；重叠相同 pair 時 fence/closed/reconnect。當缺 original-server validation 時不以 geometry-valid 自動判斷可走、可 spawn 或新手出生。Born (31,29) 只指向女性招募員引導點。

A-022 原先 integrated，這次追加 observed-resource collision-like flags/geometry；`map_resource_geometry_ready=true`（491份）；`native_map_collision_full_ready=false`、`tutorial_content_ready=false`、`native_client_validation=not-run`。CT-069～071 planned，真正 first tutorial map/spawn 和原服 blocked-step packet capture 未提供。