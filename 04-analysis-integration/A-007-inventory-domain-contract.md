# A-007 — 物品實例、背包與裝備 Server 安全交接

來源 [A-007 BIN-first](../03-analysis-requests/A-007-roy1-inventory-lifecycle.md)，原版 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；Evidence `ev_a007_20261031_inventory_lifecycle_static`。**此文件的 transaction/ledger/instance schema 屬 designed，非原服實作證明。**

## 原生最小 codec

C1C `0x1c` = `u8 kind,u8 slot,u8 flag,u8 use_kind,tail(use_kind)`。tail：1 string8、2 u32BE、3 4×u16BE、4 3×u16BE、5 empty、6 2×u16BE、7 u16BE、8 2×u8、9 2×u16BE；writer 0x577800，jump table0x577920。C1E `0x1e` = u8 slot (0x578010)；C08 `0x08` CDrop = 3×u8 (0x571ff0)，C0C `0x0c` CPutRequest = u32BE (0x574af0)。C08/0C 欄位原生語意未完整驗證，不能開放資產效果。

S0F `0x0f` AddInventory 變長 (0x57a3f0)：mode0 u16BE / mode1 u8 / mode2 u8+u8 count+additional variable entries，尚有尾欄；S37 `0x37` AddEquipment (0x579830) 變長描述；S10 `0x10` RemoveInventory = 3×u8 (0x585c30)；S38 `0x38` RemoveEquipment = u8 slot,u8(raw flag) 且 local boolean `raw==1` (0x585ac0)。S10/S38 對 Client 結果的完整 action 分支仍需證，不可自行製造其 success code。所有 body 不含 opcode/ordinal/AA frame。

## Designed Domain

```text
ValidatedSession/WorldGeneration
  -> Decode exact C1C subtype/C1E/C08/C0C
  -> Verify item ownership, current bag/equip location,
     item instance ID by server lookup, slot bounds, quantity, 
     template/equip legality, target/map/World state and item revision
  -> Atomic InventoryMutation + OP ledger + outbox
  -> Project native-compatible S0F/S10/S37/S38 and S33 appearance
  -> Reconnect: durable snapshot; no duplicate grant/consume or ghost equipment
```

Schema: `ItemTemplate(resource_release,template_id,stack_limit?,equip_slot?,flags?)`; `ItemInstance(instance_id PK,owner_id,template_id,location,slot,quantity,revision,attrs)`; `UNIQUE(owner_id,location,slot)`；`InventoryOperation(op_id UNIQUE,owner_id,world_generation,request_digest,decision,result)`；`Outbox(op_id UNIQUE,packet_projection)`。不確定原服數值時必須明確標 unknown。item_instance_id/op_id 是 Server-only，不是原版 Client packet 的 32 位欄位。

失敗處理：背包滿不能卸裝、非法 slot/件數/owner/舊 generation 不更新狀態；stack split/merge 防 overflow；相同 op_id+digest 重送 return saved result，不同 digest conflict，交易和 outbox 同事務。無原生唯一 request id 時 wire-level 原始完全相同重送的歧義只能靠 state/generation/fencing 控制，不能保證任意舊包識別。

可交 DEV：以上已證欄位 codecs、嚴格 bounded parser、sqlite Domain transaction tests、通用裝備/背包投影骨架。**不可**用本機服裝測試替代全部 item lifecycle；原生 item legal template、item use_kind 業務含義、真正 drop/pick/unequip UI、經濟交易及 S0F/S37 變體未完成，`native_full_item_lifecycle_ready=false`。CT-057～059 planned；A-007 integrated/handoff partial，original Client E2E not-run。

## 2026-11-08 消耗品與堆疊增量

本輪補核原生非指定物品使用C1C(kind1,slot,flag0,useKind5)，分開可信Server的穿戴與消耗品政策；不是將所有C1C種類開放成任意資產能力。C30 subtype8與同格S0F／耗盡S10投影已有精選來源。見[原件使用及數量投影](20261108-native-consumable-use-and-stack-projection.md)、[消耗／堆疊／升級權威](20261108-consumable-stack-and-upgrade.md)及[實作與驗收範圍](20261108-consumables-color-and-manual-acceptance.md)。原版完整道具效果、C08丟棄與C0C拾取語意仍未開放；也未把Server可部分拆到空格冒稱已有原生手勢。


## 2026-11-08 裝備模型投影增量

[武器／盾牌／頭部Human外觀](20261108-equipped-human-visuals.md)補上S05／S33附件欄位、圖像庫查找、重建物品的顯示綁定及多人一致快照；原始物品模板與全部裝備效果仍未完成，原生畫面待測。
