# A-023／roy2 — 教學入口最小 NPC、Script 與任務初始化依賴（BIN-first）

> 本文保留 E01～E13 的歷史分析；最新已追通的 S44→Main、精確 wire、資源 CRC 與 Dispose 回送，請以 [完整 Client 契約](A-023-script-entry-contract.md)（E14～E18）為準。本文「首次觸發 unknown」現僅適用原服發送政策，不再適用 Client 封包啟動機制；「沒有顯式 SendReply」也不代表關閉時沒有 C6C。

- 日期：2026-10-31；工作路徑：`task_a/roy2`；分析分支：`task_a/roy2`
- 範圍：R-027、SYS-QUEST、ONB-03/05、SCN-009/011；對照 A-011、A-012、A-022。不追教學完成、獎勵、怪物 AI 或技能細節（A-024～026）。
- Client：`Asgard.exe` PE32 x86、ImageBase `0x00400000`、檔案 3,235,840 bytes、SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，匹配 `TW-seed0-local-v0.1` 的既有身份。
- 證據來源：本輪原始 EXE 反組譯與字串／交叉引用（`observed-static`）；本 repo 的既有資源與封包整理（`prior-research`）。現已取得 Born.dat；仍未取得原始 MAP/NPC 定義、原服首登入抓包，無 `observed-runtime`。
- 門檻：A 研究與 DEV/CT 分離；`handoff_status=partial`，可交付原生 Script 通道安全子集與入口狀態的開發／測試規範；**首個必備 NPC、Born 觸發條件、任務步驟／opcode 仍 unknown**，不得標為原生教程已可完整實作。

## 1. 可核查的 BIN 證據

|ID|種類|原始位址及具體觀察|允許結論／限制|
|---|---|---|---|
|A023-E01|observed-static|PE header image base 0x400000、`.text` RVA 0x1000；本檔 SHA 如上|只對指定 Client profile 生效；此處為原始檔而非改版 EXE|
|A023-E02|observed-static| `0x575140` CScript 建構，`0x575159: push 0x6c`；`0x575210` serializer 先讀 `[esi+0x18]` subtype，`0x575221` 與 `0x57522a` 以範圍 `0..4` dispatch|C2S opcode **0x6C**，至少五個不同 serializer 分支；不能把 body `03` 外推到所有 subtype|
|A023-E03|observed-static| `0x5862e0` SScript 建構，`0x5862f9: push 0x44`；`0x4e0b79..0x4e0b85` 進 `0x52c2a0` handler；`0x52c2ca..0x52c2e6` 在 type 1 下按 subtype `0..4` 分派|S2C opcode **0x44**；有多種 script update/執行/控制分支，不是通用 ACK；完整 byte offsets/length 仍需追 parser|
|A023-E04|observed-static| `0x52c8df: mov ecx,[0x66d13c]`、`0x52c8e5: call 0x5294e0` 是 type1/subtype3 路徑；`0x52951d` 參考 `%s\\Script\\*.dat`，`0x52954c` 呼叫目錄列舉 API，`0x529570..0x529583` 迴圈處理項目|該 S44 分支帶**本機 Script 檔案列舉／清快取**副作用；與既有 profile-login.md 對照，不能傳「空成功」或測試 S44(1,3) 而忽略刪檔風險。沒有在本輪執行刪檔|
|A023-E05|observed-static| `0x5290bc` 引用 `R%s\\Script\\%s.dat` 的字串相鄰位置；`0x529351` 引用 `%s\\%s.dat`；`0x5292c6` 引用 `%s\\Script`；`0x52951d` 引用 `%s\\Script\\*.dat`|Client 有按名稱載入／更新與掃描外部 Script .dat 的機制；不是內建固定 Born 內容|
|A023-E06|observed-static| `0x521d32` / `0x521d84` 對應 Unicode `client` / `Script` 的 script 物件註冊；`0x526626` 取 `SendReply`、`0x526652` 呼叫 `0x51a9f0`；`0x51aa3c` 在後者建構 `0x575140` 的 CScript 並於 `0x51ab3d` 走 packet 送出程序|Client 腳本可透過 `SendReply` 建構 C6C 回送，但本輪**未**證明它是哪個教學 NPC 或首個任務事件|
|A023-E07|prior-research| `04-analysis-integration/resource-formats.md`：`Script/*.dat` 外層 zlib 解壓；4-byte header `00 01 00 00`、BE u16 UTF-16 長度、UTF-16LE XML；315 XML、NDW 為非 XML。該整理稱 `Born` 為新手對話／座標導引|這是先前資源研究摘要，**不是本輪有 Born.dat 原件的驗證**；不能推論 Born 一定是登入後自動觸發或唯一首個 NPC|
|A023-E08|prior-research| `04-analysis-integration/scenarios.md`／`packet-processing.md`：已知世界初始化 S02→S05→S15→S14(1)→C35→S04/S33→S14(2)；`profile-login.md` 的 C6C(03) 最小 Server 不回覆|可當最小 profile 的入圖基線，**不是**本輪證實「沒有首段教學 Script」；不以經驗測試反證未抓到的原服訊息|

