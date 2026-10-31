# A-030 roy3：原版 C02 Region1 欄位來源不一致、NAME/E-MAIL 最終提交及 S02/C15 研究（2026-11-01）

沿用 task_a/roy3；原始 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145、Basic.dat SHA 0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96、Locale.dat SHA 813f2800696555f16ec6c4bfc5975b649332340b5a6975d7aeba4c4e77380161。繼承 03-analysis-requests/A-030-roy1-original-resource-proof-20261101.md 及 A-030-roy1-native-fields-failure-c15-handoff.md。新增 A030-E05..E08。原始 EXE/BASIC/LOCALE 都已直接在本輪驗證；沒有原版 Windows GUI/TCP E2E，不聲稱真正成功顯示。

## A030-E05：Region1 的第三欄存在明確 Native source/writer discrepancy

Client 0x4B2764..0x4B28D2 在 NewUser 表單從輸入欄位複製至 C02 本地物件；writer 0x5742B0..0x574352 依 Native region 決定真正 wire body。

|Region|UI widget 第三欄複製目的|C02 writer 真第三 string8 來源|第四 string8|
|---|---|---|---|
|0|widget10 → packet+0x424|packet+0x424|無|
|1|widget15 → packet+0x624|**packet+0x424**|無（雖然 widget16 複製到 +0x822）|
|2,3|widget15 → packet+0x624|packet+0x624|widget16 → packet+0x822|
|4|widget23 → packet+0x624|packet+0x624|widget24 → packet+0x822|

Native calls：0x4B2816 檢查 region0，0x4B2863 檢查 region4，其餘非零 region 的 UI 複製走 0x4B289D（widget15 到 +0x624）及 0x4B28BB（widget16 到 +0x822）。Writer 的 0x5742EC/0x5742F1 只接受 Region2..4 的 extended F3=+0x624 / F4=+0x822 / flag；Region0/1 落 0x574338 的 writer this+0x418，即 packet+0x424。Region1 UI 值與第三個 wire 字串不同，這是可重現的原始程式碼**來源不一致**，但 packet+0x424 在 Region1 最終的初始化值尚未驗，**不得宣稱一定為空或必然傳 NAME**。這是新確認的本版 Client 行為，不應以修改 Client 方式補救。

## A030-E06：原版 NAME/E-MAIL 與空值檢查界線

BasicString.txt 73=NAME、75=E-MAIL；SkinString.txt 2153=名字、2154=E-Mail。EXE 0x4B24ED 查 key0x49/73，對應 packet+0x624；0x4B2516 查 key0x4B/75，對應 packet+0x822。Region2..4 writer 同欄位，已證 F3=NAME、F4=E-MAIL。此對照**不得**套到 Region0/1。

新追 final submission 0x4B28D2..0x4B2918：0x4B28F0→0x4B1A30 以第一字串（packet+0x24）做 region-dependent length check；0x4B290C→0x5B4A62 比對 packet+0x224 password 和本地 CONFIRM。**在此精確片段內沒有對 +0x822 EMAIL 的直接非空檢查**；然而別的 widget callback/button enable logic 或本地驗證仍可能阻擋空 EMAIL，因此不能斷言 GUI 允許留空，亦不能說 Client 一定送出空 EMAIL C02。Runtime region/locale 本回合也沒有 GUI capture。

## A030-E07：S02 failure / C15 相容性

原始 S02 0x57DBC0 讀 status:u8 + message:string8。MakeInfo callback 0x4B1D60：非空 message 可進 0x4B1DFF→0x4B1EBE dialog builder；Region3 + state0x1E 抑制對話。非零 status 經 0x4B1F2F enqueue C15，0x4B1F34 設 state0x1F；C15 opcode0x15 由 0x571609 建構、0x5716A0 writer 空 body。非零 status 的 focus 某些分支由 Roy1 既有研究完成。**真正的 S02 各官方錯誤碼、Windows UI 是否顯示文字、C15 後誰關 TCP、能否重試，依舊沒有原版實機資料。** status1 / Request rejected 是合成 S02 decoded-body 測試向量，不是官方錯密狀態。

status0 state1D→C04→state1E、第二階段成功→Client 後續界面；最新 ADR-008 要求成功創角直接進 World，真正 C10/C25/World 依 A028/A031，不能自行推定。Server 不應因普通失敗無聲關 socket 冒充 S02。

## A030-E08：再現、交接、缺口

- 本輪工具 task_a/roy3/a030_roy3_region_submit_probe.py：原件 EXE SHA pinned、34 x86 exact VA byte windows、區域 F3/F4 來源、Basic/Locale SHA 與 key crosscheck，限定 0x4B28D2..0x4B2918 的直接 EMAIL 檢查 negative audit。
- task_a/roy3/test_a030_roy3_region_submit_probe.py：11 項 offline tests 在原件可用環境 PASS；原版 Client GUI/TCP not-run。原始 EXE、Basic、Locale 和任何帳號密碼/EMAIL/raw 個資沒有進 Git。
- 可交 DEV：Region2..4 的 C02 四 string8+flag、NAME F3、EMAIL F4，Region0/1 三 string8（Region1 third source mismatch），S02(status+string8)、失敗 C15(empty)/state1F；C02 帳號 owner 驗證/EMAIL 僅儲存及正常錯誤回覆仍是 Server 語意。
- CT-104 需原版 Windows GUI 實測 Region1 widget15 改值的第三 wire string8、Region2..4 空 E-MAIL、S02 失敗 message 畫面/C15 和 TCP FIN/RST 來源/同連線 retry；成功 C04 後直接進 World 的真封包另 CT-105/A031。
- 由於 A030 原始交付要求實際原版 UI 演示及 retry，**目前狀態 integrated / handoff partial / native_client_validation not-run / native_s02_failure_gui_ready false**。Region2..4 static NAME/EMAIL ready，但 A30 full E2E 未完成，不得宣稱整體驗收通過。

**缺少靜態分析檔案：無。** 已提供 Asgard.exe、Basic.dat、Locale.dat；未完成的是 Windows 原版 Client 可運行環境和去敏 UI/封包／TCP 連線 trace，而非另一份 DAT。
