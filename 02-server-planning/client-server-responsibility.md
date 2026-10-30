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
