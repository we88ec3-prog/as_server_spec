# A-012 / roy1 — 任務腳本與對話協定 Client I/O 完整靜態交付（2026-11-01）

**判定：A12 Client I/O 靜態研究範圍完成，可作 `handoff_status=ready` 交 DEV；正式原版任務規則與 GUI E2E 不在已證範圍，`native_client_validation=not-run`、`native_quest_rule_ready=false`、`native_npc_script_binding_ready=false`。** 原研究 [A12 基線](A-012-roy1-quest-dialog.md)、[A23 Script 入口](../task_a/roy2/A-023-script-entry-contract.md) 已證的 C6C/S44 不能因 Server 缺規則被抹去，也不能升格成原服完成/獎勵。

原件：`Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；`Born.dat` SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`；`Basic.dat` SHA256 `0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`。固定 profile TW-seed0-local-v0.1；以下本次重驗為 **observed-static-client／observed-original-resource**，非原 Client 實際連線。新 evidence `ev_a012_20261101_original_basic_dialog_resource_lifecycle`。

## 1. 原版 Client 操作→wire→UI 的可實作契約

|trigger|S→C / 來源|C→S / 原生 body|Client 可證反應|位置／證據級別|
|---|---|---|---|---|
|Server 指定執行腳本|S44 type1/subtype0，script 名稱、context、text CRC、相依腳本及參數|缺件發 C6C subtype0 + script:string8|查 Script 本地資源/依賴，齊備則執行 Main；缺件排隊及等待 S44(1,1) 更新|A23 原始 reader `0x586410`，start manager `0x52C2A0`、Main `0x524FA0`|
|本地 Born.Main|Born.dat 單一 Main；其直接依賴 **PaperDialog.dat**（A23 資源已研究，本輪未重驗原件）|只顯示紙張當下**未必發 C 包**|建立 page 陣列，插入單頁提示並呼叫 `PaperDialog_Create`；引導往 (31,29) 點女性招募員，**不是出生點、NPC id 或 quest 完成**|本輪 Born 解包/UTF16/CP950 CRC 原件 PASS；PaperDialog Dispose 借用 A23|
|腳本 UI 的 SendReply|使用者在腳本回覆控制邏輯選擇某選項|C6C subtype1 + string8 name + u32BE context + u16BE pairs + pairs*(string8 key,string8 value)|設定 runner replied flag=1，交由 Server 解讀這是**觀察到的選擇意圖**，不具完成/獎勵授權|native `0x526626` API、`0x51AA5C` subtype1、`0x51AB33` replied、`0x51AB3D` send|
|dialog.Dispose、client.Dispose|紙張 OK/關閉（借用 A23 原件）|C6C subtype4 + script/context，若本次 runner 未回覆，再送 subtype2 + script/context|對話 UI 和 runner 清理。**兩個 send call 不代表兩個 TCP frame**|native `0x526873`、`0x5268C6` C6C4、`0x5268F4` send、`0x519479` flag、`0x5194CE` C6C2、`0x5194F1` send|
|更新或清理 Script cache|S44 type1/subtype1 是資源更新，type1/subtype3 會掃描 Script 目錄|缺件按原有 C6C(0) 請求；其它需匹配已證狀態|**S44(1,3) 不是 ACK，可能刪除本地快取**；錯 CRC 路徑疑有悬空參照，禁止正式 Client 隨機 CRC 測試|原生 `0x52951D` 檔案掃描 string、A23 指令與 CRC 界線|

既有 [A12 wire 詳表](A-012-roy1-quest-dialog.md) 已明確 C6C subtype0/1/2/3/4 與 string8/u16/u32BE；本輪**沒有猜測或修改任何 opcode**。另外 C43 ObjectInfoRequest / C39 Merchant 是獨立 Client→Server 通道；**尚無證據**可把任一通道中所有 NPC 點擊直接標作 quest 的必備入口。

## 2. 這次新補的 Basic.dat 逐資源實證

