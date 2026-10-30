# A-023／roy2 — 教學入口最小 NPC、Script 與任務初始化依賴（BIN-first）

- 日期：2026-10-31；工作路徑：`task_a/roy2`；分析分支：`analysis/A-023-roy2`
- 範圍：R-027、SYS-QUEST、ONB-03/05、SCN-009/011；對照 A-011、A-012、A-022。不追教學完成、獎勵、怪物 AI 或技能細節（A-024～026）。
- Client：`Asgard.exe` PE32 x86、ImageBase `0x00400000`、檔案 3,235,840 bytes、SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，匹配 `TW-seed0-local-v0.1` 的既有身份。
- 證據來源：本輪原始 EXE 反組譯與字串／交叉引用（`observed-static`）；本 repo 的既有資源與封包整理（`prior-research`）。未取得原始 `Script/*.dat`、MAP 及原服首登入抓包，無 `observed-runtime`。
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
|拒絕、取消、重送、斷線與重登入|原版原生 Script 回覆狀態及重播語意 unknown|同一 NPC 先接受/再取消/重送與舊 generation；CT-030 驗證 Server ledger 不錯誤加進度|

**無實機不構成分析停止理由。** 本輪已完成 EXE-only 可以核查的 Script 協定、快取副作用及前置時序研究；真正需資源／原服訊息的必要欄位是研究證據缺口，保持 partial，不自行捏造。

## 4. 可交付 DEV 的防 BUG 規則（designed，非原版事實）

1. `ScriptCatalog` 使用 Client hash、Script revision/hash、載入結果、來源；`Born` 可列為待查候選，但尚不允許設為「必需」或自動指派首步。
2. `TutorialEntryState` 明確區分 `world_loading`、`world_ready`、`tutorial_entry_committed`、`tutorial_completed`；進圖與完成分離。收到腳本回覆前驗 Session/character/instance generation。失敗不可偷改完成旗標。
3. 將 `CScript` 按 subtype 分配 schema/欄位驗證、大小限制及必要的 Script/對話 context；未知 subtype 應記可控不支援／拒絕，不以空成功處理。
4. `SScript` 的快取更新/刪除不是純 UI 彈窗；未掌握安全 schema 和必要條件前不主動發，尤其不發 type1/subtype3 清快取；拒絕路徑不擬造 opcode。
5. NPC/初始任務僅從經確認的 profile/content revision 載入；若缺官方資源就「native-content-unresolved」，勿使用假 NPC id/座標在官方 profile。
6. 未來任務觸發與初始 grant 應由 Server 權威、原子性/冪等 ledger 實作；現階段這只是安全設計，不當作原服協定。
7. UI/Client 事件需等 World/MapPane 有效；**不代表**確認了某個 Born 自動啟動時點。不可因缺 CT-029/030 就抹掉 E02～E06 的靜態證據。

## 5. 下游 CT 計畫（尚未原生測試）

- **CT-029 Script 通道與副作用防護**：在隔離測試副本（先備份 Script）重現 C6C subtype0..4/SScript type1/2 分派。只驗 BIN serializer/parser／file sandbox 行為，S44 type1/subtype3 須明確禁用正式服或於可丟棄檔案環境觀察；不得將其當普通 ACK。缺 byte layout 時先跑 mock unit 檢查，不送未知真實封包。
- **CT-030 首次可操作邊界**：管理員預建無角色帳號，原 Client 創角、首次進 A-022 證實的教學圖；收集 S14(2) 前後、最初 NPC/Script/任務視窗是否主動出現、mapID/NPC ID、C6C/S44 實際 bytes，與不互動控制組比對。無原 Server 時先用 DEV 模擬/事件 instrumentation，標 mock；真正相容判定待原 Client CT。
- **CT-031 中斷／重送**：對首個已驗證事件進行取消、重送、重登入與未載入完成即回覆；Server 拒絕 stale session、重複 ledger、不在錯誤時間更新 quest。
- 所有 CT：Owner=DEV/CT；`native_client_validation=not-run`；本輪沒有執行 Client GUI。

## 6. Handoff／待證據

研究項目已具體核查：`A023-E01..E06` 的 EXE/指令、既有整合 `E07..E08` 的基準，並把多 subtype 與快取清理列入可用的 Server 風險規格。限制是 **首個不可省略的教學觸發/NPC/Script ID/quest flag 尚未解**。交接至 A-022（原教學 map/出生）、A-011/A-012（NPC/腳本語意）、A-024（首 NPC 生成與封包）與後續 DEV/CT；若原始資源補齊，應回本 A 追加精確觸發證據，補齊缺口後才能改為 `handoff_status=ready`。

本成果進 review；可接受「有限子集整合、A partial」與「原生全段仍未可實作」同時成立。不聲稱 peer-review 已完成，不以 CT 未開始為失敗原因。
