# A-011 / roy1 — NPC／怪物資源 ID、互動與外觀動畫接線（BIN-first）

> **main 補正**：本檔「缺 Monster00.dat」為當時分支狀態，目前已有 Monster00.dat、World00.dat 各5個YPF member，未驗證具體NPC/Monster imageId→YPF動畫或點擊。Roy1 原 CT-066～068 是過時的來源局部編號；請以 main CT-082～086 為準，原版 Client E2E not-run。


日期：2026-10-31；分支 `task_a/roy1`；Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。Evidence `ev_a011_20261031_monster_bank_s07_c39_motion_static`。方法：原始 EXE x86 反組譯與 UTF16 resource filename xref + A-004 S07/sprites/entity registry + A-026 C39/S44/Born。**本次完成可從 Client 直接證明的載入/封包/動畫子集；原始怪物模板→實際 ID/技能/掉落/正式 NPC 對話仍未知；original Client E2E not-run。**

## 1. 具名原版資源 — Monster%02d.dat

原版 `Asgard.exe` 的 UTF-16LE string 位於 **VA0x5F1D3C**：`Monster%02d.dat`。資源註冊函式 **0x403F80..0x4043B0**（處理 `Basic.dat`、Human、Effect、Monster）在 **0x404371** 令 `EDI=0x1F40`，**0x404380..0x4043AF** 每輪：
`format(L"Monster%02d.dat", edi-0x1f40)` → `0x440720` 登記 `resource_index=EDI` → EDI++ until `EDI>0x1F6A`。

因此明確 Client 資源索引區間 **0x1F40..0x1F6A（8000..8042，含 43 種 Monster 群檔）**，具體檔名 **`Monster00.dat`～`Monster42.dat`**。這是資源庫索引範圍，**不是原版 Server 永久 `monster_template_id`、NPC instance EntityId 或 S07 的 object_ref**；本機沒有上述 `MonsterXX.dat`，無法解析每個檔內角色 sprite/animation/recolor、monster template 對照或實際圖片。

此外 Client 會註冊 `Basic.dat`（VA0x5F1FC4，0x403FA4 呼叫）；Human asset `Human\\s%03d.dat` 等（另有不同類別包）及 `Effect%01d.dat`；Human 資產不能用來臆測 NPC 全部採用玩家模型。原始 EXE 含 `monsterimagelib.cpp/monsterobject.cpp/NPCChatDialog.cpp` 的 debug paths，足以證相關 Client 類別存在，**不代表其任何特定貼圖、對話或動作已從檔案讀出**。

## 2. Server→Client 外觀／可見性提供哪幾種識別

A-004 的 `S07 DrawObjects`（opcode0x07，parser **0x57E3E0**）：body 前兩個 byte 是 BE u16 count；每筆共通前綴按順序 **BE u16 x、BE u16 y、u8 kind、BE u32 object_ref、BE u16 appearance_or_resource**；其後依 `kind` 決定 flags/RGB/string8（kind1/2/4）、5×u8+string8(kind3)、string8(kind13)、2×u8+u16(kind14)、kind5..12 不增加 tail（觀察 parser 而非全部 Server 合法性）。`0x4F17C0` DrawObjects handler:
- `0x4F1818` 先讀 `record+8` 的 **32-bit object_ref**，`0x4EAC70/0x4EAC30` 連到 MapPane 物件容器；
- `0x4F1975..` 根據 `kind` 選不同建構支路，對 `kind1/2/4` 會把 `record+0x0C` **16-bit appearance/resource candidate** 和其他方向/染色/名稱欄送去建立物件函式 `0x4D6FA0` 等。
- **`0x4F198D..0x4F199F` 有一個特殊 resource candidate `0x8000..0xBFFF` 範圍測試**，通過後走 `0x496540` 另一路呈現。這說明 **不同 resource ranges 的 Client 選擇行為不同**，但沒有證據可直接把 `0x8000..0xBFFF` 全部稱為「怪物編號」；Monster file registry 的 `0x1F40..0x1F6A` 是**另一層 ID namespace**。不得以 `resource_id-0x1f40` 當怪物實例/模板 ID。
- `S33 PutHumanObject` 另給人物座標、方向、u32 object_ref、衣服/髮型/顏色/name；`S05` 是本地玩家，不能當 NPC 用；`S0E`、`S5F` 分開移除與死亡。
- `S0C`、`S64` 提供位置/路徑，`S11` 提供轉向；`S1A Motion` reader **0x582FD0** 讀 `u32BE object_ref,u8,u16BE,u8`，是可證的動作通知，但 3 個控制欄位對應的 stance/animation frame/state 尚未從 `MonsterXX.dat` 比對證明。完整帧長與動畫循環頻率也 unknown。

