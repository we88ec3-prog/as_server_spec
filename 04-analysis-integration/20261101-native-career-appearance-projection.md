# 原生職業名稱與S05／S33職業投影

日期：2026-11-01。接續[選職持久化](20261101-tutorial-career-advisor.md)及
[完整TCP路線](20261101-tutorial-route-tcp-evidence.md)。本輪讓已保存的選職
結果進入Client外觀資料；靜態及Server驗證不等於原生GUI已通過。

## 原件證據

EXE SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，
REA／Ghidra12.1.4。指令、素材SHA及evidence ID見[機讀證據](native-career-appearance-20261101.json)。
原始匯出留本地，不提交EXE／DAT。

StatusDialog更新函式0x540050取控制項0x19，呼叫0x479ea0將HumanInfo的40bytes
複製至stack+0x28，再讀stack+0x2d的byte，加0x1c7(455)，經0x498010取文字。
0x479ea0來源為HumanObject+0x284，因此是HumanInfo+5；不能猜成S08狀態欄。

Basic.dat SHA `0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`；
BasicString.txt位於190844、長14810bytes，UTF16LE BOM，member SHA
`fa92f7a3cf544ff9e141d98620943b362e2d3dcc6e327878a818ebaa6ac3123b`。

|HumanInfo class byte|BasicString ID|Client名稱|
|---|---|---|
|0|455|平民|
|1|456|戰士|
|2|457|盜賊|
|3|458|魔法師|
|4|459|聖職者|
|5|460|武道家|
|6|461|吟遊詩人|
|7|462|騎士|

6／7只證顯示名稱，教學仍只提供五基本職業；此表不是轉職／能力／裝備規則。
Server symbolic enum宣告順序不同，必須明示映射，不能cast enum值送Client。

## 封包到HumanInfo

|封包|decoded body offset|reader暫存|handler完整Packet欄位|HumanInfo|
|---|---|---|---|---|
|S05|5，u8|0x5895a0的this+0x1d|0x4f3830讀+0x29|+5|
|S33|10，u8|0x585570的this+0x25|0x4f31a0讀+0x31|+5|

reader this相對完整Packet有+0xc調整，不可直接把偽碼結構offset當wire offset。
本輪補名不改body長度、髮色、衣色或可選flags解析。

共用派送表S05 thunk0x4f48e8，JMP0x4f48ec→0x4f3830；S33 thunk0x4f48f1，
JMP0x4f48f5→0x4f31a0。S05入口缺Ghidra function定義，使用exact decoded
instructions核對：ESI+0x29→stack+0xd；profile位於stack+8，該byte為+5，
之後傳0x556e30建立自身物件。沒有杜撰缺失的procedure偽碼。

S05 handler移除／重建自身HumanObject，不能當作中途無副作用的文字更新。
S33同object分支經0x47ab70更新既有profile，並呼叫0x540050刷新StatusDialog。
0x47ab70內的0x47cf60是包含+5的相等／變更比較，不是職業授權檢查。

## Server契約

選職仍由issued Merchant context、owner／lease、地圖／距離、入學revision及
SelectCareer交易授權。中文JOB先轉symbolic career，再依上表映射；不接受
Client直接提供class byte作權限來源。

1. 未選職為0。C25後S05、C35成功後S33都從持久選職讀code。
2. STATE=OK先持久保存；選擇runner Dispose後依序發S33、S44(DIRECT結果)。
   S33使用當前權威XY、面向、角色外觀，不套地圖出生點或改position version。
3. 同一串行RespondMany按S33→S44分配ordinal並寫入；重複Dispose不重發。
   若保存後、Dispose前斷線，重登仍投影保存的職業。
4. 切圖／重登保留code。教學完成仍只由正確目的圖C35提交，不因顯示更新提早完成。

Protocol輸出界限為已知顯示值0..7，高於7拒絕，避免索引到其他無關文字。
Application僅產生未選0與五職業1..5，不新增6／7轉職。這是Server輸出設計，
不宣稱Client原件自身將數值限制於7。沒有新增schema或遷移使用者DB。

## 驗證與限制

353項.NET測試通過：原有選職授權／拒絕，加上職業欄不污染其他外觀、未知
code拒絕、五職業S33→S44及ordinal、pose保留、重登S05／S33保存職業。
五職業完整真實TCP路線均通過，另核對選職S33、學校／目的圖重登S05與S33的code與順序。
Client實際名稱顯示與城鎮身份仍待GUI，整體目標保持未完成。
