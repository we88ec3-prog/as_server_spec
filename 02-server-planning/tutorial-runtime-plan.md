# 教學執行規劃：從入圖到完成（ONB-05～06）

日期：2026-10-31。對象：台灣版 Asgard 原 Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，profile `TW-seed0-local-v0.1`。本文件屬 **designed**；沒有來源的原生封包、map ID、角色技能、怪物、NPC、任務與獎勵均 **unknown**。

## 與既有流程的邊界

ONB-01～04：管理員預建帳號 → Client 登入 → 創角 → World 交接 → 教學地圖可操作 → 故障恢復。
ONB-05：教學地圖 NPC/怪物生成、行動、技能/攻擊、任務目標。
ONB-06：達成真正教學完成條件、一次性狀態/獎勵（若存在）及離開教學轉往普通地圖。
不得因 C35 成功或完成首次進圖，就寫 `tutorial_completed`；`tutorial_entry_committed` 是不同欄位。

## ONB-05A：NPC／怪物內容與世界狀態（R-029）

邏輯資料：`TutorialContentRevision`（profile / origin / checksum / confidence）、`SpawnDefinition`（scene / actor_kind / resource_id / position / trigger / respawn policy）、`WorldEntity`（instance_id / entity_id / generation / position / facing / lifecycle）、`MonsterBehaviorState`（current action / target / cooldown / wakeup）。

1. 初始地圖內容須來自版本化並已驗證的資源；不使用本機測試座標冒充官方原版。
2. 單一地圖 instance 的 spawn 由 Server 權威裁定；同一 spawn definition+instance generation 不重複生成。Client 只收到合法可見物件。
3. 抽象 AI 狀態 idle / patrol / acquire / pursue / attack / dead / removed 僅作可替換架構；實際遊戲是否存在、速度、仇恨、tick、動畫與封包必須由 A-024 確認。
4. 移圖、死亡、清除、斷線、重啟後回收 stale actor；舊 generation 事件不得操作新 instance。AI 計算不得阻塞 transport。
5. 缺資源或未知 schema 不應偷偷生假怪；標示 blocked 並輸出不含隱私/機密的診斷。

## ONB-05B：技能／戰鬥與教學目標（R-030）

邏輯命令：`CastIntent` / `AttackIntent` → `ValidateActorAndTarget` → `ResolveAbility` / `ResolveCombat` → `UpdateObjective`。這些 **不是**原 Client opcode。

- Session、角色生存、目標存在且屬可互動世界、距離、資源、冷卻、施法中斷由 Server 裁定；Client 的傷害值或任務完成聲稱不是權威。
- 有效行為才更新目標計數；用 event identity / objective version 去重，不能因封包重送、同場景多玩家或重連加倍計數。
- 公式、ID、技能動畫與效果更新若未知，必須明示暫不相容；自訂規則只能放在清楚標記的自訂 profile。
- 若 A-025 證明原版教程不要求技能/戰鬥，應按證據修正教程實例要求，而非強迫使用非原版功能。

## ONB-06：教學完成與出口（R-031）

資料：`TutorialProgress(character_id, content_version, step, objectives, version)`、`TutorialCompletionLedger`、可選 `RewardGrantLedger`。

1. 教學步驟、NPC 對話、獎勵與完成條件須有 A-026 的 Client/Script/資源證據；不預設固定擊殺數、道具或官方獎勵。
2. 每次進度更新驗證目前合法步驟；完成轉移與任何原生獎勵在原子提交/等價可靠交易後才回成功。重送完成不能再領。
3. 目的地地圖、位置與切圖順序必須確認，否則不能將自訂跳圖宣稱官方相容。失敗、逾時、重登入依持久化事實恢復。
4. 原生是否支持跳過教學也屬未知，不能新增未確認的 Client 按鈕/封包。

## 出場標準

先完成 A-021/A-022 保證能建立角色並進入原版教學，再由 A-023/A-024/A-025/A-026 建立各功能的 PKT/SCN/CT。SCN-011～013 與 CT-021～028 只是在此版本規劃；全部新情境尚未原生 Client 驗收。
