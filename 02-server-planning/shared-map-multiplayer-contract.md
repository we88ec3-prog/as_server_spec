# ADR-007 — 多人進同一張地圖、共享 NPC 與怪物（2026-10-31）

**決策來源：使用者明確選擇「多人進同一地圖」。** 此決策適用新手教學及一般共用世界地圖；**不使用每個角色各自隔離的場景作正式模式**。這是新 Server 的 designed 規則，不聲稱原服的所有分流/副本政策已知。

## 玩家看到的行為

1. 玩家 A、B 進入同一世界（realm/world）及同一地圖時，會共處**同一個共享場景**，在彼此可見範圍內可看見對方、同一組 NPC 與同一隻怪物。NPC/怪物不因新玩家登入而各自生成一份。
2. A 殺死/移走一隻怪物，B 立即經由**同一權威世界事件**看到死亡或消失；重生也只發生一次。旁觀者新加入會取得當前世界狀態，不會看到已死亡怪物的舊身影。
3. A 離開／斷線／換線／換圖，只移除 A 的 participant 和觀察狀態，B 的場景/AI/怪物不中斷。最後玩家離開後，世界場景可依 Server lifecycle 策略待命或卸載；**不可因任一玩家離線就立刻重置其他人的怪物**。
4. 玩家自身的任務進度、角色資料、初始獎勵仍按 `character_id` 分開記錄；怪物共享不代表擊殺歸屬、獎勵一定共用。協助擊殺/經驗/掉落歸屬、組隊規則未有使用者決策／原生 Client 證據，先保留 policy hook，不猜值或開放正式發獎。
5. 本期世界模型只有**每個 world + map 一個公用場景**；不因 `CharacterId` 創建副本。未來若為擁塞/特殊副本新增 channel/instance 類型，須另行取得需求決策並確認原版 Client 能理解分流；本次不暗中建立多個同圖副本。

## 共享場景鍵與版本

- 主要公用場景鍵 `SharedMapKey(world_id,map_ref)`。同一鍵的 `content_revision` 必須一致；第二個玩家若持有不同資源修訂版，拒絕進場或走明確的版本協商／重新載圖流程，**不得悄悄按版本建立私人場景**。
- `SharedSceneInstance` 持有 NPC/Monster Actor Registry、Server EntityId、生命代次、生死/移動/AI 狀態與有序世界事件（單地圖 sequencer）；每個 `SpawnKey`、instance 只生成一次，死亡後重生產生新 `life_generation`。
- `PlayerParticipant` 由 `character_id + account_id + world_session_generation + connection_id` 驗證；重連同角色以最新合法 World lease 替換，舊 socket/logout/timer/event 無權影響新 lease 或其他參與者。
- 觀察者 `PlayerVisibilityState` 按每個玩家維持 observed entity versions、加入/離開事件；只有 Server 驗證過的 World Ready/移動位置能更新權威玩家座標。**讀取可見性 `Observe` 不得同時寫入玩家座標**。
- 針對玩家 A/B 的生存或移動，廣播只投遞兩人/怪物在合法 AOI 的差異，而非全世界資料。每個 Client 的 Spawn/Move/Death/Despawn 包轉換必須等 A-004/A-011/A-024 確認；目前僅內部 `SceneChange` 合成模型，**不新增猜測的原版 opcode**。

## DEV-070 既有實作差距與遷移

`as_server_roy@3a9d5b7` DEV-070 已有 1Hz synthetic actor、Scene Actor 狀態、單角色 World lease fencing、DB commit 後才 Activate、Development 限定 mock 和自動化測試；**但 `TutorialSceneRuntime._scenes` 以 CharacterId 作鍵，`Activate` 每名角色建新 actors，`Observe` 會寫 `PlayerPosition`，因此不符合本決策**。後續 DEV-070-M 是既有 DEV-070 的多人修正批次，不另開任何 Git branch：

1. 將 `_scenes` 改按 `SharedMapKey` 建立；參與者表以 `CharacterId` 查目前有效 Session/Scene；`Join`/重連 idempotent，只有**第一個合法玩家**建立地圖 Actor。
2. `Leave`／同玩家舊連線收尾僅移除符合 lease 的 participant；場景其他玩家繼續 Tick。換圖從舊場景除名、在新地圖 commit 後再 Join。
3. 將 `Observe` 拆為只讀/更新 observer cache，與權威位置 `CommitValidatedMove` 分離；不可讓未驗位置或 client 自報 NPC/HP 更動世界。
4. 地圖事件序號單調、Actor `EntityId + life_generation` 不重用歧義，雙玩家各自觀察同一 actor 狀態；重連補完整 snapshot 或有序 delta，不顯示 ghost。
5. 內部 Scene aggregate 原子序列化 Tick、Join/Leave、Death/Respawn、AOI delta；採有限 queue/backpressure/CPU 限額的可觀測 Server 策略。死亡、掉落、任務每角色 ledger 留 DEV-080/090。
6. 開發期保留「Development explicit synthetic fixture only」限制；正式世界直到資源/碰撞和 Client wire 已有證據才開啟。部署已使用的單人測試不等於正式多人驗收。

## 具體驗收與需要的 A

- **CT-055**：同 world/map 的 A/B 共享同一 instance id、同一 NPC/monster Actor id+life；A 的死亡事件 B 可見、A disconnect 不刪 B 的場景；重新加入和跨 generation 依然只有一份 Actor。先跑 Server synthetic；原始 Client 實機雙人互見仍 `not-run`。
- 既有 **CT-021/022** 更新 shared-monster 與 reconnect 測試期望，**CT-007/008** 外觀欄位不可代替實體生命周期。
- **A-004**：玩家 A/B 的 S→C spawn/move/despawn、可視範圍及 ID 生命週期。
- **A-011/A-024**：NPC/怪物的 S→C spawn/move/death/despawn 與 Click NPC 的 C→S，Client 渲染/資源 ID。**不要求分析 Server 仇恨公式或固定重生數值**。
- **A-005/A-022**：原 Client 移動及地圖載入/位置封包，如何讓 AOI 用可信 Server 位置；地圖/碰撞實際格式仍按 A-015 子集核對。
- **A-025/A-026**：技能傷害與任務進度事件；共享怪死亡但每人獎勵/任務如何判定，屬 Server designed，待需求後再定具體受益規則。
- **原件現況**：已提供 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat`；追 NPC 外觀缺檔時，先由 A-011/A-024 確認**精確資源檔名**，不猜檔名。Script UI 依賴已知 `PaperDialog.dat`。

**狀態：design-approved / Server refactor planned / native-client-validation not-run。**
