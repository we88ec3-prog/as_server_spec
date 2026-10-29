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
