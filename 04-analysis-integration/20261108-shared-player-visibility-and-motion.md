# 共享地圖玩家互見、外觀與真實移動歷史

後續增量：[已提交戰鬥事件與多人旁觀](20261108-committed-combat-observation.md)現已接上逐次普攻／技能／怪物受擊投遞；本頁結尾「戰鬥待接」為此前743項回歸時的歷史範圍。原生GUI仍待驗收。

日期：2026-11-08。需求來源為使用者已核准的[ADR-007多人共用地圖](../02-server-planning/shared-map-multiplayer-contract.md)及持續完成Server的指示。原件收發格式見[REA遠端玩家生命週期](20261108-native-remote-player-lifecycle.md)。引用分配、快照、歷史容量與重同步策略是Server重建設計，不宣稱原服採相同架構。

## 世界身份與唯讀觀察

同一個配置世界資料庫內，同 mapRef／內容 revision 的當前已提交玩家共用可見場景，不按角色建立私人NPC／怪物。同角色只有當前 account／character／generation／connection 租約能操作；舊連線收尾不能移除新連線。Host須先具備已提交位置及可信移動政策才啟用玩家投影；只做載圖／能力診斷、尚未啟用移動權威的舊流程不因觀察而補建位置。

觀察者必須已提交載圖。由資料庫的真實位置與可信Server地圖設定推導可見矩形，不能由Client提供bounds或來源座標。固定版Client採912×672 MapPane與48×32圖塊：originX=(X−viewportX−1)×48，originY=(Y−viewportY−1)×32；左上以max(0,origin)除圖塊尺寸，右下以min(地圖像素尺寸,origin+Pane尺寸)除圖塊尺寸，右／下邊界exclusive。沒有另縮成聊天半徑8，也不宣稱支援其他解析度。

每個玩家快照包含真實角色記錄、精確租約、位置／版本、衣櫃與獨立衣色、實際穿戴衣服／背包版本、職業及可選能力狀態。所有這些欄位連同已提交載圖來源由同一資料庫讀取快照取得，不能拼成舊位置加新衣服。沒有能力或背包資料就保持未知，觀察本身不建立初始獎勵、不補HP、不改位置或裝備。

來源session必須有匹配租約的committed載圖且沒有pending載圖。先核對同mapRef所有已提交在線角色的revision／map校驗值，發現不同內容即拒絕觀察，不悄悄按revision分出私人場景；因此畫面外的衝突也不能略過。再套可見矩形、排除自己。仍未建立跨Host載圖入口的全域catalog pin，不能宣稱所有不一致都會在進圖前拒絕。

## 物件引用與投影

穩定角色引用沿用隊伍成員引用範圍0x10000000～0x1FFFFFFF，同一角色跨重登／地圖／Host重啟保留。每個接收Client自身仍是local ref1；其他角色的地圖Human引用與該角色在組隊名單中的引用相同。這些wire ID不是角色帳號，也不是可授權物品或PvP的能力。

|狀態變化|Server投遞|
|---|---|
|首次可見／返回可見範圍|S33完整遠端Human外觀與位置，隨後S1A站立；self不另生影子角色|
|不再可見／離線／來源pending切圖|S0E移除，清除該觀察者的已見記錄|
|同角色新租約取代舊租約|先S0E舊實體，再以同穩定ref送S33新實體；不是重用舊連線狀態|
|衣服、獨立衣色、髮型／髮色或職業變更|重建S33；原件對相同remote ref本來就移除重建，不能稱為不重置動畫的原地更新|
|純面向變更且有連續turn歷史|S11，保留位置|
|HP跨過生死邊界|重建最新外觀，死亡用S1A motion3墓碑，復活回motion0；此為他人狀態呈現，不替他人執行復活交易|
|Client C0C報缺失物件|重新查權威可見快照；只有目前有資格看見的真實Human可重送，任意未知ID不能造角色|

衣服優先使用實際背包穿戴：存在背包但已卸裝為0，不能回退穿回舊衣櫃服裝。沒有背包記錄時才使用衣櫃服裝。髮型／RGB保留創角值，衣色使用獨立RGB或原素材sentinel。S05只處理自身，不能用來生成遠端玩家；S33不照搬S05的0x1000衣色控制旗，否則會抑制Human攻擊／死亡動作。

## 移動必須使用實際提交過的路徑

每次成功提交一步或面向位置版本，在同一交易保存From／To完整位置與精確租約。每角色只保留最近32筆，新增 `_player_motion` 類資料，World輔助表總數52→53；已有SQLite角色庫先一致備份一次再建表。位置更新或歷史保存任一失敗就全部回滾。換租約首步重建自己的歷史；觀察不追加歷史。

