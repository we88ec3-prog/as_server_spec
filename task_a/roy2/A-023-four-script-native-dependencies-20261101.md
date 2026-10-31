# A-023／roy2：四份新增原版 Script 完整依賴與入學回覆補證（2026-11-01）

> 本報告建立在同一版 `Asgard.exe` 的既有 [S44(1,0)→Script Main→C6C lifecycle 原生契約](A-023-script-entry-contract.md)、[Born/Basic 原件核對](A-023-born-basic-native-dispatch-20261101.md) 之上。**本次實際上傳並讀取** `PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat`、`Merchant.dat`；未把原始文字或遊戲 binary 放入 Git。原版 Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。靜態資源確認 ≠ 真正的 native UI/TCP/原服 NPC 政策驗證。

## 1. 原件身份、版本、解壓與原始 Script text CRC

全部採 `zlib` 完整 stream，解包為 **BE u16 version=1 + BE u32 UTF-16LE code unit count + 對應 XML bytes**（正好 `6+2*units`）；每一份獨立完整 SHA256、function set、XML well-formed，並以 **LanguageMan index4／CP950 條件** 計算 XML 原文 CRC32（不是 DAT raw CRC，也不是重序列化 XML）。

|原版資源|原檔 bytes|unpacked bytes|function 數|UTF16 units|CP950 XML CRC32|raw SHA256|
|---|---:|---:|---:|---:|---|---|
|`PaperDialog.dat`|1639|9196|3|4595|`f870c574`|`5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054`|
|`PaperDialog02.dat`|1771|10518|3|5256|`42683546`|`49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a`|
|`nNewJoin01.dat`|1359|9962|23|4978|`d9390353`|`8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae`|
|`Merchant.dat`|1603|7856|1|3925|`e9b389cf`|`6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350`|

`Born.dat` 與 `Basic.dat/AlertFrame.ypf` 也已在本次對照：`Born` 主函式的 `PaperDialog_Create("",page)` 現在能連到**真正持有這個函式的原始 PaperDialog.dat**，不用再標 PaperDialog 本輪 unavailable；Basic 的紙張背景成員 hash/frame version 已由 A023-E20 核對。**個別版本 SHA 配合內容相容不等於取得可信的官方發行包配對 manifest**。

## 2. 函式解析、相依圖、真正可觀察 Client 行為

### 路徑 A：Born 與 PaperDialog（只有觀看引導）

```text
[Server designed/original trigger unknown] S44 type1/subtype0 root="Born"
  └─ requires PaperDialog_Create, ShowIndexedHelp, PaperDialogProc
       └─ PaperDialog.dat + Basic.dat/AlertFrame.ypf
            └─ UI OK / cancelControl=OK / defaultControl=OK
                 └─ dialog.Dispose() → client.Dispose()
                      └─ native C6C(4, root="Born", context)
                      └─ if unreplied, native C6C(2, root="Born", context)
```

- `PaperDialog.dat` 有且僅有 `PaperDialog_Create`、`ShowIndexedHelp`、`PaperDialogProc`。建 UI 三個按鈕 object 11/12/13、使用 `Basic.dat/AlertFrame.ypf`，預設/取消控制均 `OK`；**沒有** explicit SendReply，不能因按 OK 改 tutorial_completed 或發獎。
- Born 的 **(31,29) 是文字導引**、不等於 NPC EntityId、出生位置或原服教學地圖。A-023 過去已證 C6C(4) 與未回覆情境 C6C(2) 為 **ScriptRunner lifecycle**。

### 路徑 B：PaperDialog02 是獨立的帶選擇紙張（並非 Born 自動下一頁）

