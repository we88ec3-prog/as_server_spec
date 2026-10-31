# A-004 / roy1 — 其他物件可見性、32-bit wire object reference、移動與消失（BIN-first）

2026-10-31；branch `task_a/roy1`（原分支，不新建）；原始 `Asgard.exe` 3,235,840 bytes，PE32 x86 / ImageBase0x400000，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；profile `TW-seed0-local-v0.1`；evidence `ev_a004_20261031_world_entity_visibility_bin_static`；R-004/R-007、SCN-005、A-024 依賴。

**分級**：原 Client observed-static 已證以下 opcode、reader 欄位、地圖 registry lookup 與部分 handler；新 Server AOI/generation/fencing 是 designed；原 Server 可見半徑、何時廣播、EntityId scope/reuse/死亡復活策略 unknown；原 Client 兩開 E2E not-run。A-004 `integrated/handoff partial`，只對已證 codecs 與安全 Domain skeleton `implementation_ready=true`，原生多人可見生命週期未驗收。

## 1. 不是 S33 一種封包：原版 S2C entity lifecycle

|opcode / class|constructor opcode VA|原始 reader VA|Client decoded body (opcode/ordinal/frame **不含**)|
|---|---|---|---|
|**S07 DrawObjects**|0x57e329 push 0x07|**0x57e3e0**|`u16BE count; count × variable record`；每 record 的共通前綴 **u16BE x,u16BE y,u8 type,u32BE object_ref,u16BE resource_or_attr**（11 bytes），type 決定額外 fields|
|**S33 PutHumanObject**|0x5854d9 push 0x33|0x585570|既有 `appearance.md` human: BE u16 x/y, facing u8, **u32BE object_ref**、外觀/名稱/flags（variable）；不能拿 C33 自身移動封包取代|
|**S0E RemoveObjects**|0x585e79 push 0x0e|**0x585f10**|**u32BE object_ref**，reader 寫 [packet+0x24]（subobject +0x18）|
|**S5F DieObjects**|0x57e1c9 push 0x5f|**0x57e260**|**u32BE object_ref**，和 S0E **不同 opcode/不同 Client handler**；不是 kill/quest authoritative ACK|
|**S0C MoveObject**|0x5833b9 push 0x0c|**0x583450**|u32BE object_ref, u16BE x, u16BE y, u8 field0, u8 field1 (**10 bytes**)；最後兩 u8 真正意義待 handler/動態證據|
|**S64 MovePath**|0x583549 push 0x64|**0x5835e0**|u32BE object_ref, u16BE x, u16BE y, u8 field0, u8 path_count, `path_count × u8` path data, u16BE field1, u16BE field2, u8 field3（**15+N** bytes）；各欄語意尚非原生證實|
|**S11 ChangeDirection**|0x57d6d9 push 0x11|**0x57d770**|u32BE object_ref + u8 direction（**5 bytes**）；方向 0..7 profile 已有 C11 用例，但原服完整合法集合待驗|
|**S1A Motion**|0x582f39 push 0x1a|**0x582fd0**|u32BE object_ref, u8 field, u16BE field, u8 field；動作意義/時長不可猜|
|**S05 UserAppearance/Self**|0x589509 push 0x05|0x5895a0|含 u32BE 自身 ref 與外觀；**S05 是自身**，其他角色用 S33 / generic S07，不應把 own S0B 當他人可見更新|
|**S15 Map**|已在 A-022|0x57ff30|Client 載新圖清理舊圖其他物件、保留自身的本地 map transition；不是若干 S0E 等價之世界永久死亡|

### S07 type-specific 原生分支（反組譯已完整區分「哪些型別有額外尾部」）

0x57e3e5 先讀 BE u16 count；0x57e3f1 `count × 0x228` 配本地 record 結構空間；0x57e428..0x57e456 依序 u16 x/u16 y/u8 kind/u32 ref/u16 attr。0x57e45a..0x57e46f `dec kind; cmp <=13` 加索引表 0x57e5e8 與 dispatch table 0x57e5d4：