接收者從自己已見的版本，按連續From／To串接到最新快照。真正走過的方向壓成S64 runs，每byte高4bit方向0～7、低4bit步數1～15，最多11 bytes；起點用已見舊位置，終點用最新權威位置。不能只看兩個端點猜直線，亦不能發Monster用法的S0C假裝Human走路。S06只確認已存在的Human路徑節點，不能拿來啟動走路。

版本缺口、歷史超過保留窗口、超過11 runs或閉環起終點相同，都重同步S33最新位置；不捏造中間路徑。原生S64對start==end走校正分支，會忽略非空閉環，因此不能將整圈塞同一包。正常100ms連續移動即使觀察輪詢250ms錯過中間更新，也能從歷史得到真實多步／轉彎路徑。純turn記錄不編入移動run，最後面向保留。

自身離開遊戲、換圖開始或重生重建自身時，清除本機觀察快取；新地圖正確C35提交後才重新投影其他玩家。在來源pending載圖期間，其他玩家先看見其離開舊圖，不因來源尚未提交目的圖便提前生成。

## 驗證與範圍

多人TCP另暴露SQLite輪詢寫入放大：聊天／隊伍gate對INTEGER主鍵賦同值仍會寫出日誌，造成無遊戲狀態變動的觀察也等待磁碟。SQLite在此Provider預設BEGIN IMMEDIATE，且先驗本人租約，已有交易級writer排除；因此移除SQLite的多餘主鍵重寫，PostgreSQL保留原row lock。不改成deferred，不降低同步／耐久設定。匹配目前Microsoft.Data.Sqlite10.0.14的兩項回歸證實暖機後空隊伍觀察／空聊天取件不改變另一連線的data_version，真實退隊／發送／取件仍提交；連同原有權限、競爭及回滾共28項通過。這是重建Server實作修正，與原遊戲EXE無關。

交易行為已核對固定版本的[SqliteConnection](https://raw.githubusercontent.com/dotnet/efcore/v10.0.14/src/Microsoft.Data.Sqlite.Core/SqliteConnection.cs)與[SqliteTransaction](https://raw.githubusercontent.com/dotnet/efcore/v10.0.14/src/Microsoft.Data.Sqlite.Core/SqliteTransaction.cs)官方來源；[官方交易說明](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/transactions)亦指出deferred升級失敗須重跑整筆交易，不能只移除鎖再假定安全。

完整 .NET 回歸743項已通過，其中本輪共享玩家核心16項、Host wire4項及兩項SQLite空輪詢回歸。Host合成Client覆蓋多步轉彎S64、同ref新租約先移除後生成、衣色與創角髮色分離、生死呈現、組隊ref一致、未知C0C不造角色，以及原生格式NPC對話→pending切圖→正確C35提交後在同圖重新相見。核心另覆蓋界線／角落、讀取無遊戲狀態副作用、舊連線、revision／CRC衝突、引用耗盡回滾、移動歷史回滾與舊庫一次備份。

最終三玩家實際TCP通過8組情境：雙向唯一Human與無self影子、未知C0C／空閒觀察不改位置、S64／S11只改移動者、穿戴與獨立衣色保留髮色、離開視野／返回、南往北邊界重新可見、隊伍與地圖引用一致、EOF後移除且新租約沿穩定ref恢復外觀。使用原本5秒觀察上限，沒有以延長逾時掩蓋延遲；本機46筆移動ACK修前平均0.991秒／最大2.672秒，修後平均0.124秒／最大0.219秒，轉向投影0.422秒、隊伍提示0.297秒。這是同機隔離測試，並非生產負載或所有硬體的延遲保證。

本輪TCP實收80筆S64皆為單步；多步轉彎由Host wire及獨立編解碼向量驗證，不冒稱最終TCP已覆蓋多run。真正網路跨圖與原生GUI仍未執行；上述跨圖是Host合成封包流程測試。

驗證成品不只看Host DLL：只修改Infrastructure時Host hash可能不變。最終Host SHA256為`29937a26cccb12d6f04197613bea4e0ce1dcb45503e3ce4faf43c7681821d4ae`，Infrastructure為`39afc3f8e3b7ffde93a5f9b234100f487313abae85bf8f1ac54cb1e61cb00e55`；8個Server DLL的名稱／SHA256 manifest於執行前後一致，bundle摘要為`802d8fb530a16d5de47df042f46ec4670b4518f43d2c133352370f998a38d14f`。不公開私有程式、DLL或運行日誌。

此增量完成玩家外觀／位置／面向／生死狀態的投影。其他玩家的每次普攻、技能施放、命中數字與特效仍需共用可重放戰鬥呈現事件接線，不能從位置或HP變化猜一次攻擊；PvP、交易、好友／公會、跨世界分流與全地圖怪物內容也不因有遠端Human便完成。原生雙Client GUI、相機裁切、走路插值、染色／墓碑觀感及PostgreSQL負載／併發仍待實測，不把合成TCP當作CT-055原生驗收。
