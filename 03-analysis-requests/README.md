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

## A-024：NPC/怪物 Client I/O 已證子集（2026-10-31）

原版 `Asgard.exe` SHA `db3df616...`：C13 Attack (`BE u32`)、C43 ObjectInfoRequest (`u8,BE u32,u8`)，S07 DrawObjects、S0C MoveObject、S64 MovePath、S5F DieObjects、S0E RemoveObjects 的 native ctor/reader；[A-024 分析](../task_a/roy2/A-024-analysis.md)、[7 項合成測試](../task_a/roy2/test_a024_npc_codec.py)。正式 Client I/O 矩陣的 `FLOW-GAMEPLAY` 已補收發欄位，但 **C43≠已證女招募員點擊**、S07 物件非空完整 row/原版 UI/封包操作還不完整；A-024 `integrated/partial`, CT-021/022/034 planned，Native E2E not-run。Server AI/重生規則由 DEV 設計，不是 Client A 完成條件。

## A-004／roy2：原始 Client 多人視野／移動／移除（2026-10-31）

以原版 `Asgard.exe` SHA256 `db3df616...` 的 RTTI、vtable 與 native reader，確認 **S33 PutHuman** 起首 BE u16 x/y、u8 facing、BE u32 actor 欄，**S06 MoveHumanAck** BE u32,u16,u16，**S11 ChangeDirection** BE u32,u8，**S0E RemoveObjects** BE u32，**S0B MoveAck** BE u16,u16,u8 **不含第三方 actor ID**。C33/C11 是 Client 移動／轉向送出方向；S33（玩家）與 S07（其他圖上物件）的資料路徑不可混淆。

5 種 S2C native opcode constructor + 5 reader sequence 以實際 PE 及 SHA 鎖定 probe 全部 PASS；9 個合成 CP950/欄位長度/選配 flags/epoch/重送測試 PASS，**不是** native 兩 Client E2E。已更新 [A-004 分析報告](../task_a/roy2/A-004-analysis.md)、[機讀 locator](../task_a/roy2/A-004-native-locators.json)、[CT-060/CT-055](../05-conformance/A-004-visibility-test-plan.md)、SCN-005 與 FLOW-VISIBILITY。

目前未追通完整原生 MapPane/ObjectRegistry callback、跨包 u32 ID 的實際 key 查找和 Native UI 的離視野效果。Server 可按 map_instance/epoch/id 做權威可見集合和斷線 fencing（**designed**），但原服 AOI 範圍、重用規則不得聲稱已證。`A-004.status=integrated`, `handoff_status=partial`, `native_client_validation=not-run`。

## A-005／roy2 角色移動、地圖旗標與校正研究（2026-10-31）

原始 `Asgard.exe`：C33（0x573BF0）連續寫 3×u8、C11（0x571960）寫 1×u8、S0B（0x583150）讀 BE u16 x/y + u8。S0B 是**自己的位置／序號回覆**，沒有第三方 actor ID，其他玩家應使用 A-004 的 S06/S11。C33 不含絕對座標、地圖 ID 或 timestamp；原服速度 tick、拒絕失敗的 bit7/UI 重試規則並未全證。

原始三份 Map DAT 494 張／**7,701,805** 個 tile 的 `LE u32 flags` 只出現 0、1、16、17、512。`0x4B3520` 以每格 10B 原始 tile 轉成 17B native tile，`+6` u32 flags 原樣複製；`0x4B4BB0` 使用 bit4(0x10) 做線段遮擋測試，`0x4B2CA0` 動態設/清 bit0，`0x4D1206` 另一處用 bit0。**這些位元 consumer 不足以證明玩家走路唯一碰撞位元。** 不得直接以 `flags & 0x10` 決定移動通行；Server 的行走碰撞、最大速度、重送/epoch 保護必須明標 **designed**。

