# A-022／roy2：494 張原生 MAP 的 C35 全量盤點與入圖交接（2026-11-01）

- 工作分支：`task_a/roy2`。只補 A-022 Client I/O 與資源靜態研究，不修改 Client/Server，不推送遊戲原始素材。
- 原件 `Asgard.exe`：SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，PE32 x86。
- `Map0.dat`：SHA256 `dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761`（288）；`Map1.dat`：`8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b`（184）；`Map2.dat`：`5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb`（22）。
- **證據分層**：EXE VA 為 observed-static；原件 494 張 map 的離線重算為 observed-resource/static-reconstruction；Server 保護策略是 designed；原版 Client 實際 World TCP/GUI 是 **not-run**。
- 主線既有 [A-022 BIN](../../03-analysis-requests/A-022-roy1-bin-analysis.md) 與 [地圖解析勘誤](../../03-analysis-requests/A-022-roy1-map-geometry-collision.md)；本檔為 roy2 增量驗證，不覆蓋既有結論或 CT 編號。

## 一、MAP 原始資料與 C35 重算

DAT：file+0 為 LE u32 slot_count（含最後一個 EOF sentinel）；索引從 file+4 開始，每個 36B＝LEu32 start + filename[32]。MAP：三個 LEu16 header、u8 width、u8 height、block 為 ceil(w/2)×ceil(h/4)×2B，tile 為 w×h×10B，末尾三段各 LEu32 count + count×7/8/16B。禁止採用舊版錯誤 index 起點 `8+36*n`。

|原始 EXE 位址（VA）|實際觀察|
|---|---|
|`0x4B33A0`、`0x4B2C80`|從本地 `%05d.map` 載入；tile 下標 `x+y*width`；磁碟 10B/tile，本地記憶體 17B/tile|
|`0x4B4850`|C35 第一個 u16 取原始 MAP header 位移 +4，**不是 map_ref**|
|`0x4B4890 → 0x4B3650 → 0x4B2EC0`|第二個 u16 對解析後 MAP 資料做結構化 checksum，非原始整檔 CRC|
|`0x43E0A0`、`0x664720`|原生 16-bit CRC byte updater 與 256 項表，初值 0；表開頭 0、0x1021、0x2042|
|`0x573490`|C35 wire body 是兩個 BEu16，共 4B|
|`0x57FF30`|S15 讀 3×BEu16 + 2×u8 + string8，只有第一個 u16 存為 map_ref|
|`0x4F2300`|S14 control1 生成 C35；control2 在物件存在時做 loading callback；control3 進 3000ms 的異常/清理支線|
|`0x589990`|S04 解析連續 4×BEu16，不能從 parser 得到固定官方出生座標|

native structured feed：初值 0，依序 block 原始 bytes、tile 原始 bytes；7B tail：byte0 bool normalize、LEu16、兩個 LEi16 各 sign-extend 為 LEi32＝每筆 11B；8B tail 四個 LEu16；16B tail 使用 +0 LEu16、+2 **整個 LEu16** 是否非零、+3 byte 是否非零、+4 byte、+8..+11 四 bytes、+12/+14 LEu16＝13B，跳過 +5..+7。MAP header 與三段 tail count 不餵入。完整演算法及 SHA-locked 494 份 metadata-only probe 見 `a022_map_c35_catalog.py`。

### 全量結果（494/494 原件 PASS）

|統計|結果|
|---|---:|
|全部合法 MAP 成員|494|
|不同 payload SHA256|330|
|不同 C35 pair|330|
|重複 pair 群組|33|
|處於重複群組的 map_ref 數|197|
|額外相同內容別名（197−33）|164|
|**不同 payload 卻相同 C35 的群組**|**0（僅此 corpus）**|

|S15 map_ref|真實成員|寬×高（tile）|預期 C35 decoded body hex|
|---:|---|---:|---|
|0|Map0.dat / 00000.map|20×20|`000063A9`|
|6|Map0.dat / 00006.map|60×60|`00040F90`|
|10000|Map1.dat / 10000.map|60×60|`00040F90`|
|18001|Map1.dat / 18001.map|150×150|`0012F892`|
|20001|Map2.dat / 20001.map|60×60|`0016E9B9`|

**map_ref=6 與 10000 的 MAP payload SHA 完全一樣、C35 四 bytes 相同，但是兩個不同的地圖 ID。** 本 corpus 沒有非相同 payload 的 C35 碰撞，**不代表 checksum 在所有輸入上不可能碰撞**。C35 既非 map_ref 也不含 session/epoch，不能當成 map identity 或權限憑據。結果與 [A-032 的五個靜態例子](../roy3/A-032-roy3-native-map-c35.md) 交叉一致。

## 二、Client I/O：已證順序與未證部分

