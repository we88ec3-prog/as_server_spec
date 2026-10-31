# 分析需求

每個A由Server規劃的具體缺口提出，也可依系統、功能或情境深入。分析不是無範圍全量掃描；先寫要回答的問題、最小入口、成功條件及前置依賴，再選REA／資源解析／原Client實測。

|ID|系統|優先序|問題|方法|交付門檻|
|---|---|---|---|---|---|
|A-001|SYS-AUTH|P0|種子表、版本分支與字串|沿socket codec及語系分支補表0..9、長度單位與錯誤版本處理。|每個已支援profile給解碼向量，未解分支不得填猜測值。|
|A-002|SYS-AUTH|P0|重複登入及斷線交接|正常／錯誤密碼／token過期／同帳號兩連線／交接途中斷線。|雙客戶端實測與連線狀態機；確認原型政策和原生必要行為的差異。|
|A-003|SYS-CHAR|P0|創角合法值與帳號角色模型|查建立介面、C02/C04、重名、取消、名字編碼及一帳號多角色是否原生支持。|合法集合、失敗代碼、兩階段回復；不先假定現代帳號多角色UI。|
|A-004|SYS-WORLD|P0|多人進出視野|兩原客戶端與MapPane/object registry；追加入、移除、死亡、斷線與ID重用。|確定出生／更新／移除封包、ID生命週期、作用域與可見性情境。|
|A-005|SYS-MOVE|P0|碰撞及移動權威|追map tile/block位元與尋路；正常／阻擋／邊界／速度超限／重送序號。|碰撞資料語意及拒絕／校正向量；標記速度政策是否原服還原。|
|A-006|SYS-LOOK|P0|螢幕置中及獨立染色驗收|依8/9鏡頭及S05/S33已知RGB，批次站立、八向移動、更衣、切圖、重登。|原客戶端人工驗收；目前僅自動與靜態，不能先標通過。|
|A-007|SYS-ITEM|P0|完整背包與裝備生命週期|追CUseInventory、CWear、脫裝、物品刪減、數量、槽位、持久物品ID。|實體物品模型及非衣櫃情境：使用失敗／背包滿／斷線／重送。|
|A-008|SYS-STATS|P1|數值／狀態面板|由狀態UI讀取、封包parser、裝備修正追所有顯示與單位。|初始數值、更新、溢位與死亡邊界；未知公式獨立列出。|
|A-009|SYS-COMBAT|P1|攻擊命中傷害死亡|從輸入→C2S→動畫／傷害／HP→死亡→復活，查失敗與中斷。|完整收發時序、公式來源、權威裁定及同時死亡策略。|
|A-010|SYS-SKILL|P1|技能施放與持續效果|逐類：單體、範圍、治療、BUFF、召喚；查範圍、消耗、冷卻、取消。|技能型別表、效果更新及過期，原規則與設計補完分列。|
|A-011|SYS-NPC|P1|怪物/NPC與掉落|由資源、可見物件及互動UI追物件類別、外觀、AI動作與掉落。|生成／移動／消失／互動對話的最小可驗收鏈。|
|A-012|SYS-QUEST|P2|任務腳本與對話協定|查Script資料、執行環境、對話選項、任務條件、獎勵發放。|區分client呈現與server規則；不可把client腳本當全部Server邏輯。|
|A-013|SYS-ECONOMY|P2|商店／倉庫／玩家交易|逐情境拆開追選擇、價格、堆疊、鎖定、確認、取消及斷線。|各情境交易邊界及防重領測試；金額上限與編碼來源。|
|A-014|SYS-SOCIAL|P2|聊天／組隊／公會|查各輸入通道、UI事件、權限及成員狀態；先確認功能存在。|各頻道收發路由、非法操作、離線及斷線情境。|
|A-015|SYS-CONTENT|P0|資料檔語意及權利範圍|盤點地圖、衣服、技能／物品定義；為每欄記原始位置與未知語意。|可驗證的資料格式和抽取步驟；不在共享repo附原始遊戲資產。|
|A-016|SYS-PERSIST|P0|事件重送及崩潰回復|登入狀態、移動確認及未完成切圖、交易、領獎跨斷線／重啟。|每項操作的冪等鍵、提交點、已確認成功的定義。|
|A-017|SYS-OPS|P0|管理操作及可觀測性|列出角色調整、生成物品、傳送、封鎖與追蹤的權限和記錄需求。|管理API與遊戲wire分離；無敏感body的診斷欄位。|
|A-018|SYS-OPS|P1|負載與時序模型|量測PBKDF2、DB寫入、tick、可見性與輸出佇列；不預設支援人數。|2客戶端正確性→可重現負載基準；再選tick與容量。|
|A-019|SYS-AUDIO|P2|原地圖音樂配置|追原資料是否含map→track對應；找不到時保持明示自訂配置。|原曲目對應有證據，或明確宣告未知；不可把測試曲1當官方配置。|