來源 [A-005 報告](../task_a/roy2/A-005-analysis.md)、[完整旗標統計](../task_a/roy2/A-005-corpus-flags.json)、[原始 PE 驗證](../task_a/roy2/a005_native_probe.py)、[10 項 synthetic test](../task_a/roy2/test_a005_move.py)、[CT-056/057](../05-conformance/A-005-movement-test-plan.md)。`A-005 integrated/partial; native Client not-run`；已知 Client I/O 子集可交 Server DEV，仍需進一步原生 MapPane 失敗校正／實際角色碰撞 handler 驗證。


## A-006／roy2 原版 S05/S33 flags 補證與置中驗收（2026-10-31）

原始 `Asgard.exe` SHA `db3df616...` 以實際 binary VA 核對 13 組 native instruction patterns；`S05` `0x5895A0` 先 BE u32，按 flags 低 byte `bit0`（額外 RGB3）、`bit4`（額外 BE u16）、`bit1`（額外 u8）、`bit7`（額外 u8）條件讀取。**29B S05 僅能用於已知本版 `flags=0/0x1000`**；不適用全部 flags。自身 `S05` 髮色 RGB +10..12、衣色 +25..27 是兩個獨立值。

`S33` 原生 parser `0x585570` 已確認前段 BE u16 x/y、u8 facing、BE u32 object；flags=0 的 CP950 string8 名稱與髮色 +15..17、衣色 +30..32；`0x585667` bit0 額外 RGB、`0x58568B` bit4 額外 u16、`0x5856A4` bit1 額外 byte、`0x5856B4` bit7 額外 byte、`0x585719` bit13 額外 string8。**`42+CP950-name-bytes` 僅 flags=0 profile**。另在 `0x585780..0x5857F4` 有三色全零→FF00FF 的原生 sentinel 正規化分支，但不能據此推論所有黑色顏色禁用或 YPF 完整染色層行為。

已知 profile viewport `(8,9)` 在 48×32、pane(-56,-36) 計算錨點 `(400,300)`，`(9,9)` 則 `(448,300)`；**此為畫面座標投影/既有公式，非原生截圖完成證據**。13 組原件 PE checks 與 10 項合成測試 PASS；CT-058 offline subset 已驗，CT-059 原生 8 向動作／髮衣獨立染色／換裝／切圖／重登**未執行**。參見 [A-006 原生 Client 報告](../task_a/roy2/A-006-analysis.md) 與 [驗收腳本](../05-conformance/A-006-appearance-test-plan.md)。A-006 `integrated / ready` 是 Client I/O **靜態交付完成**，不代表 renderer/YPF/DOI/native GUI fully validated。


## A-009／roy2 原版攻擊與戰鬥效果（2026-10-31）

已直接核對原始 `Asgard.exe`：`C13`（BE u32 攻擊請求）與兩條 native send producer；`S13`（14B 基礎效果資料、flags0x01 另加 17B、flags0x08/0x10 為原欄位拆分）；`S5F`（BE u32 死亡事件）；`C3D/S3D`（subtype0..15 多態戰鬥封包）。已證的 S3D 短格式可用安全 decoded-body codec，複雜 string/vector subtype 仍須 Native reader/UI 深查。

**16 原件 PE 指令檢查 + 5 RTTI PASS；15 synthetic tests PASS**，不是原生 Client GUI 戰鬥驗收。完整詳見 [A-009 原生報告](../task_a/roy2/A-009-analysis.md)、[CT-063/064 計畫](../05-conformance/A-009-combat-test-plan.md)；`A-009 integrated/partial` 代表核心攻擊/效果/死亡 wire 可供 DEV 實作，尚未證明 hit/crit/死亡/復活公式或所有 S3D subtype。原服 Server 權威政策由 DEV 決定；`native_client_validation=not-run`。本輪不需追加原始素材檔。


## A-024／roy2：NPC／怪物原生 S2C 生成、移動、資訊、動作、死亡與移除已完成靜態交付（2026-10-31）

已依原始 `Asgard.exe` 的 ctor/reader 與 jump-table 補齊 **S07 非空 type1..14 全部 wire row 分支**、S0C/S64 物件移動，以及額外資訊/互動狀態封包 **S34 subtype6/11、S3C、S62、S63、S29**，並區分 S5F 死亡事件與 S0E 物件真正移除；Human 的 S33/S06/S11 不混用於一般物件。**靜態 Client I/O 研究 ready** 只代表可解碼上述封包，不代表已知道每種 type 是哪一種 NPC/怪物、官方 spawn、sprite/動畫或原版 Server AI。

