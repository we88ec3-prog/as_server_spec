# 地面丟棄／拾取與物件重同步

2026-11-08。延續A-007未解欄位，本輪沿同版不可變EXE的UI producer、ItemObject及S07／S0E補證。原件SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。未修改Client／素材／Host，尚未完成本輪GUI驗收。

## C08 Drop的三個byte已追到來源

DraggedItemCell `0x447290` 查目前背包entry+0x612數量；大於1時建立數量對話，否則以1呼叫 `0x4471c0`。後者建立 `CDropPacket`（constructor571f40），寫kind=`489a90(displaySlot)`、slot=`489ab0(displaySlot)`、quantity=數量回調第一參數。writer571ff0依序寫三個u8。

因此一般背包最小body為 **`u8 kind=1, u8 bagSlot, u8 quantity`**。不是Drop action旗標，也不是三個座標。數量wire上限255；Client可顯示u16堆疊不等於單次C08可帶u16數量。Server須拒絕0／超過持有數量／無權限來源，並以權威目前角色位置決定落地點；Client沒有提供drop XY或持久物品ID。

這是丟棄意圖，原生sender沒有在送出後自行扣背包權威數量。Server提交背包與地面物品原子轉移後，剩餘正值以S0F同格數量覆寫、整格消失以S10清除，再向合法觀察者投影地面S07；取消／拒絕不創造地面物品。

## 真正拾取是C07 Get，不是C0C PutRequest

ItemObject `0x496880` 建立CGetPacket，constructor **`0x5728e0→0x578600(7)`**，把ItemObject+0x20的object ref寫packet+0x24再送出。writer `0x572990` 原件bytes為 `8b411850e8a782eeffc3`，即從serializer subobject+0x18取u32並交已審BEu32 helper45ac40。Ghidra未將此10B列為procedure；本輪保留REA精確byte match證據，不假稱已有該procedure完整偽碼。

**C07 body恰為BEu32 ground object ref**，沒有XY、數量或Client指定bag slot。MapPane `0x4bf370` 在互動角色與目標格位 `abs(dx)<2 && abs(dy)<2` 時呼叫496880；這支持本輪Server的同圖／已投影／鄰近一格拾取子集，仍須Server驗當前生命、容量、堆疊相容與claim原子性。此ref只指當前地面投影，不是永久item instance ID。

C0C producer **`0x46d230`** 先經 **`0x4edae0`** 的missing-object節流紀錄（GetTickCount），再發CPutRequestPacket的BEu32 ref。S0C／S64／S1A等handler在收到未知ref時會呼叫它；因此 **C0C是要求重同步缺失物件的入口，不是拾取授權**。回覆可依當前合法可見物件重新投影，已被拾走／過期的ref不能因此復生、扣背包或再次發獎勵。

已追拾取sender未建立一個必須收到專用成功ACK才能解鎖的交易狀態；本輪以權威S0F及S0E同步結果。這不等於已證原服從不發其他提示／拒絕封包，不能自行猜成功碼。原生sender送出時播放本地音效，也不代表Server已提交。

## S07 kind3確實建立地面ItemObject

最小body為BEu16 count；每列 **`BEu16 x, BEu16 y, u8 kind=3, BEu32 objectRef, BEu16 icon, 5×u8 tail, string8 name`**。string8以CP950編碼後byte長度計，不是字元數。

kind3 reader分支 `0x57e538..0x57e57c` 依序把五個u8存local row+0x11、+0x10、+0x12、+0x13、+0x14，再讀名稱至+0x16。handler `0x4f19cf..0x4f19f4` 對0x8000..0xbfff selector呼叫ItemObject constructor496540，取第一個tail至object+0x230、第二個至+0x22e；另外三個未在本輪最小投影鏈賦予用途。**最小安全投影傳五個0，不能任意把其中一個當ground quantity。** Server可在名稱明示數量，真正stack由Server保存。

針對全0是否使圖示染黑的窄核對：**4967b0的完整ground draw不讀+22e或+230，也不以它們設定RGB／alpha**。它使用固定繪圖模式與固定0xffff8001參數，依+22c的icon及像素座標直接繪ditem frame；沒有Merchant LAYER→223c0的染色路徑。因此不能將先前Merchant的O=0黑染結論套到kind3 tail，亦沒有因此把tail改255的依據。兩欄在其他路徑的完整用途仍unknown，此結論只限定實際ground圖片繪製；原生GUI可見性仍須驗收。

kind1／2／4進MonsterObject類分支，不能用目前怪物／NPC的row冒充ground item。kind5..12雖有不同reader短分支，不因constructor共通fallback就視為合法物品替代。kind3及其尾欄初始化是本輪已證子集。

