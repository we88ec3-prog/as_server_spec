# A-030 roy3 — Region1 C02 / S02 / C15 Client I/O 契約增量

來源 task_a/roy3/A-030-roy3-region1-submit-failure.md；A030-E05..E08。Client SHA db3df616...729e1145。

- Trigger：原版 MakeInfoDialog 的最後確認 callback，S02 收包回 0x4B1D60。
- Client sends：C02 Region2..4 4×string8 + u8，F3 (packet+0x624)=NAME、F4 (packet+0x822)=E-MAIL；Region0/1 3×string8。**Region1 UI 第三 widget15 複製到 packet+0x624，但 writer 實際第三取 packet+0x424；Region1 第三值與 NAME label 未獲可靠來源證明。** S02 status!=0 送 C15 empty。
- Client receives：S02 status:u8、message:string8。
- Client reaction：S02 非零可嘗試原生 text dialog、依 status 設 focus，enqueue C15(empty) 並 state1F；region3/state1E 抑制文字。不是已驗 TCP close 或可重試 UI。
- 原始 evidence：Asgard.exe 34 VA opcode anchors、BasicString 73 NAME/75 E-MAIL、SkinString 2153 名字/2154 E-Mail、11 項 offline tests；最終提交 0x4B28D2..0x4B2918 僅直接檢查首欄與確認密碼，無直接 F4 非空 gate（不可外推整體 GUI 必允許空值）。
- Unknown：實際 runtime region、Region1 第三欄原始實際值、空 E-MAIL 提交、原版 S02 message/focus GUI、官方 status 意義、C15 後 TCP/重試、C04 後直接 World 完整 native flow。

DEV：嚴格依 region 解碼，Region1 fail closed 或單獨用經驗證資料策略；R-035 EMAIL 僅在授權建角成功同交易儲存，不是 account ownership proof。原版 Client GUI CT not-run，A30 handoff_status=partial。實機測試見 05-conformance/A-030-roy3-region1-native-acceptance.md。
