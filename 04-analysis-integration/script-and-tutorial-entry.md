# A-023 Script／教學入口：可供 Server 設計採用的受限證據

## 最新核查：封包啟動與關閉回送

已追通 S44(1,0) 指定名稱／context／文字 CRC／依賴／參數，資源齊備後 0x52c2a0→0x52bd30→0x524fa0 呼叫 Main；缺檔由 C6C(0) 請求、S44(1,1) 更新後重試。Born.Main 需 PaperDialog 函式依賴。原服首次登入何時發送、使用何種帳號／任務旗標仍未知，與 Client 機制分開。

PaperDialog 關閉時的 client.Dispose 會送 C6C(4,name,context)，並在尚未 SendReply 時再送 C6C(2,name,context)；因此舊段落「Main 無顯式 SendReply」不得被當作沒有回包。這些是 script lifecycle，不能直接等同教學完成。精確 schema、位元組序／CP950 條件、CRC、清快取與 mismatch 風險、原始位址和合成向量見 [A-023 完整 Client 契約](../task_a/roy2/A-023-script-entry-contract.md)。後續與本段衝突的早期 unknown 敘述以此段及完整契約為準。

參考 [BIN-first 全文](../task_a/roy2/A-023-analysis.md)。日期 2026-10-31；原版台灣 Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。本頁屬部分研究整合，不是經原生 E2E 驗證的教學初始腳本契約。

## 已確認的 Client 層（observed-static）

- **PKT-C6C**：0x575140 構建 opcode 0x6C；0x575210 serializer 以 subtype 0..4 分岔。0x526626（腳本 API 名 `SendReply`）→0x51a9f0→0x575140 表示腳本有回送 CScript 通道。各 subtype 詳細 wire 欄、何時主動回送 unknown。
- **PKT-S44**：0x5862e0 建構 opcode 0x44，0x4e0b70/0x52c2a0 分派；type1/subtype0..4 各異，type1/subtype3 → 0x5294e0，掃描／操作本地 `Script\\*.dat`（既有研究指出清快取）。**禁止**把 S44 任意 subtype 當作無副作用成功回覆。
- **ScriptRunner/檔案來源**：0x521d32/0x521d84 識別 `client`/`Script`；0x5290bc/0x529351/0x52951d 的 .dat 路徑與 wildcard，表示需處理外部資料。資源研究中 `Born` 是新手對話／座標導引線索，但本輪 Born.dat 原件已被核對（A023-E09/E10）。
- **入世界基線**：既有 SCN-001/009 是 S03→C10→C25→S02/S05→S15→S14(1)→C35→S04/S33→S14(2)；不能把這條封包鏈當作首 NPC/Script 已被啟動的證據。

## 對 Server 的契約（安全設計，非原服事實）

- `WorldReady`、`TutorialEntryCommitted`、`TutorialCompleted` 分開；登入/載圖不可默默寫入完成。
- 首個 NPC、Script、任務 UI 是否為必要初始條件、觸發條件、map/npc/script/quest id、payload／拒絕碼全部 unknown：需資源與 A-022/A-011/A-012/A-024 補齊。禁止用測試值冒稱原版。
- 只有取得來源與精確 schema 時才能向 Client 傳送對應 S44；不能以 C6C(03) 最小登入 fixture 取代所有 script 互動。封包重送、stale session、跨 instance 的任務進度須伺服器權威處理。
- 完整 BIN 觀察、失敗路徑、CT 重現腳本見報告。CT-033～035 的 `native_client_validation` 均 `not-run`。

**A gate**：`integrated`／`handoff_status=partial`，因真正的首教學觸發/任務封包尚缺必要證據。這不是因新 Server 未建立而 blocked。

## Born.dat 新證據

直接 Script 依賴已補查（A023-E12）：`PaperDialog.dat` 定義 Born 所需的 `PaperDialog_Create` 及翻頁／關閉 callback。Born 單頁資料使 PREV/NEXT 隱藏，預設／取消均指向 OK；OK 依序呼叫 `dialog.Dispose`、`client.Dispose`。資源沒有顯式 SendReply 或 quest 修改，native Dispose 內部效果仍未知。視覺引用為 `Basic.dat/AlertFrame.ypf` 與按鈕 object 11/12/13，尚未驗證視覺資產載入。詳見報告 A023-E12 與 `task_a/roy2/entry-dependency-verification.json`；不可把關閉紙張視窗當成原服任務完成。

