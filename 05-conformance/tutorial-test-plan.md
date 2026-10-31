# CT-021～028 教學玩法/完成驗收計畫

適用原生台灣版 Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。下列均為 planned、未執行，wire 必須等 A-024～026 補證。

|CT|測試與預期|前置|
|---|---|---|
|CT-021|同一 scene 重入/重連不重複生成 NPC/怪物，物件與可見性正確|A-022/A-024|
|CT-022|NPC/怪物行動、死亡、回收、斷線不留幽靈物件|A-004/A-024|
|CT-023|技能非法目標/距離/冷卻/資源不足不可成功也不計目標|A-010/A-025|
|CT-024|合法技能/戰鬥、傷害及死亡依原版 UI / Server 狀態一致|A-008～010/A-025|
|CT-025|同一合法事件重送、亂序、跨 session 不重複計進度|A-012/A-025|
|CT-026|目標未達成不能完成；成功後獎勵若存在僅一次|A-012/A-026|
|CT-027|完成教學轉入原版合法目的地，切圖失敗或重登一致|A-016/A-026|
|CT-028|原版 Client 完整「首次登入→教學互動→完成→離開」實測|A-021～026|

若 A-025 證實教程不要求技能/戰鬥，應修正本 profile 的實際目標與 CT，不得硬造原生玩法。Server unit/integration 和原 Client 人工實測分開保留證據，不因 CT 規劃存在宣稱通過。

## CT-055 新增：多人進同一張地圖（planned/not-run）

使用兩名**不同登入帳號/角色** A/B 進同 world/map：期望同一 instance/EntityId 的 NPC/Monster、A 與 B 在 AOI 內互見；死亡和重生只發生一次並由兩人看見；A 斷線不消除 B 的怪物；新玩家 C 加入取得最新 Snapshot、不回放舊 Spawn；不同地圖不共享。同一角色舊 Session 的離開事件不影響新 Generation。先做 Domain synthetic tests，原 Client 互見待 A-004/011/024 提供 wire；**本輪沒有完成原生 CT-021/022/055**。詳見 [完整驗收表](shared-map-multiplayer-test-plan.md)。

## 合併後 CT-056～081 來源註記

Roy1 新 CT-056～069（登入分支/戰鬥/教學完成/物品/音樂）及 Roy2 新 CT-070～081（雙玩家 AOI/移動/外觀/狀態/戰鬥/NPC）已納入 `vectors.json`，原來源編號見 [映射](ct-id-remap-roy1-roy2.md)。S07(kind1..14) 已有 Native BIN-first decoded-body schema，**不能因此標實機 CT-081 passed**。另外 Roy1 曾把 DieObjects 當 S1E，需先釐清與 S5F 的反組譯歸屬，不能在 Native 場景發兩種猜測的死亡包。