S0E body=BEu32 ref，dispatch `0x4f1da0→0x4ba0c0`，後者清物件選取集合並經4b9ce0移除該ItemObject及registry。拾取成功用S0E移除地面投影，不用S5F怪物屍體流程。Server轉移完成後才移除，不能用Client消失視覺當持久claim成功。

### 同ref重新下發與Name更新

S07 handler4f17c0在kind!=14分支（包含本輪kind3）建立新物件之前，先無條件呼叫 **4ba090(ref)**。該helper以4eac30查目前registry，存在時經4b9ce0移除舊物件，然後返回繼續496540建立新ItemObject及4b6450註冊。因此同ref S07是**先刪舊投影再建立新投影**，不是插入第二個同key物件，也不是忽略更新。

名稱隨kind3 string8解碼至row+16後交496540，再進共用46e1d0建構流程；重投影使用新名稱，不是對舊物件字串緩衝直接覆寫。C0C重同步或原地數量名稱刷新可重送完整kind3 S07，不必額外先送S0E來防duplicate。但這仍會重建物件及相關本地狀態，不應每次輪詢無條件反覆送出；滑鼠選取／音效等實機副作用另測。

此安全性只描述Client同ref替換。Server仍須先確認該ref在當前map／life／visibility有效：已被領取、過期或淘汰的舊ref不能因重同步重建權威資產；也不能用同ref替換機制掩蓋跨實體ref重用與過期請求。

## 地面圖示是另一個索引，不能直接沿用背包圖示

ItemObject hit-test／bounds `0x4965f0` 使用Icon library2/member1 item.tw.ypf的object=`icon-0x8000`；但實際ground draw **`0x4967b0`** 使用library2/member0 **ditem.tw.ypf、object0、physical frame=`icon-0x8000`**。這與Merchant／背包圖示的member1多object結構不同。

原件Icon.dat SHA256 `b80cfdd28b4331bf4012210756bf46196c37d43de1240d70df3cb6480e920dee`；ditem member0 offset292、612470 bytes、SHA `716aeec66fc4102d5690e07781b079c93f0229943bc43b2ea439891403f1eeb9`。它只有 **1object、388physical frames**，metadata恰好到data base12424。原件有些frame超過名義header45×40，離線解析改採128×128有界尺寸檢查，仍逐channel驗界線，未修改來源。

|既有bag selector候選|ground frame|原件結果|
|---|---:|---|
|0x8079|121|存在，離線目視為頭盔，不能稱原版泳裝落地圖|
|0x80f2|242|存在，離線目視為短柄槌，不能稱原版禮服落地圖|
|0x8244|580|超過388，沒有該ground frame|
|0x824a|586|超過388，沒有該ground frame|

因此GroundVisualId必須與bag IconId分離，並核對所選ground frame及同selector hit-test object的合法bounds。原服物品→ground／bag雙索引對照仍未知。依使用者授權已生成388frames聯絡表供挑選明示重建外觀；圖像與解碼工具只留本地分析區，公開僅metadata及來源SHA。不能拿不存在的frame580／586啟用藥水ground投影。

本輪選定下列**Server重建視覺綁定**；不是原版物品對應。兩種服裝共用generic白布，以Server名稱區分：

|重建物品|GroundVisualId／frame|離線觀察|與member1同索引hittest的opaque像素交集|
|---|---|---|---:|
|HP藥水|0x8019／25|紅色瓶|85|
|MP藥水|0x8017／23|藍色瓶|61|
|海灘服／禮服|0x80d7／215|白色布片／短衣輪廓|69|

三者的ground及hit-test primary channel都非空且channel span有效，按原bounds定位後有正像素交集；這只證有可點區域，不代表hit-test輪廓與ground完全一致。member1同索引圖像分別是其他物件外觀，不應拿來替換原來bag IconId。

拒絕的禮服候選：frame42雖非空並有131像素交集，放大更像頭盔／護頸，未採為服裝。frame34雖ground非空，但member1 object34是空frame、bounds全0、flags12、alpha0，沒有hittest交集，因此不適合可點ground。它們不列已選source frame。

## Server權威與待測

落地／拾取、背包拆合堆疊、容量、ground唯一claim、map／位置／lease與兩個玩家競爭須同交易處理。原生沒有唯一操作ID，重播相同C08仍可能是下一次合法丟棄；須以實例版本、情境與lease做去重，不能永久以三bytes當唯一鍵。重登、過期清理、保護時間、所有者限制及消失時間是重建政策，不是Client推得的原服規則。

待集中GUI：拖地數量輸入、丟一件／整疊、合法ground外觀、點地面拾取、鄰近／過遠、滿背包／部分合併、失敗保留地面及資產、多人單一claim、移出視野重入及重登。C0C重同步不得當成拾取。本輪靜態、離線預覽及未來TCP測試與原生GUI分列。