|type|reader target / 分支|有界結論|
|---|---|---|
|1、2、4|0x57e476|多旗標與選填 RGB/u16/string8；參見 0x57e476..0x57e538，**不可當固定11 bytes**|
|3|0x57e538|5×u8 + string8|
|5～12|0x57e5b1|無額外欄位；共通 11 bytes/record（可作**純合成**最小 fixture）|
|13|0x57e57e|string8|
|14|0x57e592|u8,u8,u16BE|
|其他|default 0x57e5b1|原 reader 無額外尾部 **不代表 Server 可創建合法未知型別**|

**重要 parser 限制**：原始 count 是 u16，原 reader 的 `count × 0x228` 未在本輪證實具 Server 分量上限；設計新 Server 時需對 records/list/string 與總 frame 設容量上限、防整數溢位。不能因 type=某號碼就直接命名為 NPC、怪物、道具，缺 World handler/資源對應證據前保持 unknown。

### 32-bit object_ref 的地圖 registry 使用

- DrawObjects handler **0x4f17c0**：取 packet+0x24 count，packet+0x28 record array；`0x4f180d` 按 stride0x228 取每筆；`0x4f1818` 讀 record+0x08 object_ref，呼叫 **0x4eac70**；type0x0e / flag 特殊分支 `0x4f1821`，進一步由 **0x4f183f** 呼叫 `0x4eac30` 找現存 object。
- registry lookup **0x4eac30..0x4eac62**：對 MapPane-like context `+0x94` 樹狀容器依傳入 ref 查找、找不到傳回 null，找到傳回保存的 object pointer。其它事件函式 `0x4f1610`、`0x4f16e0`、`0x4f1750`、`0x4f2a70` 取 packet+0x24 object_ref 後走此查詢；找不到時部分分支會檢查替代 registry `0x4ea240` 並呼叫 `0x46d230`，**有可觀察的未命中恢復／訊息路徑，不能理解為 Client 會憑空替未知 ID 生成精確對象**。
- `0x4f16e0` lookup 後走 `0x47a2f0`，`0x4f1750` lookup 後走 `0x47c9c0`，形成**不同的 removal/death 類 action**。惟尚未將這兩條回調逐一動態綁定 S0E 與 S5F 的所有可見效果，**不可聲稱兩者一樣或固定哪條一定移除渲染/生成屍體**。
- `u32BE object_ref` 在各 reader 前綴中跨封包一致；不能由此推出 Server 永久 `character_id` / `npc_spawn_id` / `item_instance_id` 的存活週期、跨 map 全域唯一性、ID 範圍、最高 bit 語義或重用政策；**原生 wire 沒有 map_epoch/visibility generation**。
- map loading S15 清除舊場景其他物件，Self S05 與 S04 定位另分流；S0E (離開/清除候選)、S5F (死亡/移除候選)、S15 切圖清理 **不得混為持久 world entity 刪除**。真原版掉線是否主動一律 S0E、可見視距半徑、多人 AOI 首入順序仍 unknown。

## 2. Server-only 可交付模型（DESIGNED，不冒充原服）