詳情及狀態以requests.json為準。先完成A-004多人可見性與A-005移動權威的閉環。結果提交後必須更新04區，不只將A標完成。

新增A-020：完整登入前metadata／Script／清單分支，先以profile-login.md的可實作最小子集為基線，再補其他原生種類與拒絕情境。

## 首次玩家新增分析需求（2026-10-31）

|ID|優先|必須回答|
|---|---|---|
|A-021|P0|預建空角色帳號如何進原生 Client 創角 UI、C02/C04/S02 及轉服；禁止 Client 註冊 Account。|
|A-022|P0|原生新手地圖 ID、出生座標、進圖條件、CRC 失敗、重登恢復。|
|A-023|P1|教學入口不可省略的 NPC/Script/任務初始化；不要求完成教學。|

以上均為 open，不能因規格完成而標記已解析。

## 新增 A-024～026：教學玩法待分析

- **A-024（P1）**：教學 NPC／怪物實際生成、行動、AI 與清除。
- **A-025（P1）**：教學必需的技能/攻擊、權威結算、目標與任務計數；若原版沒有這些操作，交付反證並更新規格。
- **A-026（P1）**：教學完成/獎勵是否存在、出口轉圖與重登。

A-021/A-022 應優先分配，A-023 可先做靜態研究；**所有新 A 仍 open/unassigned**。詳見 [可交付給分析人員的分工包](onboarding-assignment-pack.md)。

## A 任務交付與原生 Client 驗收的分界（所有 A 適用）

**A 的結案標準是可稽核的逆向成果，不是原生 Client 已連上新 Server。** A 的已知/未知需要交付；完整 Client E2E 是後續 DEV/CT 的獨立驗收。執行前必讀 [跨角色工作關卡](../00-governance/phase-gates.md)、[A 通用模板](request-template.md)，A-021 則讀 [專用驗收](A-021-acceptance.md)。所有 A 在 requests.json 記 `completion_policy`、`handoff_status` 與獨立的 `native_client_validation`，不可把 CT 未通過當成 A 未完成的唯一理由。

## roy1 核對後新增 P0 解析任務

- **A-027**：C02 能在 C03 前送出，必須查明預建 Account 的身份與憑證如何安全校驗、綁定；不容許未認證聲稱擁有帳號。
- **A-028**：C04 之後 Client state 0x1e 的 Server 成敗回覆、建角提交時機和重登／轉服結束流程。

A-021 保留 `integrated / handoff_status=partial` **僅表示靜態證據子集可交付**；整條原生創角仍需要 A-027/A-028。見 [roy1 merge 後審核](../04-analysis-integration/A-021-roy1-review.md)。

## A-022 roy1 分析已整合（通用 World-loading）

