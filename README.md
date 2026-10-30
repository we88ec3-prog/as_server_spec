# Asgard Server Specification

版本：0.1.0-draft · 日期：2026-10-30

這是本作者及其他開發者共同依循的、與實作語言無關的 Server 規格專案。任何實作，包括作者的私有 Server，都應依同一版本實作與驗收。此 repository 不包含作者的 Server 原始碼、部署憑證、帳號資料庫或原始遊戲檔案。

本版是可繼續補完的規格基線，**不是完整遊戲協定已還原的宣告**。目前主要證據來自指定台灣版 Client 與單人原型；戰鬥、多人、經濟等缺口明確列在分析需求。原型的實作行為不得直接當成原服規則。

## 從這裡開始

1. [共同開發流程](00-governance/workflow.md)：需求到驗收的固定編號與交付規則。
2. [Server需求](01-server-requirements/README.md)：完整系統範圍、優先序、驗收及非功能需求。
3. [Server規劃](02-server-planning/architecture.md)：系統邊界、資料責任、狀態機與階段路線；另見[邏輯介面與資料](02-server-planning/interfaces-and-data.md)。
4. [分析需求](03-analysis-requests/README.md)：依系統／功能／情境分派問題。
5. [分析結果整合](04-analysis-integration/README.md)：封包、Client行為、遊戲規則與情境整合。
6. [獨立實作指南](05-conformance/implementer-guide.md)：共用測試向量及相容性宣告。
7. [目前基線及已知缺口](00-governance/baseline.md)：先讀以免沿用歷史文件的舊結論。

可機讀資料：requirements.json、systems.json、requests.json、packets.json、scenarios.json及traceability.csv。它們與說明文件放在各分區。

開發原始碼在另一個獨立 repository。共享規格不引用該 repository 的函式或私有套件作為行為定義。別人不需取得作者原始碼即可實作已完整指定的profile。

授權條款尚待專案擁有人選擇，見[分享與授權決策](00-governance/sharing-and-license.md)。本repository只維護可分享規格；作者的私有Server實作不發布在這裡。

已有研究的整合情況請看[既有分析覆蓋表](04-analysis-integration/analysis-coverage.md)：逐份列出舊文件、新規格落點及哪些只保留摘要／身份索引。

## 首次玩家流程：登入 → 創角 → 進入新手教學（2026-10-31）

已確認：**只有管理員能建立 Account；玩家透過原 Client 登入及自行建立 Character，不得自行註冊 Account**。閱讀 [R-025～028 需求](01-server-requirements/first-login-onboarding.md) → [ONB-01～04 規劃](02-server-planning/first-login-onboarding.md) → [A-021～023 待分析](03-analysis-requests/README.md) → [SCN-007～010 情境](04-analysis-integration/scenarios.md) → [CT-011～020 計畫](05-conformance/onboarding-test-plan.md)。目前為規劃，不是原 Client 已完成驗收。

## 首次玩家：管理建帳 → Client 登入 → 創角 → 新手教學（2026-10-31）

已確認使用者需求：**帳號由管理員透過獨立後台建立，玩家只能使用原始 Client 登入並建立角色，不能由 Client 註冊帳號**。新的規格鏈： [R-025～028](01-server-requirements/first-login-onboarding.md) → [跨系統 ONB 規劃](02-server-planning/first-login-onboarding.md) → [A-021～023](03-analysis-requests/README.md) → [SCN-007～010](04-analysis-integration/scenarios.md) → [CT-011～020](05-conformance/onboarding-test-plan.md)。目前是規劃／待分析，不是新手地圖已通過原 Client 實測。

## 首次玩家流程已規劃延伸至教學完成（2026-10-31）

本次新增 **R-029～031**（教學 NPC/怪物、技能/目標、完成/退出）、**A-024～026**（待逆向）、**SCN-011～013**（分析必要）與 **CT-021～028**（planned）。

[最新 Server 進度板](02-server-planning/onboarding-delivery-board.md) · [A-XX 分析交付包](03-analysis-requests/onboarding-assignment-pack.md) · [ONB-01～06 開發批次](02-server-planning/work-items.json) · [教學 Server 詳細規劃](02-server-planning/tutorial-runtime-plan.md) · [CT-021～028 驗收計畫](05-conformance/tutorial-test-plan.md)。

管理員建立 Account、玩家只用原 Client 登入的 R-025 決策不變；本次規劃仍不代表教程已開發或跑通原 Client。

