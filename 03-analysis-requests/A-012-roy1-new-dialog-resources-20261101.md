# A-012 / roy1 — MerchantDialog／QuestDialog／QuestDialog2 原件補證（2026-11-01）

**範圍：原始 Client 腳本資源與已證 C6C ScriptReply 靜態契約。** 在既有 task_a/roy1 分支分析；不修改 EXE、Server/DB，也不提交私有 DAT。A12 原生 Client I/O 靜態 handoff=ready，原版 Windows GUI/TCP not-run，QuestRule 與 NPC Script 綁定仍 unknown。

## 原件鑑識

三檔都為 zlib，展開後 BE u16 version=1 + BE u32 UTF16LE code_units + XML UTF16LE，CRC32 是完整 XML 文字重新編碼成 CP950 的值，不是 .dat raw CRC。

|檔案|原始大小|SHA256|解壓 bytes / UTF16 units|CRC32（CP950 XML）|函式|
|---|---:|---|---|---|---|
|MerchantDialog.dat|2455|ed194a77a669cbd8f83fbbd01bb08ed0f800b122695cc204a3a12f002f945095|18782 / 9388|9267D99D|MerchantDialog_Create, MerchantDialogProc|
|QuestDialog.dat|1938|13f068d8053ea7e7b0231357c318bc6effae867888b94305820fe483a17a02dc|9304 / 4649|D4844B07|QuestDialog_Create, QuestDialogAdjust|
|QuestDialog2.dat|1959|acb097c05f440e560394199622bb2e971d2ef9d1a33fff1a1c150ba633e63195|9410 / 4702|893C64EB|QuestDialog2_Create, QuestDialogAdjust2|

Asgard.exe 已核對與既有 A12 同一 SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。**本次八項離線單元測試 8/8 PASS**（SHA/wrapper/CRC/函式/回呼/壞檔）；原版 GUI/Socket 未操作，不得當成原服真實封包。

## MerchantDialog：UI callback → ClientReply

MerchantDialog_Create(greeting,bBuy,bSell,bRepair,bBank,bIdentify,bTalk) 使用 Script.dat/MerchantFrame.ypf 畫主窗，Script.dat/ScriptButton.ypf 畫選項標記；使用 MerchantTile、MerchantName、greeting 產生肖像和文字。肖像從 Portrait.dat/informationNN.ypf 取圖，規則是 0<tile<32768 時 tile-16384 後除10與取餘數。此為**顯示用計算，不能等同 NPC EntityId/Server model ID**。各 b* 布林決定可顯示 BUY/SELL/REPAIR/BANK/IDENTIFY/TALK；固定 CANCEL。點擊回呼 MerchantDialogProc：

|control|ClientReply.Add|callback 同步動作|可靠的 wire 判讀|
|---|---|---|---|
|BUY|TYPE=BUY|SendReply；dialog.isActive=false|已知 SendReply→C6C(1)，不等於完成購物|
|SELL|TYPE=SELL|SendReply；dialog.isActive=false|不等於發放金錢|
|REPAIR|TYPE=REPAIR|SendReply；dialog.isActive=false|不等於修理完成|
|BANK|TYPE=BANK|dialog.Dispose → Add → MerchantBank()|**此 case 無直接 SendReply**；不能假設立即 C6C1，需追 MerchantBank|
|IDENTIFY|TYPE=IDENTIFY|SendReply；dialog.isActive=false|不等於鑑定成功|
|TALK|TYPE=TALK|dialog.Dispose → Add → SendReply → MerchantTalk()|**先 SendReply，再本地轉對話 hook**，不一定等 Server 回包|
|CANCEL|TYPE=ABORT|dialog.Dispose → Add → SendReply → client.Dispose|ABORT 不是 QuestFailed|

以上 callback 源碼直接證實 **MerchantDialog_Create provider 是 MerchantDialog.dat**。先前標其實作來源未知已失效。交叉參照 A-012-roy1-merchant-original-bridge-20261101.md：Merchant.Main 建 ClientReply/ServerParam 等 globals、nNewJoin01.MerchantTalk 最終增加 STATE=ACCEPT/REFUSE。ClientReply 是可變容器，TALK 先 SendReply、STATE 後 SendReply；**原版 runner 中兩次送出時 pairs 是否累積、快照與 context、真正 TCP 次序仍待 CT-093 實測**。先前只有 STATE 一組的 C6C body 僅是 synthetic codec 範例，不是原版對話真 trace。不要把商人選擇當直接交易或任務完成。

