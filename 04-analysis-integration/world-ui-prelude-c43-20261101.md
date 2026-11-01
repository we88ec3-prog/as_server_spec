# 參考本地原型的入圖修正：UI prelude與C43

2026-11-01。來源是使用者明確要求參考之前本地Server並回寫spec；功能目的延續R-004入圖。以下wire／Client限制來自既有分析，有限延後策略屬本次Server設計，不將兩者冒稱使用者逐項要求。

## 原型與新試驗的差異

- 本地 `workspace/anal/world-flow.md` 及原型 `Session.receive` 的一般登入／C25路徑，先回 **S02(status0, empty string8)**，再S05／S15／S14(1)。歷史隔離Client曾顯示原始map0，不等於所有region／原始EXE均已驗證。
- LoginDialog的S02處理0x4A8D60建立遊戲UI／MainMenuPane(0x4AEFC0)與MapPane(ctor0x4BDF70)。在這個歷史路徑下，S05/S15不能先假設MapPane已存在。新native-map trial先前只送S05/S15/S14，缺少這個UI初始化。
- S05 handler0x4F3830建立自身後會發C43；舊本地trace曾在world_initializing記錄C43、payload length8並當unknown不回，仍繼續入圖。**不能據此推出所有未知封包可忽略**。
- [A-011靜態分析](../task_a/roy2/A-011-analysis.md) 已證CObjectInfoRequest ctor0x574500／writer0x5745B0：body精確為u8 type、BEu32 object key、u8 subtype，共6bytes；加opcode/ordinal為上述8bytes。已證NPC producer的1/ref/4不代表S05觸發的type/subtype已被本次實測辨識，不能假造其S34／任務回覆。

## 本次公開Server合約

限定 **Region3、已授權既有角色、明確啟用native-map試驗**：

1. C03/S03/C10已驗證owner；C25只解析billing；取得指定MapCatalog／loading epoch後，發S02(0, empty)→S05→S15→S14(1)。S02只啟動此試驗的Client遊戲UI，不代表創角完成或C35已成功。
2. WorldLoading接到C43時，必須仍有有效World owner、同試驗設定且body精確6bytes；僅延後，不產生猜測的S34/S3C、NPC或Quest結果，也不提交角色／地圖。此階段每連線最多8次是 **designed observation budget**，不是原服常數；保留既有loading期限。
3. 正常C43列為`native-loading-object-info-deferred`，不誤標unknown opcode或完整已實作；畸形、未授權、錯階段或超預算仍拒絕。
4. 精確C35 header／structured checksum通過才atomic entry commit，後發S04/S33/S14(2)並進WorldReady。任意C43不能代替C35，合成DEV-050的舊出包順序不因本修正改動。

**不包括**：創角後直接World的ADR-008、全region正式支援、實際走路／碰撞、完整物件資訊回覆。原型C35僅驗長度、移動夾邊界及忽略未知封包的捷徑不帶入新版。

## 實作與驗證

私有roy已實作UI prelude、C43嚴格parser／有界loading處理及journal分類。完整Release合成回歸 **248 passed**，新增覆蓋原生順序、無owner／畸形billing無S02、synthetic順序維持、C43不提交entry／不進WorldReady、畸形與超預算拒絕；真loopback HTTP/TCP smoke另通過 C03/C10/真Region3格式C25/S02/S05/S15/S14/C43/C35/S04/S33/S14與保守S0B停止。

測試使用獨立新SQLite與空閒埠；未啟停使用者原本Server、未操作遊戲UI。輸入原件Map0 archive SHA鎖定，Client測試候選是既有手動登入修改副本。Map6、spawn30/30、viewport8/9、S15 FieldB/C=60仍是明示的局部實驗值，不是原服新手圖／合法行走證據。原始Client CT-108/109仍not-run。

## 請使用者操作的批次

私有roy測試入口會建自己的試驗Server／DB、由管理API建立throwaway帳號及已存角色，再產生Client啟動器；不把密碼或Admin Key寫入啟動器／session metadata。使用者自行輸入測試密碼登入，回報是否完成loading、看見人物與地圖、任何錯誤／卡住畫面，保持試驗Server視窗供日誌對照。試驗角色只有停止／校正回應，**不可把不能走路誤報為已完成CT-109**。在視窗按Enter結束測試時只停止它建立的Host，正常Server與資料庫保留。

此批次先驗證一般已存角色入圖；創角、自動進World、換衣、音樂、即時切圖後續逐項接上。結果保留本地raw與去敏摘要，原型通過、修改版通過與未修改Client通過分欄記錄。

## 使用者第一次畫面回驗：已到C35，但尚未通過

15:11（UTC+8）的本地獨立試驗使用既有 `Asgard-manual-login.exe`（SHA256 `b9f9fb9013df604081f1d40a1c11baee76f4a308e4abf6b0519eeecb04eac380`）。使用者畫面出現遊戲UI與Local World Trial標題，但地圖／人物未顯示，接著連線中斷。Server去敏journal證明 C10→C25→S02/S05/S15/S14→C43(body6)→C35(body4)；C43保持WorldLoading，C35處理後關閉。這是 **diagnostic-client failed**，不是成功入圖或原版CT通過。

該輪程式的close reason尚未含C35數值，僅能定位C35處理拒絕，**不能事後斷言兩個校驗值已證不符**。journal的assembly build為基底c4170f8，當時在未提交增量上建置，不能單用該字串把執行內容等同基底commit。

私有實作增量 `ed4adb5` 已加上CloseSummary的可選`MapCheck`，只含預期／收到的header／checksum四個u16及Accepted bool，分別用`native-map-c35-mismatch`與`native-map-c35-state-or-deadline`，沒有改成回聲式接受或放寬CRC。也修正C43延後分類在實際packet journal被覆蓋為expected的問題。

使用者保留現場時曾鎖住共用Release DLL；新測試入口改為每輪獨立Server輸出副本，資料／埠／程序仍各自隔離。增量完整248項回歸通過，真HTTP/TCP smoke確認正確C35與刻意錯誤C35的型別化journal；已請使用者重新操作讀取實際值。後續修正必須先核對Client資源／S15參數／實際C35與靜態模型，不以猜測常數掩蓋差異。

## 第二輪回驗與修正

診斷副本收到 C35=00060F90，先前 Server 錯預期00040F90；已追到 MapData 物件／檔案 offset 混淆並修正。詳見[第一欄勘誤](../04-analysis-integration/c35-map-reference-correction-20261101.md)。248項測試與本機TCP smoke通過，畫面仍待使用者重驗。測試入口依使用者需求改為原生預填ID的既有診斷副本，見[ID預填需求](../02-server-planning/test-client-id-prefill-20261101.md)。
