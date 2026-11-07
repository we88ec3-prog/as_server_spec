# 背包、技能與普攻格位的持久化排序

日期：2026-11-08。使用者回報拖曳技能／法術排序與背包換位後斷線，本地診斷確認收到C30、len4而被當成未知封包。C30的原生欄位與確認投影由對應原生分析記錄；本頁說明排序的Server權威與持久化合約，不從Server設計反推原服資料庫。

## 背包空格移動與交換

排序與使用、堆疊拆分、保存或販賣是不同操作。Server必須持有目前owner lease、已提交載圖、整體inventory revision、來源instance ID／slot／item revision，以及目的格的權威預期。

- 目的格預期為空時，實際必須仍是空格。
- 目的格有物品時，驗證其exact instance／slot／revision後交換；不能只驗來源後覆寫另一件。
- 來源與目的相同為NoChange，不變更版本，但可保存收據。
- 排序不自動合併相同堆疊，不改數量、owner、取得事件、裝備、保管庫或錢包；實例ID保留，改格位的實例版本各自增加，inventory revision只增加一次。

交換必須單一交易，不能先刪除或提交一件再處理另一件。唯一索引`owner／location／slot`在中間階段仍有效。同一location的兩件都放到slot0會撞索引；本輪修正為各自不同的交易內負原格位，最後全部恢復正合法格位。負格位不能被提交或投影，任何寫入／收據失敗整筆回滾。

## 技能與普攻格位

角色技能JSON新增`BasicAttackSlot`，舊JSON缺此欄位預設1，不重建技能或改舊角色進度。技能／普攻合法格位1..80；新學技能仍優先沿原有2..80配置，再考慮1，既有首技能2的預設配置不因本次修正改變。

普攻以保留內部key `basic-attack`辨識，不是可新增的職業技能定義。非魔法師的職業技能與普攻同屬kind1格位空間，不能重疊；把技能拖到普攻位置可以交換，普攻位置因此持久改變。魔法師spell kind0與普攻kind1為獨立空間，同一數字格位可以各有一項，不能誤把法術拖曳當成交換普攻。

技能排序驗證來源key／slot、目的key／slot或預期空格、目前技能revision及角色職業。只變更格位，不改rank、SuccessfulUses、ReadyAtUtc、HP／MP／SP、技能定義或遊戲事件。重整已學技能、升級或記錄成功施放必須保留BasicAttackSlot；非魔法師新增技能時必須避開目前普攻格位，不能假設普攻永遠固定1。

此頁取代早期「kind1／slot1永遠是普攻」的固定格位假設；原生Client仍需由Host正確投影、處理C65及清理舊格位，不能只保存JSON而留Client快捷鍵指向錯誤技能。

## 收據與交易邊界

背包沿既有inventory收據，技能排序沿既有skill_ops表，使用獨立`skill-reorder:`鍵空間及排序專用receipt DTO，避免把施放結果誤解成排序結果。不新增資料表或重設任何帳號／金鑰。

同操作ID同意圖只回歷史收據；不同source／destination／預期內容碰撞為衝突。歷史snapshot不能回寫目前狀態，也不能直接覆蓋已重新排序的Client畫面；Host需重讀目前權威狀態後投影。舊lease、斷線、未提交載圖或錯owner，即使重送已成功收據也不能繞過權限。

## 定向驗證與界線

本輪排序Domain3項、SQLite持久化10項全部通過，涵蓋空格／交換、相同堆疊不合併、來源／目的exact expectation、舊版本、舊lease及斷線、防重、NoChange收據、普攻交換後新增技能避位、魔法師兩個kind空間、舊JSON相容、保留熟練度與冷卻、施放／排序同文字ID不混DTO、並行同事件及強制收據失敗回滾。

抽換位保留格後，既有Inventory Store11項、Skill Store24項、Commerce Store10項回歸通過。這些是Server／合成資料庫驗證，不是原生GUI拖曳、快捷鍵重綁或全套Server驗收；原生確認封包、實際拖曳後技能施放、跨重登／Server重啟仍由Host與集中測試記錄。
