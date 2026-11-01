# 直接開發與同步規格（最新使用者授權）

2026-11-01，使用者明確調整：「現在你直接在as_server_roy開發，把分析與規劃放入as_server_spec」。並更正：**as_server_roy程式碼不給其他人看，as_server_spec公開**。本決策覆蓋舊「本對話僅分析、不得修改Server」分工；既有歷史越界紀錄保留，不反向抹除。

## 路徑與分工

- 公開spec：`E:\Asgard\asgard_server\as_server_spec`。保存使用者需求、可重現分析／證據限制、語言無關的Server行為、相容性及驗收規格。
- 私有實作：`E:\Asgard\asgard_server\as_server_roy`。保存Server程式、實作測試及開發／診斷工具；不可複製程式進公開spec。
- 原始遊戲及提供的程式／資源：`E:\Asgard\workspace\神之領域`。保留原件，修改副本及取樣原件須明記身份並與原版驗收分開。

## 同一輪完成的流程

1. 定位需求與現況，區分使用者意圖、程式事實與設計建議；先讀已有證據與測試，不重開同義分析。
2. 在roy直接完成已授權且證據足夠的可測增量；需要的分析可邊做邊記。不再要求先完成一個獨立spec交接回合才開始實作。
3. 同輪把公開合約／分析／驗收及來源更新回spec；spec仍應足夠讓其他人自行開發，不能只留下私有方法名或「照roy做」。
4. 在roy做合適的程式驗證，在spec查引用／phase gates／manifest。實作、合成測試、修改副本及原始Client驗收分開記錄。
5. 各repo各自提交，發布前確認公開／私有邊界。Git只收可審查內容，不發布憑證、DB、原始EXE/DAT或runtime原件；沿用既有branch，不自行新增branch。

這是工作授權，不是把未知封包當已證、任意覆寫DB、丟棄現有工作或自動部署公網的授權。資料遷移先備份／確認影響；原生error/status未知時先分析或隔離為明示的實驗profile，不虛構成功。

同次延續的監測工具需求：使用者問先前監聽程式能否自行使用，實作放roy；公開spec只保留 [監測能力合約](../02-server-planning/client-monitor-tool-contract.md)。Server主流程後續仍按既有RI／PAR優先序推進。
