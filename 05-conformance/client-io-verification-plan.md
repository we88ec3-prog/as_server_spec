# Client I/O 合約分段驗收計畫（DEV fixtures 與 CT 原生測試分離）

|階段|如何做合成/codec 測試（DEV）|原 Client CT/目前尚未驗證|
|---|---|---|
|FLOW-LOGIN|C03 字串長度/CP950、帳密失敗拒絕；S03 地址、port、token_len 編解碼|CT-019/037/038；S02 任意錯誤碼不當成原服原義|
|FLOW-NEWUSER|C02 region variant、UI 0x1d→0x1e、C04 五 u8/十色表、C15 零 body、C02 不得無 owner claim|CT-029～032/041～044/052～053；**C03 無角→NewUser native UI 尚未知**|
|FLOW-TRANSFER|S03 發 opaque token → 另一個 TCP C10 raw token，一次性 Grant，先斷登入 TCP 不踢掉合法 grant|CT-037/038/045/046；原 Client socket behavior 尚須實測|
|FLOW-MAP|對一張經可追溯版本配對的 MAP 產生 C35 預期兩 u16；含錯序/錯版/重送|CT-016～018/039/040；選 map/spawn 是 Server 設計，不是 Client A 要查原服政策|
|FLOW-SCRIPT|隔離環境 S44(1,0)/S44(1,1) + C6C(0/4/2)；close 不寫 QuestCompleted|CT-033～035；禁送 S44(1,3) 到非隔離 Client；PaperDialog.dat 資源缺失需具名回報|
|FLOW-GAMEPLAY|先以純 Domain 模型測 NPC/AI/技能/Quest Ledger，不往原 Client 發猜測 bytes|CT-021～028；待 A-024～026 的 Client writer/parser 交付後再驗收|

每項 CT 的 status 仍以 `05-conformance/vectors.json` 為唯一來源；此計畫**沒有執行任何 CT**，也不以單元測試假冒原 Client 通過。

**Bug triage**：原 Client 操作/收發不合預期→補 A Client I/O；Server 的權威判定/持久化/錯誤狀態→DEV；原 Client 與新 Server 可互操作→CT passed（需真 Client 步驟/證據）。保留先前已證的靜態子集。