### 位址重現（不需原 Server）

```sh
sha256sum Asgard.exe
objdump -h Asgard.exe
objdump -d -M intel --start-address=0x575140 --stop-address=0x575310 Asgard.exe
objdump -d -M intel --start-address=0x5862e0 --stop-address=0x586410 Asgard.exe
objdump -d -M intel --start-address=0x52c2a0 --stop-address=0x52cb10 Asgard.exe
objdump -d -M intel --start-address=0x5294e0 --stop-address=0x52959d Asgard.exe
objdump -d -M intel --start-address=0x526626 --stop-address=0x52665e Asgard.exe
strings -el -t x Asgard.exe
```

判讀限制：`strings` 能找到 Script 與 UI API 名稱不代表對應函式必然在新手地圖執行；函式及封包名稱是定位線索，只有指令/呼叫關係才是上述 confirmed static。原始 .exe、資源、完整反編譯及其他人的私有程式不提交共用 repo。

## 2. 客戶端入口的最小狀態模型（非臆測原服）

### 追加 C6C serializer 契約（A023-E13，observed-static）

REA/Ghidra 12.1.4 對指定 SHA 核查 `0x575210`，Evidence `ev_78de5bbeebab4156741f475aa2cced960617a78e69ae64287a9339ab013efe76`。以下是 body 的序列化順序，排除 frame/opcode；欄位名稱僅表示儲存位置，未賦予任務語意。

|subtype|body 順序|來源物件 offset|
|---|---|---|
|0|u8(0), string8|0x18、0x1a|
|1|u8(1), string8, u32, u16 count, count 組 (string8, string8)|0x18、0x1a、0x21c、0x220；array 0x224，每組 stride 0x400，兩字串差 0x200|
|2|u8(2), string8, u32|0x18、0x1a、0x21c|
|3|u8(3)，沒有額外 payload|0x18|
|4|u8(4), string8, u32|0x18、0x1a、0x21c|

writer `0x45ab00` 寫一 byte；`0x45b1b0` 以 `WideCharToMultiByte` 和全域 codepage `0x66e47c` 編碼，寫 u8 byte length 再寫字串 bytes，wire 不含 NUL；buffer 256 bytes，長度最多 255。長字串轉換失敗的 native API 行為不可當安全截斷策略。`0x45ab40`/`0x45ac40` 寫 2/4 bytes：writer offset 0x10 非零時 BE，零時 native x86 LE。本輪未追本通道該 flag 初始化及 codepage 值，故不可直接稱所有 subtype 為固定 BE/Big5。

上述四個 helper 的 REA Evidence 依序為 `ev_3d1ec696a0779fc38c07d16ea384ad72549b8145577aa9078e7c17ad2189574a`、`ev_a9616b9b5418d23da5026960e5e56187746f59ce5c320ad4822490744c87ae88`、`ev_c0c9aae0fec0512d0350e44781aa437705febcf4e6eac993011a64b6ff92c338`、`ev_f4228c3d7b533e44801a49be40fdaf34baaccd71be47a47ebf6b0876d9de8886`。以對應地址呼叫 REA `procedure_pseudo_code` 可重現；反編譯為工具輸出而非原始碼或 runtime。未知 subtype 先寫 selector 然後將物件 offset 0x14 的有效旗標清零；Server 應拒絕未支援的 schema，不猜回覆。仍未證實哪個 subtype 對應首 NPC／任務。