1. `Entity(entity_id stable Server PK, kind, map_instance_id, spawn_state, world_generation)` 與 `ClientEntityRef(connection_id,generation,map_epoch,u32wire_ref,entity_id,visible,revision)` **分開**；同個 u32 引用只在綁定的 session/world/map epoch 有意義。
2. Server authoritative AOI interest `Visible(observer,entity)`：**使用已證地圖與角色位置**、授權/實例/遮蔽規則，未確證原服半徑時由 DEV 明示 designed 參數；禁止跨地圖、跨 instance、未通過 World loading 的物件投影。
3. 新入視野人類 S33（必要外觀與資源完整後），其他類別 S07（只供已證 type/res fields，未證型別 fail closed）；進視野後的位置 S0C/S64/方向 S11/動作 S1A。離開 AOI 或斷線需發經權威確認、同 epoch 的 S0E；真正死亡可使用 S5F（詳細視覺/移除流程待 E2E），**不能以 Client death packet 充當 Server loot/quest progress**。
4. 同連線 `visible[wire_ref]` 唯一：重複 spawn 同身分是 refresh，換了 entity_id 卻重用 wire_ref 必先消除舊可見 binding / epoch fence；漏 spawn 的 move/death 不可建立假 entity；清 map 清全部非自身 projection，client S15 的局部清理不刪除 DB 永久 entity。
5. 原本 packet 沒有 epoch，同一 TCP 若 **舊 S0E 與新 S33 使用同 wire_ref**，Client 無法分辨新舊實體，單靠 Server 內部 epoch 並不足以消除此歧義；必須序列化/batch 排序與可驗證傳輸屏障，否則 fail closed/reconnect/不重用 ref。
6. 玩家斷線 / World generation 淘汰：對其他觀察者發其 scope 內 removal，不能讓離線 object 繼續收 movement；玩家登入/出圖則與進圖 snapshot 同步，避免「幽靈」與重複渲染。
7. Client 最大 frame/loop/字符串限制是 parser 安全閘；Server 不可以將未知 S07 type 的 payload 任意映射為 NPC/monster/graphics，也不能把 S33 用於所有種類。

## 3. 研究與驗收

- 原始 EXE **20 個 byte signature 全部匹配**；`tools/a004_visibility_model.py` 本地 **18 個 unittest 全部通過**，含 S07 type5 共通欄位、S0C/S64/S11/32-bit endian，DESIGNED two observer/map instance/generation/reuse/tombstone 範例。這是 BIN-static+synthetic，**非原 Client E2E，也不是 Server 已實作**。
- `CT-063`：S07/S33/S0E/S5F/S0C/S64/S11/S1A native byte layouts，kind 分支及截斷/長度上限。
- `CT-064`：兩個 Client 同圖加入互見、移出視野、斷線、重登、切圖；identity/visible state、生成/消失/更新確實出現在原 Client；未實測為 planned。
- `CT-065`：Server-synthetic per observer generation/map_instance ID 重用、跨圖/跨 World 舊封包、重送 spawn/disappear/death、死而未移除、遺漏 spawn 等，含 fail-closed。
- 原有 `CT-018`（多人原生）、`CT-022`（NPC 可見）保持 planned；SCN-005/011 保持 analysis-required。
- **針對 A-025 更正**：先前 `PKT-S1E DieObjects` 是把 `0x57e298 push 0x1e`（工廠配置/除錯參數）誤認 opcode。真正 constructor `0x57e1c9 push 0x5f → call 0x578730`，因此正確 **PKT-S5F**。此更正不改 C1E Wear 的 0x1e，也不證死亡就是 quest objective。
- **精確缺件／證據**：現有 `Asgard.exe` 與 `Map0.dat/Map1.dat/Map2.dat/Born.dat` 可供再追；**沒有已證可指名的 NPC/Monster map 配置檔名**。要把 A-024 的怪物類型↔S07 type、原版 vis radius/ID reuse、玩家斷線通知變原生驗收，需要原版同版 Server→2 Client 的登入、兩人相遇、出視野、死亡/復活、斷線、重入圖封包 trace（包含 S15/map id 與時間），以及能連結 NPC spawn/script/map 的同版資源。不可捏造 `NPC.dat` 已存在。

重現：
```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x57e1b0 --stop-address=0x57e5f6 Asgard.exe
objdump -D -M intel --start-address=0x585e60 --stop-address=0x585f1d Asgard.exe
objdump -D -M intel --start-address=0x5833a0 --stop-address=0x58366a Asgard.exe
objdump -D -M intel --start-address=0x4f17c0 --stop-address=0x4f1b55 Asgard.exe
objdump -D -M intel --start-address=0x4eac30 --stop-address=0x4eac65 Asgard.exe
python3 tools/a004_visibility_model.py
```
