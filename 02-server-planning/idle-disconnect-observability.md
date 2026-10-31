# RI-005：程序存活與遊戲連線的分離、閒置斷線診斷

2026-10-31 本地回報整合；**root cause=unknown**，沒有變更 Server。對應 A-020（Client 前置／相容性）、A-016（恢復設計）；與 A-030 的創角斷線暫不合併為同一根因。

## 本次可確認與無法確認的事

|類別|內容|
|---|---|
|Client 身份|主選單預覽修改副本，SHA256 `e834a07d21807748561bafa7e9cca97195234a9b664ea9c20f9e83faafc8cb9d`，PID 29780。不能據此聲稱未修改 Client 的結果。|
|程序監測|2026-10-31 23:24:51～23:25:21（UTC+8），每約3秒共11筆，Responding 都是 true，工作集約85～88 MiB。沒有同時取得 TCP 或 UI 狀態，故不代表「仍連線」或「沒斷線」。|
|使用者觀察|回來看畫面時已顯示斷線；忘記斷線前畫面，之後手動關閉遊戲。未取得提示原文／時間或畫面。|
|後續查核|約23:26，Client PID 已不存在；Server PID 6400 仍監聽 localhost:15010、18080，沒有已建立的遊戲 TCP 連線。因使用者關閉 Client，不能把 PID 消失列為 crash。監聽 socket 只證明 listener 存在，不證明每一會話正常。|
|實作靜態快照|唯讀 `as_server_roy@b8e212e` 的 GameTcpProbeService：連線開始設60秒讀取期限，每次 ReadAsync 返回非零資料重設60秒；處理後仍在 WorldLoading 會再設20秒；非停機取消共用 reason=idle-or-load-timeout。這是現有實作的 designed timeout，不是原服規則或本次 runtime close 證據。|
|缺口|不知最後 UI／phase、最後收發時間與 opcode、實際關閉時間、FIN/RST 主動端及 close reason。未取得本次 Server console／既有持久日誌；不能倒推先前內容。讀取的 source commit 也不能單獨證明執行中的 binary 就是該版。|

本地原始資料留在 `workspace/anal-roy-temp/runtime-monitor/`；不發布含會話細節的 raw log。整合者已在本地保留 binary SHA／修改時間作後續比對，未修改或重新啟動 Server。

## 給 Server 開發者的增量合約（designed）

這是對既有狀態／逾時規格的補充，不要求關閉全部 timeout，也不以延長60秒宣稱已修復本次問題。

1. **三種狀態分開**：程序／視窗回應、TCP transport、協定會話 phase／Client 可見狀態。OS Established 不代表 Client 已登入；顯示斷線也不代表 UI 執行緒卡死。
2. **逾時按階段明示**：handshake、登入／創角等待輸入、WorldLoading、InWorld 分別記錄 idle 與 absolute deadline 的政策、預設值、設定來源和可重設事件。表單輸入時間不應無意套用載入 ACK 的短期限；若允許的操作時間超出目前60秒，須修正階段政策再驗收。期限具體數值由 Server 規劃／設定定義，原 Client 的 heartbeat 存在與否另以證據確認。
3. **不要杜撰保活封包**：TCP keepalive、收到 TCP bytes、成功解析有效 frame、合法會話動作與 Client 原生 heartbeat 是不同事件。要明示何者重設期限；不以無效碎片流永久延長合法會話期限。若需接 heartbeat，先交 Client writer／handler、格式及階段證據，再接 Server，不能為防斷線發未知 opcode。
4. **一次關閉一筆可歸因摘要**：具 UTC 時間與 traceId、Server build identity、phase、最後有效 C2S/S2C opcode／length／時間、套用的 timeout 類別／設定值／elapsed、close origin。分開 idle deadline、load deadline、host shutdown、peer EOF、IO／socket failure、protocol rejection 和 expected transfer；不要只保留合併 idle-or-load-timeout。正常 S03 轉服的舊 socket 關閉不得誤判遊戲斷線。
5. **監測不干預狀態**：讀取日誌不發遊戲封包、不為保持連線模擬使用者操作。不得自動重連而抹掉首個失敗；Server 在終止時按既有 owner／generation／epoch 規則清理 pending，不刪其他連線或已提交角色。
6. **資料最小化**：不記帳密、CONFIRM、Email、解密正文、credential hash、token；連線／帳號以匿名關聯。提供本地可讀去敏診斷出口與保留期限，避免只存在難以回收的 console。這是待開發合約，不宣稱目前已有此出口。

## 一輪回驗清單（planned，尚未執行）

- 先記 Client SHA／修改狀態、Server binary／source 身份與啟用的各階段期限；同步取樣程序和連線，保留 Server 去敏 close 摘要。
- 在已辨識的主選單、登入輸入與創角表單各測：短於期限、接近期限及跨越期限；中途有合法動作時按已記錄的重設政策判定。兩分鐘停留可作比較窗口，但不代表所有 phase 都強制允許兩分鐘。
- WorldLoading 缺 ACK 的超時與正常 ACK 分開；進圖後靜止與正常移動分開。關閉／重新連線的提示、phase 和 Server close 分類須可對上同一時間線。
- 測 Server 主動關閉、Client 手動關閉、真正程序異常退出、正常 S03 轉服；四者不得使用相同的故障結論。保活能力未知不得填 native passed。

通過條件：不再以 Responding=true 宣稱連線正常，每個斷線能關聯到版本／階段／明確原因；遊戲在允許的等待時間內保持預期狀態，超時依既定政策清理並可重新登入。RI-005 在取得根因及相同版本重測前維持 open。此清單補充既有 CT-103 的 H0 前置／逾時觀測；若實際失敗屬其他階段，回到該階段既有 CT，不能冒認 CT-103／105 已覆蓋或通過。
