# 背包與裝備：已知分支

S0F（parser 0x57a3f0）：種類u8、格位u8、圖示u16、RGB3、旗標u8、使用類型u8、另一旗標u8、附加標籤string8、名稱string8、描述string8、三旗標u8（第三為數量模式）、模式0時u16數量、u8旗標、u8附加描述數；每個描述分支仍須補完整欄位。本profile種類1、使用類型5、數量模式0／數量1、附加描述數0。

種類0在已查路徑被忽略；種類1進UserInventory。ItemListPane 0x4932c0在使用類型5及合法性檢查成功時送C1C：01 slot 00 05。其他使用類型的對話及後續包屬A-007範圍。

S37（parser 0x579830）：格位u8、圖示u16、RGB3、旗標u8、名稱string8、描述string8、三旗標u8、跳過一byte、bool一byte、附加描述數u8。本profile無附加描述。裝備格位2在所測Client顯示鎧甲，不能據此填滿全部槽位表。

原型衣櫃以slot映射衣服資源ID、允許反覆換裝且不消耗。這是本機測試設計，不是正式物品實例模型或官方資料表。正式Server必須另外定義物品實例、堆疊、所有權、交易和各種刪減／脫裝封包。

成功換裝的共同語意是：檢查意圖→原子更新裝備狀態→回S37及S33；保留面向、髮色、衣色和world座標。其他玩家的外觀投影與移除事件待A-004。失敗不得先更新外觀再嘗試回滾資產。

## A-007 / roy1 — 原版完整 item wire 有界子集（2026-10-31）

[原始 EXE BIN-first 報告](../03-analysis-requests/A-007-roy1-inventory-lifecycle.md) / [Server 契約](A-007-inventory-domain-contract.md)：C1C writer 0x577800 body `kind:u8,slot:u8,flag:u8,use_kind:u8`，`use_kind` 1..9 由 jump table0x577920 分流：1 string8；2 u32BE；3 4×u16BE；4 3×u16BE；5 無；6 2×u16BE；7 u16BE；8 2×u8；9 2×u16BE。原本本機衣櫃 C1C type5 不可套到所有物品，分支語意仍 unknown。C1E u8（writer 0x578010）；新增 C08 Drop 三 u8（0x571ff0）、C0C PutRequest 一 u32BE（0x574af0），其三個 drop byte 與 put object ID 作用仍 unknown，不能自動發放/刪除 item。

**新增 S10 RemoveInventory opcode0x10**（ctor0x585b80、reader0x585c30）3×u8；**S38 RemoveEquipment opcode0x38**（ctor0x585a10、reader0x585ac0）`u8 slot,u8 raw_flag`，其內部 bool 判定為 `raw_flag==1`。不能只憑名稱宣稱 S10/S38 必是全量刪除；原 parser 只證欄位。S0F AddInventory reader0x57a3f0，在 0x57a4f8 依 count mode0→u16、mode1→u8、mode2→u8+變長 list；另有附加尾欄，正式 encode 需完整 branch；S37 reader0x579830 含多種 flags + 變長 description，非固定大小。原生 Client 不攜帶可證 item_instance_id（不同於 icon/resource/object ref），Server 需要內部穩定 ID；原服 stack cap、合法 equip slot、真正卸裝及交易仍 unknown。

**DESIGNED Server 方案**：ItemTemplate/ItemInstance(owner,location,slot,quantity,revision) + 唯一槽位、帶 session/generation 的權威檢查、原子 mutation/operation ledger/outbox；背包滿卸裝不得修改裝備、同 intent 重送不重消耗、回覆遺失/SQLite 重啟按 durable snapshot 恢復。注意 C1C 本身沒有原生唯一 request ID，無法在任意重送情境僅靠 wire 精準去重。SCN-015/CT-057～059 planned；A-007 integrated/handoff partial、native Client E2E not-run。
