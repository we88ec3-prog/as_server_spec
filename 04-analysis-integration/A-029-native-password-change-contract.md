# A-029 — 原 Client 改密碼 C26 與 Server 權威界線

範圍：R-025/R-032，原始 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；**original Client** 具可觀測 code path，**original Server credential policy** 不在 EXE 內。本約束不授權修改 `as_server_roy` 或遊戲 Client。參考 [A29 BIN-first](../03-analysis-requests/A-029-roy1-native-password-change.md)、[三入口政策](../02-server-planning/three-native-account-entry-policy.md)、[CT-098/099](../05-conformance/account-password-native-change-test-plan.md)。

## Observed static：三個入口，真實 packet 不可混淆

|Client 入口|C2S|S2C / native callback|限制|
|---|---|---|---|
|登入|C03，name/password/flag|S02/S03→C10|A002，已有 profile|
|直接創角|C02，name/password/region fields → S02 → C04|S02（A027/A028）|不須先 C03，但 Server 必須驗既有 Account 憑證|
|**改密碼**|**C26** 三 `string8`：`account`, `old_password`, `new_password`（舊/新/確認 UI：controls9/10/11；確認**不傳**）|LoginDialogPane generic **S02** opcode0x02 status/message routing，VA 0x4a9670→0x4a9694→0x4a8d60；**改密專用 status→success/error 仍 unknown**|submit event12；confirm != new / old == new 時本地提示，不建 C26；cancel event13 reset、無 C26|

- C26 constructor VA `0x571a10` / opcode `0x571a29`，writer `0x571ac0`，三 string8 helpers `0x45b1b0`，UI producer `0x4a8a81..0x4a8d05`。`PKT-C26` body 無 opcode、無 subtype、無 confirm、無 token。Native codepage 取決於 LanguageMan；index4/CP950 是條件，不可強制推導所有 region。
- 帳號控制8 為 account 候選；UI 的中文 label、預填、是否可在 world state 呼叫，待 CT-098 GUI；old/new/confirm 的順序由原生比較/producer 確認。native widget 對 controls9..11 設 input cap8；**min4、ASCII/alnum 與是否只登入前**未從 Client 校驗 opcode 獨立確認。
- 原本 `S02` 為多流程共用 Client status handler；沒有原服 trace 不可用任一 code 冒稱 C26 原生成功結果。**現階段不宣稱 Server password-change E2E native-ready**。

## Designed Server responsibility（並非原 Server 還原）

- 僅讓此原 C26 進 native 玩家改密碼 handler；解析精確三個 string8（長度按 encoded bytes、拒絕截斷/尾端、invalid encoding、Null 字元）；保持 log redaction。不混成 Admin `credential-reset`、C03 或 C02。
- 以 Account canonical-name 找既有 Account，驗 old credential verifier + ban/rate limit；依 User policy 確認新密碼4..8 ASCII 英數、大小寫敏感、不能剪裁/trim、有效/不同 old；確認欄**不在網路封包**，Server 不可能驗證原生 UI 的 confirm 字串，需信任 Client 的本地 UX，但絕不能因此信任身分或改密碼成功。
- 同 DB transaction 更新 password hash、credential_version 和 revoke 規則；Account ID、Character 與其進度不動。以 transaction/replay fence 和版本比較拒絕過期操作及並發重播；不保存密碼本體。成功後 C03 與直接 C02 都驗新密碼，舊授權失效。
- 回 S02 前，先從 CT-098 補到**改密碼專用** status/message 與 UI 成敗映射；不以其他 S02 登入/創角成功常數當作官方改密成功。C26 unknown/disabled path 顯式 fail closed，非新造 opcode；測試中間態要跟正式 profile 分離。

## 驗收與缺件

- `tools/a029_password_change_contract.py`：原始 EXE SHA 與 RTTI、19 native anchor、C26 3×string8 synthetic encode/decode + negative、UI local predicate、designed Server 4..8 validation。已獨立核對 anchor 19/19 與測試向量；沒有 Client GUI 執行。
- **CT-098**：進原版 LoginDialogPane 的改密碼畫面，實測 controls8..11 /8上限／4下限與 region，按取消/確認不符/錯舊密碼/正確，擷取無敏感的 C26 與 S02 status、Client message/focus/轉頁；核對 prelogin/inworld。未知 S02 status 不先猜。
- **CT-099**：測試同一 Account 上 old password→new、C03/C02 共同 verifier、同角進度不變、停權、不存在/密碼錯、重播/並發/中途斷線、舊 grant 撤銷，回覆不明不得把 UI 成功等於 DB commit；Server 尚未執行此 CT。

原件 `Asgard.exe` 已有，**沒有明確缺少的 Client 資源檔名**；最關鍵缺口是原版原生 Client 的去敏封包與畫面記錄、原服 C26 status semantics / Server handler（檔名未知）。A-029 `integrated / partial`；Client wire 可開發但 E2E 還須 CT-098/099。
