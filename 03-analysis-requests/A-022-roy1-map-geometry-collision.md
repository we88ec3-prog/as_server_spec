# A-022 / roy1 追加 — 原始 MAP 位元組、格子／遮蔽旗標與幾何座標（2026-10-31）

**依據**：同版原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`、`Map0.dat` SHA256 `dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761`、`Map1.dat` `8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b`、`Map2.dat` `5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb`；原始碼/來源未提供，對 Client BIN 是 observed-static，對三個 MAP 是 observed-resource，Server 通行政策 designed。Evidence `ev_a022_20261031_map_archive_collision_resource`。原有 A-022 與 C35/CRC 結論仍有效。

## A. DAT 封包中的真正檔案邊界

原件 `Map*.dat` 起頭 `u32LE directory_count, u32LE directory_size`，其中 directory_size = `4 + 36*directory_count`。directory 位於 file offset8，record 固定36 byte，**前 32 byte 包含 NUL-terminated filename/未知資料，最後4 byte是這個 entry 的 MAP payload「結束 offset」**；第一筆 MAP 的 start 為 `8+36*count`，後續 start 等於上一筆 end。不能把這個4 byte 誤當檔案起點。三份各有 1 個末端非檔名的 sentinel/尾紀錄，不得當作正常 MAP。

- `Map0.dat` directory count289、288 個 `NNNNN.map`、其中 **287 個**符合完整 tile 格式；`00000.map` 為特殊未識別/空維度（非可遊玩 0×0地圖）。
- `Map1.dat` count185、184 個檔名、其中 **183 個**完整 tile 格式；`10000.map` 同為特殊未識別/空維度。
- `Map2.dat` count23、22 個檔名、其中 **21 個**完整 tile 格式；`20000.map` 同為特殊未識別/空維度。
- 合計 **494 個有檔名、491 個可完整解出 MAP 格子/附加段**，另 3 個特殊 `00000.map/10000.map/20000.map` 不可由本次格式宣稱碰撞或可出生；沒有推測其具體用途。三份原件同 Client 版本的**配對關係仍未由原服資源 Manifest 證明**。

### 每個可解 MAP payload

```text
file_off +0: u16LE header0
file_off +2: u16LE header1
file_off +4: u16LE header2    ← Client C35 第一個 u16BE 的本地來源
file_off +6: u8 width        ← tile 列寬
file_off +7: u8 height       ← tile 列高
file_off +8: u16LE blockGrid[ceil(width/2) * ceil(height/4)]
                ← 0x4B34A3..0x4B34DC 檢查計算
after blocks: byte tileRecord[height][width][10]
                ← Client 0x4B3520..0x4B356A 解為 17-byte local per tile
after tiles: u32LE count7; byte records7[count7][7]
             u32LE count8; byte records8[count8][8]
             u32LE count16; byte records16[count16][16]
