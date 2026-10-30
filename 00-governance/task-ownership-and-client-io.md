# 全部接案者必讀：研究與 Server 責任分工（v2，2026-10-31）

> 本規範適用本專案所有新任務與接案者。**研究者須先確定 Client 能發什麼、會接什麼、接到後做什麼；Server 內部決策由 Server 設計負責。** 不得因原服／新 Server／原生 CT 不可用而停止已可進行的 Client 靜態分析；不得以合成 Server 回覆冒認原服實況。

## 接案前先分軌

|handoff_track|對象|必需交付|不得要求作為研究結案條件|
|---|---|---|---|
|`client-io`|Asgard.exe 操作、UI、封包、Client 狀態|trigger、C→S、S→C、reaction、證據、unknown、供 DEV 的最小合約|原服帳號 DB/權限政策、原服出生點選擇、任務初派決策、怪物 AI／傷害公式無證據時的伺服器內部值|
|`resource-analysis`|Client DAT/MAP/Script/資源|format、provenance、client_usage、unknown／可重現安全 probe|特定地圖一定是原服教學出生點、原服內容派送規則|
|`server-design`|恢復／管理／負載等 Server 規劃|policy、invariants、failure_modes、validation；明示 designed|用 Client BIN 證明 DB transaction、Server 內部權限、容量或回復策略|

原本 A-016/A-017/A-018 屬 `server-design`，A-015 為 `resource-analysis`；其餘 A 依所屬 Client 互動以 `client-io` 為主。若工作同時涉及兩軌，以主任務軌交付，將另一類需求列給 Server/另一 A，不偷換範圍。

## 執行與交付

1. 先讀 `00-governance/phase-gates.md`、`03-analysis-requests/client-io-handoff-standard.md`、`03-analysis-requests/request-template.md`；查 `requests.json` 的該 ID、既有 PKT/SCN/CT、Client SHA；**不預設要建立 branch**，預設在既有指定 branch 工作；除非使用者明確要求，禁止自行創建分支。
2. 對 `client-io`，用觸發點→C→S→S→C→Client UI/下一個送包的逐步表；每欄附 VA、封包 bytes/編碼/長度、狀態與正反路徑。不存在事件可標「no packet observed」但要說明查過的路徑。
3. 對 `resource-analysis`，先記原件檔名、SHA、解析/引用位址、結構，再說明哪些只是推論；對 `server-design`，先寫 designed 決策及其安全／持久化驗收，必要時另提 Client I/O 分析。
4. 將結論分 `observed-static`、`observed-resource`、`observed-runtime`、`inferred`、`designed`、`unknown`；只在同一 Client profile 下比較，不將 UI 限制等同 Server 接受規則。
5. 提交研究結果與 `requests.json`、PKT/SCN/CT 引用；`handoff_status=partial/ready` 與 `native_client_validation=not-run` 可同時存在。研究要能移交 DEV，不以「還沒有新 Server」當 blocked。
6. 若研究中缺資源，**明確列出檔名**；已有 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat`，不要重複請求。現有已知 Script 視窗缺件可指 `PaperDialog.dat`；不憑空猜造其他檔名。
7. Server DEV 對應交付 `ServerOwner` 決策（身分驗證、map/spawn、腳本首次派送、AI/quest、DB），以原生可理解的 wire/state 執行；CT 等 Server 可用再跑原 Client。若 CT 失敗：Client 表現/封包規格錯→回 A；Server 實作錯→回 DEV。

## 兩個應避免的假阻塞

- **「還不知道原服選哪個出生點」**：Client 分析只需解析/驗證地圖與位置 S→C，Server 可選合法且 Client 能顯示的出生座標；原服實際政策 unknown 不阻擋 A。
- **「無法證明原服在帳號建立前如何授權」**：Client 分析只需明確 NewUser/C02/C03 UI/收發和反應；Server 必須用自身可靠憑證檢查，未通過不能發授權成功。此安全 DEV 限制不等於 Client A 未完成。

## 對照與檢查

`requests.json` 每個 A 必須有 `handoff_track`、`handoff_document`、`handoff_requirements`；`tools/validate-phase-gates.py` 與 main CI 驗證欄位和跨軌引用。這是機器可查的規則入口，原始函式/語意證據仍須人工 review。

詳見 [Client I/O 封包矩陣標準](../03-analysis-requests/client-io-handoff-standard.md)、[Server / Client 邊界](../02-server-planning/client-server-responsibility.md)。
