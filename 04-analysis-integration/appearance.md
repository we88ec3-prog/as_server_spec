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


## A-006／roy2 原版 S05/S33 flags 補證與置中驗收（2026-10-31）

原始 `Asgard.exe` SHA `db3df616...` 以實際 binary VA 核對 13 組 native instruction patterns；`S05` `0x5895A0` 先 BE u32，按 flags 低 byte `bit0`（額外 RGB3）、`bit4`（額外 BE u16）、`bit1`（額外 u8）、`bit7`（額外 u8）條件讀取。**29B S05 僅能用於已知本版 `flags=0/0x1000`**；不適用全部 flags。自身 `S05` 髮色 RGB +10..12、衣色 +25..27 是兩個獨立值。

`S33` 原生 parser `0x585570` 已確認前段 BE u16 x/y、u8 facing、BE u32 object；flags=0 的 CP950 string8 名稱與髮色 +15..17、衣色 +30..32；`0x585667` bit0 額外 RGB、`0x58568B` bit4 額外 u16、`0x5856A4` bit1 額外 byte、`0x5856B4` bit7 額外 byte、`0x585719` bit13 額外 string8。**`42+CP950-name-bytes` 僅 flags=0 profile**。另在 `0x585780..0x5857F4` 有三色全零→FF00FF 的原生 sentinel 正規化分支，但不能據此推論所有黑色顏色禁用或 YPF 完整染色層行為。

已知 profile viewport `(8,9)` 在 48×32、pane(-56,-36) 計算錨點 `(400,300)`，`(9,9)` 則 `(448,300)`；**此為畫面座標投影/既有公式，非原生截圖完成證據**。13 組原件 PE checks 與 10 項合成測試 PASS；CT-058 offline subset 已驗，CT-059 原生 8 向動作／髮衣獨立染色／換裝／切圖／重登**未執行**。參見 [A-006 原生 Client 報告](../task_a/roy2/A-006-analysis.md) 與 [驗收腳本](../05-conformance/A-006-appearance-test-plan.md)。A-006 `integrated / ready` 是 Client I/O **靜態交付完成**，不代表 renderer/YPF/DOI/native GUI fully validated。
