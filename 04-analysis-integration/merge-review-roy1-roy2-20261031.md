# Roy1 / Roy2 最新研究整合與原始資料交叉驗證（2026-10-31）

## Git 來源與處理

- main baseline：`8e4f42ddd1338890386c4f6bf4ebcdbfe3916c99`。
- Roy1 head：`fd189fc74fd7897558d03322fe19e6a0809568c1`，有 A-011、A-022 及新增 A-013 經濟協定研究。
- Roy2 head：`81d3a2ba77ff7ec4ab8e1b6323664315883ea0b5`，有 A-015 MAP 全庫與碰撞/座標的新原始證據。
- 整合採 main 的 JSON/CT/密碼等既有正式政策為基準，**新增兩側唯一成果、保留兩邊 branch 歷史（不覆寫 analyst branch）**；由 main 的三親 merge commit 對接兩條分支。分析者可以從原分支歷史看到原始研究的勘誤前後。沒有修改 `Asgard.exe`，也沒有上傳原始遊戲 DAT 資產。

## 交叉核對與衝突修正

1. 原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。Roy2 A-015 的 **26/26 native VA byte anchors PASS**；Roy1 A-013 的 **18/18 VA anchors + 6 RTTI 名稱 PASS**（本輪重新依原始 EXE 核對，非 Client GUI）。
2. 三張 MAP 原始庫 SHA 相符，Map0 **288**、Map1 **184**、Map2 **22**，共 **494/494 MAP**，**7,701,805 raw tile**，全部 block/tile/tail exact EOF。Roy1 原程式把第一個 map 的 payload 由正確的 `4+36*n` 錯讀成 `8+36*n`，多跳4B，把首筆 `00000.map`、`10000.map`、`20000.map` 誤判為不合法「特殊空圖」；原件不支持其 491/494 結論。**已改寫 Roy1 報告與工具採 Roy2 正確的 offset-first 36B indexed DAT reader**。
3. 真的已證：`x+y*width` grid address、Client 10B raw tile→17B runtime tile、48×32 畫面候選、tile bit0 runtime set/clear、bit4 line test、獨立 u32 auxiliary grid。**仍未證玩家全圖可走、合法 spawn、出生的原版 MAP ID、C35 第二欄 structured checksum**。
4. Roy1 A-011 的 43個 Monster 資源庫 ID 8000..8042、S1A Motion/C39 Merchant bounded codec 與 Roy2 已知 Client ImageID/MonsterObject 證據不衝突；`Monster00.dat`、`World00.dat` 已提供各5個 YPF 成員，但「image slot = YPF member = EntityId」**不成立、未證**。
5. Roy1 A-013 新增 C4A/S42 Exchange、C17/S6E Trade、C39/S2F Merchant 具證據的 codec/reader；**無證**原版 Exchange 一定是倉庫、原服物價、買賣流程、玩家交易確認/取消與完成後 UI。Server transaction/ledger 是**designed**，原始 GUI native E2E 仍 not-run。

## CT ID 衝突已解決

- main CT-001～086 完整保留，包括 CT-069 音樂、CT-070 兩原 Client AOI、CT-054 原生創角、CT-055 多人共享圖。
- Roy1 A-013 新增 **CT-087、CT-088、CT-089**（經濟／商店／玩家交易）。
- Roy2 A-015 分支原 CT-087/088 改為 **CT-090**（MAP 離線解析）、**CT-091**（原生 Client 撞牆／移動），更新 `requests.json`、`vectors.json`、`client-io-flow-matrix.json`、`traceability.csv`、研究及驗收計畫。
- 原件 static/offline/synthetic PASS **不等於**原 Client E2E passed，所有新 CT status `planned` 且 `native_client_validation=not-run`。

## 需求與下一步

[Server 迭代](../02-server-planning/map-resource-actor-plan-20261031.md) 依 DEV-060 → DEV-070-M → DEV-090 安全實作，經濟 Domain 可並行。需要 A-005/A-015/A-022 的 Client 角色真正移動／碰壁與 C35 checksum，A-011/024 Monster ImageID→YPF/Motion/NPC click，A-013 交易／商店 GUI trace，A-027 無角色已登入創角路徑。**沒有新增必需資源檔名**；已有 `Asgard.exe`、`Map0/1/2.dat`、`Born.dat`、`Monster00.dat`、`World00.dat`、`nNewJoin01.dat`、`PaperDialog.dat`、`PaperDialog02.dat`。若後續定位需要其它素材，才用實際 Client reference 指定 `MonsterNN.dat` 或 `Basic.dat`。

**使用者政策不倒退**：原 Client 不修改，遊戲密碼4～8字（DEV-030 私有程式尚須改），管理員建帳、創角帳號輸入不符登入 owner 則拒絕、同地圖多人共用 NPC/怪物。
