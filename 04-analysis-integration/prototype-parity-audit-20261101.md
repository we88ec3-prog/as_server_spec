# Python 原型與目前 Server 的差距稽核

2026-11-01。唯讀比較舊 Python 原型與 `as_server_roy@e93c9a1748fbca539106cba5e75458757c8e490d`，規格起點 `c77e908`。本次沒有啟動、測試或修改兩套 Server／DB／Client。這是指定版本的功能與接線快照，不宣稱原型等於原服或新版每項均未實作。

## 判讀基線

**需求來源更正**：本頁的「差距」是把既有使用者需求／回報與目前實作比較；不代表這些功能需求由分析程式產生。登入、創角、入圖、換衣、立即切圖、Web管理、BGM、獨立衣色與人物置中均有使用者來源。S66/C75、wire欄位等屬程式分析；epoch／冪等／資料模型屬Server設計。逐項來源見 [需求歸因](../00-governance/requirement-origin-policy.md) 與機讀待辦的`provenance`。

- **原型**：單人、本地測試用衣櫃與地圖設定。既有紀錄曾實測登入失敗→成功、建角／外觀、map0 入圖移動、兩衣切換與重啟恢復；之後使用者確認立即切圖、位置保存、更衣面向、BGM。置中與獨立衣色有靜態／合成修正，最後畫面驗收仍缺；曾有 tooltip 懸停無回應，修改副本 workaround 的通過不能外推原版穩定性。
- **新版**：SQLite/PostgreSQL、Account/Character 分離、管理身份、停權／憑證版本、世代／epoch、共享場景與診斷更完整。合成 codec、domain 或 API 已實作，與 Host 接上原生操作、實機通過是三種不同狀態。
- Client 身份固定記 SHA／region／seed。原型的隔離設定、跳動畫、tooltip、手動 ID／主選單預覽各屬不同變體；不把修改副本結果移植為未修改 `Asgard.exe` 的通過紀錄。最新 RI-006/007 另見 [現場派工](../03-analysis-requests/dispatch-20261101-preview-crash-and-world-entry.md)。

## 功能對照

|能力|舊原型的實際範圍|新版 e93c9a17 的唯讀狀態|需補的交付|
|---|---|---|---|
|帳號、登入與角色身份|一名稱對一角色；創角可建立本機帳號|Admin 建 Account、共用憑證／停權／版本、C03/S03/C10 已有|沿用新安全模型；**不移植 Client 自行註冊 Account**。正常錯密與創角錯誤需原生可重試 UI。|
|C02/C04 創角|兩段 S02，已測指定外觀與重登；F1 被當成角色／帳號名|Region2～4 的 opt-in 成功 wire 已接 verifier／pending／transaction／E-MAIL；預設關閉，region需明確選定|不再重派「所有 C02 都無條件 Close」的舊工作；剩下實際 region、負向 S02/C15 與原版 E2E。A-030 的 NAME=F3／EMAIL=F4 已證，不重新猜欄位。|
|創角後進世界|歷史路徑回登入再登入|最終 S02 後尚無已證 post-create World grant／callback|依 **ADR-008** 必須自動進世界，不要求玩家人工第二次 C03。原型不滿足新需求。|
|一般登入後真實入圖|曾用 S02→S05→S15→S14(1)→C35→S04/S33/S14(2) 顯示 map0|真 Region3 C25 可解析；無 fixture 時只記 billing 後 Continue，沒有 World S2C；現場 RI-007 已捕捉停在 WorldGranted|接正式原生載入／MapCatalog、合法出生及真 C35。舊順序是特定 profile 的候選證據，不盲套所有入口／region。|
|MAP／C35|資源清單494張；只因 C35 body長度4就繼續，**未核對兩個值**|已有 synthetic loading/checkpoint 與嚴格 expected pair；map6靜態 C35已解，真載入未接通|保留嚴格校驗；一張同版可重現地圖先通過，禁止以所有494張已可玩或關掉 CRC 達成 parity。|
|走路／轉向／重登位置|C33→S0B、C11更新方向，每步保存；有短程及重登案例|codec、seq7 window、入圖 recovery 存在；Host沒有正式 C11/C33 gameplay route|權威移動、碰撞／速度／重播、防跨圖，accepted位置與面向持久化；初次入圖 checkpoint 不能當永久最新位置。|
|時間同步／存活|InWorld每5秒 S66 challenge，接C75兩u32；曾實測往返|分階段600秒表單期限及close journal已有；未找到S66/C75 Host接線|補查原生時序及階段，接有界 challenge／重送處理；5秒是原型政策，不能當原服規則或硬套創角表單。|
|背包／更衣|S0F本機slot衣櫃，C1C或C1E→S37/S33；兩件已測，重啟保存|有 ClothingId 欄位與 S05/S33 writer，但 Host以 ClothingId=0建立自身；未找到實際更衣路由／裝備保存|接已持有且可穿物品／測試衣櫃、權威穿戴與持久化、自他視野。**無限衣櫃≠正式庫存或物品實例**。|
|獨立衣色／外觀|獨立衣色表與S05/S33修正，最後GUI未驗|writer具衣服ID但染色固定ff00ff，沒有獨立衣色模型／更新入口|髮色與衣色各自保存；兩種投影一致；保留sentinel與素材染色層限制。|
|人物置中／更衣面向|S04偏移8/9靜態對齊800×600；更衣保留C11/C33方向，使用者確認面向修正|viewport／facing在fixture／checkpoint；尚無動態更衣與移動接線|驗證目標profile的錨點及八向走停；更衣不可硬重設方向，不為置中改世界座標。|
|在線立即切圖|管理頁選圖與座標，同socket重載；使用者回報通過|有單次World-loading/recovery核心；未找到正式管理傳送或在線重載入口|傳送意圖、loading epoch、C35提交、失敗恢復、AOI離開／加入；保留衣服、面向、最新位置，無需重登。|
|BGM|S19(kind1,repeat0,track)，每圖選曲／停止並保存；使用者確認有聲音|尚未找到S19 writer／Host播放或map音樂管理路由|接已分析S19與版本化曲目政策，切圖與重登生效；自訂曲目明示 designed，原服map→track仍unknown。|
|Web 管理|建角色、外觀／衣櫃／圖座標、切圖／曲目、啟動副本、回報／更正|**WEB-P0頁面已存在**：建帳／查ID／停權／解封／救援重設／audit；沒有同等角色／地圖／衣色／音樂／回報工作台|補受保護的角色查詢／操作API再接頁面；現有開發fixture不是正式GM API。玩家正常改密碼走原生C26，非Web自助重設。|
|啟動／動畫／tooltip|Web可選副本、跳動畫可恢復，保存素材；tooltip延遲曾被接受|新版Server沒有義務重現EXE patch；原版目標不變，RI-006新預覽崩潰另查|分離Client測試launcher與Server功能；原版／修改副本對照、退出／無回應／網路斷開分開記錄，不以patch掩蓋原版CT。|
|玩家原生改密碼|沒有經證原生流程；管理頁僅本地重設|C26三string8 codec／已知未實作分類；沒有正式handler／原生結果|A-029／CT-098/099接共同憑證與版本撤銷；兩套都缺完整原生驗收。|
|多人、NPC／怪物／任務／戰鬥|未實作；衣櫃、地圖物件不代表動態NPC／怪物|共享場景／AI／AOI／獎勵與對話部分domain、native codecs已有；GUI投影、任務／戰鬥完整閉環未通過|依ONB-05/06逐條接線與雙人實測，不要求退回原型單人架構。|
|維運與診斷|metadata trace、Web回報更正、程序退出紀錄；偏本機單人|分階段期限、逐包／close／拒絕／取消去敏journal、停權／audit及雙DB較完整|沿用新版能力；補運作版本／Client變體／操作與trace關聯、Web回報更正與原版批次回歸。容量／備份還原等仍需A-018，兩套都非完整營運驗收。|

