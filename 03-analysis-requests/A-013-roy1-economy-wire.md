# A-013 / roy1 — 商店、Exchange、玩家交易 Client I/O（BIN-first）

日期 2026-10-31；工作分支 \`task_a/roy1\`，已合併截至 \`8e4f42d\` 的 main；原始 \`Asgard.exe\` SHA256 \`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145\`。R-014/R-017，SYS-ECONOMY，evidence \`ev_a013_20261031_client_economy_wire_static\`。證據級別：observed-static（Native x86 opcode/reader/writer/RTTI）、synthetic（自製有限向量）、designed（Server 安全合約）。**沒有原服網路 trace 或原 Client 點擊實測**。

## 1. Native class/opcode 對照（已證實是 3 條不同通道）

| 原始類別（RTTI）|方向/opcode|建構及 opcode 位址|codec VA|可證範圍|
|---|---|---|---|---|
|CExchangePacket|C2S **0x4A**|0x572540 / 0x572559|**0x5725F0**|subtype 0..5|
|SExchangePacket|S2C **0x42**|0x57E920 / 0x57E939|**0x57E9F0**|subtype 0..5|
|CMerchantPacket|C2S **0x39**|0x5737B0 / 0x5737C9|**0x573860**|u8/u32BE/u16BE common + subtype-tail|
|SMerchantPacket|S2C **0x2F**|0x581B90 / 0x581BA9|**0x581CA0**|common header + array/string tails; case0..9|
|CTradePacket|C2S **0x17**|0x5770F0 / 0x577109|**0x5763A0**|wire type field 0..130 dispatch; most use no further fields|
|STradePacket|S2C **0x6E**|0x588150 / 0x588169|**0x588330**|type0..3 + variable record branches|

上述 opcode **不代表**已經證明 Exchange 等於倉庫，也不證玩家交易先送/後收什麼、或是哪個 type 意味確認/取消。原始 EXE 有 \`ExchangeDialog\`、\`TradeDialog\`、\`MoneyInputDialog\` 和 \`MoneyDraggedPane\` RTTI（分別在 0x6651E8、0x66898C、0x667008、0x664C00）；這只證明 Client 有對話 UI 類別，**不能憑名稱推測持久倉庫、手續費、交易鎖定或可用金額上限**。

## 2. Client sends（observed-static）

### C4A / Exchange
\`0x5725F3\` 先寫 \`u8 subtype\`；\`0x572601\` 上界 5；\`0x5726A8\` jump table 對應：
- subtype0、4、5：\`u8 subtype + u32BE f1\`，**5 bytes**（0x572611 / 0x57268C / 0x572699）。
- subtype1：\`u8 + u32BE + u8 + u8\`，**7 bytes**（0x57261E）。
- subtype2：\`u8 + u32BE + u8 + u8 + u8\`，**8 bytes**（0x572643）。
- subtype3：\`u8 + u32BE + u32BE\`，**9 bytes**（0x572674）。
此處 \`u32BE\` 的來源為 \`0x45AC40\` writer；**欄位是數值/引用的哪一種語意未經上游 UI 追認，不能都稱「價格」**。C4A subtype 不等於 S42 subtype 可無條件做一對一回覆。

### C39 / Merchant
\`0x573863..0x57387F\` 依序寫 \`u8 field_19 + u32BE field_1c + u16BE field_20\`，固定前綴 **7 bytes**；\`0x573884..0x5738F6\` 再依 **packet local subtype +0x18** 選擇字串或額外 u8 尾段，具多種分支。未求證每個分支的商店購買/賣出語意與價格。尤其 \`field_1c\` 可能是 NPC/object ref，不能因其為 32-bit 就當金錢。

### C17 / Trade
建構器 \`0x577109 push 0x17\`；writer \`0x5763A3\` 先寫 **u8 type**，\`0x5763B1\` 對 type0..130 做 dispatch；以 \`0x576508\` 131-byte selector table 逐項驗證：
- **type0**（0x5763CB）：\`u8 type + u8 count + count × (u8, u8, u32BE, u16BE)\`，每筆 8 bytes wire，對應本地容器 stride 12；\`count\` 為 u8。
- **type3**（0x57643B）：\`u8 type + u8 count + count × (u8, u16BE)\`，每筆 3 bytes wire、本地 stride12。
- **type128 = 0x80**（0x576495）：\`u8 type + u32BE field\`，5 bytes。
- **type130 = 0x82**（0x5764A3）：\`u8 type + u8 count + count × (u8, u16BE)\`，每筆 3 bytes wire、本地 stride4。
- type1、2、4..127、129（其餘 127 個 type）：writer 不再增加欄位，**只有 type byte**。這是 serializer 觀察，**不是**原服接受這些全部 type 的證明，尤其不代表「按下確認」的真實 type。
應防範變長 count 穿越 frame 上限，不要把本地 stride12 複製成 wire stride。

## 3. Client receives（observed-static；不是臆造請求回覆的配對）

- **S42 Exchange**：ctor \`0x57E939 push 0x42\`，reader \`0x57E9F0\` 先讀 u8 subtype，max5、六路 \`0x57EC0C\` dispatch；type0 讀 **u32BE + string8 + u8**（0x57EA20）、type1 讀 **u8+u8**（0x57EA5D），其餘為不同的欄位／陣列分支，未完整以 GUI 回調確認；不能從同編號猜與 C4A 一對一。
- **S2F Merchant**：ctor \`0x581BA9 push 0x2F\`，reader \`0x581CA0\` 先讀 u8 subtype，接續 u8 / **u32BE** / u8 / **u16BE** / u8，再跳過 4 bytes、讀 bounded string buffer（0x581CBE..0x581D07），之後依 subtype0..9 的跳表 \`0x582084\` 讀不同列表/文字；分支0 讀 u8 count 後有動態項目描述。**不可**把所有 S2F 當 fixed length 7。
- **S6E Trade**：ctor \`0x588169 push 0x6E\`，reader \`0x588330\` 先讀 u8 type，分支0..3（\`0x5885EC\`）；**type0**（0x588377）讀 u8 count，再讀每筆多欄（含 u8、u16BE、u32BE、string8 與 nested count，0x5883B0..0x588501）；type1/2/3 另有回覆格式，未完整推到特定畫面/接受/取消效果。原服成功/失敗碼及 Client UI 變化均需動態驗證。

## 4. 觸發 → C→S / S→C → Client reaction（必需交接欄位）

|Trigger / precondition|Client sends|Server sends / Client receives|Client reaction|evidence / unknown|
|---|---|---|---|---|
|玩家在 Exchange 類介面執行動作|C4A 的 subtype0..5 codec 已證|S42 subtype0..5 可解析；**實際是否配對未知**|原有 ExchangeDialog UI 可能更新；尚未追到完整 handler|Native serializer / RTTI；倉庫身份與資產原子性 unknown|
|玩家與具有效可見 ref 的 Merchant 互動|C39，7B common + variant tail|S2F subtype0..9（可變）|實際商店列表、購買結果、關閉行為 unknown|原 C39/S2F codec；上游按鈕與商品售價來源 unknown|
|玩家在 TradeDialog 提交條目、數值或指令|C17 type0/3/128/130 或 type-only（依 native serializer）|S6E type0..3（可變/含 item list）|對方報價/準備/確認/取消的具體 type→UI 規則 unknown|CTrade/ STrade codec；兩邊 ACK、斷線處理 unknown|
|取消/關視窗、斷線、重送/雙提交|**未證實各 UI 路徑發出的精確 type**|不應任意填成功/失敗 S2F/S42/S6E|尚未觀察 native rollback/snapshot|須做 CT-088/089，Server policy designed|

ServerOnly **designed**：商店價錢/合法物品與金額以 Server 經授權的目錄為準；交易雙方、物品實例、槽位、堆疊數量、金額扣加與庫存修改必須在同一 durable transaction 中完成。交易 offer 每變動就讓雙方 ready/confirm 失效；兩階段確認、version/generation/fencing、成功 receipt 僅發一次、重試冪等、雙方斷線撤銷 pending reservation、超額/負值/同玩家交易拒絕。**這些是新 Server 安全設計，不是原服已實證的流程**。Wire 看到 u32BE **不代表**原服最大金額一定為 2^32−1；client UI 文本限制、錢幣型別、上限與捨入仍 unknown。

## 5. 測試、限制與下一步

離線工具 \`tools/a013_economy_contract.py\`：鎖定原始 EXE SHA，18 個指定 VA 的 Native bytes + 6 個 RTTI 類別；合成 C4A 六 subtype、C39 common、C17 四特殊 type/負例，以及 SQLite designed 錢幣雙人原子移轉／重放／溢位／token collision／未確認不扣款；10/10 PASS。只支持本次明示的 wire 子集；**不宣稱 10 tests 是 native Client E2E**。測試 CT-087（static/offline）、CT-088（商店/Exchange 原版 UI）、CT-089（雙人交易、斷線與防重）仍需實機驗收。

保留未解：C17/S6E/C39/S2F/C4A/S42 全 subtype 的 GUI callsite 和原生動作語意、是否有原版可操作倉庫、交易背包變更順序 S0F/S10、裝備限制、商品價格／金幣上限／手續費、雙方接受/取消／逾時/斷線效果、原版 Server durable DB。要補齊請提供相同版本的 **兩 Client 互相交易及 NPC 買賣/倉庫視窗操作之遮蔽封包 trace（C2S/S2C opcode、decoded payload、時間）與 UI 圖**。本次 **不缺新增具名原版資源檔**；已有 Asgard.exe、Map0..2.dat、Born.dat 不需重傳。

**A-013: status=integrated, handoff_status=partial, implementation_ready=true（僅已證 codec + designed Server safety），native_client_validation=not-run，native_economy_semantics_ready=false。** 按 \`03-analysis-requests/client-io-handoff-standard.md\` 客戶端研究可交付，不因尚無原服 Server DB 就阻止分析結案；但不能假稱交易 UI/倉庫實機全部完成。
