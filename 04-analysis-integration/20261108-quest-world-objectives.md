# 任務到達區域與NPC互動目標

2026-11-08。延續[一般任務與原子領獎](20261108-town-quests-and-atomic-rewards.md)。使用者要求持續完成Server功能；本輪到達／互動目標、判定政策及第三關內容是**Server重建設計**，不是原件解析出的原服任務規則。既有S44／C6C及C33契約沿用，沒有新增Client完成封包、修改EXE或改Script模板。

## 目標資料與相容性

QuestDefinition新增可選 `Visits`、`Talks`。null時不序列化，因此舊補給／擊殺definition與catalog canonical JSON不變，不借相同revision修改舊規則。

|欄位|內容與限制|
|---|---|
|Visits|1..8項；精確mapRef／mapRevision、MinX／MinY／MaxX／MaxY（含邊界）及AllowTransfers（預設false）|
|區域|每邊最多32格，Min不得大於Max；啟動時驗完整地圖版本、座標範圍及區域內至少一個可走格|
|Talks|1..8項；每項NPC key、mapRef、mapRevision、X、Y，必須與配置NPC精確一致，拒絕重複NPC key|
|Events|角色進度的可選欄位，包含ActivationId與Visit／Talk布林陣列；陣列長度須與definition一致|
|View|新增可選Visits／Talks布林進度，與既有擊殺／交付目標共同決定Ready|

可只設定世界目標，亦可混合擊殺／交付；有世界目標的每次接取都產生全新的ActivationId。放棄清除旗標與本輪ID，重新接取重新累計；已完成不再更新。舊任務無新欄位，也不強迫重寫舊JSON。新增目標應使用新key或有明確進度遷移的新definition revision，禁止同版偷改。

## 到達判定

1. 只有接取後、存活角色的權威事件計入。有效步行必須已在同一交易提交新座標，且X或Y確實改變；原地轉向、讀取進度、站在目標區域接取、重登或載圖不會補進度。
2. 比對完整mapRef／mapRevision及包含邊界的矩形。命中後保存該旗標並增加quest revision；重複進區不重加，也不產生獎勵。
3. 預設只計步行。AllowTransfers=true時，可計已完成C35與轉圖交易的正常來源：NPC、技能、MapGate及教學轉圖；Admin來源永不計入。待載圖、失敗C35與回滾皆不計。
4. 位置、32步移動歷史及任務旗標同交易。進度保存失敗時位置也回滾，不能用Host事後補記造成兩邊不一致。任務僅要求接取後抵達，不證明全程行走的路線。

新功能重用已釘定的active quest definition，不依賴Host現時載入哪份目錄；仍在進行的任務即使暫時從新目錄移除，也可依既有定義接收事件。每角色最多16項active，處理有界；舊無世界目標任務不做逐步definition查詢。

## 互動判定與視窗權限

本輪Talks的具體語意是：**開啟並關閉一次指定城鎮NPC的已授權對話窗**。它不是「原服TYPE=TALK分支已完成」；取消（ABORT後Dispose）也可算本次互動。只點NPC、只送ABORT、未開窗直接偽造關閉都不計。這是明示的重建政策，需特定回覆分支、選項或順序的原服任務仍另待開發。

- 每次實際送出城鎮S44前，在Core建立當前角色唯一的對話權限：租約／連線／generation、非零context、Script名、NPC完整身份、開窗位置、生命代次，及當時已接取且目標吻合的 `(quest key, definition revision, ActivationId)` 清單。
- 不從C6C取可信NPC、座標、進度或獎勵；Host必須確認這是目前已發、仍可點到的NPC視窗。Core重新核對當前租約、已載圖及精確持久位置。正常遠距點選仍沿用使用者指定的可見即可互動規則；若需靠近，可另設Visits目標。
- 有效C6C(4)時，Core驗context／Script／NPC地圖／存活與生命代次，再只更新發窗時捕捉、目前仍為同一ActivationId的active目標。同一NPC可同交易更新多個任務，但不發任何物品、Gold或EXP。
- 旗標與對話Consumed同交易保存。任一處失敗全部回滾，同一有效關閉可安全重試；成功後重播不再更新。重播同一發窗context不重新捕捉任務，因此接取前開的視窗或放棄後重接前的舊視窗不能回填新進度。
- 銀行金額視窗、商店買賣清單每次換context都重新發權限；舊runner的延後Dispose不更新新context。C6C(2)只是清理，不計入進度。
- 開始轉圖、重新載圖或接受新World連線會清除舊對話權限；死亡／復活的生命代次不符亦不計。切圖後再回原地或重登，不能拿舊視窗補互動。

只保存每角色最新一筆對話權限，scope最多16項，不逐點追加無界對話歷史。完成目標仍需回委託NPC重新開窗、按領獎，由原有一次性原子交易結算；Dispose本身從未成為領獎指令。

## 可選第三關

原兩關補給與既有測試入口不變。明確啟用 `TownNpcs:WorldObjectivesEnabled=true` 且QuestsEnabled=true後，五城旅館各追加「重建：認識城鎮」：

- 前置：完成該旅館的第二關藥品交付。
- 目標：接取後走到該城藥水商座標周圍一格的區域；開啟並關閉該藥水商對話。
- 獎勵：回原旅館手動領40Gold及100EXP，無物品交付／獎勵，僅一次。
- 米魯里斯例：旅館90,80→藥水商85,36附近（84..86,35..37）步行→開關對話→回90,80領獎。步行及互動兩項可任意先後，均須在同一輪接取後。

資料依實際城鎮NPC建立，其他四城同政策；這不是已證的原版旅館或新手任務。新入口沿用local-shop-vault帳號、金鑰與DB，只新增獨立world-content-quest-world設定，既有兩關設定檔不被替換。舊進度與舊definition保留，新catalog僅追加第三關。

任務視窗仍用原ServerTownQuest模板／CRC，在TEXT增加區域及互動的0/1狀態；沒有新資源或新opcode。完整文字須通過CP950 string8的最壞情況長度預檢。Script執行與GUI排版仍未實測，不把Host編碼流程當原件畫面驗收。

## 保存、驗證與後續

新增quest_dialogues單表；已有帳號的SQLite在建表前一致性備份，獨立升級tag `.pre-quest-world-events-v1-*`，暖啟動不重複。原四張任務表與JSON進度不重寫。PostgreSQL有等價DDL與交易路徑，實例驗收、還原演練仍另列。

檢查包含區域／NPC邊界、舊JSON省略新欄位、真正步行與原地不算、接取前事件、放棄重接nonce、錯NPC／Script／context／其他角色、存活與重登、正常傳送與Admin排除、位置＋旗標回滾、多任務＋Consumed回滾、備份，以及原生編碼C33→普通NPC／銀行／商店context切換→C6C4→手動領獎→重登。啟動器只在臨時fixture驗證，不啟動使用者Client或Server。

最終950項.NET回歸通過（0失敗／0略過），另3項Python啟動器fixture通過。這些是Domain／Store／Protocol／Host合成測試，本輪未跑真實TCP或原生Simkin／GUI，也未把前輪TCP結果移作本輪驗收。

原生GUI、原服任務條件／名稱／獎勵、完整任務日誌、對話分支及順序、日常重複、計數型多次互動與既有active definition升版遷移仍未完成。這輪補上世界目標，不代表整個任務系統或全部Server已完成。

後續：[重複任務與領獎歷史](20261108-repeat-quests-and-completion-history.md)已新增兩種時程與新輪重設；上方未完成項保留為本報告當輪歷史。
