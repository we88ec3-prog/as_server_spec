# RI-007：一般登入 S03/C10/C25 成功後無 World 回包；另確認創角後當掉為 main-menu-preview.exe

> **重要測試邊界（2026-11-01 使用者明確更正）：`Asgard-main-menu-preview.exe` 是經過調整的「僅供排錯」副本，並非原始程式。它的 Windows WER、TCP trace、位址與行為一律標示 `modified-preview-debug-only`；不得作為原版 `Asgard.exe` 之反組譯原件、動態行為證據或 Native CT PASS。只有經原始 SHA 驗證之 `Asgard.exe` 能作為原始 Client 靜態分析基準。預覽版 RVA `0x00141264` 不可逕行映射成原始 EXE 相同指令或函式故障。**


2026-11-01｜本報告是**使用者提供的 Server JSONL 與 Windows Event 摘要 + Server 代碼唯讀分析**，不修改 `as_server_roy`、Client 或資料庫。原生未修改 `Asgard.exe` GUI CT-107/108 仍然 **not-run**。

## 1. 新的證據來源與審計界線
- 上傳的 `game-packets-20261031(2).jsonl`（84筆；30,921 bytes；SHA256 `3eb2180ae27023b037ae8c3b0a0c073439fa17a0d71277a45f23d4bd7cadb643`）、`game-tcp-20261031(2).jsonl`（17筆；9,151 bytes；SHA256 `7365b0d0e1768d0bcaaa9cac95c55c1d8dc8a69e09430994ba5e34052f8e42a6`）、`game-validation-20261031(2).jsonl`（4筆；2,272 bytes；SHA256 `54135dccf9ab866a5b360e9fdb7b41ddb4acc2c1f90d603a6e`）。檔案是累積多版 Server/多次連線，不得把舊紀錄當新事件；原 JSONL 不上 Git。
- 另一來源是使用者貼的 Windows Application Log 列表，**只有被 PowerShell 截斷的 Message 摘要**，無完整 event XML/message/故障模組/例外碼。
- 先前 RI-006 依 SHA-locked **原始 `Asgard.exe` 靜態證實 C42 是 `CExceptionPacket`**，但這次 Windows 事件**明示 03:38:13 故障程式是 `Asgard-main-menu-preview.exe`，版本 2.1.2...（後續文字截斷）**。因此 RI-006 中「該次封包必出自未修改原版 GUI」須更正為**修改/預覽副本上的 runtime test，非原版原封不動 Client CT PASS**。原件分析的 C42 類別定位仍屬原版的靜態事實，不能直接移植到未知哈希的預覽執行檔作唯一 runtime 根因。
- 此批新 Log 的 `Build=1.0.0+e93c9a1748fbca539106cba5e75458757c8e490d`，唯讀對應 `as_server_roy/main@e93c9a1748fbca539106cba5e75458757c8e490d`；其他 log 中的早期 build 不能代表當次操作。

## 2. 不應混淆的第一個事件：創角成功回覆後預覽程式崩潰
|時間（台灣 UTC+8）|來源|觀測|
|---|---|---|
|03:38:13.334～03:38:13.586|Server Trace `c126a05e...`|C02→S02(status0)→C04→S02(status0)，Server 成功寫出第二段成功回包，但沒有同 trace 的 World 封包|
|03:38:13（事件列表精度為秒）|Windows Application Error 1000|**`Asgard-main-menu-preview.exe` 發生 Application Error**；精確模組／例外碼尚缺|
|03:38:17|Windows Error Reporting 1001|系統產生應用程式錯誤報告，和 preview 當掉時間接近；報告詳細內文被截斷|
|03:38:17.899|Server `c126a05e...` close|Reason=`io-error`，約在最後 S02 回覆後4.313s；Server 的 `IOException` 統一轉為此文字，**不代表可直接判斷主動踢線或讀/寫方向**|
|03:38:47.813～.817|另一 Server Trace `0f5b5b86...`|C62→C42(body39)→`unknown-opcode`／`invalid-native-protocol-or-state`；原始 EXE 靜態 C42 為 exception report，**跨 socket 沒有 PID 佐證**|
|03:38:47|Windows `.NET Runtime` 1000|Message 摘要開始 `Category: Asgard.Server.Host.GameTcpDiagnosticJournal...`；**這可能只是 Server Console/EventLog 診斷事件，不可僅依 .NET Runtime provider + ID=1000 認為 Server 崩潰**|

**因果界線：** Windows 的 Application Error 1000 使「preview.exe 在創角後當掉」成為比前輪更強的 OS 層證據，然而仍缺 ExceptionCode、FaultingModuleName、FaultOffset/Stack，**不能假設是 World/地圖資源、S02 本身、特定 EXE 位址或 C42 關線導致**。已知 C42 出現在另一條後來連線，不能反向將它當第一個崩潰的原因。需先拿完整 Windows 事件。

