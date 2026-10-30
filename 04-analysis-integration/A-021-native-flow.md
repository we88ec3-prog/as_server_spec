# A-021 原 Client 創角收發：靜態可證子集

來源：[`A-021 roy1 靜態報告`](../03-analysis-requests/A-021-roy1-static-analysis.md)；Evidence `ev_a021_20261031_asgard_static`；Client SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

| 原生路徑 | Body（已驗證） | 對 Server 的規格影響 | 不得聲稱 |
|---|---|---|---|
| C02 serializer `0x5742b0`，UI 發送 `0x4b229f` | region 2..4：4×string8 + u8；其他：3×string8 | 必須按 region/profile 辨識欄位及嚴格限定合法前置狀態 | field1..4 語意或 Client 一定在無角帳號時進入 UI |
| S02 parser `0x57dbc0`，UI callback `0x4b1d60` | u8 status + string8 message | status=0 且 UI state 0x1d 的分支將發 C04；登入/創角不同狀態不能混用 status code 表 | 所有錯誤碼含義與取消行為已知 |
| C04 serializer `0x574420`，UI 發送 `0x4b205a` | u8 sex + u8 hair + RGB 3 bytes | 僅經前置成功路徑處理，應為每次 Session/角色操作關聯，並行/重送由 Server 保護 | 收到 C04 就表示已建立持久角色、必須立即發 S03 |

靜態 UI 路徑：事件 1→C02→state=0x1d→S02(status0)→C04→state=0x1e。帳號是否由 C02 建立、C03 無角帳號如何到此 UI、C04 後轉服與實際建角回覆仍 `unknown`。**R-025 是 Server 設計要求：Client 永遠不得建立 Account**；不可假借原生 C02 的名稱解除此限制。SCN-008、CT-011..014/018/019 維持待實機驗收。

合成 body 向量（非抓包）：C02/四字串 `016101620163016401`；C02/三字串 `016101620163`；C04 `0102112233`；S02 status0 + 空訊息 `0000`。未知字串語意不得在實作中命名為帳密或角色名。

## A-021 靜態分析完成後的 Server 契約

參見 [深入追查與相容設計](../03-analysis-requests/A-021-roy1-followup.md)。C02 原生 `MakeInfoDialog` 在 C03 之前即可建立並送出，`0x4B2764→0x4B279E` 從原生控制輸入欄位生成 C02，`0x4B21E0/0x4B229F` 送出後 state=0x1d，S02(status0) `0x4B1F46` 觸發 C04 `0x4B2031..0x4B205A`；C04 後 state=0x1e。**不能要求 C02 必須已有 C03 已登入 Session**。**A-027 安全勘誤（取代這項早期 designed 建議）**：C02 只能在 Protocol 層解析；目前**不得**僅憑 C02 claim/authenticate 已預建 Account，亦不得 INSERT Account。必須先有經 Server 驗證的 Account owner/AuthContext 和原生可達流程證據，才能允許 pending create；C04 再與 pending lease 綁定，一次交易完成 Character + Appearance；後續以 C03/S03/C10 正常登入進圖。無角帳號直接 C03 時不可擅自進 World，原 UI 是否會自動切創角未證明，以 NewUser UI 作 designed 暫定替代。A-021 `integrated` 但 CT 仍 `planned`。

## A-027 / roy1 重新校核 C02 的 UI 字段與權限（2026-10-31）

[原始研究](../03-analysis-requests/A-027-roy1-identity-ui-security.md) / [04 安全交接](A-027-preauth-safety-contract.md)：C02 field1 對應 UI+0x26C、field2 對應 UI+0x270，另有 UI+0x274 作 UTF-16 確認相等比較，region2..4 的其他欄位源自區域控制；這是 Client 本地驗證，**不是** Server owner 憑證。原生預建帳號的認領驗證、C03 無角色後切入 MakeInfoDialog 尚未證實，因此 native account-claim route=blocked、A-027 static handoff=partial，Protocol/Domain 的 no-auth fail-closed 可開發。C02 收到 S02 success 會促發 C04，禁止無驗證成功。A-028 仍負責 C04 最後狀態/提交。

## A-028 / roy1：C04 後 S02 與 CancelNewUser 終局（2026-10-31）

[A-028 原生證據](../03-analysis-requests/A-028-roy1-c04-terminal-analysis.md)／[可用 Server 安全交接](A-028-newuser-terminal-contract.md)：MakeInfoDialog 在 0x1d 收 S02(status0) 傳 C04 並進 0x1e；**在 0x1e 再收 S02(status0) 時走 0x4b206b 的 local UI 成功路徑，不會在這個 callback 立即發 C03/S03**。收到 S02(nonzero) 會呼叫 C15 CancelNewUser constructor 0x5715f0、發 opcode0x15 **空 body**（serializer 0x5716a0），state 改成 0x1f；code3/4/18/26/31 讓 first edit focus，code17 second edit focus，具體原服錯誤名稱仍 unknown。A-027 原生 owner route / 原服 DB durable commit / 之後重登轉服仍未證實，**不能因 A-028 integrated/partial 就授權 C02 或盲送 S03**。CT-031/032/041/042 planned。

## A-003：十色盤與原生字串長度補證（2026-10-31）

[A-003 完整報告](../03-analysis-requests/A-003-roy1-create-legal-values.md) 和 [契約](A-003-character-create-contract.md) 補證 `0x4985dc/0x4985e8` 初始化 `0x91fed0` 為 region0=6、region1..4=12，但 `0x4b1a30` region0 跳過 narrow byte 長度 gate、其他 region 要長度>=12。C04 `0x4b2031` 前兩字節來自預覽選擇值，色彩 `0x66422c` 原始十筆 DWORD index0..9 查出 RGB 三字節；C04 **沒有單獨角色名稱**。Client 色盤可用不是原服拒絕其他 RGB 的證據；原服 sex/hair enum、重名 status、一帳多角仍 unknown。安全 owner 仍由 A-027 限制，不得把 A-003 已整合誤用作未驗證 C02 認領。CT-047/048 planned。
