# A-019 / roy1 — 原地圖音樂配置與 S19 Client 播放路徑（BIN-first）

- 日期：2026-10-31；工作 branch：既有 `task_a/roy1`，未建立 branch、未合併 main。
- 樣本 `Asgard.exe`，PE32 x86，ImageBase 0x400000，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
- 附原始 `Map0.dat`、`Map1.dat`、`Map2.dat`，精確 hash、index stats 見 `02-server-planning/map-music-evidence.json`，不提交原始遊戲資產。
- Evidence `ev_a019_20261031_music_s19_map_index_bin_static`；R-022；SCN-006；CT-005/006、CT-060～062。
- **完成狀態**：A-019 `integrated / handoff_status=partial / native_client_validation=not-run`。這代表有證據的 Client 音樂播放/停止、地圖 archive index 審查及正式 Server 設計已交付，**不是原服 map→track 音樂配置已還原**；`native_map_track_mapping_ready=false`。

## 一、原版 S19 不只是固定四 bytes

**原始 x86** `SPlaySoundPacket` ctor `0x584A30` at `0x584A49 push 0x19`；parser `0x584AE0`；vtable `0x615238`。原 parser **先讀一個 u8**，在 `0x584AE8..0x584AEF` 正規化為 `(kind == 1)`，若真再讀一個 `u8 repeat`，最後都讀 **`u16 BE track_or_sound_id`**。不是所有 `kind` 都帶 repeat。

| Body (decoded, without opcode/frame) |原生解析與 handler|證據強度|
|---|---|---|
|`01 repeat track_hi track_lo`|kind=1、repeat u8、track u16 BE；`0x4F25D0` → `0x53CDC0` music branch|observed-static|
|`other_kind track_hi track_lo`|kind!=1，不讀 repeat；handler track!=0 → `0x53D250` 其他音效分支|observed-static；其他 kind 的精確業務枚舉 unknown|
|`01 00 00 12`|播放音樂 track18 的 **已存在本機合成 profile fixture**，不是該地圖的官方曲目|synthetic|
|`01 00 00 00`|music branch track0 走清除/停止音樂路徑（`0x53CED1..`），不是用 mp3 檔案0|observed-static + local-fixture；原服切圖是否送 stop unknown|

最短獨立 xrefs：

| Native VA |原件可觀察行為|
|---|---|
|`0x584A49`|`push 0x19` → Server→Client packet type|
|`0x584AE3`|`call 0x45ADB0` read u8 kind|
|`0x584AE8`|`dec al/neg al/sbb/inc`，僅 kind1 抽成 bool true|
|`0x584AF6`|kind1 才 read u8 repeat|
|`0x584B00`|`call 0x45ADE0` read u16BE track|
|`0x4F25D4..0x4F25EF`|handler 在 full packet +0x24 bool 檢查後把 +0x28 track、+0x2c repeat 交 `0x53CDC0`|
|`0x4F25F8..0x4F260B`|kind!=1 且 sound_id!=0，調用獨立 `0x53D250`|
|`0x53CE4D / 0x53CF01`|music 檔名格式指標指向 UTF-16LE `%05d.mp3` (VA `0x60EE20`)|
|`0x60EE3A`|原版字串含 `Music\\%s` 資源相對路徑模板|
|`0x4B3424`|Map loader 使用另外的 `%05d.map` 模板，不是 music track|
 
**注意指標偏移**：parser ECX 是 packet +0xC 的 reader subobject。parser 寫的 `+0x18/+0x1C/+0x20` 與 callback 用完整 packet 的 `+0x24/+0x28/+0x2C` 一致；**不能把二者當兩份不同欄位**。

## 二、Map0/1/2.dat 真正查到的內容及證據界線

從實際提供的三個原件各自解釋其**可辨識的目錄索引**：

- File offset0：LE u32 index entry count；offset4：LE u32 值等於 `4+36*count`；索引由 file offset8 起、每 record 36 bytes。這是原件統計格式觀察，**不是**已把所有 payload 的欄位語意/密碼/打包方式解析完。
- 名稱 `[0-9]{5}.map\\0` 可辨識的 entry：Map0 共288個（header count289）、Map1 共184個（count185）、Map2 共22個（count23）。合計 **494 個實際可辨識 `*.map` 名稱**；每份有 1 個不符合此 filename pattern 的 slot，Map2 最後 slot 含非零 bytes，不應一律認定它是空檔或是 audio entry。
- **這三個目錄索引均沒有 `Music` 或 `.mp3` 檔名**。這是**限 index 的陰性證據**：不是聲稱所有 MAP 二進位 payload、其他 Script 檔或原始 Server 設定完全不含 track ID。
- 原生 MapData loader `0x4B33A0` 依 map_id 組 `%05d.map`，讀 MAP header、tile/records（A-022 已有分段資訊），沒有在本次已追入圖/音訊鏈上找到一個能被核對的 `map_ref→music_track` 檔案欄位或 lookup。地圖檔存在不代表提供地圖的背景音樂設定。
- 即使從 archive index 可找 map00000/10000/20000，也**不可推論** `00001.map→00001.mp3`、`map_id→track_id` 或 `出生地圖→track1`；也不可把 `S15.map_ref` / `C35.first_word` 誤當音樂曲目。

