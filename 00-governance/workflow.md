# 同一份規格，獨立的 Server 實作

## 追蹤鏈

`R-需求 → SYS-系統／ADR-設計決策 → A-分析問題 → PKT-封包／SCN-情境／規則 → CT-相容性測試 → 各實作DEV任務 → 原Client驗收`

需求回答「要做到什麼及如何驗收」；規劃回答「系統如何合作、為何如此設計」；分析需求回答「缺哪項證據，如何取得」；分析整合回答「已確認的行為是什麼」；私有開發回答「作者如何實現」。不要把這五種內容混成一份日記。

## 一項工作的閉環

1. 新增R，填功能、玩家情境、優先序、驗收；新增或更新SYS/ADR。
2. 遇到未知則新增A，指定前置問題、Client版本、分析入口、最小實驗與交付物。
3. 保存原始證據到分析者自己的工作區；提交可分享的結論、Evidence ID、位址、限制及必要摘錄。不要整包上傳執行日誌或帳號資料。
4. 將分析結果整合到PKT／遊戲系統規則／SCN。每一欄分開標示未知與來源，未知不可補0後當成已解。
5. 更新共用CT向量、相容性profile及變更紀錄。各Server實作再將自己的DEV任務連到相同R/PKT/SCN/CT。
6. 自動測試通過與原客戶端實機通過分開記錄；失敗回報保留，修正後追加驗收。

分析任務狀態：open → scoped → analyzing → review → integrated；證據不足可blocked並記具體依賴。整合不等於已開發，已開發不等於Client驗收。

## 證據與設計標記

- `observed-static`：原程式指令／解析器觀察。
- `observed-runtime`：指定版本、操作、封包或執行結果實際觀察。
- `inferred`：由已知證據推導，仍需驗證。
- `designed`：為完成Server而採取的設計，不能稱為原服行為。
- `unknown`：未知，需連到A。

一份規格可能同時含這幾種標記。別用單一「已完成」掩蓋個別分支或未知公式。

## 規格變更

版本0.x階段仍採顯式破壞性變更說明。PR應列受影響R、PKT、SCN、CT、原生版本和遷移辦法。作者私有實作發現缺口時，也先補共同規格；不可只在私有程式悄悄修正，讓其他實作無法相容。

共享的規範性文字用「必須／不得／應／可」。歷史觀察、實作建議與待分析問題不可偽裝為規範性條文。新增官方未知公式時，必須以明示的自訂規則profile呈現。

## 防止研究／開發循環等待：所有任務的共同關卡

**工作閉環分成 R/SYS 規格 → A 證據交接 → DEV 實作 → CT 原生 Client 驗收，不要求 A 等 DEV／CT 才能結案。** A 可整合且 handoff ready/partial，CT 仍是 not-run；但要有實際證據、明確交付範圍與未知清單，不可把推測當已還原。Server 尚未建置不是 A 的 blocked 理由；只有本身必備研究證據不可取得時才能 blocked。CT 實測若暴露偏差，再回開 A/DEV，不反向取消有效的研究證據。

本規則對**所有新舊接案者**生效；詳細角色、完成/部分交付/blocked、回報與 A-021 案例見 [phase-gates.md](phase-gates.md)。新派工必須套用 [request-template](../03-analysis-requests/request-template.md) 並接受跨階段驗證腳本檢查。

## Client I/O 導向工作規範（v2，2026-10-31）

新舊 A 必讀 [全員接案規範](task-ownership-and-client-io.md)，工作前先依 `requests.json.handoff_track` 判斷是 Client I/O、資源研究或 Server 設計。Client 研究僅負責玩家操作/收包事件、送包、必要回包、畫面及下一個封包；Server 決定帳號授權、地圖/出生點、教學首次派送、NPC/AI、DB/冪等。即使原服政策無法由 Client 推論，已證的 Client 封包子集仍交 DEV。**禁止未經明確要求新建 branch**；缺檔回報準確檔名。所有新派工使用 [v2 模板](../03-analysis-requests/request-template.md) 並通過 CI 機讀契約。
