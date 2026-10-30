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

## 0.1.0-draft 補充 — 2026-10-31／所有接案者的分階段驗收

新增通用「A 研究證據交付 → DEV 實作 → CT 原生 Client 驗收」分離契約、A-021 專屬交付清單、通用任務模板與 AI handoff 規則；更新所有 A 紀錄與 ONB 工作的機讀 gate 欄位，並增加 GitHub Actions 結構檢查。A-021/A-022 的表述不再以新 Server 的實機測試作為分析完成的必要條件；重要 unknown 仍依 partial/blocked 誠實記錄。未改變任何 A 的實際 open 狀態或 CT 的 not-run 結果。

## 0.1.0-draft 補充 — 2026-10-31／A-023 roy2 BIN-first Script 研究

新增 `task_a/roy2/A-023-analysis.md`、原始 Client SHA 的靜態證據 E01～E08 與教學入口 Script 整合；C6C serializer 確認 0..4 分支、補 PKT-S44（含 type1/subtype3 的本機 Script 快取清理風險），更新 SCN-009/011、CT-029～031、追蹤與 manifest。教學第一個必需 NPC、Born 自動執行、任務 UI/flag 與首次 Script 封包仍無資源/原服證據；A-023 進 review／handoff partial，CT 未執行，未宣稱完整教程還原。

## 2026-10-31／A-023 Born.dat 原件補證

驗證 Born.dat SHA `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98` 的 zlib/UTF-16 XML，得到 Main 紙張導引、(31,29) 女性招募員與滑鼠點擊；無顯式 quest/NPC 生成/SendReply，不能推定自動觸發或出生座標。補實證 EXE IAT DeleteFileA、離線可重現校驗器、A/SCN/CT/evidence/manifest。A-023 限定證據範圍 integrated/handoff partial，原生 Client not-run；剩餘 NPC/原版觸發交 A-022/A-024。
