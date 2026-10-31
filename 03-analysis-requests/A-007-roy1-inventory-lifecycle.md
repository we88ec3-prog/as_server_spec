# A-007 / roy1 — 背包、裝備、數量與移除的原生 Client BIN-first 分析

2026-10-31；既有分支 `task_a/roy1`；原始 `Asgard.exe` 3,235,840 bytes PE32 x86，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，ImageBase 0x400000；Evidence `ev_a007_20261031_inventory_lifecycle_static`。目標 R-008/R-017，關聯 A-004/006/008/013/015/016。結論：A-007 `integrated / handoff_status=partial / native_client_validation=not-run`；可開發 **type-specific codec、inventory/equipment safety skeleton、持久唯一 ledger**；完整原版經濟與物品 business semantics 仍未證實，不得把測試衣櫃當真正式資產模型。

## 原始 Client 已證 C2S 欄位與行為

|封包|constructor / serializer|body（不含 opcode/ordinal/frame）|實際限制|
|---|---|---|---|
|**C1C UseInventory** opcode0x1c|0x577750 ctor（push 0x1c at 0x577769），writer **0x577800**|固定 **4×u8** `kind,slot,flag,use_kind`；其後 **依 use_kind=1..9** 變長|此前 local `01 slot 00 05` 只是 type5、無額外 bytes 的衣櫃測試；不能視所有可用物品皆此型|
|**C1E Wear** opcode0x1e|0x577f60 ctor，writer **0x578010**|`u8 slot`|哪一個 Client UI 操作導致脫裝/換裝、是否直接消耗或替換，需 action callsite 與 runtime 證據；不能因名為 Wear 就等於真脫裝命令|
|**C08 Drop** opcode0x08|0x571f40 ctor（push 0x08 at 0x571f59），writer **0x571ff0**|`u8,u8,u8`|這是 drop 類 request 的已知 wire，實際每 byte（bag slot/count vs action）語意未證，**不能直接把第3欄當數量**|
|**C0C PutRequest** opcode0x0c|0x574a40 ctor（push 0x0c at 0x574a59），writer **0x574af0**|`u32_be opaque`|疑似拾取/放置交互流程，必須查其 UI sender / world object identity，**不可把這個 u32 當物品持久 instance ID**|

### C1C `use_kind` jump table 原始逐分支證據

0x577831 `movzx eax,[esi+0x1b]; dec eax; cmp eax,8; ja default; jmp DWORD PTR [eax*4+0x577920]`。table 0x577920 按 1～9 的 target：

|use_kind|實際 writer target|額外 body|全 body 長度（string8 例外）|
|---:|---|---|---|
|1|0x577846|string8（u8 encoded byte count + encoded bytes）|5+len(bytes)|
|2|0x57785f|u32 BE|8|
|3|0x5778ba|4×u16 BE|12|
|4|0x577894|3×u16 BE|10|
|5|0x57791e|無|4|
|6|0x57787a|2×u16 BE|8|
|7|0x57786c|u16 BE|6|
|8|0x5778ec|2×u8|6|
|9|0x577906|2×u16 BE|8|

原始 endian writer helper `0x45ab00=u8, 0x45ab40=u16BE, 0x45ac40=u32BE, 0x45b1b0=string8`。不在 1..9 的 type 會走不寫尾部的 default；**這不代表其 type 是合法且可執行的 Server command**。字串長度是編碼後 byte 數，TW CP950 codepage 依 LanguageMan index4 profile；其他語系不能沿用。

## 原始 S2C 同步、移除和數量分支

|封包|original constructor / reader|Native body 與限制|
|---|---|---|
|**S0F AddInventory** opcode0x0f|0x57a1c0 constructor（既有）、reader **0x57a3f0**|既有主欄 u8 kind,u8 slot,u16 icon,RGB3,flags/u8、使用類型、文字與 description；新增核對 0x57a4f8 選 **mode0/1/2**：**0→u16 BE count，1→u8 value，2→u8 + u8 count + 變長 entry 清單**，具體每 entry 的 name/flags/order 和後續尾欄需完整 parser spec 才能正式 encode。模式 0 的 count 字段不等於所有 mode 的 count|
|**S37 AddEquipment** opcode0x37|0x579170 constructor、reader **0x579830**|u8 slot/u16 icon/ RGB3/flags/2×string8 + additional flags、boolean、變長描述；先前已知 local outfit/no-extra 只是子集|
|**S10 RemoveInventory** opcode**0x10**|**0x585b80 ctor，push opcode at 0x585b99，reader 0x585c30**|**3×u8**，native stores packet +0x18,+0x19,+0x1a；推測其中含 inventory slot/更新 mode 但實際作用尚需 handler 調查；不可假設每次 S10 都永久刪掉全部堆疊|
|**S38 RemoveEquipment** opcode**0x38**|**0x585a10 ctor，push opcode at 0x585a29，reader 0x585ac0**|**u8 slot, u8 raw flag**；第二欄經 `dec; neg; sbb; inc` 投影 Boolean `(raw==1)`；Bool 意義（卸下/移除/刷新）仍 unknown，不能把 S38 某固定值當原服確認卸裝|

注意方向：C1E opcode0x1e 是 **Wear C2S**，與 **S1E DieObjects S2C** 完全不同；C0F 和 S0F 也不同。

