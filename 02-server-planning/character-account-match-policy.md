# R-026 — 創角輸入帳號必須匹配登入帳號（暫行 Server 政策）

## 暫行創角帳號比對政策（使用者決策，2026-10-31）

**不修改 Client，也不禁止編輯原生帳號輸入框。** 在原 Client 的 NewUser/C02 第一欄被確認為帳號欄、且存在與此創角會話相同 generation 的 Server 已驗證登入 Account 後，Server 只接受 **輸入帳號與該登入帳號相同** 的創角請求；不符必須失敗，且不得建立 PendingCharacterIntent/Character、改別人帳號、核發 Grant 或送會觸發 C04 的 S02(status0)。帳號相等依現有管理帳號規格使用 3～32 ASCII 字母/數字/底線且大小寫不敏感比較（不 trim、無別名），實際角色 owner 一律使用 Server account_id。

**無有效登入 AuthContext → 一律拒絕**，即使字串剛好相同；匹配成功只通過此檢查，另需帳號未停權、有效 session/generation、角色/外觀唯一性等規則。A-027 仍未確認 C03 無角色→NewUser 原生可達及 C02 第1欄確為既有登入帳號，因此正式 native C02/C04 仍必須 fail closed，直到證據足夠；不得把原服註冊 UI 直接當作新 Server 的角色創建授權。原生錯誤回覆 status 尚未知：拒絕時不得發 S02(status0) 或亂猜 status；目前安全實作可結束未授權連線。這是 **Server designed**，不宣稱原版原本有相同限制。

## 處理順序（DESIGNED）

1. Session 具有先前成功的 C03 身份驗證，讀取 `authenticated_account_id`、`authenticated_account_name`、`session_generation`；不得從 C02 欄位生成 AuthContext。
2. 按 Client profile 正確解析 C02，且證實第一欄原生用途符合帳號輸入。比對 `submitted_account_name` 與已驗證的 account name（ASCII case-insensitive，完全不修剪）。
3. 不相同、無登入、過期/停權/舊世代：立即拒絕；**禁止建立 PendingIntent/Character，禁止 S02(0) 觸發 C04**。如原生失敗 S02 非零碼未知，採 fail closed 而不是猜錯誤代碼。
4. 相同：繼續驗證其他條件，於 Server 建立同一 account_id + generation 的草稿；C04 必須對應同一草稿、只持久保存一次。
5. 不變更 `Asgard.exe`，不禁用、不自動填入帳號欄。若 C03→NewUser 原生流程無證據，C02 在登入前送達仍保持拒絕。

## 對應驗收（CT-041/044/053）

- 帳號 A 已登入，C02 第一欄為 B → 拒絕、不建草稿、角色、grant；B 帳號不受影響。
- 已登入 A，C02 第一欄大小寫不同但 canonical 同帳號 → 僅通過名稱一致檢查，仍受其他創角條件限制。
- 無登入的 C02 填 A → 拒絕；登入後另一個 connection/generation 的 C02 → 拒絕；登入 A 但停權/失效 → 拒絕。
- C04 無已認證且匹配的 C02 pending → 拒絕；帳號 A 的 C15 不可刪 B 或已提交角色。

此頁只更新設計與合成測試預期，原生 Client E2E 尚未完成。