原始 `Basic.dat` 是 39 項目錄，header `u32LE count`、每筆 `name[32] + u32LE end_offset`，**前一筆 end_offset** 是此筆資源起點；最後有 unused terminal record，解析器停止於空名稱。已對完整原件重新算 SHA256，以下四個內含資源的邊界／雜湊：

|內含資源|原件 byte 範圍（半開）|SHA256|這次確認的能力與限制|
|---|---|---|---|
|`AlertFrame.ypf`|0x338c–0x2e97c|b641441d1f0378de04b6f7929c333d95e6ad7df451f3927432e5c4d0305602ce|Born→PaperDialog 的 AlertFrame 視覺相依**存在**，不代表已在 GUI 成功渲染|
|`BasicString.txt`|0x2e97c–0x32356|fa92f7a3cf544ff9e141d98620943b362e2d3dcc6e327878a818ebaa6ac3123b|繁中 UTF16LE，**101=對話視窗教學提示**、**198=與 NPC 對話的視窗**|
|`QuestImage.ypf`|0x3b41ed–0x3b4800|1f49352d77e79dcc8c535e03458e0f98d6532f1a01d38cedb164b29fd8ffec8e|QuestImage 圖像成員確實存在；**不是 quest 狀態／定義／獎勵表**|
|`SkinString.txt`|0x3ccbc9–0x3cf08d|7ba039919300dccf595fc5f5f4e6d79156b8b96c23a56fa3118d1e55847f199c|繁中 UTF16LE，**2263=任務日誌**、**2264=任務欄**；沒有追到正式 quest 狀態封包或 UI 元素與 Script reply 的全部綁定|

**證據上升的部分**：以前只知道腳本 UI／對話封包，現在有同版 `Basic.dat` 裡的原始對話/任務 UI 資源和 SHA 可核查；但資源名稱與顯示文字本身 **不授權** Server 自行給予經驗、物品、畢業旗標，或把 `QuestImage` 誤視為任務資料庫。

## 3. Born.Main 完整離線安全界線

`Born.dat` 原件 zlib 展開 1,154 bytes，header `BE u16(version1) + BE u32(UTF16LE code_units574)`，XML 只有 `function Main`，完整 XML 文本經 CP950 CRC32=`0x1D87B0C0`。此 Main 明確呼叫 `client.CreateArray`、`page.Insert`、`PaperDialog_Create`；沒有直接 `SendReply`、`SetQuest`、`SetFlag`、`GiveReward` 或 `Teleport`。這是**此單一 Main 中無顯式呼叫**，不是反證所有腳本/Native API/原服都有無任務副作用。

原版 PaperDialog OK 的 Dispose/native caller 路徑已由 A23 驗證，這次重驗 x86 指令與**合成 context=0x11223344** 的 C6C body：
- `04 04 426f726e 11223344` → C6C(4,Born,context)，client.Dispose;
- `02 04 426f726e 11223344` → C6C(2,Born,context)，**只在 runner replied flag=0**；
- 若已有 C6C(1) SendReply，仍可能有 C6C4，但 **不會走此 no-reply C6C2 清理分支**。

不能將 C6C4/C6C2 解讀為 QuestAccepted/QuestCompleted，不能因玩家點 OK、拿到 script 文案或看見任務日誌，就修改 Server 的 QuestProgress/RewardLedger。

## 4. Server 可依證據開發 vs 原服仍未知

**可交 DEV**：在已有正確身份的 ScriptRun 中合法接收 S44 start / 缺件 update、C6C(0～4)（最小已證變體），完整 name/context/pairs decoding 和大小界限、身分/連線 generation/版本/時效、重播防護、Dispose 的 C6C4→C6C2 合理序列、清快取危險 opcode 的防護；支援 Born/PaperDialog resource catalogue（需真的持有匹配版 PaperDialog 才 enable）。型別是 Client wire 合約 + 新 Server 安全政策，不是假稱原版 Server 內部實作。

