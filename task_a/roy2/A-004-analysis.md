# A-004／roy2 — 多人入視野、移動同步與物件移除：原版 Client I/O

日期：2026-10-31；既有 branch/workdir：`task_a/roy2`（無新 branch）。分析原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，PE32 ImageBase `0x400000`。涉及 R-004、R-007、SCN-005；與 A-005 移動、A-006 外觀、A-024 非玩家物件相互參照。

## 結論與證據分級

**已直接驗證**：原 Client 存在顯示玩家 S33、帶 u32 物件識別欄的 S06/S11、移除 S0E、自己的移動回覆 S0B。5 個 S2C native constructor opcode、5 個 reader 序列經原始 PE 靜態重新執行探針 PASS。已知 S33 的 flags=0 常用欄位與 CP950 string8 profile；另有 C33/C11 客戶端移動/轉向已在專案 packet registry。**尚未證明**：S06/S11/S0E 的 u32 是否都被原生 ObjectRegistry 以同一 key 處理、角色離視野精確 trigger、原服視野半徑、重用 ID 和斷線後的實際網路事件順序。這些項目保留 `unknown`，不把 Server 設計當成觀察到的原服行為。

## 1. Trigger → Client 發送 → 接收 → Client 效果

|觸發與狀態|C→S|S→C 已證 decoded body|Client 可證/限制|
|---|---|---|---|
|角色已在世界/可見角色加入|無需 Client 先發特定 spawn 包；world entry C25/C35 屬另一階段|`S33 SPutHumanObjectPacket`：前綴 `x:BE u16,y:BE u16,facing:u8,object_id:BE u32`；之後外觀、flags、name:string8、profile 尾欄。flags=0、profile 無選配時 **42+name CP950 bytes**|parser `0x585570` 以固定順序讀到 packet 結構。完整非零 flags/原生 MapPane registry callback 尚未證實|
|本機玩家按鍵移動|`C33 Move`：u8 direction,u8 seq7,u8 gait_flags（既有 A-005）|`S0B SMovePacket`：BE u16,BE u16,u8|`0x583150` 接收 x/y/sequence/status；**沒有 u32 object id**，不能拿來當其他玩家的移動廣播|
|遠端人型移動事件（由類別名推得用途）|無需目標 Client 發包|`S06 SMoveHumanAckPacket`：BE u32,BE u16,BE u16|`0x5832D0` 讀取 8 bytes；u32 很可能是 object ID，但需 handler 核對；x/y 語意由類別/對比推定，不是逐 MapPane registry 實測|
|本機玩家面向變更|`C11 ChangeDir`：u8 direction（既有 A-005）|`S11 SChangeDirectionPacket`：BE u32,u8|`0x57D770` 讀取 5 bytes；第一欄很可能指向可見 object、第二欄是方向，但 handler 與範圍 policy 待證|
|角色離開可見集合/切圖/斷線|退出本身不保證有專屬 C2S；C33 位置改變/斷線是不同事件|`S0E SRemoveObjectsPacket`：BE u32|`0x585F10` 讀取 4 bytes；以類別名可判定移除物件事件，尚不能斷言只移除玩家、或其 u32 可重用規則|
|普通 NPC/怪物入視野、移動、死亡|Client 互動候選 C13/C43 見 A-024|`S07,S0C,S64,S5F,S0E` 見 A-024|**S33 是 PutHuman，S07 是多類物件**，不可將 S33 充當所有怪物 spawn；共用 S0E 類別並不證明所有 entity 的 registry 相同|

### native 位址與欄位來源（VA，非 file offset）

|類別 RTTI name VA|constructor/base opcode|vtable parser|解碼步驟|
|---|---|---|---|
|SPutHumanObject `0x669F78`|`0x5854D0` push `0x33`→`0x578730`|`0x585570`|`0x45ADE0,u16` ×2、`0x45ADB0,u8`、`0x45AEB0,u32`，後續 appearance/flags/string8 的 native 條件欄位|
|SMoveHumanAck `0x669E68`|`0x583220` push `0x06`→base|`0x5832D0`|`0x45AEB0` u32、`0x45ADE0` u16、`0x45ADE0` u16|
|SChangeDirection `0x669BA8`|`0x57D6C0` push `0x11`→base|`0x57D770`|`0x45AEB0` u32、`0x45ADB0` u8|
|SMove `0x669E4C`|`0x5830A0` push `0x0B`→base|`0x583150`|`0x45ADE0` u16 ×2、`0x45ADB0` u8；與 C33 序號回覆相對應|
|SRemoveObjects `0x66A038`|`0x585E60` push `0x0E`→base|`0x585F10`|`0x45AEB0` u32|

