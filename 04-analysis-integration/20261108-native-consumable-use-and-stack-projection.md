# 原生直接使用物品與堆疊同步

2026-11-08。使用者要求繼續開發；藥水的HP40／MP40、stack20、冷卻1秒、買30／賣15為Server重建政策，原服物品定義及效果仍未知。紅／藍瓶圖示8244／824a沿既有原件圖示契約，不由顏色推導原版用途。本輪只補Client意圖與同步證據，未修改Host／Client／素材。

## useKind5是直接使用意圖，不是穿衣限定

S0F既有安全子集可投影一般背包kind1、slot、圖示、RGB255、useKind5、名稱／描述與quantity mode0的BEu16正值數量。writer的useKind在固定頭第9個byte；原件reader57a3f0存parser+425，完整packet+431，handler4f4610交489fe0的parameter6存InventoryEntry+611。數量由parser+628／完整packet+634交parameter7，存entry+612；mode0存entry+610。

ItemList activation4932c0依entry+611分流，case5建立577750的C1C，寫kind=489a90(displaySlot)、slot=489ab0(displaySlot)、flag0及useKind5，直接5788a0送出；沒有因圖示或其他欄位自行選C1E。ctor577750本身也明設flag0。一般背包結果為 **C1C body `01 slot 00 05`，恰好4bytes、沒有tail**。它是Server授權使用的意圖，是否消耗／裝備／回復仍須查該格權威物品定義，不能依Client要求創造資源。

快捷列GameLogic46d2c0的case0為物品；查489e60後，同樣依entry+611 case5建立C1C、寫kind／slot與useKind，flag保留ctor0。因此原生快捷鍵可以使用本次重建藥水。其他useKind進文字／選目標等流程，本輪不開放。ItemList activation是已追通的原生使用入口；此輪未將其所有滑鼠手勢逐一對應為雙擊或右鍵，應由GUI驗收各自確認，不把未測手勢稱為通過。

## 目前格數量與快捷列

S0F4f4610經4899c0把entry放入UserInventory；後者對kind1／2呼叫539490，同key會先解構舊entry，再置入新entry。**S0F同slot完整投影新quantity可覆寫剩餘數量，不必先S10。** mode0由4896c0依entry+612格式化數量文字，不能把BEu16誤寫成一個u8。

最後一件消耗後用 **S10 body `01 slot 00`** 清整格；S10沒有「減一」數量欄。4f2450第三欄0選UserInventory，489a00→538f20移除該格及解構entry。已追InventoryEntry48a2a0→48a240→40b3e0的釋放鏈；S10及S0F replacement均沒有呼叫559500的技能快捷列清理。這與S63清技能時不同，不能把S63的清快捷列結論套到S10。快捷列仍以格位引用；該格空時不能用殘存引用通過Server物品授權。

成功使用且remaining>0只投影同格S0F新數量，消耗完才S10；同交易完成資源恢復與扣物品後再送S08及背包delta。拒絕、滿資源、死亡、冷卻、owner／lease／版本不符的政策由Server決定，不先樂觀扣物品。是否原版允許滿血消耗未知；重建可明示採無變更不扣費。

## 拖曳合併與空格拆疊界線

沿既有C30契約：492be0在**非空目的、相同icon及完整名稱**的分支，經數量對話回調4925c0，寫quantity至packet+2b；571c60將subtype8序列化為 **`08 kind src dst quantity`五個u8**。數量不是u16；Server仍須檢驗來源堆疊、目的相容與上限，不能只比名字／icon。

目的空格走subtype0四bytes，沒有數量欄，是整疊移動意圖；本版已追UI沒有因此提供空格部分拆疊入口。Server的部分轉移API／單元測試與原生UI能否送出要分開標示。一般背包kind1，另一區kind2不因本輪藥水需求開放。

本輪是原件靜態ABI補核。待集中GUI：背包啟動、快捷鍵連用、剩餘數量顯示、最後一件清格、耗盡後殘存快捷列、同類堆疊合併與重登保存；右鍵／雙擊手勢未測，不以TCP合成測試替代。
