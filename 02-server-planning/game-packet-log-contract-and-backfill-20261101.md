# R-037：Server 封包收發、預期外封包與去敏診斷 — 過往越界實作補登／正式規劃

2026-11-01。**角色分工：此文件是 `as_server_spec` 的分析／規劃回補；並非本次 Server 開發指令已完成、也不是原版 Client 實測。**

## 0. 來源與已存在的 Server 實作（read-only source audit）
- 2026-11-01 分析者曾未經明確授權，直接修改 `as_server_roy/main`。非正當授權範例；須在交接中揭露而非隱去。首次程式 commit `95977823e7fa9c177e3ae4314e835fda6c9d7a8e`，隨後文件 commit `71ebd25954386609fa224f3267f7ae5942fd0354`。
- 原程式增：`GameTcpProbeService.cs` 入站/出站逐包呼叫 journal；`GameTcpDiagnosticJournal.cs` 純 metadata JSONL；`GamePacketExpectation.cs` phase/Opcode 分類；`LoginWireSession.cs` 僅觀察性 `InspectInbound`；設定 `Asgard:Game:PacketLog:Enabled` 預設 true；`GamePacketExpectationTests.cs`；`docs/game-packet-logging.md`。
- 2026-11-01 唯讀再次核對私有 Server `main@a86e28cf9946971cee5bd244b248ff9ef52be34e`：上列逐包記錄仍在；其後**其他開發提交**另增 `[VALIDATION_FAILED]`／`[REQUEST_CANCELLED]` 結構化事件與實驗性原生 S02 錯誤分支。這不是本分析者執行的更新、不得因 source existence 標記任何 native Client UI 成功。
- **此補登不修改 `as_server_roy`，不重推程式，不建立/刪除分支，不回退或 cherry-pick 他人提交。** 若需移除先前越界實作，須由 Server 擁有人決策，交 Server 開發者執行；分析者不再改 Server。
- 之前 RI-005 規格只規劃一條 TCP close 摘要；ADR-009/R-036 規劃業務驗證原因 Log；**兩者不能取代完整逐包收發與預期外封包契約**，本 R-037 專門回補。

## 1. 期望功能與實作／驗證分層

|領域|規格要求|read-only Source 狀態|不代表|
|---|---|---|---|
|逐包 C2S|僅在 AA frame + codec 成功後記每筆 decoded packet，包含 UTC、方向、op、body length、ordinal、before/after phase、traceId、build、disposition|**已在 Host 實作**|不是 Client UI/native 可運作|
|逐包 S2C|每次實際 `NetworkStream.WriteAsync` 成功後記一筆 response metadata；發送失敗另有 error/close reason|**已實作**|Server write 成功不是 Client 接收/顯示|
|封包異常|未知 Opcode／錯 phase／不支援狀態／AA malformed 以 `[UNEXPECTED_PACKET]` 與穩定 `classification` 辨識|**已實作 metadata classifier**，只代表目前 Server 支援範圍|未知不等於 Client 違規；不可從標籤直接踢線|
|連線結束|保留既有 `game-tcp-YYYYMMDD.jsonl` close summary，統一 TraceId|**已實作**|不可混淆正常 S03 transfer、業務拒絕與 timeout|
|預期內驗證失敗|另外記 `[VALIDATION_FAILED]` `reason_code`、`response_sent`、退回階段、是否保持 socket；**不標為 `[UNEXPECTED_PACKET]`**|**此契約另屬 ADR-009/R-036；較新 Server 程式已增部分事件**|僅有事件仍不等於原生錯誤 status/UI 已實測|
|使用者取消|合法 C15 等屬 `EXPECTED_CLIENT_CANCEL`，與驗證失敗分開|**較新 Server 程式已增 `[REQUEST_CANCELLED]` 事件**|是否保留同一 socket 仍需原 Client trace|
|資料保護|禁止記 decoded/raw body、ID、密碼、NAME、EMAIL、token、billing、IP、SQL/自由文字；允許固定拒絕碼與匿名 TraceId|**程式欄位表面為 metadata**；須在 CT-114 查意外訊息／例外|沒有實證隱私測試不得宣稱全程不洩漏|

不同 `as_server_roy` commit 可能已變更行為；**標記 observed-source（指定 SHA），不是已由本分析者在 Runtime 重新驗收**。後續檢查應優先核對最新 Server build 與實際本機執行版，並把版本寫入 CT。

