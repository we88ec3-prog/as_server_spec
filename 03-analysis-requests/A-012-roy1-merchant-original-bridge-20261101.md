# A-012／roy1 — Merchant.dat 原件驗證、初級學校對話依賴與 C6C 回覆邊界（2026-11-01）

**工作範圍／結論：** 使用新提供的原始 `Merchant.dat` 重新完成 `Merchant.Main`→共用 Script globals→`nNewJoin01.MerchantTalk` / `JoinMessage01..03Proc` 的**靜態資料依賴交叉證據**，確認原版 Script 可取得回覆容器與 NPC 顯示資料，但**未證明真實原服 NPC 實體與 Script 綁定、某個已載入 runner 必然執行此 hook、實際 GUI/TCP 封包或官方任務／獎勵政策**。A-012 的 Client I/O handoff 維持 `integrated/ready`（**僅限已證的原生/資源子集**）；`native_client_validation=not-run`、`native_quest_rule_ready=false`、`native_npc_script_binding_ready=false`。不更改 `Asgard.exe`、Server/DB 或官方資源。

## 一、為何 A12 必須提供 Merchant.dat？

原先提供的 `nNewJoin01.dat` 只有 23 個 `function`、**沒有 `Main`**，但其 `JoinMessage01` 呼叫 `QuestDialog_Create(MerchantTile,MerchantName,...)`，最終 `JoinMessage03Proc` 透過 `ClientReply.Add("STATE","ACCEPT"/"REFUSE")` 然後 `client.SendReply(ClientReply)`。在這份檔案本身找不到 `MerchantTile`、`MerchantName`、`ClientReply` 的建立／指派位置。**單憑對話資源不能安全決定實際 Script 執行環境、ServerParam 欄位與 Client 回覆的 runner scope**。

你提供的 **`Merchant.dat`** 正是此缺口的重要原始資源：只有 `Main(args)` 一個函式，會宣告/設定共用 globals，並依 ServerParam 與 NPC 可用功能建立/分派對話。它是**共用 Merchant/NPC UI 執行入口**，**不是**官方 Server 商店商品、價格、任務條件或 NPC 生成資料。

|Merchant.Main 原始來源|Client local script 變數／行為|與 nNewJoin01 的關係|
|---|---|---|
|入口 `Main(args)`|`client.AddGlobal("ServerParam",args)`|保存 S44 Script 執行時參數，**不是**由 Client 自行證明的授權|
|`client.CreateParams()`|`client.AddGlobal("ClientReply",reply)`、`ClientTemp1`|nNewJoin 最後一頁的 `ClientReply.Add` 使用這個**候選共同環境來源**|
|`args.Get("TILE")` → `client.Str2Int`|`MerchantTile`|nNewJoin 的 `QuestDialog_Create` 顯示參數；**不是**已證的網路 EntityId／地圖座標|
|`args.Get("MNAME")`|`MerchantName`|nNewJoin 三頁 Dialog 的 MerchantName 顯示參數|
|`UGOLD`、`UBAL`、`UAGOLD`、`UABAL` → `Str2Int`|`UserGold`、`UserBalance`、`UserAvailGold`、`UserAvailBalance`|共用商人介面資料，**不等於權威金額／授權獎勵**|
|`UCOLOR`|`MerchantColor`、部分 `MerchantDialog_Create` 參數|外觀/選單參數，不是原服 NPC model binding|
|`GREETING`（若有）／`BuildMuttering()`|`MerchantGreeting`、`GlobalGreet`|nNewJoin 的 `BuildMuttering` 提供候選文字；取用哪段是原生分支但 GUI 未跑|
|`TYPE` 條件|`BUY / SELL / REPAIR / BANK / IDENTIFY / DIRECT` 分支|Client script 含這些分派/呼叫；**`DIRECT`→nNewJoin 的確切 UI 事件仍未追證**|
|若無 `TYPE`|`DoesBuy/Sell/Repair/Bank/Identify/Talk` 再 `MerchantDialog_Create(...)`|nNewJoin 的 `DoesTalk()` 回 true，其餘交易功能回 false，因此是**對話能力候選**，不代表 NPC 已有原服實體|

