# 離開角色後，同一Client登入卡住

## 使用者回饋與範圍更正

使用者確認上一輪「提示正常、兩次都能退出，重登位置正確」，接著
補充：按「離開遊戲」回到登入頁後，再登入會卡住。必須區分關閉／
重新啟動Client的重登、同一Client回登入頁重登；先前通過不代表後者。
空白提示及快捷列初始化修正已獲診斷副本實測確認，不升級原始Client CT。

本輪診斷Client SHA `874c83db4840af6db584c1814fdda107e02713f0bb26204a3c6decec9b0fc3ef`，
Server fd3ffeb。本地16:57:47、16:58:14、16:58:39、16:58:58 UTC+8都
收到WorldReady C0B/body0並由Server以expected-client-quit關閉TCP。
紀錄中未看到卡住操作所產生的後續C03；不能宣稱已觀察它在網路上送出。

## 原生Client路徑

原件SHA沿用 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

- MapPane0x4BE2B0：送CQuitPacket後清理世界物件，再於Region3呼叫
  MainMenu(1,0)，重建LoginDialog。
  `ev_c11307638427d3d480208c1b8595be70fd915d05d40542dbf29abfb1931ca759`。
- LoginDialog event4送出路徑0x4A7D10建立C03、讀帳密widget並排入傳送；
  該producer沒有重新連線動作。
  `ev_ea1822d54fc19581c4f70b1f664557cd1110ebc437a23a5f096a9504027ca3b9`。
- Region3 S03 handler0x4A8370才明確要求連上交接端點，然後送C10與C25。
  `ev_4e7784abc8f9c1e089e57fd2a070c52cb3053b6139ca593f75b2e3aec0a5b0c1`。

結合Server主動關閉紀錄，保留C0B後的登入通道是本輪相容設計；這不
代表已還原原服全部logout／斷線／重新認證規則，也不以靜態負面搜尋
宣稱整個Client絕無任何其他重連機制。

## 更新後Server合約（取代舊C0B關閉策略）

1. 只接受native profile、現行授權WorldReady的加密C0B，body恰0bytes。
2. 以account、character、generation、connection精確比對撤銷世界lease；
   若已被新登入取代，不可撤銷新lease，舊socket應拒絕。
3. 退場景、清除此socket的World身份、載圖、位置快取與腳本context，
   保留已持久的位置、首次入場、Born確認與教學進度。
4. 保留同一TCP與封包ordinal串流，切回LoginReady／FormInput期限；
   產生新的內部login generation。不送猜測的quit ACK，不把退場視為
   已重新登入，不讓舊World權限繼續使用。
5. 後續同socket C03重新驗證密碼、帳號狀態與角色歸屬，失敗仍以正常
   登入錯誤回覆；成功發S03單次交接，新socket C10/C25/C35才可再進場。
6. 使用者直接關閉程式時則以TCP EOF結束傳輸。不得把所有C0B都當成
   需要關閉程式／socket，亦不得無條件忽略所有未知封包。

無資料庫schema遷移。lease撤銷需與位置寫入的同一authority fence相容，
過期logout不能撤銷新連線。斷線後的全套重連策略仍另列，不由此推定。

## 驗證

私有實作追溯roy `7c35793`；265項Server測試通過，包含C0B清除世界權限、同socket錯密碼再正確
C03、S03／新C10進場、過期lease刪除不影響新lease、已撤銷lease不能
再寫座標。真loopback HTTP/TCP也通過同socket C0B→C03、新交接及
位置恢復，與創角／Born／移動一併驗證。

待使用者原操作驗收：不關Client，連續至少兩次「離開遊戲→登入→進圖」
並確認位置；最後直接關視窗確認不當機。這仍為診斷副本驗收，原始
未修改EXE正式CT維持not-run。
