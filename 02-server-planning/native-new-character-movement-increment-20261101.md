# 新角色直入世界與權威移動增量

## 目標與來源

使用者目前目標是「創新角色能進入新手教學移動」，並授權直接開發、
將分析／規劃同步公開 spec。此增量承接 ADR-008；以下自動交接、速度、
碰撞與儲存策略屬於 Server 設計，與 Client 已證 wire 分開。
map_ref=6 是目前已可顯示的試驗場景，**仍未證為原版新手教學地圖**。
新手腳本／NPC／真正教學場景身份未因此完成。

## 創角完成後自動交接

1. 管理端建立 Account；Client NewUser 使用 C02 的既有帳密驗證，沒有
   C03 也不等於未驗證。NAME/外觀仍由玩家選擇。
2. C02→S02(0) 只建立草稿；C04 以同一 owner/generation/credential version
   原子提交 Character 與外觀。未提交前不發 World grant。
3. 額外開啟 Development/Region3/NewUser/native-map 試驗開關時，提交後
   再驗證 credential version／帳號狀態，發 **S02(0)→S03**，正常結束
   舊 socket。使用既有短效單次 token，綁定 Account、剛建立的 Character、
   issuer generation 與目的埠；不把 C02 欄位當 bearer token。
4. 原生 Client 接 S03 後建立新 TCP，以 C10 帶 token，再送區域3 C25。
   Server 通過 owner／lease 後 S02/S05/S15/S14(1)→C35→持久提交→
   S04/S33/S14(2)。不等待玩家再次手動送 C03。

靜態依據：A-028 顯示第二段 S02(0) 後 Region3 建立 LoginDialogPane；
本次 REA 原始 EXE `0x4A8370` 顯示其 S03 callback 依目的端點連線、
成功後送 C10，Region3 再送 C25，未在此函式發現必須先送 C03 的 guard。
證據 `ev_4e7784abc8f9c1e089e57fd2a070c52cb3053b6139ca593f75b2e3aec0a5b0c1`。
這支持 **可實測的 Server 設計候選**，不證明原服首次創角就是此順序。
需要使用者 GUI 實測此時序與 UI callback；若失敗依實際封包／畫面修正，
不可退回要求人工第二次登入而宣稱達成 ADR-008。

## 逐步權威移動

- C54 是路徑意圖，不能直接採用 start/destination 當權威位置。C11 僅更新
  合法方向；目前不發明自身 S11 ACK。
- C33(direction,seq7,mode) 每步由 Server 的目前位置計算下一格。
  `0x557AC0` 以 `0x4431E0` 求方向並直接寫入 C33，八向順序為
  北、東、南、西、東北、東南、西南、西北；本次沿用已記錄的原始偽碼。
  mode 為1/2，可能 OR0x80；不得推導成未證的加速倍率。
- 試驗地圖 archive/member SHA 嚴格比對；MAP 八byte檔頭後略過
  `ceil(width/2)*ceil(height/4)*2` block bytes，每tile十bytes，+6為原始flags。
  本試驗 **Server 設計**：目的 bit0 擋路；bit3 所需的方向遮罩來源未完整
  取得，遇到該類格保守拒絕；越界拒絕；斜角要求兩側正交格也能站立。
  不把 Client raw flags 偽裝為已驗證的動態 NativeMemoryTile。
- 此 profile 尚未建立會移動的 Server NPC／玩家碰撞 overlay；不能宣稱
  完整原服動態碰撞已完成。後續 Actor 系統需把佔位／加減 flags 納入。
- 操作者明示設定步伐下限，試驗入口選 **100ms**，以 monotonic clock
  計時；是 Server 設計值，不是逆向得出的原服速度。第一步可立即走。
- seq7 重送回相同快取 ACK，不能重複寫位置；衝突重送／跳號拒絕。
  太快、碰撞、無效方向／mode 回 S0B(目前座標,seq,bit7=0)，消耗該序號。
- 合法步伐先以 lease＋位置版本 CAS 寫入，再回 S0B(新座標,seq,bit7=1)。
  資料庫失敗不能先回成功；新登入會使舊連線無法再移動。

## 持久化與遷移

首次進場 checkpoint、tutorial_entry_committed 與首次 outbox 保持不變。
另建 mutable current-position，鍵為 Character，保存 map_ref、content revision、
x/y、facing、單調遞增 version 與更新時間。重新完成相同地圖 C35 後，
優先以目前位置送 S04/S33；不同內容版本不可套用舊位置。

寫入 CAS 同時檢查當前 Account/Character/generation/connection lease、
已有 committed map load、原先 map/revision/position/version。一次步伐
最多鄰格，不能從 Client 座標任意 teleport。轉向同樣保存但不變更 x/y。

schema v6 新增位置表，v5 的 email/帳號/角色資料保留，所有啟動元件接受v6
並避免降版。SQLite 有既存帳號資料時，升級前以 SQLite backup API 寫
`<db>.pre-world-v6-<unique>.bak`，失敗停止升級；新隔離空DB免備份。
備份在 migration transaction 前執行，以免來源交易鎖造成 SQLITE_BUSY。
PostgreSQL SQL 支援另列待實機驗證，既有部署升級前應有營運備份。

## 驗證範圍

單元／SQLite整合與本機真HTTP/TCP涵蓋：創角持久後才發grant、單次token、
完整C02/C04→S03/C10/C25/C35、有效步伐、牆／角落／邊界／mode／速度、
重送不多走、舊連線隔離、首次checkpoint不變、重登讀目前位置、v6不降版
與既存資料備份。它們不能取代 Client 真正創角自動進場／行走畫面驗收。

使用者下一輪應一次驗證：創角選外觀→直接進場→步行多格→靠牆／邊界→
關閉Client後以同一測試Server的一般登入入口重登，確認位置與面向保留。
測試Server每次重跑建立新DB；要測重登不能重建Server。

## 本輪補證與測試結果

REA `0x4430C0` 直接回傳八方向的單格 delta，方向8為(0,0)，未在此
helper 發現依 mode 乘倍數；`0x4431E0` 是相反的向量取方向。
`0x556E30` 初始化 UserObject+0x534=1，路徑 producer 再於1/2間切換。
證據：`ev_1e16b65a9e136f5f437dcca4b2bfd2f96d58014f2879db0857c743584ea2753a`、
`ev_5698ad70ad4097320070a2768726deb04fdbfe9f9629f1457cedf58f03e83a86`、
`ev_41b26568e32962cb4673e85d41803de54649858c70e0b44801e2eedcc08bbbb9`。
這些是原件靜態補證，實際行走畫面仍需驗收。

完整255項Server測試通過；真loopback HTTP/TCP額外一次測：錯密碼拒絕→
實驗generic S02→C15重試→C02/C04成功→S03/C10→C35→C54→成功步伐→
重送不多走→錯C35拒絕→重登讀取保存座標。NewUser／一般登入啟動器的
billing模式、PowerShell語法與不保存密碼亦驗證。PostgreSQL原生執行未驗。

使用者第一次NewUser畫面停在登錄中；實際Server只收到C02並拒絕帳密，
沒有C04。截圖ID看似漏掉worlddemo的l；已請使用者於同一仍開啟的試驗
修正ID重試，不要求提供密碼。因此這輪不能判定自動進場callback成敗。
後續新試驗開啟既有Development-only的generic failure S02候選，改善
錯誤後C15重試流程；原生訊息是否顯示仍需實測，不能宣稱完整錯誤UI已驗。

私有實作追溯：roy `399f09e`；程式碼不隨公開規格提供。
