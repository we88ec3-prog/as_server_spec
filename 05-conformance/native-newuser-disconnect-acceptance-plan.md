# CT-103..CT-105：原版創角斷線修正測試矩陣

**全部 planned / native_client_validation=not-run**；目前只規劃。原版 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145，Server 正式改動前另行向使用者確認；合成與原版實機不可混淆。

2026-10-31 進度註記：下面「原 main 無條件 Close」指歷史查核版本 `ad84f9`，不是永遠對目前 main 的判斷。唯讀核對 `b8e212e` 已有後端創角／診斷實作，原生 C02/C04/C15 adapter 仍以明確原因關閉，尚無本次原版實測。見 [RI-001 交接](../02-server-planning/runtime-feedback-handoff.md)；此註記不將任何 CT 改為 passed。

## Test matrix

|#|情境|Server 合成／DB 驗收|原版 Client 驗收|
|---|---|---|---|
|01|未 C03，管理端預建帳號、正確 ID/PASSWORD|驗 hash/停權後 creation-only proof，先 S02(0) 才允許 C04，無 Account INSERT|原版 NewUser 送 C02 並收到第一 S02→送 C04；不再無條件斷線|
|02|正確 ID、錯 PASSWORD|不得建 Account/草稿/角色/WorldGrant，統一認證錯誤|原版 UI 顯示已證 S02 非零提示，非 generic disconnect（能力需證）|
|03|不存在的 ID|與錯密公共提示一致、不做 Account.Create、稽核匿名化|原版 UI 可理解，不觸發 C04|
|04|停權／永久停權帳號|任何正確密碼也禁止建立 proof/角色|原版 UI 相容錯誤、不冒充 TCP 斷線|
|05|帳號已有角色|一帳一角 unique，拒絕再建|正確 S02 失敗位置／可返回登入|
|06|角色 NAME 重複或不合法（含 CP950、長度）|名稱唯一，沒有已提交/未提交不合法角色|原版非零 S02 對應已證錯誤焦點／處理 C15|
|07|EMAIL 留空、NAME/ID/CONFIRM 地區差異|Region2..4 4 strings+flag、其他3 strings 嚴格 codec；不能拿未知欄當身份|UI 是否阻擋提交、是否發 C02；核對地區第一欄 min12 和 Region1 差異|
|08|正常 C02→S02(0)→C04→S02(0)|C04 五 u8 正確，同 proof+generation+version、atomic Character+Appearance+progress commit|state0x1D→0x1E→local done，成功後以原版操作回登入，**不直接 S03**|
|09|C02 前斷線／前置包錯序|close_reason 分 handshake/idle/peer/protocol，若未收 C02 不誤判帳密|有時間戳 packet 與實機畫面對照 H0|
|10|C02 成功後 C04 前斷線|尚無 Character；pending 清理或 TTL 到期|重新合法 C02，不能沿舊 C04 接續|
|11|C04 DB commit 前崩潰／斷線|整個 transaction 回滾、無半角色|後續再次創角/登入可辨實際 DB 狀態|
|12|C04 DB commit 後 S02 第二段遺失／重送|同 owner/intention/body 冪等，不第二次 INSERT，不刪已提交|重新登入得回角色；若原 Client 不會重送 C04，記限制|
|13|C15(empty)、取消、重送、舊世代|只取消同 owner/connection/generation 未提交 pending；舊 C15 不刪已提交角色|S02(nonzero)→C15→0x1F，是否可 retry/維持 socket 需實測|
|14|密碼 reset、停權與 C02/C04 之間競態|proof credential_version/status 有效；變更後舊 C04 拒絕；錯密限流，不印 secrets|原版 Client 不越權、不造成重複角|
|15|創角成功後再登入|C03 已持久帳號和角色核發合法 S03/C10，帳號與角色歸屬一致|登入入口獨立，確實回登入並可進 World|
|16|無效 frame／未知 opcode／錯地區 payload|Protocol fatal 可以 fail-closed，記明確原因；**一般業務拒絕**不能無理由 close|區分合法錯誤與真 socket 問題，不能以繞過 guard 達成「沒斷線」|
|17|併發、斷線/重啟、SQLite/PostgreSQL|相同帳號與重名競態唯一性不破壞，不重抽/雙 INSERT|native Client E2E 獨立執行，CI 只寫 synthetic PASS|

## Definition of Done

