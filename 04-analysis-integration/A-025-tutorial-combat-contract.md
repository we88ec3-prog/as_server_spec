# A-025 — 新手教學技能/攻擊與任務事件 Server 交接（observed-static + designed）

來源 [A-025 BIN-first](../03-analysis-requests/A-025-roy1-tutorial-combat.md)，原件 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，Evidence `ev_a025_20261031_attack_skill_bin_static`。

## 原生 Client 已確認

|C2S opcode|建構/序列化|body|Client 何時發送|
|---|---|---|---|
|0x13 CAttack|0x570A10 / 0x570AC0|BE u32 target ref|攻擊 UI 互動路徑 0x55709C / 0x557A5D 通過本地狀態/timer gate|
|0x4D CStartCastSpell|0x575510 / 0x5755C0|BE u16 spell value|0x401FB8..0x402052 讀選擇 [ebx+0x80e] 非零時|
|0x56 CCastSpell|0x571750 / 0x571800|u8 unknown|確定 writer，**尚無逐一對應使用者按鍵/完整 stage 的追鏈**|
|0x3D CBattle|0x5711B0 / 0x570DE0|u8 subtype(0..15)+分支欄位|變長多態，所有原生 subtype 未完整對照|

|S2C opcode|reader|body|
|---|---|---|
|0x52 SCastSpell|0x57D600|BE u32 opaque,u8 unknown result/state|
|0x5F SDieObjects|0x57E260|BE u32 opaque object ref；**不是 server quest kill ACK**|
|0x3D SBattle|0x57C890|u8 subtype0..15 + branch-specific body，需逐型補充|
|SAddLastingSpell 等|參照本輪報告|Client buff reader 存在；效果持續/傷害計算未證|

## World/Quest 安全管道（新 Server designed）

```text
AuthorizedCharacter + WorldReady + current WorldGeneration
  → CAttack / CStartCastSpell / CCastSpell / supported CBattle subtype
  → Server validates target identity, map/instance, alive, range/LOS,
     learned skill, resource, cooldown, tick and intent replay
  → CombatResolved(server_event_id, generation) authoritative
  → Project S3D/S52/S5F (only supported native layouts)
  → IF verified_tutorial_objective_mapping from original content/server evidence:
         unique objective_event ledger → progress transaction → optional response
    ELSE: no tutorial progress change
```

C13 包只有 target u32，不信任 Client 對傷害/擊殺/目標計數宣告；C4D 只有選擇的 u16，不足以推原服冷卻/耗魔；C56 一個 byte 不能作任意傷害命令。C3D/S3D subtype0..15 的合法性及每個 body 必須分別驗證；未知分支 deny，不做破壞性副作用。現有 Born.dat 只做引導，沒有可核對的教學殺怪目標；**不能從這一份 Script 推論整個教程不需要戰鬥，也不能擅自規定必須戰鬥**。

## 責任與測試

A-025 = `integrated/handoff partial`；已證 opcode codec / hostile input validation / designed objective once ledger 可交 DEV；`native_tutorial_combat_requirement_proven=false`、`quest_progress_ready=false`。原生戰鬥公式、合法技能列表與 status、怪物 spawn/object id、教學 quest objective 由 A-008/009/010/012/024/026 或原服封包/資源證據補證。CT-023/024/025 尚未 native E2E；CT-051/052/053 為 planned synthetic/native-replay 設計。離線核對工具：`tools/a025_tutorial_combat_model.py`，須以原始 `Asgard.exe` 比對 14 組 byte signature；在單純 synthetic 環境中沒有 EXE 時只能部分跳過，不能聲稱已重現原生證據。


## A-004 / roy1 更正（2026-10-31）

原版 `SDieObjects` 真正 constructor 是 `0x57e1b0`，在 `0x57e1c9` 將 opcode **0x5F** 傳 `0x578730`；reader `0x57e260` 仍是 BE u32 object_ref。先前把 factory `push0x1e` 誤當 opcode，已更正成 **S5F**（另有 S0E RemoveObjects）。死亡通知本身仍非原服 quest completion 證據。參照 [A-004](../03-analysis-requests/A-004-roy1-world-visibility.md)。