[原始靜態報告](A-022-roy1-bin-analysis.md)、[協定整合](../04-analysis-integration/A-022-map-loading-crc.md)。S14/S15/C35/S04 的部分 layout、map checksum 的結構化計算、MAP record 16 bytes 有可核查 BIN 根據；`status=integrated/handoff_status=partial/implementation_ready=true` 僅指通用 loading，`tutorial_content_ready=false`、`native_client_validation=not-run`。教程 map/spawn 必須接續 A-015 資源調查。

## A-023 roy2 靜態／Born 資源子集已交付

[原始研究](../task_a/roy2/A-023-analysis.md)、[整合結論](../04-analysis-integration/script-and-tutorial-entry.md)、[Born 機讀摘要](../04-analysis-integration/tutorial-born-resource.json)。C6C/S44 的分支與危險快取行為已定位；Born.Main 描述 (31,29) 女性招募員是**文字目的地非出生點**。A-023 可設 `integrated/handoff_status=partial`，但首觸發/首 NPC/quest wire 仍需後續研究，Native E2E not-run。測試 ID 經併入 main 後統一 CT-033..035。
 
## A-001 / roy1：十張 seed mask 的 BIN-first 靜態整合（2026-10-31）

原本 A-001 open 且未有獨立交付；本輪已從同 SHA 的原版 `Asgard.exe` `0x53B630` 分支追出 **seed0..9 每張 256 項遮罩公式**，連同 `0x53BE70/0x53BD90` body XOR、C00/S00 version/result 分支、string8 encoded byte 長度、ASCII alternate mode 範圍，整理成 [研究報告](A-001-roy1-seed-and-version.md) 和 [可執行合成測試](../tools/a001_codec_vectors.py)。更新 `04-analysis-integration/transport.md`、封包欄位與 CT-036。狀態 `integrated/handoff_status=partial/implementation_ready=true/native_client_validation=not-run`：binary seed0..9 算法可開發，原服各 region seed/key 選擇、非零 S00 拒絕 UI 與 ASCII 全相容仍 unknown。原版 E2E 屬 DEV/CT，未實機不阻擋已證靜態交付。

## A-002 / roy1：重複登入／C03→S03→C10 交接研究（2026-10-31）

[完整 BIN-first 研究](A-002-roy1-login-transfer.md)、[可執行 Server 狀態機合成測試](../tools/a002_session_model.py)。A-002 `integrated/handoff_status=partial/implementation_ready=true/native_client_validation=not-run`。靜態證實 C03 string8/string8/u8、S02 status+message、S03 addr/port/u8 token_len/raw bytes，以及地區3/4 S03 handler `0x4A8370` 連 World 後發送不帶額外長度的 C10 raw token；**此地址先前被 A-022 誤認成 C25 入口，已修正**。重複登入原服 kick/reject 策略仍 unknown；Server 先採帶 generation 的單一 World 狀態與 once-only grant，CT-037/038 留待下游驗證，不因沒有實機停工。

## A-015 roy2／資源檔與分享界線（2026-10-31）

已完成原始 EXE 對資源池、MAP/YPF loader 的 BIN 核對，Born.dat 實際重跑與 synthetic DAT/MAP/Script 結構測試；新增 [A-015 報告](../task_a/roy2/A-015-analysis.md)、[結構化資源欄位](../04-analysis-integration/content-resource-catalog.json)、[可在個人資源目錄執行的無素材輸出檢查](../tools/a015_content_probe.py) 和 [CT-039/038 計畫](../05-conformance/A-015-content-test-plan.md)。`status=integrated/handoff_status=partial` 指已證的格式/來源子集，**不代表原版教學地圖/技能物品/碰撞/授權已全部解出**。

## A-015 補充原始地圖檔已收齊（2026-10-31）

Roy2 現已獨立解析 `Map0.dat`、`Map1.dat`、`Map2.dat`：**494 張地圖結構全部通過**；330 個 unique binary map payload、33 組重複；`Born` 的 (31,29) 可位於 477 張圖尺寸內，無法據此判定真正新手地圖。詳細來源、hash 與方法見 [A-015 報告](../task_a/roy2/A-015-analysis.md)／[map corpus metadata](../04-analysis-integration/a015-map-corpus.json)。完整 Native Client CT-040 仍須找原版觸發與 spawn，A-015 handoff partial 不變。