## 分析交付與開發／實機驗收分離（所有新舊任務）

為防止 A-021 類「逆向分析等新 Server 的實機驗收、Server 又等逆向分析」的循環依賴，**所有 A/DEV/CT 接案者都需按 [phase-gates.md](00-governance/phase-gates.md) 的獨立出場條件工作**。A-021 有專用 [交付清單](03-analysis-requests/A-021-acceptance.md)；共用要求由機讀 requests.json、work-items.json 以及 CI [validate-phase-gates.py](tools/validate-phase-gates.py) 驗證。分析可完成並保留 CT=not-run，前提是證據支持範圍與未解事項如實交代。

## roy1 A-021 合併後 review（2026-10-31）

`task_a/roy1` 已 fast-forward merge 並經 Asgard.exe BIN 靜態核對；已確認 C02 region variants、C04 五 u8、S02 status/string 及 UI 0x1d→0x1e。**A-021 只達靜態 partial handoff**，新開 A-027（前認證身份／帳號權限）及 A-028（C04 最終回覆/轉場），CT-029～032 計畫中。詳見 [roy1 review](04-analysis-integration/A-021-roy1-review.md)。未經認證的 C02 絕不能認領管理員已建立的帳號。

## 2026-10-31 A-022/A-023 整合後的分析優先順序

[下一輪分析順序與 DEV/CT 解鎖條件](02-server-planning/analysis-priority-after-A022-A023.md) | [BIN 靜態驗證與 Born 來源限制](04-analysis-integration/A-022-A-023-merge-validation.md)。A-027/A-015 為首批並行，A-028 隨後；Script 相關 CT 使用 033～035，保留原有 CT-029～032。

## A-001/A-023 最新可實作交接

[2026-10-31 roy1/roy2 新成果驗證](04-analysis-integration/A-001-A-023-merge-verification.md) · [Script 啟動/關閉 Server 規劃](02-server-planning/script-lifecycle-contract.md)。A-001 seed0..9 binary codec、A-023 S44(1,0) named start／C6C2/4 close 子集可先開發；原服 first-login policy／NPC mapping 未確認，原生 Client CT 均 not-run。

## A-002 登入／轉服規劃

[SessionTransfer 契約](02-server-planning/session-transfer-contract.md)／[A-002 新證據驗證](04-analysis-integration/A-002-merge-verification.md)：S03 addr/port/token 引導新 TCP，C10 只寫 raw token。已勘誤 0x4A8370 真正是 S03 handler 而非 C25。CT-037/038 native not-run。

## task_a roy1/roy2 最新分析合併（2026-10-31）

[A-015/A-016/A-027/A-028 首次登入、創角、恢復、地圖的 Server 整合規格](02-server-planning/merge-20261031-roy1-roy2.md) · [原始二進位與 MAP/Born 覆核報告](04-analysis-integration/A015-A016-A027-A028-validation.md) · [A-014 聊天／密語／組隊／公會安全開發契約](02-server-planning/social-contract.md) · [A-015 格式與盤點研究結案界線](task_a/roy2/A-015-closure-review.md)。保留原 client/S02/C15/Script 與 494 MAP 的部分已證成果，沒有將建角原生 owner proof、首次出生、群組 type/op 或 Client E2E 宣稱通過。CT-039～040 為地圖內容、041～046 為創角／恢復、047～049 為社交。

[A-017 管理端 API／停權解封／去敏稽核](02-server-planning/admin-operations.json) · [A-017 原始報告](03-analysis-requests/A-017-roy1-admin-audit.md)。主線測試 CT-050/051 planned，不冒認實機通過。

## 新版工作規範與 Client 收發導向 Server 路線（2026-10-31）

**所有接案者先讀**：[工作軌／責任／禁止自行建分支](00-governance/task-ownership-and-client-io.md) → [Client I/O 交付規範](03-analysis-requests/client-io-handoff-standard.md) → [新版任務模板](03-analysis-requests/request-template.md)。新增 [Server 可開發的 DEV-IO-01～06 縱切規劃](02-server-planning/client-io-delivery-plan.md)、[6 條機讀 Client I/O／Server decision 矩陣](02-server-planning/client-io-flow-matrix.json) 與 [分段驗收計畫](05-conformance/client-io-verification-plan.md)。CI 將強制 A 任務分類與交付要求；實機 CT 全部仍須獨立執行。
