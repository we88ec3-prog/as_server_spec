# 原版 Client 更改密碼 UI：A-029 / CT-098..099（全 planned）

此功能由使用者指出**原遊戲內已經有更改密碼 UI**。但原版 `Asgard.exe` 對應的 Client C→S packet opcode、body、S→C 回覆、畫面回調、錯誤代碼、是否必須先登入、region 差異 **尚未有本研究證據**。**禁止替原 Client 自造更改密碼封包或改 EXE**。

|測試|流程|要求|
|---|---|---|
|CT-098 native UI／wire|原版 UI 開啟→填原密碼、新密碼/確認→按確認→擷取 Client 發送 C→S、Server 回 S→C、Client 成功/失敗提示|A-029 提供 VA/UI/reader/writer/region/例外分支；Client SHA、去敏 trace、畫面證據，密碼不得存檔|
|CT-099 正常更新|管理員既建 A 初始 4～8，從原版改密碼 UI 提交舊密碼+新密碼|Server 在原子 transaction 更新既有 Account hash/version，稽核去敏；Login C03 和 Create C02 只接受新密碼，舊密碼拒絕，角色與進度保留|
|CT-099 負面及恢復|原密碼錯／新密碼3或9字／兩次輸入不合／停權／並發／重放／斷線／回覆丟失／改密後舊 grant|不改資料、無帳號枚舉、限速、成功後舊 Session/grant撤銷、不發意外角色授權；若原 UI 不允許某類輸入，區分 native UI gate 與 Server policy|
|CT-097 交叉路徑|改密成功前後測登入、創角入口|兩者都驗同一 credential_version；創角不要求前置 C03，但要求本次完整帳密|

實作時應另外確認 scope：這是**遊戲 Client 的正常密碼更改路徑**，不是管理 Web 的自助重設功能；管理員 `/admin/accounts/{id}/credential-reset` 仍是救援操作。除非原版可發送的 opcode/body 和 Client 成敗 UI 有證據，不得宣稱此功能 native-ready。
