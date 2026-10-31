# R-026：創角入口輸入帳密需符合管理端已建帳號（取代舊先 C03 登入政策）

**最新使用者決策（2026-10-31）**：原版登入與創角是**兩個獨立入口**。創角輸入的帳號和密碼須都符合 **Server 後端**既有 Account；不需先經過 C03 登入。正常改密碼必須走原版遊戲內修改密碼 UI。詳細見 [權威契約](three-native-account-entry-policy.md)。

## 創角時的後端判定（DESIGNED）

1. 管理員先建立 `Account(account_id,canonical_name,credential_hash,status)`；遊戲 Client 不可用 C02 建新 Account。
2. 玩家從原 Client NewUser/MakeInfoDialog 直接輸入「帳號＋密碼」與原版既有其他欄位。Server 依 **該原始 UI 已證對應的 C02 欄位**查既有 Account、用同一 `CredentialVerifier` 比對完整密碼（大小寫敏感，4～8 ASCII 英數）及停權狀態；**無 C03 Session 不構成拒絕理由，若本次 C02 自身憑證驗證成立即可**。
3. 錯帳號/錯密/停權/帳號不可創角 → 回傳原版 UI **可以顯示的錯誤**，不建立 Account/草稿/Character/WorldGrant，不發會誘發 C04 的 `S02(status0)`。目前 S02 native failure code/文字與 region UI 仍未知；**不能因要求錯誤回覆而捏造 status**，此 native route 先 fail closed，需 A-027/A-028 補證。
4. 正確 → 只建 `CreateAuthProof(account_id,credential_version,connection,generation,expiry)`（不能用它冒充 World 登入 grant），建立 owner 綁定 `PendingCharacterIntent`，回真 Client 已證能接受的 C02 階段成功 S02；再 C04 appearance 只在有效同一 proof/connection/generation 下原子保存一次 Character。
5. 同名/已有角色、錯外觀、C04 缺 C02、C15 取消/競爭與重送一律用持久唯一性、過期/世代、單次提交保護。Client **欄位自己比對密碼確認**不能取代 Server Hash 驗證。原版 CharacterName/AccountName 欄位語意與 region 0/1 差異仍須研究。
6. 角色成功後，玩家照原版登入 UI 使用同一既有帳密登入。**不假定 C04 成功的 UI 會自動進入 C03/S03/C10**；Client 真實回登入步驟仍待證。

**歷史舊政策已作廢**：先前本檔要求 `C03 已登入 AuthContext`、C02 欄位名稱與它相同才允許建角，**與使用者確認的雙入口不相容**。現在帳號一致性改成「本次 C02 帳號/密碼實際驗證結果指向 Server 同一筆 existing Account」，而不是「本次 C02 名稱必須等於先前登入帳號」。匿名只送帳號名或跳過密碼的 C02 仍必須拒絕；若不能確認密碼欄位原生 wire，暫不得開放創角成功。

[原生驗收](../05-conformance/native-creation-gate-test-plan.md) · [A-027 證據](../03-analysis-requests/A-027-roy1-identity-ui-security.md)。

## 2026-10-31 再確認：Guard 不需 C03（尚未改私有實作）

規格改為 C02 submitted **帳號和密碼**直接驗 existing Account 的 hash/status，無先前登入 `loggedIn` 要求；Server 可以建立 creation-only proof，但不直接建立 LoginSession。私有 `as_server_roy/main` 的 `CharacterCreationAccountGuard.RequireMatch` 仍是舊規則，屬明確的**DEV-040 待改項**，不能把本規格當成程式已修改。見 [新決策](three-policy-adjustments-20261031.md) 與 CT-100。
