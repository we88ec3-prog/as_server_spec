# 原生郵件：MailBoxDialog 使用外部 NMCO3 服務

## 本輪結論與可開發範圍

使用者要求持續完成 Server 功能。本輪針對 A-014 郵件入口做原件靜態追查，發現本版 MailBoxDialog 的寄信、收件列表、通知及信件處理走 **NMCO3.DLL 的 Note API**，不是目前遊戲 TCP 的 C12/S58 郵件封包。不能將 SDK 的本機結構當作遊戲線路格式，或宣稱只新增 Server C12 handler 就能恢復原生郵件視窗。

Server 可以另建文字郵件儲存／查閱服務，經已證聊天通道或 Web 管理呈現；那屬重建的替代操作介面。原生 MailBoxDialog 相容還需要研究 NMCO3 的連線、驗證、事件及資料協定。本輪未改 Client、未呼叫 SDK、未連接原郵件服務，原生 GUI 驗收未執行。

## 原件綁定

- Asgard.exe SHA256：`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
- 同份提供物中的 nmco3.dll：430080 bytes；SHA256 `bd1184bd16daef225a58734da950685ecae3c2563f7e922bc871927434d6f579`。
- 本輪 REA 目標只有 EXE；DLL 僅做檔案身分核對，未反編譯其協定。
- Ghidra 12.1.4，原始檔唯讀。精選位址／結論可由本報告與 JSON 重現；完整偽碼與快照保留私有分析資料夾。

## 已證呼叫鏈

| 功能 | 原件路徑 | 已證內容 |
|---|---|---|
| 開啟一般／公會撰寫 | 4AA3F0 → 4AA070 | mode1 一般、mode2 公會；mode0 唯讀顯示。開啟撰寫本身為本地 UI。 |
| 寄給單人 | 4AA660 → 4AB6A0 → 4DE2D0 → 4DDD20 | 最後直接 NMCOSendNoteMsg，不經 5788A0 遊戲 packet sender。 |
| 寄給公會名單 | 4AA660 → 4ABCB0 → 4DE8A0 → 4DDD20 | 按名單每批至多10個地址呼叫 SDK；不是本輪 Server 公會功能已完成。 |
| 收取列表 | 4DF6F0 / 4DF7C0 | NMCOGetNoteBox(0 / 1, buffer, count=100, 0, -1)。API回傳成功後建本地 MailData 列表並更新4AD060/4AD090。 |
| 信件處理 | 4DDF50 / 4DDF70 / 4DDF90 | NMCOProcessNote(id, 2 / 1 / 3)。caller4ACE70、4AB6F0有本地列表／暫存移除分支；各operation語意未僅靠名稱強命名。 |
| 新信 | SDK callback 4DF890 case8 | NMCOGetNoteBox(0, buffer, count=10,0,eventId)，再4DF4E0→4AB860(2)更新右側圖示並新增列表。 |
| 列表刷新通知 | 4DF890 case11 | param2=1重載box1，其餘重載box0。 |
| SDK初始化 | 4DE250 | NMCOInit(2,hwnd,asgard_nm_%d,0x30)，NMCORegisterCallbackMessage(WinMsg0x405)。 |
| SDK登入 | 4DE360 | NMCOLogin；需要獨立 SDK 身分與憑證派生，不能等同遊戲登入成功。 |

Import名字由EXE的IAT/外部procedure可核對：NMCOInit、NMCORegisterCallbackMessage、NMCOLogin、NMCOLogout、NMCOGetMyStatus、NMCOSendNoteMsg、NMCOGetNoteBox、NMCOProcessNote、NMCOGetServerMessage。

### C12/S58 的正確界線

4ABD90 先送 C12 body `00 01` 與 `00 02`，隨後本地呼叫4AA3F0(0,1)開公會撰寫視窗。這兩個請求與收件人地址名單依賴有關；它們不是寄信本文、讀信或刪信命令。C12同時出現在Friend/Guild/UserList相關路徑，不得整個opcode重新標成郵件。S58 reader5800F0只讀兩個u8，並未讀本文或3032-byte Note row。

## 撰寫資料與限制

4AAE90 設 control7 收件人上限30、control10 標題28、control11 本文350。這是本地文字控制項限制；尚未證明都是CP950編碼byte數上限，也不是Server API天然必須使用的長度。4AA660拒絕空標題。本文與標題經Unicode處理；550910以全域DAT66E47C呼叫WideCharToMultiByte，這個呼叫不做嚴格不可編碼字元拒絕。新Server應另明示其驗證政策，不照抄預設字元替換。

4DE2D0 將收件者組合為 `<name>@asgard.<MailManager+50>`。4DDDE0將標題與本文以 `#aS!!` 拼接，轉為多位元組字串；4DEE40讀回時以同標記分割。原生SDK格式不提供獨立title欄位的遊戲packet。

4DDD20 建立0xBD8(3032)-byte本機結構並交NMCOSendNoteMsg：首DWORD清0，收件地址在+0x7C，組合文字在+0x5C4。此為**本機SDK ABI觀察**，未知其實際網路序列化、認證、服務端上限或錯誤碼完整集合，不能直接做raw遊戲body。

### 寄信中的視窗狀態

4AB6A0/4ABCB0設定MailListDialog+58 pending旗標與2000ms timer。4AA660送出後disable control1；公會撰寫會隱藏。4AB860(0/1)處理pending結果，取消timer並呼叫4A9F30：result0隱藏撰寫；result1顯示錯誤提示並重新enable control1。事件與超時的完整成功分支仍待補核，不把callback3的某個值直接當遊戲S2C成功碼。

## 列表資料、讀取與操作界線

SDK row stride0xBD8。4DEE40轉成0x78-byte本地MailData：+4存SDK原始DWORD id；顯示日期讀row+0xBC8/+0xBCA/+0xBCE；依box方向從row+0x14或+0x7C讀對方地址，再去除@asgard尾綴；row+0x5C4文字分解標題／本文。UI具有兩個列表，4AB720對應模式1/2。尚未以同版字串／動作完整確認兩列表正式名稱、伺服端cursor、id跨box/角色的唯一性或排序規則，不能由count100推造分頁契約。

本輪MailBox控制項7/10/11及send結構只證收件人、標題、本文。未找到附件／金錢 UI、商品row、領取或退回的原件閉環；這是有界未證，並非宣稱SDK或其他遊戲版本永無附件。C17/S6E Trade不得移作郵件附件。

## 開發與驗收要求

1. 若本輪先開發文字郵件，明示為重建政策與替代通道；帳號、所有權、收件角色、id scope及刪除權限由Server權威驗證。
2. 本文相同的兩次新寄送應可成為兩封信；不能以內容hash當重放識別。
3. 附件／金錢不在本輪已證原生範圍。加入時需獨立原子移轉、重播與拒絕後刷新契約。
4. 下一輪原生相容先研究NMCO3.DLL的Note API transport、endpoint及登入，不再猜C12/S58為完整mailwire。
5. 原件GUI、重建介面TCP測試與SDK相容測試須分開記錄。本輪原件GUI、SDK連線、真實寄信全部未執行。

機讀JSON保存各結論依據的Evidence IDs與位址；未知項仍須保留，不能把分析阻塞改寫為已完成原生郵件功能。
