# 原版 Client 三個獨立入口：登入、創角、遊戲內修改密碼（最新使用者決策）

**日期**：2026-10-31。**狀態**：`specified / Server changes not authorized / native Client E2E not-run`。本文件為 **Server-designed 產品契約**，優先於其他文件中「C03 必須先登入才可使用 C02 創角」的舊暫行假設。**不修改原始 `Asgard.exe`，不新增 Client 控制項，也不在本次實作 Server / Web。**

## 0. 使用者確認的不可混淆規則

1. **管理端建立 Account**：只有授權管理員能 `ProvisionAccount(account, initial_game_password)`。管理端不是一般玩家更改密碼的入口，不能把 C02 誤當 Account.Create。
2. **原生「登入」入口獨立**：玩家輸入既有 Account + Password，透過已分析的 C03 → S02/S03 → C10；Server 用目前同一帳號儲存的 credential verifier、停權/速率限制驗證，成功才可核發與角色綁定的 World grant。此路不創建 Account。
3. **原生「創角」入口獨立，無需先登入**：玩家可以直接開啟 NewUser/MakeInfoDialog。Server 必須以該入口所提交的 **既有帳號 + 正確密碼** 向同一後端資料庫驗證；帳號不存在、密碼不符、帳號被停權或已有不可重建的角色，均不得進入成功創角流程。帳號/密碼一致但只通過身份檢查，仍須合法角色欄位、唯一性及 C02→S02→C04→S02 的授權時序。**不得要求有事先的 C03 Session，也不得只比對帳號名字就授權**。
4. **遊戲內「更改密碼」入口獨立**：玩家正常更改密碼**必須透過 Client 原有更改密碼 UI**，不是跳去管理 Web。Server 驗目前持有的帳號和原密碼（或原生 UI 已證的等價可信 AuthContext），新密碼遵循原版 profile **4～8 ASCII 英數、大小寫敏感**、確認欄一致、不可剪裁與記明文；成功後只修改既有 Account credential，不刪 Character/進度。管理端 `credential-reset` 僅保留為管理員救援／首次建帳／遺失密碼時的明確授權程序，**不是玩家正常修改密碼的替代 UI**。
5. **三個入口同一 Account 身份/密碼資料來源**：任何修改成功，登入和創角之後都必須接受新密碼、拒絕舊密碼。Client 不能直寫 Account/DB、繞過驗證或自行宣稱成功。

## 1. 分離的 Server 命令與安全狀態

|原生入口|已證 / 待證線路|Server-owned 驗證、結果|前置 C03？|
|---|---|---|---|
|登入|C03 `name:string8,password:string8,flag:u8`，S02/S03/C10|帳號/密碼存在且相符、未停權、credential version；grant 屬該已保存角色|**此入口本身是 C03**|
|創角|NewUser UI → C02 region-dependent `string8` fields（第一欄為 account 候選、第二欄為 password 候選，見 A-027） → 成功 S02(status0) 觸發 C04 五u8 → C04 final S02|**從 C02 submitted account+password 直接驗證既有 Account**，建立 `CreateAuthProof(account_id,connection_generation,credential_version,expiry)`；綁同一連線的 `PendingCharacterIntent`，只提交 Character；錯誤返回原版 UI 可解析的失敗 S02（確切非零 status 待分析），不建立草稿|**不需要**|
|遊戲內改密碼|**使用者確認 UI 存在**；其 native packet/opcode/欄位/回覆 **未查明**（A-029 P0）|驗證現有憑證及新密碼/確認欄，原子更新 credential_version/revoke grants/sessions、只留去敏稽核；失敗不變更原帳號|**不預設需要**；以原版 UI 真實憑證欄位／已驗證狀態為準|

