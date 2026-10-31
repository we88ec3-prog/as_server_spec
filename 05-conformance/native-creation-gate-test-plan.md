# 原版登入／創角兩入口：驗證與回覆（最新設計，未實機）

依使用者最新要求：**登入與創角是兩個獨立入口**。創角直接驗證本次輸入的帳號與密碼是否與管理端既有 Account 一致，不需先成功 C03。遊戲內改密碼是第三個獨立入口。所有 Client Native / GUI 測試仍 `planned/not-run`。

|情境|Server 預期結果|需要的原版 Client 證據|
|---|---|---|
|管理員建 A / 密碼4～8字；直接開創角填 A + 正確密碼|查唯一 Account、驗 PBKDF2/credential_version、未停權，建立只供創角的 proof，才回可觸發 C04 的 S02(success)|A-027 field1=account/field2=password 的原生 writer+UI、region差異；CT-097|
|直接創角填 A + 錯密（或不存在帳號 B）|同一種可見錯誤，不建草稿、角色或授權、**不觸發 C04**|A-027/A-028 原版 S02 非零 status 到具體提示字串；不猜錯誤碼|
|直接創角填 A + 不同大小寫的帳號 / 正確密碼|帳號 canonical 依管理端已有規則，若對應同一 account_id 則可通過身份檢查；密碼字元大小寫敏感|原 Client UI 若有額外輸入限制，另留記錄|
|C02 未帶可驗密碼、停權、已存在角色、錯區欄位、跨連線、重放|fail closed；C04 沒有有效 proof 則拒絕；沒有 Account INSERT 或 World Grant|CT-030/041/044/053；仍是安全設計，非 GUI passed|
|C02 正確 → C04 正確外觀|只存一次 Character+owner、S02 成功進正確 UI；取消/斷線/重送不可重複或刪已提交角色|A-028 0x1D→0x1E→S02 state，CT-097|
|管理員已建 A，從登入 UI 輸入錯／對帳密|C03 不建帳，錯密拒絕、成功才執行既有登入/轉服|CT-019/037；與創角流程各自驗證|
|遊戲原有改密碼 UI|成功後從兩入口使用**新密碼**，舊密碼都拒絕，帳號/角色不變|A-029、CT-098/099，native opcode 未明|
|已登入空角色是否自動開創角 UI|**非產品功能的必需條件**，只作補充觀察|原版 CT-054 保留研究結果，不再作直接創角開放先決|

**狀態**：本文件是規劃。Server / Client 都未就此要求重新測試，不能填原版錯誤 S02 數字、創角 UI 實際訊息或改密碼封包。詳 [安全權威流程](../02-server-planning/three-native-account-entry-policy.md)。
