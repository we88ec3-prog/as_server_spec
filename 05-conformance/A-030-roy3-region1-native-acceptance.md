# A-030 CT-104 原版 Client GUI/TCP 驗收 — Region1 mismatch、空 EMAIL、S02/C15

狀態 planned / not-run。本報告提供手動原版 Client 測試步驟，不表示已運行。原始 EXE SHA db3df616...729e1145，同版 Basic.dat/Locale.dat，合法測試 Server，紀錄去敏封包及 TCP 事件。

|Case|操作|需保留的結果|
|---|---|---|
|R1|Region1 修改 widget15／widget16 個別值|比較 C02 第三 string8 長度與匿名 hash 差分；UI +624 vs writer +424，不能先猜空|
|R2|Region2/3/4 只改 NAME、只改 EMAIL|F3/F4 各自變動，驗四 string8+flag|
|R3|Region2/3/4 留空 EMAIL 送出|是否本地阻擋、進確認 popup、送 field4 len0、或不送 C02|
|R4|state1D 給 S02(status1,非空 message)|原版 GUI 真訊息、C15 empty、local state1F、TCP close origin。status1 僅合成候選|
|R5|state1D S02(status3/17,非空)|第一／第二欄 focus 及 C15 實測|
|R6|Region3 state1E S02(status1,非空)|驗文字抑制例外，不推定 dialog|
|R7|C15 後同 TCP 再試/或重連|精確 C02/C15 帧、Server FIN/RST、client retry 動作|
|R8|創角兩段 S02(0) 後直接入 World|C04→後續真封包 S03/C10/C25 依 A028/A031，不手動再 C03|

記 Client/資源 SHA、region、seed、去敏欄位長度/ordinal、S02 status/msg、GUI 截圖及連線時間。不能提交明文密碼、EMAIL、完整 token。原件靜態 34 anchors／11 offline tests 的 PASS 不算 GUI 通過。
