# 創角後空白提示與首次退出當機

## 使用者回報及驗收範圍

2026-11-01，使用者確認上一版診斷副本可持續在線、重登位置正確。
另回報：新角色的Born歡迎紙張按OK後出現空白小框；新角色退出卡住，
一般登入可以正常退出。這是使用者實測回饋，不是原服規則。
本輪沿用e5f7b1ac…診斷副本及roy51bed5b的隔離試驗。

## 空白框的作用與Server合約

原始EXE SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，
Ghidra12.1.4，MakeInfo回覆handler `0x4B1D60`：

- state1D收到成功S02後產生C04，不能跳過這一個S02。
- 最終state1E、Region3成功後清除創角物件，建立LoginDialog；接著
  **無條件**使用S02.message建立MessageDialog（0x442570）。
- 因此最終S02(status0,message空字串)仍會產生空白提示。
  這個框是創角結果提示，與Born/PaperDialog是不同的UI。

證據 `ev_c238a648583068de57ecea29258fd05b7bab9889f1b239501bac926016f04ed9`。
靜態路徑與使用者兩張畫面相符；尚未取得兩個視窗的即時物件追蹤。

Server設計：初次C02成功S02維持status0、空訊息；持久提交C04後的
最終成功S02使用CP950 string8「角色建立完成。」。這是本Server選擇的
提示文字，並非找回原服原文。其後的S03/C10交接與owner授權照既有
契約，不可為省略提示而漏發UI清理所需的最終S02。

## C0B原生退出契約

| 證據 | 結果 |
| --- | --- |
| ctor0x574BA0，`ev_fb284639fe2d06c490dfa05e4e3359612f3e8bb199d8f898394da0624c620238` | CQuitPacket opcode0B |
| writer0x574C50，`ev_f83c12f38ff8fe9e6c7e98436822324d386f6cd68f94ec689164ef8b88fbb97f` | RET，空body；該入口未恢復成procedure，以精確bytes確認 |
| MapPane0x4BE2B0 | 送出後立即進行本地UI及物件清理；本次未證有等待Server退出ACK |

16:39:49新建角色及16:41:50、16:42:04一般登入退出，都收到WorldReady
的C0B/body0。舊Server誤記unknown-opcode並關閉；這一點不足以解釋
只有第一次退出出錯，不可把日誌分類修正當成Client當機已解決。

Server設計：僅已授權WorldReady、現行owner有效、native trial啟用且
encrypted body恰0bytes時，正常關閉TCP，分類expected-client-quit，
不發猜測的S2C ACK。錯階段／畸形body照常拒絕。位置在移動ACK前已
持久提交，退出不可覆寫成首次進場位置。C2S C0B與S2C S0B移動ACK
必須依方向區分。

MapPane退出呼叫證據：`ev_c11307638427d3d480208c1b8595be70fd915d05d40542dbf29abfb1931ca759`。

## 退出例外定位及Client相容性邊界

Windows Application Error於16:39:49記錄例外C0000005、診斷副本模組
RVA `0x15BC85`。以該固定版本ImageBase0x400000換算VA `0x55BC85`，
原始指令為讀取快捷列slot的DWORD，位於個人設定序列化0x55B820，
不是Born紙張或網路等待迴圈。

- 精確指令：`ev_66b46f61ce5fdc73bea1ca7f105b25fd5e1a7231ab9ef6655fa8b7d5fb03b6cd`。
- 序列化assembly：`ev_56c8462b8a8eac19be970ba9b845b25eb289c73a99d9191fa030e88a44237311`。
- 預設初始化0x55E140未寫profile+0x18快捷列數，卻清了row index等欄位；
  儲存按該u8列數讀取固定容量slot，沒有容量上限檢查。
  `ev_9dc2409d155f40542fbf631bdc099baa97a0e6b4a77b8a85aa06dfad277002c3`。
- profile reader0x55E3C0從有效設定檔讀取列數並檢查小於10；無檔／無效
  回退預設流程不保證此欄位定義。有效載入與首次缺檔可產生差異。
  `ev_3efcf9ef4dbd2f4ff1b4f91c6cf9382a8436c79b116bcde8c7c4000cc3b19c6b`。

以上支持「預設列數未初始化導致退出越界」診斷，但未保存當時register／
heap快照，仍須新副本GUI重測，不能宣稱所有退出當機都由此原因造成。
現有設定檔保留，不複製他人的設定、不刪使用者偏好，也不藉此變更
Server封包規則。這是Client相容性修正，不是所有Server必須修改EXE。

獨立診斷副本於預設初始化前補快捷列數1，保留被移動的兩條初始化
指令後返回。原件與舊診斷副本不覆寫；試驗入口預設選新副本。
新SHA `874c83db4840af6db584c1814fdda107e02713f0bb26204a3c6decec9b0fc3ef`。

## 實作及待驗收

私有實作roy `fd3ffeb`。265項Server測試通過；隔離本機HTTP/TCP涵蓋
錯密碼重試、短名創角、非空完成提示、自動進圖、Born回包、移動／
去重、重登位置及C0B正常EOF。副本建置檢查固定來源SHA、PE結構、
原始指令及兩條跳轉目的地；不等於實際執行驗收。

待使用者一次確認：歡迎紙張→有文字的創角完成框→移動→關閉是否
退出；同一Server重新登入、確認位置並再次關閉。原始未修改Client的
正式CT仍維持not-run，不能以診斷副本結果升級。
