# A-030 / roy1 — 原版 NewUser NAME/E-MAIL 欄位來源、S02 失敗提示及 C15（BIN-first）

日期：2026-10-31；branch `task_a/roy1`；原版 `Asgard.exe` PE32 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，ImageBase 0x400000。對應 R-025/R-026，SCN-014/SCN-018 與 CT-103/104/105。證據 `ev_a030_20261031_newuser_regions_s02_failure_bin_static`。

**結論：A-030 integrated / handoff_status=partial；native_client_validation=not-run；implementation_ready=false（官方 NAME/E-MAIL 端到端語意與原生錯誤 UI 尚未通過，Server 不可直接啟用正式 C02）。** 已完成目前 EXE-only 可驗的控制項 ordinal→packet field、S02 非零顯示/C15 分支與可重現 30 條 x86 簽章 + 15 offline tests。**NAME/E-MAIL 的「實際 label 語意」未有原 Client UI 資源/GUI 診斷支持，不能把待證的推論寫成已證。** 不造新 opcode、不修改 Client、Server 或 DB。

## 一、Trigger → C2S → S2C → Client effect → evidence → unknowns

|Trigger / 前提|原生 C→S|原生 S→C|Client 反應（observed-static）|證據與未知|
|---|---|---|---|---|
|MakeInfoDialog 確認按鈕 `[esi+0x278]`；`0x4b2764`|先從 UI IDs 複製文字進 `C02` 本地 packet；`0x4b21e0..0x4b22a9` 再送 C02/切 state **0x1d**|尚無|0x4b28f0 第一欄格式 gate；0x4b290c 第二欄與 confirm 比較；0x4b2918 條款 UI 額外 gate，合法才建立最後確認框 `0x4b2360`|BIN observed；此階段是否收到指定 labels 的 UI 資源、是否已完成 NewUser handshake 及 Server 收包：未實測|
|Region 0 C02 提交|body = `string8 f1, string8 f2, string8 f3`|S02`(status:u8,message:string8)`|f3 來自 widget `0x0a` 的條件分支，若某 UI 條件成立直接寫空 UTF16 string|0x4b2825..0x4b2856、0x574338；f3 **不是已證 NAME 或 EMAIL**|
|Region 2..4 C02 提交|body = `string8 f1, string8 f2, string8 f3, string8 f4, u8 flag`|S02|region4 的 f3/f4 來自 widgets 0x17/0x18；region2/3 是 0x0f/0x10；flag 由全域 `0x66d110+0x219` 取值|0x4b2858..0x4b28e0、0x5742ec..0x574337；**f3/f4 是額外的原生欄位，無資料足以把兩個 label 唯一對應 NAME/E-MAIL**|
|Region 1 C02 提交|writer 在 region1 只寫 f1/f2/f3|S02|UI 走「非 region0」的 0x0f/0x10 填兩個額外記憶體欄位，writer 只使用其 region1 的 f3|UI/writer layout 差異確實存在；region1 不是 region2/3 的 4-string wire|
|本地 CONFIRM 不等於第二欄|不送 C02|不需要 S02|0x4b290c UTF16 compare 非零 → `0x4b2983` 焦點第二控制項/警告；不發正常 C02|EXE static；**確認欄本身沒有 wire 欄位**|
|在 state0x1d 或0x1e 收到 S02 非零，且 message 非空|**C15 空 body**（0x5715f0/0x5716a0）|S02 status!=0、message 非空|status→焦點 switch、建立顯示 message 的對話框，`0x4b1f1b..0x4b1f34` 送 C15，state **0x1f**；region3 & state0x1e 在 `0x4b1e0d..0x4b1e21` 會跳過 message-display branch|原始 UI 走函式 `0x4b1d60`；**通用文字顯示為靜態可達，沒有跑 GUI**；C15 的 Server 反應與 TCP 是否繼續 unknown|
|state0x1d 收 S02 status0|Client 送 **C04 五 u8**|S02(0,message)|`0x4b1f46..0x4b205f` 建 C04、送出並進 state0x1e|C04 本地值來自 UI 角色外觀；**還不是創角已持久完成**|
|state0x1e 收 S02 status0|沒有在此 handler 必然送 C03|S02(0,message)|`0x4b206b` 後續本地 UI 完成分支|實際回到 Login UI 的點擊/關閉順序：native GUI not-run|