|資料來源|能證什麼|不能證什麼|
|---|---|---|
|Client `S19` parser/handler|Server 可用 kind1 指定 u16 track，Client依編號生成 MP3 名稱，track0 清除|**Server 如何根據地圖選歌**|
|三個 Map archive 目錄|494 個 MAP 檔名；目錄無 `Music/*.mp3` 或對照檔名|所有 map payload 與其他資源內均無隱含曲目資料|
|SCN-006 原有人工驗收|本機某些 S19 profile 播放/停止可聽見|原服每張地圖曲目及相同版本內容配對|
|A-022 S15/S14/C35|通用換圖/結構化 MAP CRC|是否在原服每次換圖都發 S19 及其時序|

## 三、Server 開發規格（DESIGNED，非原始 Server 政策）

**唯一可信 map→track 資料入口**：`MapMusicCatalog(profile, client_sha, content_revision, map_ref, track_u16, repeat_u8, source_evidence_id, origin_verified)`； `origin_verified=true` **只能由與原始 Server/map content/packet trace 對應的可稽核來源設定**，不能因 local template 或 map 數字相同就設 true。現在正式 native catalog **0 筆已證 mapping**；JSON 明確保留 `map_track_bindings=[]`。

- `MusicCue` 在 World `InWorld/WorldLoading` 狀態下只接受 Server domain 的合法地圖與 session generation/content revision，決定是否播放；Client 不決定 authoritative map id。
- local-fixture 可指定 `map→track1` 或 `track18` 作測試，但須 `origin=local-fixture` 且不能出現在 `native_verified` profile；正式 Server unknown 時 **不推送猜測的曲目**。若遊戲設計要求離圖即停，可顯式選擇 `S19(kind1,0,0)` 作 **designed fallback**，不得稱官方切圖一定停音樂。
- 換圖（S15→S14(1)→C35→S04/S14(2)）可以設計在安全 World loading 完成後觸發音樂；**原服 S19 相對時序未知**。同一 map generation/epoch 只觸發一次 cue；stale World generation/epoch 禁止晚到播放覆蓋新圖，與 A-016 C35 無 epoch 需 fence 的限制相符。
- 音量/靜音及 MP3 不存在時由原版 Client/音效引擎處理；Server 不可因玩家聽不到聲音而判定 map loading 失敗。不能把 `repeat`、`kind!=1` 曲目數字解釋為原服的所有音效枚舉。

## 四、離線驗證／CT 與本次缺口

可重現原件 signature **11/11**、3 個 Map archive count/filename/header/hash check、S19 mode1/non1 的合成 codec，以及帶來源 gate 的 map cue policy，**共10/10 Python unittest pass**（`tools/a019_music_map_probe.py`）。這些 **不是**真 Client 任意 map 切圖後收到原服音樂封包的實機證據。

- `CT-005/006` 延續 existing `01000012`、`01000000` 合成 fixtures，不能升級成官方 map tracks。
- `CT-060` native S19 kind1/non1 分支、track u16BE、repeat 欄位存在條件、停止／截斷／unknown kind fail-closed；原 Client 尚未完整實測。
- `CT-061` 三份 Map archive 的版本身份、目錄 name→map 可解析性與對照來源確證：**無官方 map track 記錄時預期值為 UNKNOWN，不應自動填表**。
- `CT-062` designed World map transition：相同 epoch/idempotency、舊 generation、重連/換圖/音樂靜音/檔案不存在／local-fixture 明示 provenance。

**缺少具名音樂資源**：目前本機提供 Asgard.exe、Map0/1/2.dat、Born.dat，**沒有 `Music/00018.mp3`**（CT-005 track18 的合成播放目標；若希望實際播放 track18 可提供此檔），也未提供其他 `Music/*.mp3` 音訊檔。即使提供 `Music/00018.mp3`，只能驗證播放/解碼，**不足以證明哪張地圖應播放18**。取得原版 map→track 的充分來源是原服帶 map_id 的 S19 實際切圖 trace、原服地圖音樂設定/腳本表（確切檔名未知）、或可還原 map→track 欄位的同版資源及 cross-reference；不能捏造某個未證實存在的 `MapMusic.dat`。

```sh
sha256sum Asgard.exe Map0.dat Map1.dat Map2.dat
objdump -D -M intel --start-address=0x584a30 --stop-address=0x584b0d Asgard.exe
objdump -D -M intel --start-address=0x4f25d0 --stop-address=0x4f2618 Asgard.exe
objdump -D -M intel --start-address=0x53cdc0 --stop-address=0x53cf90 Asgard.exe
python3 tools/a019_music_map_probe.py
```
