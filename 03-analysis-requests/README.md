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

## A-015／roy2 MAP→Tile→碰撞證據→可用座標（2026-10-31）

這次以同一原始 `Asgard.exe`＋`Map0.dat/Map1.dat/Map2.dat` 追到完整 **MAP raw 10B tile → Client memory 17B tile → index=x+y*width**。Native `0x4B4920` 只證合法 tile 邊界，`0x4B4A3B/0x4B4A73` 的 32×48 視窗單元是像素→tile 的**候選**；tile bit0、bit4 線段測試和獨立每格 4B grid 具有不同用途，尚不能自稱原版玩家 walkable map。

原始 494 地圖／7,701,805 tile 重新掃描且 SHA 全部吻合；477 張地圖包含 Born(31,29) ，該格 flags 0:242／1:109／17:126，絕不能當玩家出生點證據。**26 原始 PE signatures PASS、18 synthetic map tests PASS**（[GitHub Actions run 41188097214](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41188097214)）；[完整分析](../task_a/roy2/A-015-map-coordinate-collision.md)、[metadata-only MAP codec](../task_a/roy2/a015_map_coordinate.py)、[26 PE checks](../task_a/roy2/a015_map_native_probe.py)、[CT-087/070](../05-conformance/A-015-map-coordinate-test-plan.md)。資源/地圖解析研究已交付，完整原版 passability / native Client GUI **未驗證**；不需要再提供 Asgard/Map0/1/2/Born，同版真實走路／撞牆 trace 有助於後續結案。


## A-010／roy2：施法、取消、持續效果 Client I/O 原版靜態研究（2026-10-31）

已以原始 `Asgard.exe` SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145` 確認六組 native opcode→class→writer/reader：

|封包|已證 native decoded-body|
|---|---|
|C4D StartCastSpell|BE u16，Client 真實 producer `0x402034..0x402052` 從 `[ebx+0x80E]` 取得 word|
|C56 CastSpell|u8；真正 UI producer 未追完整|
|S52 CastSpell|BE u32,u8|
|S48 CancelCastSpell|BE u32|
|S2C AddLastingSpell（opcode 0x2C）|BE u32,u8,BE u16,u8,string8 encoded-byte length,u8,BE u32,BE u32|
|S2D RemoveLastingSpell（opcode 0x2D）|BE u32|

實際動作分類（單體、AOE、治療、BUFF、召喚）與技能 ID、射程、消耗、冷卻、效果時間、疊加/過期及原生 Client UI callback **未證**。原版 `SkillSpellDialog`／`LastingSpellDialog` 等類別存在不等於某類技能的效果已還原。A-010 交付 `integrated/partial`，**只完成可驗證的 Client I/O 靜態範圍**；Native UI `CT-090` not-run，不把原服公式或完整技能表補猜。

[完整研究](../task_a/roy2/A-010-analysis.md) · [decoded-body codec](../task_a/roy2/a010_skill_codec.py) · [25 原始指令／六 RTTI 驗證](../task_a/roy2/a010_native_probe.py) · [CT-089/090](../05-conformance/A-010-skill-cast-lifecycle-test-plan.md) · [CI 19 項測試成功](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41193941400)。未獲已證名稱的正式技能定義檔：不要憑猜測要求 `Skill*.dat` 或 `Spell*.dat`；此輪無新增必需檔案。