|Trigger|Client C→S|Server S→C|Client effect / 限制|
|---|---|---|---|
|S03 轉 World 的已證分支|C10 raw token；region3 緊接送 C25 `3×string8`|S03 addr/port/token|[A-031](A-031-analysis.md) 已核實 C25 是 `CBillingInfoPacket`，**不是** map_ref、WorldEntryMetadata 或權限驗證。非 region3 沒有一般必送 C25 的證據|
|Server 進入選定地圖的載入流程|此步沒有已證的額外 C2S|S15：`map_ref:u16BE, other:u16BE, other:u16BE, flags:u8, extra:u8, title:string8`|Client parser 可讀；真正 S15 與 S14 的時序/原生 GUI 尚未擷取|
|Client 接 S14(1)，本地 MapData 可讀|C35：`header_word:BEu16, checksum:BEu16`|S14 `01`|`0x4F23CB..0x4F2428` 取兩個本地計算值後 enqueue C35。離線估值可能受 runtime 更新影響，需 CT 擷取|
|Client 接 S14(2)|此分支不直接 C35|S14 `02`|有 `0x91FBE0` 物件才 callback；不是 Server 收到成功入圖 ACK|
|Client 接 S14(3)|此分支不直接 C35|S14 `03`|3000ms 與特殊清理/異常路徑；不能當正常成功|
|Client 收到角色位置|玩家實際移動 C33/C11 尚需抓封包|S04 四個 BEu16，後續 S33|render、viewport、朝向、S33 觸發/順序仍有 unknown|
|資料缺失、CRC 不符、舊 epoch、超時/斷線|原版 Client 對失敗後續是否重送 unknown|原服錯誤回覆 unknown|Server 的拒絕/恢復策略是 designed，不能標原生觀察|

**交 DEV 的相容子集**：已認證的 World session 選 map_ref、版號/原件 SHA 與預期 C35 pair；建立單一 pending loading generation；只在同流程期待 C35 並檢查完整 4 bytes。若同一連線上舊/新流程的 pair 相同，僅憑 C35 **無法分辨**，需按會話序列避免疊加，無法判別則 fail-closed。C35 通過不等於 S04/S33 已正確渲染，更不等於 tutorial 完成。

**地圖碰撞限制**：tile `0≤x<w, 0≤y<h` 僅代表可索引。原始 flags bit0 可 runtime set/clear，bit4 被線段測試讀取，另有 u32 per-cell grid。`flags_u32=0` 不足以宣告合法出生、可行走；48×32 僅是 Client 畫面幾何候選，不是已證 S04 玩家腳底網路單位。原服教程 map、spawn、facing 不是純 EXE/MAP parser 能推導的 Server 決策。

## 三、再現、驗收與缺件

```sh
python task_a/roy2/a022_map_c35_catalog.py --exe Asgard.exe --map-dir .
python task_a/roy2/a022_map_c35_catalog.py --exe Asgard.exe --map-dir . --json /private/a022-494-metadata.json
python -m unittest discover -s task_a/roy2 -p 'test_a022_map_c35_catalog.py' -v
ASGARD_ASSETS_DIR=/path/to/original/assets python -m unittest discover -s task_a/roy2 -p 'test_a022_map_c35_catalog.py' -v
```

`--json` 才輸出本地逐圖 manifest（map_ref、寬高、header/checksum、payload SHA、三段 tail count），不匯出遊戲地圖原始 bytes。所有原始資產 hash 強制鎖定，拒絕跨版本混算。合成負例：CRC primitive、16B canonical skip、壞 MAP、越界/截斷 DAT 及庫 ID 錯置。本次在原件實跑 **5/5 unittest PASS**，含全量 494 census；這不是 Native Client CT。

- **完成（本次 A-022 roy2）**：全部 494 MAP 的 version-locked checksum 再計算、map_ref/pair 一對多風險、可重現工具/測試、C10/C25→S15/S14→C35→S04 的證據邊界。
- **還需 CT-108/109、CT-090/091**：不修改原版 Client 擷取已遮罩 C10 / region3 C25 / S15 / S14(1) / C35 / S04 / S33 / S14(2) / C33 / S0B，確認顯示、碰撞/回滾、有效出生座標、重連和 mismatch 分支。不能用假 Server 或 synthetic fixture 當原服封包證明。
- **無新增缺失的具名 DAT**：`Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat` 已有。尚缺的是原始 Client **World TCP 去敏收發 trace 與 GUI 操作記錄**，並非再次要求提供這些檔案。
- **狀態**：A-022 主線 `integrated` 保留；roy2 靜態/資源子集已可 DEV handoff，`handoff_status=partial`、`native_client_validation=not-run`、`tutorial_content_ready=false`。不宣稱已完成官方新手教學進場或走路 E2E。
