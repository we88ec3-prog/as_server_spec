# A-015／roy2：Client MAP 解析、碰撞資料與可用座標原件分析（2026-10-31）

> **最新規格範圍**：既有 `A-015` 已完成資料來源/格式與權利邊界；本節額外把 MAP 解析、tile 座標與真正碰撞的證據分開處理。**Client 原生結構已驗、所有 MAP 格位可定位；玩家真正 passable / spawn-safe 規則仍未證實**。不得用單一旗標推算原服合法出生點。

- 唯一工作分支 `task_a/roy2`；沒有新建 branch、沒有改動原始資源，僅推送非素材程式碼與聚合 metadata。
- 原件 `Asgard.exe` PE32 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
- `Map0.dat`：`dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761`；`Map1.dat`：`8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b`；`Map2.dat`：`5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb`。
- **證據等級**：original PE instruction／original three MAP archives＝observed-static/native-resource；自造 MAP、DAT 及座標試算＝synthetic；玩家走路、實際 collision/出生點、原版 Server policy＝unknown/not-run；Server 拒絕越界等為 designed safety gate。

## 1. MAP 原始檔 → Client 記憶體欄位

原生 loader `0x4B33A0`；`0x4B34A5..0x4B34F3` 分配 block 與 tile；`0x4B3520..0x4B355C` 複製 tile 至已配置陣列；`0x4B3575/0x4B35AD/0x4B35BC` 處理 7/8/16B 尾段。獨立地圖 `%05d.map` 透過 library `map_id//10000+9` 查 `Map0.dat`、`Map1.dat`、`Map2.dat`（具體 map ID 存在與否必須在指定 archive 驗證）。

|原始 MAP offset / 資料|Client memory 展開／索引|證據與界線|
|---|---|---|
|0..5：三個 LE u16|header 的 +0/+2/+4（其中 +4 在 C35 檢查使用）|Client `0x4B4850` 讀 map header+4；不能稱其就是地圖 ID 或最終 checksum|
|6、7：u8 width、u8 height|Client MapData +0x240 = width，+0x244 = height|原件 `0x4B2C20/0x4B2C30` 取寬高；0 不合法|
|8 起：`ceil(width/2)*ceil(height/4)*2` bytes|+0x250 block pointer；+0x248 block width；+0x24C block height|讀取函式 `0x4B2C60` 對 block 按 **2 bytes/entry** 訪問。bit/碰撞意義未證|
|之後 `width*height` 筆 **10B tile**|Client 每筆分配 **17 bytes**，+0x254 起，`0x4B2C80` 訪問 `base+17*(x+y*width)`|每筆原始 `LE u16,u16,u16,u32(flags)`，原生本地值分別置 +0,+2,+4,+6；其餘 7 bytes 來自本地初始化/其他函式，不是磁碟固定欄|
|後面 3 段各 `LE u32 count + count*7/8/16 bytes`|+0x260/+0x264/+0x270 等保存指針/數量；另建每格 u32 的 +0x258 網格|7B `u8,LEu16,LEi16,LEi16`；8B 四個 LE u16；16B `LEu16,u16,u32,u32,u16,u16`。**不能直接叫 NPC 出生/傳送/碰撞表**|

磁碟/記憶體 stride 不同：`10B` 是 MAP 原始 tile，`17B` 是 Client **in-memory** tile；`+6` 上的完整 32-bit flags 才是可分析的旗標，不能只取 low byte（此版存在 `0x200`）。

## 2. Tile 座標與畫面像素座標：原生映射

```text
0 <= tile_x < width
0 <= tile_y < height
index = tile_x + tile_y*width

raw_tile_offset = 8 + ceil(width/2)*ceil(height/4)*2 + 10*index
memory_tile_address = map.tile_ptr + 17*index
raw_flag_u32 = LE32(raw_map[raw_tile_offset+6:raw_tile_offset+10])
```

原生 `0x4B4920..0x4B497E` 先檢查 **x>=0 且 x<width、y>=0 且 y<height**，再調用 tile 消費函式 `0x4C1850`；無效座標走輸出 0 路徑，**證明 Client 有邊界 gate，但未證這是玩家移動成功 gate**。

另外 `0x4B4A3B` 使用 **height × 32**、`0x4B4A73` 使用 **width × 48** 做視圖/範圍限制。由此可做定位候選：`tile_x = floor(pixel_x/48)`、`tile_y = floor(pixel_y/32)`，只在像素 `0<=x<width*48, 0<=y<height*32` 的本地範圍使用。**這是 Client 畫面幾何/候選 grid mapping，不是已證的角色腳底座標、點擊正確格中心或實際碰撞格索引。**

