# A-022 原版 MAP 格子與安全坐標 Server 合約（Roy1/Roy2 修正）

- 真實容器：從 file+4 起的 `n×36B` LEu32 **start offset** + name32；第一資料 `4+36*n`，最後 sentinel=EOF。**494/494** 可完整解碼，Roy1 舊 `8+36*n` 是誤判。
- MAP payload 8B header+block+tile10×w×h+尾段7/8/16；Client local 17B tile，索引 `x+y*w`。geometry valid 僅保證 tile 可查，不保證可走、NPC 可生成或出生點。
- Client 48×32 pixel extent 是候選視覺坐標，bit0 runtime、bit4 line test、aux u32 grid 三種獨立資料，不能無條件組成原服 walkability。
- C35 第二欄 structured checksum 尚未從原始 map 逐圖生成；不能以 raw CRC、默認0或接受一切 C35 代替。
- DEV-060 實作版號+map_ref索引、TileQuery/bounds/原件 SHA；DEV-070-M 再接權威 move，並維持 SharedMapKey 玩家共享 NPC/怪物。CT-090 離線、CT-091 原生移動 `not-run`。
- [勘誤報告](../03-analysis-requests/A-022-roy1-map-geometry-collision.md) · [版本化資料](../02-server-planning/map-geometry-evidence.json)。