- `PaperDialog02.dat` 只有 `PaperDialog02_Create`、`ShowIndexedHelp`、`PaperDialogProc`，**沒有 Main**；建立紙張含 object 11/12/13/14、`Basic.dat/AlertFrame.ypf`。callback 按 **OK**：`ClientReply.Add("PAPER02","START")` → `client.SendReply(ClientReply)` → Dispose；按 **CANCEL**：`PAPER02=NOT` → SendReply → Dispose。
- **重要原件 UI 風險**：雖有顯式 CANCEL 按鈕，但原始 `PaperDialog02_Create` 仍設 **`dialog.cancelControl="OK"`** 且 `defaultControl="OK"`。所以按鍵盤取消/ESC 若經原生 cancelControl 機制，可能會走 `PAPER02=START`，**而非** `NOT`；這是原始 Script 的字面控制設定與合理 UI 推論，**未做 GUI 實測**。Server 不得把 ESC 直譯為 REFUSE/NOT，應以實際 C6C(1) key/value 為準。
- PaperDialog02 **直接使用外部 `ClientReply`**，本檔未初始化該物件；不能憑有 `PaperDialog02_Create` 就宣稱獨立 `S44(1,0)` 將能順利運行。其特定 Server 上游 ScriptRun、被哪個 NPC 觸發、`PAPER02=START/NOT` 的進度與地圖效果均 unknown。
- `PaperDialog.dat` 與 `PaperDialog02.dat` **同時宣告完全同名的 `ShowIndexedHelp` 和 `PaperDialogProc`**，但主建構函式名稱不同。原 Client 的 runner `0x52bd30` 會匯入依賴函式；同一 ScriptRun 無條件匯入兩份有名稱衝突風險。Client 遇重名到底覆蓋或失敗未經動態驗證，因此 **Server 設計上不得自動雙載**，應按獨立且已核對的 dependency set 發送。

### 路徑 C：Merchant 主程式 + nNewJoin01 初級學校三頁對話

```text
[實際 NPC→Script 名稱/依賴包 未證]
 Merchant.dat : Main(args) [有 Main 的 root]
   ├─ AddGlobal("ServerParam", args)
   ├─ reply = client.CreateParams(); AddGlobal("ClientReply", reply)
   ├─ 取 TILE/MNAME/UGOLD/UBAL/UAGOLD/UABAL/UCOLOR
   ├─ TYPE 分支可選 DIRECT 等特殊主介面模式
   └─ 無 TYPE 的初始菜單使用 DoesTalk、MerchantDialog_Create
       └─ 若依賴/界面確實綁 nNewJoin01.dat：
          DoesTalk = true；其他 Buy/Sell/Repair/Bank/Identify = false
          MerchantTalk → JoinMessage01 → JoinMessage02 → JoinMessage03
            ├─ final OK : ClientReply.Add("STATE","ACCEPT") → SendReply → Dispose
            └─ final CANCEL : ClientReply.Add("STATE","REFUSE") → SendReply → Dispose
```

- `nNewJoin01.dat` 實際 **23 個函式，但沒有 Main**；MerchantTalk 從第 1 頁開始。第1頁 NEXT→2；第2頁 PREV→1 / NEXT→3；第3頁 PREV→2、OK→`STATE=ACCEPT`、CANCEL→`STATE=REFUSE`。**後兩者是玩家 UI 選擇意圖，不是 Server 已核准入學或任務完成**。
- `Merchant.Main` 是實際函式，參數表用 `ServerParam`，並初始化供其他依賴使用的 `ClientReply`。主介面呼叫 `MerchantDialog_Create`；學校三頁另使用 `QuestDialog_Create`。**這兩個函式定義不在四份原件中**；另外 `MerchantDirectTalk` 亦未見本次四檔定義，無法在缺相符共用 UI 依賴時宣告 NPC 原生 GUI 完整可跑。
- **即使把 Merchant 和 nNewJoin01 的原件可執行函式串接起來，仍未有 Born 招募員 EntityId/map/spawn → Merchant root + nNewJoin01 dependency 或 GUI action 的 Server 原件／封包證據。** Born 描述女性招募員、nNewJoin 描述初級學校是語意相符的候選，不可據此寫死 NPC ID 或任務事件。
- `TYPE="DIRECT"` 在 `Merchant.Main` 可走 `MerchantDirectTalk`，不等於一定展示上述三頁；不能從 `DoesTalk=true` 推定所有商人對話都是 nNewJoin。

## 3. C6C 封包究竟要帶哪個 Script 名稱？

Native C6C(1) 的 `script:string8` 來自**當次 ScriptRunner 的 root name**，不是定義 callback 的資源檔名。若 Server 送 S44 start `script="Merchant"`，把 `nNewJoin01` 作為依賴合併，那麼 `ClientReply.Add("STATE","ACCEPT")` 的 native C6C(1) **script name 應是 root `Merchant`**。反之如果 Server 選用其他 root，不能硬編 `Merchant`／`nNewJoin01`；**實際原服 S44 root/context 尚未有 trace**。

