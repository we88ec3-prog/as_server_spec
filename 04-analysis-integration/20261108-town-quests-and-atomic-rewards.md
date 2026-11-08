# 一般城鎮任務、進度與原子領獎

後續增量：[到達區域與NPC互動目標](20261108-quest-world-objectives.md)已補上Server權威世界事件與可選第三關；本文保留第一版兩關的交付範圍，原服規則與原生GUI仍未知。

2026-11-08。使用者要求持續完成Server功能、新手流程暫緩，以及分析與規劃公開、程式私有。本輪開發一般任務引擎與城鎮可測內容，不改新手流程。下列任務內容、數量、獎勵與政策為**Server重建設計**，不是原件解析出的原服需求。

原件對話、S44／C6C與自訂視窗邊界見[原生任務對話分析](20261108-native-town-quest-dialog.md)。原件Quest04是固定「擊退波特」文案，不能改稱摩斯任務；本輪也未證明原版任務日誌opcode。原生Simkin執行／GUI仍待驗收。

## 可測內容與啟用方式

任務預設關閉，需 `TownNpcs:QuestsEnabled=true` 與 `AcknowledgeServerAuthoredQuestScript=true`；同時須有已核城鎮NPC、地圖與角色物品目錄。明確的開發測試入口沿用原商店／銀行環境的帳號、金鑰、角色與DB，只新增任務用世界設定副本，不修改原設定或重產身份。此開關只用於測試，不能視作原生GUI通過。

五城各有兩個獨立的一次性補給任務：

|NPC key／城鎮|座標|共同第一關|共同第二關|
|---|---|---|---|
|miles.inn／米魯里斯|90,80|交2瓶重建生命藥水，領80Gold、50EXP、1瓶魔力藥水|完成第一關後交3瓶魔力藥水，領120Gold、100EXP、2瓶生命藥水|
|suomi.inn／斯歐米|150,76|同上，該NPC獨立進度|同上|
|luars.inn／路爾斯|86,78|同上|同上|
|dark.inn／魔界村|68,111|同上|同上|
|pirate.inn／海賊村|116,113|同上|同上|

沿用既有重建NPC位置／外觀，**沒有證明原服這些旅館提供上述任務**；亦不代表旅館住宿服務已完成。沒有自動給交付物品，可到已接線的藥水商店購買。每角色每任務最多完成一次，沒有日重置或跨城共享進度。

預設目錄依實際載入城鎮定義計算revision，支援單城或五城子集；任務definition各自釘定key／revision／完整內容。可提供有界絕對JSON配置路徑，替換成自行設計的任務；不可在相同revision偷改獎勵或NPC位置。

## 公開資料與行為契約

- QuestCatalog：revision、1..64個definition。Definition包括key／revision、名稱／說明、Giver、等級、單一前置任務、0..8擊殺目標、0..8交付目標、0..8物品獎勵、EXP及Gold。擊殺／交付至少一項，拒絕重複selector、重複物品、缺前置及循環依賴。
- Giver：既有NPC key、mapRef、完整mapRevision、X／Y，必須與配置NPC精確一致。Core操作綁當前角色租約、已完成載圖及精確持久位置；Host另須驗該NPC仍在已發可點選視野、目前對話及腳本context。原生C6C不提供可信NPC／租約／位置欄位，不能直接信任key。
- KillObjective：mapRef、mapRevision、spawnKey、數量1..1000。來源是Server持久戰鬥紀錄中該角色`after_hp=0`的致命事件；普攻及技能共用既有權威擊殺紀錄，沒有Client「我殺了幾隻」入口。**只計最後擊殺者，不計旁觀者或隊友助攻**，不等同原服組隊任務政策。
- Delivery：definition ID／revision與數量1..1000，來源限角色背包；銀行、裝備、地面及交易保管不計。獎勵只接受活動物品目錄已有的definition、正數數量，Gold／EXP各0..1000000，單次物品種類最多8項。
- State：characterId、quest key、definitionRevision、questRevision、Active、Completed、KillBaselines、接受／完成UTC時間。一次性狀態為未接→進行→完成；進行可放棄回未接。最多同時16個進行中任務，包含從目前目錄移除但仍保留的舊進度，不因配置刪除繞過上限。
- View：State、各目標進度、Eligible、Ready。等級／前置／存活決定Eligible；Active且所有目標完成才Ready。閱讀不接任務、不發獎。完成後不能再次接受或領獎。

接取時在角色鎖下記錄各精確擊殺selector的現有總數作baseline；進度為目前總數−baseline，上限目標數量。因此接取前／放棄前的擊殺不可重用，同時間戳的擊殺也不靠時間大小猜先後。斷線及重登不重設baseline。擊殺journal目前必須保留；若計數低於baseline，拒絕而不默默補進度，將來清理前須先加入權威checkpoint遷移。