## 3. 第二個事件：一般 C03 登入成功，World C25 後 Server 沒有回覆
這是**獨立於 03:38 preview 崩潰的登入測試**，並非同一條 Client/Server socket。以下來源都是新上傳 JSONL（UTC timestamp 已轉台灣 +8）。

|時間|Trace|方向/Opcode|Server phase/結果|
|---|---|---|---|
|03:47:22.735～03:47:22.876|`18dbe839...`|C62/C00/C6C/C0F/C57/C57，S00/S18/S56/S60|連線完成正常 LoginReady|
|03:47:31.919|`18dbe839...`|C2S C03，body_len=13|從 LoginReady 進 TransferIssued|
|03:47:31.955|`18dbe839...`|S2C S03，body_len=31|成功寫出原生登入轉服資訊|
|03:47:31.956|`18dbe839...`|關線 `expected-s03-transfer`|**正常**轉服舊 TCP 結束，不是「伺服器無回應」的失敗原因|
|03:47:32.956|`88d9d015...`|新 Socket C2S C10，body_len=24|Connected→WorldGranted；World grant 成功兌換|
|03:47:33.143|`88d9d015...`|C2S C25，body_len=16，ordinal=6|WorldGranted→WorldGranted，`Unexpected=false`，`Disposition=handled`|
|C25 之後|同 trace|**無 S05/S15/S14、也無 C35**|在這份 Log 的截點尚未走入 WorldLoading；`88d9d015...` **沒有 close summary**|

此為 **C03 一般登入成功 + 原生 World Region3 C25 已到、Server 不提供下一段 World 初始化**；不應回去查帳密、C03/S03/C10 授權，因這些本次都走過了，也不是 C35 錯碼（尚未下發 S15/S14(1)，Client 無法先做本階段應答）。

## 4. 靜態 Server 根因（source-confirmed，非猜測）
`as_server_roy/main@e93c9a1748fbca539106cba5e75458757c8e490d` 的 `src/Asgard.Server.Host/LoginWireSession.cs` `case 0x25`：

```csharp
if (_worldFixture is null)
{
    // A-031: Region3 C25 carries 3 opaque billing string8s.
    // C10 alone is the authority. Native map/spawn/S2C after
    // billing is not yet proven; retain WorldGranted and wait.
    if (_nativeRegion != 3 || _billingSeen)
        return Close("native-world-map-not-configured");
    _ = TwWorldPackets.ParseRegion3C25(input.Body);
    _billingSeen = true;
    return Continue();
}
```

`Continue()` = `LoginReply(empty Frames, CloseConnection=false)`。在所提供的 C25 封包 `handled`、phase 保持 WorldGranted、**零 S2C** 的情形下，和這個 native `_worldFixture=null` 分支吻合。相反地，`_worldFixture != null` 的本地 synthetic fixture 分支只接受 `C25 body=01`，會發 S05/S15/S14(1)；**本次是真實 Region3 C25 16 bytes，絕不可改成測試用 body01 以虛報 native 通過。**

因此最直接原因不是 C25 編碼錯誤或 C03 驗證失敗，而是**DEV-ENTRY 原生地圖載入/出生/S2C 路徑尚未啟用**。Server 留在 WorldGranted 沒有進一步回覆，原版或預覽 Client 自行顯示「伺服器無回應」符合這個未完功能，但**本份沒有該 Client 畫面時間戳，所以無法證明具體 Timeout 秒數**。