## A-015 task_a/roy2 續查（2026-10-31）

在既有 `task_a/roy2` 分支續查 A-015（不另建分析分支）：取得 MAP 原件的 7／8／16-byte record 欄位型別原生 accessor、494 張地圖的標頭差異與疑似像素座標範圍，新增 [研究報告](../task_a/roy2/A-015-field-audit.md) 和 [metadata-only 重跑工具](../task_a/roy2/a015_field_audit.py)。A-015 仍 `integrated/partial`，尚無 Human/完整技能與物品定義；不提前轉做 A-016。

## 2026-10-31 最新 Client 收發交接優先規則

上面的歷史 A-XX 表格含有「原服怎麼決定帳號、出生、任務、AI」的舊問法；**以 [全員接案規範](../00-governance/task-ownership-and-client-io.md) 與 [最新 Client I/O 交付標準](client-io-handoff-standard.md) 為準**。每個 A 已有 `requests.json.handoff_track`，新接案必須用同一模板；Client 研究看 trigger→C→S→S→C→UI，Server 政策由 DEV。實際可開發分段見 [Server 縱切計畫](../02-server-planning/client-io-delivery-plan.md)。

## 2026-10-31 Roy1/Roy2 最新分析交接

11 項新 integrated/handoff 子集：Roy1 A-007/019/020/025/026，Roy2 A-004/005/006/008/009/024。**已證 S07 14 kind 解碼，不再回報「非空 S07 未解」**；真正需要補的是 kind→Client sprite/renderer/EntityId，以及 A-027 原生登入後創角、地圖真 C25/CRC、S1E/S5F 死亡類別爭議、教學 NPC/Quest UI。見 [新待分析列表](post-merge-analysis-queue.md)。Native E2E 是 CT 工作，不是 A 靜態 handoff 必要條件。

## 2026-10-31 現行 task_a/roy1 + task_a/roy2 再同步

Roy1 A-013 的商店/交易原生 codec 與 A-011 的 Monster bank/S1A/C39，以及 Roy2 A-015 MAP/collision 研究已驗證增量整合；Roy1 A-022 地圖 index 多4B錯誤修正為494/494 MAP，不採491/494。主線新增經濟 CT-087/088/089、MAP CT-090/091（原版 Client E2E 未執行），詳 [整合審查](../04-analysis-integration/merge-review-roy1-roy2-20261031.md)。不修改原版 Client，遊戲密碼4～8字、多玩家同圖不變。

## 2026-10-31 Roy1/Roy2 最新分支再次同步

Roy1 沒有新待合入提交；Roy2 A-010 離線 CI metadata 已增量轉入主線，主線保留 Economy CT-087..089、MAP CT-090/091、Quest CT-092..094、Skill CT-095/096。來源 Roy2 的局部編號 CT-087/088/089/090 **不可覆寫**。本輪 Web 管理 UI 只有 Server 設計，不需要偽造 Client 原生 opcode。詳 [整合審查](../04-analysis-integration/roy-branch-web-admin-sync-20261031.md)。

## 2026-10-31 Roy1 新的 A-029 / A-030 Client 靜態交付

- **A-029**：原生改密碼 C26（0x26）實際存在，body=Account/old/new 3×string8，確認新密碼本地比對，不傳第四欄；S02 generic handler 已定位但官方 status/原生 GUI 未驗。見 [A-029](A-029-roy1-native-password-change.md)、[整合契約](../04-analysis-integration/A-029-native-password-change-contract.md)。
- **A-030**：原生 C02 的 region0/1/2..4 widget→field slot 及 S02 非零文字提示與 C15 分支可證，**NAME/E-MAIL 真欄位／必填仍 unknown**。見 [A-030](A-030-native-newuser-disconnect-fields.md)、[整合契約](../04-analysis-integration/A-030-newuser-s02-field-contract.md)。
- 舊表格的 open/not-started 僅是歷史狀態；以最新 `requests.json` integrated/partial/native-not-run 與 [主線同步審查](../04-analysis-integration/roy1-roy2-password-newuser-sync-20261031.md) 為準。