## 3. 點擊互動與任務分流

- 原版有 `C39 Merchant`（ctor 0x5737C9、writer **0x573860**）：固定 `u8 field,u32BE opaque ref,u16BE field`，依 subtype1..9 有 string8/u8 額外尾欄；可作**商店或 NPC 交易意圖 codec**，但 `opaque ref` 要在目前 World/map/observer 可見表中驗證，不能把它當已授權 NPC Template ID，也不能聲稱女性招募員一定走此封包。
- `C0C PutRequest`（0x574AF0）有 `u32BE object ref`，名稱提示不同互動入口，但尚未追到精確 mouse UI callsite；也不能把它當肯定的 NPC 點擊。
- `C13 Attack`（0x570AC0）也送 `u32BE target_ref`，這是戰鬥意圖不是 NPC 對話；不能將任何 click target 混成攻擊／交易／任務完成。
- `S44/C6C` 是腳本資源與執行生命周期。已提供 `Born.dat` 引導玩家去 **(31,29)** 找女性招募員；**沒有**指定 NPC entity id、NPC template id、確定 map_id、觸發 Merchant subtype、對應 `nNewJoin01.dat` 綁定與任務獎勵。A-023/024 的其他 Script 資料與原服封包仍需。
- 未找到可原生證明的「單一 universal NPC-click opcode + 永久 NPC ID」；目前應把 `OnClientClick(object_ref)` → `Server validated visible target` → `InteractionKind` 視為**新 Server 設計抽象**，而不是原版協定新封包。

## 4. 交付給 Server（DESIGNED）

`ContentAssetRef(archive,resource_index,filename,release_sha)`、`NPCMonsterTemplate(template_id,kind,asset_ref?,animation_map?,interaction_roles?,drop_table?)`、`Spawn(entity_id,world_instance,map_ref,x,y,template_id)`、`ObserverWireRef(connection_generation,world_epoch,u32_object_ref,entity_id)`、`InteractionIntent(observer,opcode,wire_ref,subtype)` 必須分層。只有已核對的 resource archive+實例 map/row 才可生成 S07，缺 `MonsterXX.dat` 時不捏造外觀和動作；Server 驗證 NPC 同圖/距離/可見/有效 generation 與權限才允許 Merchant/dialogue/combat 效果。S1A 三個參數只能按 proven variant encode；沒有完整 asset animation table 時，不能使用自製的通用動畫 enum 當作原服動作碼。

## 5. 結果與缺少的精確資源

A-011 `status=integrated, handoff_status=partial, implementation_ready=true` 僅對 **Monster00..42 檔名/索引、S07 物件外觀候選、S1A motion codec 與 C39 bounded interaction intent**。`native_npc_template_binding_ready=false`、`native_monster_appearance_animation_ready=false`、`native_click_action_mapping_ready=false`、`native_drop_table_ready=false`、`native_client_validation=not-run`；A-024 原版教程 NPC/怪物還需專項解析，未因此關閉。CT-066（索引/檔案）、CT-067（S07/S1A 模型對接）、CT-068（互動與最小 E2E）planned。

**尚缺檔名**：最明確是 **`Monster00.dat` 至 `Monster42.dat`**（原 Client 的 43 個 resource-index 檔名）；也尚缺原版 **`Basic.dat`**（Client 直接使用，未證其含 NPC 模板表），可選 `Effect0.dat`～`Effect9.dat` 依 Client `Effect%01d.dat` 模式。其他真正 NPC spawn／掉落定義檔**確切檔名未知**，不得虛構存在。需要原始同版 NPC/Monster assets、NPC 點擊／死亡封包 traces 才能完成真實 template→Client render/animation/action mapping。
