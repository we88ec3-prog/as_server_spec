# 外觀profile欄位與螢幕座標

body offset不含opcode／ordinal／frame header。此處只規範原型已實作的選填欄子集，不能套用任意flags。

## S05 body，29 bytes，本profile flags=0或0x1000

|offset|型別|語意|
|---|---|---|
|0|u32 BE|object_id|
|4|u8|sex|
|5,6|各u8|未知，本profile0|
|7|u16 BE|clothing_id|
|9|u8|hair_id|
|10..12|RGB3|hair_color|
|13|u8|未知，本profile0|
|14..16|RGB3|附件相關欄位，本profileffffff，語意待補|
|17|u8|未知，本profile0|
|18..20|RGB3|附件相關欄位，本profileffffff，語意待補|
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
|10,11|各u8|未知，本profile0|
|12..13|u16 BE|clothing_id|
|14|u8|hair_id|
|15..17|RGB3|hair_color|
|18|u8|未知，本profile0|
|19..21|RGB3|附件相關，本profileffffff|
|22|u8|未知，本profile0|
|23..25|RGB3|附件相關，本profileffffff|
|26..29|u32 BE|flags，本profile0|
|30..32|RGB3|clothing_color，獨立於hair_color|
|33|u8|未知，本profile0|
|34..|string8|名稱|
|名稱後|u8,u8,u8,u8,u16 BE,u8|本profile 0,0,0,0,100,0；各欄正式語意仍待分析|

原生shape衣色RGBA在+0a、頭髮RGBA在+0f。衣色為原始配色時不疊染色；本Client的S33 parser將RGB000000轉成ff00ff，ff00ff亦為原始色保留值。本profile自訂衣色不可宣稱純黑／保留洋紅能精確顯示，可用近黑；此限制不代表所有暗色不可用。染色只影響原資產具有染色層的範圍。

## S04鏡頭與world座標必須分開

S04四個u16為x,y,viewport_x,viewport_y。原版此畫面viewport912×672、pane偏移(-56,-36)、tile48×32。格中心=(x*48+24,y*32+16)，鏡頭origin=((x-vx-1)*48,(y-vy-1)*32)。vx=8,vy=9使站立錨點與行走強制中點皆為(400,300)；舊9,9站立為(448,300)。改鏡頭參數不修改world x/y。此推導已服務測試，最後原生畫面驗收仍待A-006。

Evidence：S04 ev_08f45301d5c17fcf09333f54c049442dd32a4a6f551c4eba162e87fdd9ea893a；行走中點ev_7ef42381f981f43d0445908032c8e49e53fae75cac4328784b83661e4bcb97a7；S33 parser ev_b87944056795dfae54db7b4dbb56b24f2d5ddaf2fe93da340822ca1a2a1c257b；S05 parser ev_2e40660b7657ca90cb324c25e7c8a1bb095e3c1395b6335e1109c17f4740bcb0；renderer ev_26329f59fb408885c1bf63d2650f557748afd1ca6df71c02cb9298596e9e2864。