## A-030 E-MAIL/C02 靜態增量（2026-11-01）

[確認 E-MAIL 候選實際封包路徑](A-030-roy1-email-c02-field.md)：原版 C02 opcode 0x02，Region2..4 F4 string8 由第二個額外 UI 控制項寫入（region4 widget0x18／region2、3 widget0x10），packet+0x822→serializer+0x816；確認頁也使用此字串。高可信對應 E-MAIL，但原版 literal label 尚需 `Locale.dat` 或原 Client GUI 驗證；不聲稱郵件必填。Region0/1 另有不含此 F4 的三字串結構。測試工具新增固定原件 x86 路徑驗證；不修改 Server/DB/Asgard.exe。


## 2026-11-01 A-030 原版 Basic.dat 語系資源交叉驗證（取代先前 label unknown）

配對原件 `Basic.dat` 確認 `BasicString.txt` **73 NAME／75 E-MAIL**，`SkinString.txt` 2153 名字／2154 E-Mail；EXE 確認畫面 F3/F4 key0x49/0x4B + C02 writer 原生對應 ⇒ **Region2～4 C02 第3個 string8=NAME、第4個 string8=E-MAIL 正式已證**（不再只是候選）。S02(status!=0,message) 原生 message dialog 建構＋C15(empty)/state1F 分支已證，但原版 GUI/TCP 實際 display 和 retry、錯密 status 官方意義仍未實測。A30 `integrated/resource-confirmed, runtime partial`；見 [原件資源與 EXE cross-reference](A-030-roy1-original-resource-proof-20261101.md) 與 [離線驗證](../tools/a030_resource_labels.py)。

## A-031／roy2：C10 後原始 C25 及 World 入口證據（2026-11-01）

原始 `Asgard.exe` SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145` 完成 BIN-first 靜態追查：C25 opcode0x25 真正的 native class 是 **`CBillingInfoPacket`**（ctor `0x5712E0`，writer `0x571420`，RTTI）；**Region3 寫三個 `string8`**（每欄 u8 byte length + encoded bytes，來源 global `[0x66D100]+0x0C/+0x20C/+0x40E`）。其他 Region 的 writer 不寫 payload，但**四條已追的 C25 原生送包入口全部受 region3 guard**，不能要求非3 Client 一定送 C25。

已定位兩條原始 callback **C10 raw token enqueue → C25 enqueue**（`0x4A8446→0x4A84F3`、`0x52FB8C→0x52FC4B`），兩次送包之間沒有等待額外 S02。不能拿 Client class `CBillingInfoPacket` 的字串當角色/登入憑證，也不能以合成 `C25 body=01` 當真正 World 握手。實際 first S2C、map/S14/C35/GUI 與各非3 Region 完整動態時序仍在 **CT-108 native not-run**。

[A-031 完整報告](../task_a/roy2/A-031-analysis.md) · [native 35 VA + RTTI probe](../task_a/roy2/a031_native_probe.py) · [decoded-body codec](../task_a/roy2/a031_world_entry_codec.py) · [CT-110 / CT-108](../05-conformance/A-031-native-world-entry-test-plan.md)。研究 `integrated/ready` 限於上述原生靜態 Client I/O；**不代表成功進 World**。無新增必需原版檔案；若要 runtime 驗收，需要同 SHA 原始 Client 去敏 S03→C10→C25/first World S2C 封包 trace。


## A-028／roy2 完成後補證：C04 第二段 S02 成功的 UI／World 交接（2026-11-01）

已從原始 `Asgard.exe` SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145` 追查 `state0x1e+S02(0)→0x4B206B`：確認此成功 callback 會**清理 0x0B/0x0C/0x0D/0x07 UI 槽位**，並且只有 **Region3** 在 `0x4B2109` 建立 `0x4A9380` 的 native class。透過 vtable `0x609BBC`→COL `0x625970`→TypeDescriptor `0x6665D8` 明確辨識為 **`LoginDialogPane`**。這是 Client 記憶體內的 UI 物件，**不代表玩家需要手動再次登入**，也不證明 Client 自動送 C03。