## 2. 機讀事件與 Console 契約
- 一般 C2S/S2C：`[PACKET]`，欄位 `AtUtc`、`TraceId`、`Build`、`Direction`、`Opcode`、`BodyLength`、`WireOrdinal`（可能 null）、`PhaseBefore`、`PhaseAfter`、`Unexpected=false`、`Classification`、`Disposition`；新版本可能另外帶 `S02Status`。只有**原生已證** status 才能宣稱其業務語意。
- 真正異常封包：`[UNEXPECTED_PACKET]`（warning）／JSONL `Unexpected=true`、`Classification` 必可辨 `unknown-opcode`、`out-of-phase`、`invalid-aa-frame`／`invalid-packet-codec`、`handler-rejected-unknown-state`、`world-movement-handler-not-implemented` 等已定義分支。新 opcode 解析完成/Server 實作後需更新 classifier，避免永久錯標合法原生包。
- 預期內業務拒絕：`[VALIDATION_FAILED]` + reason_code（例如 `AUTH_INVALID_CREDENTIALS`、`CHAR_NAME_TAKEN`）；成功送 S2C 的事實、已證原生 status 和 Client 顯示事實**三層分開**。參 [ADR-009](expected-validation-failure-policy-20261101.md)。
- 使用者取消：`[REQUEST_CANCELLED]`，不能顯示成未預期包或驗證錯誤；嚴重授權竄改/未知格式應另外標 `SECURITY_FATAL`／`PROTOCOL_UNEXPECTED`。
- 日誌是診斷，**不得變更協定處理器的授權決策**：`InspectInbound` 只分類，不允許透過該分類略過身份授權、C35、移動碰撞、限流或 epoch；亦不可因 `Expected=false` 自動把正常功能失敗視為必須斷線。
- Log 缺漏風險：資料若在未完成 frame 前斷線，只有 `invalid-aa-frame`／close 摘要，不該捏造 Opcode/內容；單次 Socket read 可包含多 frame；不要將兩次讀取當兩包。

## 3. 路徑、開關、保存與隱私
- 現有程式輸出到 Server **啟動工作目錄**下 `data/diagnostics/`：`game-packets-YYYYMMDD.jsonl`（逐包），`game-tcp-YYYYMMDD.jsonl`（連線結束）；較新版本另有 `game-validation-YYYYMMDD.jsonl` 與 `game-cancel-YYYYMMDD.jsonl`。
- 日期以 **UTC**、逐日滾檔、best-effort 最近 7 日（相對於寫入事件時清除過期檔）；目錄與檔案僅保留本機，不公開上傳原始封包或資產。
- 設定 `Asgard:Game:PacketLog:Enabled`（環境變數 `Asgard__Game__PacketLog__Enabled`）預設 true；關閉只應影響逐包 metadata，不能無意關閉 close summary／必要拒絕原因 Log。除錯開關不解除服務端限本機綁定與 credential 權限。
- 失敗安全：日誌寫檔 IO/權限錯誤不應殺掉 Game listener；記有界 warning；大量封包的吞吐/磁碟壓力、檔案輪轉誤清、崩潰時末尾資料遺失需另測，不把 best-effort 當強持久交易。
- 事件內容與錯誤原因必須由固定白名單產生，不把 `Exception.Message`、使用者表單文字或解密 payload 洩露到 Console/JSONL。

## 4. 待 Server 開發者處理／禁止分析者直接實作
|交接|指定 Server 檔案或責任|驗收|
|---|---|---|
|`DEV-LOG-01` 回補規格一致性|Host `GameTcpProbeService.cs`／`GameTcpDiagnosticJournal.cs`|C2S/S2C/close 同一 TraceId，表單敏感內容沒有被寫入，entry 只在對應 read/write 階段發生|
|`DEV-LOG-02` classifier 校正|Host `GamePacketExpectation.cs`／`LoginWireSession.cs`|語意「目前 Server 未支援」與「真正畸形/攻擊」分開；新功能接通後更新 known opcode/phase|
|`DEV-LOG-03` 驗證失敗對接|ADR-009／`DEV-REJECT-01..06`|業務拒絕有 `[VALIDATION_FAILED]` 精確安全原因，不只是 `[UNEXPECTED_PACKET]` 或 socket close；Client 可理解回覆/安全重試，原生 status 未證標 blocked|
|`DEV-LOG-04` 運維|啟停、設定範例、日誌輪轉／權限|UTC 檔案與本機目錄、預設開啟可停用、7日留存、IO 失敗不使遊戲崩潰；Load 下有界|
|`CT-114` 獨立驗收|Server CI + 本機 Client 去敏觀察|依 [驗收清單](../05-conformance/game-packet-observability-acceptance-20261101.md) 分別記 synthetic／native，不能說有 Log 就等於創角/入圖 E2E PASS|

以上 DEV-LOG 為**交接審查與缺口切片，不要求重新編寫已存在的程式**；任何 Server 變更只可由獲授權的開發角色進行。分析者只可更新 `as_server_spec`、核查 `as_server_roy` 既有內容。

## 5. 進度標示
- **原有 server commit：source-implemented（至少逐包 metadata 記錄）**；且 GitHub Actions 在先前程式提交 `95977823` 時曾成功，**不是本次新驗證**。
- **規格回補：specified／tracked**，CT-114 `planned/not-run`；不因本次補規格 retroactively 假稱有原生 Client 驗收。
- **後續需核查**：從真 Client 產生之每一 S2C/錯誤是否仍同 TraceId、驗證回覆 UI、異常與預期內業務拒絕的區分、日誌的隱私及壓力邊界。CT-105/107/108/109/112/113 全部仍須各自實測。
