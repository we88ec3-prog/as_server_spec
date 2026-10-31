# Server 下一段創角規劃：原版登入與創角獨立（新決策覆蓋舊 C03 前置）

目前使用者要求：管理端建帳，原版 Client 登入與創角是兩個入口；創角直接輸入帳密，必須和後端既有 Account 的 **名稱＋密碼** 都一致，否則回原版 UI 錯誤。玩家正常改密碼走遊戲既有更改密碼介面。原版 `Asgard.exe` 不修改。

## 可規劃的 Server 安全切片

|Slice|Server 契約|Client/分析阻塞|
|---|---|---|
|SAFE-01：共用憑證服務|`CredentialVerifier` 同時服務 C03 登入、C02 創角、原版改密碼（當其 wire 已查明）。既有帳號唯一，停權/過期/credential_version 一致，4～8 ASCII 英數；C03 和 C02 必須分別認證，不拿帳號名當 owner|C03 已證；C02 第二欄雖高度符合 password，需 A-027 查 native fields|
|SAFE-02：獨立創角會話|NewUser C02 **不要求之前有 C03 Session**；只有本次 C02 正確帳號及密碼才發 creation-only `CreateAuthProof`，它不得直接授權 World 登入或修改其他 Account|A-027 C02 UI/region 欄位及原版錯誤 S02 status|
|SAFE-03：創角負面安全|未知/錯帳號、錯密、停權、重放、同帳號已創角，均不發會觸發 C04 的 S02 success；原版 UI 要有錯誤提示但 wire/status 先查證|A-027/A-028 原生 status/focus/message；不能猜用 S02(3) 表示錯密|
|SAFE-04：C04 提交|同 connection/generation/proof 的 C04 才可原子建 Character；C15 取消未提交、不動別人帳號、不誤刪角色；已成功 C04 的 UI 回登入不直接 S03|A-028 相關 Client callback 部分已證，最終原生 E2E 未測|
|SAFE-05：原生改密碼|由遊戲原生密碼 UI 觸發，驗舊憑證、新憑證符合 4～8、原子更新同一 hash/credential_version + 撤銷舊 grant/sessions，保留角色與進度|**A-029 P0** 原 Client UI、C2S opcode/body/S2C UI、region 鍵值 unknown；未證前不能發未知封包|
|WIRE-01|Client NewUser 是否可自主開啟、C02 第1/2欄是否輸出帳密、錯誤如何顯示|A-027/A-021；**不再要求 C03(no character)→NewUser 自動跳轉**|
|WIRE-02|C02 的 S02(0)→C04；C04 的 S02(0)→本地 UI，失敗 C15；原版實際回登入步驟|A-028|
|WIRE-03|改密碼 UI→C2S→S2C→成功/失敗提示|A-029|

## 出場與交付

Server 實作仍需另行批准；能先設計 Account Store 共用 CredentialVerifier、creation-only proof、登入/創角/改密碼 rate limit 和限時性。**不能**因原版有 NewUser UI 就開放免驗證自助 AccountCreate，不能在同名失敗時修改帳號、不能回捏造的 S02 成功/錯誤狀態。**所有原生 CT 目前未執行**。

[總契約](three-native-account-entry-policy.md) · [Gate](onboarding-readiness-gates.json) · [原生測試](../05-conformance/native-creation-gate-test-plan.md)。
