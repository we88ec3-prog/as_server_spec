# A-012／roy1 — 三份原始 Script 補件驗證與 Client 對話選項閉環（2026-11-01）

**本次已完成 A12 的原始 Client 靜態與資源對話選項交接；`status=integrated`，`handoff_status=ready`，`native_client_validation=not-run`。** `ready` 限 S44／C6C 與所持原件可證的 Script UI/回覆路徑，**不是**原服任務完成／獎勵／NPC 來源及 Windows GUI/TCP E2E 已成功。工作在既有 `task_a/roy1`；無新 branch，未修改 Asgard.exe 或私有資源。原始資產只記雜湊和內容定位，不上傳完整腳本／美術或玩家資料。

## 1. 這次真正取得並重驗的四份 Script

|檔名|原始 bytes|SHA256|zlib unpack bytes／UTF-16LE code units|CP950 XML CRC32|函式數|
|---|---:|---|---|---|---:|
|`Born.dat`|589|`992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`|1154 / 574|`1D87B0C0`|1|
|`PaperDialog.dat`|1639|`5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054`|9196 / 4595|`F870C574`|3|
|`PaperDialog02.dat`|1771|`49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a`|10518 / 5256|`42683546`|3|
|`nNewJoin01.dat`|1359|`8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae`|9962 / 4978|`D9390353`|23|

每個檔經 `zlib` 解包，檢查 **BE u16 version=1 + BE u32 UTF16LE code_units**（`len(unpacked)=6+2*code_units`），XML `<script><function name=...>`，UTF16LE 轉 CP950 的 CRC32。上述四個原件 SHA、CRC、全部函式 inventory 本輪 **PASS**。原始 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，驗 C6C/S44 native 9 個指令窗。已有 [A12 原始靜態 baseline](A-012-roy1-quest-dialog.md) 與 [A23 完整 Script 啟動契約](../task_a/roy2/A-023-script-entry-contract.md)，保留原驗證，不重複發明 wire 欄位。

## 2. 腳本層實際選項與原生封包回覆

|來源函式／頁面|控制鍵|來源內的實際 Client API|C6C(1) 的 reply key/value|是否證成 quest completion?|
|---|---|---|---|---|
|`Born.Main`→ `PaperDialog.PaperDialogProc`|OK|先 `dialog.Dispose()`，再 `client.Dispose()`；**沒有 SendReply**|無：依原版 native runner 對未回覆者依序送 **C6C(4)**、**C6C(2)**|否：只結束單頁提示|
|`PaperDialog02.PaperDialogProc`|OK|先 `ClientReply.Add`，再 `client.SendReply(ClientReply)`、`dialog.Dispose()`、`client.Dispose()`|`PAPER02=START`|否：僅 Client 選擇意圖|
|`PaperDialog02.PaperDialogProc`|CANCEL|同上|`PAPER02=NOT`|否|
|`nNewJoin01.JoinMessage03Proc`（最終加入確認）|OK|同上|`STATE=ACCEPT`|**否：不能直接由 Client 選擇宣告入學、任務成功或給獎**|
|`nNewJoin01.JoinMessage03Proc`（最終加入確認）|CANCEL|同上|`STATE=REFUSE`|否：Server 依 R-034 REFUSE 不應異動 Domain|

**C6C 真格式** 來自 `Asgard.exe` native `0x575210` writer 與 `0x51AA5C` SendReply producer：`u8 subtype=1, string8 runner_script_name, u32BE context, u16BE pair_count, pair_count×(string8 key,string8 value)`。string8 的 byte-length 依 Client 所選 codepage；TW index4 使用 CP950。不以 Python XML 內的 `client.SendReply` 字面直接捏造新 opcode。關閉函式 `client.Dispose` 由 native `0x5268C6` 送 C6C(4)，replied flag `0x51AB33` 避免另送 no-reply C6C(2)，未回覆清理見 `0x519479/0x5194CE`。

**合成示例，不是原服抓包**：以任意 runner name `nNewJoin01`、context `0x11223344`，一組 `STATE=ACCEPT` 的 C6C(1) body：
```text
01 0A 6E4E65774A6F696E3031 11223344 0001 05 5354415445 06 414343455054
```
同一 context 回覆 `STATE=REFUSE` 只替換尾字串；`PaperDialog02` 的 `PAPER02=START/NOT` 也是同一 subtype1 格式。**腳本 runner.name 是 S44 入口/運行上下文的名稱，未證真實 UI 操作時必為檔案名稱 nNewJoin01 或 PaperDialog02**。Script 可能作為共用 Merchant 依賴被載入，Server 不可對任何腳本名/任意 context 都接受此選項。C6C(4) 與 no-reply C6C(2) body 不帶 pair；Born 的 synthetic:
```text
04 04 426F726E 11223344
02 04 426F726E 11223344
```

