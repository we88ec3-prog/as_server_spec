# 創角後條件式 C03 與 S03 分派補證

本輪核對原始 EXE
`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，
以 REA／Ghidra 12.1.4 讀取原件。這是靜態補證，不是實機 C04 之後的
封包紀錄。Server 既有主動 S02→S03 試驗仍須 Native GUI 驗收。

## 可確認的呼叫鏈

1. `0x4B1D60` 的 final S02 成功分支，Region3 會建立 LoginDialogPane
   `0x4A9380`；仍不等於玩家必須手動再輸入帳密。REA
   `ev_c238a648583068de57ecea29258fd05b7bab9889f1b239501bac926016f04ed9`。
2. `0x4A9380` 尾端檢查記住的 ID／password 欄位是否都非空，並以
   `GetAsyncKeyState(VK_CONTROL)` 判斷 Ctrl 未按住。條件成立時呼叫
   `0x4A8950(event=4)`。REA
   `ev_3e331042d2818fa5bb76a1addb34bead6f4973d72907b6405d685b5071dbe4be`。
3. `0x4A8950` 的 case4 建立登入等待物件後直接呼叫 C03 sender
   `0x4A7D10`。REA
   `ev_929aabe6d5854f2ed4672d1f9a5ffd228e758a00e6aeb64b5ffbf9ef1f34d945`。

因此不能只因 constructor 本體沒有直接 CALL `0x4A7D10`，便解讀成
「建立此 pane 不可能自動登入」。現在可證**條件式自動 C03 路徑存在**。
但首次創角完成當下這兩個快取欄位是否非空、是否就是剛建立角色的帳密，
以及鍵盤條件，仍未由 Runtime 證實。本次不讀取任何使用者快取帳密。
這也不是「所有新角色必然先送 C03」的證據。

## S03 不以已發 C03 作此分派的前置條件

`0x4A9670` packet/event dispatcher 的 bounded bytes（0x70 bytes）由 REA
`ev_c16bc554a6f6b5c07996c5919e174a854659abc76b0b6639ef6568603936b8cf`
取得：它先讀 event packet 的 selector（packet+8），範圍檢查0..0x68，
再用 `0x4A96D8` index table 與 `0x4A96C4` target table 分派。

| selector | index | target | 尾跳轉 handler |
|---:|---:|---|---|
| 0x02 | 1 | 0x4A968D | 0x4A8D60（S02） |
| 0x03 | 2 | 0x4A96B1 | 0x4A8370（S03） |

這段 dispatcher 沒有再查「已送C03」狀態。`0x4A8370` 的 Region3 分支
則依 S03 目的端點連線，成功後送 C10、C25；見既有
`ev_4e7784abc8f9c1e089e57fd2a070c52cb3053b6139ca593f75b2e3aec0a5b0c1`。
這縮小主動 S03 候選的 UI 前置條件疑慮，仍不能取代 pane 註冊、事件
排程、TCP 切換與實際原生封包順序驗收。

## 排程邊界與 Server 實作含意

`0x5788A0→0x53B3E0→0x54BA50(command7,packet,0)` 把送包交給通訊命令
佇列；`0x53B300` 以同一入口提交 command3 連線命令。證據
`ev_b223ef224f6e29edbb5d2cdb425d010ca4c3fd320adbe383a080255c615f3d4a`、
`ev_b8bdd26af013fb6de02370c0541239681b824042a24a868fca9a0b3b5cb096e6`、
`ev_6f998e1dc4f148ac5c4f187dce988f46f0abb55d27c031cfa66be84a57549e99`、
`ev_7e5e2c163340245636b2dbc4d351a3ab00e1d375ca32975bc8138cfabcd2b6d4`。
尚未完整驗證消費端排程，不能從 enqueue 本身斷言所有命令已送出，
或自動 C03 最終一定在哪條 TCP 上。

目前 Server 在持久 C04 完成後主動 S02→S03，再正常結束舊連線，
目的是滿足使用者不需二次手動登入的需求。若 Native 重測失敗，需區分：

- C02 帳密拒絕、尚未收到 C04：不屬於 post-create 分派失敗。
- C04 已提交但沒有 C10：查 LoginDialog 建構／S03 route／是否崩潰。
- 同時出現自動 C03：記錄其舊／新 socket 與 S03/C10 時序；不能把它
  當作使用者違反流程或直接套成原服唯一成功順序。
- C10 已到後才失敗：查 grant／C25／C35／後續 World，不倒推成創角失敗。

本輪沒有更改 Server 或 Client 時序，也不添加猜測延遲。原始 Client
實際創角後自動進場、行走與教學地圖身份仍待使用者驗收／提供線索。
