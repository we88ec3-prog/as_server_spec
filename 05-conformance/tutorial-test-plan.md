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

## A-025 靜態已證的戰鬥/技能接口與仍未證的教學必需性

來源 [原生函式核查](../03-analysis-requests/A-025-roy1-tutorial-combat.md)，已用 14 組 EXE byte signatures / 7 項 Python unittest 做 **離線** 確認：
- CT-051 planned：C13 `u32BE`、C4D `u16BE`、C56 `u8`、S52 `u32BE+u8`、S1E `u32BE`；驗截斷、拒絕非法欄位，原 Client 仍 not-run。
- CT-052 planned：C3D/S3D 的第一個 `u8 subtype0..15` 和 variant-dependent wire；完整 subtype schema 未證，不得先假造 battle success。
- CT-053 planned：Server 不信任 Client 傷害/kill；任何非法目標、跨世代、距離/資源/冷卻失敗不計進度。已驗證 objective 的同一 server_event_id 無論重送/SQLite 重啟只計一次；**未驗證原服需求時即使合法攻擊也不計 tutorial progress**。
既有 CT-023/024/025 仍 planned、native Client E2E not-run。Born.dat 是招募員 PaperDialog，不包含已證戰鬥必須條件，但不排除未知後續 Script。教學是不是必須打怪必須由 A-024、A-012/026 或 original-server capture 決定。
