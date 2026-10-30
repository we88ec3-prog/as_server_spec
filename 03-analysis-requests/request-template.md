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