**重要安全條件**：C02 在 C03 前出現，是原 Client 靜態證據支持的真實可能；不能拿「尚未發 C03」當作拒絕合法創角的唯一理由，也不能因此把 C02 視為匿名免密碼權限。只有通過 Account Store 的密碼雜湊比對才能建立 creation-only AuthProof，並且該 AuthProof 只能用來完成創角，不可直接取得登入或 World grants。若 C02 region/field2 真用途未證或無法驗證 owner，正式 native policy 仍 **fail closed**，待 A-027 補證。

## 2. 創角詳細流程、錯誤及重放

```text
Admin → (creates Account with initial password)
                                  │
Native Login UI                  Native Create UI
 C03(name,password)                C02(name,password,region fields)
       │                                    │
 AccountVerifier                   AccountVerifier (same credential store)
       │                                    │
 valid → login/auth/grant          wrong/nonexistent/banned → fail reply, no draft
                                     valid → creation-only proof + pending intent
                                          → S02 success *only after proof*
                                          → C04 appearance (same connection/generation)
                                          → atomic Character INSERT bound account_id
                                          → S02 final UI result (not auto S03)
                                          → player may use Login UI normally

Native Change Password UI → native opcode UNKNOWN → account+old credential verification
   → new password+confirm → atomic credential update → old password rejected by both paths
```

- 使用原始 C02 region 2～4 的 **四個 string8 + flag** 與其他 region 的 **三個 string8**，不能假設多出來的欄位是任何認證 token。A-027 僅確認欄位來源：field1=UI 第一欄、field2=UI 第二欄且會跟確認控制比較；「帳號／密碼」為本次使用者指定的 Server **目標語意**，仍要研究證實相應 Client region 封包對齊。
- Server 按 Admin Account canonical-name 查帳號（既有管理帳號 3～32 ASCII 字母數字底線，大小寫不敏感）；密碼驗證大小寫**敏感**、不截斷、不 trim、不由任何 C02 可選欄位或 UI 本地確認結果代替。返回錯誤對「帳號不存在／密碼錯」使用**相同公開訊息/狀態**，避免帳號枚舉；真 S02(status!=0) code 與 UI focus/message 意義仍需 A-027/A-028 實際核對，**禁止亂猜某個 status 然後宣稱 native 成功**。
- 帳號被停權、角色已存在、異常字元或密碼長度不合法、並發重送、C04 缺有效 proof、別人 account、過期 proof 或不同連線必須拒絕；無 `S02(0)` 讓 Client 誤發 C04。失敗記錄 **去敏 reason**，不能透露明文、hash 或 token。
- C04 限持同一 `CreateAuthProof` / `PendingCharacterIntent` 的 connection + generation，一帳一角（目前保守新 Server 政策）及角色名稱唯一/外觀合法；DB transaction 原子提交，C15 只取消同 session 未提交 pending，不撤銷已提交角色。
- 本設計與原生 A-028 不衝突：**C02 的 S02(0) 不是創角完成**；C04 後 state0x1e 接另一個 S02(0) 才走 UI 完成，而不會當場自動 S03。回到登入的實際點擊/畫面仍待 A-028 native E2E。
- 密碼變更後，**登入與創角**都驗新密碼；舊密碼及所有跨階段短期授權失效。有效舊角色/進度不變；若更改過程斷線須有可確定的 DB commit 結果、不因回包丟失而誤恢復舊密碼。
- **4字密碼安全性較弱**：C03、C02 與改密碼 UI 都要 per-account+per-IP 登入/認證速率限制、通用錯誤、審計/告警和有界退避；不可只保護登入 C03。

## 3. 分析責任與驗收（皆未實機）

