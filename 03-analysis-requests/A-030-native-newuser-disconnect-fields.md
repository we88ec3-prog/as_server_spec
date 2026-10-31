# A-030 / P0：原版創角斷線定點追查、五欄映射、S02 錯誤 UI

**Status: open, handoff_status: not-started, native_client_validation: not-run.** 本工作是 A-021/A-027/A-028/A-020 的殘留缺口精準增量，**不重做**既有 C02/C04/S02/C15 serializer、opcode 和 state 機研究。只分析 Client I/O；**不更動** Asgard.exe、Server/資料庫、不新 Git branch。

固定 EXE SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145，TW-seed0-local-v0.1；本次 Server 唯讀版 ad84f9fb11606a318aff6bd67e065aa0ee07cc45。

## 1. 一定要回答的 Client 研究問題

|題組|問題／查找位置|必要交付|
|---|---|---|
|A30-1: 連線斷點|原版 Client 在創角表單按確認前是否已送 C02？按確認後最後 client_send 是哪個 opcode？C02/S02/C04/C15 各自的相對時間與 Socket FIN/RST 主動端？是否另連到舊版 Server/其他 localhost port？|去敏 C2S/S2C opcode、frame length、ordinal、timestamp、session stage 與 UI popup 對照；H0 C02前、H1 C02後、H2 C04後、H3 C15後、H4前置錯誤，逐個判定；禁止因 generic reconnect popup 就填帳密錯|
|A30-2: 表單標籤|實際畫面 ID、PASSWORD、CONFIRM、NAME、E-MAIL 的 UI control ID/相對 offset、label 來源、按下送出 callback VA、各欄空白/長度格式提示為何？|每個控件 UI→serializer field 一對一對照或明確 not-sent/local-only，widget label 證據或具名 external-resource loader xref|
|A30-3: 欄位|核對 A-027 field1=Dialog+0x26C、field2=+0x270、confirmation=+0x274；field3/field4 何者是 NAME/EMAIL？NAME 是否另由 field1 對應？ region0 widget 0x0A，region4 0x17/0x18，其他非0 0x0F/0x10；region1 UI/writer 矛盾？|每個 region 3×string8 或 4×string8+u8 的逐欄來源、用途/未知、長度和 native serializer VA、被 Client 本地阻擋的分支|
|A30-4: E-MAIL 必填|EMAIL 留空仍可按最後確認嗎？若 Client 拒絕在哪個 VA/提示？若可以送 C02，EMAIL 是否出現在 field3/4、是否空 string8、地區版本是否差異？Server 是否應解析但不持久化（此為 DEV/產品決策，非原 Server 事實）？|具體 UI event/callback、對照 **空白與填入虛構格式 EMAIL** 兩次去敏包長度/本地提示、標記 observed-static / native-GUI / unknown；勿猜必填|
|A30-5: ID 長度|A-003/A-027 的 region!=0 lower bound 12（global 0x91FED0）是否真的限制正在用的 ID 欄位？ADMIN 建帳允許 3..32；Client 若 3..11 字是否從未送 C02？|目標 region、實測輸入長度（不用透露文字）、gate VA / UI message、最小兼容長度；不要用改 EXE 繞過|
|A30-6: S02 錯誤|原 Client 在 local state0x1d 與0x1e 收 S02 status!=0 + string8 text 如何顯示、聚焦、關 Dialog、發 C15？已知 status 3/4/18/26/31 focus 第一欄，17 focus 第二欄，但 **不等於**正式錯誤原因。status1/2 或其他如何？|至少提供原生 **可安全呈現文字的非零 S02 構型**與 retry/cancel 反應，並明確區分一般 credential error 的 status 映射「已由實測證實／仍 unknown」；不可沿用 C03 LoginFailure(status3)|
|A30-7: 成功與取消|S02(0) local0x1D→C04→local0x1E→S02(0)→0x4B206B 本地完成，UI 如何返回登入？收到非零 S02 後 C15(empty) / state0x1F 是否同 socket retry？有無額外消息？|逐個畫面和 callback / writer VA，地區3特殊 popup、成功後回 LoginDialog 的真實操作；若不可還原標 unknown|
|A30-8: 前置協定|非 C03 的原版 NewUser 入口在 C62/C00/C6C/C0F/C57/C4B 與 S00/S18/S56/S60 需要哪些最短回應？Client seed/region/key 使用何種選法？|只查相對 NewUser 入口的 prelogin 切片，重用 A-020 static，若 C02 根本沒到達先回報前置協定/本地 gate|

## 2. 固定證據與安全規則
BIN-first 已證：C02 writer 0x574170 / 0x5742B0..0x574352；NewUser form 0x4B2764..0x4B2A37，confirmation compare 0x4B28FD..0x4B2916，S02 parser 0x57DBC0，state handlers 0x4B1D60..0x4B217A，C15 constructor 0x5715F0 / empty serializer 0x5716A0，C04 writer 0x574420。無需重做這些函式，只補缺失邊界。

保護：只在本機用**測試帳號**操作，報告不能記 Password/CONFIRM/EMAIL 的明文、C02 decrypted raw body、真正 Account token/hash。允許記 packet opcode/length、欄位 ordinal、匿名化帳號標籤、VA，畫面截圖須遮掉輸入；不提交 EXE 或帳號資源。

交付六欄格式：
- trigger：UI、region、確認步驟、VA；
- client_sends：C02/C04/C15 或前置 opcode+去敏 frame length；
- client_receives：S02 status、可顯示文字的**去敏**表示、原生接收 handler；
- client_reaction：local0x1D/0x1E/0x1F、錯誤/重試/斷線/回登入；
- evidence：client SHA、VA/resource exact path、timestamp、packet+UI matching；
- unknowns：還沒查到的 EMAIL/NAME/region / native status 及其 blocker。

**缺檔**：目前用已提供 Asgard.exe 可繼續；若發現 UI label 在外部資源，請先報 loader 證明的**精確檔名**再要求使用者補檔，禁止猜檔案。分析可以在 native E2E not-run 時以 partial handoff，但不得編造 status 錯誤碼。對應 CT-103/104/105。