## 5. 優先交接與禁行捷徑
1. **DEV-ENTRY-04／Server 開發者 P0**：把已證 Region3 C10→C25(3×string8) 正式接到 native real map profile、A-032 C35 結構驗證、合法 spawn/viewport，依可證順序 S05/S15/S14(1)→真 C35→S04/S33/S14(2)。保留 account/character/world grant、epoch/DB fencing；**不重做已可用的 C03/S03/C10/C25 parser**，不可複製 synthetic C25 body01。
2. **DEV-ENTRY-03／A-028/A-031 P0**：新角色首次創角成功後直接進 World 的 ADR-008 仍未知；本次只有「已經有角色的 C03 一般登入」可達 WorldGranted，不能把它當首次創角直入 World 的 CT-107 PASS。
3. **World no-response 診斷**：對於明知 native World map 未配置的情況，避免長時間 `Continue()` 造成無提示等待；Server DEV 應在內部留下獨立穩定 `NATIVE_WORLD_PROFILE_UNAVAILABLE`／`world-load-not-started` 原因與必要的 timeout/Client 已證錯誤回覆政策。未知原生錯碼不得猜測；Server 安全驗證與 Auth Grant 不能因暫時缺映射被放寬。
4. **A-020/A-028 / Windows crash**：要求完整 `Application Error 1000` 與 `Windows Error Reporting 1001` 的 `Message`／Event XML，至少 FaultingModuleName、ExceptionCode、FaultOffset、FaultingProcessId、ReportId；若 Client 是預覽副本，要記 **該 EXE 的 SHA256** 並區分 `Asgard.exe` 原件。未取得前不要依原件虛擬位址套到 preview 執行檔判案。
5. **另行 A-020 C42**：CExceptionPacket 是已證原件 static；日誌中的 C42 是不同 socket（可能為異常上報），Server unknown-opcode 拒絕會失去診斷資料，但**不必把它納入 World grant 或造成首個 crash 的根因**。是否加入最小化安全接收/過長 body 防護由 DEV 設計，不由分析者直接改程式。
6. **CT-108 新負向測項**：Native C25 後若無 S05/S15/S14(1) 的輸出，必須明確標記「停在 WorldGranted / native World 未實作」並判 CT fail，不可把 `C25 handled` 當入圖成功；分開測 normal C03 login 世界入口與首次 C04 直入 World。

## 6. 建議使用者擷取完整 Windows Event 的指令
使用者目前只有 PowerShell 表格摘要（`Message` 被截斷）。Windows PowerShell：

```powershell
Get-WinEvent -FilterHashtable @{
    LogName = 'Application'
    StartTime = [datetime]'2026-11-01 03:38:00'
    EndTime = [datetime]'2026-11-01 03:39:10'
    Id = 1000,1001
} | Where-Object {
    $_.ProviderName -in @('Application Error', 'Windows Error Reporting')
} | Format-List TimeCreated,ProviderName,Id,Message | Out-String -Width 4096
```

檢視/分享前先遮蔽本機路徑/使用者資訊；無法找到 `Crash_as*.log` 不妨礙用 Windows WER 故障模組/例外碼確認崩潰方向。

**最終分級：** C03→S03→C10→C25 **runtime-observed，且 Server 原碼解釋其停住**；World S05/S15/S14/C35 **not reached/not-run**。Preview app crash **Windows event observed but cause unknown**，原版 `Asgard.exe` 對應 GUl **not-run**。本次只改 as_server_spec，沒有 Server 程式更改。
## 2026-11-01 完整 WER 事件與測試程式版本邊界（debug-only）

使用者提供完整 Windows `Application Error` 1000 和 `Windows Error Reporting` 1001，**僅供排除錯誤**：

- 2026-11-01 03:38:13（台灣時間）Windows Application Error：`Asgard-main-menu-preview.exe` version `2.1.2.0`；faulting module 同為 `Asgard-main-menu-preview.exe`；`ExceptionCode=0xC0000005`（access violation）；`FaultOffset=0x00141264`（該修改版的 RVA）。
- 03:38:17 WER：`APPCRASH`、P7=`c0000005`、P8=`00141264`，Report ID=`8410ed03-4f93-4691-9b86-0d5ed08b48cb`；WER 曾列可能的暫存 dump 檔 `WER.bc18ed12-1c61-42c9-87f0-db3f3b273470.tmp.dmp`，檔案是否尚存未核實。
- 同時段 Server 的 C02→S02(0)→C04→S02(0) 和 `io-error` 仍是**Server 端操作／輸出事實**，但因本次測試用修改版，**不能當作原版 `Asgard.exe` 在相同後創角 UI 路徑會 crash／不 crash 的證據**，也不能宣告 original Client E2E 成功或失敗。
- **位址推論降級：** `0x00400000 + 0x00141264 = 0x00541264` 僅是映像基址的算術換算；即使原件 `0x00541264` 恰有某指令、且原件 A-028 的 UI callback 曾呼叫附近函式，仍**不證明修改版該 RVA 的 bytes／堆疊相同**。不可把它寫成「原版 Client 的崩潰指令」。除非提供預覽版 hash／RVA bytes／dump 比對，否則這只是修改版的排錯候選，不列入原版分析成果。
- 若需要**排錯**，可唯讀檢查 WER dump 之 exception context、暫存 fault address、call stack、修改版檔案 hash 和預覽版 RVA；此流程不得覆蓋原件 SHA 或污染原版 A-028/A-031 結論。
- **另一路問題保持有效但狀態須精準：** 03:47 的 C03→S03→C10→C25 已在 Server JSONL 觀察到；Server `_worldFixture==null` 於 C25 後 `Continue()` 零回覆是 Server 程式既有設計。這可用於定位**Server 目前沒有啟動原生 World 載入回應**，但若送包者是修改版，並不等於未修改原件的 GUI/World E2E 已實測。

