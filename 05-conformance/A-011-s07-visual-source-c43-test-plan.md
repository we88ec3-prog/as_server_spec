# CT-116：A-011 原版 S07 圖片來源到 MonsterImageLib、C43 三模式驗收

本驗收僅是**原版 Asgard.exe 靜態原始指令 + synthetic decoded-body**。Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，既有 Monster archive 的 YPF/DOI、原生 NPC GUI、原服 NPC/怪物 AI／掉落不是此 gate 可宣稱已完成的內容。

## Offline original Client binary

```bash
python task_a/roy2/a011_s07_native_visual_probe.py Asgard.exe
```

確認 **43 VA instruction anchors**：
1. S07 native reader `0x57E451→0x57E456`：共同第五欄 BEu16 存解析行 `row+0x0C`；與變長 tail `row+0x222` u16 分開。
2. World handler `0x4F1A7F` 讀第五欄，`0x4F1A83` 寫入 20B descriptor；S07 kind1/2/4 在 `0x4F1AEB/0x4F1BC7/0x4F1C31` 用 descriptor ptr 建構 MonsterObject。
3. `0x4D7020..0x4D703E` ctor 複製 descriptor；`0x4D70A6` image factory `0x4D2340`；`0x4D235C` dereference descriptor first u16，`0x4D2361/0x4D236E` 呼叫 bank／slot index `0x4D7530/0x4D7560`：`image_id 0x4000+N → Monster(00..42).dat, library8000+N/10,slotN%10`（安全 guard `0x4000..0x41AD`，Server design）。
4. S07 tail `row+0x222` 的 variant_u16 在 constructor 分別作獨立參數，`0x4D7056` 轉 float、`0x4D7061` 存 object+0x27C；**不是 image ID**。
5. `0x4A2376..0x4A2558` 的同一 UI panel mode0/1/2，C43 type1/subtype `0x04/0x10/0x40`，共用 object ref `[pane+0x4C]`；另一 `0x479DEB` producer subtype04。**不是肯定 NPC click/merchant 入口**。
6. local MonsterObject motion `0x4D6BC0` 的 0..5 selector → base+`0x20/0x30/0x40` 是數字規則，**走/攻/死 語意與 YPF/DOI frame mapping 未證**。

## Synthetic CI (no original files committed)

```bash
python -m unittest discover -s task_a/roy2 -p 'test_a011_s07_visual_chain.py' -v
```

23 tests：S07 kind1/2/4 原生欄位投影、430 個 image IDs/43 個 bank 每個10 slots、first/last、object_ref vs variant_u16 不混用、其他11 kind 不擅自說 MonsterObject、未註冊 namespace 只回 unresolved、截斷/多餘 byte/非法 kind/count 拒絕，以及 C43 UI panel mode0/1/2 的 BEu32 ref/subtypes、非法 mode/ID 拒絕。

**實際例子**：S07 第五 u16 `0x402A`、kind1/2/4 => Monster04.dat slot2 library8004。另 S07 tail variant_u16 若 `0x41AD` **不應**使外觀變成 Monster42.dat slot9。這些數字**是合成 fixture**，不能說原版 Monster ID 或官方 NPC 物種已有名稱。

## Native Client CT-083 / 依賴（still not-run）

要完成真實 YPF/DOI 動畫與 NPC 對話：
- 真正 `Monster00.dat`、`World00.dat` 或其他同版樣本（這回合本地沒有），由 0x4000 bank/slot 綁到 archive 成員/YPF group/pivot/direction/event；**單一 MonsterNN archive 有幾個 YPF member 不等於 MonsterImageLib 固定 10 slots**。
- 兩個原版 Client 對相同場景物件 S07 spawn/走/動作/死/消失，點擊時記 C43/C39/S34/S3C/S44/C6C 具體時序及 UI；原服 spawn/掉落/AI/任務旗標需獨立配置或實際 Server source。沒有資料不得把 C43 type1/04 當所有 NPC click，也不得將 Born(31,29) 當出生。
- Scene object_ref u32 授權需同 map/AOI/epoch/generation/target type；圖片 archive id、角色 template id、u32 object_ref 應分層。

本次可標 **CT-116 static original source + synthetic PASS**，但 **CT-083 original native GUI/render/animation and Server AI/drop not-run**。完整 [A-011 新增報告](../task_a/roy2/A-011-native-s07-visual-id-c43-20261101.md)。
