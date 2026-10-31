# CT-055 — 共享地圖的雙玩家驗收規劃

本期**先 Domain 合成測試**：原版 Client 的 A-004/A-011/A-024 實體封包未證，不能把內部 SceneChange 假扮 native packet。原 Client 不修改，真正雙 Client 驗收仍 `not-run`。

|條件|預期結果|
|---|---|
|A、B 不同帳號/角色、相同 world/map/revision|只建立**一份** SharedMap Instance、一組 SpawnKey/Actor 與一次 Tick；兩個 Participant/Observer|
|A、B 彼此靠近並進出視野|兩個玩家互見；Observer 維護各自已發 EntityId/Version，差異 Spawn/Despawn 可重送安全|
|A 對同一隻怪造成有效死亡、B 旁觀|怪物只有一次 Death/Removed/Respawn；兩位看到相同 ActorId/生命代次及相同世界事件序號|
|A logout，B 留在地圖|A 自己的 participant/visibility 清掉，B/怪物/AI 不重置；舊 generation 的 A cleanup 不清新 A 或 B|
|C 在怪死後 Join|立即拿**當前**世界 Snapshot；死亡中不得看到舊 Alive，重生生命代次遞增|
|A、B 不同 map|獨立 Scene/Actor Registry，不互相廣播；移圖後舊 observer 完整回收|
|同 world/map 但 content revision 不同|拒絕或明確協商資源版本；不得不透明創建第二個同圖私人 instance|
|角色 A 新登入後老 C10/logout/packet 到達|舊事件沒有權限修改新 PlayerParticipant，更不能更動 B 的共享場景|
|玩家移動但尚未經 Server 驗證|禁止更動權威座標／怪物 Aggro；Observe 查詢不得隱式寫入 PlayerPosition|
|多角色同時 Join/Leave/MarkDead/Tick|單 Actor 版本序列化、無重複 Spawn/重複 reward /幽靈玩家；壓力下 Event queue 有界且可觀測|

**Client E2E 的獨立出場**：在兩份原始 `Asgard.exe` 確認 A/B 互見、NPC/怪物同一顯示、死亡/重生及斷線、移圖，逐包保存 direction/opcode/body hash 與畫面；**未有 A-004/A-011/A-024 的 S→C/C→S layout 前不得假造封包**。個人 quest credit/loot/XP 尚無規則，不做成功測試聲明。