|階段|既有基線|Script/NPC 的證據結論|Server 作法|
|---|---|---|---|
|登入前 Script 協商|C6C body 03：既有 local-profile 不回覆|observed-runtime-profile（舊測試）；C6C 其他 subtypes unknown|不得將該次「不回」推導為任一教學 Script 永遠不需要|
|Token 世界交接|S03→C10→C25→S02/S05|prior-research|未建立 session/角色 ownership 前，不接受腳本互動／獎勵／NPC 對話完成聲稱|
|進圖載入|S15、S14(1)、C35、S04/S33、S14(2)|prior-research；原生教學 map、出生點依 A-022|入圖中只準備必要內容，不以 S14(2) 自動標 `tutorial_completed`|
|可操作後首事件|C6C/S44 都存在於 Client，`SendReply` 可回 C6C|observed-static（功能存在），**是否在此階段觸發 unknown**|原生 Script/NPC 內容與首觸發規則待資源／A-022 交叉驗證；不可發假 S44 或假 NPC 來冒充原版|
|後續任務|原版任務 flags、NPC id、必須互動次序、獎勵均不明|unknown|A-024/025/026 分管生成／戰鬥／完成；不得填猜測值|

最小可交付 wire 子集：
- `PKT-C6C`：C2S opcode `0x6c`，`0x575140`，serializer `0x575210`；已知 subtype 有 0..4；每種可變 payload 的精確 offset/編碼不完整。`C6C(03)` 是 local login profile 觀察，不代表全部教學回覆。
- `PKT-S44`：S2C opcode `0x44`，constructor `0x5862e0`、dispatcher `0x52c2a0`；已見 type1/subtype0..4 與 type2 分支。type1/subtype3 會進 `0x5294e0` 本地 Script 掃描/清理。尚未確定 S44 哪個 subtype 是入教學事件，也不知全部壓縮欄、大小與成功失敗狀態。**Server 不可用合成 S44 當作已知通用觸發。**

## 3. 教學首段是否需要 NPC／Script／任務的問答

|待回答|結論與確信度|下一個可重現驗證|
|---|---|---|
|是否有新手導引 Script 資源？|既有資源研究提及 `Born`，prior-research，可能性高但未親查原件|提供匹配 SHA 的 `Script/Born.dat`／Script 資源集合，解壓 XML/CDATA、索引所有指令/API|
|首次載入教學地圖是否**自動執行** Born？|unknown；不能把存在誤讀成首次觸發|取得 A-022 map/出生、Client 初始化呼叫鏈，追 `0x529060` 的 key 來源，或隔離原服捕獲事件|
|首個 NPC 是誰、id/位置/可見性？|unknown，EXE 不含已驗證地圖生物表|取得版本化地圖/NPC/事件定義，對照 A-011/A-024 的 object parser/handler|
|是否必需送 S44 才能讓角色移動？|unknown；最小 profile C6C(03) 不回覆不構成否證|原生教程與非教程對照，錄首圖 S14(2) 前後 UI、封包及未互動下行動|
|首個任務 UI/flag/quest event/回包？|unknown；Script 可建立 dialog 並 SendReply，但具體任務語意無證據|資源腳本中的 `CreateDialog`、`SendReply`、資料鍵/事件 hook 與 BIN 呼叫點逐一映射|
|拒絕、取消、重送、斷線與重登入|原版原生 Script 回覆狀態及重播語意 unknown|同一 NPC 先接受/再取消/重送與舊 generation；CT-034 驗證 Server ledger 不錯誤加進度|

**無實機不構成分析停止理由。** 本輪已完成 EXE-only 可以核查的 Script 協定、快取副作用及前置時序研究；真正需資源／原服訊息的必要欄位是研究證據缺口，保持 partial，不自行捏造。

## 4. 可交付 DEV 的防 BUG 規則（designed，非原版事實）

