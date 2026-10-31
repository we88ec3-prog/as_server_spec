# 原版創角 E-MAIL 單純保存契約（2026-11-01）

**狀態：R-035 產品決策已確認；僅 Spec/DEV 規劃，Server/DB 未改、Client 原生 E2E 未驗收。** 本契約取代 2026-10-31「E-MAIL 可不儲存」的舊候選，不改 A-030 客戶端證據分級。

## 產品範圍
- 原版 `Asgard.exe` 創角輸入的 E-MAIL，Server 必須保存，但**目前只有保存，沒有其他用途**。
- 對已由管理端建立的既有 Account 增加 nullable 欄位 `creation_email`。SQLite：`accounts.creation_email TEXT NULL`；PostgreSQL：`asgard_accounts.creation_email TEXT NULL`。以 account_id 為擁有者，**不建立另一個 Account**，不把它當 Character name／登入憑證。
- 確認 C02 帳號及密碼成功且有綁定 owner/connection/generation/credential_version 的 creation-only proof，待 C04 五個外觀位元組通過驗證，**同一 DB transaction 一起原子寫入 Character、Appearance、onboarding 初始資料與 Account.creation_email**；commit 成功才發最終 S02(0)。C02 先認證或建立 pending 時不得先寫入 E-MAIL。
- 錯密／帳號不存在／停權／重名／非法欄位／未授權 C04／C15 取消／失敗／未提交／逾時／rollback 時 E-MAIL 不可更新；已成功建角後重送不得覆寫。帳號間不得交叉寫入。
- **既有帳號沒有來源值保持 NULL**。可已證傳入空字串的 profile 若允許空值，保存空字串 `""`；不可拿 NULL、空值推斷 E-MAIL 是必填。保留原生 CP950/string8 解碼文字，不 trim、lowercase 或自訂格式驗證，僅檢查原協定及儲存安全範圍。
- A-030 靜態證據確認 region 2–4 C02 具 F3/F4，**沒有確認 F4 就是 E-MAIL、F3 就是 NAME**；region1 的 UI→writer 不一致。只有拿到原 Client 真實 UI label、widget、region 與匿名化 C02 對照才能啟用欄位映射。不可因需要存信箱就猜欄位、篡改 EXE 或發明封包；未知時 native adapter fail-closed。

## 暫不規劃任何額外用途
E-MAIL **不得**用於身份驗證、登入、密碼重設、帳號救援、郵件寄送、電子郵件驗證、通知、行銷、欄位唯一性、索引搜索、Admin UI 顯示或 API 回傳。若未來有用途，另行決策。不要把 E-MAIL 放在普通錯誤、稽核、Console、TCP trace、decrypted C02 dump 或憑證日誌；備份與 DB 權限按個資處理。

## DEV-CREATE-EMAIL 實作交接（本次不修改 Server）
1. SQLite/Pg **schema v5**：新建庫含欄位、現有 v1–v4 平滑 migration（SQLite `PRAGMA user_version`、Pg `asgard_schema_migrations`）；既有所有 migration initializer 的最高支援版本與 v5 同步，不能有「newer than known v4」。保留 Account、Character、ban、credential_version、密碼 hash、進度。更新前備份。
2. 建立 server-only email value 傳遞（C02 已驗證 field → PendingCharacterIntent/creation service → CharacterCreationStore.CompleteDraft transaction），不可讓不可信 C02 改寫 Account。不應改變 C03 登入、C26 更改密碼、現有 Admin API 或 Web UI。
3. C04 transaction 使用 parameterized SQL，從已驗證 account_id 定位單一既有 row，在角色成功提交時單次寫入；DB error rollback 全部；成功 retry 取既有結果，不能更新 E-MAIL。
4. 先做 DB/domain 合成測試，再做原版 Asgard.exe 真實 UI／wire 對照；不得將 domain PASS 當作 native PASS。

## CT-106 驗收
- SQLite/PostgreSQL 新 DB／v4 升 v5 與重啟，舊帳密狀態/角色均保留、E-MAIL default NULL。
- 成功的原版或先經明確映射的合成 C02+ C04，`creation_email` 只在對應 Account 跟 Character 同交易提交，文字準確、可持久讀取；正負案例嚴格隔離。
- 失敗、C15、斷線、交易 rollback 無部分寫入；重放已成功 C04 不覆寫；不意外把 NAME 存信箱。
- 不增加必填、正規化、唯一、驗證、寄信、登入或管理功能；不外洩敏感值，原版 Client E2E 與 synthetic 分開標示。

追蹤：R-026/R-035、A-030、ONB-02、PKT-C02/C04/S02/C15、SCN-008、CT-105/CT-106。