**未有可靠原件不能還原**：首個 S44 何時送、女性招募員 EntityId/NPC→Script 綁定、nNewJoin01 對應哪隻 NPC、Script 是否對應官方任務 ID/進度／條件、拒絕/完成/獎勵是否存在、原版 UI 選項實際操作/真 C6C bytes、切圖後回覆及斷線重登入原服狀態。這些是 A-024/A-026、DEV QuestRule、原版 Client CT 的後續責任；**A12 Client I/O 靜態工作結案，不代表上述領域已解**。

**精確待補資源（本次仍未在容器收到）**：`PaperDialog.dat`、`nNewJoin01.dat`。兩檔在 GitHub 的 A23 研究有原件 SHA 與解析證據，但本次未掛載，不能重新宣告原件驗證 PASS。前者是 Born 直接函式依賴，後者只是候選商人／學校加入對話；真正的原服 NPC/Quest/Reward 表無已證唯一檔名，**不猜檔名**。原版 Client GUI/原服 trace 是動態證據缺口，不是可以用 `Basic.dat` 取代的 Script 檔案。

## 5. 離線重現／CT

本次原件 **EXE 15/15 native x86 byte anchors、Born/Basic SHA、4 個內含資源 SHA 與 12/12 unittest PASS**（Python stdlib）；`tools/a012_quest_resource_bridge.py`。原有 `tools/a012_quest_dialog_contract.py` 保留 20 anchors/14 tests 的獨立研究基線，本輪沒有冒充全部舊套件已重跑。

```sh
python tools/a012_quest_resource_bridge.py
# 若要驗私有原件，確保以下檔案存在於環境，或設定：
# ASGARD_EXE, ASGARD_BORN_DAT, ASGARD_BASIC_DAT
objdump -d -M intel --start-address=0x526873 --stop-address=0x526901 Asgard.exe
objdump -d -M intel --start-address=0x519479 --stop-address=0x5194f7 Asgard.exe
objdump -d -M intel --start-address=0x52c2ca --stop-address=0x52c2e7 Asgard.exe
```

|Test|目前可宣告|不可宣告|
|---|---|---|
|CT-092|Client 原始 x86 C6C/S44/Dispose 與 Born/Basic 資源、合成 C6C：**offline PASS**|原版 Client GUI runtime PASS|
|CT-093|Born PaperDialog UI 及 nNewJoin 候選流程有可測 S44 和 C6C 靜態導引|原始 Client 完成 NPC 點擊→選擇→封包/提示 E2E|
|CT-094|Server 可以驗 Session/context/stale/重播之設計|原版完成規則／獎勵已證或重放/併發真 Client E2E|

本報告以規格原始 Client 的 **trigger / client_sends / client_receives / client_reaction / evidence / unknowns** 六欄標準交接，保留 runtime/test 的未完成狀態，不上傳原遊戲素材、密碼或真封包。
## 2026-11-01 A12 補件閉環（PaperDialog／PaperDialog02／nNewJoin01 三份原件）

本報告「缺 `PaperDialog.dat`／`nNewJoin01.dat`」**只描述過往工作環境**；現在原件已提供並完成 zlib/UTF16LE/CP950 CRC 驗證，另取得 `PaperDialog02.dat`。新增確證：`PaperDialog02.PaperDialogProc` 的 `PAPER02=START/NOT`，`nNewJoin01.JoinMessage03Proc` 的 `STATE=ACCEPT/REFUSE`，它們是 Client C6C(1) 選項意圖，並非任務完成或獎勵。後者為 MerchantTalk hook、沒有 Main，也不證 Born 女性招募員就是此腳本；PaperDialog02 有獨立 CANCEL 按鈕而 cancelControl 仍 OK。完整原件 SHA、CRC、函式清單、wire fixtures、缺少的外部依賴請以 [本次最新交接](A-012-roy1-new-script-resources-20261101.md) 為準。native GUI／Server authority unknown 保留。