**完全合成的解碼 body 範例**（不含 opcode、frame、ordinal／encryption；`context=0x11223344` 自訂；CP950／ASCII）：

|S44 假設 root|按鈕結果|C6C subtype|decoded body hex / shape|
|---|---|---|---|
|`Merchant`|`STATE=ACCEPT`|1|`01 08 4d65726368616e74 11223344 0001 05 5354415445 06 414343455054`|
|`Merchant`|`STATE=REFUSE`|1|`01 + string8("Merchant") + BEu32 context + BEu16(1) + string8("STATE") + string8("REFUSE")`|
|未知 root|`PAPER02=START/NOT`|1|`01 + string8(root) + BEu32 context + BEu16(1) + string8("PAPER02") + string8("START"/"NOT")`|

Native `client.SendReply` 會建立 **C6C(1)** 並標 `replied=true`；接著 `client.Dispose` 仍建立 **C6C(4)**，而 **replied=true 時不再自動發 C6C(2)**（沿用同 SHA 的 A-012/A-023 native code）。這與 Born 只關閉不回覆、先 C6C4 後 C6C2 明顯不同；兩次 send call 並未證實一定對應不同 TCP frames。

**Server designed**：C6C(1) 必須校驗目前合法 session/character/world_generation/ScriptRun、**root script**/context 與允許的 reply key；不同 ScriptRun 的 `STATE` 和 `PAPER02` 嚴格分別處理，`REFUSE` 不修改完成/入學/獎勵且可重新交談是已決的 Server Policy，不要冒稱原服事實。重送同值冪等、不同值或 stale generation 拒絕；只有經正式 NPC/quest 規則確認才允許切圖/完成/發獎。

## 4. 還有哪些真正缺件？能宣告 A-023 完成到哪裡？

**不再缺** `PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat`、`Merchant.dat`、`Born.dat`、`Basic.dat`、`Asgard.exe`。本次四份真實 Script 完整重新解析／SHA/CRC/回覆分支與相互依賴交叉核對均通過。

**仍需原件**：`QuestDialog_Create`、`MerchantDialog_Create`、`MerchantDirectTalk` 的**真正函式定義原始 Script**；候選對應檔名可能是 **`QuestDialog.dat`**、**`MerchantDialog.dat`**，但本次四份檔案**未提供可信的 filename→function 對應**，故只是**待確認的檔名候選**，不可說它們一定存在或足以涵蓋三個函式。若有與本版 Client 配套的 `Script/` 資源函式清單，可確認具名檔案後補交。即使補齊這些 Client UI 函式，原服 NPC/entity→Script/start/world/quest旗標決策仍須 **原服配置/去敏 first-login+NPC trace** 才能證實，不是任何一份美術 DAT 可以取代。

**本次獨立核查**：`python task_a/roy2/a023_script_bundle_probe.py --script-dir /原件目錄 --born /原件目錄/Born.dat`，四 Script SHA、strict zlib/UTF16、CP950 text CRC、callback 分支與 collided function names，再產生 synthetic C6C(1) 向量；新增 **28 項 synthetic tests** 跑 GitHub CI（不含原始 Script）。另 [Born/Basic 原件 native 驗證](A-023-born-basic-native-dispatch-20261101.md) 仍有效，原版 Client GUI/NPC E2E **not-run**。

### A gate 結論

A-023 可**完整交付目前取得之所有 Client resource/codepath**：S44(1,0) start、依賴/CRC、Born/Main/紙張、PaperDialog02 分支、Merchant+nNewJoin 選項與 C6C lifecycle，及 GUI 函式碰撞／缺件。**但整體 `integrated / partial` 保留**：首個原版招募員 EntityId/map/Script 觸發與原服 quest flag/任務政策及 GUI E2E 不能由這四份原始 Script 證成。此研究的未解是「確有來源缺口」，不是漏讀當前上傳的檔案。無須等待這些 P1 教學 NPC 才讓 Server P0 進 World 可移動。