## 3. 原版碰撞與佔用資料至少三條不同消費鏈

|資料來源|Native reader/caller|已證行為|不能推論|
|---|---|---|---|
|原始 tile `+6` 的 `u32 flags` **bit0**|動態修改 `0x4B2CA0`，非同一個 line-test；`0x4D1206..0x4D120F` 在另一條 grid 掃描使用 `test [tile+6],1`|確定 bit0 能由 Client 本地設/清，也有消費者|不能稱 bit0=實際玩家可站立；該掃描可能為另一用途|
|同一 tile `u32 flags` **bit4 (0x10)**|`0x4B4BB0`、`0x4B4BEB`、`0x4B4C03/0x4B4CB8/0x4B4D58`|對一條線段/格列進行 bit4 檢查，命中會返回 0，不命中返回 1（由分支現場確認）|這是**線段旗標檢查**，不能無條件當玩家行走碰撞；也不能等同 bit0|
|MapData **另一個每格 4-byte** 網格|+0x258、`0x4B2CE0`、`0x4B2D00`、`0x4B3250`；loader 在 `0x4B35F6` 呼叫格位建構|Grid 4-byte/格；`0x4B2D00` 在目前格非零、上一列左右/中間和目前左側為零時回 1。另有 header 值比對與格位寫1|這可能是區域/物件/地圖資料的另一個佔用或分類層，**未證與可走路的關聯**；它不是 raw tile flags，也不是每格17B 中的欄位|
|原始 tile 外的 block 2B/entry|block pointer+0x250，`0x4B2C60`|block 索引是另一組格子布局（ceil width/2, ceil height/4）|尚未有原生玩家移動判定 consumer，可否走不能用此 block 一筆就判定|

因此最低限度的 Server 相容性設計應把 `in_bounds`、`tile_flags_bit0`、`tile_flags_bit4`、`auxiliary_grid`、`line_segment_result`、`player_walkable` 分為**獨立欄位/證據層**，其中 `player_walkable = unknown`，不可寫成 `flags==0` 或 `flags&1` 的權威版本。

## 4. 494 張原始地圖完整校驗：不能由 (31,29) 決定教程出生

這次獨立重掃全部三個 SHA 綁定原始 MAP 資料庫：

|庫|map 數|tiles|bit0 設置|bit4 設置|含 tile(31,29) 的 map|
|---|---:|---:|---:|---:|---:|
|Map0.dat|288|4,347,940|2,779,914|2,415,339|284|
|Map1.dat|184|2,983,365|1,986,238|1,876,320|171|
|Map2.dat|22|370,500|233,869|211,497|22|
|**合計**|**494**|**7,701,805**|**5,000,021**|**4,503,156**|**477**|

- 整庫旗標精確計數：`0:2,701,300`、`1:496,877`、`16:12`、`17:4,503,144`、`512:472`。**這個分布完全不足以證明 0/1/17 各代表可走/不可走**。
- 在 477 張包含 `(31,29)` tile 的地圖，該格 flags 取值為 **0:242、1:109、17:126**。所以 Born.dat 的導引點不能驗證原服 tutorial map_id 或實際合法出生位置。
- 8B tail 中候選 `+2,+4` 的 396/396 組、16B tail 中候選 `+12,+14` 的 2269/2269 組均符合 `x<width*48,y<height*32`，提示與像素座標可能有關；但 **8B/16B 尾段的「本體是 NPC/傳送事件」仍未證**。不能用 48×32 將它們直接當 spawn points。
- MAP payload 曾有 **494 名稱對 330 個唯一 bytes**；別名相同不代表 Server map identity/instance 一樣（繼承 A-015 previous structural audit）。
- 既有 Born.dat 原始 XML 僅指路 (31,29) 的女性招募員，**不等於玩家出生座標**。

## 5. Server 交接：可實作與尚未證明

