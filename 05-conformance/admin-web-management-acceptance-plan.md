# WEB 管理頁面驗收案例（全部 planned / not-run）

依 [Web UI 規劃](../02-server-planning/admin-web-management-interface-plan.md)。下述 `WEBUI-Pxx` 是**規劃案例標籤**，不佔用既有 CT-001～096，也不是已有頁面的測試結果。

|ID|測試與通過要求|
|---|---|
|WEBUI-P01|無 Key 管理 API 503、錯 Key 401、正確 Key 才能讀寫；金鑰只存頁面記憶體，重整/關閉清除|
|WEBUI-P02|僅 localhost 同來源；拒絕非 loopback 綁定，無 public CORS、第三方 script、Key query|
|WEBUI-P03|新建帳號4/8英數成功，3/9/12字失敗、重名409、大小寫敏感、密碼不被瀏覽器持久存取|
|WEBUI-P04|按 ID 查帳號成功／404、XSS 文字安全呈現；P0 不宣稱已有帳號名稱搜尋|
|WEBUI-P05|指定天數及永久停權、解封的二次確認、重送/失敗回報及重新讀取|
|WEBUI-P06|密碼重設後舊 token/Session 無效、角色保留，Admin Key 可長於8字|
|WEBUI-P07|稽核只能授權查看；時間/結果明確，log/URL/console/network 不洩漏密碼/hash/token|
|WEBUI-P08|CSP/no-store/nosniff、禁止 HTML 注入、back/refresh 無殘留授權資料|
|WEBUI-P09|health live=200但ready=503時清楚顯示未就緒；Production 不暴露 Development-only 操作|
|WEBUI-P10|Windows Edge/Chrome 鍵盤操作、錯誤處理與 SQLite/PostgreSQL 兩種後端一致|

**本次不執行 UI 測試**。獲使用者實作確認後才將這些計畫轉為可執行 UI/E2E 測試。