獨立的 LoginDialogPane `0x4A8890` callback 可在參數非零時呼叫 C03 sender `0x4A7D10`；**final S02 success 是否自動觸發尚無原生 call/packet 證據**。S02 非零仍回 `C15(empty)`／state0x1f；Region3 state0x1e 的一般文字提示有特殊略過分支。**ADR-008 的產品需求仍是成功創角直接進 World、不需手動重登**，實際自動 World TCP 與首個 C2S/S2C 留給 CT-105/107/108 原版擷包；不以舊版推測的「回 LoginDialog 手動 C03」取代需求。

[A-028 新增完整原件證據](../task_a/roy2/A-028-postcreate-ui-native-followup.md) · [31 VA/RTTI 原生驗證工具](../task_a/roy2/a028_native_postcreate_probe.py) · [合成狀態機](../task_a/roy2/a028_postcreate_model.py) · [CT-111/原生 CT 計畫](../05-conformance/A-028-postcreate-native-callback-test-plan.md) · [22 項合成回歸 GitHub CI](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41226689277)。任務為 **`integrated/partial`**：已完成可證的 UI 靜態交接，但首次創角成功後 World 連線因果未證，**`native_client_validation=not-run`**；沒有新缺的具名遊戲檔案，真正需要原版 Client 去敏的創角最後 S02→World 封包及 UI 時序。

## A-023／roy2 原版 Born、Basic 與 S44 GUI 分派再次補證（2026-11-01）

本輪 **直接讀取使用者提供的原件**：`Born.dat`（zlib native Script、Main、CP950 XML CRC `1d87b0c0`）、`Basic.dat`（39 slots/38 members，完整 indexed DAT）與 `Basic.dat/AlertFrame.ypf`（offset13196、size177648、SHA `b641441d1f0378de04b6f7929c333d95e6ad7df451f3927432e5c4d0305602ce`、YPF v17）。同 SHA `Asgard.exe` 再驗 **22 個原生 S44 dispatch 指令**：`S44(type2/subtype0)` 使用 UI slot0x23＋components3/4，`S44(type2/subtype2)` 使用 slot0x24；**與已證 Born `S44(1,0)→Main` 不同**。新增 21 個 synthetic DAT/index/UTF16/zlib 正負向測試及 `CT-117`。完整 [原件報告](../task_a/roy2/A-023-born-basic-native-dispatch-20261101.md)／[驗收](../05-conformance/A-023-original-born-basic-ui-test-plan.md)。

本次未收到 `PaperDialog.dat` 原始檔，只能引用先前已驗證的相符 hash 與函式；**如要重新獨立比對完整紙張依賴，確切需 `PaperDialog.dat`**。首發 Born 的原服規則、女招募員 EntityId/map/spawn 與 NPC→`nNewJoin01.dat` 綁定依然無原服／Native GUI 證據，A-023 保持 `integrated/partial`、`native_client_validation=not-run`，不是漏做 Client S44 啟動機制。Server 最小入圖/行走 P0 不依賴這個 P1 教學 NPC 與 Script 自動派送。

## A-023／roy2 四份原始 Script 已補上並完成依賴核查（2026-11-01）

**本次已實際取得** `PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat`、`Merchant.dat` 四份原件，各自原始 SHA256、strict zlib＋BEu16 version／BEu32 UTF16 codeunits、CP950 textCRC、所有函式及回覆分支都已核對；不再列為 A-023 缺件。詳細 [BIN-first 資源/對話交接](../task_a/roy2/A-023-four-script-native-dependencies-20261101.md)、[SHA/CRC 版本報告](../task_a/roy2/a023-four-script-verification.json)、[CT-115](../05-conformance/A-023-four-script-verify-test-plan.md)。