1. `ScriptCatalog` 使用 Client hash、Script revision/hash、載入結果、來源；`Born` 可列為待查候選，但尚不允許設為「必需」或自動指派首步。
2. `TutorialEntryState` 明確區分 `world_loading`、`world_ready`、`tutorial_entry_committed`、`tutorial_completed`；進圖與完成分離。收到腳本回覆前驗 Session/character/instance generation。失敗不可偷改完成旗標。
3. 將 `CScript` 按 subtype 分配 schema/欄位驗證、大小限制及必要的 Script/對話 context；未知 subtype 應記可控不支援／拒絕，不以空成功處理。
4. `SScript` 的快取更新/刪除不是純 UI 彈窗；未掌握安全 schema 和必要條件前不主動發，尤其不發 type1/subtype3 清快取；拒絕路徑不擬造 opcode。
5. NPC/初始任務僅從經確認的 profile/content revision 載入；若缺官方資源就「native-content-unresolved」，勿使用假 NPC id/座標在官方 profile。
6. 未來任務觸發與初始 grant 應由 Server 權威、原子性/冪等 ledger 實作；現階段這只是安全設計，不當作原服協定。
7. UI/Client 事件需等 World/MapPane 有效；**不代表**確認了某個 Born 自動啟動時點。不可因缺 CT-033/034 就抹掉 E02～E06 的靜態證據。

## 5. 下游 CT 計畫（尚未原生測試）

- **CT-033 Script 通道與副作用防護**：在隔離測試副本（先備份 Script）重現 C6C subtype0..4/SScript type1/2 分派。只驗 BIN serializer/parser／file sandbox 行為，S44 type1/subtype3 須明確禁用正式服或於可丟棄檔案環境觀察；不得將其當普通 ACK。缺 byte layout 時先跑 mock unit 檢查，不送未知真實封包。
- **CT-034 首次可操作邊界**：管理員預建無角色帳號，原 Client 創角、首次進 A-022 證實的教學圖；收集 S14(2) 前後、最初 NPC/Script/任務視窗是否主動出現、mapID/NPC ID、C6C/S44 實際 bytes，與不互動控制組比對。無原 Server 時先用 DEV 模擬/事件 instrumentation，標 mock；真正相容判定待原 Client CT。
- **CT-035 中斷／重送**：對首個已驗證事件進行取消、重送、重登入與未載入完成即回覆；Server 拒絕 stale session、重複 ledger、不在錯誤時間更新 quest。
- 所有 CT：Owner=DEV/CT；`native_client_validation=not-run`；本輪沒有執行 Client GUI。

## 6. Handoff／待證據

研究項目已具體核查：`A023-E01..E06` 的 EXE/指令、既有整合 `E07..E08` 的基準，並把多 subtype 與快取清理列入可用的 Server 風險規格。限制是 **首個不可省略的教學觸發/NPC/Script ID/quest flag 尚未解**。交接至 A-022（原教學 map/出生）、A-011/A-012（NPC/腳本語意）、A-024（首 NPC 生成與封包）與後續 DEV/CT；若原始資源補齊，應回本 A 追加精確觸發證據，補齊缺口後才能改為 `handoff_status=ready`。

本成果進 review；可接受「有限子集整合、A partial」與「原生全段仍未可實作」同時成立。不聲稱 peer-review 已完成，不以 CT 未開始為失敗原因。

## 最新交付：PaperDialog 直接依賴（A023-E12）

2026-10-31 在 `task_a/roy2` 追加核查。下文第 7 節取代前文 Born 尚未取得的歷史問答；本節補完 Born 的直接 Script UI 依賴。CT 編號已依主線調整為 CT-033～035，避免與帳號／創角 CT-029～031 混用。

- `PaperDialog.dat`：1639 bytes，SHA256 `5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054`；解壓 9196 bytes，SHA256 `491021376f9500c2a32a3c3ab56439bb302b39c660147903dcc4ba4b5c6f526a`。同樣採 `00010000`、BE u16 4595 UTF-16 code units；與 EXE 的發行配對仍 unverified。
- XML 定義 `PaperDialog_Create(titleString, helpArray)`、`ShowIndexedHelp(paperDialog, index)`、`PaperDialogProc(dialog, control)`。這是 Born.Main 外部函式的直接定義，不可只部署 Born 並假設函式內建於 EXE。
- 建立紙張對話，註冊 `PaperDialogProc` callback；保存 `PAPERARRAY` 與 `INDEX=0`，顯示第 0 頁。Born 只插入一頁，因此依靜態分支推導 PREV/NEXT 皆隱藏，預設與取消控制均為 OK。這是資源預期，尚未在 GUI 觀察。
- OK 分支依序呼叫 `dialog.Dispose()`、`client.Dispose()`。三個函式沒有顯式 SendReply、SetQuest、SetFlag 或 NPC spawn 呼叫；不能從字面名稱推定 `client.Dispose` 會斷線，也不能排除 native API 的內部副作用。關閉視窗不得被 Server 當作收到任務完成回報。
- 視覺依賴還包含 `Basic.dat/AlertFrame.ypf` 與 image button object 11/12/13。本輪只確認引用，未驗證這些資產解析、載入成功或版本配對；沒有將其加入 Git。

