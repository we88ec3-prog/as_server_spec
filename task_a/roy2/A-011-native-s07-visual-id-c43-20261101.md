# A-011／roy2 — S07 原始圖片欄位→MonsterImageLib 與 C43 三模式實證（2026-11-01）

**固定原件**：`Asgard.exe` PE32/i386 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；未修改主程式，不上傳 binary。既有 A-011 [原始資源庫／MonsterObject／舊 C43 證據](A-011-analysis.md)、[A-004 物件可見性](../../03-analysis-requests/A-004-roy1-world-visibility.md)、[A-024 14 種 S07 格式](A-024-analysis.md) 都繼續有效。本次是 **可重現的 BIN-first 原始 PE 呼叫鏈補證**，非 Client GUI/TCP 原始 Server capture。

## 1. 關鍵補完：哪個 S07 欄位真正決定 Monster sprite？

先前 A-011 知道 `MonsterImageLib` 能把 `client_image_id 0x4000+N` 轉成 `Monster(00..42).dat` library+slot，但沒有證明 S07 哪個 u16 最後送到這個算法。**本次從 S07 reader 一路追到 0x4D7530/0x4D7560，已解開這個 Client 靜態欄位對應。**

|順序|原始 native 位置|直接觀察|
|---|---|---|
|① S07 reader|**`0x57E451→0x57E456`**|每行共通欄依序讀 BEu16 x、BEu16 y、u8 kind、BEu32 object_ref，**第五欄 BEu16** 寫在解析後行 struct `[row+0x0C]`。行 stride `0x228`、body 中第一筆第五欄自 offset **11** 開始；每筆 record 不是固定 wire 0x228 bytes。|
|② S07 kind1/2/4 共用進入前|**`0x4F1A7F..0x4F1A83`**|讀 `word [esi+0x0C]`，寫到 stack 上 **20-byte 視覺 descriptor 的第一個 u16**。不是拿 `[esi+0x222]` 做圖片索引。|
|③ 三個 new MonsterObject|**`0x4F1AEB` kind1、`0x4F1BC7` kind2、`0x4F1C31` kind4**|三個分支都把同一 stack descriptor pointer 傳給 `MonsterObject` ctor **`0x4D6FA0`**，但 ctor options 不同，不可因此將 1/2/4 強行命名 NPC/monster/pet。|
|④ MonsterObject ctor|**`0x4D6FF9..0x4D703E`**|取 descriptor pointer，複製其 **前 20 bytes 到 object+0x28C**；`0x4D70A6` 呼叫 image object factory `0x4D2340`，也傳入該 descriptor。|
|⑤ Image object factory|**`0x4D2356..0x4D236E`**|factory 取 descriptor pointer，**`0x4D235C mov ax,word [esi]`**，兩次讀 descriptor 第一個 u16，依序 call `0x4D7530`、`0x4D7560` 取得 Monster Library ID 與 local slot。|
|⑥ MonsterImageLib|**`0x4D7530/0x4D7560`**|減 `0x4000`，`0x66666667` 魔數實現 10 的 quotient/remainder；library offset `0x1F40`。註冊表對應 `8000..8042→Monster00..42.dat`。|

因此，對已證會建 MonsterObject 的 S07 kind **1／2／4**，只在 **Client 已註冊的安全 image namespace `0x4000..0x41AD`**：

```text
S07(row).field_c (body 第五欄 BEu16) = native [row+0x0C]
delta       = field_c - 0x4000
library_id  = 8000 + floor(delta/10)
archive     = Monster%02d.dat % floor(delta/10)
image_slot  = delta % 10
```

|S07 第五欄 image_id|archive|slot|library|
|---|---|---:|---:|
|`0x4000`|`Monster00.dat`|0|8000|
|`0x4009`|`Monster00.dat`|9|8000|
|`0x400A`|`Monster01.dat`|0|8001|
|`0x402A`|`Monster04.dat`|2|8004|
|`0x41AD`|`Monster42.dat`|9|8042|

### 另一個 u16 不是 image_id

