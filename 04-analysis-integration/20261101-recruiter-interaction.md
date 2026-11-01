# 招募員：原生物件點選到加入對話

> 後續實機回報 NPC 不可見；已確認 S07 建構／登錄，補方向2及 S1A 站立初始化。279項測試與隔離TCP通過，GUI重測中；詳[不可見問題修正](20261101-recruiter-invisible-motion.md)。舊「GUI待驗」不代表已通過。

## 本輪解開的Client路徑

原始EXE SHA沿用`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，
REA/Ghidra12.1.4。以下是靜態路徑，不是原服NPC設定表或GUI驗收。

1. S07 handler0x4F17C0的kind1建立MonsterObject，ctor0x4D6FA0第一個
   option為1，保存至物件+0x284。kind2傳0，kind4傳3；不能把它們混用。
   證據`ev_deb6d724b94d46dc20f39c4addf9650920b00bf3ce8e3ef4e63f9e0645fb8edf`、
   `ev_01f58130c8e7d33878dd109b3c3ec95e07c087224ac0b02d1af193d2ea9baf89`。
2. MapPane滑鼠入口0x4C1030，命中物件後經0x4B9DF0、0x4B72F0與
   accessor0x4D6050。mode1進互動分支；該路徑構建C43(kind1,target,subtype0)。
   target由物件ref accessor0x46E2E0取得，不是硬編碼玩家自身。
   證據`ev_d1bbfd4f5c802d0f919dad035ef31a166b96b137670bb4f7f75cbca52a9b14f0`、
   `ev_6cd265bc41f8650eb7f81499a7af2e4e9fd7bef1f735b0492f9747411fab6b02`、
   `ev_30219daef93e70025920a3175c0bfd65d1f4438d5a4fb7807317a6b0793fceea`。
3. 舊C43(kind1,subtype4)的0x479A20來源為HumanInfoDialog；它不是本輪
   招募互動的必要前置，不能只靠相同opcode誤把資訊頁請求當加入事件。
   證據`ev_19caf8e91107a671cb46b0e9f445dcb1952c313cdea7f81da64a865b87fd08ee`。
4. Sprite建立0x4D2340實際將descriptor首u16送入0x4D7530/0x4D7560，
   接回既有MonsterImageLib除10／餘數對應。這縮小先前S07 image欄未接
   最後讀圖呼叫的缺口，不代表任一圖像就是官方招募員。
   證據`ev_dce3fb08155dcda57c0c1d2c2c778f7f3af870092fc58051a8252f938ae295fb`。

## 素材身份與復原版試驗設定

原件Monster05.dat SHA
`d002581e97450f05dca76fd4964b15886adfe3eb0e75d02ab651864750d419ec`，
索引存在M_05_5_…的helper命名成員，對應候選image0x4037／library8005／slot5。
檔名角色提示是素材線索；原版性別、場景／招募功能綁定仍未證。
既有CPU YPF預覽器不支援該成員所選frame的channel配置，沒有藉此修改素材，
也不把預覽失敗解讀成原件損壞。原生圖像顯示需實機驗證。

獨立Development試驗明示：map6及當前內容revision、位置31/29、wire ref0x1001、
image0x4037、kind1、原始variant5全0、額外word1000。這些綁定與數值為
復原版試驗政策，尤其word單位尚未證；不得冒稱官方NPC實體／出生表。
位置參考Born waypoint，該文字本身不證明NPC原版精確站位。

只在明示承認復原版綁定、map6／移動政策可站立、資源及實際候選Client
目錄校驗通過時啟用。原始EXE/DAT不改，普通測試入口預設不啟用此NPC。
World載圖完成S14(2)之後才送S07，之後才有可選音樂與Born紙張。

## Script啟動與回覆

點擊驗證：WorldReady、當前owner／lease、同map、精確NPC ref及kind1/subtype0，
權威最新位置與NPC切比雪夫距離<=2。距離與ref是Server政策，不是原服常數。
未知／遠端資訊意圖不開對話；重複點擊不重開未結束runner。

S44(1,0)啟動 **Merchant**，隨機非0 context，依賴MerchantDialog、QuestDialog、
nNewJoin01。所有原件Script SHA／文字CRC事先校驗，禁止用錯CRC探測重抓，
不發清快取或素材更新。TILE0省略選用portrait，與地圖sprite ID分開；
MNAME為本地招募員名稱，未實作的金錢／銀行欄位填0只是UI參數，不是資產。

|資源|原始SHA256|嚴格CP950文字CRC|
|---|---|---|
|Merchant|6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350|e9b389cf|
|MerchantDialog|ed194a77a669cbd8f83fbbd01bb08ed0f800b122695cc204a3a12f002f945095|9267d99d|
|QuestDialog|13f068d8053ea7e7b0231357c318bc6effae867888b94305820fe483a17a02dc|d4844b07|
|nNewJoin01|8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae|d9390353|

Merchant原選單點TALK時，C6C(1)先回TYPE=TALK，Client本地隨即呼叫
nNewJoin01的MerchantTalk。Server不再發第二份腳本或重複對話。
加入／拒絕時，同runner回TYPE=TALK與STATE=ACCEPT/REFUSE，接著Dispose；
取消初始選單TYPE=ABORT視為拒絕，不等同教學完成。

驗證issued runner name/context、當前world身份／距離與白名單keys。
相同接受重送冪等；衝突決策、陌生key、過期／未發出的context拒絕。
C6C4/2僅runner生命週期，不能產生接受。新登入與離開世界清除舊context。

## 持久化、驗證及目前邊界

接受後在既有outbox，以character＋事件kind／admission revision唯一保存
`tutorial.admission.accepted`；交易內鎖定精確world lease並要求已提交載圖。
拒絕／關閉不保存加入；重送不重複。無schema遷移。
**這一事件不是tutorial_completed、獎勵、職業或出圖checkpoint。**

私有roy `36c71fd`；275項測試通過。隔離真HTTP/TCP另核對實際資源、
S07、C43、Merchant start、TALK／拒絕／Dispose／重開／接受／重送／Dispose、
移動、位置保存及同Client重登；未啟用NPC的基準流程也通過。

實機待測：是否看到候選NPC，滑鼠能否開原生選單、交談、拒絕後重開及接受。
測試入口停留加入結果屬本增量範圍；後續學校場景、選職與職業城鎮尚未接線。
整體目標仍是完成教學並進入各職業城鎮，不能在此標記完成或關閉目標。
