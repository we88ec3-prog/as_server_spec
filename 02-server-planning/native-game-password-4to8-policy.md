# P0：原版 Client 遊戲帳號密碼 4～8 字元（取代固定 8 字規劃）

**2026-10-31 最新使用者決策**：目前遊戲帳號密碼允許 **4～8 個字元**；未來可能修改主程式改善長度限制，**目前不修改 `Asgard.exe`，亦未授權啟用修改版 Client**。本規格優先於先前「恰好 8 字」版本；舊文件 [8char-policy](native-game-password-8char-policy.md) 保留導引以避免既有連結失效。

適用：R-025 / ONB-01 / DEV-030、CT-019 / CT-037 / CT-050；目前規格 `specified`、私有 Server 變更 `not-reported`、原版 Client E2E `not-run`。這是新 Server 的**設計規則**，不是原服密碼長度已全面逆向證實。

## 事實和責任邊界

- 使用者觀察：原始登入框最多輸入 **8 字元**；待 A-020/A-002 於原版 EXE 的 C03 password field xref、UI paste/鍵入、CP950/string8 實際 byte stream 再確認（`reported-client-UI`）。
- 截至本規劃編寫，`as_server_roy/main` 的 `src/Asgard.Server.Infrastructure/Pbkdf2PasswordHasher.cs` `ValidatePassword` 要求 **10～128 字**，不符合原生 Client 輸入限制；SQLite / PostgreSQL 的 `CreateAsync`、`ResetPasswordAsync` 均調用這個檢查。不能把原先的「最少12字」當程式已驗證事實。
- 此處限制的是管理員發給玩家、供 `C03` 登入使用的**遊戲密碼**，**不是**管理員 `X-Admin-Key` / 獨立管理身份密碼，也不是 C02 創角某個 region 的長度門檻。

## 密碼規則：TW-native-password-4to8（Server designed）

|欄位|規則|
|---|---|
|遊戲帳號密碼新建／重設|接受 **4～8 個 ASCII 英文字母或數字**，正則 `^[A-Za-z0-9]{4,8}$`；大小寫**敏感**；不做 `trim`、大小寫折疊、截斷、前綴比對或靜默替換。這沿用先前 ASCII 英數保守字元範圍，**僅改長度**。|
|邊界|3 字拒絕；4、5、6、7、8 字接受；9 字以上拒絕；含空白／控制字／符號／非 ASCII 均依本 profile 拒絕，禁止將 Unicode 字元數和 CP950 bytes 混淆。|
|管理員建帳|Account 只能由管理後台建立；允許依規則輸入 4～8 字；**自動產生時建議永遠選 8 位安全隨機英數**，不要因最低4字而生成弱密碼；禁止可預測固定初始密碼。|
|重設密碼|相同 4～8 字；保留原本 account_id／角色／進度；更新 credential_version、撤銷舊 login/world/session/transfer grant（在能安全落地的既有操作範圍內），不可將長密碼直接截成 8 或 4 字。|
|身分與儲存|沿用帶鹽的強雜湊（現有 PBKDF2-HMAC-SHA256）；固定時間比對，審計紀錄與例外不得包含遊戲密碼或 C03 原始 body；管理員身份不降級。|
|防暴力登入|因容許 **4 字極短密碼**，必須有帳號與來源 IP 多層速率限制、逐步延遲／有界暫停、通用錯誤、警示及管理端重設手段；避免攻擊者造成永久鎖帳。這是原生相容性下的**高優先風險補償**，不是宣稱 4 字密碼本身安全。|
|既存長密碼帳號|既有 10+ 字的 hash 不變、角色不刪；須由授權管理員安全重設為 4～8 字後才能按原版 UI 登入。絕不能不經本人確認就只驗前 8 字。|

## DEV-030 交接：只更新 Server，不能私改 Client

