# Client 與 Server 責任分界（原生相容）

|問題|A-XX Client 分析|Server DEV 決策|
|---|---|---|
|預建帳號／創角|C03/C02 UI 觸發、string8 fields、S02→C04/C15 UI/state|Admin 建帳、帳密/停權/owner、角色唯一性、DB commit|
|新角色進圖|S15/S14 如何控制 Map 載入、C35 核對、S04/S33 渲染坐標|選 map_id、spawn(x,y,heading)、版本與 checksum、World instance|
|教學開始|S44 Script start、Main、資源缺件 C6C(0)、視窗關閉 C6C(4/2)|何時送 Born、任務/旗標/NPC/獎勵的條件|
|NPC/戰鬥|點擊/技能 UI 發什麼包、收到哪些物件/動作/傷害包|怪物生成、AI、判定、傷害及任務計數|
|斷線|Client 收包與重新連線實際行為|Session/Grant TTL、一致性、冪等、持久層恢復|

**不是放棄相容性**：即使 Server 自行選出生點或任務時機，傳給原版 Client 的 opcode、欄位、CRC 與先後狀態仍要符合 Client parser；不能自行加欄位或填假的成功碼。A 只交付 Client 可證行為，Server 設計補足權威決策，CT 最後測原 Client 能否操作。例：C02 字串不能構成安全 owner 證明是 DEV 必守規則，但無需分析者推測原服資料庫憑證演算法。

[Client I/O 分析規範](../03-analysis-requests/client-io-handoff-standard.md)。

## 2026-11-01 ADR-008：成功建角直接進遊戲（覆蓋舊推定）

**使用者明確確認：創角成功後不回登入畫面、不需要再手動 C03，而是由原版 Client 直接進入遊戲世界。** 本檔早期「創角後回登入」「從 LoginDialog 再認證」僅是過時假設，不再作為 Server 實作或 CT 驗收標準；後續由 A-028 的 C04 final S02 callback `0x4b206b` 與 A-031 的新角色原生 World 轉場封包研究確定安全的 post-create authorization、socket 與 Client 需要的 S2C。日後已存在角色的普通登入 C03/S03/C10 保留，與首次創角分開驗證。參閱 [ADR-008](post-create-direct-world-decision-20261101.md)。原版 GUI E2E 仍為 not-run。
