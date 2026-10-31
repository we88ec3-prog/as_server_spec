# 原生創角帳號比對：合成與真實 Client 的獨立驗收

規格 R-025/026；SCN-007/008；Client 不修改。帳號欄不遠端 Disable；Server 檢查是否等於**本次已驗證登入帳號**。

|場景|Server/合成驗收（可立即規劃測試）|原生 Client 驗收|
|---|---|---|
|登入 A，創角輸入 B|拒絕；無草稿/角色/Grant；不回引發 C04 的 S02(0)；B 資料不變|既有 CT-041、CT-053 仍 not-run|
|登入 A，輸入 a（ASCII 大小寫差異）|只通過 canonical 名稱比對，仍驗身份/世代/停權/唯一性；不自動創角成功|仍需證實 C02 首欄語意（A-027）|
|匿名 C02、跨 connection/舊 generation、停權|一律拒絕；不能靠字串認領 Account|Client UI 入口未證時 native 一律 fail-closed|
|符合身份/名稱並送 C04|正確 pending + 5-u8 外觀原子提交一次，重送/中斷/延遲 C15 無重複與撤銷|CT-044/053；A-028 的 UI 後續尚 unknown|
|C03 已驗登入且無 Character|Server 內部可判 no-character，但**不能假設 Client 顯示創角畫面**|**CT-054 (planned)**：追原版 Client 是否能從已登入狀態到 NewUser、C02 帳號欄來源及操作/封包；若無入口回報限制|

CT-054 的測試紀錄應包括 `Asgard.exe` SHA/profile、玩家按鍵/畫面、C03/S02/C02/C04（若有）、當次 AuthContext/Connection id（去敏）、預期與實際、UI/下個封包、Server DB 角色數與 Grant 狀態。**不得記明文密碼/token**。未實際使用原生 Client 就保持 planned/not-run，不能把守衛或 SQLite 單元測試冒認 Native E2E。

[Server 下一輪切片](../02-server-planning/native-creation-next-iteration.md) · [分析交接](../03-analysis-requests/next-client-io-evidence.md)。
