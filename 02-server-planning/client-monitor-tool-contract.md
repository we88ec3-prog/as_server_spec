# 本地Client監測工具合約

來源：使用者詢問「你用來監聽遊戲的程式我能使用嗎?該怎麼使用?」。這是使用者使用工具的需求；觀測方法／欄位與限制是診斷設計。實作及操作文件位於私有roy，本公開規格不含其程式。

- 基本模式不需Frida：明確選擇一個Client PID或唯一候選，記程序身份hash、存活／Responding、CPU／記憶體及遊戲TCP端點狀態。TCP查詢失敗須標不可用，不能當零連線；PID重用須停止舊觀測。
- 可設定時間與取樣間隔；停止僅終止監測，不終止遊戲或Server。輸出保留本地、UTF-8 JSONL，不自動上傳或進公開Git。
- 進階Client API觀測需另外啟用runtime探針，附加成功才操作送出；記同步send/recv的時間、requested/result及可辨識frame前綴opcode/length，不記body、憑證、token或表單。有限事件預算且明示耗盡。
- 沒有完整TCP重組、未覆蓋非同步WSA APIs／附加前流量時，必須明示coverage限制。Client send成功不等於Server已收到；搭配Server去敏packet／close／validation同trace時間線確認。
- UI回應、程序退出、TCP關閉與原生遊戲結果分開。Frida會掛runtime hook，不能將其結果冒稱完全無探針原版驗收；原始檔不因此被修改。

驗收：無／多候選不得猜PID；不監測Server Host作為Client；JSONL有效且不含正文；傳送失敗、短前綴、EOF、事件上限及查詢不可用可區分；使用離線fixture與短程OS取樣，不因此宣告遊戲E2E。對應PAR-010／R-019／R-037，既有原生CT結果保持獨立。

## 本次交付快照

私有roy實作 `c4170f82`：基本版提供Windows PowerShell入口與雙擊wrapper，進階提供Frida metadata script及使用說明。Windows PowerShell 5實際短程OS取樣（無害Node fixture）通過，包含TCP權限不可用與可用情境；離線探針的前綴讀取邊界、send=-1、短recv／EOF、敏感正文排除及事件上限通過。本次未附加真遊戲、未安裝預設Python所缺的Frida套件，也未啟停使用者Server；CLI實際載入與原版Client結果仍須另記。原始測試輸出留私有data目錄。
