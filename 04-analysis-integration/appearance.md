# 外觀profile欄位與螢幕座標

2026-11-08武器／盾牌／頭部接線見[裝備Human外觀](20261108-equipped-human-visuals.md)，以下舊增量保留當時範圍，後續進度以該文件及進度表為準。

職業欄位新增證據與行為契約見[原生職業投影](20261101-native-career-appearance-projection.md)。

2026-11-01開發增量：使用者要求「衣色獨立於髮色」。新 Server 已加入可選 clothing tint 的 S05/S33 編碼；未指定時維持原始色 sentinel，指定時僅改衣色及 S05 的0x1000旗標。拒絕把000000／FF00FF當可精確顯示的自訂色。4個新增測例核對髮色不變、面向／位置保留、S05與S33各自旗標及保留色拒絕；全套279項測試通過。此增量尚未接持久化、衣櫃／裝備交易與Web操作，不能宣稱新Server已可完整換衣染色；原生GUI仍待測。

body offset不含opcode／ordinal／frame header。此處只規範原型已實作的選填欄子集，不能套用任意flags。

## S05 body，29 bytes，本profile flags=0或0x1000

|offset|型別|語意|
|---|---|---|
|0|u32 BE|object_id|
|4|u8|sex|
|5|u8|HumanInfo職業code；未選0，戰士1、盜賊2、魔法師3、聖職者4、武道家5|
|6|u8|未知，本profile0|
|7|u16 BE|clothing_id|
|9|u8|hair_id|
|10..12|RGB3|hair_color|
|13|u8|武器模型編號，0無；已核註冊上限109|
|14..16|RGB3|附件RGB，目前ffffff|
|17|u8|盾牌模型編號，0無；已核註冊上限13|
|18..20|RGB3|附件RGB，目前ffffff|
|21..24|u32 BE|flags；自訂衣色設0x1000|
|25..27|RGB3|clothing_color；原始配色sentinel ff00ff|
|28|u8|尾欄，本profile0|

## S33 body，flags=0，長度42+名稱CP950 byte數

|offset|型別|語意|
|---|---|---|
|0,2|u16 BE,u16 BE|world x,y|
|4|u8|facing 0..7|
|5..8|u32 BE|object_id|
|9|u8|sex|
|10|u8|HumanInfo職業code，對應S05 offset5|
|11|u8|未知，本profile0|
|12..13|u16 BE|clothing_id|
|14|u8|hair_id|
|15..17|RGB3|hair_color|
|18|u8|武器模型編號，0無；見20261108-equipped-human-visuals|
|19..21|RGB3|附件相關，本profileffffff|
|22|u8|盾牌模型編號，0無；見20261108-equipped-human-visuals|
|23..25|RGB3|附件相關，本profileffffff|
|26..29|u32 BE|flags，本profile0|
|30..32|RGB3|clothing_color，獨立於hair_color|
|33|u8|未知，本profile0|
|34..|string8|名稱|
|名稱後|u8,u8,u8,u8,u16 BE,u8|本profile 0,0,0,0,100,0；各欄正式語意仍待分析|

原生shape衣色RGBA在+0a、頭髮RGBA在+0f。衣色為原始配色時不疊染色；本Client的S33 parser將RGB000000轉成ff00ff，ff00ff亦為原始色保留值。本profile自訂衣色不可宣稱純黑／保留洋紅能精確顯示，可用近黑；此限制不代表所有暗色不可用。染色只影響原資產具有染色層的範圍。

## S04鏡頭與world座標必須分開

實機教學已攔到把此偏移誤算成絕對viewport origin的錯誤；修正與回歸範圍見
[2026-11-01相機偏移修正](20261101-tutorial-camera-offset-correction.md)。

S04四個u16為x,y,viewport_x,viewport_y。原版此畫面viewport912×672、pane偏移(-56,-36)、tile48×32。格中心=(x*48+24,y*32+16)，鏡頭origin=((x-vx-1)*48,(y-vy-1)*32)。vx=8,vy=9使站立錨點與行走強制中點皆為(400,300)；舊9,9站立為(448,300)。改鏡頭參數不修改world x/y。此推導已服務測試，最後原生畫面驗收仍待A-006。

Evidence：S04 ev_08f45301d5c17fcf09333f54c049442dd32a4a6f551c4eba162e87fdd9ea893a；行走中點ev_7ef42381f981f43d0445908032c8e49e53fae75cac4328784b83661e4bcb97a7；S33 parser ev_b87944056795dfae54db7b4dbb56b24f2d5ddaf2fe93da340822ca1a2a1c257b；S05 parser ev_2e40660b7657ca90cb324c25e7c8a1bb095e3c1395b6335e1109c17f4740bcb0；renderer ev_26329f59fb408885c1bf63d2650f557748afd1ca6df71c02cb9298596e9e2864。
