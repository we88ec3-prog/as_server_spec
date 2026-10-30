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

## task_a/roy1 — 2026-10-31 A-021 分析整合

依 Asgard.exe SHA 覆核 MakeInfoDialog、C02/C04/S02 與 UI 分支，完成靜態研究及可開發的 R-025 相容規格：Client C02 可在 C03 前認領管理員已預建的 Account，不得新增 Account，C04 再原子完成 Character；精確原生 UI 跳轉及部分錯誤碼保留 unknown。A-021 integrated/handoff partial、Server 可開始實作、Client CT 尚未執行。保留 main 新增的 phase-gates/CI 與分離 A/DEV/CT 完成定義。

## A-021 roy1 merge 後審核與安全規劃 — 2026-10-31

Fast-forward merge `task_a/roy1` (d1b53b0)；獨立比對 Client SHA 與 BIN，確認 C02 region variants、C04 五 u8、S02 status/string 及 0x1d→0x1e UI path。修正 `implementation_ready=true` 的過度聲明為 partial codec-only、整體 false；新增 A-027/028 追 pre-C03 身份授權及 C04 後續回覆。R-025 admin-only Account 政策不變，禁止無身份綁定的 C02 認領。這些均非原生 Client E2E 通過。

## Merge A-022 task_a/roy1 — 2026-10-31

合併 A-022 BIN-first map/world-loading 靜態研究：S14 control 1/2/3、S15 欄位、C35 MAP header (+4) 與 structured checksum、S04 位置、MAP 16-byte 記錄及安全重連/epoch 設計。通用 World loading codec 可交 DEV；原生教學出生 map/spawn 仍依 MAP/資源佐證，native CT not-run。

## A-023 roy2 source integration — 2026-10-31

整合 roy2 Script/Born 研究（C6C subtype 0..4、S44 多分支含 Script cache 修改風險、Born.Main UI 導引至 (31,29) 女性招募員）。Born 資源 SHA/解析詳見 roy2 報告；原件未納入共用 repo，與 EXE 發行版的配對仍 unknown。原始教學首次觸發、NPC id/map/spawn 仍 unknown；登入後任務 CT 不可誤認已通過。原 roy2 CT-029..031 與 main 已佔編號衝突，整合時調整為 CT-033..035。

## Main 完整合併與驗證 — 2026-10-31

已將 `task_a/roy1` 以 merge commit `d239bff` 併入 main，將 roy2 實際來源分支 `analysis/A-023-roy2` 以 merge commit `7dd8d86` 併入 main。以指定 Asgard.exe 實體 SHA 及原生函式位址覆核 A-022 MAP/S14/S15/C35 與 A-023 C6C/S44；Born.dat 原件本次無法再次取得，因此 Born hash/XML 為 roy2 提供且可重跑的報告證據，非本次獨立 raw replay。已解 CT-029～031 編號撞號：roy2 Script CT-033～035，保留 A-021 原 CT-029～032；重新整理分析優先順序與 ONB 依賴。
 
## task_a/roy1 — 2026-10-31 A-001 seed0..9 / 版本/字串分析

發現 A-001 尚無正式分析，採提供的 Asgard.exe SHA 做 BIN-first 復核，解得 `0x53B630` 十種 256 項 seed 遮罩公式、`0x53BB30` key、`0x53BE70/0x53BD90` XOR、`0x53C460/0x53C130` binary/ASCII framing、`0x577E80` C00 與 `0x589B60` S00 0/1/2 分支及 `0x45B1B0/0x45B7A0` string8 byte 長度。新增可執行無外部依賴 Python golden vectors，原本 seed0 C62 fixture 不變。A-001 `integrated/handoff=partial`，十個 binary seed 算法可交付，region/version/error/ASCII 的原生未知維持 partial，Client CT not-run。

## 2026-10-31 — task_a/roy1 (A-001) + task_a/roy2 (A-023) 新分析 merge

主線由 2517e60 fast-forward 至 roy1 0facfc2（A-001 seed0..9 binary codec）；另以兩 parent commit c544af3 將最新 roy2 ae95270 合併（A-023 S44 named start、PaperDialog 依賴/CRC、C6C4/2 Dispose、候選 NPC Script），後續整合原 JSON/CT 而不覆蓋 A-001；留存 CT-029～032、CT-033～035 和 CT-036。原本 A-023 之「Script 如何啟動未知」修正為「Client 端啟動機制已有靜態契約、原服首次發送政策未知」。新增 ScriptRun 安全狀態機、檔案版本/語系/CRC 前提及分派更新。EXE SHA 和 18 個 roy2 byte signatures 複核通過，roy2 Born/PaperDialog 完整資源離線 PASS 非本次獨立 replay。

## task_a/roy1 — 2026-10-31 A-027 BIN-first C02 身份/控制與安全修訂

從指定 SHA Asgard.exe 的 0x4B2700 UI→0x5742B0 C02 writer 追出 field1 UI+0x26C 受 0x4B1A30 長度 gate、field2 UI+0x270 與確認 UI+0x274 經 0x5B4A62 UTF-16 相等檢查、region 0/2..4 額外字段，並核對 0x4B2360/0x4B21E0/S02 觸發 C04。預建帳號的 native owner 身份/credential 仍無 Server 或 Client 可信關聯證據、C03 零角色自動進 MakeInfoDialog 亦未證，故 A-027 研究 integrated/handoff partial，但 native account-claim **implementation_ready=false**、must fail closed；修正先前 A-021 建議裡「直接 claim 預建 Account」的危險解讀。新增 CT-039/040 合成契約，Client CT not-run。