此 VA 表是以 MSVC RTTI TypeDescriptor→COL→vtable 及 ctor push opcode 追溯；原件 PE32 SHA 固定。**端序：網路多位元整數為 BE**。S33 外觀欄位及色彩以 [appearance.md](../../04-analysis-integration/appearance.md) 的 profile為準，非零 flags 不能直接使用目前簡化編碼器。

## 2. ID 生存期、視野範圍與 Server 介面：observed vs designed

**observed-static**：S33 的 body offset5..8 有 BE u32；S06/S11/S0E body 首 4 bytes 為 BE u32；S0B 自身移動回覆只有 5 bytes，沒有可用來指定別人的 u32。`S33` 名稱字串依 runtime codepage，此次固定測 CP950。對 S06/S11/S0E 跨封包同一 object_id 的 **registry 實際查找/同 id 刪除** 尚沒有完成 MapPane handler 追鏈；列為 inferred，不將欄位從『opaque u32』擅改為官方確認的 `object_id`。

**designed — Server 開發建議（不得表述成原服權威）**：
1. 以登入成功且 in-world 的 `WorldSession(character_id,connection_generation,map_instance,map_epoch)` 決定 sender；移動消息由 Server 做合法校驗。自己的位移回覆走 S0B，其他玩家可見時用有 ID 的 S33/S06/S11 子集，不要對所有觀眾重播無 ID 的 S0B。
2. 在特定 map_instance+epoch 定義 `VisibilitySet(observer, entity_runtime_id)`，只對新增集合送 S33，移動/方向送 S06/S11，離集合送 S0E。**可見半徑、形狀、裁切與心跳頻率皆待 DEV 自訂或 Native CT 驗證**；不得標原服已證。
3. `S33` 重送採同一 ID 的 idempotent refresh；S0E 去除 ID 後在該 epoch 暫時列入 tombstone，避免晚到 S33/S06 使已離視野角色復活。無 native wire generation 欄，若要同 epoch 重用 ID，先由 Server session+instance/epoch 歷史與 outbox 確認，不應假設 Client 能區分。
4. 切圖/斷線/重登入先清除舊 epoch 可見集合，丟棄舊 instance 的待發廣播；新 epoch 再依 world-ready 重新加入。不能以 C35 校驗成功代表其他玩家已收到 S33。死亡/移除與角色離視野為不同事件，是否同用 S0E 應再驗。
5. 需要至少兩個真正原生 Client 的 CT 才能確認遠端移動/面向、ID 後續查找、顯示與清除成功；目前未執行。原服『收到某個 opcode 必然渲染』沒有原生 GUI 驗收，故不能如此宣稱。

## 3. 可重現測試、負向情境和交接狀態

```
python task_a/roy2/a004_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a004_visibility.py' -v
```

原始 SHA256 核對，5 ctor/5 parser static probes **PASS**；9 synthetic tests **PASS**（S33 CP950/長度/flags、S06/S11/S0E/S0B、遠端入視野→位置/方向→離開、重送、舊 epoch/ID 重用、截斷與未知可選欄）。原生 Client E2E **not-run**；合成測試驗證的是 decoded-body/本 Server 設計，不是原服視野政策。

**A-004 交付**：已知 Client 封包/欄位可交給 Server DEV，與 A-024、A-005 的已知邊界相容。完整 native callback registry、S06/S11/S0E 跨包同 ID 的實際處理、視野觸發的精確 Client 畫面仍須 CT-visibility/後續 BIN 補驗。`status=integrated / handoff_status=partial / native_client_validation=not-run` 是不混淆證據的狀態。缺的不是素材檔，而是**同版 Client 實際雙角色視野事件 trace 或對應 MapPane handler 的深入靜態交叉引用**。本次不需新增任何使用者資源檔。
