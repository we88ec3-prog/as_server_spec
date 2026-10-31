# CT-114 — Server TCP 封包收發日誌／預期外標記／與驗證失敗 Log 分流
2026-11-01｜R-037／ADR-009，`planned`，`native_client_validation=not-run`。

1. 用本機 Server 以合法 seed0 AA frame 送 C62、C00、C02（若啟用合法 Region）、C03 和 World C10/C25；不同連線、新 TCP grant 各有 TraceId。每個有效 Client 封包有 `C2S`、每個 WriteAsync 成功有 `S2C`，關線摘要與包事件相同 `TraceId`，時序與 phase 可追溯。
2. 證明 TCP 分段與合併 frame 不會漏記、重複紀錄，不暴露未完成／畸形 AA payload 的內容；格式錯誤為 `[UNEXPECTED_PACKET]` 與可辨原因；未知 op、合法 op 不合法階段、Server 未支援但原 Client 會送的 opcode 要不同 reason_code。
3. 一般密碼錯、創角重名、Client 合法取消、碰撞拒移等（**僅對已實作且原生回覆可證的功能**），不得只留 `[PACKET]`；依 ADR-009 顯示 `[VALIDATION_FAILED]` 或 `[REQUEST_CANCELLED]`，不錯當 `[UNEXPECTED_PACKET]`；Server 是否斷線與 error S2C 是否送出要準確記錄。
4. 掃 Console 與 `data/diagnostics/game-packets-YYYYMMDD.jsonl`、`game-tcp-YYYYMMDD.jsonl`、版本支援的 validation/cancel 檔：不得有 ID、NAME、EMAIL、密碼、token、raw body、billing 和敏感 exception／IP；只允許固定 reason code、metadata、匿名 TraceId。
5. 驗證開關 `Asgard:Game:PacketLog:Enabled`、UTC 日期旋轉、7日留存與檔案權限；日誌磁碟滿／寫入失敗不使 TCP host crash；大量封包應有可說明的容量及性能界線，禁止日誌影響授權/sequence/World 行為。
6. S2C `sent` 僅證實 Server write 完成，不表示原版 Client 顯示；需另外用不修改的 `Asgard.exe` UI 和去敏 TCP trace 驗正向／錯誤回應。原版 Client 的完整創角/進圖/移動仍由 CT-107～109 另行驗。
7. 錄入 Server 程式 build SHA、Client SHA、Region、UTC 時間、OS、DB provider；合成 Codec/CI 通過只可標 `synthetic-passed`，不可以變更 `native_client_validation=not-run`。

驗收標準：逐包 metadata、分類、隱私、拒絕語意、安全、輪轉都通過；分析／規劃角色只收件、比對、回報，不直接改 Server。規格來源 [R-037 回補](../02-server-planning/game-packet-log-contract-and-backfill-20261101.md)、[ADR-009](../02-server-planning/expected-validation-failure-policy-20261101.md)。
