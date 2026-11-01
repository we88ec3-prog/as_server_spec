# 工作授權與歷史確認紀錄

## 2026-11-01 最新使用者授權：直接開發、同步規格

使用者已明確改為由本對話直接在私有 `as_server_roy` 開發，分析／規劃同步整理到公開 `as_server_spec`；不再要求先獨立規劃、再交另一人實作。以 [最新工作流程](direct-development-workflow-20261101.md) 與根目錄AGENTS為準。以下僅分析限制與額外分輪確認是歷史工作方式，**不得拿來阻擋最新已授權的開發**。未知需求、資料破壞／外部發布等仍按實際風險處理，不將一般可逆開發再設成重複確認關卡。

## 以下為歷史授權／限制與事件紀錄

使用者已更正：「我只是要你規劃不是要你實作管理介面，之後若我要你實作請提醒我做確認」。

**立即生效**：
1. 本次僅允許在 `as_server_spec` 做需求/畫面/API/測試規劃、Roy1/Roy2 分支研究比對整合、提交規格 Git；**不修改任何 `as_server_roy` 程式碼，也不建立 Web UI**。
2. **未來即使明說「請實作 Web 管理介面」**，也須先提醒使用者並取得**另一輪明確確認**，確認目標 repo（預設 `as_server_roy`）、階段 P0/P1/P2、是否新增 API/DB、是否僅限 localhost。確認前不可寫入或提交 `*.cs`、`*.html`、`*.js`、`*.css`、migration 或可執行測試。
3. 不必重問已確立的基線：原始 `Asgard.exe` 不修改、遊戲帳密4～8 ASCII 英數、Admin Key 強密鑰獨立、管理員建 Account、創角帳號不符拒絕、同 world/map 玩家共用怪物與 NPC。
4. 不得無授權新增 Git branch，不上傳原始遊戲 EXE/DAT；規格 `planned`、實作 `implemented`、原 Client 實機驗收 `native-validated` 必須分開記錄。
5. 本文件只約束**Web 管理介面實作**的額外確認；不應將使用者對一般分析與規格 Git 更新的既有指令推定成可改 Server 程式碼的授權。

參閱 [Web 介面設計](../02-server-planning/admin-web-management-interface-plan.md)。

## 2026-11-01 使用者最新角色分工（適用所有 Server 功能，覆蓋僅限 Web 的舊範圍）

**本對話／本專案的分析角色只可分析、整合 Client 證據、編寫／提交 `as_server_spec` Server 規劃與驗收。不可因使用者要求新增某 Server 功能而擅自改 `as_server_roy`、運作中 Server、DB、API、Web、程式測試或可執行服務。** 若需實作，交 DEV 開發者處理；原 Client `Asgard.exe` 不修改。Web UI 仍保留上面額外明確確認關卡。

2026-11-01 曾越界寫入 `as_server_roy/main`：`95977823`（Game TCP 每包 Log 與 Unexpected marker）與 `71ebd259`（文件修正）。此為**已發生的越界**，不是下次允許範例。相關成果只能在 [R-037 backfill](../02-server-planning/game-packet-log-contract-and-backfill-20261101.md) 如實登記 `source-implemented / native-not-run`。分析角色不得自行改寫、撤銷、重置或重新提交 Server commit，必要回退須由使用者交 Server DEV 決策。