**原版 Client 沒有看到可直接信任的 Server 物品 persistent instance ID / 全球唯一持久識別值**；顯示用 icon/resource ID/slot/name 不能取代 Server 的 item_instance_id。C08/C0C 的真正 UI sender、地面物件擁有權、多人競爭拾取與後續 item removal 尚須 A-013/011/015 或原版 Server trace。A-007 已把原生包格式追到可交接的範圍，不硬猜遊戲經濟規則。

## 新 Server 領域模型（DESIGNED，不冒充原服）

- `ItemTemplate(template_id,resource_release,equip_type,stack_limit?,bind_policy?,appearance_refs?,validated)`；真正模板、各類限制由 A-015/013 證據確認，未知保留 null。
- `ItemInstance(instance_id PK, owner_character_id, template_id, location, slot, quantity, revision, attrs, acquired_event_id)`。即使 wire 無 instance_id，Server 內部仍使用穩定唯一 ID 和版本。location 為 Bag/Equipped/World/Bank/TradePending 之 tagged domain；其他 location 未有原生完整封包者不得對 Client 公開。
- 槽唯一 `UNIQUE(owner,location,slot)`、背包容量按 *verified slot capacity*，裝備佔用/equip compatibility 按 template+character。堆疊不能負數/零/越界；split/merge 的 instance 轉移需同一 transaction，merge 只在模板/綁定/屬性可合併、總數不越界時成立。新 Server 不以本機衣櫃 slot→服裝資源直接創造任意物品。
- `InventoryCommand` 只代表 Client intent，使用 `owner+session_generation+world_epoch+slot+item_revision+body_digest` 安全核對；C1C type5 僅證明本地成功換衣服，不代表可免費複製衣物或所有 use_kind 同政策。C08 Drop/C0C PutRequest 驗證 map/ownership/real world object atomically；未知流程先 fail closed。
- 原子流程：verify owner/slot/template/count/bag capacity/World readiness → CAS ItemInstance revision → commit inventory/equipment change + `operation_ledger(op_id, owner, digest)` + `outbox` → **按 native已證 S0F/S10/S37/S38、S33 投影**。沒有權威已證 fields 時不能送會被誤解的完整 payload；失敗不得先改 S33 appearance 再「補救」資料庫。
- 背包滿的卸裝保持裝備原位，使用/消耗失敗資產不變；同 request 身分/內容 replay 回既有結果、不二次消耗；相同 op key 不同 digest conflict；斷線/重登/Server crash 依 durable ledger/revision 重建 Bag/Equip，不可複製或遺失；跨 owner 或舊 session reject。
- 與 A-016 一致：Client C1C/C1E/C08/C0C 沒有已證 globally unique operation ID；上述 `op_id` 是 **Server 內部 designed** 交易意圖，不能捏造成 wire 原生欄位。當兩個相同封包在無可辨識 context 被重送時，單靠 bytes 可能無法判定新操作／舊重送；需單 outstanding intent、generation/response fencing 或 fail closed，不能保證任意流量完全自動去重。

## 測試、限制與精確缺件

- 離線 **15 組** 原版 EXE opcode/reader/writer byte signature 核對；本地 Python SQLite synthetic **12 個 unittest 均通過**：C1C 1..9 的逐類長度、S10/S38 截斷與 bool、equip/unequip/replay、背包滿、跨 owner、split/consume/數量、duplicate operation digest、crash/reopen/唯一 slot。不等於原版 Client E2E。
- `CT-057`：C1C 1..9、C1E、C08/C0C、S10/S38 的 native opcode & strict parse, 每 subtype 截斷/尾隨拒絕。 `CT-058`：S0F mode0/1/2、S37 變長描述及裝備/背包完整 snapshot，內容異常拒絕。 `CT-059`：物品實例 unique/owner/capacity/count、equip/split/consume、重送/SQLite crash/outbox，並保留 native pending E2E。
- **仍缺**：原服的物品模板/stack cap/裝備 compatibility、真正 C08 Drop/C0C PutRequest 互動、C1C 每 use_kind 的消耗及回覆判定、S0F/S37 全部 mode/描述詳盡欄位、原版背包容量與金額交換、物品取得掉落。具名現有資料 `Map0.dat/Map1.dat/Map2.dat/Born.dat` 沒有被證實涵蓋 item template；**無從證實單一真正物品定義 `*.dat` 的檔名，不能虛構需要上傳特定模板檔**。若能提供正式原服的 item resource index/catalog、Client 物品背包／卸裝／道具使用與地面拾放的封包記錄，能解除 unknown。A-013（交易、商店、倉庫）獨立研究仍 open。

### 重現

```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x577750 --stop-address=0x577944 Asgard.exe
objdump -D -M intel --start-address=0x585a10 --stop-address=0x585c55 Asgard.exe
objdump -D -M intel --start-address=0x57a3f0 --stop-address=0x57a850 Asgard.exe
objdump -D -M intel --start-address=0x579830 --stop-address=0x5799b9 Asgard.exe
objdump -D -M intel --start-address=0x571f40 --stop-address=0x572018 Asgard.exe
objdump -D -M intel --start-address=0x574a40 --stop-address=0x574afa Asgard.exe
python3 tools/a007_inventory_contract.py
```

檔案/完整 DAT bytes 不提交，僅交付位址/精簡特徵/合成 fixture。