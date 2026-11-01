# 本地問題收集與規格整合責任

2026-11-01 最新使用者分工：本工作直接開發私有 `as_server_roy`，同步維護公開 `as_server_spec` 的需求／分析／合約／驗收。此分工覆蓋2026-10-31僅做spec、交另一人修改的方式；見 [直接開發流程](direct-development-workflow-20261101.md)。

## 工作邊界

- 收集本機 Client／Server 實際測試的症狀、重現步驟、版本及去敏證據；必要時以 REA 補足 Client 收發與狀態分析。
- 在本 repository 更新需求、分析問題、分析整合、Server 行為合約及驗收條件，完成檢查後提交 Git。
- `as_server_roy` 現為本工作直接實作／驗證的私有repo；依授權範圍開發並在同輪回補規格。資料遷移、運作中程序與發布須評估實際影響；不把私有原始碼複製進公開規格。
- Server 合約必須能由第三方獨立實作；私有實作的 commit 是查核版本，不是規格的定義。
- 延續既有規範：不自行建立 Git branch；不發布 EXE、DAT、憑證、帳號資料庫或未去敏封包。

## 問題到交付

收件時另按 [需求來源規範](requirement-origin-policy.md) 記錄使用者功能目的與原始回報，與程式分析、Server設計分開；不能在整合後把使用者提出的需求改寫成分析程式新發現的需求。

1. **收件**：使用者可直接描述症狀或在本地 Web 回報，不需代轉兩邊的分析文字。整合者先讀可取得的本地紀錄，再補問確實缺少的重現資訊。紀錄不含密碼等秘密。
2. **版本辨識**：記錄 Client SHA256／是否修改、Server repository 與 commit、地區／seed／編碼。舊 Python 原型與新 Server 分開，不因相同症狀就視為同一根因。
3. **問題登錄**：更新 [runtime-issues.json](../03-analysis-requests/runtime-issues.json)，使用穩定 `RI-xxx`，保留失敗與更正歷史；同一問題掛回既有 A／CT，不重開同義研究任務。
4. **證據與規格**：分清 `user-reported`、`observed-static`、`observed-runtime`、`implementation-reported`、`designed`、`unknown`。Client 路徑不明回 A；已證合約不符合回 DEV；預期行為未定先修需求／設計。一般 reconnect 提示本身不能證明帳密錯誤。
5. **直接開發並保留交付合約**：在 [修正交接表](../02-server-planning/runtime-feedback-handoff.md) 寫出目前／預期行為、封包及狀態、負向案例與驗收依據，並可在同輪直接於roy實作。列出已有實作避免重做；未知欄位不得補猜值，公開合約仍要供第三方獨立實作。
6. **回驗**：開發者提交其 Server commit、對應 RI／合約版本、合成檢查結果；原版 Client 測試另記操作、去敏 trace 與結果。測試可以一次涵蓋錯密→正確登入→創角→進圖等多項，逐項記錄，後段未能到達須寫 not-run。

## 關閉條件與歷史資料

只有相同版本組合的驗收證據支持預期行為，才能標 `verified`。開發者回報已修、合成測試通過、分析完成均不等於原版 Client 通過。無法重現寫「本次未重現」，不覆蓋原失敗。

舊原型曾通過的切圖、音樂、跳動畫等功能不能自動成為新 Server 的通過紀錄；修改副本顯示主選單也不能替代未修改 Client 的創角驗收。原始紀錄留在本地，Git 僅收經 review 的摘要、Evidence ID、原生位址、去敏重現步驟及合約。

本流程不新增常駐監控或自動將紀錄送往外部服務。與 [階段出場條件](phase-gates.md)、[Client I/O 標準](../03-analysis-requests/client-io-handoff-standard.md) 共同適用。