重現：`python task_a/roy2/verify_entry_dependencies.py /local/Script`。驗證兩份原件 hash、完整 zlib stream、wrapper/XML、callback、首頁、翻頁條件及關閉分支；不執行遊戲腳本。機讀結果見 `entry-dependency-verification.json`。完整資源 PASS；缺 PaperDialog、截斷及版本不符須 FAIL。此工具限上述固定 hash，不是任意腳本語言的通用解析器。

交付判定：A-023 的現有可取得靜態分析與依賴交接已追加完成，保留 integrated/partial。原生首次觸發、必要 NPC/任務 opcode 尚不足以宣告 ready；CT-033～035 仍由 DEV/CT 執行，native_client_validation=not-run。

## 7. Born.dat 已補：原件實證與 A-023 交接結論（2026-10-31）

|證據|核查結果|不能推導的內容|
|---|---|---|
|A023-E09 observed-static-resource|原始 589 bytes、SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`；zlib 解壓 1154 bytes、SHA256 `a33d271e4f71e9958f59060b1aba01430919752a357b9615d60271b26c933546`。頭 `00010000` + BE u16 `0x023e=574` UTF-16LE code units，`6+2*574=1154`；唯一 XML `<script><function name="Main">`。|無法證明此資源和 EXE 屬同一版本，沒有原版觸發設定|
|A023-E10 observed-static-resource|`Main` 順序：`client.CreateArray()`、`page.Insert(msg)`、`PaperDialog_Create("",page)`；文字要求玩家往**中間 (31,29)**，點選**女性招募員**（滑鼠）。|座標是**文字導航目標**，不是已驗證出生點／NPC spawn，也沒有實體 NPC ID 或 map ID|
|A023-E10 absent calls|此 Main 不含明確 `SendReply`、`SetQuest`、`SetFlag`、`SpawnNpc` 呼叫。|不能由單一腳本證明引擎內部沒有副作用、沒有其他任務或必然自動啟動|
|A023-E11 observed-static|EXE IAT `0x5f11fc=KERNEL32.DeleteFileA`；`0x529569` 讀取該 IAT，`0x529575` 間接呼叫；S44 handler `0x52c8e5` 通往 `0x5294e0` 的 Script cache 掃描流程。|不能拿 S44 type1/subtype3 當無副作用 ACK；本輪沒有實際執行刪檔|

本輪用 Python stdlib 完成離線 zlib/UTF-16/ElementTree 解析與字串遮罩後呼叫核查，正常資源 **offline PASS**；截斷檔 **FAIL**。可執行 `python task_a/roy2/verify_born.py /local/Born.dat` 重現；原始 Born.dat 不提交 Git。機讀摘要在 `04-analysis-integration/tutorial-born-resource.json`。

### 入口最小依賴／決議

1. **已證**：存在一個只顯示教學紙張對話並引導玩家去 (31,29) 點選招募員的 `Born.Main` 資源；原生 Client 的 C6C/S44 script 通道存在且有危險清快取分支。
2. **仍未證**：是否首次登入自動呼叫 Born.Main、首個不可省略的 NPC、招募員身分及原生初始任務/互動 wire、原服回覆。單憑 Born 沒有這些欄位，不能在正式 profile 填猜測值。
3. **DEV 交接**：ScriptCatalog 可登記 SHA256 驗證的 Born 候選，Dialog 可按內容資源發生但不得自稱原版已觸發；WorldReady、EntryCommitted、TutorialCompleted 分開；不主動發未知 S44，拒絕 stale/未載圖的互動。
4. **A gate**：`status=integrated`、`handoff_status=partial`、`native_client_validation=not-run`。完成本次實際可取得的資源與 BIN 證據整合，原生首次觸發/必要 NPC 缺口交 A-022/A-024、quest/對話分支交 A-012/A-026，實機由 CT-034/035；不是等新 Server 才停止分析。舊段落的「沒有 Born 檔」敘述屬先前階段，以本節為準。