已證：Born `PaperDialog_Create` 的原始實體可對上 `PaperDialog.dat`，背景為 `Basic.dat/AlertFrame.ypf`。普通 PaperDialog OK 只關閉（C6C4→未回答 C6C2）；`PaperDialog02` OK `PAPER02=START`／CANCEL `PAPER02=NOT`，但 **`cancelControl="OK"`**，ESC GUI 真結果未驗。`Merchant.Main` 初始化 `ClientReply`，`nNewJoin01`（本身無 Main）`MerchantTalk→JoinMessage01/02/03` 最終回 `STATE=ACCEPT/REFUSE`；回覆是原生 C6C1→Dispose C6C4，不能當任務完成。**C6C1 的 script 名稱取當次 S44 root ScriptRunner，而非 nNewJoin01 依賴資源名稱**。兩種 PaperDialog 有 `PaperDialogProc/ShowIndexedHelp` 同名碰撞，不能無條件混用。

目前缺的 Client 函式定義是 **`QuestDialog_Create`、`MerchantDialog_Create`、`MerchantDirectTalk`**（候選來源檔 `QuestDialog.dat`、`MerchantDialog.dat`，但**尚未證實檔名**），還有真正女招募員 NPC EntityId/map/spawn→Script root/依賴的原服綁定、首次 Born 發送政策與 native UI。A-023 新增 **9 個原件證據 E25～E33、28 synthetic tests／CT-115**；保留 `integrated/partial`、`native_client_validation=not-run`，只因這些真正的外部缺口，不是原件尚未讀。基本 World 進圖/行走 P0 不因 P1 教學 NPC 被卡住。

## A-011／roy2 S07 真正 Monster image 欄位與 C43 三模式補證（2026-11-01）

A-011 已在最新原件 `Asgard.exe` SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145` 追通：**S07 的共通第五欄 BEu16（reader `0x57E456` 寫入 row+0x0C）→ `0x4F1A7F` local 20B visual descriptor → kind1/2/4 `MonsterObject0x4D6FA0` → image factory `0x4D2340` → `MonsterImageLib0x4D7530/0x4D7560`**。已知註冊 image namespace `0x4000..0x41AD` 依 `Monster00..42.dat`、library8000..8042、每檔10 logical slots 對應。S07 tail `variant_u16` row+0x222 另轉 float 存 MonsterObject+0x27C，並非 image ID；u32 scene object-ref 又是另一個命名空間。

UI panel `0x4A2376..0x4A2558` 確定 C43 送 `type1/subtype 0x04/0x10/0x40`（mode0/1/2）、全部用相同 pane object ref；**仍未證原版 NPC 點擊是否使用這些 mode**。完整 [A-011 新研究](../task_a/roy2/A-011-native-s07-visual-id-c43-20261101.md)、[43 VA 原件檢查](../task_a/roy2/a011_s07_native_visual_probe.py)、[23 個 synthetic tests](../task_a/roy2/test_a011_s07_visual_chain.py)、[CT-116](../05-conformance/A-011-s07-visual-source-c43-test-plan.md)。原版獨立 Client GUI CT-083 `not-run`、A-011 `integrated/partial`。

**缺少要進一步對照的具名檔**：本輪未提供實際 `Monster00.dat`／`World00.dat` bytes（或其他任一同版 MonsterNN/WorldNN），Git 已有其歷史五個 YPF member metadata 但不足以映射 logical slot 到 YPF/DOI frame/group。原服 NPC EntityId/spawn、哪個腳本綁到招募員、AI/掉落及實際 mouse→dialogue TCP trace 仍是其他證據缺口。這不影響已證 Client 靜態封包格式開發，也不影響基本 World 地圖/玩家行走 P0。
