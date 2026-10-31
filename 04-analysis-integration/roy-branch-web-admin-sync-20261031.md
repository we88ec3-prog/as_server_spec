# task_a/roy1、task_a/roy2 同步與 Web 管理介面規劃審查（2026-10-31）

- 主線：`main@899cc1d9d6f4efe8bd89735a34935872ef6bb0ad`，Roy1 `eb4dfe1c320de4cdacf11a30fd86b9845c7e5768`，Roy2 `ab2525bbe7f36d5cec89f35189e2d776ea5a8942`。
- **Roy1** `ahead=0/behind=32`：已為 main 祖先，沒有新待合入提交。
- **Roy2** `ahead=4/behind=12`：未納入的四個提交只更新 `03-analysis-requests/README.md`、`requests.json`、`04-analysis-integration/packet-processing.md`、`05-conformance/vectors.json`。增加 A-010 離線 CI 證據與 A-015 舊版文件片段，**沒有新的原版 GUI 實測**。
- **衝突解決**：Roy2 局部編號的 A-015 `CT-087/088` 與 A-010 `CT-089/090` 會覆寫 main 經濟與地圖測試；主線仍保留 **CT-087..089 Economy、CT-090..091 MAP、CT-092..094 Quest、CT-095..096 Skill**，只增量轉入 A-010 的 offline-static/CI metadata 與經更正的 `packet-processing.md`，不覆寫舊 vectors。使用 Git merge parent 吸收 Roy2 來源提交歷史，Roy1 已在 main 歷史。
- 原始研究聲稱：Asgard.exe SHA 配對的 A-010 25 PE 指令 VA、6 RTTI、19 合成 codec tests 在 <https://github.com/we88ec3-prog/as_server_spec/actions/runs/41193941400> 通過；只是離線，不是原始 Client 技能 UI E2E。
- 私有 `as_server_roy/main@be3d2444f39029b86930cc82a0ce9292928a9185` 已有受 `X-Admin-Key` 保護的 `/admin` HTTP JSON API，無 HTML/Web UI；已實作遊戲密碼4～8字。公開 `admin-operations.json` 的 `/admin/v1` 是未實作設計路徑，不可混為現有 API。
- **使用者更正只准規劃**，本次沒有變動私有 Server、Client、部署或 GUI。Web UI 規劃及實作前確認 Gate 分列 [設計](../02-server-planning/admin-web-management-interface-plan.md)、[驗收](../05-conformance/admin-web-management-acceptance-plan.md)、[授權](../00-governance/explicit-implementation-confirmation.md)。
