# A-XXX — 問題標題

- 所屬SYS／R／SCN：
- 分析類型：系統／功能／情境／失敗分支／效能
- 問題及不做的範圍：
- 目標Client身份（SHA、語系、是否隔離修改版）：
- 已有結論及Evidence ID：
- 入口：serializer/parser/handler、RTTI、字串、UI事件、資源欄位
- 最小實驗：前置狀態、操作、正常／拒絕／重送／斷線情境
- 記錄：精確方向、opcode、offset、條件、呼叫先後、狀態變化
- 原始證據：分析者私有工作區，提交時僅附可分享摘錄與身份
- 每項結論標記：observed-static／observed-runtime／inferred／designed／unknown
- 影響：PKT／遊戲規則／SCN／CT
- 驗收：另一位實作者能否不看私有程式就實作該行為
- 未解問題及後續A：

## 強制交付關卡（每項 A／新對話都要填）

- 使用完成契約：`A-EVIDENCE-HANDOFF-v1`，先讀 [跨角色關卡](../00-governance/phase-gates.md)。
- **本 A 可獨立交付的東西**：哪些 BIN／資源/Client parser 證據、逐欄協定、狀態表、Client 效果、拒絕分支、可供 DEV 實作的規格。
- **不包含**：寫 Server、讓原 Client 接新 Server 成功登入、CT 實機驗收；這些是 DEV/CT 工作，不得作為 A 結案前提。
- **證據範圍**：觀察到的/推定的/設計的/未知各自列出；若被 mock 驅動，明確標記只是 Client 在假設回覆下的反應。
- **交接狀態**：`handoff_status=ready`（限定範圍足以實作）／`partial`（已知子集可實作，必要未知另列）／`blocked`（研究本身所需 EXE/資源/證據阻塞，寫具體理由）。
- **下游驗收**：列 CT ID、在 Server 可運行時的測試步驟及 Owner；保持 `native_client_validation=not-run`，直到真實驗收確實完成。
- 審查者不得因尚未開發 Server 而拒收有證據且完整的 A；也不得因 A 的部分規格能交給 DEV，就把仍有關鍵未知的整條原生流程宣稱完全相容。

## v2 接案必填（優先於上方含糊的舊式「原服規則」問題）

- **`handoff_track`**：`client-io`／`resource-analysis`／`server-design`；先查 [全員規範](../00-governance/task-ownership-and-client-io.md) 與 `requests.json`。
- **Client I/O 主軌**：為每條事件寫 `trigger`（誰按／哪個 S→C 先來）、`client_sends`（C→S opcode/body/資料來源）、`client_receives`（Client 必須接的 S→C opcode/body/狀態）、`client_reaction`（畫面/狀態/再送包）、`evidence`（EXE VA、原件檔名/SHA、重現方法）、`unknowns`（尚未查證的 Client 分支）。若 Client 只單向送或只收，另一欄明填「此觸發無封包」，不得省略。
- **資源研究主軌**：`format/provenance/client_usage/unknowns`；Server 內容選擇並非原服既定值驗證。
- **Server 設計主軌**：`policy/invariants/failure_modes/validation`，標 `designed`，不可偽稱原生。
- **Server owner 交接**：清楚分開帳號/授權、角色持久化、出生點選擇、NPC AI／任務首次派送等 Server 判定，不把這些當作 Client 靜態研究尚未結案的理由。
- **驗證**：A 可在證據完備子集標 `integrated/partial`、Client E2E 維持 `not-run`；在本地執行 `python3 tools/validate-phase-gates.py`。除使用者明確指示，不建立新 Git branch。
