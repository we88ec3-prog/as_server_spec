# 變更紀錄

## 0.1.0-draft — 2026-10-30

建立共同規格與私有開發分區；整理24項需求、20項待分析問題、系統責任、34項已知封包入口、6個基線情境與合成相容性向量。保留已知未知，未將完整MMORPG實作或最後畫面驗收標成完成。

同日補充：核對舊分析，新增逐份覆蓋表、Evidence身份索引、資源／地圖與Client相容性整理；補回metadata及SScript快取清理的已知細節。大型原件與私有實作未納入。

## 0.1.0-draft 補充 — 2026-10-31

依需求方確認的「僅管理員建帳、玩家 Client 只登入」，新增 R-025～028、A-021～023（open）、SCN-007～010（analysis-required）、CT-011～020（planned）與首次玩家規範、子里程碑、測試計畫。原 Client 無角創角 UI、C02/C04/S02 完整分支、原版新手教學 map ID/座標仍 unknown；無任何新 Server 實作或實機通過宣稱。

## 0.1.0-draft 補充 — 2026-10-31

依需求方確認的 R-025「僅管理員建帳，玩家 Client 只登入」，新增 R-025～028、A-021～023（open）、SCN-007～010（analysis-required）、CT-011～020（planned）及首次玩家需求/設計/測試文檔，更新系統分工、追蹤與 manifest。原 Client 空角創角轉場與真實教學 map/出生座標維持 unknown；本次不代表 Server 已實作或 Client 已驗收。

## 0.1.0-draft 補充 — 2026-10-31 教學完成延伸

新增 R-029～031、A-024～026（open）、SCN-011～013（analysis-required）、CT-021～028（planned）；新增 ONB-01～06 工作板、work-items.json、分析人員交付包、教學執行規劃與測試計畫。原生 map/出生、NPC/怪物、技能及任務完成、出口與獎勵仍需證據，沒有宣稱新 Client 人工驗收通過。

## task_a/roy1 — 2026-10-31（A-021 靜態證據與阻塞）

逐位址檢查 Asgard.exe C02/C04/S02 與原生 MakeInfoDialog，更新 A-021 證據索引與協定、CT；A-021 status=blocked，未聲稱首次預建帳號成功進入原版 UI，沒有假造原生 runtime 證據。另以 merge commit 整合 main 同時新增的教學規劃 A-024～026/R-029～031，不回退他人變更。

## task_a/roy1 — 2026-10-31 A-021 分析/實機流程分離

依需求方確認改正 A-XX 完成標準：僅以分析實質缺失 blocked，不以缺乏原 Client 實機 blocked；可靜態整合並開始 Server 開發，再由 CT 驗收及 BUG 回饋。擴展 A-021 MakeInfoDialog 的 UI 欄位綁定、C02/C04/S02 狀態路徑，形成安全的「管理員預建 Account → C02 認領 → C04 完成 Character → C03 正常登入」 designed 相容方案。標示未證明的 C03 無角色自動 UI 轉場，無實機驗收宣稱。
