# CT-101：隊伍最高有效傷害取得全額經驗＋個人掉寶

來源 [三項新規則](../02-server-planning/three-policy-adjustments-20261031.md)，R-033、SCN-018；本版只有 Server Domain 設計，**全部 planned/not-run**。Monster life 唯一、Party DamageLedger、PartyRoster Snapshot、PerCharacterRewardLedger 都待程式實作；Native Client UI packet 仍需 A-014/A-009/A-025/A-007。

|測試|輸入|預期|
|---|---|---|
|最高隊伍，而非最高個人|A隊甲60+乙40=100；B隊丙90|A隊勝，甲、乙每人**完整100%怪物基礎EXP**，丙0；不按個人60/40/90選隊|
|全隊享獎，不看個人輸出|A隊甲造成100，乙0|乙仍取得與甲相同的**完整怪物基礎EXP**，兩人都**各獨立一次**掉落表判定；不是共享一抽|
|獨立機率|同隊3人，一次 Monster death；測試 loot table 每角色中獎機率 p|每人執行一套獨立 drop resolution，可能全未掉、有人有、各人都掉；不保證每人掉落物品|
|單人虛擬隊伍|A獨自傷害100；B隊總90|A 代表一人隊伍，A 得全額 EXP + 一次 drop，B 0|
|有效傷害／刷分|重送同 damage event、打空、超 HP 造成溢出、治療|無效/重送不計，實際扣血傷害計；不靠 Client 告知傷害總數|
|死亡、重登、並發|同 `life_generation` 兩個死亡請求、timeout、DB commit 成功但 socket 斷線、重新讀取獎勵|只選一隊一次，各 winner member `monster_life+character+category` 只記一份 RewardLedger，掉寶抽選一次且結果可恢復|
|跨生命|怪物死後重生新 `life_generation`|傷害歸屬清零，新 life 才可重新結算，舊結果不重派|
|隊伍異動／平手／跨圖／離線|中途入/退隊、A隊=B隊總傷害、成員不在線或別圖|**未決政策**：實作前需明確定 tie、snapshot/eligibility；在尚無政策時不可暗選某個贏家或把「全員」改成只有打到的人|

獎勵投影給原版 Client 的 `EXP/Item` packet 仍需獨立確認，不可用這份規劃填造封包。另需測 Player A/B 共享同 Monster Actor，不同隊伍得到一致死亡視覺。真正原版兩 Client 的 CT 仍 not-run。
