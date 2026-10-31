# 「規劃」與「實作」的明確確認關卡（2026-10-31）

使用者已更正：「我只是要你規劃不是要你實作管理介面，之後若我要你實作請提醒我做確認」。

**立即生效**：
1. 本次僅允許在 `as_server_spec` 做需求/畫面/API/測試規劃、Roy1/Roy2 分支研究比對整合、提交規格 Git；**不修改任何 `as_server_roy` 程式碼，也不建立 Web UI**。
2. **未來即使明說「請實作 Web 管理介面」**，也須先提醒使用者並取得**另一輪明確確認**，確認目標 repo（預設 `as_server_roy`）、階段 P0/P1/P2、是否新增 API/DB、是否僅限 localhost。確認前不可寫入或提交 `*.cs`、`*.html`、`*.js`、`*.css`、migration 或可執行測試。
3. 不必重問已確立的基線：原始 `Asgard.exe` 不修改、遊戲帳密4～8 ASCII 英數、Admin Key 強密鑰獨立、管理員建 Account、創角帳號不符拒絕、同 world/map 玩家共用怪物與 NPC。
4. 不得無授權新增 Git branch，不上傳原始遊戲 EXE/DAT；規格 `planned`、實作 `implemented`、原 Client 實機驗收 `native-validated` 必須分開記錄。
5. 本文件只約束**Web 管理介面實作**的額外確認；不應將使用者對一般分析與規格 Git 更新的既有指令推定成可改 Server 程式碼的授權。

參閱 [Web 介面設計](../02-server-planning/admin-web-management-interface-plan.md)。
