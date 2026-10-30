# A-027 — C02 預建帳號認領的安全邊界（BIN 與 DEV 交接）

來源：[A-027 roy1 深入分析](../03-analysis-requests/A-027-roy1-identity-ui-security.md)；證據 ev_a027_20261031_asgard_identity_static；Client SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。研究為 observed-static；下述 Server 權限與 fail-closed 判決屬 designed。

## 原版 Client 已有可追溯證據

- 0x5742B0 C02 writer：region2..4 的 4×string8+u8、其他 region 的 3×string8。0x4B27B5 / 0x4B27D6 從 NewUser UI 的 Dialog+0x26C / +0x270 產出前兩欄。
- 0x4B27F7..0x4B2811 將 Dialog+0x274 的文字放進局部暫存；0x5B4A62 是 UTF-16 逐 word 比較；0x4B2900..0x4B2916 把 field2 與確認輸入相等比較。故 field2 很可能是密碼類欄位，但**原生標籤與 Server 預建帳號憑證契約尚未證實**。Confirm 值不是附帶的 token。
- 0x4B1A30 對 first UI field 做 region-dependent 文字長度 gate；非所有 region 同一條件。0x4B2858..0x4B28CD 延伸欄位 UI controls 0x17/18（region4）、0x0F/10（其他非0）。0x4B2825 對 region0 使用 ID0x0A／packet+0x424；region1 的 UI/writer 對照仍有待釐清。
- 0x4B2360 確認視窗 callback 0x4B21E0，事件1 發 C02 並進 state0x1D；0x4B2340 只接受 S02；state0x1D + S02(status0) 就發 C04 並進 0x1E。**返回 status0 是授權敏感動作，不是無害 ACK**。
- 0x4AEF08 / 0x4B0B67 可建立 MakeInfoDialog。未證明「C03 成功登入角色為空的已預建帳號」會自動進此 UI；C02 在 C03 前送出亦不代表帳號已登入。

## Pre-auth 與權限的強制狀態機（designed）

1. Account 只可由 Admin.ProvisionAccount 建立；Client C02 只在協定層被解析。未證明 Account owner 前，NO_AUTH_CLAIM；不能建立 Account、改憑證、建立角色、產生 PendingCharacterIntent、S02(status0) 或 World grant。
2. 只有 **server-side 已驗證身分** 可取得 AuthContext（含 account_id、connection_generation、期限）；必須對該帳號與角色草稿授權。要開放 C02 以前，需先證明原生 Client 的哪條線路能安全完成身分驗證（C03→可達 NewUser UI，或 C02 經認證的 password/token），不能自行推定帳號名稱即 owner。
3. 若已獲可信 AuthContext，C02 欄位的 UI/codec 檢查只是輸入格式、確認及正常顯示。正式 Server 再檢查 account status、資格、角色唯一性、原生 Client 所能送出的合法欄位。任何分支不符拒絕，且無寫入。
4. C02 的 S02 success 只能在正確已認證 owner + PendingCreateIntent 已確認時使用；後續 C04 外觀輸入需要相同 session/generation 且一次性使用。C04 最終回覆與提交時點仍由 A-028 判定，**本報告未將其冒認完成**。
5. 同帳號競態由 Server 原子唯一性與 generation 綁定保護；Client 不可信的 Name/Flag/Confirm 字串一律不能變成授權判決。

## 可用性與阻塞分別表達

- **A-027 研究 integrated、handoff partial**：UI 字段來源、第一欄本地長度 gate、第二欄與確認輸入的 UTF-16 相等、region 尾欄、S02→C04 的觸發條件已交付。
- **原版管理預建帳號認領路由 blocked / implementation_ready=false**：目前無已證的 pre-C03 Account ownership credential，也無 C03(no character)→MakeInfoDialog native auto-transition。開發可以先完成無權限 decoder、格式與 domain 授權守衛及 CT-041/042；不能直接把 C02 視為 Account 或 Character 的授權意圖。
- 若後續取得獨立 native 資源/原服 trace，更新此契約及 A-021/A-028；Server 開發完成後 CT 驗證另行記錄，不因本次 Client CT not-run 而停止逆向研究。

參見 03-analysis-requests/requests.json，SCN-007/008，CT-029/030/031/032，CT-041/042。