## 二、C02 跨 Region UI/widget→wire 映射（指令已核查）

|Region|F1 packet+0x24 / writer+0x18|F2 packet+0x224 / writer+0x218|本地 CONFIRM|F3（存在）|F4（如有）|尾 u8|
|---|---|---|---|---|---|---|
|0|widget **1**（Dialog+0x26c）|widget **2**（Dialog+0x270）|widget **3** (+0x274)，比較用|widget **10** → packet+0x424、writer+0x418（條件可能清空）|**不送**|不送|
|1|widget **12**|widget **13**|widget **14**|writer 取 packet+0x424，但提交分支填 packet+0x624/+0x822（widgets 15/16），**未找到在本路徑寫 packet+0x424 的證據**|**不送**|不送|
|2、3|widget **12**|widget **13**|widget **14**|widget **15** → packet+0x624、writer+0x618|widget **16** → packet+0x822、writer+0x816|+0xa22 → writer+0xa16|
|4|widget **20**|widget **21**|widget **22**|widget **23** → packet+0x624、writer+0x618|widget **24** → packet+0x822、writer+0x816|同上|

此表對應 `0x4b1afa..0x4b1bc1` native widget mapping、`0x4b27b5..0x4b28e0` native input copy、`0x5742b0..0x574352` writer。所有 `string8` 是 encoded byte length + bytes、無 NUL；Locale codepage 需和 Client 配對，TW index4 可按 CP950 對照；其他地區不能照搬。

**語意證據邊界**：
- 用戶所看到 **ID/PASSWORD/CONFIRM/NAME/E-MAIL** 五個標籤屬 user-reported UI。f1=ID、f2=PASSWORD、+0x274=CONFIRM 有功能上的強支持（長度 gate 與兩次密碼確認），但未取得本版 UI 每個標籤的外部資源/畫面 ID 字形，因此視為 `inferred-high`，**不是同名原始 label 字串定位**。
- 在 region2..4，**NAME=F3、E-MAIL=F4 是待原生 GUI/資源證實的候選**，不是本次已證結論；不能排除反過來、某地域不用一欄或其他內容語意。
- region0 只有一個 F3，不能把兩個額外 UI 文字都塞進已證 C02 writer，不能把不存在的 F4 自造出來。Region1 的 UI / writer 不一致是實際疑點，不得忽略。
- `0x4b2764..0x4b2a3c` 的明示提交 gate 對 first-field、confirm、條款，但**未發現額外 f3/f4 的必填 EMAIL 字串測試**。不等於證明 E-MAIL 可空；UI widget 屬性、外部驗證器或其他 callback 仍需查。
- `0x91fed0` 作 first-field 的 region !=0 長度最低界（A-027 既有推 12），此處從程式可追 gate，**未由原生畫面驗證 region 下限**；不要用 Admin 3..32 代替原版 UI gate。

## 三、S02(status/message) 可顯示的「靜態安全候選」及使用限制

`0x57dbc0` reader 讀 **u8 status + string8 message**；`0x4b1da9` 以 `edi+0x24` 選 29 項（status 3..31）focus jump-table，`0x4b1dff` 檢查 UTF16 `message[0]!=0`，非空且不是 region3/state0x1e suppression 就走 `0x4b1e2e..0x4b1ec3` 建 message dialog；`0x4b1eec` 非零分支送 C15、state0x1f。