`Merchant.Main` 還設定常見的對話按鈕 object ID `OkObject=13`、`CancelObject=14` 與排版/文字配色 globals。這些是顯示素材/本地控制值，不能拿來當 network opcode、NPC ID 或任務 flag。

**重要依賴邊界：** nNewJoin01 裡的 `MerchantTalk()` 會呼叫 `JoinMessage01()`，後者接 `JoinMessage02()`、`JoinMessage03()`。但是 `Merchant.dat` **沒有**函式 `MerchantTalk`、`QuestDialog_Create`、`MerchantDialog_Create` 或 `MerchantDirectTalk` 的定義，它只是呼叫共用 hook/對話 UI。本輪兩份檔的相容呼叫關係是 **resource-level dependency evidence**，**不是**證明 Script VM 有哪個固定執行/載入順序，也不等於 NPC entity→Script name 映射已證。不要憑名字創造 `QuestDialog.dat` 檔名。

## 二、原始檔案與可重現證據

|原件|bytes|SHA256|解壓 bytes／UTF16LE code units|CP950 XML CRC32|
|---|---:|---|---|---|
|`Merchant.dat`|1603|`6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350`|7856 / 3925|`E9B389CF`|
|`nNewJoin01.dat`|1359|`8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae`|9962 / 4978|`D9390353`|
|`Born.dat`|589|`992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`|1154 / 574|`1D87B0C0`|
|`PaperDialog.dat`|1639|`5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054`|9196 / 4595|`F870C574`|
|`PaperDialog02.dat`|1771|`49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a`|10518 / 5256|`42683546`|
|`Asgard.exe`|3235840|`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`|PE32, not zlib|不適用|

上述 Script 均以 zlib 解包，`BE u16 version=1 + BE u32 UTF16LE units`、UTF16LE XML text，再以 CP950 bytes 做 `zlib.crc32`；此 CRC 是 **XML 原文文字 CRC**，不是 .dat raw SHA 或整包 CRC。已重驗 `Merchant.dat` 僅 `Main`，`nNewJoin01.dat` 含 `MerchantTalk` 但無 `Main`，原版 EXE C6C/S44 指令定位 7 個簽章。**本地 25/25 個 unit tests PASS**，包含真原件 SHA/CRC/依賴/回覆、錯誤選項、格式不良/篡改檔拒絕；只代表離線驗證，非原 Client GUI/Server E2E。

可重現：`python tools/a012_merchant_bridge_probe.py`；預設從 `/mnt/data` 讀原始檔，或設 `ASGARD_RESOURCE_DIR`，個別資源可覆寫 `ASGARD_<FILENAME_WITH_DOT_TO_UNDERSCORE>`。乾淨 checkout 沒有原遊戲檔時將相關原件測試標記 skip，**不能宣稱未執行的 native checksum PASS**。本次原件不入 Git。

## 三、整條 Client 對話流程與 Server 最小安全契約

|候選入口/操作|原版 Source 已證|Client→Server／限制|
|---|---|---|
|Server S44(1,0) 指定已存在的 Script runner 和相依資源|可執行 Main（需要提供的 Script 名稱/CRC、runtime 版本與依賴正確）|**無法由 Merchant.dat 證明原服在哪次 NPC 點擊時下發 S44**|
|`Merchant.Main(args)`|讀取 `TILE/MNAME/.../TYPE`，註冊 `ServerParam`／`ClientReply`／Merchant globals，為 UI/後續 hooks 準備環境|不因 Client 看見選單就獲得 Server transaction、NPC interaction 或任務完成授權|
|`nNewJoin01.MerchantTalk()`|→ `JoinMessage01`（下一頁）→ `JoinMessage02`（上一/下一）→ `JoinMessage03`（上一/OK/CANCEL）|**原服使用哪個 runner.name、context 和 NPC binding** 沒有確證。此檔無 Main，不能僅用 S44(name=nNewJoin01) 取代共用入口|
|`JoinMessage03Proc` OK|ClientReply.Add(`STATE`,`ACCEPT`)、SendReply、dialog.Dispose、client.Dispose|Native C6C **subtype1** 帶 ScriptRun.name、context、pairs；`STATE=ACCEPT` 是 Client 選擇意圖，**不是** QuestComplete/Grant|
|`JoinMessage03Proc` CANCEL|`STATE=REFUSE` 走同樣回覆/關閉流程|Server 應依 R-034 不更改 Domain，可再次合法互動；不假定 NPC 已自動離開|
|`Born.Main` / `PaperDialog`|只顯示單頁引導、紙張 OK 只 Dispose|native C6C(4) 後 unreplied C6C(2)，與 nNewJoin 回覆 C6C(1) **不同**|
|`PaperDialog02`|PAPER02 START/NOT 兩選項|獨立腳本的 C6C(1) 意圖；Merchant.Main 不能證明它也使用 Merchant 的 ClientReply/context|

