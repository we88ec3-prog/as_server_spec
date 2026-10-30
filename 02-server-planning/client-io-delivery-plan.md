# 從 Client 收發契約交付可開發 Server：下一輪工作計畫

日期 2026-10-31；規格原則：[全員接案規範](../00-governance/task-ownership-and-client-io.md)。對照 [機讀 Client I/O 矩陣](client-io-flow-matrix.json)；每個矩陣階段的 Client 觀察／Server 決策／DEV fixture／native CT 均分開。

## 以可運作的 Client 事件串接 Server（不要倒過來要求分析者解原服決策）

|Server 開發單元|能使用的 Client 證據|Server 要實作的權威行為|測試/目前真正缺口|
|---|---|---|---|
|DEV-IO-01 Gateway + Auth|A-001 C00/S00 加密、A-002 C03/S02/S03|解碼、admin-only Account/憑證/停權、成功與拒絕分支|seed0 synthetic fixtures；錯誤 S02 不能猜原服碼；CT-019/037|
|DEV-IO-02 Character intent + UI bridge|A-003/021/027/028 C02→S02→C04→S02/C15|只有驗過憑證的 owner 才能建立 PendingIntent；交易與重送冪等|先做 codec/安全拒絕；**C03 無角→NewUser UI 未證**，不能宣稱原生完整創角可用；CT-030/032/041～044/052/053|
|DEV-IO-03 Handoff + World loader|A-002 S03→C10/C25、A-015/022 S15/S14→C35→S04/S33|一次性 Grant；選**已驗可載入** Map/Spawn/CRC；同連線單一 pending load|以 Map0/1/2 對特定 profile 做 map-id/revision/checksum fixture；**(31,29) 不當出生點**；CT-016～018/039/040|
|DEV-IO-04 ScriptCatalog + ScriptRun|A-023 S44(1,0)/(1,1)、C6C(0)/(4)/(2)|Server 自選第一次派送時機、resource/version registry、一次性 run/取消；不得誤把 close=QuestComplete|先用隔離／受控 fixture，不送危險 S44(1,3) 刪快取；PaperDialog.dat 缺件時保留獨立動態驗收 blocked；CT-033～035|
|DEV-IO-05 NPC / Skill / Quest adapters|A-024～026 待查 Client writer/parser；A-011/012 可先取證|自行定 NPC spawn、怪物 AI、技能傷害、任務進度與獎勵|先做 Domain 模型與 mock；真 Client 端協定不得填猜測 opcode；CT-021～028 pending|
|DEV-IO-06 Recovery / observability|A-016 Server designed、A-002 Client 轉服、A-022 MAP response|代次/TTL/一次性 ledger/斷線重連及錯誤記錄去敏|合成 fault-injection、stale connection、CRC mismatch；CT-045/046，原版 Client E2E 獨立|

**重要**：DEV-IO 編號是規劃工作包，不宣稱 `as_server_roy` 已實作；現有 `ONB-01～06` 仍是正式開發工作追蹤 ID，不創建分支、不替私有 repo 宣稱測試 PASS。

## 第一個可落地的縱切流程（雙人可並行）

1. **封包與認證線**：錄入 profile/fixed byte fixtures → C03 解析及錯密拒絕 → 合法 S03／新 TCP C10（原始 token body） → 驗一鍵兌換與舊連線關閉。R-025 永遠不允許 C02 新增 Account。
2. **Client UI／內容線**：NewUser 操作→C02 payload/region→S02→C04→S02/C15 的狀態 fixture；與此同時核對具體 MAP id/CRC/可見座標 + S15/S14/C35→S04/S33 的顯示條件。**不能跳過 Client 不支持的 UI 轉場；未知仍 partial**。
3. **Script 線**：WorldReady 後 Server **選定**受控首次派送策略，S44(1,0) Born（合法版本/CRC/依賴）→ Client Main/紙張→ C6C(4)/(2)，任務完成旗標仍為 false。缺 `PaperDialog.dat` 時可交 Script codec 和 Mock/Domain，但真 Client PaperDialog 完整驗收仍不宣稱成功。
4. **玩法線**：A-024／025／026 的 Client I/O 收包/送包矩陣到位後，才接入真正的 NPC 互動、戰鬥/技能和任務 UI；沒有觀察到的 opcode 絕不填到正式 Server 原生 adapter。

## 如何判斷分析是否交付、DEV 是否能開工

- A 分支若已證 `Client trigger + 封包 schema + reaction` 子集，標 `handoff_status=partial/ready` 並交 DEV，**不需要先有 Server 實機**。Client 不可見的原服帳號資料庫、出生政策、首次 quest 規則屬 DEV designed。
- 某功能即使 Wire codec ready，若 UI 下一步還 unknown（例如 C03 無角導向 NewUser），完整原生 UI E2E 仍 blocked；這是**未解 Client 分支**，應回 A 做定點分析，不可讓 DEV 偽造下一個 GUI state。
- Server Domain 可以用 designed policy 開發、單元／合成測試，**不得稱為原服相容**，直到 CT 使用原 Client 覆核。
- CT 失敗時保存 Client SHA、操作、收/送 bytes、畫面及預期/實際；可追溯地分派給 A（Client contract）或 DEV（自訂政策/實作），不要使其他已證 Client 子集全部回到 open。

## 本輪優先分工

按最短可見結果：**A-020（登入 metadata/狀態）＋ A-027 的「C03 無角→NewUser UI」部分**與 **A-022 的「具體 MAP→C35/位置」部分**並行。A-023 的 Client Script 啟動/關閉機制已可給 DEV，不要再叫它還原原服首次派任務。接著 A-024 實際點擊 NPC（包括互動 C→S 和出生 S→C）、A-025 技能攻擊、A-026 完成 UI。Server 的 spawn、任務派送及身份授權不再列為 Client 分析者的交付阻塞。

參閱 [逐情境驗收案例](../05-conformance/client-io-verification-plan.md) 和 [ONB 正式工作板](onboarding-delivery-board.md)。
