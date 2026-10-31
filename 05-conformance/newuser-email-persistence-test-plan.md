# 創角 E-MAIL 僅保存：CT-106 驗收規劃

**planned / DB 未實作 / 原版 Client not-run**。先由 A-030 證實正確 region/widget/C02 欄位，不能將 F4=E-MAIL 的假說當原生事實。

1. SQLite `accounts`、PostgreSQL `asgard_accounts` 新庫及現有 v4 版本升級到 v5，`creation_email TEXT NULL`。確認舊資料、密碼版本、角色、停權不變，重啟可讀。
2. 預建 Account A/B：A 的合法 C02/C04 完成創角，同 transaction 寫 A 的信箱／角色；B 不變。檢查原文 CP950 字元、已證的空字串與 legacy NULL。
3. 錯密、停權、重名、非法 C04、不同帳號/連線/generation、C15、逾時、crash/rollback 均不得更新 E-MAIL；重送已提交的 C04 不覆寫也不重複建角。
4. 確認 C03 認證、C26 修改密碼、Admin API/UI、Audit／trace、通知與找回密碼均**不使用、不回傳** E-MAIL。
5. 原版 Asgard.exe E2E 獨立比對真 UI E-MAIL label 與去敏 C02 field，確認 region、空白值以及成功/失敗行為；未做保留 not-run。

規格：[E-MAIL 保存契約](../02-server-planning/newuser-email-persistence-20261101.md)。