## 3. 三份 Script 的精確用途與無法推廣的界線

### PaperDialog（Born 直接依賴）
- 原件有 `PaperDialog_Create(titleString,helpArray)`、`ShowIndexedHelp(paperDialog,index)`、`PaperDialogProc(dialog,control)`。Create 建 TITLE/EDIT/PREV/NEXT/OK 控件，設定 `dialog.onControlClick="PaperDialogProc"`，`cancelControl=OK`、`defaultControl=OK`，背景 `Basic.dat/AlertFrame.ypf`，按鈕圖像 object **11/12/13**。
- Born.Main 只建立一個 page，`page.Insert(msg)`，`PaperDialog_Create("",page)`；因此 index0 時 PREV 隱藏，最後一頁 NEXT 隱藏，OK 收束。其文字提示往 **(31,29)** 點女性招募員，座標是文案，不是 map spawn／NPC 實體/quest waypoint ID。
- 按 OK 的腳本只有 Dispose，**沒有** ClientReply.Add／SendReply／Quest completion／Reward grant。native runner cleanup 所送 C6C(4) 與 C6C(2) 不應被新 Server 當任務完成。

### PaperDialog02（獨立的可回覆紙張）
- `PaperDialog02_Create` 額外建立 **CANCEL image button object14**（其他 PREV11/NEXT12/OK13），背景仍 `Basic.dat/AlertFrame.ypf`；與 PaperDialog 並非同一函式。callback `PaperDialogProc` 的 OK、CANCEL 都 `ClientReply.Add`、SendReply、Dispose。
- **需要特別注意**：雖然有可點擊 CANCEL 控件，原 XML 仍設 `dialog.cancelControl = "OK"`，故無法從字面假定按 ESC 或原生取消鍵會送 `PAPER02=NOT`；這必須由原 Client 實際 GUI 驗。此檔引用外部 `ClientReply`，在本檔不自行建構；**不能無前置就直接發 S44(name=PaperDialog02)** 並保證成功。
- PaperDialog 與 PaperDialog02 都定義同名 `ShowIndexedHelp` 和 `PaperDialogProc`，目前**不證明**執行器在同時載入時如何命名空間隔離／函式覆蓋。不要在正式 Client 未驗載入情境下擅自混合兩份依賴。

### nNewJoin01（MerchantTalk 的學校加入對話）
- 原件 23 functions，**沒有 Main**。`DoesTalk` 回 true、Buy/Sell/Repair/Bank/Identify 都回 false，`MerchantTalk` 直接呼叫 `JoinMessage01`；三頁 `JoinMessage01 → JoinMessage02 → JoinMessage03`：第一頁 NEXT、第二頁 PREV/NEXT、第三頁 PREV 及 OK/CANCEL，只有第三頁 OK/CANCEL 呼叫 `SendReply`。
- 最後一頁的問題是「要進入初級學校嗎？」；`STATE=ACCEPT/REFUSE` 僅是 UI 表意。不證明 Server 採納後立即完成教學/發獎/轉圖，也不證 NPC 一定是 Born 文案女性招募員。
- 外部依賴 `QuestDialog_Create`、`MerchantTile`、`MerchantName`、`ClientReply`，此檔本身沒有這些定義／賦值。主線 A23 已有 **`Merchant.dat`** 的明確檔名與 SHA256 `6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350`（本次**未上傳/未重新驗**），說明 Merchant.Main/ServerParam 外部共用框架；`QuestDialog_Create` 實際由哪個已發行腳本檔提供，**在此次三檔中未獲證實，不能憑函式名捏造檔名**。
- NPC EntityId/地圖/生成位置/互動識別與腳本名綁定仍必須由 A11/A24/原服 trace 交叉。缺真正 Server QuestRule、入學授權回覆及獎勵存在的原服來源，保持 `native_quest_rule_ready=false`。

## 4. 安全交付、負面例與 CT

**可給 Server 開發的既定 Client I/O 契約**：S44(1,0) 按 name/context+資源 CRC/依賴啟動；C6C(0) 缺資源請求、C6C(1) key/value 候選、C6C(4) 顯示後 dispose、未回覆 C6C(2) cleanup。此輪可附上具體 **`PAPER02=START/NOT`、`STATE=ACCEPT/REFUSE`** 來源，僅讓 Server 維持有權限/有效 context 的 ScriptRun 事件，不允許無證直接改 quest/進度/金幣/物品；ScriptRun 綁角色、連線 generation、world/map/target、資源版本與合法的 keys，回覆重送冪等，過期或跨 NPC 拒絕。新 Server 權威操作屬 DESIGNED，不能冒稱原服行為。