交付物品可在接任務前取得，採領獎時實際持有數量；非獨立「拾取過」計數，也不鎖住物品。存入銀行或用掉藥水會降低可交付數量，取出後可恢復Ready。

## 原子交易與稽核

領獎的同一交易：

1. 驗當前租約／載圖、目錄與definition原文、已發任務／預期revision、當前精確位置及存活，重新查前置與目標。
2. 規劃從背包依slot順序扣交付，再把物品獎勵堆疊或放入空格。交付完全用掉的格可立即容納獎勵；只扣部分堆疊而仍無空格時整筆拒絕。
3. 同時預檢錢包與成長容量。空間不足、Gold上限、EXP／能力容量或成長revision不符，皆不扣交付、不標完成、不發部分獎勵。資源改變僅可能來自既有升級政策，非任務任意補滿。
4. 保存物品、錢包、成長與完成標記，以及唯一operation receipt。任一保存失敗，全部回滾。inventory revision以整次交付領獎+1，物品instance與版本保持合法；銀行／裝備不被搬動。
5. 收據保存rewardEventId、物品Before／After變化、GoldGranted／ExperienceGranted，連接新物品取得來源及成長收據。成功重播回原結果，不能再次發獎；同operation ID不同意圖拒絕。拒絕不釘死operation，清出空間後可重試。

Accept／Claim／Abandon皆有角色與quest revision屏障；已完成標記是最終唯一性屏障，即使換operation ID也不再領。放棄不扣物品、不退款或發獎；重新接取時建立新baseline。Host每次視窗只有一個可執行的意圖，重複回覆與已關context只清理，不把Dispose當領獎。

## Client收發與新視窗

使用全新名稱 `ServerTownQuest_20261108_v1`，不覆寫Born／Merchant等原件，也不使用cache-delete selector。Server先發S44(1,1)資源更新，再發S44(1,0)含非零context、精確CP950文字CRC、零Script依賴與有界參數。資源更新是**zlib(CP950 XML原字串)**，不是磁碟UTF16 `.dat`容器。

嚴格限制自訂命名空間，拒絕路徑、原件名、NUL、超過16Ki字元／32KiB編碼／16KiB壓縮；Host僅發嵌入的固定模板。Client若缺資源C6C(0,name)，只允許當輪已發名稱、仍開啟的任務context及最多兩次補發；沒有檔案讀取／任意下載API。新檔會進入Client自訂Script快取，EXE與原有腳本不變。

參數為TITLE／TEXT／MNAME／QUESTKEY、CAN_ACCEPT／CAN_CLAIM／CAN_ABANDON及按鈕標籤。文字只從參數顯示，不作程式執行。配置需通過最壞進度文字CP950 string8預檢；過長或無法編碼的模板不得啟動。第一輪UI採短文案，實際排版及換行仍待GUI。

C6C(1)必須只有三個pair：`TYPE=TOWNQUEST`、精確已發`QUESTKEY`、`ACTION=ACCEPT|CLAIM|ABANDON|CANCEL`。只允許已發按鈕；Client偽造完成／獎勵／CAN無效。C6C(4)及no-reply C6C(2)僅處理關閉。取消不改任務，成功領獎發背包更新、S08與既有S0A通知；不立即在舊runner仍Dispose時強開下一個視窗，再點同NPC看新進度。每NPC先顯示進行中或下一個未完成任務，全部完成則只顯示完成文字與取消。

## 保存與驗收範圍

新增四表：quest_catalogs、quest_definitions、quests、quest_ops；SQLite新增前以一致性備份保護有帳號的既有DB，獨立升級tag為`.pre-town-quests-v1-*`，成功後暖啟動不重複。PostgreSQL共用交易與DDL，實際等價／備份還原仍另驗。既有任務definition升版不會自動抹除進度，缺明確遷移時拒絕。

自動驗證覆蓋前置／循環、物品定義、接取／放棄／重登、實際Server致命事件的baseline、他人擊殺隔離、交付與領獎、滿背包／滿錢包／死亡／成長容量、收據／任務／成長寫入故障回滾、競爭領獎、舊租約／位置／revision、備份、C6C視窗上下文與重播、S44壓縮形狀及原件名拒絕。啟動器測試只用臨時fixture，不啟動或修改使用者Client／Server。

最終928項.NET回歸全數通過（0失敗／0略過），另2項Python啟動器fixture通過。這不包含本輪真實TCP／Simkin／GUI驗收；不借用前輪TCP結果替新視窗背書。Excel保留原有人工實測，新增任務仍標待測。

待驗收：明確開啟開關→旅館開窗→取消→再開接取→買足藥水→領獎→第二關→重登確認完成／物品／Gold／EXP；若視窗無法開、文字裁切或按鈕異常，保留Client與Server，先查Simkin／資源處理。新手流程、原服Quest04規則／怪物綁定、任務日誌、移動／對話目標、日常重複與完整原服任務內容仍未完成；不可將本輪重建引擎等同全部任務恢復。