- **CT-103 / pipeline+diagnostic**：能證明原 main 的 C02/C04 是無條件 Close 且沒有 S02。修正後合法本次驗證的 C02 不再無條件關閉；去敏 trace 明確判定 H0/H1/H2/H3 之一與 Server close origin。合成可先寫 PASS，原版 native status 獨立。
- **CT-104 / auth negatives+native error**：account missing/wrong password/banned/duplicate/invalid 都不建立任何 Account/Character/未授權 draft，原生 S02 status+message 在 state 0x1D/0x1E 與 C15 可正確回應；若 A-028/030 未查證錯誤碼，**不能標完整 PASS**。一般驗證失敗不能作無理由 TCP close。
- **CT-105 / original-client E2E**：原版相同 SHA 的 Asgard.exe 成功 C02→S02→C04→S02、返回獨立 LoginDialog C03、Server DB 已持久化角色，重登入取得角色。錯密/未知/停權/中斷/重送/取消和可見提示逐項記錄。Server 合成、SQLite/PostgreSQL、真 Client UI 都需分開標註。

## 紀錄必要欄位
spec SHA、server SHA、client SHA256、region/seed/codepage、timestamp、traceId、經遮罩的 account id、Client 操作、C2S/S2C opcode/len/status（不含解密正文）、Server close_reason、UI popup/focus、DB 前後唯一性與 native_client_validation。不可寫入 Password/Confirm/E-mail 明文、hashed credentials、raw C02 body、transfer grant。

延伸 [根因修正規格](../02-server-planning/native-newuser-disconnect-remediation-20261031.md) 和 [A-030](../03-analysis-requests/A-030-native-newuser-disconnect-fields.md)。

## A-030 增量驗收切片（2026-10-31，原生 Client 仍待測）

- 原始 EXE SHA 鎖定、30 x86 bytes anchors、29 status selector：用 `python tools/a030_native_newuser_contract.py` 離線驗證；對應 [A-030 報告](../03-analysis-requests/A-030-native-newuser-disconnect-fields.md)，**不等同 Client GUI pass**。
- CT-104 **UI labels/field order**：確定實際 region 與 seed；在原生 NewUser 先保持 ID/PASSWORD 固定，把 NAME 改動一次、E-MAIL 留白/填入合成值各一次；只記 C02 field ordinal 與**長度**，不得留 decrypted body/真正帳密/郵件。Region0 只有第3字串、Region1 第4個 UI 額外控件不一定上線；Region2/3 第3/4控制為 0x0F/0x10，Region4 為 0x17/0x18。不得把候選 F3 NAME/F4 EMAIL 寫成已確證。
- CT-104 **可顯示錯誤的獨立試驗**：在完成 NewUser state0x1D 且 Client UI 上下文有效時，送 S02 **synthetic body** `01 10 526571756573742072656a6563746564` (status1 + ASCII `Request rejected`)；錄畫面焦點/文字顯示、後續 C15(empty)、local0x1F、TCP 是否保留。status=1 只是無專屬 focus 的靜態可達候選，**非已證原服錯密狀態**。state0x1E+region3 的 message 抑制例外另測；優先使用隔離環境。
- CT-103/105：對照實際輸入 → 最後 native C02/C04/C15 的 opcode/frame length/timestamp，匹配 Server source-level Close origin；兩段合法 success S02(0) → C04 → final S02(0)，後續回獨立 Login UI 仍需實機證據。**合成測試通過不代表這三項 native CT 通過**。


## A30 新取得的原 Client 靜態路徑（2026-11-01）

[完整 A30 Client I/O 追鏈](../03-analysis-requests/A-030-roy1-native-fields-failure-c15-handoff.md)；40 native instruction signatures locally verified。Region2/3 F3/F4 widgets15/16，Region4 widgets23/24，C02 writer+0x618/+0x816，確認 popup locale keys0x49/0x4B；Region0/1 不可使用四字串假設。實際 NAME/E-MAIL 字樣仍需 `Locale.dat`／native GUI。S02(nonzero text) 在 NewUser 可走文字對話窗 + C15(empty)/state0x1F；Region3/state0x1E 不走文字窗仍 C15。合成 status1/string8 `Request rejected` 僅供**隔離測試**。CT-104 須捕捉原始 client 的 UI text、C15、TCP FIN/RST 主動端、同連線 retry；不得因看見 C15 就宣稱 socket 保持，亦不能套 C03 LoginFailure status3 原服語意。CT-103/105/106 planned/not-run，勿與 offline PASS 混淆。
