# A-015 MAP 座標／碰撞驗收：CT-069／CT-070

Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。只接受指定版本 Map0/1/2；全部原件僅在本機驗證，不進共用 Git。說明 [A-015 詳細報告](../task_a/roy2/A-015-map-coordinate-collision.md)。

## CT-069：MAP 解析、欄位級映射及離線驗證

```sh
python task_a/roy2/a015_map_native_probe.py Asgard.exe
python task_a/roy2/a015_map_coordinate.py --verify-original-sha Map0.dat Map1.dat Map2.dat
python -m unittest discover -s task_a/roy2 -p 'test_a015_map_coordinate.py' -v
```

- 本回合原件 SHA 對齊，26 native VA byte-patterns PASS，三庫 **494/494 MAP** 及 **7,701,805 tile** PASS。
- 必須驗證 DAT index/EOF，MAP header 3×LEu16、u8 width/height、block=ceil(w/2)*ceil(h/4)*2、10B raw tile、7/8/16B tails。
- 必須驗證 **x+y*width** 並分清 10B raw tile 與 **17B client memory tile**；原始 32bit flags bit0/bit4/bit9 需保留完整寬度。
- 對 `0,0`、`width-1,height-1`、負值、剛好等於 width/height、bool、截斷及跨 MAP 越界測試，非法一律 fail closed。
- 48×32 畫面邊界只作候選 pixel-to-tile 換算，**不是 Native 玩家角色腳底/可走路保證**。8B/16B tail 候選 pixel offsets 必須有 XREF 才能命名。
- (31,29) 的 477 個 in-bounds MAP 分別出現 flags 0:242、1:109、17:126；禁止把 in-bounds 等同通行或出生。
- test report 應記為 `observed-static-PE-and-resource + synthetic`，不標 Native Client GUI PASS。

## CT-070：原版 Client 撞牆、合法站立／可用座標實機驗收（planned/not-run）

1. 選擇具體原版 map_id 與版本綁定，錄得 Client 讀取該 `%05d.map` 的資源庫、C35 header/checksum。Map0..2 有 494 entry，不代表任意 map ID 都在原版 Server 可進。
2. 記錄原生地圖可視範圍與 pixel(48×32)對應角色 tile 的實際腳底座標、碰撞尺寸及 tile 點擊位置，辨認 GUI 與 wire 座標的單位。
3. 在**同一 map** 各選取 `flags=0/1/16/17/512` 且存在的測試格，從相鄰合法位置嘗試移動；記錄 C33 方向/序號、S0B 是否校正、Client 是否退回，避免把 0x10 line-test 和可行走 mask 一律等同。
4. 對角移動、地圖邊界、地圖轉場、物件動態阻擋、死亡/重登、重複/亂序封包，同時追 MAP 4B secondary grid 及 bit0 本地 set/clear 的 input 時機。
5. 需要拿到真正的原生 Client move candidate→碰撞函式→是否發 C33／如何處理 S0B 的函式 call chain。重現到單格級 sample，若不同類角色受不同阻擋，需顯示 role/occupancy 分層。
6. Server authority **designed**：未驗出 passability 的 map/spawn 不允許自動轉成全部可站立；先採人工明確驗收點、對非法座標拒絕，不猜原版碰撞策略。
7. 最後把觀察得到的碰撞定義、Client 座標單位與 replay trace 放入增量證據，更新 `CT-070` 狀態；沒有原生資料前保持 not-run。

**狀態**：CT-069 的離線原件/合成階段可驗證；CT-070 原生玩家走路/撞牆 **not-run**。這不阻礙已證 MAP 解析研究交付，但不允許宣稱原版全部可用座標已解出。