- **A-027/A-021**：追創角 NewUser UI 第一／二輸入與 C02 每個 region 的 writer，確證管理預建 Account 名稱/密碼的原版欄位，及 S02 非零錯誤碼/錯密 UI；**不再把 C03→NewUser 自動跳轉當必須存在的前置條件**。
- **A-028**：C02 初段成功/失敗 → C04 終局 S02(status0/非0)、C15、回登入 UI，真正原版互動與 DB status 的界線；只研究 Client 可證的顯示/封包。
- **A-029（新增）**：定位遊戲**原有更改密碼 UI**及其提交、欄位驗證、封包 opcode/writer、收到的結果 parser/UI、取消/重送與 regional profile。找到後才能開始在 Server 端實作真正 native 改密碼路徑；本次**不創造自訂遊戲 opcode**，也不要求新資源檔。
- **CT-097**：兩個入口分離、創角直接以原始帳密驗證及錯誤；**CT-098**：原版改密碼 UI 真人操作/封包/回覆；**CT-099**：改密碼成功/錯誤/並發、舊憑證失效與帳角不變；全部 `planned/native-client-validation=not-run`。

## 4. 實作權限界線

此文件**只更新 `as_server_spec` 規格**；私有 `as_server_roy` 是否要修改 C02 Auth Guard、加入 password-change wire handler、調整 Admin UI，都需另一次用戶明確授權／確認，尤其 Web UI 不得未經確認自行實作。既有 `Asgard.exe` 不是待改標的。

## 2026-10-31 創角 Guard 實際程式缺口（以本節為準）

最新使用者再次指定：**創角不需要已登入 Session**。私有 `as_server_roy/main@ad84f9fb11606a318aff6bd67e065aa0ee07cc45` 的 `CharacterCreationAccountGuard.RequireMatch(loggedIn, generation, submittedAccount)` 與 `AuthenticatedCharacterCreation.BeginFromClientAsync` 仍要求先登入，**尚未實作與規劃一致的直接 C02 帳密驗證**。不能僅刪 `loggedIn` null check 就讓任何 C02 認領帳號；後續 Server 開發應用 **C02 本次 submittedAccount+submittedPassword → 與後端比對 → 簽發限本次創角的 proof (account_id,credential_version,connection,generation,TTL) → pending C04** 代替 Guard 的「已登入身分姓名一致」門檻。原 Client C02 第二欄語意、錯密 S02 回覆仍需 A-027/028；未查實前 live native 路由繼續安全拒絕。詳 [三項決策](three-policy-adjustments-20261031.md) 與 [CT-100](../05-conformance/native-creation-gate-test-plan.md)。


## A-029 原生靜態結果（2026-10-31；更新此節，取代上面「wire UNKNOWN」的歷史描述）

**已取得原 Client 的更改密碼封包**：`PKT-C26` C2S opcode **0x26**，原 `CChangePasswordPacket` ctor `0x571a10/0x571a29`，writer `0x571ac0` 依序三個 `string8`：（1）原生 UI control8 的 Account 候選，（2）control9 舊密碼，（3）control10 新密碼。control11 再輸入新密碼只在本地確認相等，不在 wire；新舊密碼相同時也只本地提示並拒送。原生 widget 對密碼 controls9～11 設 UI length 8。所需 Client opcode **不再未知，絕不自造 opcode**。

S→C 走共用 `PKT-S02` selector2→`0x4a8d60` status/UI callback，**專屬 C26 的成功、舊密碼錯、停權等 S02 status-to-UI 意義仍 unknown，原生 Client GUI 未測**。所以只開放規格的 C26 decoder/authority 設計，不能宣稱改密碼 E2E 已可正式上線；`4～8 ASCII 英數` 仍由新 Server 執行帳號 policy（本次未由原版完整驗證 4 字下限與字元集）。原 Account 同時供 C03 登入與 C02 無前置登入直接創角，原子 credential rotation / char retention / revoke 仍是 Server 設計，不能當作原版 Server 事實。本次只改 `as_server_spec`；未觸碰 Server 或管理 Web。詳 [A-029](../03-analysis-requests/A-029-roy1-native-password-change.md)、[契約](../04-analysis-integration/A-029-native-password-change-contract.md)、[CT-098/099](../05-conformance/account-password-native-change-test-plan.md)。
