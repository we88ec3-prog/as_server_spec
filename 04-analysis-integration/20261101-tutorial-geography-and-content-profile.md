# 教學城鎮名稱、WorldMap派送與完整候選內容入口

日期：2026-11-01。使用者目標仍是新角色走完教學並進入所選職業城鎮，
不是設定檔可載入就算完成。本輪不請使用者重測個別中途步驟。

## 已確認的地名，尚未確認的map_ref

SHA已鎖定的`nNewLife01.dat`（7caa5c656c7ab50b9701506e0d137f7fb1550f6eb6fd7ceb1bd0b3e72f169414）
之`LifeMessage02Proc`在生活講義內列出以下對應：

|職業|腳本中的城鎮名稱|
|---|---|
|戰士|路爾斯城|
|聖職者|米魯里斯城|
|魔法師|斯歐米城|
|盜賊|雅柏城|
|武道家|瑪賽城|

這能支持職業／城鎮名稱，沒有提供map_ref、出生點或原服傳送設定。
不能僅依數字順序宣稱1001／3001分別是哪座城市。

後續[全目錄腳本掃描](20261101-town-script-geography-followup.md)補出首都／森林／
湖泊／海岸／冰原描述與傳送點回覆界線，保留包裝有效但文字異常及XML失敗。
這些是候選城鎮交叉核對條件，尚未升級任何map_ref綁定。

## 原件REA新增線索

EXE SHA db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145，
Ghidra12.1.4；精選指令及各函式evidence ID見[機讀證據](tutorial-geography-dispatch-20261101.json)。

`FUN_00564e20`先經`FUN_004b4850`取得MapData物件+4的map_ref，將AX零擴充至EBP。
它以六位數格式建立metadata key，透過`FUN_004ceea0`查詢`WorldMap`區段，
再由`FUN_00564ad0`切分返回字串並轉數字。第一值為真時，傳原map_ref至
`FUN_005645f0`，組出`%s\\world\\%05d.html`；否則走內建圖像分支。
所以World目錄有沒有某個HTML，不足以排除該圖有內建城鎮圖，也不能把缺檔
當作該城市不存在。尚缺原服WorldMap metadata，不能補出官方派送表。

這也不要與raw MAP header+4混淆：getter讀的是已載入MapData物件中的欄位。
Metadata收發另見[A-020](A-020-prelogin-contract.md)；此處沒有新增未驗證的S18資料。

本地World HTML含`town_pins.py`定位／本地化修改註記；與使用者提供的7z中
對應HTML逐byte一致，表示此修改亦已存在於提供的壓縮檔。不能把「壓縮檔也
一樣」誤當作未修改的官方原件證明。目視圖02001／04001／00001分別標有
路爾斯／斯歐米／米魯里斯，僅當本地歷史參考線索，仍需原生場景核對。

## 復原版候選內容入口

Private Server開發工具現在可額外讀一份明示JSON內容profile；不改正常啟動
預設，也不改使用者當前Server。設定只允許AdditionalMaps、入學目的圖、
CareerAdvisor、Lessons、TrainingCombat及Teleporter。不能透過這個入口
覆寫管理金鑰、資料庫、帳號、監聽位置或原始招募員設定。

Profile需schema_version1、非空profile_id、binding_origin明確為
`reconstruction-candidate`，禁止重複JSON key及超過128KiB；轉成Host設定後，
仍須通過現有Development、map/member SHA、腳本CRC、素材及站立位置驗證。
會話摘要保存profile ID、來源類別與檔案SHA，便於日後重現同一輪。

目前供內部視覺核對的候選路線如下；**沒有升級為原版綁定**：

|用途|候選map_ref|候選出生點|來源狀態|
|---|---|---|---|
|教學學校|7|30,34|復原版設計，原版學校未定|
|聖職者目的圖|1|62,92|本地城鎮圖有名稱線索，原生待驗|
|盜賊目的圖|1001|99,100|僅候選，尚無本批原件地名配對|
|戰士目的圖|2001|100,100|本地城鎮圖有名稱線索，原生待驗|
|武道家目的圖|3001|105,98|僅候選，尚無本批原件地名配對|
|魔法師目的圖|4001|100,100|本地城鎮圖有名稱線索，原生待驗|

出生點設計為離圖中心最近的完整可站立5×5區域，依距離、Y、X穩定排序；
不是原版spawn。學校四位NPC、練習目標放在該區域相鄰格，使用既有helper
候選外觀。三份MAP庫SHA與各member身份固定，完整Host reader再驗checksum。
畢業條件沿現有Life／War對話關閉及實際正傷害practice三項，屬明示復原政策，
不是由原版講義推定的必經任務。

## 本輪驗證與接續

後續[五職業完整TCP路線](20261101-tutorial-route-tcp-evidence.md)已驗真實內容下
全流程與重登；下列啟動-only限制屬本篇初版時點，地理身份與原生GUI仍未定。

以真實六張MAP、所有對話腳本／helper素材、全套候選設定啟動獨立Host成功，
使用獨立SQLite及隨機loopback埠，確認seed0 greeting後停止。沒有改動執行中
的使用者Server或DB。這證明設定接線與素材驗證能整體載入；**沒有證明**
Client已從創角一路完成教學、目的城鎮身份正確、職業數字投影或怪物動作。

接續使用此獨立內容profile跑完整TCP流程及原生GUI，核對學校可行走／NPC、
攻擊、選職、出圖與重登；再依真實地形與可核對地標修正候選城鎮身份。
如候選不符，修改設計綁定並保留版本差異，不將啟動成功充當使用者驗收。
