# A-022／roy1 地圖碰撞與幾何：經原件勘誤後的 main 版本

來源：`task_a/roy1@fd189fc74fd7897558d03322fe19e6a0809568c1`、`task_a/roy2@81d3a2ba77ff7ec4ab8e1b6323664315883ea0b5`、原件 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`。Roy1 舊報告的 491/494 源自錯誤地把 index 起點當 `8+36*n`；實際 `4+36*n`，前4 byte被跳過後首筆 `00000/10000/20000.map` 才會被錯誤判為特殊空圖。原版 Roy1 commit 保留可追溯；main 不保留此錯誤結論。

## 真實可重現證據

- DAT 起始 `LE u32 slot_count`（含最後一個 sentinel），從 file+4 起，每筆36 byte：`LE u32 payload_start + raw filename[32]`。最後 sentinel offset=EOF，前後 start 單調。
- 成員 MAP：`3×LEu16, u8 width, u8 height, ceil(width/2)*ceil(height/4)*2B block, width*height*10B tiles, count×7/8/16B tails`，精確 EOF。原件 Map0=288、Map1=184、Map2=22，**494/494**，共 **7,701,805 tile**（[metadata](../02-server-planning/map-geometry-evidence.json)）。
- Client map loader `0x4B33A0`；`0x4B2C80` 使用 `y*width+x`，原始 tile 10B 展開成 Client local 17B；原生映射的26個 byte anchors 已核對。
- Client 畫面相關 `width*48 / height*32` 是視覺格子候選，**不是**已證 C33 網路坐標單位／角色腳底；tile flag bit0 是 runtime set/clear，bit4(`0x10`) 是一條線段阻擋測試，另有獨立 u32 per-cell grid。**不能將任何單一 flag 當全部 walkability / NPC spawn 判定**。
- Born(31,29) 在477張地圖上是合法 tile 索引，但僅是女性招募員的文字導引，**不是**已證教學地圖、原服出生點或可走格。
- C35 第一欄來自 MAP header2，第二欄是 structured checksum（不是原 MAP raw CRC），仍缺整圖重現與真實 loading sequence。Server 必須在 map revision/World Session generation 中 fail closed。

## DEV / CT 正確分界

可以直接實作 DEV-060 MapResourceCatalog/TileQuery/bounds/版本保護；DEV-070-M `CommitValidatedMove` 不得以 `in_bounds` 視為 `walkable=true`。需要實際 Client C33/S0B 成功與碰撞回滾、角色腳底/像素坐標、來源版圖/出身與 C35 驗證。原版 Client GUI/E2E **not-run**。

**來源舊 CT-069/070/071 是 Roy1 當時的局部編號，main 不沿用**；main 既有 CT-069 音樂／CT-070 雙人AOI不修改，這次原件離線核對是 **CT-090**、實機步行/撞牆是 **CT-091**。

[跨分支驗證](../04-analysis-integration/merge-review-roy1-roy2-20261031.md) · [Roy2 A-015 專項](../task_a/roy2/A-015-map-coordinate-collision.md)。
