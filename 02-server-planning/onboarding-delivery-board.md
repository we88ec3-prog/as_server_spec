# Server 進度板：規劃／分析／實作／驗收分開

截至 2026-10-31，僅以 `as_server_spec` 這份共用規格判斷；私有 Server 原始碼、最新編譯與測試不在本 repo，**不可推定它們已完成或未完成**。

|工作|規格|分析|可先做的 Server 工作|原生 Client 出場門檻|
|---|---|---|---|---|
|ONB-01 管理建帳＋登入|已規劃 R-025|A-021 子集已整合；A-027 未完成|管理 API、權限、稽核、憑證/停權、最小 C03 profile|預建帳號合法登入；Client 不可建 Account|
|ONB-02 創角與保存|已規劃 R-026|A-021 子集已整合；A-003/A-027/A-028 待補|原子建角、名稱/外觀驗證、草稿/重送|原 Client 正確創角/重登|
|ONB-03 首次入教學|已規劃 R-027|A-022 通用 Map/CRC 已整合；原生 MAP/出生待 A-015|grant、Loading/CRC 狀態機、內容版本|原版教學地圖出生且可操作|
|ONB-04 中斷恢復|已規劃 R-028|A-016/A-021/A-022 缺失分支|故障注入、幂等、重登入恢復|Client 中斷後無重複角色/錯誤進度|
|ONB-05 教學 NPC/怪物/技能/目標|規劃 R-029/030|A-023 Script/Born 部分整合；A-024/025 未完成|場景生成、AI/戰鬥架構與目標 ledger|教學真實互動流程跑通|
|ONB-06 教學完成/出圖|規劃 R-031|A-026 待分析|完成狀態/獎勵交易、轉圖骨架|原 Client 完成所有必要教學並離開|

## 下一步與狀態定義

**依最新 [分析優先順序](analysis-priority-after-A022-A023.md) 執行：A-027、A-015 先行，A-028、A-003/A-020 與資源/Script 研究並行**；A-021～023 已交付有界靜態子集，其餘 A-024～026 可讓專長人員先研究已知系統。所有 A 新增時仍為 open/unassigned，只有接手者確認才改 scoped/analyzing/review/integrated。參見 [分工包](../03-analysis-requests/onboarding-assignment-pack.md)。

- `specified`：需求已規劃；不代表已開發。
- `open`：分析任務待認領；不代表原版行為已解。
- `planned`：測試尚未執行。
- `implementation_status=not-reported`：共用規格未收到該私有實作的驗證資訊；不是斷言「沒有實作」。
- 原生 Client 驗收需要相符 Client、具體操作/輸出和測試證據；單人一般進圖通過不能算完整新手教學通過。

每次完成 A 應回寫 04 分析整合，補 CT，並更新版本與追蹤；Server 實作則由相應開發 repo 另行回報。

## roy1 合併後 P0 阻塞更新

A-021 已交付且靜態驗證其 C02 region variants、C04 五 u8、S02 status/string 及 state 0x1d→0x1e 的**部分**規格，不能解讀為原生創角路徑全部可開發/已實機通過。**新增 A-027/P0**：C02 pre-C03 身份/憑證及預建帳號認領安全證明；**新增 A-028/P0**：C04 之後的回覆/提交/重登轉服。ONB-01/02/03 的原生相容通路仍 blocked；管理端建帳、domain 唯一性、region-aware codec fixtures 可先做，禁止未驗證 C02 授權角色建立。


## A-022/A-023 合併後狀態（2026-10-31）

A-022 通用 Map/CRC 的部分可直接支援 DEV，但真正新手 map/spawn/C35 expected pair 仍無原版內容證明。A-023 有 Script C6C/S44 與 Born.Main PaperDialog 的靜態及 roy2 資源報告，**(31,29) 是文字導引而非 spawn**，首 NPC/自動觸發未知。CT-033/034/035 為 A-023 教學 Script 的測試（main 原 CT-029～032 保留給 A-021）；所有原生 Client CT 仍 not-run。

正式序列與可並行項見 [分析優先順序](analysis-priority-after-A022-A023.md)。

## 最新 A-001/A-023 分界（2026-10-31）

**A-001 integrated/partial**：seed0..9 binary codec 可先做 unit fixtures；實際 region/版本選 seed/key、S00 錯誤狀態仍交 A-020，不能宣布十種模式都真 Client 登入成功。**A-023 integrated/partial**：S44(1,0) named start、缺檔 C6C0/S44(1,1) 更新、Main 及 C6C4→C6C2 Dispose 已有靜態契約；原服首次發送時機、NPC 位置與 quest flag 仍 unknown。ONB-05 的 Script transport/run registry 可先 DEV；ONB-03/05 的原生教程全程仍 blocked。詳見 [Script Lifecycle](script-lifecycle-contract.md) 與 [本輪證據核對](../04-analysis-integration/A-001-A-023-merge-verification.md)。
