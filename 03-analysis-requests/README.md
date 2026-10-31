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

## A-027 / roy1：C02 身份與 UI 字段靜態交付

[A-027 逐位址研究](A-027-roy1-identity-ui-security.md) / [安全契約](../04-analysis-integration/A-027-preauth-safety-contract.md) / [合成測試](../tools/a027_pre_auth_contract.py)。新追 UI+0x26C/0x270/0x274 來源、0x4B1A30 的第一欄長度 gate、0x5B4A62 UTF-16 相等比較、region 尾欄。**C02 在 C03 前送出不能證明 pre-provisioned Account owner**，C03(no-character)→原生 MakeInfoDialog 仍 unknown；`A-027 integrated/partial` 僅限可證研究，`implementation_ready=false/native_account_claim_ready=false` 表示原版認領路由必須 fail-closed，不能憑 C02 建帳/建角色/發 S02(status0)。新 CT-039/040 為 planned、非實機通過。

## A-028 / roy1 已完成 C04 後 Client S02/C15 的靜態分析

[完整研究](A-028-roy1-c04-terminal-analysis.md) / [安全規格](../04-analysis-integration/A-028-newuser-terminal-contract.md) / [合成測試工具](../tools/a028_newuser_response.py)。0x4b205f 的 local state0x1e 後，S02 status0 走 `0x4b206b` UI，並非直接 World transfer；status 非0 送 C15 CancelNewUser（0x5715f0、serializer 0x5716a0 無 body）並進0x1f。已獨立核對 status 3/4/17/18/26/31 的焦點分流（不是原服 status 語意）。A-028 `integrated/handoff_status=partial/native_creation_commit_ready=false/native_client_validation=not-run`，原生 owner+角色 durable commit 未證；新增 PKT-C15、CT-041/042，更新 CT-032。

## A-016 / roy1：重送與斷線恢復分析（2026-10-31）

[A-016 BIN-first 報告](A-016-roy1-replay-recovery.md) / [恢復合約](../04-analysis-integration/A-016-idempotency-recovery.md) / [SQLite 合成測試](../tools/a016_recovery_model.py)。確認 Client C33 7-bit sequence/S0B ack、C35 只含 MAP header word+structured checksum（**無 epoch**）、S14 control2 loading callback、C10 one-shot token interface、C04/C15 缺原生 request ID；提供每種操作的內部冪等鍵、提交時點與崩潰恢復矩陣。A-016 `integrated/handoff partial/implementation_ready=true` 限通用 Server 防重/持久化子集；原服 DB/經濟/重連/獎勵政策 unknown，CT-043/044 planned。

## A-017 / roy1 管理 API／觀測與稽核交付（2026-10-31）

[範圍與威脅矩陣](A-017-roy1-admin-audit.md)、[管理 API 契約](../04-analysis-integration/A-017-admin-observability-contract.md)、[機讀操作](../02-server-planning/admin-operations.json) 及 [合成測試](../tools/a017_ops_contract.py)。R-018/R-019/R-021 含帳號建檔、停權 N 天/永久與解封、角色傳送／調整、物品發放、診斷關聯與敏感欄位白名單；所有管理操作與遊戲 C2S 分離，不因 IP/URL 可達就授權。A-017 `integrated / handoff ready` **只對 Server Admin/Telemetry 設計規格**，原版 GM/ban 管理 wire 未確認、Server 未宣稱已實作；CT-045/046 planned，SCN-014 是獨立管理場景。

## A-003 / roy1：創角合法值、UI 欄位與原版十色盤（2026-10-31）

