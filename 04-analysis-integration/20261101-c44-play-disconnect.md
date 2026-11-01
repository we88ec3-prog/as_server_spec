# 進場可移動後斷線：C44 物件資訊請求

## 本輪實機進展與斷線點

使用者回報「可以移動，但玩到一半連線中斷」。本地診斷副本
SHA `e5f7b1ac742afdda9c6ec30a8934267dfac10221e115f74c2acd6449a4832dba`，
Server067d129，2026-11-01 16:29～16:32 UTC+8：

- C04提交後收到S03並交接新TCP，無需使用者第二次手動登入；C10/C25通過。
- C35=6/3984通過，S04/S33/S14(2)/S44已送；兩筆C6C body10被Born生命週期
  handler接受，DB保存一筆intro ack。多筆C54/C11/C33及S0B持續交互。
- 約168.9秒後收到 **C2S C44/body4**，被標成unknown-opcode並關閉。
  不是600秒idle timeout，也不是C35再次不一致。
- 唯讀DB檢查：Character1、目前map6/pos28,28/facing3、位置version60，
  tutorial_completed仍0。version包含轉向更新，不能解讀為已走60格。

這是**診斷副本**的新角色自動進場／Born關閉回包／實際移動證據，
不升格未修改原始EXE驗收，也沒有證實教學地圖身份、招募NPC或教學完成。
使用者本輪未提供斷線前的精確操作或C44 target bytes。

## REA 原始 EXE 契約

原件SHA沿用主線 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

- `0x5753B0` ctor呼叫packet base(0x44)，RTTI對應CShowObjectInfoPacket。
  證據 `ev_b425e2eebf0a2637bf7aca6c282644142b35bfb06006def5915c41e1eb1c3e2c`。
- writer `0x575460` 在Ghidra未恢復成procedure，本輪未取得其偽碼；
  REA讀取16bytes，指令為讀取reader-subobject+0x18的DWORD、push、
  call0x45AC40、ret。證據
  `ev_51ca1060975c5157f930722e993e9f895d7665b191504995ff810d43e5dfcdd8`。
- `0x45AC40` 在endian旗標非零時依高到低byte寫u32；正常packet writer
  profile為BE。body因此為**單一BEu32 target object key，恰4bytes**。
  證據 `ev_f4228c3d7b533e44801a49be40fdaf34baaccd71be47a47ebf6b0876d9de8886`。
- MapPane `0x4BEE70` 的一條producer在UI／物件條件成立且距上次大於
  500ms時建立此packet，將MapPane+0xC8填入完整packet+0x24並送出。
  另有其他producer；不能斷言每個C44一定由這個分支或某個按鍵觸發。
  證據 `ev_a0aca4c011ade4c60173d298a4a13bc162953bbdcda7fc69dffe6fe01aaca75f`。

C2S C44與S2C S44 Script雖然opcode相同，必須依方向區分，不能套用Born
selector格式解讀這四個bytes。

## Server 增量與未實作邊界

原生map trial、WorldReady、owner仍有效且map loading已提交時，嚴格解析
上述形狀；self、0或過期／未知key只是資訊顯示意圖，不得取得角色控制權，
不更新位置、任務、外觀或授權狀態。此版不發明任何物件詳情S2C回覆，
將處理分類明示為 `native-object-inspect-response-unavailable`，保持連線。
其他階段／未啟用profile／畸形長度仍拒絕。這不是全域忽略未知opcode。

物件詳情內容與回包尚未實作；未宣稱完整物件檢視功能通過。本增量目的
是支援已證合法請求形狀，解除遊玩途中這個明確斷線點。

264項Server測試通過，涵蓋BE key、精確長度、錯階段、self/zero/stale key
不中斷；真本機TCP亦覆蓋C44後仍可移動及重登。修正後的使用者GUI穩定
遊玩／重登位置驗收待回報。

私有實作追溯：roy `51bed5b`。