`S44(type1/subtype3)` 原 Client 可能掃描/清除 Script 快取；錯 CRC 曾有 unsafe native code 路徑，**嚴禁在正式 Client 用不匹配內容試探**。

**CT-092 offline 增量**：原始 EXE+四份腳本的全部固定 SHA；9 個 native producer/signature；zlib/UTF16LE wrapper及 CP950 XML CRC；原始 callback 控件 case；`C6C(1)` 正反例（synthetic），缺控制分支/無 SendReply/不合法 context/長名字拒絕。這輪本地腳本 **20/20 unittest PASS**，仍非完整原版 Client 端對話 UI 實機驗收。重現：`python tools/a012_dialog_option_native_probe.py`（可設定 `ASGARD_ASGARD_EXE` 等環境變數，預設讀 /mnt/data；缺檔可 skip），再參照早先 `tools/a012_quest_dialog_contract.py` 和 `tools/a012_quest_resource_bridge.py`。
  
**CT-093 原生 GUI**：在隔離原版 Client 指定 S44 的合法資源/CRC，驗 PaperDialog 單頁 OK 是否如期 C6C4+2；驗 PaperDialog02 兩個按鈕是否送相應 C6C1（尤其 `cancelControl=OK` 的鍵盤取消行為）；驗 nNewJoin 在**已證 NPC→Merchant/QuestDialog 前置與正確 runner script/context** 下三頁轉場與 C6C1、Dispose/C6C2 gate。注意一次 SendReply 後不再補 no-reply C6C2。

**CT-094 Server 授權**：雙 Client 同圖、同 Script 不同 runner、重送/跨 session/錯 NPC/超出範圍、角色登出、回覆跟資源 revision 不一致、STATE=REFUSE、PAPER02=NOT 全部不能錯誤提交 Quest/Reward；只有真正 Server 原服 QuestRule 證據另行決定進度/獎勵；目前沒有證據證明獎勵存在。

**餘下真實缺口**：原件 `Merchant.dat`（主線已確認名稱/hash，這次未附上）及 `QuestDialog_Create` 的**已證定義來源**（目前未能確定具名檔案，需腳本索引/原件再定位）；還缺對應 NPC→Script Server binding/first-login dispatch/QuestRules/任務獎勵的原服證據及 Windows 原版 Client/Socket 雙向去敏 trace。此次 `PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat` 已齊、驗證通過，**不再列為缺檔**。

## 5. 合格交付狀態

- `A-012 status=integrated, handoff_status=ready, implementation_ready=true` **限定原生 Client I/O 與 static resource scope**。
- `native_client_validation=not-run, native_quest_rule_ready=false, native_npc_script_binding_ready=false`；CT-092～094 的 native GUI／Server E2E 未通過，不得將測試腳本成功當作 Client 正式登入或任務發獎成功。
- 不提交任何原始 DAT/EXE、任務完整內文、客戶端私有二進位或玩家識別資訊；只提交證據摘要/雜湊、probe 和交接文件。

## 2026-11-01 A-012 Merchant.dat 原件完成：共用 Script 執行環境補證

**本文件早期「Merchant.dat 未附上」的資源缺口已解除。** 新上傳原始 `Merchant.dat` SHA256 `6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350`，1603 bytes，zlib 解包 7856 bytes，BE v1/u32 3925 UTF16 units，CP950 XML CRC32 `E9B389CF`，只有 `Main`。它建立 `ServerParam`、`ClientReply`、`MerchantTile`、`MerchantName` 等 globals，再呼叫 `DoesTalk`/外部選單程式；`nNewJoin01` 則提供 `DoesTalk=true`、`MerchantTalk→JoinMessage01` 與最後 `STATE=ACCEPT/REFUSE`。此為兩份原資源之**靜態依賴交叉證據**，不是已跑原版 NPC 介面，也不證在 `TYPE=DIRECT` 時必定執行 nNewJoin。仍待 `QuestDialog_Create`、`MerchantDialog_Create`、`MerchantDirectTalk` 的真正 Script/engine 提供者（確切檔名未知），原服 NPC EntityId→Script、Quest/Reward；不能猜 `QuestDialog.dat`。詳 [A12 Merchant 原件說明](A-012-roy1-merchant-original-bridge-20261101.md)、[新離線測試](../tools/a012_merchant_bridge_probe.py)（本地 25/25 PASS，原生 Client GUI 未跑）。