end: exactly  payload_end from archive directory
```

**驗證實例**：
|檔名|w×h|header2|count7/8/16|尾端是否吻合|
|---|---:|---:|---|---|
|`00006.map`|60×60|4|7 / 0 / 0|是|
|`00007.map`|60×70|0|60 / 0 / 0|是|
|`10001.map`|200×200|9|678 / 0 / 0|是|
|`10055.map`|60×60|4|56 / 0 / 0|是|
|`20001.map`|60×60|22|4 / 14 / 0|是|
|`21001.map`|150×150|22|303 / 3 / 31|是|

**原生 x86 位址交叉驗證**：`0x4B33A0` MapData ctor；`0x4B3466..0x4B3497` 抽 header0/1/2/w/h；`0x4B34A3..0x4B34DC` half-row/quarter-column block indexing；`0x4B3520..0x4B356A` 寫 17-byte local tile，從原檔吃 10 bytes；`0x4B3575..0x4B35E0` 三組 7/8/16 附加紀錄。<br />`0x4B2C80` 取得 Client local tile `MapData+0x254 + 17*(y*width+x)`；`0x4B2C60` 取得前置 2-byte block grid 指標，使用另一個 block stride，不是標準 tile 寬。此處 **原檔 `[tile+6]` 是 little-endian 4-byte flags 的第一 byte**，所以 `0x4B2C80` 返回本地 17-byte tile 後的 `+6` bit mask 與原檔 `tile+6` 保持一致。

## B. 碰撞／遮蔽與「可用座標」不能畫等號

- `0x4B4BB0..0x4B4D75` 逐格掃描連線／路徑上的 tile local flags **bit `0x10`**，命中便轉成阻擋分支；這是確定的 **Client 某條線段阻隔判斷**，不能直接把它命名成「角色走路不可通行」或「所有 NPC 應不能生成」。
- `0x4B2CA0..0x4B2CD6` 按 x,y 位置設定/清除 local 17-byte tile flags 的 **bit `0x01`**；它是能在運行時修改的旗標。修改者 `0x4BBF0E` 等需要與實際碰撞/動態物件細查，不能單靠位元名稱宣告永久可走。
- `0x4B2D00..0x4B2D5D` 使用另一個 **`MapData+0x258` 的 u32 grid** 判斷五格鄰近 cells 是否皆 0，於 `0x4D1189` 被掃描作物件／路徑分流。這組 grid 是 Client **初始化為 0 的本地 Runtime 資料**，不是 MAP raw 中的永久「可走 flag」。
- 幾何座標：MAP tile 合法索引為整數 **`0 <= x < width` 且 `0 <= y < height`**，`index=y*width+x`，`source_tile_offset=8+2*ceil(width/2)*ceil(height/4)+10*index`；**這只代表 Client 能尋址這一格**，不代表地面可走／可生怪／可作首次出生。非空地圖寬高皆 u8，不代表原 Server 可以容忍 255 以外任意座標；S04/network 位址仍為 u16BE，正式 bounds 應依 **resource** 判斷。
- `Born.dat` 提到 (31,29) 女性招募員，是對話導引 waypoint，**不是 verified tutorial spawn map 或該地圖 ID**。該座標在多張真 MAP 中都符合幾何邊界，例如 `00006.map` 的 `31,29`，但**不能據此認定這張就是教學地圖或該 NPC 在此產生**。

## C. C35 及 Server 安全合約（沿用 A-022）

`S15` 第一個 u16BE 是 map_ref；`C35` 是 2×u16BE（本地 MAP header2、由 `0x4B2EC0` 對 block、tile 與 record **結構化**計算的 checksum），**不帶 map_id、width/height 或 map_epoch**；此處已能從原 Map 直接提供 header2/格子尺寸，但**本次未獨立重建每張 MAP 的真實 C35 第二欄**。不能把 raw MAP CRC16、固定 0 或隨意接受 client C35 當 pass。C35/Client map 已載入也不代表原服 character 可站立點合法。

DESIGNED：`MapResource(archive_sha,map_ref,header0..2,width,height,blocks,tiles,record7/8/16,crc_status)` + `TileQuery(x,y)` 使用幾何 bounds；`CollisionPolicy` 必須先核對原服/Client 真正移動決策，區分 geometry、line-test bit0x10、runtime bit0x01、dynamic occupancy 與 Server authoritative movement。未知資料 fail closed、不將目前的 bit masks 充作官方可走區。伺服器不能把玩家送至特殊 0×0 的 map 或未驗證 map revision。

## D. 驗證、缺件與後續

本次原始三份 archives **491/491 可遊玩格式的檔案按 width/height/block/tile/7+8+16 各段精確吃完**；3 個特殊 `00000/10000/20000` 明列未知。附 `tools/a022_map_geometry_probe.py` 離線 original resource format/bounds/flags fixture。新增 CT-069（完整索引/尾端）、CT-070（線段旗標 vs 通行）、CT-071（C35 配對與 spawn/security）。A-022 原先通用載圖任務已 `integrated`，本次補全 resource 子集，但 `tutorial_content_ready=false`、`native_map_collision_full_ready=false`；CT-018 真 Client 新手首生未執行，A-005 原服移動與碰撞仍 open。

**缺件精確檔名**：地圖三個 DAT 原件已齊；尚缺原版**Server 的 Map spawn／collision 設定**（來源檔名未證）、原版玩家真實移動成功／阻擋 trace 與教學首次 S15/S04 封包；只靠 MAP 格子不能證明完整原服通行政策。若要算 native checksum 還需繼續照 `0x4B2EC0` 逐欄復現。
