# 裝備能力與S08戰鬥數值投影

2026-11-08，延續A-007／A-008。原件Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，Ghidra12.1.4。僅靜態分析原件及有界讀取同版skin；未改／執行Client，未改私有Server。本輪原生GUI未測。

## 已證欄位，並非從縮寫猜位置

InventoryDialog使用的S08接收入口為48ABA0；它先呼叫53F8A0更新Status singleton，再逐控制項讀欄位及格式化。Ghidra沒有48ABA0 procedure boundary，故以精確指令保存，不修原件或分析函式邊界。

SkinMan537EE0載入Skins/Default.skn，537930從library6/member47讀skin.tbl，5367D0依dialog/control表建UI。Inventory constructor48B630明確註冊dialog4；原件skin.tbl dialog index4名為Inventory，控制項19..24依次名為Ac、Mc、AAR、SAR、DAM、Hit。這份原件表與native控制項id／Status offset的讀取形成交叉證據，不是按遊戲常識猜順序。

下表body offset零起算，**包含開頭BEu16 flags**。適用flag0x40存在、它是第一個payload區塊的S08（現行0078亦同）；其他區塊在full之後，故不改表內offset。

|UI / control|S08 body offset|wire|reader子view offset|完整packet offset|Status offset|原生顯示|
|---|---:|---|---|---|---|---|
|DAM / 23|20..21|BE16，signed顯示|3E|4A|43E|MOVSX word、%d|
|HIT / 24|22..23|BE16，signed顯示|3C|48|440|MOVSX word、%d|
|SAR / 22|24|8bits，signed顯示|69|75|46D|MOVSX byte、%i|
|AAR / 21|25|8bits，signed顯示|68|74|46C|MOVSX byte、%i|
|WEIGHT目前 /31|26..27|BEu16|42|4E|444|MOVZX word、%u/%u第一值|
|WEIGHT最大 /31|28..29|BEu16|44|50|446|MOVZX word、%u/%u第二值|
|AC /19|54|8bits，signed顯示|66|72|46A|MOVSX byte、%i|
|MC /20|55|8bits，signed顯示|67|73|46B|MOVSX byte、%i|

**更正範圍：body20..29不是六個完整戰鬥欄。** 其中兩個u16是負重目前／最大；AC／MC在full block較後的body54／55。reader586D40→Status53F8A0→Inventory48ABA0沒有由STR推算AC等的數學，它們是Server傳入的最終顯示值。

Wire reader本身只讀位元；所列signedness由最終UI的MOVSX與格式字串證實。Server API宜以sbyte保存AC/MC/AAR/SAR、short保存DAM/HIT，再按二補數編碼。可顯示範圍分別-128..127及-32768..32767；負數是否原服允許、AC高低好壞與戰鬥公式仍未知，不由格式化推導。

### RESIST與五能力

Inventory control30名為RESIST，48AE2F以MOVZX byte讀Status442。它來自S08 fullpacket4C，即reader子view40；但586D40在該欄直接寫0，並未消耗wire。**不能把body24或25改名RESIST**，也不能另插一byte破壞60-byte full block。

五能力仍是STR body30、INT31、WIS32、CON33、DEX34，各u8。Inventory controls25..29及StatusDialog5..9直接顯示同一Status總值。因此可在Server原子計算base＋裝備＋buff的有效值後投影；不應把裝備bonus同時累加到永久base又再投影一次。

負重目前>最大時48AE8B使用unsigned比較選色；這證明顯示警示，尚不證原服超重時禁止何種動作。S08 full block仍60bytes，Current起點62、錢包90與本輪新增欄位互不位移。

## 可重現的skin來源

- Skins/Default.skn：67966545bytes，SHA256 `95be44549794b04eb96a926a18bdd6e056691e0e8939dd535e82ffcfab2a469f`。
- member47 skin.tbl：offset67953440、13105bytes，SHA256 `eff367461f76f5a44969dee779c9d491f9b0c943a587df2d815bea0bb14a9ca0`。
- 表version1，依537930讀取的LE欄位長度有界解析，消耗恰好13105bytes，無尾隨。只發布對應控制項精選metadata，不發布完整skin或圖片。
- 格式字串：60795C是%i、5F1C44是%d、5F19A4是%u、606EF8是%u/%u。

## 裝備需求／原版能力來源的界線

本輪未定位一份可證的原服物品能力／需求模板檔。UI schema的Weapon／Armor等名稱不是數值表。衣裝槽2仍是本輪唯一開放裝備槽；skin表存在其他槽位不代表其wire／所有權／裝備限制已完成。

已核MetaDataMan：4CEEA0查Metainfo及HelpString namespace；4CED90按已載入key與index取文字；4CEBC0從物件+10/+14所持blob解析BEu16 row count、string8 keys與文字列，**這不是一個已證的本地物品檔名**。目前不能從HelpString名稱宣稱找到了原版AC／職業需求／等級需求權威表，也不能從圖示或衣服檔號推原版bonus。

本輪可明示重建可配置衣裝模板的STR/HP/AC等bonus與需求，套用Server權威裝備交易後更新有效能力和S08。原服加成、需求、命中／傷害／防禦公式仍unknown。Client只顯示最終值，不能當數值權威。

## 實作及集中驗收建議

1. Slot2換裝／卸裝／交換應以同交易重算有效能力與資源上限；current超出新max時裁切的政策須明示，避免卸裝永久保留bonus。
2. S08在同一投影事件更新上述最終數值；不要將S37外觀或tooltip文字當作能力已生效。
3. 測裝上、卸下、替換、重登後STR／AC／DAM／HIT一致，及戰鬥實際使用同份有效值；超界模板拒絕，非法槽位不扣物品。
4. 原生GUI需確認Inventory及角色能力窗同時正確，並涵蓋負號、負重顏色、滑過tooltip不當機。靜態解析與TCP fixture不等於GUI已通過。

主鏈Evidence：ev_e42c827e77bac120c18a94f6d5d9332b0a8822ed959b4b52cc4a42362dbd1ba8（586D40/53F8A0/540050）；skin loader ev_665137ff85c1f94cc59975d0903340007a8988b5957d6810eaae77fde7573d6b。精確Inventory指令Evidence IDs與UI有界解析結果見JSON／私有raw目錄equipment-stats-native-20261108。
