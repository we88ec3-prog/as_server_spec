# 教學戰鬥啟動設定與TCP場景更新

日期：2026-11-01。接續[共享血量與攻擊結算](20261101-training-combat-authority.md)。

## 來源與交付界線

使用者要求先完成創角、教學、選職及進入職業城鎮，再集中實機測試。
本篇是復原Server的設定與傳輸設計，不是從原件推導出的原服排程。
原件封包依據沿用前篇；250ms更新間隔、內容開關與界限都是設計選擇。

啟動流程現在會讀取combat profile，經場景內容容器傳至每條TCP會話；
配置有效且角色已完成該版入學接受、載入正確地圖後，才提供訓練場景。
預設仍關閉，不把未確認的地圖自動命名為原版學校或職業城鎮。
現有啟動器與使用者執行中的Server不會因此自動變更。

## 設定契約

設定前綴為`Asgard:World:NativeMapTrial:TrainingCombat:`，環境須為Development。
未啟用時不需要其他欄位；啟用後必須明示以下內容，缺漏即拒絕啟動。

|欄位|契約|
|---|---|
|Enabled|true才啟用|
|AcknowledgeReconstructionPolicy|必須true，承認是復原版內容／戰鬥規則|
|MapRef、MapRevision|精確對應已驗證地圖目錄；不接受fallback或錯revision|
|ClientDirectory|絕對路徑；驗證helper使用的Monster05、Portrait、Script庫SHA，沿用既有素材鎖|
|DamagePerHit|1..10000，Client不提供傷害值|
|MinimumAttackIntervalMs|100..5000，持久成功命中時間控制冷卻|
|RespawnDelayMs|1000..600000|
|Monsters|1..32個明示目標，依SpawnKey排序後產生內容revision|

每個目標欄位為SpawnKey、ReferenceBase、X、Y、Facing、ImageId、MaximumHp。
SpawnKey非空、最長48字且無控制字元；同圖key及base各自唯一。
ReferenceBase為十進位uint，範圍0x20000000..0x3fff0000且低16位為0；
生命編號佔低16位，完整wire ref由Server配置。X/Y必須可站立、Facing0..7、
MaximumHp1..100000。本輪Host僅允許已鎖定helper候選ImageId0x4037，
不能用任意怪物圖號繞過素材驗證。helper作攻擊目標的kind2及動畫仍待GUI。

policy revision為上述內容、入學revision與行為版本的SHA256；順序不同不應
造成同一內容產生不同revision。既有共享地圖內容不符仍拒絕，不因重啟清HP。

傳送師RequiredMilestones的某一項可指定`TrainingCombat: true`，解析為該
已配置profile的固定`practice-attack-resolved`及policy revision。不得同時
覆寫Key／Revision或混用Lesson selector；沒有配置戰鬥producer就拒絕啟動。
這項條件是明示復原設計，不能宣稱原版教學必須攻擊／擊殺此helper。

## 連線排程與順序

只有WorldReady、InWorld且位於訓練圖的連線會在等Client輸入時每250ms
檢查共享場景。每次檢查仍驗證owner及入學條件；錯owner／位置衝突會關閉。
死亡／重生投影沿既有S5F與S0E→S07→S1A，不以重複生成充當更新。

同一連線只有一個未完成socket read。計時檢查與HandleAsync共用串行迴圈，
ordinal配置與socket寫入也在同一迴圈，不同時修改會話或交錯寫AA frame。
若等待期間收到資料，先完成正在進行的projection，再處理該資料；下一次
讀取前必須觀察／結束上一次read。無輸入時仍能收到共享死亡與到期重生。

背景更新不呼叫accepted-input計時器，不能延長idle或absolute deadline。
partial AA frame亦不續期；外層既有連線期限涵蓋poll、DB與寫入。
EOF、deadline取消、poll／publish失敗或projection要求關閉時，取消並觀察
該次owned read，才交回既有離線／pending world清理。

這不是完整多人玩家動畫廣播：自身視覺ref1不會作為其他玩家的全球identity。
沒有額外發送猜測HP／傷害數字，也沒有新增掉落、經驗或怪物反擊。

## 驗證與尚待事項

350項Server測試通過。新增真實loopback TCP測試涵蓋靜默Client先收projection、輸入分段後繼續讀取、
projection關閉、poll／publish例外、父token取消、EOF，以及清理後再次讀取
不被孤立read搶走。另驗啟動時錯revision、未確認內容、越界座標、保留ref、
重複identity、未驗證圖號與不合法戰鬥值被拒絕。

這些證據驗證傳輸及設定，不證明原始Client已玩完教學。尚待完整啟動器內容
綁定、學校與各城鎮確認、數字職業投影、攻擊／死亡GUI及完整流程實測。