## QuestDialog 兩版

|項目|QuestDialog.dat|QuestDialog2.dat|
|---|---|---|
|Create 參數|tile,name,title,desc,bPrev,bNext,bEdit,bOk,bCancel,proc|tile,color,name,title,desc,bPrev,bNext,bEdit,bOk,bCancel,proc|
|函式提供者|QuestDialog_Create|QuestDialog2_Create|
|大小及背景|366×250；Script.dat/QuestFrame.ypf|同|
|portrait|tile-16384、Portrait.dat/informationNN.ypf、SetFrame|使用 SetPortrait(tile,color)，舊 SetFrame 以及 tile-16384 為註解|
|callback|dialog.onControlClick = proc（由呼叫者傳入）|相同|
|EDIT 的 OK 啟用|QuestDialogAdjust：EDIT 非空時 OK active，否則 inactive|QuestDialogAdjust2：相同|
|default/cancel|bCancel→cancelControl=CANCEL；bNext→defaultControl=NEXT|相同|
|SendReply|**Create 內無 SendReply**|**Create 內無 SendReply**|

兩份均依參數建立 PREV/NEXT/EDIT/OK/CANCEL，還能呈現 PORTRAIT/NAME/TITLE/DESC。兩份曾寫 dialog.defaultContol（拼字少 r），但其後還有正確的 dialog.defaultControl=NEXT；不能據 typo 宣稱 GUI 無法使用。**QuestDialog_Create provider 已確定為 QuestDialog.dat**，不再是未知檔名。這兩檔是純共用 UI 工廠，任務回覆值由外部 proc 決定；無法由它們判定 QuestID、任務完成、獎勵或 Server NPC→Script 配表。

## Client I/O／安全交接

既有 EXE/A12/A23 已證：ScriptRun 以 S44(1,0) 啟動；client.SendReply 在原生 writer 形成 C6C(1) = subtype1 + string8 runner_name + u32BE context + u16BE pair_count + 每對 string8(key,value)。TYPE 與 STATE 是腳本層 key/value，不是新 opcode。dialog.Dispose 只釋放 UI；client.Dispose 才是 native runner Dispose 可觀察路徑；不可把所有 dialog.Dispose 視為 C6C(4)/(2)。

Server 仍須基於**Server 發放的** session / world epoch / ScriptRun/context / NPC target 和合法 TYPE、STATE 選項白名單，拒絕重放、跨角色、錯 runner 或任意金流/獎勵。TYPE=BUY/SELL/BANK 等不授權貨物或餘額變動；STATE=ACCEPT 不授權 QuestCompleted；依既定 R-034，STATE=REFUSE 不異動 Domain、可再次交談。

## CT 與剩餘缺口

- CT-092：本次三原始 DAT hash/CRC/函式/8 項離線單元測試已 PASS；不等於真 GUI/TCP PASS。
- CT-093：原 Client 驗 Merchant.Main 依賴載入、TALK 立即 SendReply / nNewJoin 最終 STATE 的**實際 pair 集合**、BANK 下游 MerchantBank、QuestDialog2.SetPortrait 的真實畫面、EDIT 空值/鍵盤取消操作與 C6C 時序。
- CT-094：雙 Client、不同角色/世代、錯 NPC、重送、拒絕再問、商店/任務金流與獎勵權威結果；仍 planned/not-run。

**已具名並補齊：MerchantDialog.dat、QuestDialog.dat、QuestDialog2.dat。** 既有 A12 也已有 Merchant.dat、PaperDialog.dat、PaperDialog02.dat、nNewJoin01.dat 的原件驗證。仍未取得 MerchantBank、MerchantDirectTalk 的**實作提供者**；目前無可證的精確檔名，亦無原服 NPC→Script、QuestRule、Reward 來源檔名。需要 Script 資源索引或匿名化原版 Client/Server 雙向封包與 GUI 操作紀錄，不可編造 Quest.dat。

驗證：python tools/a012_new_dialog_original_probe.py（或指定 ASGARD_RESOURCE_DIR）；缺三原件時 skip 而非假報 PASS。
