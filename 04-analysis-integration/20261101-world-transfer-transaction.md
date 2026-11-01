# 在線切圖持久化交易

**使用者需求**：先完成接受教學、下一場景、後續教學／選職及進入新手城鎮，
再安排一次完整人工測試；不要每個中間步驟都要求重跑。這是最新測試安排，
不是Client程式推導的要求。NPC動畫與對話頭像已由使用者確認正常。

## Server合約與信任邊界

目前已實作持久化核心及Host同socket切圖處理；正式教學目的圖仍未綁定。intent由Server產生，包含epoch、
來源位置／version、目的map/revision與出生點、origin與授權關聯ref、期限。
不能直接將Client送來的map/xy轉為intent；origin列舉與ref字串本身不授權。

TutorialAdmission來源需在交易中核對角色對應的持久入學事件及revision；
其他Npc/Skill/Admin/MapGate由來源業務另驗對話context／距離、技能資格或
管理權限後呼叫核心。核心另外一律驗當前lease／generation／connection。

## Begin、載圖及提交

1. 鎖定當前角色World owner，要求已完成目前載圖、無其他pending載圖，
   source位置／map revision／version必須與資料庫完全一致，epoch不可重用。
2. 同一交易保存pending load及完整transfer描述；未收到匹配C35前不移位置。
   此時可讀上次已提交位置，但移動／要求已提交載圖的狀態寫入會拒絕。
3. 提交需C35的map_ref/checksum與目的內容一致，並比對保存的完整intent、
   owner、期限、舊位置version。參數或目的地被換掉、舊連線、重播均不提交。
4. 同一交易將pending改committed、新位置及version+1、每epoch唯一outbox
   事件一起保存。首次入場checkpoint維持原值，不因切圖改寫或標畢業。
5. 逾時／錯C35未提交可棄置該epoch；新World owner會將舊pending改abandoned，
   保留最後已提交位置。重連按該位置的map/ref及revision從可信目錄選圖；
   內容缺失、版本不符或保存位置不可站立時拒絕入場，不退回第一張圖。

內部epoch不塞進原生C35；C35仍只有兩個u16。每socket至多一個pending，
Host依目前階段及TCP處理順序判斷回覆，不能宣稱Client回報了epoch。

## Host封包與對話接點

以下是復原Server實作政策；S15／S14／C35／S04／S33格式沿用已有Client分析。
目前只對Server已配置的入學目的圖開放此來源，沒有Client任意指定map/xy的入口。

- 已發行Merchant context、近距離合法ACCEPT先寫入學事件；等原生runner的
  C6C subtype4 Dispose才開始切圖。REFUSE、只有TALK或尚未Dispose不切圖。
  接受不等於畢業；目的圖未設定時保留既有入學行為。
- WorldReady轉WorldLoading，同一socket送S15目的圖及S14(1)。不用第二次
  C03/C10登入，也不重送S02完成提示或S05初登入資訊。
- 匹配C35提交成功後送S04位置、S33自身外觀、S14(2)，按目的圖設定送S19。
  首次出生checkpoint保持不變；目前位置獨立保存。Born與招募員不跨圖生成。
- 載圖期間合法的舊C33/C11/C54/C44只解析／丟棄，上限64次；不寫位置、
  不回舊座標ACK。已處理Merchant context的遲到Dispose／Close可忽略，
  其他context或不符階段的控制仍拒絕。C43另沿既有載圖查詢預算處理。
- 舊C33序號若連續就推進保留序號；C35後清舊ACK快取與移動節流時間。
  第一個新圖移動允許sequence歸零或延續當前expected sequence，之後恢復
  正常序號與重播檢查。**這是相容政策，尚未證實原生切圖必然重設序號。**

## 多圖內容與設定邊界

可信目錄的key為map/ref及內容revision，含載圖fixture、可行走規則與可選BGM。
重登載入已提交地圖前，資料層核對目前位置及歷史已提交載圖的map/checksum
來源；不能用第一張圖的checkpoint覆蓋目前地圖，也不能藉改checksum造新版本。

本地Development支援明示額外地圖：逐圖提供archive/member SHA256、map/ref、
標題、spawn、viewport、facing、flags、fieldD及移動間隔；地圖尺寸與C35 checksum
從已驗證原件計算。缺欄、重複map/ref、阻擋出生點、素材不符會在啟動時拒絕。
BGM按圖獨立驗證，不能挪用來源圖的revision。招募員目的地必須精確指向目錄版本。

明示候選綁定不等於原版角色證據。此輪沒有將任意Map7或城鎮候選設定成正式學校；
測試用的map7、checksum BEEF及school命名都是合成fixture，不能引用成原件發現。

## Schema與驗證

既有World v6增加transfer-v1描述表，epoch FK連至既有load attempts。
已有帳號的file-backed SQLite在新增表前建立一致性備份，重複啟動不重複
遷移；既有帳號／位置／進度保留。PostgreSQL此輪未實際執行，部署前的
備份與資料庫實測仍須獨立完成。這不是對使用者運行中Server的在線遷移。

291項Server測試通過，持久化涵蓋入學前置、loading禁移動、單pending、
錯checksum、逾時／棄置、替換owner、竄改spawn/context、重播、重啟讀位置、
首次checkpoint不變及備份還原內容。Host新增涵蓋同socket接受／Dispose切圖、
序號歸零與延續、丟棄舊圖移動、重播不重寫位置、錯C35或斷線保留舊圖、
成功後重登留新圖，以及多圖素材與出生點設定驗證。

這些是合成Host／SQLite驗證，不是原生Client已成功切到學校或城鎮。
尚缺原版地圖角色綁定、後續教學NPC、選職、戰鬥與畢業／出城提交；
完整「創角→完成教學→各職業城鎮」仍未完成，原生CT狀態不因本輪測試升級。
