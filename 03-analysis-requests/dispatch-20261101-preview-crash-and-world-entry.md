# 2026-11-01 原版 Client / 修改版崩潰 / Native World 後續 — 已建立派工單

**性質**：使用者同意「不先安裝 WinDbg，依目前證據派發分析」。此頁是 **A 後續研究的工作單與責任分派**，不表示任何分析者已接案/完成。沿用已指定的 Roy1、Roy2 工作線；禁止新增 Git Branch、修改 `Asgard.exe`、`Asgard-main-menu-preview.exe`，或由分析角色直接實作 `as_server_roy`。Github Issues 已開，但沒有可確認的 GitHub 個人帳號 assignee；**Roy1/Roy2 是規格工作線 owner，不聲稱人員已認領**。

## 排程與正式 GitHub 工作單

|層級|既有 A 與研究者工作線|已建立的工單|狀態|研究產物與交付關卡|
|---|---|---|---|---|
|**P0**|**A-028／Roy2**|[#7](https://github.com/we88ec3-prog/as_server_spec/issues/7)|queued / awaiting-claim|原始 Client final S02 callback `0x4B206B`→UI 釋放與建構→`0x541250` 的 xrefs/caller/指標生命週期；修改版 Patch 僅除錯候選；對 ADR-008、CT-107 交付 Client-I/O 狀態表|
|**P0**|**A-031／Roy2**|[#8](https://github.com/we88ec3-prog/as_server_spec/issues/8)|queued / awaiting-claim|原始 Client 在 S03/C10/Region3 C25 後能接收何種 World S2C、callback 時序與狀態；交 DEV-ENTRY-04 的 verified vs unknown；CT-108/109 不提前填通過|
|**P1**|**A-020／Roy1**|[#9](https://github.com/we88ec3-prog/as_server_spec/issues/9)|queued / awaiting-claim|原始 `CExceptionPacket` (C42) sender、writer/body/觸發、C62 後例外上報路徑與 Server 可安全辨識的去敏資料；不得把 C42 當 World 入口|

## 已有的可稽核基線（不必等新的工具或原件）

- **原版 `Asgard.exe`** SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；A-028 已確認 final S02 成功後 Region3 建 `LoginDialogPane`；未證其 UI 一定顯示、必然 C03 或自動 World handoff。A-031 已確認 Region3 一般登入 S03→C10→C25 的 3×string8；尚未確認下一個 S2C/原版 UI。
- **修改版只供排錯** `Asgard-main-menu-preview.exe` SHA256 `e834a07d21807748561bafa7e9cca97195234a9b664ea9c20f9e83faafc8cb9d`。WER 2026-11-01 03:38:13 APPCRASH `0xC0000005`，RVA `0x00141264`；經修改版實際 EXE byte diff，該處 `mov [eax+4],edx`，而 Region3 final S02 callback `0x4B212A` 是 `0x541250` 的候選 caller 之一。**缺實際 EAX／堆疊**，不能宣稱這個 caller 已證，也不能反向說原始 EXE crash；可先從原始 EXE 做 xrefs/dataflow，沒有 WinDbg 仍可交付 partial。
- **Server JSONL 只證 Server 處理**：03:38:13 的 Preview 測試 C02→S02(0)→C04→S02(0) 後 `io-error`；另一條 03:38:47 socket 的 C42 不能確知同 PID。03:47:31 一般登入 C03→S03→新 TCP C10/C25(body len16) 之後，Server `WorldGranted` 零回覆；read-only `as_server_roy@e93c9a17` `LoginWireSession.case 0x25` 的 `_worldFixture=null; return Continue()` 可解釋 Server 不發 S05/S15/S14。**此為已知 DEV 配置／實作缺口，不能讓 A 研究者自行修改程式**。
- Windows Event 1000/1001 及原件靜態 C42 RTTI 都有證據，但不能跨不同 client binary、不同 socket、不同事件推斷同一因果。

## 任務執行規範與不得重複項目

1. 已有 **A-028 `integrated/partial`、A-031 `integrated/ready`（已證 C25 static 子集）、A-020 `integrated/partial`** 不得因新的失敗重設為 `open`。本輪 follow-up 是 **queued/awaiting-claim**；有人接手才改 `analyzing`，原先已證的主體狀態保留。
2. 優先做不需 WinDbg 的 EXE xref、RTTI、serializer、callgraph、UI state/dataflow 與既有去敏 Log 對照；缺 WER `.dmp` 時直接寫 `EAX/call stack=unknown`，不能因此擋住可交付的靜態部分。
3. 完成的報告以 `A-EVIDENCE-HANDOFF-v1` 呈現 `trigger, client_sends, client_receives, client_reaction, evidence(original VA+SHA), unknowns`；測試版的結論獨立標 `modified-preview-debug-only`；`native_client_validation=not-run`。
4. 請沿用既有 `task_a/roy1`／`task_a/roy2` 分支（若該分析者已在使用），不要建立新分支；**派工文件在 spec/main 整合不等於要求分析者將自己的分支 rebase**。避免覆蓋同時修改中的研究結果。
5. 交 Server DEV：`DEV-ENTRY-04` Native C25 後下發真 World map/position/CRC、避免無期限無回覆；C42 原生例外上報的安全最小診斷。A 不重做 C25 3×string8／A-032 C35 pair／C02 NAME/E-MAIL 已證部分。
6. **目前不缺新原件**：既有 `Asgard.exe` 和此測試版都已提供；將來若要確定崩潰時 EAX/caller，可能需要 `*.dmp`，但這是**可選的動態驗證資料**，不是派工及原件靜態分析的開工前提。

## 對應紀錄

- RI-006 Preview APPCRASH：[#7](https://github.com/we88ec3-prog/as_server_spec/issues/7)、[RI-008 修改版 Binary Diff](../04-analysis-integration/20261101-preview-exe-crash-debug-diff.md)、[RI-006／007 原因校正](../04-analysis-integration/20261101-native-c25-wait-and-preview-app-error.md)。
- RI-007 Server C25 零回覆：[#8](https://github.com/we88ec3-prog/as_server_spec/issues/8) 與 [World 入圖規劃](../02-server-planning/roy123-playable-world-implementation-20261101.md)。
- 原版 C42 類別：[#9](https://github.com/we88ec3-prog/as_server_spec/issues/9)、[原件 CExceptionPacket 證據](../04-analysis-integration/20261101-postcreate-c42-exception-report-evidence.md)。

**審查結束條件**：各分析者回報與原件來源比對後，更新 A/04-analysis-integration/DEV-ENTRY/CT 的已證與未知。不以 GitHub issue 已建立當研究完成；只有實際證據才能更新 `handoff_status`。