589-byte zlib SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98` 解壓為 1154-byte UTF-16LE XML，唯一 `Main` 執行 `client.CreateArray` → `page.Insert` → `PaperDialog_Create`；紙張引導提及 **(31,29)** 女性招募員與滑鼠點選。這個座標**不是已證實出生點**。本 Main 無顯式 NPC/quest/SendReply，是否首次自動觸發與 NPC/quest ID 仍 unknown。另 EXE IAT `0x5f11fc=DeleteFileA` 確認 S44 Script 清除風險。見 [資源機讀摘要](tutorial-born-resource.json) 和 [驗證工具](../task_a/roy2/verify_born.py)。

## 2026-11-01 A-023 精確原件增量（E19～E24）

本回合原始 `Born.dat`、`Basic.dat` 皆在模型側實際解讀、比對 hash；Basic indexed DAT **39 slots/38 members**，`AlertFrame.ypf` 偏移13196、長177648、SHA `b641441d1f0378de04b6f7929c333d95e6ad7df451f3927432e5c4d0305602ce`，YPF **17**；搭配 Born.Main **CP950 text CRC `1d87b0c0`** 證明紙張依賴的原始 Frame 資料確實存在，**不是** GUI 已成功顯示。PaperDialog.dat 的 XML 是既有歷史報告的來源，該檔本輪未上傳，不能稱重跑原件全鏈。

額外原件 22 VA native-static：`S44(2,0)` 外層 handler 對 **UI slot0x23**／components3/4；`S44(2,2)` 操作 **slot0x24**；兩者均需與 `S44(1,0)→ScriptRunner Main` 分開，不可用 type2 偽造 Born start 或 script ACK。既有 `C6C(4)`＋`C6C(2)` Born normal close **不表示** quest 完成。完整精確證據與 21 合成邊界測試：[A-023 補證](../task_a/roy2/A-023-born-basic-native-dispatch-20261101.md)、[CT-114](../05-conformance/A-023-original-born-basic-ui-test-plan.md)。

**Server gate**：P0 登入／地圖顯示／可移動不須等待原服未知的第一名招募員或 Born 自動發送政策。P1 本地 Script schema/資源/安全 runner 可開發；真正 first-login S44 push、NPC EntityId/map/spawn、NPC→nNewJoin01/Quest flags 仍 unknown，Native CT-034/035 `not-run`。不要延用上文將 `S03→C10→C25` 當所有 region/第一次創角必須路由的舊推定；A-028/A-031 已證明應分路。

## A-023／2026-11-01 四份原版 Script 原件補齊（E25～E33）

此前 PaperDialog 原件缺口**已在本回合實際補齊**：`PaperDialog.dat`／`PaperDialog02.dat`／`nNewJoin01.dat`／`Merchant.dat` 全部 SHA/strict zlib/UTF16LE XML/CP950 text CRC 與函式表通過。由此 [完整證據](../task_a/roy2/A-023-four-script-native-dependencies-20261101.md)、[檔案機讀資料](../task_a/roy2/a023-four-script-verification.json) 可證 Born.Main 呼叫 PaperDialog_Create；普通 PaperDialog OK **不** SendReply，依原生 C6C4→C6C2 關閉。

`PaperDialog02` OK→`PAPER02=START`、CANCEL→`PAPER02=NOT`；卻設 `cancelControl="OK"`，ESC 原生 GUI 將觸發哪個分支仍要 CT。該腳本自己**沒有 Main**，使用外部 ClientReply。 `nNewJoin01` 23 個函式、沒有 Main；MerchantTalk→三頁 QuestDialog，OK→`STATE=ACCEPT`、CANCEL→`STATE=REFUSE`；`Merchant.Main` 提供 Script root 候選與 ServerParam／ClientReply。**真正 C6C1 script name 是 S44 ScriptRunner root，不是回覆函式所屬的 nNewJoin01 依賴檔名**。原生 SendReply→C6C1，再 Dispose→C6C4，replied flag 不再走未回覆清理 C6C2。

這四檔仍**沒有** `QuestDialog_Create`、`MerchantDialog_Create`、`MerchantDirectTalk` 函式定義；`QuestDialog.dat` 和 `MerchantDialog.dat` 只是待查候選名字。兩種 PaperDialog 的 `ShowIndexedHelp/PaperDialogProc` 名稱碰撞也未做原版跑圖實測。原服女招募員 NPC/entity→Script 綁定與任務旗標、首次 Born 時機仍 unknown。CT-115 離線驗證＋28 synthetic tests PASS；**CT-034/035 原生 GUI not-run**，A-023 保留 `integrated/partial`。
