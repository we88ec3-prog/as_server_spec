# 首次快捷鍵命中、NPC未動作、學校BGM與原生重連

使用者實機回報：對NPC按空白鍵時角色完全沒有揮拳；快捷鍵必須先用空白鍵
命中怪物一次才會造成傷害；登入學校沒有BGM。本輪修正均仍待新版GUI驗收。
原件視圖見[native-first-shortcut-tail-bgm-reconnect-20261102.json](native-first-shortcut-tail-bgm-reconnect-20261102.json)。

## NPC未揮拳：撤回未擴充S13為14B的舊分析

重讀原件reader `0x57de90` 確認：14B固定欄位後，bit0若有則讀16B擴充資料；
**兩條分支最後都呼叫 `0x45adb0` 讀一個u8**。最小15B，擴充31B。
先前把最後一個u8算進可選17B，造成無擴充時少送1B，屬分析／實作錯誤。
先前codec與TCP emulator沿用同一錯誤邊界，所以通過不能支持native可解析。

`0x45adb0` 發現剩餘byte不足時會清stream+0x14有效旗標；不憑空宣稱會拋例外。
必讀尾碼的用途尚未知，重建送0。它不表示命中、不扣HP，也不是MISS enum。
本輪把尾碼移到封包共同欄位，條件擴充只有16B；原31B命中封包bytes維持一致。

當前最小MISS範例（ref0x1001）：
`00000001 00001001 04 0000 0064 00 00`。
仍依既有HitNumber type3/4/5／MISS素材證據，不改成數字傷害0。
公開packets、既有A-009 codec、測試與分析已同步更正；舊日期的14B通過敘述只作歷史。

本次診斷Client/build9fcfe5d的遮蔽日誌彙整曾有16次C13後發14B S13，
證明不能把「NPC沒動作」都歸咎於沒有發出C13；但這不是新版15B GUI成功證據。

## 首次快捷鍵命中：取消先前選取依賴

先前C0E普攻使用3秒內C44／C13目標，使用者先按空白鍵命中後才可用快捷鍵的
現象與這份重建政策吻合。本輪撤除該政策，C44恢復純檢視請求。

原生Space `0x497230→0x4430c0` 以面向一格找物件。重建C0E現在從Server已提交的
位置／面向計算同一格，只在已投影、存活訓練怪或已投影設定NPC中選取；
沒有目標就空揮。方向0..7依次為N/E/S/W/NE/SE/SW/NW。
同格衝突採訓練怪優先、ref遞增，是明示的重建決策，未宣稱原服目標排序。

因此不需先C44或對目標送C13。依然驗owner、載圖、對話狀態、距離、冷卻與生命週期；
NPC不扣血、不給practice進度。C65仍只驗已發kind1/slot1，不執行第二次攻擊。
朝向不同就不會打中旁邊／後方對象，這不應再用保留的舊選取目標補打。

## 登入學校無BGM：缺少額外地圖cue

現有初始Map6有明確開發用music設定；AdditionalMaps的Map7及城鎮沒有Music段。
已保存位置重登時會選該map runtime，其Music原為null，故C35完成後不發BGM cue。
這是Server配置接線問題，不能從此說該地圖原版沒有音樂或Client音量被關閉。

新政策：有額外地圖Music段就尊重該段，包括Enabled=false與Track0明確停止；
沒有段時，沿用已驗證的初始試驗track，重新綁定該map/ref/revision。
初始音樂關閉則不繼承。未恢復官方map→track表；目前是使用者希望有BGM的重建fallback。
載圖與重登均經C35後S19 kind1、local0、trackBEu16；測試cue為 `01 00 00 01`。
原本命中／死亡的一次性音效維持獨立，不與BGM欄位混用。

## C00起始的原生斷線重連

原件 `0x4320a0` 初次連線先送raw `baram` 再呼叫 `0x4f1050` 發CVersion；
`0x4c02f0` MapPane斷線確認成功重連時直接呼叫 `0x4f1050`，再 `0x4be2b0(0)`
清場並建立登入介面。這一分支沒有初次標記；先前日誌確有新連線直接C00/body8而被拒絕。
`0x577dd0` 的opcode0、writer `0x577e80` 的u16/u8/u8/u16/u16共8B，支持此握手格式。

本輪僅Region3 NativeMapTrial允許Connected收到plaintext C00/8B後進VersionAccepted；
不偽造SignatureAccepted，也不直接授予帳號或World lease。普通非native流程仍拒絕。
後續metadata／選服／帳密／一次性C10 grant照常驗證；錯密碼仍拒絕。
此分支沿用既有C00長度檢查，未宣稱恢復所有原服版本／CRC相容性比對。
重複C00、錯誤長度、未完成握手直接C03仍拒絕。GUI自動重連尚待實測。

## 被動實測、驗證與下一輪

已成功以VM_READ讀診斷Client有限欄位：own flags0、狀態byte0、移動階段0、
資料存在、攻擊間隔1000、普通鍵模式0、input gate15，Attack列為20/00/20/02；
當下clock126567、上次攻擊110421。這是非同步快照，不是對過去某次按鍵的完整因果證明。
本輪未注入hook、未改Client記憶體／EXE，也未重開使用者Client／Server。
日誌中C65已正常處理且可繼續動作；使用者對新版NPC動作的明確失敗仍保留。

380項.NET通過，公開A-009修正codec的15項測試通過；五職業實際內容TCP全部通過：
不先選取的快捷鍵首次命中、C65不雙打、15B NPC MISS、不給practice進度、
每次載圖／重登BGM1、畢業、C00起始重新認證與保存城鎮。參見
[機讀驗證](first-shortcut-tail-bgm-reconnect-validation-20261102.json)。
TCP第一輪曾誤等不存在的C11 turn ACK而timeout，依既有契約移除該等待後重跑通過，
沒有因此改Server增加假ACK。

下一次正常重啟後集中驗：面向相鄰新生摩斯直接按1→面向相鄰NPC按Space→
確認揮拳與MISS→離開遊戲同Client重登及BGM。發生問題時保留Client／Server。
地圖數與出口另見[室內圖與教學範圍](20261102-school-room-and-exit-scope.md)，
目前不把所有教師同放Map7的候選安排當成原版完整教學動線。
