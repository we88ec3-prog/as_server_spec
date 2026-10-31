# 原版 Client 更改密碼 UI：A-029 / CT-098..099（全 planned）

此功能由使用者指出**原遊戲內已經有更改密碼 UI**。A-029 已以原始 `Asgard.exe` 證實 C→S 為 **C26（account/old/new 三個 string8）**，UI 的確認欄只作本地比較，且 Client 共用 **S02** 回覆 handler；**C26 專屬成功/錯誤 status、是否必須先登入、region/畫面 E2E 仍未實機驗證**。**禁止替原 Client 自造更改密碼封包或改 EXE**。

|測試|流程|要求|
|---|---|---|
|CT-098 native UI／wire|原版 UI 開啟→填原密碼、新密碼/確認→按確認→擷取 Client 發送 C→S、Server 回 S→C、Client 成功/失敗提示|A-029 提供 VA/UI/reader/writer/region/例外分支；Client SHA、去敏 trace、畫面證據，密碼不得存檔|
|CT-099 正常更新|管理員既建 A 初始 4～8，從原版改密碼 UI 提交舊密碼+新密碼|Server 在原子 transaction 更新既有 Account hash/version，稽核去敏；Login C03 和 Create C02 只接受新密碼，舊密碼拒絕，角色與進度保留|
|CT-099 負面及恢復|原密碼錯／新密碼3或9字／兩次輸入不合／停權／並發／重放／斷線／回覆丟失／改密後舊 grant|不改資料、無帳號枚舉、限速、成功後舊 Session/grant撤銷、不發意外角色授權；若原 UI 不允許某類輸入，區分 native UI gate 與 Server policy|
|CT-097 交叉路徑|改密成功前後測登入、創角入口|兩者都驗同一 credential_version；創角不要求前置 C03，但要求本次完整帳密|

實作時應另外確認 scope：這是**遊戲 Client 的正常密碼更改路徑**，不是管理 Web 的自助重設功能；管理員 `/admin/accounts/{id}/credential-reset` 仍是救援操作。除非原版可發送的 opcode/body 和 Client 成敗 UI 有證據，不得宣稱此功能 native-ready。


## A-029 原件靜態已證及尚待實機驗收（2026-10-31）

- 原始 Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；`CChangePasswordPacket` ctor `0x571a10` push opcode **C26** at `0x571a29`；writer `0x571ac0` **三個 string8**：LoginDialogPane UI index8 **account 候選**、index9 舊、index10 新；index11 確認欄不在封包。
- 事件 **12** 進送出路徑，event13 在 `0x4a8d27` 重置/取消。control10 與11 不同（message 0x4d）或 control9 與10 相同（message 0x5d）時不送 C26。各密碼 input max8 widget 參數已確認。原 Client 4 字下限/字元白名單 **仍要實機確認**；Server-defined 4～8 ASCII 英數是獨立政策。
- 回覆 Client 用既有 **S02** generic dispatcher `0x4a9670→0x4a9694→0x4a8d60`，其 status/ui 分派已知，**改密成功/錯舊密碼/ban 的 status 意義沒有抓包，不可假設 S02(0) 就在此流程代表正式成功**。
- **CT-098 操作清單**：使用未修改的同 SHA Client 截圖/記 UI 進入（登入畫面 vs 遊戲中、region）、account 控制8 是否預填、欄9舊/10新/11確認、長3/4/8/9及英數/其他字元本地拒絕或接受；先按取消與確認不一致（確認沒有 C26），再測舊密碼錯與正確。捕捉 C26 opcode/body **只記欄位長度及去敏內容**，記錄 Server S02 status/message、Client focus/是否重新登入/中斷；原服沒有受控測試環境時不要送憑證或臆造成功值。
- **CT-099 操作清單**：依 A-029/Server 新政策，測既有帳號/錯密/停權/併發/重送/成功/回包遺失，更新同個 hash+credential_version、撤銷舊 grants，C03 與獨立 C02 均只認新密碼，Character/進度不變；區分 DB transaction 已提交與 GUI 顯示成功。

新本地工具 `tools/a029_password_change_contract.py` 提供 19 原件機器碼簽章、UTF16 source/RTTI、synthetic C26 codec、negative/原 UI 比對邏輯測試。**CT-098/099 仍 planned/native Client E2E not-run**。詳 [報告](../03-analysis-requests/A-029-roy1-native-password-change.md)。
