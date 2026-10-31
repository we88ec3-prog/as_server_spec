# 2026-10-31 新提供 Script / Monster / World 原件驗證（資源證據，不是原生 Client E2E）

來源：使用者直接提供 `nNewJoin01.dat`、`PaperDialog.dat`、`PaperDialog02.dat`、`Monster00.dat`、`World00.dat`；以原本 `Born.dat` 和 SHA 鎖定的 `Asgard.exe` 既有 A-011/A-023/A-026 作交叉核對。**只有 SHA、大小、索引與行為摘要進共用 Git；不存放原始遊戲資產、完整腳本文字或圖片**。提供原件≠證實與 EXE 的發行版配對；未執行原版 Client GUI/封包 E2E。

## 1. Script 的離線結構驗證

每個檔案均直接 zlib 解壓，檢查開頭 BE u16 version=1 / BE u32 UTF-16LE code units、`len(unpacked)==6+2*units`、UTF-16LE/XML 結構及具名函式。以下 CP950 文字 CRC32 是 **在 LanguageMan=index4/CP950 時**，對完整 XML 轉碼後 `zlib.crc32`，不是 .dat raw CRC。

|原件|raw bytes|SHA256(raw)|解壓 bytes|UTF-16 單元|CP950 text CRC32|
|---|---:|---|---:|---:|---|
|nNewJoin01.dat|1359|8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae|9962|4978|`d9390353`|
|PaperDialog.dat|1639|5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054|9196|4595|`f870c574`|
|PaperDialog02.dat|1771|49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a|10518|5256|`42683546`|
|Born.dat（既有比對）|589|992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98|1154|574|`1d87b0c0`|

- **nNewJoin01**：`DoesTalk()` 為 true，買/賣/修理/銀行/鑑定等 capability 為 false；`MerchantTalk → JoinMessage01 → JoinMessage02 → JoinMessage03`，是三頁「初級學校關口」對話。前兩頁 NEXT/PREV 純本地轉頁；第三頁 `OK` 呼叫 `ClientReply.Add("STATE","ACCEPT")`、`client.SendReply`、清 UI/runner；`CANCEL` 對應 `STATE=REFUSE`。**腳本直接內容確證**；它不具有 `Main`，不能單獨當 `S44(1,0)` 的主腳本；使用共享 Merchant runtime 的來源 A-023 曾以 EXE 靜態分析支持，但 **NPC entity→script 名稱→畫面 trigger 仍未知**。
- **PaperDialog**：`PaperDialog_Create`/ `ShowIndexedHelp` / `PaperDialogProc`；OK 只 `dialog.Dispose`、`client.Dispose`，無明示 `SendReply`。配合 A-023 靜態 native Dispose 路徑，Born 一般關閉預期 C6C(4)、可能 C6C(2)，不是任務完成。
- **PaperDialog02**：提供 `PaperDialog02_Create`，按鈕除了 PREV/NEXT 還有 OK/CANCEL；OK 明示 `ClientReply.Add("PAPER02","START")` + `SendReply`，CANCEL 是 `PAPER02=NOT`；與 PaperDialog 的 OK 處理不同。兩腳本**都宣告同名 `ShowIndexedHelp`、`PaperDialogProc`**，**不能未驗證便合併成同一 runner dependencies**。`PAPER02` 回覆不能被 Server 當 `STATE` 或完成任務。
- **Native Script wire 的已證舊規則**：A-023 `client.SendReply` 對應 C6C subtype1、`client.Dispose` 對應 subtype4；已 replied 的清理路徑一般不再 subtype2。以上是原 EXE 靜態推導的**呼叫路徑**，不是本次捕捉到的真實封包順序／畫面；需要 CT 單獨驗。
- **呈現依賴**：兩個 PaperDialog 都引用 `Basic.dat/AlertFrame.ypf` 和 UI buttons 11/12/13（02 多 14）；nNewJoin01 呼叫外部 `QuestDialog_Create`，另使用 Merchant 提供的 `MerchantTile`、`MerchantName`、`ClientReply`。尚未從原版依賴清單證明 `QuestDialog_Create` 定義位於哪個**確切檔名**；不得直接將推測的 `QuestDialog.dat` 當已證需要的原件。

## 2. 兩個 6-slot 索引 DAT 容器

嚴格驗證 `LE u32 slot_count=6`（**含尾端 sentinel**），起始 `4+6×36=220`，每 slot `LE u32 offset + 32-byte name`，offset 單調，最後 sentinel=EOF。兩包各有 **5 個真實 .ypf 成員**，不是 6 個，也不是「每 archive 有 10 個 YPF」。名稱以 CP949 解碼作 **顯示用途**，wire 比對應維持原 name bytes。

|原件|raw bytes|SHA256(raw)|5 個原始索引成員（依順序）|
|---|---:|---|---|
|Monster00.dat|4431969|ef45faefd96572695e0086753b2c881a218df2730d1cd5a0c40bf5d26c3ba505|`M_00_0_모스.ypf`, `M_00_1_모스워리어.ypf`, `M_00_2_나이트모스.ypf`, `M_00_3_드라스.ypf`, `M_00_4_모스캡틴.ypf`|
|World00.dat|44573870|01b1afc14daf4ca030004f825d8af39ff6667d184431a5aa9aa9b67a81160ef3|`TS_000_AnimStatic.ypf`, `TS_000_AnimStaticShadows.ypf`, `TS_000_Static.ypf`, `TS_000_StaticShadows.ypf`, `TS_000_Tile.ypf`|

Monster 的五筆 payload 長度依序為 556599/844770/1044873/986788/998719；World 為 1206780/70669/10990235/854222/31451744。已驗證容器索引與檔名，**尚未逐幀解開這兩包的 YPF/DOI 動畫**；也尚未證明何種 image ID 對應哪個 Monster YPF member，更未證明哪一隻是 Born 的女性招募員或教學怪物。A-011 原 EXE 的 `client_image_id 0x4000 → Monster00.dat / local_image_slot 0` 是 **Client 影像槽算法**，不能誤等同這份檔案的第一個 YPF 索引；一個檔案可能有多個 YPF 成員，每個 YPF 又可能包含多個畫面/動作。World00 為場景圖塊/靜態圖像素材，不是 World Entity 表或 map→NPC spawn 清單。

## 3. 可交 DEV／仍待 A／CT

- **可交付（observed-static-resource）**：文字 CRC 與資源 release pin、三頁就學對話的 `STATE` 兩個明確值、PaperDialog02 的 `PAPER02` 兩個值、選擇/關閉的差異、兩包資產索引及 raw SHA。
- **Server designed**：將 ScriptReply 視為已授權的 **意圖** 而非角色權限/任務完成；只接受合法 ScriptRun + context + current account/character/world generation + expected key/value，重送具冪等性；不補送未證的 S→C 分支。
- **原版未證**：女性招募員的 entity/map/visual、該 NPC 連到 nNewJoin01 的證據、Merchant.Main 與 QuestDialog_Create 依賴列表、`STATE=ACCEPT` 後的原版 Server 進圖/任務/地圖、`PAPER02` 何時啟動、Monster YPF motion mapping、原版 Client GUI/雙人同步。Native Client CT 一律 `not-run`。
- 來源文獻：`task_a/roy2/A-011-analysis.md`、`task_a/roy2/A-023-script-entry-contract.md`、`04-analysis-integration/A-026-tutorial-completion-contract.md`。原件不入 Git。參閱 [新手入學規劃](../02-server-planning/novice-school-admission-flow.md) 與 [增量驗收](../05-conformance/new-asset-validation-plan.md)。
