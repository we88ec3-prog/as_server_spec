# 原生角色能力初始化與持久狀態

本輪依[能力窗當機回報](20261102-personal-account-admin-and-status-window.md)補上 Server 已確認缺少的 S08 投影。**已完成狀態初始化實作與 Server 驗證；尚未證實滑過職業／稱號不再當機。**原件與診斷副本沒有因本輪變更而改寫。

## Client 證據與欄位來源

原始 Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，REA/Ghidra 12.1.4。`0x586d40` 是 S08 reader，`0x53f8a0` 將 packet 寫入 Status singleton，`0x540050` 按控制項 ID 刷新可見數值。讀取次序承接 [A-008](../task_a/roy2/A-008-analysis.md)。reader 的 this 相對完整 Packet 有 +0xc 調整，不能把本地物件 offset 當作 body offset。

|可見數值|Status offset|UI child ID|本輪完整 body offset|
|---|---|---|---|
|等級|0x41c|1|3，u8|
|HP 上限／目前|0x420／0x478|0x0e|4／63，BE u32|
|MP 上限／目前|0x428／0x47c|0x0f|8／67，BE u32|
|SP 上限／目前|0x430／0x498|0x10|12／71，BE u32|
|BP 上限／目前|0x438／0x480|0x11|16／75，BE u32|
|STR／CON／INT／WIS／DEX|0x448／0x44e／0x44a／0x44c／0x450|5／6／7／8／9|30／33／31／32／34，各 u8|
|FAME／TEND／BELIEF|0x452／0x458／0x460|2／3／4|35／40／45，各 signed u8|
|FAME EXP／TEND EXP／BELIEF EXP|0x454／0x45c／0x464|0x0b／0x0c／0x0d|36／41／46，BE u32，以 signed 顯示|
|EXP|0x484|0x0a|79，BE u32|
|獨立稱號文字|0x210|0x1a|100 為 string8 長度，101 起為 CP950 bytes|

這張表只適用本輪 flags 0x0078 的全量組合，不能套到刪減區塊的 S08。職業名稱 child 0x19 另由自身外觀 class byte 加 BasicString ID 455 取得，Mage=3 顯示魔法師；不由 S08 Title 或能力值決定。

後續已追出[預言者為階級徽章](20261102-occupation-rank-badge.md)：child0x1b由signed FAME=-52選到occupation.ypf object7/frame2，與截圖圖像相符。它與上表的child0x1a獨立稱號文字不同。BasicString448雖同名，並非這條徽章選圖路徑來源；不得直接解釋為選職被改成別的職業。

`0x53f510` 建構子僅初始化部分 Status 欄位，先前未送 S08 的情況不能依賴這些欄位已有合法值。`0x4cebc0` metadata 載入失敗路徑另列待查，仍沒有證據證明本次 hover 卡死就是 metadata 遞迴；未宣稱 Windows 更新所致。

## S08 全量初始化契約

僅在受支援 native World 內，C35 已通過、World lease 與角色 owner 有效且地圖交易提交後，依序送 **S04 → S33 → S08 → S14(2)**。後續既有初始普攻、NPC、BGM、怪物與 Born 紙張仍按原流程發送。每次初次進圖、在線轉圖及重登都使用同一持久狀態。

flags 為 BE u16 `0x0078`。區塊依序：0x40 full 61B、0x20 current 16B、0x10 secondary 16B、0x08 five bytes+string8。空稱號時 body 共 **101B**。

|body offset|長度|本輪欄位或政策|
|---|---|---|
|0|2|BE flags 0078|
|2|1|skip/reserved=0|
|3..19|17|等級與四組最大資源|
|20..29|10|未映射欄位明示零，不冒稱原服語意|
|30..49|20|五能力、三聲望與相應經驗，次序見上表|
|50..53|4|顯示顏色位群=0|
|54..62|9|餘點與未映射欄位=0；不要求改 NewRowCount／快捷列配置|
|63..78|16|四組目前資源|
|79..82|4|EXP|
|83..94|12|secondary 四個 BE u16 與最後 BE u32，目前零|
|95..99|5|text 區塊屬性，目前零|
|100..|1+N|string8 byte 長度與 CP950 文字|

本輪沒有啟用可分配能力點、C47 加點、成長、玩家受傷、MP/SP 扣除或裝備加成；不得因欄位已能顯示就聲稱上述玩法完成。C47 原生 wire 研究仍可供後續開發，加點按鈕依零餘點隱藏。

## Server 出生與資料政策（設計，非原服分析結論）

持久 revision `tutorial-status-baseline-v1`：等級 1、五能力各 3、HP/MP/SP 為目前 100／最大 100、BP 0／0；EXP 與三聲望及其經驗為 0。未取得稱號時文字為空，不替角色杜撰已獲稱號。五職業共用此重建基線，職業碼仍來自既有持久選職。

新增每角色一筆狀態記錄，含 CharacterId、PolicyRevision、能力／資源／經驗／聲望／Title，外鍵對角色。新增角色與舊角色第一次成功進圖時以 insert-if-absent 建立；**後續投影不覆寫、回血或重置原有記錄**，也不根據 Client 畫面值回填 DB。這是權威狀態，不是為狀態窗臨時拼出的假 HP。

狀態讀取／建立要求當前帳號、角色、World generation、connection 與 committed map load。舊 socket、其他帳號或尚未提交地圖均拒絕。舊資料不合法時明確拒絕，不能用預設值悄悄蓋掉。未來傷害／成長需另外實作交易性狀態更新，不得以重新登入初始化代替。

此為既有 World v6 的附加資料表：缺表且 SQLite 已有帳號時，遷移前使用 SQLite 一致性備份；保留原角色、位置、選職、教學進度及管理金鑰。表存在後再次啟動不重複建立備份，不改既有狀態。PostgreSQL DDL 維持相同資料契約，但本輪未執行 PostgreSQL 整合測試。

## 驗證與待測

- 384 項 .NET 測試通過：包括獨立 native body offset／BE 位元組／能力次序／signed 聲望／CP950 byte 長度、資源超限拒絕，及真正 SQLite owner/load fencing、重登不重置、缺表先備份與重跑冪等。
- 使用實際 MAP／腳本內容的五職業 TCP 完整路線通過；每次學校／城鎮載入與重登均核對 101B S08、資源及能力基線、EXP／聲望零值與 ordinal。是 TCP emulator，不是 GUI。
- 隔離的固定開發環境啟停、帳號／角色／位置／端口／管理金鑰保留、重複啟動拒絕及明示輪替測試通過；沒有輪替使用者目前的金鑰。
- 新增只讀診斷選項可在特定 SHA 相符 Client PID 擷取已證 Status 數值及「稱號是否空白」布林；不讀取稱號全文、帳密、封包 body，不注入或寫入 process。

仍須人工一次驗證：既有 Mage 城鎮角色重登→打開能力窗→數值正常、上方仍魔法師→滑過職業、稱號、能力值→走動→同 Client 離開遊戲再登入→正常關閉；新帳號亦須確認創角與狀態獨立。若再卡住保留 Client／Server，讀取當下 scalar 而不是把本輪 Server 測試當成 hover 已修復。五職業原版城鎮配對尚未全部證實，整體目標保持未完成。