## 原型證據如何移交，而非照抄行為

1. **保留候選**：map0曾接受的S2C順序、S0B自身ACK、S0F/C1C/S37/S33更衣、S66/C75時間檢查、S19播放、S04錨點與染色欄位。連回本規格現有 A／PKT／CT，並在目標profile重新驗證。
2. **拒絕帶入的捷徑**：C35僅長度檢查、把任意C25當世界觸發、移動只夾邊界、無限衣櫃當正式物品、Client自建Account、未知封包一律忽略、拿相同名字當owner、World初始化固定objectId=1外推多人。
3. **不要倒退已知研究**：A-031 C25是Region3 billing而非map/auth；A-030 Region2～4 F3/F4已由資源證明；A-032 map6校驗可離線重算。剩餘是原生入口／GUI／動態對照與Server接線，不是重新索取同一批完整EXE/DAT。

## 來源與重現性

此頁整理的來源定位以 [機讀差距表](../02-server-planning/prototype-parity-backlog.json) 的source inventory及hash為準。舊來源為本地 `workspace/anal/server/{local_server,admin_server,world_packets,equipment_packets,world_settings}.py` 和 `workspace/anal/{validation,user-testing,stability-investigation,world-flow,screen-centering,clothing-colors,background-music}.md`；未複製私有程式、原始runtime日誌或素材入Git。

新版唯讀定位：`LoginWireSession` 的C02/C04/C15/C25/C35與缺少的InWorld操作分派、`GamePacketExpectation`、`TwWorldPackets`、`WorldMovementWindow`、`WorldRecoveryStore`、`AdminAccountEndpoints`／`WebAdminUiEndpoints`及`docs/planning/DEV-ENTRY-roy123-20261101.md`。程式名稱只是查核索引；第三方的實作責任由 [公開交付合約](../02-server-planning/prototype-parity-delivery-plan-20261101.md) 定義，不依賴取得私有repo。

新版舊README／status段落有歷史狀態；本次以最新source與末尾增量文件判斷，不將`not-reported`等同未實作。既有測試數字引用的是歷史紀錄，本次沒有重跑它們。