原始 EXE：C6C constructor `0x575159`、type1 producer `0x51AA5C`、replied flag `0x51AB33`、C6C4 `0x5268C6`、no-reply C6C2 `0x5194CE`、S44 opcode `0x5862F9`。C6C(1) body 是 `u8 type1 + string8 script-runner-name + u32BE context + u16BE pair_count + n×(string8 key,string8 value)`；CP950 在 TW index4 有證，其他版本不強制。**Script 檔名 ≠ 未驗證的 live runner.name**，`TILE` ≠ 可證的 NPC entity/world ID。Server 必須先以 Server 發出的 Session/ScriptRun grant 綁 character、world instance、NPC target、resource revision、context 和合法 option keys，拒絕 stale/跨角色、任意重播與私自 STATE=ACCEPT。接受後的具體任務或獎勵還需原服權威證據/另案決策。

**高風險原 Client 路徑**：S44 type1/subtype3 可能清 Script cache，CRC mismatch 可能觸發 unsafe/native dangling pointer；不得拿正式 Client 做盲發亂 CRC 的黑箱測試。CT-092 offline 本輪 PASS，CT-093 真 GUI 的 Merchant→QuestDialog→選項→C6C 與 CT-094 Server 多人/授權／重播與 QuestRule 仍 planned/not-run。

## 四、A12 真正結案的範圍與剩餘需求

**已補齊**：以前明確要求的 `Merchant.dat`，其原始 Main 所做的 globals / ServerParam schema / Talk-capability/TYPE 分支已得到與 nNewJoin 的直接跨 Script 源碼引用。此前原件要求的 `PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat` 亦已完成 SHA/CRC 比對，**本輪不再缺這四個名稱已證的檔案**。

**仍未知且不虛構檔名：**
- `QuestDialog_Create` 函式的 Script/engine **實際實作來源檔名尚未證明**；`MerchantDialog_Create` 和 `MerchantDirectTalk` 的真正實作來源亦未在現有五份 Script 內定位。不可擅自指定 `QuestDialog.dat` 等猜測名稱。
- NPC entity ID、map／spawn、哪個 click/interaction 對應 Server S44(name,context,deps) 及 nNewJoin hook，以及原服首次發送政策：必須以 A-011/A-024、確切 Script corpus 其他依賴或**原版 Client/原服互動 trace**確認。
- 正式 QuestRule、STATE=ACCEPT 後是否入學/進度/獎勵/轉圖/持久結果與拒絕後的 UI 重開：這是 **Server authority**，不可能從 Merchant.Main 裡的 `TYPE` 或 `ClientReply` 字串解出。
- 未修改原版 Win32 Client GUI/TCP 未執行，S44 入口和真 C6C(1/4/2) 時序仍 CT-093/094；已完成的 25 個離線測試不得充當此項 PASS。

交接結論：**`A-012 status=integrated, handoff_status=ready, implementation_ready=true`（Client I/O 靜態+資源已證子集）；`native_client_validation=not-run, native_quest_rule_ready=false, native_npc_script_binding_ready=false`。** 本文件與離線驗證為 DEV 可用證據；不修改 Client/Server/DB，不上傳私有原始素材。