原件 focus selector（29 項）已逐 byte 離線讀表：
- status **3/4/18/26/31** 設第一欄 focus；status **17** 設第二欄 focus。
- status **1/2** 位於 jump-table 下界外，**不設定特定 focus**；status **5–16/19–25/27–30** 在表內取 default（也不改上述兩個欄位）。**不得由 focus 推導「錯密/帳號不存在/名稱重複」等原服語意。**
- 合成、可本地測的候選：**S02 body `01 10 526571756573742072656a6563746564`**（status=1，ASCII string8 `Request rejected`，字元數16）。在 state0x1d 與該 message 非空、UI 上下文有效時，原碼顯示 message、送 C15；**不是原服實際抓包、不是保證一定不斷線，也未證 status1 原服錯誤意義**。正式 Server 在原生 CT-104/105 驗收前不得把此 fixture 宣稱可安全正式上線。
- 不要使用 `S02(0)` 回報拒絕：在 state0x1d 會導致 Client 進 C04；普通認證失敗應與 TCP frame/加密失敗分流，Server 不能用主動 Close 假裝業務拒絕。

**各狀態差異：** 訊息空字串時 message-dialog branch 不執行但 nonzero C15 仍可走；在 state0x1e + region3 非零非空時 message 被抑制但 C15 路徑仍執行；對於已進 state0x1f 的後續 S02/重送行為未實際測定；成功 UI 和斷線 popup 的判定需 runtime capture。

## 四、Client 原件重現與驗收

`python tools/a030_native_newuser_contract.py`：30 個固定原始 x86 位址+指令 bytes signature、29項 focus selector、region shape、15 個 `unittest` 合成正反 codec、S02 status1/焦點/截斷測試，**offline 15 PASS**。原始檔案不提交，test 不連網、不接 Server、不持有帳密/email。

`objdump -d -Mintel --start-address=0x4b1a90 --stop-address=0x4b1d34 Asgard.exe` (widget region mapping)，`--start-address=0x4b2764 --stop-address=0x4b2a3c` (submit)，`--start-address=0x5742b0 --stop-address=0x574353` (C02 writer)，`--start-address=0x4b1d60 --stop-address=0x4b2180` (S02 status/UI/C15)，`--start-address=0x57dbc0 --stop-address=0x57dc30` (S02 reader)。

對應 CT：
- CT-103：Server 既有 C02/C04/C15 的 socket close 是規劃文件已核對的 source-level 缺口；原生 H0/H1/H2/H3 必須以實機 trace 才能確定，A30 沒有重跑 Server。
- CT-104：原版 Client 在確認 region/profile 後，使用測試帳號，**先比對畫面 label→widget ID**，填入假 NAME / E-MAIL 的兩次測試，遮罩值只記非敏感字串長度與 C02 field ordinal；收到 S02(nonzero text) 觀察畫面是否顯示、C15 是否送出、socket 是否仍開；**不使用現成真實帳密**。
- CT-105：對照 C02→S02(0)→C04→S02(0)→回登入、非法 NAME/EMAIL、錯密、取消、C15 後 retry、Region1 例外分支、已 commit/未 commit 斷線。原 Client GUI E2E 未執行，不能把 offline pass 算作 UI pass。

**缺件與限制**：本次有 `Asgard.exe`、`Born.dat`、`Map0/1/2.dat`，不需再上傳。實際 *畫面 label 與 widget ID* 的 resource 路徑尚未由 EXE 字串/loader 交叉引用確認，**不能憑空捏造精確檔名**；下一步可由原版創角畫面去敏 widget/event+封包 trace 定案，或提供實際客戶端 UI/皮膚資源清單後依 loader 定位精確檔名。需要的現場資料是 **原版操作的 NAME/E-MAIL 欄位前後「去敏 C02 field count/length」與 S02 回包/UI 截圖**，不需要密碼/Email 明文。

## 2026-10-31 主線 RI-001 / RI-005 動態資料補充（同步整合時追加）

