# A-023 Script／教學入口：可供 Server 設計採用的受限證據

參考 [BIN-first 全文](../task_a/roy2/A-023-analysis.md)。日期 2026-10-31；原版台灣 Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。本頁屬部分研究整合，不是經原生 E2E 驗證的教學初始腳本契約。

## 已確認的 Client 層（observed-static）

- **PKT-C6C**：0x575140 構建 opcode 0x6C；0x575210 serializer 以 subtype 0..4 分岔。0x526626（腳本 API 名 `SendReply`）→0x51a9f0→0x575140 表示腳本有回送 CScript 通道。各 subtype 詳細 wire 欄、何時主動回送 unknown。
- **PKT-S44**：0x5862e0 建構 opcode 0x44，0x4e0b70/0x52c2a0 分派；type1/subtype0..4 各異，type1/subtype3 → 0x5294e0，掃描／操作本地 `Script\\*.dat`（既有研究指出清快取）。**禁止**把 S44 任意 subtype 當作無副作用成功回覆。
- **ScriptRunner/檔案來源**：0x521d32/0x521d84 識別 `client`/`Script`；0x5290bc/0x529351/0x52951d 的 .dat 路徑與 wildcard，表示需處理外部資料。資源研究中 `Born` 是新手對話／座標導引線索，但本輪沒有 Born.dat 檔案可核對。
- **入世界基線**：既有 SCN-001/009 是 S03→C10→C25→S02/S05→S15→S14(1)→C35→S04/S33→S14(2)；不能把這條封包鏈當作首 NPC/Script 已被啟動的證據。

## 對 Server 的契約（安全設計，非原服事實）

- `WorldReady`、`TutorialEntryCommitted`、`TutorialCompleted` 分開；登入/載圖不可默默寫入完成。
- 首個 NPC、Script、任務 UI 是否為必要初始條件、觸發條件、map/npc/script/quest id、payload／拒絕碼全部 unknown：需資源與 A-022/A-011/A-012/A-024 補齊。禁止用測試值冒稱原版。
- 只有取得來源與精確 schema 時才能向 Client 傳送對應 S44；不能以 C6C(03) 最小登入 fixture 取代所有 script 互動。封包重送、stale session、跨 instance 的任務進度須伺服器權威處理。
- 完整 BIN 觀察、失敗路徑、CT 重現腳本見報告。CT-029～031 的 `native_client_validation` 均 `not-run`。

**A gate**：`review`／`handoff_status=partial`，因真正的首教學觸發/任務封包尚缺必要證據。這不是因新 Server 未建立而 blocked。
