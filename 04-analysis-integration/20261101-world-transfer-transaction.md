# 在線切圖持久化交易

**使用者需求**：先完成接受教學、下一場景、後續教學／選職及進入新手城鎮，
再安排一次完整人工測試；不要每個中間步驟都要求重跑。這是最新測試安排，
不是Client程式推導的要求。NPC動畫與對話頭像已由使用者確認正常。

## Server合約與信任邊界

目前已實作持久化核心，尚未接Host在線傳送。intent由Server產生，包含epoch、
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
   保留最後已提交位置。重連需按該位置選載圖內容，Host此部分仍待接線。

內部epoch不塞進原生C35；C35仍只有兩個u16。每socket至多一個pending，
Host還需依目前階段及TCP處理順序判斷回覆，不能宣稱Client回報了epoch。

## Schema與驗證

既有World v6增加transfer-v1描述表，epoch FK連至既有load attempts。
已有帳號的file-backed SQLite在新增表前建立一致性備份，重複啟動不重複
遷移；既有帳號／位置／進度保留。PostgreSQL此輪未實際執行，部署前的
備份與資料庫實測仍須獨立完成。這不是對使用者運行中Server的在線遷移。

286項Server測試通過，新增涵蓋入學前置、loading禁移動、單pending、
錯checksum、逾時／棄置、替換owner、竄改spawn/context、重播、重啟讀位置、
首次checkpoint不變及備份還原內容。這些是合成／SQLite交易驗證，不是原生
Client已成功切到學校或城鎮。下一步仍是Host、地圖角色綁定、選職與完成提交。