[完整 A-024 報告](../task_a/roy2/A-024-analysis.md)；[收包 decoded-body 工具](../task_a/roy2/a024_object_packets.py)；[離線原件證據](../task_a/roy2/a024_object_native_probe.py)；[CT-065/066 規範](../05-conformance/A-024-object-lifecycle-test-plan.md)。已對原始 SHA 鎖定 EXE 驗證 **20 native pattern＋14 switch entries＋六 RTTI PASS**；[CI run 41185085803](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41185085803) 的 **19 新增＋7 既有 NPC 測試 PASS**。A-024 `integrated/ready`（限靜態 Client S2C），`native_client_validation=not-run`，原生畫面及教程內容仍由後續 DEV/CT 驗證。此次無新增必要資源檔案。


## A-011／roy2：NPC／怪物資源 ID、點擊封包、外觀與動畫 Client 靜態研究（2026-10-31）

原始 Asgard.exe 的 World 註冊庫 **7000..7023**（`World00..23.dat`）、Monster 註冊庫 **8000..8042**（`Monster00..42.dat`）及 MonsterImageLib image ID `0x4000+N` → `8000+N//10` / `slot=N%10`，已有原生 binary 證據。注意字串內雖有 `@Monster%02d.dat`，**註冊實際跳過字面 @**。World S07 kind 1/2/4 原生 handler 會呼叫 `MonsterObject` ctor；兩個 C43 request producer 原生寫 `u8=1, BE u32 object, u8=4`。MonsterObject 的六種 selector 對應 `+0x20/+0x30/+0x40`（各重複一次），不能據此擅自命名具體動作動畫。

[完整 A-011 研究](../task_a/roy2/A-011-analysis.md) · [原件 probe](../task_a/roy2/a011_native_probe.py) · [資源 ID/click codec](../task_a/roy2/a011_resource_codec.py) · [CT-067/CT-068 計畫](../05-conformance/A-011-npc-resource-click-animation-test-plan.md)。29 個 original PE anchors + 4 RTTI + 3 UTF16 檔名 literal PASS；[GitHub CI](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41186221751) **16/16 tests PASS**。**`integrated/partial`（已證靜態子集；完整 NPC 物件貼圖/YPF/DOI 原生 GUI mapping 未完成）**、native Client CT-068 `not-run`。精確需補的範例檔名：`Monster00.dat` 與 `World00.dat`（僅為格式模板的實際樣本，非宣稱原檔必然存在）。


## A-015／roy2 MAP→Tile→碰撞證據→可用座標（2026-10-31）

這次以同一原始 `Asgard.exe`＋`Map0.dat/Map1.dat/Map2.dat` 追到完整 **MAP raw 10B tile → Client memory 17B tile → index=x+y*width**。Native `0x4B4920` 只證合法 tile 邊界，`0x4B4A3B/0x4B4A73` 的 32×48 視窗單元是像素→tile 的**候選**；tile bit0、bit4 線段測試和獨立每格 4B grid 具有不同用途，尚不能自稱原版玩家 walkable map。

原始 494 地圖／7,701,805 tile 重新掃描且 SHA 全部吻合；477 張地圖包含 Born(31,29) ，該格 flags 0:242／1:109／17:126，絕不能當玩家出生點證據。**26 原始 PE signatures PASS、18 synthetic map tests PASS**（[GitHub Actions run 41188097214](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41188097214)）；[完整分析](../task_a/roy2/A-015-map-coordinate-collision.md)、[metadata-only MAP codec](../task_a/roy2/a015_map_coordinate.py)、[26 PE checks](../task_a/roy2/a015_map_native_probe.py)、[CT-069/070](../05-conformance/A-015-map-coordinate-test-plan.md)。資源/地圖解析研究已交付，完整原版 passability / native Client GUI **未驗證**；不需要再提供 Asgard/Map0/1/2/Born，同版真實走路／撞牆 trace 有助於後續結案。
