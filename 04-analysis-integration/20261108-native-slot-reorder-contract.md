# 原生技能／魔法與背包拖曳移槽

2026-11-08。使用者回報拖曳技能、魔法排序及背包道具會斷線。本文件補 A-007 未涵蓋的原生 ChangeSlot ABI；觀察來源是不可變 EXE SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145` 的 REA 靜態證據。未宣稱此輪原生 GUI 已通過。

## C30 ChangeSlot

RTTI `.?AVCChangeSlotPacket@@` 位於 `0x669378`。constructor `0x571bb0` 呼叫 `0x578600(0x30)`；writer `0x571c60` 第一 byte 為 subtype。以下 body 不含 opcode、ordinal 或 AA frame。

|subtype|body|已追到的原生操作|
|---|---|---|
|0|u8 subtype, u8 kind, u8 sourceSlot, u8 destinationSlot|ItemListPane 移動／交換不同物品或移至空格|
|1|u8 subtype, u8 kind, u8 sourceSlot, u8 destinationSlot|ActionList 拖曳技能／魔法位置|
|8|u8 subtype, u8 kind, u8 sourceSlot, u8 destinationSlot, u8 quantity|ItemListPane 相同名稱及 icon 的堆疊合併／部分轉移請求|
|2|u8 subtype, u8, u8, BEu32|writer 存在，未追本次業務意義，不應由拖曳需求直接開放|
|7|u8 subtype, u8|writer 存在，未追本次業務意義|

技能拖曳原生入口 `0x445020`，`0x445082` 寫 subtype1；它先取來源、目的 cell 的原生 action ID，經 `0x4019d0` 拆解 kind/slot。該函式的精確轉換為 `kind=(id-1)/80`、`slot=(id-1)%80+1`；反向 `0x4019b0` 為 `id=kind*80+slot`。因此本次兩組 action 的 slot 是 1..80，kind0 為已實作的 Spell 分類、kind1 為 Skill 分類，不能把技能內部穩定 key 當成線上 slot。

背包入口 `0x492be0`，不同項目或空目的格走 subtype0。`0x489a90` 將本地顯示索引依分界轉為 kind1／2；`0x489ab0` 轉來源與目的 slot。一般背包只實作 kind1 時應拒絕另區 kind2 的資產操作，不能把另一區誤當一般背包延伸。相同 icon、完整名稱的 UI 路徑可經數量對話呼叫 `0x4925c0`，送 subtype8；數量在 wire 上只有一個 u8。原生 UI 的相同圖示／名字比較不是 Server 可合併規則，Server 仍須核對模板、屬性、綁定、堆疊上限及所有權。

上述兩個拖曳入口沒有在送出前完成 ActionInventory／UserInventory 的權威 swap。Server 不應僅吞包而不投影結果，否則 Client 圖示與持久槽位不一致；有效未實作操作也不該直接被 unknown-opcode 路徑斷線。

## 技能清除及重新投影

**S63 body 是 u8 kind、u8 slot。** reader `0x585950` 依序存入 parser +0x18/+0x19；完整 packet handler `0x4f2f10` 從 +0x24/+0x25 取相同兩欄，經 `0x4019b0` 建內部 action ID，呼叫 `0x538f20` 刪除 ActionInventory entry。

同一 handler 還呼叫 `0x559500(1,internalActionId)` 清理快捷列對該 action 的引用。因此 S63 不是純隱藏圖示，也不會自動把舊快捷列追蹤到新 slot。採用「S63 清來源／目的，再 S62 發新位置」時必須記錄快捷列被清除的行為；不能承諾快捷鍵仍綁定原技能。沒有因 ChangeSlot 類名就新增假 S30 ACK，本輪亦未證明獨立原服 swap-ack 封包。

S62 已有同版技能契約，會替換相同 internal action ID 的 entry；移往空格也仍須清舊來源，否則舊技能成為幽靈副本。交換時先清兩端再投影雙方新位置，基礎普攻也必須依 Server 保存的新槽處理施放，不可永遠把 slot1 認成普攻。技能 rank、冷卻及學習記錄須綁穩定 skill key，不隨槽位變更重置。

## 背包回覆與 Server 界線

背包可依既有 S10/S0F 移除／完整重投影受影響槽位；本輪沒有建立專用 ChangeSlot response。S10 仍依已審背包契約的 kind/slot/移除模式處理，不從 subtype0 推造 Drop 或永久刪除資產。移動、交換、合法合併與部分數量轉移必須在同一資產交易完成，再投影其後 snapshot。

Server 的 lease、角色 owner、槽範圍、來源存在、目的相容、數量、capacity、revision 與重播規則屬重建權威政策。相同請求 body 不是原生唯一 operation ID；交換命令不能任意用原始 bytes 當永久去重鍵，否則合法第二次交換會被誤吞。過期情境／拒絕後以當前權威狀態刷新，不可用舊 receipt 快照回退後續狀態。

需要集中驗收：移至空格、兩項交換、合併／部分轉移、技能與魔法分組、普攻移槽、重登保存、無效範圍不改資產、重排後重新拖快捷列施放。此文件是原件靜態交付，TCP 合成測試與 Client GUI 回報另記。
