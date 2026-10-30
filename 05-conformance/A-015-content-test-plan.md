# A-015 → CT-037/CT-038：資源版控／新手地圖實測計畫

**執行者**：後續 DEV/CT；`native_client_validation=not-run`。參考 [A-015](../task_a/roy2/A-015-analysis.md)、[資源目錄](../04-analysis-integration/content-resource-catalog.json)、[metadata probe](../tools/a015_content_probe.py)；所有原始遊戲資料只留分析者本機或合法私有來源。

## CT-037 本機結構／身分（planned）

1. 相符 `Asgard.exe` SHA256 必須是 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；逐檔記錄路徑、來源權限、SHA256、大小、Client版本和是否可在個人合法使用範圍內處理。不要推原始 MAP/Script/YPF/DAT 到 repo。
2. `python tools/a015_content_probe.py /path/to/owned-client/resources --json /private/path/a015-metadata.json`；確認檔案身分且 archive offsets 首尾/sentinel 合法；MAP 對 bounds/7/8/16 區段恰好 EOF；Script zlib+BE length/UTF-16LE。
3. 本輪已跑 **synthetic unit checks**（4×4 map、單 member DAT、合成 Script）與真 `Born.dat`，結構正向 PASS；故意截短的 MAP/DAT、壞 zlib 拒絕。這不是原版全量素材掃描：對資源組的 CT 狀態仍 `planned`，不能把 unit-pass 誤記成 native-pass。
4. 不符合 schema 的檔標 unsupported/corrupt 或版本不匹配；不可解壓後混用其他版索引。每個 member SHA、讀取規則、字段 unknown 分離。

## CT-038 原生教學內容鏈／地圖（planned）

1. 先取得合法的相符 `Map0/1/2.dat`、依 `A-022` map loader 找實際新手 map id；取得真 C35 header(+4) 和 parsed checksum（不可用 raw CRC），確認 Server 送的 S15/S14(1)→C35→S04/S33→S14(2)。
2. 進圖後記真出生 x/y/facing 和 map id、招募員可見性的 NPC entity ID、是否觸發 Born.Main、第一次互動對話與 Script/C6C/S44 真 bytes。**Born 的 (31,29) 是對話目標不是出生座標**。
3. 驗證錯版 / 缺 map、checksum 不符、載圖中斷、重登、斷線不誤標任務完成、不重領。任何不確定的客戶端行為標 `unknown`，不可填合成 NPC 或自編教程 map 假冒原版。
4. 實際成功/失敗、截圖/trace 在私有測試留存，公開共用資料只保留經審查的必要結果；一律區分 `observed-runtime` 和 `designed`。

此頁是測試**計畫**，不是 CT-037/038 真正執行後的 E2E 驗收。
