# 跨角色工作關卡：分析交付 ≠ 開發完成 ≠ 原生 Client 驗收

此規則適用**所有目前與未來的 R / SYS / A / DEV(ONB) / CT 任務**，尤其 A-021。目的：消除「分析者等 Server 實機通過、開發者等分析完成」的循環相依。此為工作流程政策（designed），不宣稱原版 Asgard 行為已確認。

## 工作關卡、所有權與不能冒用的完成條件

|工作型別|完成／可交付標準|誰負責|不得當作此任務的阻塞|
|---|---|---|---|
|R / SYS 規劃|寫清功能、前後置、失敗路徑、驗收、依賴；將未知開成 A|規劃者|完整原始 Client 實測、Server 已開發|
|A 逆向研究|就**明定研究範圍**交付 BIN／資源／可用 runtime 證據、字段/狀態/Client 效果、已證與未知及可測規格，經同儕 review|分析者 + 規格整合者|尚未存在的新 Server、DEV 完成、下游 CT 實機通過|
|PKT/SCN 規格整合|用證據標記支援範圍，已知分支可讓獨立開發者實作；未知欄位保留 partial + A|規格整合者|先實作整個遊戲或先跑完全教學|
|DEV / ONB 實作|根據已確定的規格/自訂 profile 完成所承諾子集，單元／整合／模擬/固定 byte 向量測試可重現|Server 開發者|所有 A 均須完全結案、整款原生 Client 功能已驗收|
|CT 原生 Client 驗收|**Server 可執行後**用指定 Client、操作步驟、封包/畫面、期待/實際、失敗案例確認；回報差異與回開 A/DEV|驗收者（與 DEV 協作）|不能倒過來要求 A 先把 CT 通過|

## A 的雙軌結案規範

**A 的研究狀態**既有 `open → scoped → analyzing → review → integrated`（或 `blocked`）與**交接就緒度**另外記錄，不要把狀態合併成一個「完成」：

- `handoff_status=not-started`：尚未審查證據。
- `handoff_status=partial`：有證據支援的部分規格可交付；**必要未知仍列 A/blocked-items**，不得宣稱整個原生行為可完整實作。
- `handoff_status=ready`：本次 A **限定範圍**內的必要欄位、條件與拒絕行為足夠使獨立開發者實作，經審查整合；仍不等於原生 Client E2E 已通過。
- `handoff_status=blocked`：缺本任務研究本身必要的原始 EXE、資源、證據或可重現入口；要指出缺什麼、能交付什麼、由誰解決。**僅「新 Server 未建好／CT 尚未通過」不得使 A blocked**。

每個 A 紀錄必備 `completion_policy="A-EVIDENCE-HANDOFF-v1"`、`handoff_status`、`native_client_validation`，其中 `native_client_validation` 與 A.status **互不推導**。在 A.integrated 與 handoff ready/partial 時，可以保留 native_client_validation=not-run。原 Client 實測若能在既有可用環境或隔離探針完成，可作 `observed-runtime` 的額外證據；**要求完整新建 Server 才能做的驗收一律移到 CT**。

**防止假完成**：不以「環境缺失」當作證實原服不存在某分支；不以 mock Server 的回包證明原服 Server 實際如何回覆；不把反編譯器顯示的名稱當協定語意。偵測到關鍵未知時，以 partial/blocked 標明，必要時拆成另一 A；已確認子集可先移交 DEV，不能把未知填 0 或猜測值。

## A-021 具體案例（不等原生 Server）

分析者可先在原 Client 靜態/BIN 層：
1. 追 C02 serializer、C04 serializer、S02 parser，找到 UI 呼叫點、分支條件和欄位類型；
2. 畫「預建空角色帳號 → 嘗試創角 → 回覆分類 → 後續登入／轉服」的狀態表，**逐格標 observed-static / observed-runtime / inferred / unknown**；不可把推測畫成已實測；
3. 交付 Server 可使用的最小 input/output 合約、欄位/編碼/長度、拒絕或取消條件、必要原始位址與 evidence、失敗分支未知清單與 CT-018 可重現腳本；
4. 交整合者審查。如果尚缺原服 S02 某些 status 的判定，則只能標 partial 並提新的 A/待證據分支；**不是因為缺 Server 而分析失敗**。