|Server 需要|能立即採用的 Client 依據|仍須驗證|
|---|---|---|
|讀取官方 MAP|嚴格 DAT 索引/EOF、map name、header/塊/Tiles/tails；原件 494/494 結構 PASS|MAP 相容版本與 Client 版本尚未有官方 release manifest|
|按 map ID 定位檔案|資源庫 `map_id//10000 +9`、`%05d.map`|對指定 map id 必須確認實際檔案存在|
|用 tile (x,y) 取單格資料|負座標、越界檢查；raw offset 公式；tile BE/LE 正確處理|tile flag 是否可走的權威語義 |
|計算畫面候選坐標|48×32 邊界與 floor 索引作**候選視圖座標**|Server spawn/移動封包的真實坐標單位、Client 角色腳底點與格中心|
|驗證角色移動 C33|必須以 Server session、map instance、位置及合適碰撞版本校驗（**designed**）|Native 真實玩家 collision mask、移動時是否動態重設 bit0、撞牆時 S0B/動畫回滾；交 A-005／CT-070|
|選定合法出生點|先檢查地圖存在、位置 bounds，**另要求已證或人工驗收的 passability policy**|原版教程 MapID/出生點/原服策略未知，絕不可自動選 Born(31,29)|

範例最小 enum（**designed**）：`OUT_OF_BOUNDS`、`IN_BOUNDS_UNVERIFIED`、`PASSABLE_NATIVE_VERIFIED`、`BLOCKED_NATIVE_VERIFIED`。在還沒有真正 Native CT 的 map/profile 上，只能出前兩種結果；**不能**對 Server 說「從 MAP 已取得全部可用座標」。

## 6. 原件再現、測試與證據編號

```sh
python task_a/roy2/a015_map_native_probe.py Asgard.exe
python task_a/roy2/a015_map_coordinate.py --verify-original-sha Map0.dat Map1.dat Map2.dat
python -m unittest discover -s task_a/roy2 -p 'test_a015_map_coordinate.py' -v
objdump -d -M intel --start-address=0x4b2c60 --stop-address=0x4b2d60 Asgard.exe
objdump -d -M intel --start-address=0x4b3250 --stop-address=0x4b3330 Asgard.exe
objdump -d -M intel --start-address=0x4b33a0 --stop-address=0x4b3620 Asgard.exe
objdump -d -M intel --start-address=0x4b4920 --stop-address=0x4b497f Asgard.exe
objdump -d -M intel --start-address=0x4b4bb0 --stop-address=0x4b4d81 Asgard.exe
```

本回合已於原始檔執行：**原版 EXE SHA 符合，26 個 native VA byte-patterns PASS；3 個 MAP SHA 相符且 494/494 MAP 解析 PASS；合成 MAP/DAT 及 bounds/flags/tail 測試 PASS**。所有結構化查詢工具**不會輸出原始地圖資料**，只輸出每庫聚合計數；完整原件不入 Git。

|Evidence ID|證據|
|---|---|
|A015-E22|原生 MAP 10B-to-17B tile / header / block / tail `0x4B33A0..0x4B35F6`|
|A015-E23|原生 `0x4B2C80` 對 tile `x+y*w` 尋址；`0x4B4920` 驗證 x/y bounds|
|A015-E24|像素 extent `width*48/height*32`，`0x4B4A3B/0x4B4A73`；轉 tile 是 inferred candidate|
|A015-E25|bit0 讀/寫 `0x4B2CA0/0x4D120B`，bit4 線段 `0x4B4BB0`；不可混成 walking|
|A015-E26|4-byte auxiliary grid `0x4B3250/0x4B2D00`，與 tile flag 分離|
|A015-E27|SHA 鎖定 494 原件 MAP／7.7M tile 聚合 + Born(31,29) flags 0/1/17 分布|
|A015-E28|26 PE 指令模式 + 合成 codec/tile bounds/負向測試；CT-069/CT-070 分開|

## 7. 結案／真正缺口

本輪**完整交付 MAP 原始布局、Client tile 尋址、可檢查的 tile bounds、旗標/輔助格/線段用途分離與 494 原件統計**。但尚無證據將某個原始 flag 或 auxiliary grid 直接定成玩家可走地板，亦無同版 Native Client movement／rollback trace；`player_walkable` 保留 unknown。原服特定 map_id／spawn 策略並非 Client 靜態研究可自動取得。A-015 原有 resource-format/provenance 交付仍 ready；本次新增 collision mapping 的 **native-passability = partial**，`native_client_validation=not-run`，`implementation_ready=false`（指全地圖可通行白名單）。

**缺少檔案：沒有新增必需檔案**。已有 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat`。真正要解開合法站立／走路邊界，需要同版 Client 的原生成功移動/撞牆/伺服器校正的去識別封包及畫面 trace，或進一步追 `MapPane` 角色移動前置碰撞 call chain；不是額外大批圖像檔。
