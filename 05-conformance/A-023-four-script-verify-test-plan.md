# CT-113／A-023：四份原版 Script 依賴、選項、C6C 名稱與安全性（2026-11-01）

對應 [四份真實 Script 的完整原件分析](../task_a/roy2/A-023-four-script-native-dependencies-20261101.md)／[版本與函式機讀報告](../task_a/roy2/a023-four-script-verification.json)。**原始資源可直接離線驗證**；Client GUI、TCP runtime、原服 NPC 綁定、原服 quest 政策仍 `not-run / unknown`。

## 一、原件驗證（本機、read-only；不把原始 DAT 放 Git）

```bash
python task_a/roy2/a023_script_bundle_probe.py --script-dir <四份dat所在目錄> --born <Born.dat完整路徑>
python task_a/roy2/a023_born_basic_probe.py --born <Born.dat完整路徑> --basic <Basic.dat完整路徑> --paper <PaperDialog.dat完整路徑>
```

確認四份 SHA/原始大小：

- `PaperDialog.dat` 1639B／`5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054`，CRC950 `f870c574`，三函式；
- `PaperDialog02.dat` 1771B／`49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a`，CRC950 `42683546`，三函式；
- `nNewJoin01.dat` 1359B／`8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae`，CRC950 `d9390353`，23函式；
- `Merchant.dat` 1603B／`6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350`，CRC950 `e9b389cf`，一個 Main。

每份 zlib stream EOF/無多餘資料，native BEu16 version1＋BEu32 UTF16 units、完整 XML、CP950 原文 text CRC、函式簽名和無重複。確認 Born.Main→PaperDialog_Create；`PaperDialog.dat` OK 沒 SendReply；`PaperDialog02` OK→PAPER02 START／CANCEL→NOT；`nNewJoin01` final OK→STATE ACCEPT／CANCEL→REFUSE；`Merchant.Main` 初始化 ServerParam/ClientReply，`nNewJoin01` 自身沒有 Main。

**特殊測項**：`PaperDialog02` 有 CancelObject14，卻設 `dialog.cancelControl="OK"`（default也 OK）；使用鍵盤 Escape 的 Native GUI 結果未證，Server 不應從 ESC 推斷 NOT；只能採信合法 ScriptRun 的 C6C(1) key/value。另一安全測項：PaperDialog 與 PaperDialog02 均定義 `ShowIndexedHelp`/`PaperDialogProc`；沒有原生衝突處理證據，禁止不加區分的雙匯入。

## 二、合成 CI（不需原件、非 Native Client 通過）

```bash
python3 -m unittest discover -s task_a/roy2 -p 'test_a023_script_bundle.py' -v
```

28 項：zlib 與 BEu32 UTF16 units、錯 version／count、截斷／尾綴／錯 XML root／重複函式、CP950 CRC、callback branch/order、C6C1 的 **root script name**/u32BE context、Merchant 假設 root 的 STATE=ACCEPT/REFUSE、PAPER02=START/NOT、UTF8/CP950 編碼長度、拒絕錯誤 context/長字串等。Fixture 的 root `Merchant` 和 context `0x11223344` 是**自行假設的測試資料**，不代表原服 S44 一定選 Merchant root。

## 三、獨立原版 GUI 與 Server 互動 CT（仍 not-run）

1. **CT-033**：用同 SHA 原 Client、匹配 Script/Basic 資源與原始 C6C/S44 檢查，Script cache 清除型 S44(1,3) 只可在可丟棄安裝副本隔離測試，禁止正式環境直接發。
2. **CT-034**：觀察真正 first-login S44 / Born Main / PaperDialog 顯示及 (31,29) 目標 NPC 的實際 object/map/點擊→特定 Script root/依賴。**四份 Script 不含原服 NPC EntityId/Spawn 定義**。
3. **CT-035**：原版 GUI 分別點 PaperDialog02 OK、CANCEL 和 ESC／鍵盤取消，抓原始 `C6C(1)` root/context/keys、`C6C(4)` 後是否有 `C6C(2)`；nNewJoin01 最後 OK/CANCEL 同樣核對。先取得 `QuestDialog_Create`、`MerchantDialog_Create` 正確依賴版本再跑缺函式 UI；避免故意錯 CRC 對真 Client 測。
4. Server 開發需 separate `STATE` vs `PAPER02`，C6C(1) 是玩家意圖，不代表 QuestCompleted、入學已批准或獎勵已提交。驗 session/generation/root/nonce/context、重播及跨場景，拒絕不合法依賴或錯 script root。不同「依賴檔名」不得充當 C6C1 封包的 root 名稱。

**真正缺少的原始 Script 函式**：`QuestDialog_Create`、`MerchantDialog_Create`、`MerchantDirectTalk`，**確切來源檔名未知**（`QuestDialog.dat`/`MerchantDialog.dat` 只能列待驗候選，非已證必要檔名）。與原服 NPC 綁定／quest flag 是獨立外部證據缺口。完整 A-023 舊報告不再說這四份已提供的檔案「缺少」。

驗收範圍：**CT-113 原始四 Script 靜態資源＋28 合成回歸：offline pass；原生 GUI/World／原服政策仍 CT-034/035 `not-run`。**