[原件 BIN-first](A-003-roy1-create-legal-values.md)、[Server 安全交接](../04-analysis-integration/A-003-character-create-contract.md)、[五項可執行合成測試](../tools/a003_create_contract.py)。已從原版 Asgard.exe 確認：C02 region 0→3-string8，region2..4→4-string8+u8；region0 的首欄本地 length gate skip，region1..4 的 narrow-byte 長度門檻12；C04=5×u8，hair-color 由 Client index0..9 查 0x66422c 原版十色表後送 RGB。C04 沒有獨立 character name 欄，原 Server 重名、帳號／角色名稱關聯、多角色、sex/hair 合法枚舉與失敗碼仍 unknown。A-003 `integrated/handoff partial` 僅表示靜態子集交付；`implementation_ready=true` 限 codec/10色/安全 Domain，`native_character_creation_ready=false`，A-027 原生 owner 問題仍擋正式建角。CT-047/048 planned、Client E2E not-run。

## A-020 / roy1：Metadata／Script／清單分支（2026-10-31）

[原版 BIN-first 分支研究](A-020-roy1-prelogin-branches.md) / [Server profile 交接](../04-analysis-integration/A-020-prelogin-contract.md) / [合成測試](../tools/a020_prelogin_contract.py)。核對 C0F type3/other、S18 kind0/list vs kind1 compressed、C57 type0/type1、S56 inflated multi-entry、C4B empty、S60 type0 u32/type1 compressed text，A-023 C6C/S44 branch 不重複猜測。原本 S18 body00030000 的原生語意為 kind0、subtype3、count0；local C4B→S60 不等於原 Server 原版必定如此。A-020 `integrated/handoff partial/implementation_ready=true` 限原生 codec 與 fail-closed local subset；region key/真正官方 metadata/Script 時序與錯誤碼待原服證據；CT-049/050 planned，native Client not-run。

## A-025 / roy1：教學首次攻擊、技能與目標事件（2026-10-31）

[完整 BIN-first 報告](A-025-roy1-tutorial-combat.md)、[Server 安全交接](../04-analysis-integration/A-025-tutorial-combat-contract.md)、[14 條原件 byte signatures／7 項測試](../tools/a025_tutorial_combat_model.py)。原 Client C13 Attack BE u32（0x55709C/0x557A5D sender）、C4D StartCastSpell BE u16（0x402034）、C56 CastSpell u8，C3D/S3D Battle subtype0..15（不同多態 payload），S52 CastSpell u32+u8、S5F DieObjects u32 已確證。**Born.dat 只有招募員紙張導引，不含證明必須殺怪/施法的條件；不能推及整個教程不需戰鬥**。A-025 `integrated/handoff partial`，可交 DEV 的是 codec、Server 攻擊/技能權威輸入檢查和 **conditional** quest event unique-ledger 方案；原服戰鬥公式、首 NPC、教學目標必需性 unknown。SCN-012 仍 analysis-required；CT-051～053 planned、native Client not-run。

## A-026 / roy1：教學完成、可能獎勵、出圖與中斷恢復（2026-10-31）

[完整 BIN-first／Born 資源交叉核對](A-026-roy1-tutorial-completion.md)、[Server 安全設計](../04-analysis-integration/A-026-tutorial-completion-contract.md)、[10 項合成測試](../tools/a026_tutorial_completion_model.py)、[機讀完成條件／所有未知欄](../02-server-planning/tutorial-completion-conditions.json)。Born.Main 只有招募員 PaperDialog 導引 (31,29)（**非出口/出生**），C6C4→C6C2 只關 Script；C39 Merchant subtype1..9 有 native 入口，NPC/Script 真實綁定未知；C0B Quit empty 非畢業；S15/S14/C35/S04 支援通用切圖，但沒有原服出口目的地。原版任務完成 rule、獎勵是否存在/內容、官方出口 map/xy、重登政策 unknown。A-026 integrated/handoff partial，可交 DEV 安全 once-only Completion/optional Reward/Exit ledger，**不代表原生教學可通關**。SCN-013 仍 analysis-required，CT-026～028/054～056 planned/not-run。

## A-007 / roy1：完整背包與裝備生命週期（2026-10-31）

