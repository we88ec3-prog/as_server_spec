# RI-006 / A-028/A-031 增量：創角兩階段 S02 成功後 Client 異常與 C42 例外回報

> **重要測試邊界（2026-11-01 使用者明確更正）：`Asgard-main-menu-preview.exe` 是經過調整的「僅供排錯」副本，並非原始程式。它的 Windows WER、TCP trace、位址與行為一律標示 `modified-preview-debug-only`；不得作為原版 `Asgard.exe` 之反組譯原件、動態行為證據或 Native CT PASS。只有經原始 SHA 驗證之 `Asgard.exe` 能作為原始 Client 靜態分析基準。預覽版 RVA `0x00141264` 不可逕行映射成原始 EXE 相同指令或函式故障。**


2026-11-01｜**原始使用者提供 Server JSONL + SHA 鎖定 Asgard.exe 靜態證據。** 此為分析/交接，不修改 Server/Client；原版 GUI / World CT-107/108 仍 `not-run`，不能推論這次是 World 畫面已載入。

## 來源、邊界
- 使用者提供 `game-packets-20261031(1).jsonl`（70筆，25768 bytes，SHA256 前16 `a238359612c334eb`）、`game-tcp-20261031(1).jsonl`（16筆，8615 bytes，SHA256 前16 `df451b3dfaa7558f`）、`game-validation-20261031(1).jsonl`（4筆，2272 bytes，SHA256 前16 `54135dccf9ab866a`）。**原始檔只在對話附件，不提交 Git**；本報告只保留脫敏摘要，沒有封包 decoded body、帳號、E-MAIL。
- 原版 `Asgard.exe` SHA256：`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，與 A-028/A-031 原件一致。
- 上述 Log 檔混合多個 Server build，包括 f2a4a38、a9326985、e50c4f08、a86e28cf、e93c9a17。**不能將不同 build/trace 直接串為同一 TCP 會話或同一 Client PID。**
- 當事使用者回報：成功創角一次，準備進遊戲時 Client 當掉。Log 只觀察 Server Socket / decoded packet；沒有當次 Windows Process exit、SEH exception code、minidump、PID 或本機畫面，因此 crash 原因不能僅從 TCP `io-error` 確診。

## 最重要的本次時間線：2026-11-01 台灣時間 (UTC+8)

|時間|Trace 前8|封包／結果|能證明|不能證明|
|---|---|---|---|---|
|03:37:38.909–03:37:38.969|`c126a05e`|C62→C00/S00→C6C→C0F/S18→C57/S56→C57/S60|Region3/native prelogin handshake 進 LoginReady|非 World session|
|03:38:13.334|`c126a05e`|C02，decoded body_len=20，ordinal5|Server 收到完整創角 request|不暴露 credentials；不能單憑此確認驗證成功|
|03:38:13.456|`c126a05e`|S02(status=0)，body_len=2，ordinal3|第一階段成功回覆已由 Server 寫出|不能證明 GUI 已顯示|
|03:38:13.458|`c126a05e`|C04，body_len=5，ordinal6|原 Client 向同 socket 送出外觀資料|非 World move|
|03:38:13.586|`c126a05e`|S02(status=0)，body_len=2，ordinal4|第二階段成功回覆已寫出；Server 應按 C04 commit 後才發送|尚缺 DB read-back，不能直接宣稱永續資料驗證完成|
|03:38:17.899|`c126a05e`|TCP Close: `io-error`，phase=LoginReady，FormInput|Server 看見 IO 例外，距最後 S02 約4.313秒|不是正常 S03 transfer，也無從證明是 Server 主動踢線或 Client OS crash|
|03:38:47.813–47.817|`0f5b5b86`|**另一 socket** C62→C42(body_len=39，ordinal1)，`unknown-opcode`→`invalid-native-protocol-or-state`|Server 收到例外通道 opcode0x42 並因不支援關線|不能證明同 PID／同次 crash 或 C42 是 World Entry|

- 此兩條 trace 的 Client/Server 連線沒有共享可核身的 process/session identifier；中間約30秒。僅能說時間上相近、並且符合 crash reporter；**不等於 C42 引起第一條連線的異常**。
- 成功 S02(0) 之後沒有觀察到同條連線的 C03、S03、C10、C25、S05、S15、C35、S04 或任何 World Ready 封包；目前證據停在 NewUser 二階段成功，**進圖流程尚未開始／未被此份 Server Log 捕獲**。

## 原版執行檔靜態分析：C42 真正身分（新證據）
- PE32 `Asgard.exe` VA `0x5723C0` ctor：`push 0x42` at `0x5723D9`，call `0x578600` (base packet ctor) at `0x5723DF`；設物件 vftable `0x613930`。
- `0x61392C` RTTI COL 指向 `0x62C050`，type descriptor `0x66940C` 的原始 ASCII name `.?AVCExceptionPacket@@`；**因此 opcode0x42 是 `CExceptionPacket`**，不能隨便當原版 World C42 handoff。
- vtable `0x613924` writer `0x572470`（實際類別虛函式）；writer 讀 object byte `+0x18` 和字串資料地址 `+0x1A`，並經 native write helper 序列化。這是靜態形狀；**本次只含 body length=39 的 metadata，未有解密 body，不能還原例外代碼、訊息或 payload 全部語意**。
- 唯一已識別外部直接 constructor callsite `0x462C08`，位於 `0x462AE0` 的例外回報處理例程。內有 `%s\\%s*.log` UTF-16 format at `0x605DD0`、`Crash_as` at `0x605DE8`、原始程式路徑 `.\\exceptionhandler.cpp` at `0x605D98`。該例程遍歷候選 crash log，建立並送出 `CExceptionPacket`。**這使 C42 高度符合「上報既有例外記錄」而非「登入 World」；即使這次沒有 crash，舊記錄也可能在後續啟動被送出。**
- Source location/function addresses 均直接取自 **未修改**的原始 EXE，非從 Server 猜測、非真 GUI capture。

## Server 現況（僅來源碼/Log）
- 這次成功 trace `Build=1.0.0+e93c9a1748fbca539106cba5e75458757c8e490d`；`LastClientOpcode=0x04`，`LastServerOpcode=0x02`，`Reason=io-error`。與以往 C02 立即 `Close(native-...)` **不同**；勿把此新故障誤診成錯密或 timeout。
- `io-error` 在 `GameTcpProbeService` 是共用 `IOException` catch；Log 未包含 exception type/SocketErrorCode、發生在 Read 或 Write、對端 FIN/RST、Client PID。可由 Client 自行結束、RST 或其他 IO 失敗產生，**單憑 `io-error` 不確證 crash 根因**。
- 新 socket C42 被現在 Server 的 opcode/phase classifier 當 unknown，之後通用 invalid-native-protocol-or-state 結束。這是 **Client 例外回報接收／分類缺口**，不能因為有新 C42 就推論原版 Client 提出 World 建立請求；Server 不應以此分支核發權限。
- C02/C04 回成功後是否有真正 PostCreateEntryContext、如何自動 World 授權／額外 UI 資源依賴仍由 **A-028/A-031** 釐清；ADR-008「玩家不手動再登入」是產品政策，不是現已證實的 Client 實作。

## 下一步：交 A 分析／DEV 規劃／Client CT
1. **A-028 P0**：從 final S02(0) callback `0x4B206B` 往後追 UI/tree/destructor、異常處理入口、背景 Socket 與 scene/load；確認是否有非法 UI 指標/缺資源、是否建立 LoginDialogPane、原件實際後續轉場，不要從 `io-error` 猜。
2. **A-031 P0**：獨立 World handoff 還缺新角首次入圖的真正起點與 Wire 交接；不能拿異常 `C42` 填補 C10/C25 的缺口。若有新 World socket，需按 PID/remote endpoint/建立時間關聯；不同 Socket 各自 traceId 合理。
3. **A-020/A-028 增量**：CExceptionPacket C42 生成與回報屬原版 crash reporter，可再補 writer 精確 body schema、Client crash log 檔案位置，標 `observed-static`；此路徑**不是 World 授權/登入**。
4. **交 DEV（非分析者自己實作）**：將 C42 類別以 `CLIENT_EXCEPTION_REPORT` 單獨識別（是否收取與限制依安全設計），不能把它當普通 World Packet；安全地存最小例外診斷或只留 metadata，避免未經授權存錯誤內文。補 `IOException` 類型/SocketErrorCode/讀寫階段的去敏欄位以追根因，不接收未驗身分 token，不解除安全 phase gate。
5. **原版 Client CT-107/108**：用現場 PID／Process exit code、Windows Event Log Application Error/WER、Client crash log，關聯 C04→S02(0)→退出／切換，記第二 Socket 的 Client PID。驗證 DB 角色/Email 實際持久化；只有可持續進 World 並收到 S05/S15/C35 才算入圖流程進展。

### 使用者下次需提供／尋找的實際檔案
- **`Crash_as*.log`**：原版 EXE 程式字串明確使用此樣式；請在遊戲安裝/工作目錄與 `%TEMP%` 搜尋最近更新的檔案。若有，先自行檢查/遮蔽帳號、路徑等敏感內容再提供。
- 同時提供 Windows Application Log 中 2026-11-01 **03:38:13～03:38:48（台灣時間）** 的 `Application Error` / `Windows Error Reporting` 事件1000/1001摘要，或 `.dmp`（若系統已有產生；目前未證有 minidump）。找不到 Crash Log，不代表沒有 exception；可能移走、被清理或報告到其他資料夾。

**禁止跨越證據**：Server S02(0) 表示寫出回覆，不等於 Native Client 已進入 World；C42 是例外回報，不是 World 手續；近似時間不證同一 Client PID；無例外 dump 不宣稱特定 crash fault address。

## 2026-11-01 Windows Event 重要校正（RI-007）

使用者補充 Windows Application Error ID 1000 訊息：**失敗的應用程式名稱為 `Asgard-main-menu-preview.exe`**，不是 `Asgard.exe` 原始檔名。先前依原始 `Asgard.exe` 靜態查證 C42=`CExceptionPacket` 仍有效，但**該次 Runtime 記錄不能再被描述為「已在未修改原版 Asgard.exe GUI 上重現」**；預覽副本版本 2.1.2...，實際 SHA 與 native UI 反應仍待記錄。03:38:13 Application Error 與 03:38:17 WER 1001 支援預覽程式發生應用錯誤，仍缺 faulting module/exception code/offset；附近的 .NET Runtime 1000 `GameTcpDiagnosticJournal` 可能是 Server EventLog 日誌，不能直接當 Server .NET 崩潰。

另 03:47:31～33 新的 C03/S03→C10→C25 登入測試，停在 WorldGranted 且無 S05/S15/S14；原因見 [RI-007](20261101-native-c25-wait-and-preview-app-error.md)。本次兩個事件不得混為同一會話、或把 C42 當 World 入口。
## 2026-11-01 完整 WER 事件與測試程式版本邊界（debug-only）

使用者提供完整 Windows `Application Error` 1000 和 `Windows Error Reporting` 1001，**僅供排除錯誤**：

- 2026-11-01 03:38:13（台灣時間）Windows Application Error：`Asgard-main-menu-preview.exe` version `2.1.2.0`；faulting module 同為 `Asgard-main-menu-preview.exe`；`ExceptionCode=0xC0000005`（access violation）；`FaultOffset=0x00141264`（該修改版的 RVA）。
- 03:38:17 WER：`APPCRASH`、P7=`c0000005`、P8=`00141264`，Report ID=`8410ed03-4f93-4691-9b86-0d5ed08b48cb`；WER 曾列可能的暫存 dump 檔 `WER.bc18ed12-1c61-42c9-87f0-db3f3b273470.tmp.dmp`，檔案是否尚存未核實。
- 同時段 Server 的 C02→S02(0)→C04→S02(0) 和 `io-error` 仍是**Server 端操作／輸出事實**，但因本次測試用修改版，**不能當作原版 `Asgard.exe` 在相同後創角 UI 路徑會 crash／不 crash 的證據**，也不能宣告 original Client E2E 成功或失敗。
- **位址推論降級：** `0x00400000 + 0x00141264 = 0x00541264` 僅是映像基址的算術換算；即使原件 `0x00541264` 恰有某指令、且原件 A-028 的 UI callback 曾呼叫附近函式，仍**不證明修改版該 RVA 的 bytes／堆疊相同**。不可把它寫成「原版 Client 的崩潰指令」。除非提供預覽版 hash／RVA bytes／dump 比對，否則這只是修改版的排錯候選，不列入原版分析成果。
- 若需要**排錯**，可唯讀檢查 WER dump 之 exception context、暫存 fault address、call stack、修改版檔案 hash 和預覽版 RVA；此流程不得覆蓋原件 SHA 或污染原版 A-028/A-031 結論。
- **另一路問題保持有效但狀態須精準：** 03:47 的 C03→S03→C10→C25 已在 Server JSONL 觀察到；Server `_worldFixture==null` 於 C25 後 `Continue()` 零回覆是 Server 程式既有設計。這可用於定位**Server 目前沒有啟動原生 World 載入回應**，但若送包者是修改版，並不等於未修改原件的 GUI/World E2E 已實測。

