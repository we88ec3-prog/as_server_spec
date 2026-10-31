# A-005 Client collision／S0B Server 交接契約（roy3）

來源 task_a/roy3/A-005-native-path-collision-closure.md；A005-E15..E21。
A005 integrated / static handoff ready / native Client GUI not-run。

1. Native 0x4BE470 在 21×19 / stride12 local grid 搜尋 8 方向；每個相鄰候選透過 0x4B8B20。
2. 候選 gate：global bypass→1（實際用途未知），0x4EA900(candidate,0)==1→0，dest effective flags bit0→0，若 src flags bit3 且 source direction byte&(1<<direction)→0，其餘→1。這**不是**正式 Server auth/collision policy。
3. Effective Tile：0x4B4920 boundary guard→0x4C1850，從 17B memory tile+6 取 11B，overlay 區內 u32 flags=(memory_flags|dynamic_add)&~dynamic_remove。source direction byte 是 in-memory Tile+0x0C，不是 raw MAP 格位的一個固定 byte。bit4 另屬 0x4B4BB0 線段消費鏈。
4. 八鄰方向索引：0 (0,-1)、1 (+1,0)、2 (0,+1)、3 (-1,0)、4 (+1,-1)、5 (+1,+1)、6 (-1,+1)、7 (-1,-1)。實際 C33 方向可能另有語意；只擔保 native path helper。
5. C33 (3×u8) 的本地 next seq 發送後加 1 modulo128；S0B (2×BEu16+u8) 回原始 seq low7，bit7 清/設分別走位置/路徑停止與 prediction/rebase。這是 Client 靜態分支；是否原服正式錯誤碼/GUI 顯示仍須 native CT。
6. Server 應獨立控管 session、same map/revision/C35、epoch、speed、重送、權威位置、碰撞輸入及動態物件。若無可驗證碰撞政策，fail closed；不能用 00006.map raw bit0 clear 900 connected candidate 當官方已走過的白名單。
7. 下一步 DEV-ENTRY-05/CT-109 原版 GUI 走路、撞牆、序號127→0、權威 rebase、雙人同圖；見 05-conformance/A-005-native-path-collision-test-plan.md。