[原生 C1C/C1E/C08/C0C/S0F/S37/S10/S38 證據](A-007-roy1-inventory-lifecycle.md)、[Server item instance 領域契約](../04-analysis-integration/A-007-inventory-domain-contract.md)、[離線原件 signature 與 SQLite 測試](../tools/a007_inventory_contract.py)。原 Client C1C `use_kind=1..9` 有多種變長尾部、S0F 數量 mode0/1/2、S37 變長裝備、S10/S38 明確移除 reader；原本衣櫃 type5 僅一個 profile。不以名稱推斷真實交易/數量/裝備槽政策；正式 Server 使用內部 item instance id、owner+slot/revision/quantity、唯一 ledger/outbox 及背包滿回滾。A-007 integrated/partial，原服 item template/合法值/掉落拾取/全 Client E2E 未知；SCN-015、CT-057～059 planned。

## A-019 / roy1：原版地圖與音樂曲目對應（2026-10-31）

[完整 S19 Client BIN-first 與 Map archive 三份原件盤點](A-019-roy1-map-music.md) / [Server 交接](../04-analysis-integration/A-019-map-music-contract.md) / [map→track 官方對照明示空表及原件 SHA](../02-server-planning/map-music-evidence.json) / [10 項離線測試工具](../tools/a019_music_map_probe.py)。S19 kind1 接 u8 repeat+u16BE track（音樂），kind!=1 只接 u16BE sound_id；原版依 `%05d.mp3` 產生音樂檔名。Map0/1/2 索引合計可辨識 494 個 *.map，未索引 Music/*.mp3 或 map→track，但這不是證明整份資源/原 Server 都無對應。**官方每張地圖音樂仍 unknown**，不可把本機測試 track1 或合成 CT-005 track18 充作官方。A-019 integrated/handoff partial，SCN-006 保留 manual-pass-subset，CT-060～062 planned/native Client not-run。

## A-004 / roy1：多人及 NPC 物件可見性

[原版 Client 封包／物件容器／消失深度研究](A-004-roy1-world-visibility.md)、[Server interest/EntityId 契約](../04-analysis-integration/A-004-entity-visibility-contract.md)、[20 BIN signatures 與 18 Python 單元測試](../tools/a004_visibility_model.py)。原生 S07/S33 生成／更新、S0C/S64 移動、S11 方向、S1A 動作、S0E RemoveObjects、**S5F DieObjects（更正舊 PKT-S1E）** 可交接；官方 AOI radius、原服 wire ref 重用及 NPC/Monster 內容綁定仍 unknown。A-004 integrated/handoff partial，原 Client 兩人 E2E 未執行、CT-063..065 planned。


## A-011 與 A-022（roy1，2026-10-31）

[A-011 NPC／怪物原生資源與外觀／動作](A-011-roy1-npc-monster-resources.md)／[交接](../04-analysis-integration/A-011-npc-monster-resource-contract.md)：Client 透過 `Monster%02d.dat` 註冊 43 個檔名 `Monster00.dat`～`Monster42.dat`（resource bank `0x1f40..0x1f6a`），S07 提供外觀候選與 u32 object_ref，S1A motion，C39 Merchant interaction；缺原生資源不能把 bank index 等同 monster template/animation/click。A-011 integrated/partial、CT-066～068 planned。

[A-022 MAP 資源、碰撞-like 旗標、可索引座標](A-022-roy1-map-geometry-collision.md)／[交接](../04-analysis-integration/A-022-map-geometry-contract.md)：Map0/1/2 實際494個命名資源、491個按 header/grid/tile/附加紀錄完整解析；幾何 bounds 不等於真正可行走。Client tile+6 bit0x10 用於某條線段測試，bit0x01 可運行時改動，真原服碰撞／出生政策未知。A-022 原已有 loader/CRC integrated/partial，本次補實際資料；CT-069～071 planned。兩任務原 Client 實機 E2E 均 not-run。
