# Server聊天拒收與原生黑名單邊界

2026-11-08。延續[普通聊天契約](20261108-world-chat-routing-and-delivery.md)。使用者要求持續完成Server功能；本輪持久化名單、容量、指令與投遞政策為**Server重建設計**。不是使用者指定原服黑名單數值，也不宣稱好友、公會或Client選項頁已完成。

## 原件補證

原EXE SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。REA／Ghidra12.1.4，靜態唯讀，沒有啟動或附掛Client。Evidence `ev_60edda16e06fb99a5f9936a430f47fc69509714c9b2b86adeb3fa6b895d62635`，procedure `0x42fe00`，analysis profile `3c06738e45e144d5f073edbd3244c6bff46222f389525fe659bc92dca2ccdece`。

S0A type0且相關option允許時，ChatInput receiver取第一個`>`之前的姓名，逐一用case-insensitive寬字串比較本機20格名單（base+0x14c8，每格0x200 bytes）。命中時建立C19，Kind=1，target為命中姓名，text空字串，送出後不追加該訊息。此分支證明**被動拒收通知**；它沒有新增／解除旗標，也沒有完整列表或名單revision。不能用它推導Server同步名單。

S0A type18走plain history，繞過type0姓名名單分支，沿用[前輪補證](20261108-native-chat-and-whisper.md)。因此當Server使用type18承載聊天時，須自行決定Server拒收。原生20格與本輪100格是不同名單，**不自動匯入／覆寫／同步**。Client本機名單的編輯、持久格式及同步協定本輪未追完；不能把Server指令宣稱為原版選項頁。

## 可操作入口

原生普通聊天C0E(kind0)的文字分流新增明示Server命令，大小寫不敏感：

|命令|結果|
|---|---|
|`/ignore add 角色名`|拒收該既存角色的聊天；允許對方離線，不能指定自己|
|`/ignore remove 角色名`|解除拒收；不恢復封鎖期間或封鎖前已被清除的訊息|
|`/ignore list`|只對本人顯示第1頁|
|`/ignore list 2`|每頁10人、頁數1..10；超出目前頁數明確提示|

命令不當作普通聊天廣播，不佔原聊天成功發話額度；kind2技能／普攻文字不進此分流。操作結果用S0A17短提示，列表用S0A18 history，無新opcode／Script／EXE修改。列表只含角色名、總數與頁碼，不展示對方位置或在線狀態。

C19 kind1仍僅辨識為通知並忽略；不廣播其text、不建立或解除Server名單。未知C19 kind也不授權修改。名單不是帳號封鎖、禁言或遊戲邀請封鎖。

## 身份、容量與持久化

每角色最多100人。目標輸入需非空、無空白／控制字元、CP950可編碼且最多24bytes；以與角色姓名查找相同的NFKC＋InvariantUpper查既存角色，保存不可變character ID。列表顯示權威現名。帳號名稱不能代替角色名稱；未實作改名功能，不以文字相似判斷同一人。

本人必須持有當前完整World租約且已提交載圖；舊連線、冒用account、pending載圖不能查改。讀取只限本人，修改帶expected revision；成功實際增刪加1，既有加入／不存在項解除為NoChange不加版。revision耗盡拒絕，不能繞回。

名單、revision、已排訊息清除及操作回執同交易。相同operation ID及相同正規化目標／新增解除／expected revision在2分鐘內重播回原結果，不再套用；同ID不同意圖拒絕。每角色最多128筆活回執，不逐出舊回執，達上限回RateLimited（包括暫時不能解除），到期後可重試。原生命令本身無operation ID，由Host每次生成，不宣稱可辨識有意重複輸入的字串。2分鐘後無跨期同ID保證。

名單本身無到期，跨離線／重新登入／Server重啟保留。不改道具、Gold、EXP、資源或隊伍會員；沒有名單的舊角色保持原聊天行為。

## 發送與接收

|頻道|政策|
|---|---|
|附近／隊伍|依每位接收者名單排除其封鎖的發話者；其他有資格者和本人回音照常|
|密語|任一方封鎖另一方都不建立新投遞，回與離線／不可接收相同的TargetUnavailable，不透露誰封鎖誰|
|系統／服務／戰鬥提示|不經使用者聊天名單，不會把系統通知一起封鎖|

附近／隊伍為單向「我不收他」：我封鎖他後，自己附近／隊伍發話仍可由他收到，除非他也封鎖我。密語雙向停止是另明示政策，非原件推導。既有隊伍範圍、附近8格、2分鐘保留與限流不變。

提交發話時先排除拒收者，再查所有實際收件人的容量。因此被排除者佇列已滿不阻擋其他人。成功RecipientCount只計真實排入者；自己的回音不因自己名單消失。密語拒絕不增加成功發話額度，也不發假成功回音。

新增封鎖時在同一聊天gate清除本人所有尚未取出的該來源訊息，涵蓋附近／隊伍／密語。解除封鎖不重播。取件仍重新檢查名單；不符合者刪除而不顯示。發話和封鎖競爭的線性化點為同一交易鎖：先送則後續封鎖刪queue，先封鎖則送件不入queue。已取出並提交、尚未寫到TCP的訊息無撤回能力；不承諾封鎖按下後絕無一則在途訊息。

鎖序沿用本人租約→party gate→chat gate，不取得對方租約鎖。操作前清理過期／舊租約聊天queue，當前精確連線最多256筆，封鎖掃描有界。既有at-most-once dequeue、失敗寫TCP可能漏顯的邊界不變。

## 升級與驗證

新增ignore state、entries及operation receipts三表，owner／target FK與owner!=target檢查。已有帳號的SQLite建表前一致備份，獨立升級tag `.pre-chat-ignore-v1-*`，暖啟動不重複。舊角色、聊天、隊伍、帳號、金鑰與既有進度不重寫。PostgreSQL有等價DDL／gate路徑；實例與完整還原本輪未驗收。

完整975項.NET回歸通過（0失敗／0略過），含15項新增Store／Host測試。範圍：定向Store／Host原生格式合成測試，包含三頻道隔離、雙向密語拒絕、離線目標、重登／租約、容量與回執上限、重送、競爭、pending載圖、滿佇列排除、清queue／state／receipt故障回滾、單次備份、C0E指令私有列表及C19kind1不修改。

三個獨立合成Client的真實TCP六組情境通過：私人命令與附近排除、組隊排除但不退隊、兩方向密語泛稱拒收、私人列表及kind1不改名單、新World租約保存，以及自己Host重啟保存／解除後恢復且無舊訊息重播。測試Host DLL SHA256 `999829b866bd090a2eb0e3ceb711690e56daf4d75eaddd1481d4820a27819c3d`。只重啟自建隔離Host，沒有動使用者環境。

原生GUI／Client輸入、多Client畫面及PostgreSQL實例仍待測。不把原生20格本機名單與Server100格當同一系統。好友新增／狀態、公會、邀請拒絕、郵件與交易封鎖政策、名單營運匯出仍待後續開發。

後續：[Server好友名單與查詢式在線狀態](20261108-friends-and-query-presence.md)已接替代命令；原生好友視窗／同步仍未宣稱完成。