S07 kind1/2/4 的變長 tail **`variant_u16`** 來自 `0x57E4B1..0x57E4B8`，存在 `row+0x222`。三個 handler 呼叫分別在 `0x4F1AC3`、`0x4F1BA0`、`0x4F1C09` 將此欄推入 **MonsterObject 第九參數**。Ctor `0x4D703E` 讀出，`0x4D7056` 以 x87 `fild` 轉成 float，`0x4D7061` 存 `MonsterObject+0x27C`。**其確切遊戲語意未知**（可能與繪製尺寸、屬性或其他變數有關，但不能猜）；從程式可證 **不應把 variant_u16 當 Monster sprite image_id**。S07 的 `BEu32 object_ref` 也不是 image ID／資料包 archive index。

同樣重要：**這個完成的是欄位→圖片庫查找算法，還不是實際 Monster 圖像／YPF frame 動畫完成**。沒有 `Monster00.dat` 等原件與完整 YPF/DOI motion-to-frame 實證，不能回答「某個 NPC 具體穿什麼衣服、長什麼樣子、走/攻擊/死亡如何播放」。

## 2. 第二個新結果：同一 C43 UI 物件有三個已證 subtype

先前 A-011 只找到 UI sender 的 subtype `0x04`；此次逐行追到 **`0x4A2376..0x4A2558`** 三個 mode branch，全部建 `CObjectInfoRequestPacket` opcode **0x43**，設 `type=1`、`object_ref=[pane+0x4C]`，依 pane 本地 `[pane+0x48]` 模式切換 subtype：

|本地 pane mode|C43 subtype|原始 native sender|
|---:|---:|---|
|0|`0x04`|`0x4A23F8` ctor／`0x4A2409` type1／`0x4A2410` subtype04|
|1|`0x10`|`0x4A249B` ctor／`0x4A24AC` type1／`0x4A24B3` subtype10|
|2|`0x40`|`0x4A2537` ctor／`0x4A2548` type1／`0x4A254F` subtype40|

三條都在 **`0x4A2553`** 寫 packet object_ref、**`0x4A2558`** 排送 `0x5788A0`。另 `0x479D8D..0x479DEB` 另一個 UI producer 的 **type1/subtype04** 原件仍成立。

合成 decoded C2S body（非 frame，非原服 capture）：
```text
pane mode0, object_ref=0x12345678 : 01 12345678 04
pane mode1, object_ref=0x12345678 : 01 12345678 10
pane mode2, object_ref=0x12345678 : 01 12345678 40
```

**Server 注意**：不能把三個 subtype 直接命名 NPC 點擊／交談／交易，這裏只是 *UI info request producer* 已知三分支；具體 mouse hit-test → object target → 原服 S34/S3C/S44/NPCChatDialog 的單條端到端因果尚未追通。更不能在未驗證同場景/可見性/距離/connection_generation 的情況下，因收到 C43 就授權 NPC 接任務、商品交易或傷害。

## 3. Animator、NPC 與原服權威的剩餘界線

- 已證 `MonsterObject` local selector `0x4D6BC0` 的 mode0..5 對 internal base motion 加 `0x20/0x30/0x40`（重複一次），與初始化 `base+8`；**不能由數值推斷原版走路／攻擊／死亡的動畫語意**。S1A Motion 有 u32BE ref＋控制欄，但 native S1A→Monster local selector 的所有條件也未全部解析。
- `World00..23.dat` 註冊 library ID 7000..7023，與 Monster 的 `0x4000+index`、S07 object_ref 是**不同 ID namespace**；沒理由直接推 `World00.dat` 某個 member 就是新手招募員。
- 上輪 A-023 真正給出的 `Merchant.dat`、`nNewJoin01.dat` 已驗內容，知道學校對話會回 `STATE=ACCEPT/REFUSE`；但**NPC EntityId/map/spawn→merchant root＋nNewJoin01 Script dependency 仍然沒有原服證據**。Born 引導的 `(31,29)` 不是出生點或已證 NPC 位置。
- `S07` 表示新物件、`S0C/S64` 移動、`S11` 方向、`S1A` motion、`S5F` 死亡、`S0E` 移除應獨立處理。掉落/AI/原版 spawn/quest/獎勵都是 **Server-owned，不能從 Sprite ID 推回原服規則**。

