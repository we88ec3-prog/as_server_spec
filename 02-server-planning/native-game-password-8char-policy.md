# P0：原版 Client 八字密碼上限與 Server DEV-030 相容性修正

日期：2026-10-31。歸屬：R-025 / ONB-01 / DEV-030 / CT-019、CT-037、CT-050；原 Client 不修改。**狀態：規劃已提出；私有 Server 尚未依本次變更實作或驗收**。

## 問題與證據分級

- **使用者在原版遊戲畫面實際觀察**：登入密碼輸入框最多可輸入 **8 個字元**。此為 `reported-client-UI`，**尚未以 Asgard.exe xref/實際 C03 bytes 獨立證明**。待 A-020/A-002 定點確認 UI 的 max length、剪貼/貼上、CP950 編碼與 C03 傳輸的實際字節。
- **直接核對現有私有 Server main**：`as_server_roy/src/Asgard.Server.Infrastructure/Pbkdf2PasswordHasher.cs` 的 `ValidatePassword` 目前要求 **10～128 字元**（並非本次使用者描述的最少 12 字）。`Hash()` 會呼叫此 validator，SQLite/PostgreSQL 的 `CreateAsync` 與 `ResetPasswordAsync` 再呼叫同一規則；已建立超長密碼即使有對應 hash，原 Client 也不能輸入完整密碼。
- **切勿混淆**：A-003/C02 某些 region 的本地長度門檻（例如 >=12）屬**新使用者/創角 UI 另一欄位**，不得作為 C03 **遊戲登入密碼**的長度政策。C03 wire 是 `string8(name), string8(password), flag`，但 string8 的 1-byte 長度前綴並不證實原 UI 支援超過 8 字。
- **本次決策是 Server designed 相容 profile**，不是已還原原服密碼規則；安全優先採 8 字元**全 ASCII 英數**，避開中文字/多 byte/鍵盤轉碼歧義。

## R-025 / ONB-01 新 Server 密碼契約（TW-native-8）

|用途|限制/行為|
|---|---|
|**遊戲帳號密碼**（原 Client C03）|新建、管理員重設：**恰好 8 個 ASCII 英數字元 [A-Za-z0-9]**，因此輸入 8 字元=8 bytes；大小寫敏感；**絕不可自動裁切**。選擇恰好 8 是本 Server 的保守安全政策，不宣稱原版不接受少於 8。|
|管理員建立帳號|只有後台能建立 Account；建議後台用**密碼學安全亂數**均勻產生 8 位英數，交付管道安全且只顯示一次；手動指定時也驗相同的 8 字規則。不能使用序號、帳號名、固定前綴、連號或僅用時間生成。|
|管理員重設遊戲密碼|同 8 字規則；保留 account_id、角色/任務，增加 `credential_version`，撤銷已有授權及有效 World/transfer grants，審計不存明文。不可單純在原長 hash 前8字做比較。|
|管理後台登入/密鑰|**完全獨立**；現有 `X-Admin-Key`、管理權限及強憑證政策不縮短到8字，遊戲玩家無 Admin API 權限。|
|密碼儲存|維持強雜湊（現有實作為 PBKDF2-HMAC-SHA256 + 獨立 salt，310,000 iterations）；儲存 hash 與參數，登入固定時間校驗；不 log 明文或 C03 密碼 body。|
|短密碼的線上安全補償|同時按帳號及來源 IP 限速；連錯逐步延遲/暫時阻擋、可設定上限與解除方式，避免被惡意永久鎖帳；通用錯誤，不暴露帳號是否存在/停權；對多來源攻擊有觀測/告警。**不能把短密碼風險推給 Client。**|
|已存在的 10+ 字遊戲密碼|標記為需要經管理員安全重設為新 8 字密碼後才能用原版 Client 登入；**不自動截斷、不復原明文、不重新建立角色、不消除舊 hash**。原始 hash 仍可先留作版本化遷移記錄，但不能作 8 字相容登入繞過。|

**相容性上線規則**：DEV-030 實作修正後，先用新的 8 字遊戲帳號做原生 C03 登入測試，必須確認 Client 真送出完整 8 字、Server 正確核驗，且可用不變的權限/轉服規則。若 Client 實際有自動大小寫轉換、全半形或特別字元行為，應補 A-020/A-002 與 profile 修正；目前**不能**因本需求規劃就把 `CT-019/037` 標成 passed。

## DEV-030 開發者具體修正清單（不修改此規格 repo 中的私有程式碼）

1. `Pbkdf2PasswordHasher.ValidatePassword()` 目前 `password.Length < 10 || >128`，拆成**遊戲密碼專用** `ValidateGamePassword` / `TwNative8CredentialPolicy`：只能 `^[A-Za-z0-9]{8}$`；維持 Hash 與 Verify 的 salt/PBKDF2 行為。避免將遊戲限制套到 Admin key/其他未來管理身份。
2. `SqliteAccountStore.CreateAsync / ResetPasswordAsync` 及 `PostgresAccountStore.CreateAsync / ResetPasswordAsync` 接同一個遊戲憑證政策；`AdminAccountEndpoints` 的建立帳號與 `/accounts/{id}/credential-reset` 明確傳回安全的驗證錯誤，不記明文、不截斷。
3. 改寫先前用 `passphrase-is-long-enough` / `initial-password-123` / `new-password-1234` 等**長度大於8**的整合測試資料；保留這些舊長密碼作**應被拒絕**的負面案例。
4. 增加 boundary/regression：7/8/9/10/12字、含多 byte 字元、空白、特殊字元；8 位英數大小寫敏感、原始 C03 string8 長度、錯誤密碼、停權、重設撤銷舊 grant、已有角色重登入。SQLite/PostgreSQL 共用相同政策；以新建/重設端完整驗收。
5. 既有資料庫 hash 格式不用因密碼長度修改；建立受控遷移/通知流程，安全地重新提供 8 字密碼，勿把新規則改成「只比對前8字」來繞過原本長密碼 hash。
6. 暫存線上保護：帳號及 IP 多層節流、延遲/防暴力嘗試，記錄不含任何密碼/packet-body 的成功失敗原因；不可把網路封包 `C02` 當成管理員建帳入口。

## CT 驗收（全部未執行，無新增正式 CT 編號）

- **CT-019** 管理員建帳／拒絕 Client 建帳、錯密/停權，新增「8字合法、7/9/10/12字拒絕、既存長密碼要求重設、角色資料不變」。
- **CT-050** 管理 API / reset 的 8字政策：SQLite+PostgreSQL；跨重設密碼、舊 token 無效；Admin key 不受8字上限影響。
- **CT-037** 真實原版 Client C03 的 8字輸入→送包→驗證→S03/C10，不可用 mock packet pass 假裝原生 UI 通過。
- **A-020/A-002** BIN/UI xref：精確輸入框最大可輸入字符、貼上/非 ASCII 的結果、C03 是否字節長度8；如與使用者觀察不同，回開本相容 profile，勿改原始 Client。

**DEV 的最短解鎖**：這是登入前置 P0，應優先於多人世界/新手教學原生 E2E；A 的更細節逆向可與開發並行，不要求為了找原服官方密碼政策而停止 Server 安全修復。
