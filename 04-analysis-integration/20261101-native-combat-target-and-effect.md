# 普通攻擊目標、S13動作效果與死亡派送補證

> 後續增量：[共享怪物與攻擊結算](20261101-training-combat-authority.md)已有Server核心及
> Host C13；正式啟動配置、即時投影與Client GUI仍待驗，本文333項codec測試屬當時範圍。

## 需求與本輪範圍

**使用者需求**：新手場景應可進行普通攻擊打怪；整段教學接好後才請使用者
測試。本輪先補實際Client路徑與S13 codec，不把封包編解碼完成當成戰鬥可玩。

原件Asgard.exe SHA256仍為
`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，
Ghidra12.1.4，analysis profile digest
`3c06738e45e144d5f073edbd3244c6bff46222f389525fe659bc92dca2ccdece`。
完整原始Evidence留本地，公開精選46條指令、派送表及procedure視圖見
[可攜證據](combat-target-dispatch-20261101.json)。沒有操作Client或取得原服封包。

部分handler沒有被Ghidra列為分析函式，偽碼查詢因而失敗；本輪改以REA精確
地址指令及bytes追查，沒有將「缺偽碼」解讀成「沒有handler」，也未修改原件
或修補Ghidra函式邊界。線性指令視圖不等於已證明全部動態可達路徑。

## C13不是一律非零的怪物ID

先前[A-009](../task_a/roy2/A-009-analysis.md)已證C13 body為BE u32，但欄位
完整語意未知。KeyBindingPane路徑`FUN_00497230`的action2分支先做hit test；
有候選時取其`FUN_0046e2e0`值，無候選時明確呼叫`FUN_005578d0(0)`。
後者會沿既有producer把參數送入C13。原件Evidence
`ev_eab44377eebdd171cf51db1adee4f45b97b499abf88ff3a8d61f00c0a129cdc1`，
producer既有視圖見[0x5578d0](../03-analysis-requests/web-skill-review/inputs/rea-attack-action.json)。

因此codec不得拒絕0或將其當成截斷；本輪將介面說明改為opaque attack argument。
這不代表Server必須對0造成傷害。零值是否代表揮空、面向前方、其他自動選敵等
仍需原生操作trace；Server不能憑0攻擊最近任意目標。也未將action2直接等同
某個固定鍵碼，教學文字的空白鍵說明與實際按鍵設定映射仍是不同證據。

## 原生派送表與handler地址

`0x578550`把opcode保存在packet base+8（Evidence
`ev_d4756836df8963a7637013895d82dd6b8195d173743f2eec6c56c7dcbda68be0`）。
`0x4f48a4..0x4f48ba`讀該欄、減3、限0..0x6e，使用byte表`0x4f4b30`後，
再查u32 thunk表`0x4f4a78`。byte/u32兩階查表不能當成opcode直接乘4。

|opcode|byte表slot|thunk|本輪確認的接收路徑|
|---|---:|---|---|
|S07|4|0x4f492d|既有物件生成handler0x4f17c0，可交叉核對派送公式|
|S08|5|0x4f495a|本輪只列派送位置，不重做狀態handler分析|
|S13|15|0x4f4990|0x4f4994直接JMP 0x4f2620|
|S1A|20|0x4f4936|與既有動作handler路徑交叉核對|
|S5F|34|0x4f49b3|0x4f49b7直接JMP 0x4f2bb0|

派送表Evidence為`ev_6e0665d5c29c269496ce81c461e722c53ae3a249535415b2db126351221fba1b`、
`ev_b3da25c5568b9870807470a867ab4946d2752b3c9f37566cd1010d84c43c3545`；
兩條JMP Evidence為`ev_00b4ff12935c543fd97580a3f9bd1195b4e63551934a1c66bf1b000421efcb16`、
`ev_85bd5fd52bc716ebc215d5ac163b9c86c1be9aeea979794f6707d6de1bf3c1d6`。

## S13欄位與效果模型

沿A-009 reader對應，完整packet pointer相對offset比reader子物件多0x0c：

|wire offset|type|完整packet offset|已觀察的使用|
|---|---|---|---|
|0..3|BE u32 ReferenceA|+0x24|registry查找並轉LivingObject；與本地角色ref比較；來源候選|
|4..7|BE u32 ReferenceB|+0x28|registry查找並轉LivingObject；後續受效果物件；目標候選|
|8|u8 Motion|+0x3f|傳入來源的動作處理，再送入動作setter|
|9..10|BE u16 EffectSelector|+0x40|非0時沿0x459660及效果建立分支使用；效果候選selector|
|11..12|BE u16 AnimationParameter|+0x3c|傳入來源動作處理的第5參數，再送虛擬表+0x44|
|13|u8 Flags|+0x3e|多種動畫／效果條件；不是已找回的傷害結果enum|

0x4f2620先從ReferenceB查找；ReferenceA的LivingObject候選與本地角色ref
比較後有選取分支。據此source/target是有根據的**角色推論**，不是原服
抓包定義；packed flags存在時更不能一律當成registry ID。

0x4f288f..0x4f28b0將目標物件、flags、motion、effect selector、animation
parameter及本地控制參數送入來源虛擬表+8。Monster對應0x4d6c60，Human
候選0x47bc20；兩者把motion與animation parameter送虛擬表+0x44，對應既有
S1A型動作setter路徑。此前對S1A的100%速度已另有分析；本輪codec仍用
中性名稱AnimationParameter，不把所有S13來源物件的單位及動作列舉當作已驗。

ReferenceB物件另進0x4a4b00效果處理。這些觀察**不證明任何u16/u32就是
權威扣血量、HP百分比、命中／暴擊／治療結果**。HP、傷害公式及成功事件
仍由Server獨立判斷，效果包不能當作已保存戰鬥狀態。

### 解碼長度

固定14 bytes。Flags bit3/bit4會把對應u32拆成兩個16-bit座標候選並清該ref，
不多讀bytes。bit0才追加17 bytes：u8、3×BEu16、u8、2×BEu32、u8，共31。
新增codec保留兩個原始u32、flags及擴充的中性欄位，不抹掉packed值；
flag與extension必須一致，截斷或多餘bytes均拒絕。codec不授權發包或扣血。

## S07 kind與S5F的進一步邊界

原S07 handler對kind1/2/4均建MonsterObject，但建構參數mode分別為1/0/3，
並保存於object+0x284；`0x4d6050`讀此值。在0x4b7351附近的輸入判斷，
mode1走回傳2，mode0經減法分支走回傳1。這為「教學NPC與攻擊怪不能直接
沿用相同kind」提供額外線索；尚未完成該action回傳值到實際滑鼠C13／C43
producer的完整證明，不能僅憑mode0就宣稱kind2已通過可攻擊實機。

S5F handler `0x4f2bb0`從完整packet+0x24取u32，沿同registry lookup0x4eac30
及MapPane清理路徑0x4ba310使用。這支持它是registry key的處理，不是死亡
傷害數字；死亡動畫、屍體留存、S0E時序與掉落仍未本輪實機確認。

## 實作與驗證狀態

333項Server測試通過；新增S13固定／packed／extension獨立byte vector、所有
截斷長度、尾隨bytes及flag不一致拒絕，並保留C13零值與非零原值。
這些是codec／合成回歸，**尚未啟用Host C13結算或產生practice-attack-resolved**。

下一步：依原生目標路徑接可信怪物registry、距離／方向／頻率與生命狀態，
由真正Server結算產生攻擊事件，再驗Client動畫、受擊及死亡。原版怪物HP、
傷害公式、教學擊殺條件與場景仍未知；不得用codec測試代替可玩戰鬥與完整教學驗收。