1. 將 `Pbkdf2PasswordHasher.ValidatePassword` 的舊 10～128 邊界拆成遊戲帳號專用 policy（建議 `TwNativeGamePasswordPolicy`，避免沿用固定「8」的類別名稱）。**對 Create/Reset 統一驗 `4 <= ASCII length <= 8`**；Hash／Verify 不變，Admin key 原強度不受影響。
2. `SqliteAccountStore.CreateAsync / ResetPasswordAsync` 與 `PostgresAccountStore.CreateAsync / ResetPasswordAsync` 必須套相同的遊戲規則；`AdminAccountEndpoints` 回傳合法的錯誤提示，不暴露憑證／持久化明文。
3. 調整既有測試中的超過8字 fixture，例如 `passphrase-is-long-enough`、`initial-password-123`，不要再用它們當合法建帳；可保留成「應拒絕」測試。以 4/5/6/7/8 字邊界、大小寫、錯密、重設、停權、併發與 SQLite/PostgreSQL 交叉驗收。
4. 補 `C03` decoded body 的 ASCII `string8` 4字與8字可重現向量；原始 Client 以相同帳號及合法新密碼做登入／轉服測試，記錄 Client SHA、Server version、去敏封包與畫面，未實測前不宣稱 CT PASS。
5. 限速、防撞庫與管理端安全重設的保護不可因本次放寬最短長度而取消；Admin `X-Admin-Key`、管理員身分認證不受遊戲密碼 4～8 上限拘束。
6. Server 使用 client-profile 明確記錄登入憑證的允許字元／長度；不得從登入字串長度猜測正在用哪一版 Client，亦不得讓一個帳號在不同政策下被無意義截短後驗證。

## 將來可能修改 Asgard.exe 的相容擴充（**未授權、未啟用**）

- 原版 profile：`TW-original` 目前保守使用 **4～8**，不可因為未來計畫而默默接受 >8 並宣稱原版可登入。
- 未來**確實修改**原 Client 時，須另外批准修改、建立相符的**Client build SHA / profile / 最大長度 / C03 實際 wire encoding** 的證據；才允許針對該 client profile 提高上限（例如 8 字以上）。不預設一定可以，也不預設是 12/16/128。
- 優先讓帳號資料與 PBKDF2 hash 無需 schema 改動；變更驗證政策的版本與升級路徑要能追蹤。舊原版 Client 的登入相容性仍是獨立 Gate；若使用者選擇只支援修改版，需明確記錄產品決策。
- 一律由 Server 進行身份驗證，Client 端文字限制變更不得繞過權限、停權、token、World generation 或帳號/角色綁定。

## CT / A 的接受條件（現為 planned、not-run）

- **CT-019（Admin/登入）**：4/5/6/7/8 字 ASCII 英數建帳成功，3/9/10/12 字及空白、控制字、符號、非 ASCII 拒絕；錯密、停權、無效/未授權 C02 仍不能登入或建 Account。
- **CT-050（Admin reset）**：4與8字重設、儲存後重新登入、credential_version、grant 撤銷、角色資料持久一致；管理員 key 可長於8字。
- **CT-037（原版 Client）**：兩端測 4 字與 8 字真實輸入、C03 送包與認證成功，9字無法當成通過；錯密仍回錯且不洩漏帳號狀態。
- **A-020/A-002**：確定原版 UI 最長字元與實際 C03 送出的 bytes、是否有特殊字符／貼上路徑。A 的研究狀態與 CT 的通過狀態不混用。

這次僅更新共用規格／開發交接文件，不觸及私人 Server 或原版 Client 的執行檔。

## 最新增補：遊戲內原生更改密碼是正常玩家操作（2026-10-31）

最新使用者決策：**登入 C03、創角 C02、遊戲內更改密碼 UI 為三個不同入口**，三者採同一資料庫 Account/credential；創角無需先用 C03 登入，必須直接核對本次輸入的既有帳號與密碼。玩家正常更改密碼**只走遊戲原版 UI**，Server 驗舊憑證與新4～8字設定，成功原子更新 password hash 和 credential_version、撤銷舊 grant/sessions；管理員 `/admin/.../credential-reset` 僅限緊急救援／遺失密碼。原版 UI 的 opcode、欄位、回應尚缺 **A-029**；不許創建想像的新封包。**先前提到私有 DEV-030 還需修改10～128字是歷史狀態，最新版私有 Server 已完成4～8字程式修正**；原生改密碼 handler 尚未完成。詳細見 [三入口規格](three-native-account-entry-policy.md)。
