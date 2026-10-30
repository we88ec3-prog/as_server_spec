# 首次玩家 CT-011～020 測試計畫

這些都是 **planned**，尚未執行；未經 A-021/A-022 證實的原生 wire/status/教學 map 值不得編造成成功向量。

|ID|測試及預期|前置或阻塞|
|---|---|---|
|CT-011|非法會話直接 C02/C04/C25，資料與 World 不變|Domain 可測；Client 拒絕形式待 A-021|
|CT-012|同名或同帳號並發，只產生單個有效角色|DB / Domain|
|CT-013|C02 後 C04 前斷線不留可進 World 的半角色|Domain；Client 時序待 A-021|
|CT-014|C04 成功但回包遺失重送，角色不複製|Domain；UI 回應待 A-021|
|CT-015|過期/跨帳號角色/重用/舊 generation token 拒絕|Auth integration|
|CT-016|S02/S05/S15/S14(1)/C35/S04/S33/S14(2) 順序正確，loading 中不可操作|一般已知 profile；教程圖待 A-022|
|CT-017|C35 前後 crash/重連不留幽靈 World 或誤寫教學完成|恢復分支待 A-022|
|CT-018|原生 Client 首次在已證據確認的教學地圖出生且可操作|**必須 A-021/A-022 + 原版 Client 實測**|
|CT-019|無權管理/Client 建帳被拒絕，錯密/停權不能取得 grant|Server / Admin integration|
|CT-020|非法 profile、錯誤順序及未知分支不得冒充 success|Server unit/integration|

每次結果要記 Client SHA、Server revision、測試環境、輸入（去秘密）、期待/實際、通過/失敗、時間、證據與未解問題。Server 自動測試通過與 Client 人工通過是兩件事。未取得原生欄位證據前，vectors.json 使用 planned 狀態而非可執行的 byte-exact 成功值。

## A-021 / roy1 靜態補充（2026-10-31；**未執行 Client 驗收**）

請參閱 [逐位址分析](../03-analysis-requests/A-021-roy1-static-analysis.md) 和 [協定子集](../04-analysis-integration/A-021-native-flow.md)。現可用合成輸入為 `C02 016101620163016401`（region2..4）、`C02 016101620163`（其他 region）、`C04 0102112233`、`S02 0000`。**body only**、只檢查 parser/serializer 形狀，非原 Client 封包擷取；它們不能直接把 CT-011..014 標 passed。

原 Client 必須額外核對以下測點：C03 已存在無角帳號是否開啟原生創角 UI、C02 4 欄 UI 語意、C02/S02/C04 的所有成功失敗/取消分支、C04 後是直接 transfer 或重新登入、網路重送/並發/斷線原生效果，以及任何 Client 發起新帳號的要求都不會讓 Server 建立 Account。沒有完整資源/可執行測服與去識別動態 trace，A-021 仍為 blocked。
