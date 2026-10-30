# 外部分析者與AI交接

一次指定一個A或一組互相依賴的A，提供相關R/SYS、已知PKT/SCN、Client身份、可分享證據及期待交付。不用每次上傳整個遊戲或全部大型JSON。

建議指令：請依本repo規格處理A-XXX。先列已知、未知及最低缺口；逐項用Client位址、Evidence ID或可重現操作支持。交付封包欄位、雙向處理、時序、遊戲規則、失敗分支及CT建議；不要依作者私有Server程式作唯一解釋，不要把設計或靜態分析說成實機通過。

原始工作資料放分析者自己的私有區；提交整合結果時帶來源身份、摘要及必要摘錄。Git分支建議analysis/A-XXX，先改03區問題與04區結果，再補05區驗收。兩人同時分析可各保留結論，整合時用證據解決衝突，不依模型名稱決定誰正確。

分析中發現Server私有實作錯誤：共同行為修正回規格；作者的程式修補另在私有repo，其他實作者自行修改自己的程式。Drive用來分享已審查規格；不保證資料夾每個檔案均被模型讀取，應要求列實際引用檔案及未分析清單。

## 所有 AI／人類分析者必須採用的 A/DEV/CT 分離驗收

任何 A 委派，先讀 [phase-gates.md](phase-gates.md)：**A 的驗收是有來源的分析結果與可交付規格，不是先用未開發 Server 通過原版 Client 實機**。若需要 Server 才能做端到端測試，將該實驗交給 CT/DEV；分析者應提供重現腳本與預期效果。確有必要的動態觀察可以使用既有可用環境或隔離探針，但模擬回覆不能證明原伺服器的行為。

完成分析時明確註明 `A.status`、`handoff_status`、證據身份、目前缺少的字段與下游 CT；不能因為 CT=not-run 就退回已證據支持的 A。A-021 的具體交付準則見 [A-021-acceptance.md](../03-analysis-requests/A-021-acceptance.md)。

## 2026-10-31 新優先規範：Client I/O 與分支權限

先讀 [全員接案規範](task-ownership-and-client-io.md) 和 [Client I/O 標準](../03-analysis-requests/client-io-handoff-standard.md)，以 `handoff_track` 決定交付。**上方「建議 analysis/A-XXX 分支」只適用使用者有明確授權時；沒有授權就使用既有指定分支，絕不新開 branch。** 不要求分析者證明原服資料庫驗證、原服固定出生點或首次任務發送；若無確切 Client 收發結果，保留 unknown 與 Client 子範圍 partial，將 Server 原因交 DEV。缺檔請寫出檔名，不重複請求已提供原件。