此 A-030 報告的 opcode/UI/錯誤狀態機是**靜態 EXE 已證子集**，並不代表使用者最近遇到的連線中斷確定發生在 C02 之後。主線新增 RI-005 觀察在**尚未送出表單前** Server 先送 FIN、Client 仍 Responding；事後 C02 send=-1 是對**已斷 socket** 的嘗試，不能反推 C02 是先前斷線原因。需依 `02-server-planning/idle-disconnect-observability.md` 和 `03-analysis-requests/runtime-issues.json` 分別排查等待輸入 timeout 與送出後 native C02/C04 fail-closed。新版私有 Server 已部署 phase-based form timeout 及匿名化 close journal，但原版 Client 最新一輪實測仍未驗收，不能把 A-030 標 native-ready。實際負責 Server 端 DEV-CREATE adapter 的障礙仍是 NAME/E-MAIL 真語意／是否必填與原生 S02 錯誤 GUI。

## Latest correlated runtime event: modified diagnostic Client, not original Client E2E

2026-10-31 23:51 的 **修改主選單預覽 Client** 回驗：Client C02 send 成功，Server f2a4a38 journal 確認收到 C02(body15、ordinal5)，以 `native-c02-fields-unknown-a030` 關閉、未回 S02。本次 H1/C02 後關閉已定位，不再把這次原因列為「可能60秒閒置」。詳見 [去敏 Client／Server 時間線](../02-server-planning/idle-disconnect-observability.md)。

這只補 A30-1 的診斷切片；欄位／地區、錯誤 UI、取消與成功路徑仍待分析，不重做已證 serializer，也不把修改副本當原版 Client passed。新版 Server 已有 FormInput 600/1800秒政策；後續優先補可接通 C02 的合約，而非繼續調整同一個 timeout。原版 Client SHA 與原版 CT 的要求維持不變。

This confirms A30-1 packet/close reason only for the **modified diagnostic Client**. Original Asgard.exe unmodified CT-103/104/105 remains not-run. Static Client NAME/EMAIL semantic and safe S02 failure mapping remain blocked.


## 2026-11-01 E-MAIL 是否經 C02 發送：後續 BIN-first 核查

已追通原版 region2..4 `C02` 第四個 `string8`：region4 widget `0x18`、region2/3 widget `0x10` → packet `+0x822` → writer this `+0x816` → native C02 send `0x4B229F`。確認畫面亦讀相同 F3/F4（label ID 0x49/0x4B）。**根據使用者畫面的欄位順序，F4 是 E-MAIL 高可信候選，但沒有 `Locale.dat` 或原 Client GUI 對照，尚不能把 E-MAIL 字樣當作已獨立確認的 UI label**。Region0/1 的三字串例外仍在，E-MAIL 是否可留空及 DB 儲存是不同議題。15/15 原始 EXE byte signature PASS；新 `test_16_native_extended_field4_chain` 可重現。詳細見 [A030 E-MAIL 封包確認](A-030-roy1-email-c02-field.md)。


## 2026-11-01 嚴格追鏈完成（Client 靜態證據）

原始 EXE 40/40 machine-code anchors 本地 PASS、6 項離線驗證 PASS。**完整整理**：[A30 NAME/E-MAIL、S02/C15 最終靜態交接](A-030-roy1-native-fields-failure-c15-handoff.md)。Region2..4 F3/F4 實際 UI→C02 confirmed（widget15/16 或 23/24；writer+0x618/+0x816）；確認 popup 以語系 keys **0x49/0x4B** 分別顯示，唯 **key0x49 是 NAME、key0x4B 是 E-MAIL 的原始翻譯文字尚待 `Locale.dat`**。Region1 的 writer 缺 F4 且第三欄來源疑點保留；不把產品 R-035 E-MAIL 保存需求當成已證 Client label。

S02 parser (u8/string8)，非零 status 觸發 Client message modal（非空文字且非 Region3/state0x1E suppress），再 C15 opcode0x15、empty body、local state0x1F，已經 EXE 指令層確認；**不能證明實際 GUI 文案、原版 Server 錯誤碼含義、C15 後 TCP 繼續與重試**。本次工具新增 S02/C15 更嚴格簽章與對應合成模型，原始 Client GUI 未跑；A30 `integrated/partial`，不可誤標 native-ready。
