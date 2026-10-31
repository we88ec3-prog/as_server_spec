# A-015 → CT-039/CT-040：資源版控／新手地圖實測計畫

**執行者**：後續 DEV/CT；`native_client_validation=not-run`。參考 [A-015](../task_a/roy2/A-015-analysis.md)、[資源目錄](../04-analysis-integration/content-resource-catalog.json)、[metadata probe](../tools/a015_content_probe.py)；所有原始遊戲資料只留分析者本機或合法私有來源。

## CT-039 本機結構／身分（planned）

1. 相符 `Asgard.exe` SHA256 必須是 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；逐檔記錄路徑、來源權限、SHA256、大小、Client版本和是否可在個人合法使用範圍內處理。不要推原始 MAP/Script/YPF/DAT 到 repo。
2. `python tools/a015_content_probe.py /path/to/owned-client/resources --json /private/path/a015-metadata.json`；確認檔案身分且 archive offsets 首尾/sentinel 合法；MAP 對 bounds/7/8/16 區段恰好 EOF；Script zlib+BE length/UTF-16LE。
3. 本輪已跑 **synthetic unit checks**（4×4 map、單 member DAT、合成 Script）與真 `Born.dat`，結構正向 PASS；故意截短的 MAP/DAT、壞 zlib 拒絕。這不是原版全量素材掃描：對資源組的 CT 狀態仍 `planned`，不能把 unit-pass 誤記成 native-pass。
4. 不符合 schema 的檔標 unsupported/corrupt 或版本不匹配；不可解壓後混用其他版索引。每個 member SHA、讀取規則、字段 unknown 分離。

## CT-040 原生教學內容鏈／地圖（planned）

1. 本輪已取得 3 庫 MAP 並完成靜態解析；後續須先確認它們與原 Client 發行版本相符，再取得真實教程 map id、依 `A-022` map loader 找實際新手 map id；取得真 C35 header(+4) 和 parsed checksum（不可用 raw CRC），確認 Server 送的 S15/S14(1)→C35→S04/S33→S14(2)。
2. 進圖後記真出生 x/y/facing 和 map id、招募員可見性的 NPC entity ID、是否觸發 Born.Main、第一次互動對話與 Script/C6C/S44 真 bytes。**Born 的 (31,29) 是對話目標不是出生座標**。
3. 驗證錯版 / 缺 map、checksum 不符、載圖中斷、重登、斷線不誤標任務完成、不重領。任何不確定的客戶端行為標 `unknown`，不可填合成 NPC 或自編教程 map 假冒原版。
4. 實際成功/失敗、截圖/trace 在私有測試留存，公開共用資料只保留經審查的必要結果；一律區分 `observed-runtime` 和 `designed`。

此頁是測試**計畫**，不是 CT-039/040 真正執行後的 E2E 驗收。

## 內建合成測試

`python -m unittest discover -s tools -p 'test_a015_content_probe.py'`：合成 map 4×4、DAT sentinel、zlib Script 的成功及失敗例；損壞的 DAT 嵌入地圖應直接失敗，不能混入合法 metadata。此為開發者離線單元測試，不得冒稱 CT-040 原版 Client E2E 完成。

## 補充：真實 MAP 索引結構驗證（A015-E09～E13）

本輪用上傳原件執行 Map0/Map1/Map2 全庫校驗，**494/494 靜態解析 PASS**；以原始 SHA 鎖定三份檔案，保留 330 unique payload、33 duplicate groups、477 coordinate-in-bounds 的負面定位結論。這是 **CT-039 的本機資源離線檢查部分已執行**，但 CT-039 整體仍 planned（YPF/技能物品/來源權利尚無全量原檔）。CT-040 原生 Client 仍 not-run；絕不可因 494 MAP 可讀而將教學 spawn / NPC / C35 視為通過。

原始 3 庫的可重現離線工具：`python tools/a015_map_corpus_verify.py Map0.dat Map1.dat Map2.dat`；內建合成測試：`python -m unittest discover -s tools -p 'test_a015_map_corpus_verify.py'`。只處理有權合法持有的個人本機遊戲資源，不把資源 bytes 輸出到 repo。

## CT-039 補充 MAP 欄位級驗證

`python task_a/roy2/a015_field_audit.py Map0.dat Map1.dat Map2.dat` 可再驗 494 張 MAP 的 7/8/16-byte 型別、標頭差異與候選 48×32 座標範圍；`python -m unittest discover -s task_a/roy2 -p 'test_a015_field_audit.py'` 是 4 個合成正反向測試。已 PASS 的是**離線原件結構與合成測試**，整體 CT-039 仍 planned，CT-040 原生 Client E2E 仍 not-run。禁止將候選像素座標直接當成官方 NPC 或角色出生點。

## 研究交付與原生 CT 分離 — A-015 ready / CT still planned

A-015 按明確的 metadata／格式／版權研究範圍交接就緒（[結案審查](../task_a/roy2/A-015-closure-review.md)）；本地原始檔驗證 494 MAP / Born 及合成 Script 長度 >65535 測試可重跑。不把此記為完整 CT-039：**CT-039 依然 planned**（缺其他原件／來源版配對），**CT-040 依然 planned、native_client_validation=not-run**。新 Script 長度 header = BE u16 version + BE u32 UTF-16LE code-unit count。任何 map ID、NPC、spawn、server-side skill/item 均留原專責 A / CT，不能因 A-015 ready 而宣告原生教學可玩。
