# 本版 Client 的物品訊息與裝備封包子集

2026-11-08後續：[十六槽裝備增量](20261108-sixteen-slot-equipment.md)已補原生key映射、多槽交易及DAM／AC投影；本頁保留原分析時間點，舊slot2限制不代表目前只開衣服。原版模型與新槽GUI仍未驗收。

2026-11-07。使用者要求將裝備列入開發，並詢問主程式是否已有裝備／道具訊息。本輪沿用 [A-007](../03-analysis-requests/A-007-roy1-inventory-lifecycle.md) 與 [既有原型欄位](items.md)，把可直接交付的封包子集接到新 Server Protocol。私有實作與測試不放入本庫。

## Client 中已知的訊息

Client 有背包、裝備、使用物品及物品說明的類別與封包。S0F/S37 能接收顯示用 icon、RGB、名稱、描述等資料；S0F 的已證子集另有種類、背包格位、使用類型及數量。這表示 Server 可以提供物品資料讓 Client 顯示，**不等於 Client 本地必然有完整原服物品定義表**。

裝備與服裝資產也不是物品實例。S0F/S37 的格位與圖示不能直接作持久 item-instance ID。傷害、防禦、裝備需求、堆疊上限、取得方式與經濟數值仍須有來源，或明示為可調整重建規則。

## 可直接實作的輸入

- C1C 固定頭為 `kind,slot,flag,use_kind` 四個u8。尾長依use-kind：1為string8、2為4B、3為8B、4為6B、5為0B、6為4B、7為2B、8為2B、9為4B。type1使用CP950編碼後的byte長度，拒絕截斷、尾隨及無效字元序列。
- 原型已測衣服意圖為 `01 bag_slot 00 05`。這只授權新 Server 對已持有、可穿的衣裝做判斷，不是任意slot免費產生物品。
- C1E只確定為一個u8。既有原型將它當衣櫃選擇格位；**本輪尚不把它直接命名為卸裝命令**。正式卸裝需另補原生UI producer證據。

## S0F 安全投影子集

固定10B頭為：`u8 kind=1,u8 bag_slot,BE u16 icon,RGB3,u8=0,u8 use_kind=5,u8=0`。
接 `string8 label,string8 name,string8 description`，最後7B為：
`u8=0,u8=0,u8 quantity_mode=0,BE u16 quantity,u8=0,u8 extra_description_count=0`。
本次數量正值1..65535。mode1、mode2及附加描述結構不由這個子集writer發送。

## S37 安全投影子集

固定7B頭為：`u8 equipment_slot,BE u16 icon,RGB3,u8=0`。
接 `string8 name,string8 description`，最後6B為三個零旗標、一個parser跳過的零byte、一個raw false零byte及附加描述數0。
slot2有舊原型衣裝實測；其他裝備槽不能僅依一件衣服推定。顯示空名稱或icon0也不能自行視為「清空裝備」協定。

## 移除 handler 與尚待核對的容器操作

S10 reader已證3個u8，S38 reader已證`slot,raw_flag`兩個u8，且後者轉成本地Boolean的規則恰為`raw_flag==1`。
追加原件指令追查：S10 handler `0x4f2450` 在第三欄為0時，以第一、二欄呼叫 `0x489a30` 查詢目前 UserInventory，再呼叫 `0x489a00`；第三欄為1時則把第二欄送往另一個 inventory 的 `0x538f20`。因此第三欄不可任意一律設為1；第一、二欄也不能互換。

S38 handler `0x4f1220` 在 reader 的 Boolean 為true時由 `0x45d160` 取得格位物件，否則由 `0x45d140` 取得，再呼叫 `0x45efc0`。S37 handler `0x4f3be0` 的 `packet+0x434` Boolean 使用相同兩個格位選擇器，最後呼叫 `0x45ee50`。本版 S37 子集固定raw false，因此其對應的 S38 應選raw0，而不是raw1。這是**兩個 handler 選取同一容器的證據**。

追加 callee 追查：`0x489a00` 在kind1/2時呼叫 `0x538f20`，後者按key查詢、呼叫被移除物件的虛擬解構函式，再呼叫 `0x538a00` 移除樹節點。`0x45efc0` 呼叫 `0x45ef70`，後者查找key的範圍並交給 `0x45ed50` 做range erase、遍歷清除。據此，本子集可發送背包格清除 `S10 = 01 bag_slot 00`，以及與S37相同裝備容器的格清除 `S38 = equipment_slot 00`。其他分支仍保留raw語意；不是任意值都等價。

這些是原件的解構／容器移除行為證據，**不是背包或裝備視窗的實機驗收**。Client 的顯示移除也不等於 Server 持久物品刪除，必須由交易後的權威狀態決定是否投影。衣服轉移到裝備欄應清除原背包格；卸回背包應清除原裝備格並新增背包投影。C1E的UI意圖尚待producer確認，不能因移除投影已證就推定C1E是卸裝。

可在同一SHA原件重現的 VA／十六進位簽章如下（不是伺服器程式碼）：

|位置|簽章|含義|
|---|---|---|
|`0x4f2456`|`8a462684c0756f`|S10第三欄分支|
|`0x4f246f`|`e8bc75f9ff`|S10呼叫UserInventory查詢|
|`0x4f24bd`|`e83e75f9ff`|S10呼叫後續容器操作|
|`0x4f1224`|`837828017519`|S38本地Boolean分支|
|`0x4f1249`|`e8f2bef6ff`|S38 false選格|
|`0x4f1250`|`e86bddf6ff`|S38 false後續操作|
|`0x4f3c97`|`8b8334040000`|S37讀取Boolean欄|
|`0x4f3d0b`|`e83094f6ff`|S37 false選相同格|
|`0x4f3d12`|`e839b1f6ff`|S37裝備資料投影|

資料交易應先提交物品位置、數量與裝備，再投影背包／裝備及S33自身外觀。失敗不先更衣；保留world座標、面向、髮色與獨立衣色。正式資產與開發衣櫃分開。

## 驗證與界線

原始EXE SHA256為`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。本輪重跑既有A-007的15個SHA鎖定原件signature錨點，並核對上表新增9個handler／容器配對錨點，全部通過。

初版隔離Protocol測試106項通過、0失敗；追加移除helper後僅重跑InventoryWireTests類別17項，全部通過。測例涵蓋C1C九種尾長、無效／未知類型、C1E長度、S0F/S37獨立offset向量、CP950 255B邊界、每個截斷位置、尾隨bytes、未支援mode／附加描述拒絕、S10/S38原始值保存與固定清除向量。這是Server codec／合成驗證，**沒有因此把背包、卸裝或物品說明視窗記為原版Client實機通過**。

2026-11-07後續：已由實際C3A斷線與REA補證[裝備欄更新／C1F卸裝](20261107-equipped-click-and-native-takeoff.md)。C1E仍不當作卸裝；新增C1F四u8玩家子集，原生手勢與畫面驗收另列。
