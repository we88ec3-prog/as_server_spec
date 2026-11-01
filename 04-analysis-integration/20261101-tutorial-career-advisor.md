# 原生選職介面與持久選擇

後續已確認[原生職業欄位與投影](20261101-native-career-appearance-projection.md)：
S05 offset5／S33 offset10帶已保存職業，五職業完整TCP更新／重登通過；
本文原先數字職業未定的限制已由該增量縮小，GUI與能力規則仍未證。

> 後續增量：[傳送師與完成交易](20261101-tutorial-town-departure.md)已有Server實作；
> 真實教學事件與場景綁定仍未接齊，本文末列待辦保留其當時範圍。

## 需求與原件證據

**使用者需求**：新角色完成新手教學並進入各職業城鎮；完整流程接好再安排
一次人工測試。這是產品目標，不代表原件含有相同Server狀態機或必殺怪物條件。

本輪重新讀取六份原始Script，驗SHA256、bounded zlib、BE版本及UTF16長度、
嚴格CP950文字CRC；與既有資源索引比對。MerchantDialog原索引漏列，另沿用
招募員分析的原件SHA pin，再計算其CRC。函式介面及原件身份見
[可公開索引](tutorial-career-script-interface-20261101.json)。此為靜態literal摘要，
不是執行期trace，也不包含完整腳本文字。

|原件函式|確認的Client介面|Server不能由此推論|
|---|---|---|
|Merchant.Main|初始化ServerParam／ClientReply等全域；TYPE=DIRECT走MerchantDirectTalk|DIRECT字串本身不授權選職成功|
|MerchantDialogProc|TALK先回TYPE=TALK，再在同runner呼叫MerchantTalk；ABORT為離開|只有TALK不代表選職或教學完成|
|nNewJob01.MerchantTalk|JOBALD=YES顯示已選職提示，否則開選職流程|Client提供的JOBALD不可當權威來源|
|JobMessage04Proc|五個選項依序設JOB為盜賊、戰士、武道家、魔法師、聖職者|選項SEL0..4不是數字職業封包代碼|
|JobMessage05Proc|最終OK回STATE=OK與JOB變數，之後Dispose runner；取消回前一選單|送出值本身不證符合Server資格|
|JobMessage01/02/03/07Proc|終止分支回STATE=CANCEL；部分內層取消只在Client返回前頁|所有取消都會有同一封包|
|MerchantDirectTalk／JobMessage06|讀JOBRET，SUCC開成功結果頁；此頁關閉只Dispose|結果頁文字不能證Server已實際發放禮物|
|nNewTeleport01.MerchantTalk／TeleportMessage01Proc|JOBRET=SUCC允許出發對話，OK回STATE=OK；未選職走CANCEL|實際目的map/ref、xy、職業數字碼及原服畢業交易|

腳本「魔術師」出現在某確認文案中，但送出的JOB變數是「魔法師」。
不能把文案別名或英文職業名當本介面的合法JOB值。

## 復原Server政策與本輪交付

五職業以穩定的符號key保存：Thief、Warrior、Monk、Mage、Cleric。
這些是Server內部key，**不是原生數字職業碼、選單index或S08欄位值**。
目前不發明對應數字、不改角色能力／技能、不發送猜測的職業更新封包。

就職指導員使用獨立NPC ref，綁定精確map/ref、revision與座標。點選需已完成
目前載圖、同World owner、近距離及已保存的正確revision入學事件。Server
發行Merchant runner及新非零context，攜帶MerchantDialog、QuestDialog、
QuestSelDialog、MultiHelpDialog、nNewJob01的已驗文字CRC。

初次開啟參數JOBALD=NO；已保存選職時為YES。Server只消費自己發出的
runner/context，且回覆schema最多TYPE/STATE/JOB三個key。TALK無選擇不寫入；
CANCEL／ABORT不選職，該run之後不能再轉成OK；新的context可重新選。
STATE=OK必須同時為TYPE=TALK且JOB精確符合五個原件值。遠距、錯context、
未知JOB、額外key、衝突選擇與舊World owner均不授權寫入。

保存交易重新核對當前lease、無pending載圖、位置與version完全一致，以及
持久入學事件。每角色只允許一筆職業；相同職業／rule／admission重送回相同
紀錄，其他職業或不同規則revision拒絕。職業與唯一outbox事件同交易提交。
它不改首次出生checkpoint、教學完成旗標、位置、金錢或道具。

選職完成後等原runner的Dispose4，再以新context啟動Merchant、TYPE=DIRECT、
JOBRET=SUCC，走原件成功結果頁。原context的延遲Dispose／Close只清理，不再
選職或重開結果頁。招募員與指導員同時最多一個Merchant run，避免共用全域
互相覆蓋；離開遊戲清除所有對話權限，重登從持久紀錄生成JOBALD。

## 配置、資料保存與證據限制

指導員目前為顯式Development配置，驗目錄、地圖位置與Script／素材SHA。
暫沿用已確認可見的helper外觀0x4037及100%動畫速度，**不是已找回的原版
就職指導員造型或座標**。本輪沒有將候選Map7預設啟用為學校，也沒有修改
使用者執行中的Server。配置入口完整接到TCP session，但需後續完整教學配置。

World v6增加career-v1擴充表，以character_id唯一保存職業key、rule revision、
admission revision與時間。既有含帳號的file-backed SQLite缺少此表時，在建表
前建立一致性備份；重複初始化不再備份。PostgreSQL本輪仍未實際執行。

驗證：300項合成／SQLite測試通過，包括五職業、取消重開、錯誤名稱拒絕、
未入學拒絕、重送冪等、原結果頁啟動、遲到關閉、不升級畢業、重登讀回、
位置過期、loading禁寫、改職業／改rule拒絕、owner替換及缺表備份。
合成測試NPC／地圖不是原版綁定證據；尚未由原生Client實機驗證選職介面。

完整教學仍未完成：尚缺生活／戰鬥教學NPC與可玩戰鬥、地圖用途綁定、
數字職業／狀態投影、已選職傳送師、各職業城鎮及最終完成交易。以上不得用
本輪測試代替驗收，既有原始Client CT維持未通過狀態。
