# 傳送師、分職業目的地與完成交易

> 後續增量：[生活／戰鬥講師](20261101-tutorial-lesson-npcs.md)已透過Host對話處理產生
> 對話關閉觀察；本文件318項測試中的直接注入描述屬當時範圍，真正攻擊仍待開發。

## 需求與原件邊界

**使用者需求**：新角色走完新手教學、選職並進入各職業城鎮，完整流程接線
後再安排一次人工測試。本輪實作傳送／完成交易，不能據此宣稱整段已完成。

原件`Script/nNewTeleport01.dat` SHA256
`092f168d5de1a25b09b080065419c62279a696fa7798cf7aa98dc82b26f90c06`，
嚴格CP950文字CRC32為`4e711abf`；身份與函式見
[已重新核對的介面摘要](tutorial-career-script-interface-20261101.json)。
它依ServerParam.JOBRET選擇分支：SUCC顯示可出發，最後OK回STATE=OK並
Dispose；否則提示尚未選職，最後回STATE=CANCEL。Merchant wrapper的TALK
會留在ClientReply中，因此這條路徑使用TYPE=TALK與STATE。

**尚未知原服規則**：腳本沒有目的map/ref、xy、數字職業碼、獎勵或原服
畢業條件。不能把文字「不同職業往不同城鎮」解讀成已找到五個map編號。
角色旗標、交易時點與下述milestone gate都是復原Server政策，非原服推導。

## Server發行與消費對話

傳送師綁精確來源map/ref、內容revision、NPC ref／位置與已驗Script CRC。
近距離點選需目前World owner、已提交載圖及同revision的持久入學紀錄。
與招募員／就職指導員最多同時一個Merchant run；context不可由Client指定。

- 未選職：發原生Merchant+nNewTeleport01，JOBRET=FAIL；可TALK與取消，
  不接受OK出發。這是原件已有的未選職分支。
- 已選職但缺本地完成條件：回非空S02教學提醒，不假裝角色沒有選職，
  不發行可出發的runner。S02沿用已有格式，本輪提醒仍未GUI驗證。
- 已保存職業的career/admission revision與政策一致，且全部條件滿足時，
  才發新Merchant context及JOBRET=SUCC。依賴包括MerchantDialog、QuestDialog、
  nNewTeleport01；本輪仍使用明示helper候選外觀，不稱原版傳送師造型。
- 只允許TYPE/STATE兩個reply key。TALK沒有STATE不出發；ABORT／CANCEL
  終止此run；合法STATE=OK記在當前run中，重送不改資料。Client不能提供
  JOB、目的圖、座標、完成條件或獎勵。錯context／遠距／舊owner均拒絕。
- 等同runner的Dispose4才開始同socket S15、S14(1)載圖；Dispose／Close本身
  不完成教學。遲到的同context cleanup不再次傳送；其他context不被吞掉。

## 指定條件與進度語意

完成計畫含rule revision、已保存的符號職業、career rule revision、admission
revision及1..8個必需milestone `(key, revision)`；key唯一、長3..48，只允許
小寫英文字、數字和連字號。revision長8..128且無控制字元。空條件集不接受。

milestone只能由可信Server遊戲事件呼叫寫入，驗當前lease／載圖／完整位置與
version；每角色、key、revision唯一並冪等。它不是開放給Client或Web管理者
勾選畢業的API。修改revision後舊事件不滿足新條件。原件沒有證明需要哪些
milestone，因此實際配置必須明示是復原版政策，不能改名為「原版完成條件」。

`life-dialogue-closed`只能代表指定對話曾關閉，不能證每頁讀完；
`war-dialogue-closed`不能當戰鬥成功；`practice-attack-resolved`需將來由真正
Server攻擊結算產生，不能從Dispose或Client自報捏造。它們目前只出現在
合成測試所注入的可信遊戲事件，**生活／戰鬥NPC及實際戰鬥尚未產生這些事件**。
本輪沒有設定自訂必殺數量或宣稱原服必殺某怪。

## 目的地與原子提交

Server必須為Thief、Warrior、Monk、Mage、Cleric各自顯式配置一個可信目錄
中的目的map/ref與revision；不使用選單index推數字職業碼，不缺省傳去同一圖。
多職業可以明示共用一個實際城鎮，目的圖的可站立出生點沿用已驗內容fixture。
未知職業鍵、缺職業、來源與目的同圖、內容版本不符都在啟動時拒絕。
實際目的圖身份仍需原件／場景查證；測試使用的1000..1004是合成編號。

Begin時鎖當前owner及位置version，重新驗入學、選職及所有milestone，要求
尚未完成教學、無其他pending載圖；保存完整transfer及不可變完成計畫至同一
epoch。計畫按milestone key排序後穩定序列化保存，Commit必須與原計畫一致；
不能在載圖中刪條件、改職業、改rule或換目的地。

C35正確、owner／epoch／期限／舊位置及全部計畫仍有效時，在**同一交易**：

1. 將load attempt改committed，寫新目的地位置及position version+1。
2. 寫唯一transfer outbox。
3. 將該角色tutorial_completed從0改1，寫唯一tutorial.completed outbox及rule revision。

首次出生checkpoint保持原值；不發未證獎勵、金錢、道具或技能。
任何一步失敗均回滾，包括完成事件寫入失敗。錯C35、逾時、斷線或owner
替換保留上次已提交位置及未完成狀態；新連線可從原場景接續。提交成功但
回應遺失時，重登讀到目的地及已完成狀態，不會再畢業一次。

World v6新增graduation-v1 epoch擴充表保存完整計畫；已有帳號的file-backed
SQLite缺表時，先做一致性備份再新增，重複初始化不再備份。PostgreSQL本輪未實測。

## 驗證與剩餘工作

318項Server測試通過。新增覆蓋五職業分別挑選目的地、未選職原生FAIL分支、
缺條件提示、OK等Dispose、錯C35／中斷重登留舊圖、成功重登留新圖且已完成、
milestone版本與冪等、載圖凍結、計畫刪條件拒絕、逾時／owner替換，以及用
SQLite trigger注入完成事件寫入錯誤後，位置／attempt／旗標一起回滾再重試。
另有啟動設定的缺職業、非法數字職業鍵、地圖版本錯誤、無revision條件拒絕。

這些是合成Host／SQLite驗證，不是實際Client已走完教學。新功能未在使用者
運行中的Server啟用，也未預設綁定未證實的城鎮。下一步仍須接生活／戰鬥
教學與真實攻擊事件、查證學校／各城鎮場景、數字職業狀態投影，再做整段GUI
驗收。資料庫能提交完成旗標不代表本執行緒的完整目標已達成。