## 4. 交付規格與測試

**可交 DEV** 的新 Client I/O：
- 收到 `S07` kind1/2/4，從 common `field_c:u16BE` 選 MonsterObject image；若在 **已知註冊 pool** 範圍內，依上列算法 resolve `ContentAssetRef(MonsterNN.dat,library,slot)`；image id 出界時視作其他/未驗 image namespace，**不得假造 archive 或自動剔除原版認得的其他 namespace**。
- `variant_u16`、`scene_object_ref` 分欄保存；不要互用，也不要把 `scene_object_ref` 當怪物模板／永久 ID。
- C43 bounded UI panel type1/subtype04,10,40 可做 codec/解析、authorization guard；**不等於原版 NPC 對話角色權限已確認**。
- Original scripted NPC 的 `Merchant+nNewJoin` 和 `Born/PaperDialog` 必須按已核對 S44/C6C 分別執行，不從 Monster picture 對應任務。

**新原件工具**：`task_a/roy2/a011_s07_native_visual_probe.py`，驗證原始 EXE 的 **43 個 VA pattern**（其中 35 屬 S07→MonsterImageLib／motion、8 屬 C43 UI），並鎖定 SHA；`task_a/roy2/a011_s07_visual_chain.py` 將 native S07 行欄位傳到 ResourceRef；`task_a/roy2/test_a011_s07_visual_chain.py` **23 項 synthetic tests** 覆蓋 430 圖像ID、kind1/2/4、variant/object-ref 不可混淆、字串/長度/越界/其他 kind 與 C43 三模式。原始 Client GUI 不在 CI，沒有將任何版權素材提交。

```sh
python task_a/roy2/a011_s07_native_visual_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a011_s07_visual_chain.py' -v
objdump -d -Mintel --start-address=0x57e421 --stop-address=0x57e4c9 Asgard.exe
objdump -d -Mintel --start-address=0x4f1a7f --stop-address=0x4f1c45 Asgard.exe
objdump -d -Mintel --start-address=0x4d6fa0 --stop-address=0x4d70b0 Asgard.exe
objdump -d -Mintel --start-address=0x4d2340 --stop-address=0x4d23e7 Asgard.exe
objdump -d -Mintel --start-address=0x4a2376 --stop-address=0x4a255d Asgard.exe
```

## 5. 成果與確切缺少檔案

`A-011 status=integrated`、`handoff_status=partial`。**本次新解決**：S07 **真正圖像欄位**與原始 bank/slot、三種 C43 info UI mode；兩者有完整的 static call chain 和可重跑的 CI synthetic codec。**仍未完成**：原版 Monster 實體 YPF/DOI 動畫分組、實際 NPC/怪物種類→asset 對照、真正 NPC 點擊→對話 GUI 的回覆鏈、Monster AI/掉落/Spawn 的原服規則、原版 Client GUI E2E。

**本輪本地實際沒有的具名原件**：
- 至少 **`Monster00.dat`**（任一同版 `MonsterNN.dat` 樣本也有價值），用來驗 library=8000 + slot 實際是檔內哪個 YPF、frame/motion/direction 映射；若要完整怪物庫需要 `Monster00.dat`～`Monster42.dat`。
- 至少 **`World00.dat`**（同版任一 `WorldNN.dat`），用來追 World 庫／靜態物件的獨立載入鏈；若要全庫需要 `World00.dat`～`World23.dat`。
- 不需重傳 `Asgard.exe`、`Born.dat`、`Basic.dat`、`Map0/1/2.dat`、`PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat`、`Merchant.dat`，它們本次已具備或在既有 A-023 已驗。

原服 NPC template/spawn/drop 表的**實際檔名仍未知**，不能臆造。要把 NPC 點擊/對話與掉落變成原版可實機驗收，需要**去敏真 Client 封包時序（S07→點擊→C43/C39→S34/S44/C6C）及配套原服 NPC/Script 設定**。`CT-116` 是新增 *offline static + synthetic*，`CT-083` native render/click **not-run**；不因本次補證改成 E2E PASS。
