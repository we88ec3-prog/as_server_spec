# A-025 / roy1 — 新手教學首次技能、攻擊、效果與任務目標事件（BIN-first）

- 日期：2026-10-31；分支：既有 `task_a/roy1`，無新 branch。
- Client：使用者提供的原始 `Asgard.exe`，PE32 I386 3,235,840 bytes，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；ImageBase `0x400000`。
- 資源：本地 `Born.dat` SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`，zlib 解包 1,154 bytes（6-byte header + UTF-16LE Script XML）。
- 證據 `ev_a025_20261031_attack_skill_bin_static`。方法：原始 EXE `objdump -D -M intel`、packet constructor 的 opcode 與 vtable/UTF-16 file path 雙重確認、writer/reader 確定欄位；讀 Born XML 的 function tags/內容對照 A-023；本地以原始 EXE 的 14 組 byte signatures + 7 個 Python unittest 驗證 codec/safe Domain。未運行原 Client、原 Server 或教學戰鬥流程。
- 任務狀態：`integrated / handoff_status=partial / native_client_validation=not-run`。可供獨立實作的範圍 **只有已證實的 packet codec/sender gate 與明示 designed 的戰鬥驗證和事件去重骨架**；`native_tutorial_combat_requirement_proven=false`，`native_quest_progress_mapping_ready=false`，不能說新手教學原版一定要求攻擊。

## 1. Client **會做什麼事**，才送出封包？

|原版 VA|原生動作與可證字段|Client vs Server 界線|
|---|---|---|
|`0x55709c→0x5570b7`|`CAttack` ctor `0x570A10` 建 opcode **0x13**；從 Client 互動傳入的 dword 參數 `edi` 寫入 packet+0x24（writer 子物件偏移+0x18）；接著 `0x5788A0` 送出|Client 顯示／對象操作可導致 **C13 u32_be opaque target reference**；不能由此保證是可攻擊怪物或有命中|
|`0x557A0F..0x557A78`|另一個 CAttack 發送路徑，同樣把 `ebx` 參數放 packet+0x24 送出|至少兩個 Client 互動 callsite；A-025 不把兩者誤當兩個 opcode|
|`0x556FB3..0x55706B`、`0x557A0A..0x557A2B`|Client 送 C13 前有本地物件狀態位元、時間讀取 `0x402C30`、選擇狀態 `[user+0x544]`、本地 `word [selected+0x15] + [user+0x528]` 和 current time 比較|能證明「有本地節流／狀態 gate」，**不能從這些比較推論原服冷卻毫秒數、命中範圍或消耗**|
|`0x401FB8..0x402052`|選取物件 `[ebx+0x80e]` 為非零時，`CStartCastSpell` ctor `0x575510` opcode **0x4D**；`word [ebx+0x80e]` 寫 packet+0x24，`0x5788A0` 發出|原 Client 的某個技能/選擇 UI 會發 **C4D u16_be spell value**，但實際 legal spell IDs 未證|
|`0x571750/0x571800`|原生 `CCastSpell` ctor opcode **0x56**，writer **u8**；與 C4D 為不同型別/不同 packet|不能直接把 C56 這個 byte 命名成技能 ID／目標 ID／傷害值，且尚未追通每個 C56 真實 UI sender 的先後條件|
|`0x5711CB/0x570DE0`|原生 `CBattle` ctor opcode **0x3D**；writer 第一欄 `u8 subtype`，原始 `cmp subtype,0xf` + 跳表分支 0..15，不同分支可見 u8/string8/u32 等|**C3D 是變長多型封包**，不能把某一分支當成所有戰鬥/任務確認；部分 subtype 的語義仍需 A-009/010|
|`0x57C6EC/0x57C8BA..0x57C8D1`|原生 `SBattle` ctor opcode **0x3D**；reader 第一欄 u8 subtype、`cmp 0x0f` 跳表|S3D 也是多型回覆；可見不同解析分支，不代表每包都算傷害或教學進度|

**線上 body 定義：** `C13 = BE u32`，`C4D = BE u16`，`C56 = u8`，`C3D/S3D = u8 subtype + variant-specific fields (partial)`。這些 body 不含 opcode、binary ordinal、加密及 AA frame。opcode 名稱與 original RTTI 之間以 constructor 確認，而不是僅依 class 文件名稱猜測。

## 2. Server 哪些回覆會被 Client 接收？

|VA|封包/讀取|實際能證明|
|---|---|---|
|`0x57D569/0x57D600..0x57D616`|`SCastSpell` opcode **0x52**，reader `u32_be opaque_ref,u8 state_or_result`|可提供技能相關 Client 呈現/狀態輸入；第二欄的確切 enum、哪個結果才算成功 **unknown**|
|`0x57E049/0x57E260..0x57E26C`|`SDieObjects` opcode **0x1E**，reader `u32_be opaque_ref`|Client 能收到物件死亡/消失候選事件；**不等於已證原服擊殺判定／任務計數成功**|
|`0x57C6EC/0x57C890..0x57CD98`|`SBattle` opcode **0x3D**，讀 subtype0..15 有多種 layout；有 list/string、數值等不同分支|需要對具體 subtype 各自反編碼、映射 UI/effect/status；不可套用單一「戰鬥成功」格式|
|`0x57A980..`|`SAddLastingSpell` 原生 parser 包含 u32、u8、u16、u8、string8 等欄位|有持續效果/狀態相關路徑；原服 buff 疊加/時間/消耗未由此證明|
|A-023 的 `S44(1,0)` 與 `C6C(1/2/4)`|腳本啟動與回覆/關閉是獨立通道|**Script lifecycle 不是擊殺或任務進度 ACK**，不能把 C6C4/2 當 combat objective 完成|

本輪明確只把 S52、S5F 做成有保證欄位的合成 fixture；**S3D** 剩餘 subtype 欄位尚無完整實例，保持 `layout_status=partial`，不能宣稱所有戰鬥結果可直接出成完整 packet。

## 3. 「新手教學一定需要攻擊嗎？」：沒有證據，不能硬填

已核對 `Born.dat` 的 zlib+UTF-16LE Script XML（與 A-023 的 SHA 相同），它以 `Born.Main` 顯示 PaperDialog 紙張引導，提示玩家前往 **(31,29) 找女性招募員**。這是**路線/對話引導，不是 spawn、不含原版 NPC entity ID、不包含技能施放、攻擊、命中、擊殺計數或獎勵解鎖的明確條件**。它沒有 Script 內的 attack/quest API 呼叫可證「必須殺怪」。

此負面結果**只能證明 Born 這一份引導資源不要求攻擊**，不能推論整個原服教程都不需要戰鬥；其他教學 NPC/Script、原服任務旗標、首次/返程登入與觸發條件仍需 A-024、A-012、A-026 或原服 trace。不能將名稱近似的 `nNewJoin01.dat` 自動當招募員完整任務映射。因為 `SCN-012` 的原始必需性未證，只有條件式戰鬥規格；玩家未戰鬥不能自動判教學未完成，反過來每次 C13 發出也不能直接加任務進度。

## 4. Server 設計合約（designed，不冒充原服公式）

1. **C13 攻擊意圖**：必須有登入驗證與當前 World session/generation、有效的角色/目標 object ref、同 map/instance、角色/目標 alive、距離/LOS 權威、能攻擊、同時 AI tick 狀態；攻擊速率、時間門檻由 Server 自己的已明示設定驗證。Client 本地 timer gate 不能替代 Server 檢查。
2. **C4D/C56 施法意圖與階段**：C4D 是 u16 spell value、C56 u8 parameter（原生目的未解）；只有對角色合法/解鎖的 spell catalog、MP/資源、冷卻、目標與相關 phase 明確驗證後才可建立 spell instance。**在原版 C56 對應行為不明時，不開放其未知語義直接產生傷害或領獎**。
3. **C3D/S3D 多型**：根據已完成具體 subtype schema 各自分派，未知或不支援 type fail closed；不可把 raw u8 低位當傷害/任務進度。避免任意 variant 造成長度溢位、資產增加或重放漏洞。
4. **提交順序**：Client C13/C4D/C56 是「意圖」；只有 Server World 經過權威判定並**提交**一筆可追溯 `CombatResolved`（成功命中/治療/效果/擊殺中具原服證據的那類）事件，才允許產生回覆 S3D/S52/S5F 及必要的角色/目標狀態投影；S5F 的到來本身不是 Client→Server 任務請領。
5. **QuestObjective 只能在有** `verified_objective_mapping` **時更新**：`character_id,quest_id,objective_id,monster_instance,server_event_id,world_generation` 必須由 Server 內部一對一驗證；建立 unique `(objective_id,server_event_id)` ledger，任務/獎勵/outbox 原子提交，同一 event 重送/Client 回覆遺失/跨重登入不得再加。**這是 designed policy，不是原服欄位**。
6. **不能把 local tutorial 直接綁到擊殺**：A-024 確認首怪 entity/map/spawn、A-009/010 確認對應戰鬥/技能 event、A-012/026 確認原始任務條件之前，`verified_objective_mapping=false`；合法攻擊也不增加教學目標。
7. 狀態中止：角色死亡、跨 map、loading epoch 變動、目標被其他人移除、取消施法、資源不足、距離/冷卻不足、不同 session generation 均不得錯誤產生 HP/MP 副作用與 quest progress；實際原生 error/result code 待後續取證，不能用自訂數值偽稱遊戲原服。

## 5. CT 與 A-025 的完成邊界

- `tools/a025_tutorial_combat_model.py`：對原始 EXE 的 **14 組 byte signatures** 核對 opcode、writer/reader、Battle selector；7 項 unittest 覆蓋 C13/C4D/C56 bytes、S52/S5F reader、bad target/cooldown/resources/replay、相同 event 只加一次、SQLite reopen 與**未經證明的教程目標永遠不加**。
- `CT-051`：C13/C4D/C56 與 S52/S5F 逐欄 synthetic/原版 signature。
- `CT-052`：C3D/S3D 多態 branch0..15 严格分流 + unknown subtypes 拒絕、保持 partial 不生成假成功；後續按原 Client capture 追加每類 fixture。
- `CT-053`：攻擊/技能合法性、非法目標/距離/冷卻/資源及 duplicate event/跨 generation/SQLite crash replay，未有 objective 證據不可加 tutorial progress。
- 既有 `CT-023/024/025` 維持 `planned/native_client_validation=not-run`；新增 static refs 與安全測試條件，不能把**合成** Domain 測試當 native Client 戰鬥畫面已通過。

**最終裁定**：A-025 已完成可取得的 Client BIN-first 攻擊/技能入口、封包型別及首份 Born Script 不要求戰鬥的限定結論，因原版教學目標、NPC 互動、戰鬥公式/全部 subtype 的本服證據仍無法由原始 Client 推出，故 `integrated/partial`，`implementation_ready=true` 限 codec/domain safe skeleton，`native_tutorial_combat_requirement_proven=false`、`quest_progress_ready=false`。依 A-EVIDENCE-HANDOFF-v1 的 A 交付規範不用等 DEV/Client E2E，但不得冒充任務完整相容。

## 6. 重現與精準缺件

```sh
sha256sum Asgard.exe Born.dat
objdump -D -M intel --start-address=0x570a10 --stop-address=0x570ae0 Asgard.exe
objdump -D -M intel --start-address=0x556f80 --stop-address=0x5570c0 Asgard.exe
objdump -D -M intel --start-address=0x5579f0 --stop-address=0x557a80 Asgard.exe
objdump -D -M intel --start-address=0x575510 --stop-address=0x5755d0 Asgard.exe
objdump -D -M intel --start-address=0x571750 --stop-address=0x571810 Asgard.exe
objdump -D -M intel --start-address=0x570de0 --stop-address=0x570f3c Asgard.exe
objdump -D -M intel --start-address=0x57c6d0 --stop-address=0x57cdda Asgard.exe
objdump -D -M intel --start-address=0x57d550 --stop-address=0x57d620 Asgard.exe
objdump -D -M intel --start-address=0x57e1b0 --stop-address=0x57e270 Asgard.exe
python3 tools/a025_tutorial_combat_model.py
```

**仍欠的具名材料**：`PaperDialog.dat`（此執行環境未掛載，但 A-023 roy2 已在 Git 有 hash/Script 依賴解析；不重做其已驗的內容）、原版教學 NPC/怪物/任務定義的**實際檔名尚未從現有 EXE/Born 確認**，及原服登入→任務目標達成前後的 C/S 封包/事件 trace 或 Server handler/config。不可憑猜測給出不存在的 NPC/Quest `*.dat` 檔名；原版 Asgard.exe/Born.dat/Map0～2 已具備，不重新索取。


## A-004 / roy1 更正（2026-10-31）

原版 `SDieObjects` 真正 constructor 是 `0x57e1b0`，在 `0x57e1c9` 將 opcode **0x5F** 傳 `0x578730`；reader `0x57e260` 仍是 BE u32 object_ref。先前把 factory `push0x1e` 誤當 opcode，已更正成 **S5F**（另有 S0E RemoveObjects）。死亡通知本身仍非原服 quest completion 證據。參照 [A-004](../03-analysis-requests/A-004-roy1-world-visibility.md)。
