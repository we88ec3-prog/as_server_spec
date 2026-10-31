# A-011 — NPC / Monster asset identity, interaction, animation handoff

源自 [BIN-first 原件研究](../03-analysis-requests/A-011-roy1-npc-monster-resources.md)，Client SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，Evidence `ev_a011_20261031_monster_bank_s07_c39_motion_static`。**Observed resource-registration/packet shape 與 Server designed mapping 分開。**

Client 資源：`Monster%02d.dat` UTF16VA0x5F1D3C，0x404371..0x4043B0 for index0x1F40..0x1F6A (43 filenames Monster00.dat..Monster42.dat)；`Basic.dat` resource registration 0x403FA4。已有 Monster00.dat / World00.dat 的5+5個 YPF member，但 Client ImageId→實際 member、Monster外觀動畫仍未證，因此未取得原版 monster template→asset/animation tables。不能從註冊 0x1F40 就宣稱 S07 appearance value 同數值。

原版 S07 count2、每個物件固定前綴 x/y:u16BE, kind:u8, wire_object_ref:u32BE, appearance/resource_candidate:u16BE；kind1/2/4 RGB/flags/string8 等 tail，kind3/13/14 有不同尾欄。0x4F17C0 根據 kind、16bit candidate 建立物件；0x4F198D 包含 `0x8000..0xBFFF` 特殊渲染分支；這和 `0x1F40..0x1F6A` 的 asset bank **不同命名空間**，不能硬轉。S1A Motion u32BE ref/u8/u16BE/u8，S11 direction、S0C/S64 move，S0E remove vs S5F death 各自獨立。C39 Merchant common u8+u32BE ref+u16BE（subtype1..9 tail），C0C PutRequest u32BE ref；不是原版萬用 NPC click 的證明。

**DESIGNED**：`ContentAssetRef(resource_bank_id,filename,content_sha)` ↔ `NpcMonsterTemplate(server_template_id,asset_ref?,motion_map?,interaction_kind?,drop_table?)` ↔ `WorldEntity(instance,wire_ref,position)`。同 World/session/visibility generation、距離、可互動權限、目標/內容已驗證才接受點擊或 C39；不能在缺 assets 時憑空生成 NPC appearance/animation，任何原版不明的 S1A u8/u16 狀態拒絕或用有註明之 local fixture。S44/C6C script lifecycle 只證腳本工作流；Born (31,29) 是 waypoint，不代表 NPC ID、招募員 map 或完成條件。

交付界線：A-011 integrated/handoff partial；codec+resource-bank 可實作，原服 NPC kind/type/resource/motion 行為、掉落、click→dialogue 對應未證；A-024 仍 open。原 Roy1 局部 CT-066～068；main 用 CT-082～086，native not-run；原版 Client E2E not-run。Monster00.dat、World00.dat 已提供；若後續驗證需要，再按真引用確認 Monster01.dat～Monster42.dat 或 Basic.dat 的具體樣本；其餘 NPC/Spawn 來源確切檔名 unknown。

## A-011／2026-11-01 原始 S07 第五欄實證與 C43 3-mode（E09～E15）

比過去只知道 `S07 appearance/resource_candidate` 更進一步，**原版 BIN 已追到完整欄位→圖像庫呼叫鏈**：原讀取 `0x57E456` 把 S07 每行第五欄 **BEu16** 寫在 `[row+0x0C]`；world handler `0x4F1A7F` 將該值放到 20-byte descriptor 第一欄，kind1/2/4 建立 `MonsterObject0x4D6FA0` 後 `0x4D7020` 保留 descriptor、`0x4D70A6→0x4D2340→0x4D235C` 解第一個 u16，經 `0x4D7530/0x4D7560` 對 `0x4000+N` 求 Monster archive library/slot。**`row+0x222` 的 tail u16 另轉 float 存 +0x27C，不能當 sprite/image ID，也不能把 scene object_ref 當 server monster template。**

已證的安全投影：`0x4000..0x41AD` → `Monster00..42.dat`，library8000..8042，10 個 logical image slots/庫。**這 10 個 slots 不等於原報告 Monster00.dat 的 5 個 YPF member，也不保證所有 frame/group/direction 均能讀出**。本輪沒有 Monster00/World00 原 binary，既有 archive metadata 只可引用過往證據；原版 Client 目前 UI 與 sprite/animation 尚未驗。

C43 已在 `0x4A2376..0x4A2558` 新確認 pane mode0/1/2 各會送 `type1/subtype0x04,0x10,0x40`、BEu32 object_ref 同源 pane+0x4C；先前只有 C43 type1/subtype04 的說法已非完整集合。但 **NPC/monster 點擊→真 C43/C39→S34/S3C/S44/NPCChatDialog 的主動因果未證**，依然不能授權對話/商店/任務。原服 AI/掉落/生成與教學招募員 Script binding 仍需 Server 原件/trace。

[最新 BIN-first 報告](../task_a/roy2/A-011-native-s07-visual-id-c43-20261101.md) · [CT-116 原始 PE/合成驗收](../05-conformance/A-011-s07-visual-source-c43-test-plan.md)。A-011 靜態 Client 對應碼可交 DEV，原生 CT-083 未執行，`integrated/partial` 狀態不變。
