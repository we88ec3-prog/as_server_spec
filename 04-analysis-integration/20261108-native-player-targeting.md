# 原生玩家指定目標與治療入口

2026-11-08，延續A-010指定目標缺口。原始Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，Ghidra12.1.4。僅靜態讀原件；未操作使用者Client/Server，原生GUI未測。

## 可實作結論

**已證的mode2／CastValue0可用Human作物件目標，並非只接受Monster。** S62的Field2設0時，不會進入額外的傷害型玩家／ALT限制分支。可用既有C65六byte body `u8 kind,u8 slot,BEu32 targetRef`開發指定存活隊友／自身治療，不需要新增opcode、開啟PvP或改Client。

這僅證明Client能選物件與送意圖。原服治療技能名稱、消耗、治療公式、哪些職業可用及同隊權限仍未知。Server需自己權威驗證投影ref、角色歸屬／生命世代、距離／視線、存活、隊伍、資源與冷卻。Client沒有替Server保證只能選隊友。

## 哪個S62欄位控制玩家限制

|層|精確位置|
|---|---|
|S62 wire固定前綴|Kind:u8, Slot:u8, Icon:BEu16, Field0:u8, UseFlags:u8, **Field2:u8**|
|reader579020|Field2→reader子view+1E|
|完整packet view|+2A|
|handler4F2CD0|fullpacket+2A作4017D0參數5|
|ActionEntry constructor4017D0|參數5→entry+9|
|使用入口46D970|只有entry+9==1才檢查額外玩家分支|

所以Field2是body offset6（零起算）的byte，不是CastValue、Field3或圖示kind。Field0=2（wire body offset4）才是entry+7的指定物件模式；UseFlags（body offset5）轉入entry+8，不可互換。射程entry+80A仍由reader常數100轉入，沒有因此多出可設定的wire range。

46D970額外拒絕條件的完整有界表達式：

```text
entry[9] == 1
&& selectedActor.IsKindOf(0x66E3F0)       // Human token
&& HumanObject[0x2AD] != 1              // getter47A520
&& (MapState[0x550] & 1) == 0           // getter45FBD0
&& singleton(0x66D0C8)[0x7C] == 0
```

拒絕後顯示BasicString477，其同版文字明示「對他人施展傷害的魔法」須按ALT再點對象。這支持它是傷害型玩家操作限制；本輪不將三個狀態值完整命名成PK／善惡／Alt鍵狀態，亦不宣稱Field2=1就是治療可選玩家。Field2=0直接跳過這一整段，不影響後面的距離／格子阻擋檢查。

Basic.dat SHA `0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`，BasicString.txt slot2 offset190844、14810bytes，SHA `fa92f7a3cf544ff9e141d98620943b362e2d3dcc6e327878a818ebaa6ac3123b`。這是key477，不能拿文字檔行號當key。

## 真正滑鼠選取Human的路徑

1. 4BEE70處理mode2物件選取，呼叫4BD530(screenX,screenY,result,6)。
2. 6=bit2 Human＋bit4 Monster。4BD530建立4BCAF0 visitor，4ED670遍歷registry繪製／拾取集合。
3. visitor callback4BDC50用IsKindOf token66E3F0／9200E8分Human／Monster，經控制項／物件bounds hit test收集候選；4BDE20最終選Human時返回類型2、Monster返回類型4。
4. 4B8BE0把真實ref存MapPane+0xC8；46D970以4EAC30從通用registry取物件。它沒有只dynamic_cast成Monster的前提。
5. 46D970取target/self座標，檢查兩軸距離與4B4BB0（經過格tile byte+6 bit0x10阻擋），將target物件ref填入CUseAction。
6. 577AA0的mode2 writer只送kind、slot、BEu32 ref；401ED0在CastValue0路徑先送C0E文字前導再送原C65。前導不含target，不應獨立結算治療。

Human token並非只靠名字猜：Human constructor47C1D0建立MI class vtable，479E90原始leaf bytes `B8 F0 E3 66 00 C3`回傳66E3F0；4A6700→5130C0沿type parent鏈比較該token。

## 自身、隊友與死者的界線

- **自身**：46D970明確比較selectedActor與UserObject+0xC；相同時使用heading8，不轉向其他格，仍安排同一use packet。自格也經4B4BB0，格子阻擋未被特判跳過。這是自身作target的直接原件分支；能點到角色圖像仍受一般hit-test呈現。
- **隊友**：上述producer沒有隊伍成員查詢。它可以選已呈現Human，但不自動限定同隊；「只治自己及存活同隊」應明示Server重建政策。
- **其他玩家**：Field2=0 producer沒有另外按敵我分流，因此必須Server拒絕不允許的對象，不能以UI可選代表權限合法。
- **死者**：46D970沒有讀HP或死亡欄位；但不能由此保證所有死亡形態可選。Human拾取virtual+50→479FD0在appearance flags bit2且附加byte bit2未設時拒絕hit；此條件尚未完整命名，不等同已證死亡。401ED0另外對mode2 target呼叫4BA410：若特定registry map(+124)包含ref，會走4BA310移除／清理並提前返回，未進送包。這些本地狀態與死亡動畫／已移除墓碑關係未完成全鏈。本輪治療應只允許Server存活者，復活另開契約。
- **施法者自身受限狀態**：401ED0檢查本地Human flags0x1000並拒絕；4BEE70也有施法者flags0x2000與pending狀態限制。不能因target gate通過就稱任何動作中都可施法。

## 精選證據與驗收

|Evidence|內容|
|---|---|
|ev_07d38f67d4f29686682de6fbf93c7157774b9ad9bb995b2519f2af9ccd310567|46D970＋579020／4F2CD0／4017D0，Field2鏈及自體分支|
|ev_30542abfc76c3162fc9a22c03cb02050bd57fad79ff136f20983c539505193ef|玩家gate helpers及本地target mode|
|ev_d94ca396835c122aa3e3a8ca24bbe92497dc428fca4aaa8c17d66f3e46a13ae0|MapPane點選、Human生成／registry路徑|
|ev_b5eaf879df3c372ca92237f53aa1b65ceb5755d819256faeffee184f84d0e767|4BDC50原指令補足反編譯遺失register的Human判斷|
|ev_cc99f5017130a3bdf85319ab7152f53ef2da60eedf69491f625f188c7fe733ed|mode2 writer、CastValue0與視線路徑|

原始多函式Evidence／精確leaf指令及同版字串精選在私有workspace/anal-roy-temp/targeted-healing-native-20261108。公開JSON保留更多Evidence IDs。

待GUI集中確認：同場景兩個已投影玩家，施法者MP足額，非滿血隊友第一次滑鼠指定便收到C65真ref與實際補血；自身點選、快捷列再選人；越界／非隊友／死亡／已離線ref不扣費且不斷線；目標移出AOI後拒絕，重新可見再可用。每次新按鍵產生的新治療不可被內容hash吞掉。網路fixture通過與原生GUI通過分開記錄。