**DEV** 依已確認的 A-021 子集實作角色創建及狀態回覆，先跑 domain/codec/state tests；**CT-018** 才負責用原生 Client 實測整條創角→教學入圖，發現不符回開 A（證據/協定錯）或 DEV（程式錯），不回頭抹掉已被證據支持的 A 結論。

## 每個接案者必須提交的交接內容

- **Scope**：自己的 R/A/ONB/CT ID、所屬 Client hash/profile、此次不做的部分。
- **Evidence**：觀察來源、原始位址／資源定位、方法與置信標籤；模擬行為明示 mock。
- **Contract**：已確認可交付字段/狀態/順序及錯誤、超時、重送、斷線分支。
- **Unknown & handoff**：必要未知清單、是否阻塞**全部**或僅**原生相容子集**、後續 A/DEV/CT owner、重現/驗收步驟。
- **Separate gates**：A 的 handoff 結論、DEV 測試結論、CT 原生實測結論分別記錄，不可用一個「未實機驗收」使整項分析打回原點。

## 統一決策表

|實際情況|A 結果|DEV 工作|CT|
|---|---|---|---|
|BIN 已證實封包/狀態/失敗路徑，Server 尚未寫|review → integrated、handoff ready|可開始|not-run|
|僅確認部分字段，其他必要字節仍未知|review/integrated 範圍限於已知，handoff partial|只開發已知子集；完整分支標 blocked|not-run|
|無 EXE／無可定位的 parser／關鍵證據不可取得|A blocked + 明列證據阻塞|獨立模組仍可開發，wire 相容部分不能假完成|not-run|
|DEV 成功但 Client 實測失敗|已證 A 結論保留，必要時另開 A investigation|修正 DEV 或明示不支援分支|failed、留下可重現差異|
|實機測試成功|A 狀態不需變更|DEV 更新支援範圍|對應 CT 標 validated|

## 避免循環依賴的機讀規則

`03-analysis-requests/requests.json` 的所有 A 都用 `completion_policy` 與 `handoff_status`；`02-server-planning/work-items.json` 的 ONB 均以 `completion_policy=DEV-CT-SPLIT-v1` 分開 `implementation_status` 與 `client_acceptance`。CI 使用 `tools/validate-phase-gates.py` 驗證必要字段、引用與**禁止 A 的完成依賴新 Server/CT**；這是結構性防錯，無法取代對文字語意及證據的人工 review。

## Client I/O 範圍防偏移（2026-10-31）

本規則對 **全部 A-XX** 生效：必要研究成果是「玩家/收包觸發 → Client 送包 → Client 必要收包 → UI/下一個送包」及原始 EXE/資源證據；**原版 Server 的帳號認證、資料庫提交、出生點選擇、任務初派政策、NPC AI/獎勵決策一律不是 A 必備結案條件**。原服未見行為標 server-policy-unknown，責任轉 DEV；如 Client 路徑本身不明才保留該 Client 子分支 partial。明確執行範本見 [Client I/O 標準](../03-analysis-requests/client-io-handoff-standard.md)。

## v2 Client I/O 範圍的 CI 支援

全體 A-XX 先分類工作軌；Client I/O 研究以操作→送包→收包→畫面/再送包為核心，不以原服帳號/出生點/任務/DB 政策作完成門檻。A-015 資源格式、A-016/017/018 Server 設計是獨立工作軌，不強迫填不存在的 Client 封包；人工審核仍不得用原服不可見決策卡住已證 Client 研究。參考 [全員規範](task-ownership-and-client-io.md)。
