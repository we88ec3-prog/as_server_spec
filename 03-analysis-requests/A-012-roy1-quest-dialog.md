# A-012 / roy1 — 任務腳本、對話選項與回覆（Client I/O BIN-first）

日期：2026-10-31；固定工作分支 \`task_a/roy1\`；原始 \`Asgard.exe\` SHA256 \`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145\`、\`Born.dat\` SHA256 \`992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98\`。R-013，SYS-QUEST。新的 A12 evidence \`ev_a012_20261031_script_reply_choice_client_static\`。參考 A-023/E14–E18、A-011/A-024 NPC、A-026 教學完成。方法：原始 EXE x86 writer + SendReply/Dispose producer call chain；本地 Born zlib/XML/CP950 CRC 再核；既有同 SHA 的 Script corpus 分析作**標明來源的先前研究**；不把先前研究冒稱本次持有全部 Script 原件。

**結論與完成界線**：A-012 已交付 Client 端的 Script start / 對話選項回覆 / 關閉 / 缺件更新流程，包含正反 codec、Server 消費者需驗證的 context/Session、測試向量。研究標 \`integrated/handoff_status=partial/implementation_ready=true\`，**僅已證封包/安全交接可開發**。沒有原版 Server 首次發送、NPC→Script、任務條件/旗標、完成/獎勵/真正 UI E2E 證據，\`native_quest_rule_ready=false\`、\`native_client_validation=not-run\`；不得稱原作任務系統已全面還原。

## 一、每一步的 Client trigger → C→S → S→C → Client reaction

|Trigger / Client state|C→S 發出|S→C 需接／可接|Client 本地反應及證據界線|
|---|---|---|---|
|Server 已指定執行一段 Script|**無必然先送 C**；若缺 resource，C6C(0,name)|**S44(1,0)** script:string8、context:u32BE、text CRC:u32BE、依賴和參數（詳 A-023）|native 0x586410 reader、0x52c2a0/0x52bd30→0x524fa0 呼叫 \`Main\`；缺件等候 S44(1,1) 更新；原服首次派送條件 unknown|
|Born.Main 的 PaperDialog 開啟|無證明會立即發 C|已先 S44(1,0) 加載 Born+PaperDialog|**本次本地 Born**：只建單頁紙張，導引 (31,29) 點女性招募員；(31,29) 不是出生點或 NPC id；未在原 Client GUI 直接顯示驗證|
|使用者在腳本 UI 選擇某個會呼叫 \`client.SendReply\` 的選項|**C6C(1,name,context,pairs)**|這一條回覆是否導致另一個 S44/NPC 包 **未知**；Server 必須按原生證據決定|0x526626→0x51a9f0 建立 CScript、\`[+0x24]=1\`、複製 runner 名稱/context 與 key/value，0x51ab33 replied flag=1，0x51ab3d enqueue 0x5788a0；此為**選項意圖**不是 authoritative 任務完成|
|使用者在 PaperDialog 點 OK，呼叫 dialog.Dispose→client.Dispose|**C6C(4,name,context)**，若未 SendReply 清理再送 **C6C(2,name,context)**|沒有必然 S44 回應；不推論 Server 完成任務|0x526873、0x5268c6；0x519479 的 replied flag gate，0x5194ce/0x5194f1 no-reply cleanup；關閉視窗不等於獎勵或完成|
|Server 更新 Script 快取|缺檔 C6C(0,name)；啟動成功後 SendReply/Dispose 分支如上|S44(1,1) asset update；S44(1,3) 會觸發本地 Script cache 掃描/刪除，不是普通 ACK|A-023 0x5294e0，資源 CRC mismatch 潛在不安全路徑；**不得對正式原 Client 送合成錯 CRC 或清快取測試包**|
|一般 NPC 點選／交易候選|C43(1,opaque-object-ref,4) 在已證兩條 UI producer 出現；C39 另有 Merchant 通道；**不能從此推導所有 NPC 點擊 opcode**|S34/S3C 是不同的物件資訊回包，S44 是 Script 通道；它們與 NPCChatDialog 的必然時序未證|A-011/024 研究，NPC id→Script 名稱仍 unknown；不把上述 C43/C39 直接等同 QuestAccept|

### 原版 wire 格式與實際生產者（observed-static）

C6C writer \`0x575210\` 首送 \`u8 subtype\`，\`0x575221\` 限 reader switch 0..4；byte 序來自 CScript 基底 writer default BE，string8 長度是**編碼後 bytes**、不含 NUL，LanguageMan 對 index4 取 CP950（region 不可無證強制所有 Client 都是 CP950）。

|C6C subtype|body（排除 opcode/frame/ordinal）|Native VA/Client 意義|
|---|---|---|
|0|u8(0), string8 script|0x575231；找不到快取時提出名稱|
|1|u8(1), string8 script, u32BE **context**, u16BE pair_count, \`pair_count × (string8 key,string8 value)\`|0x575240..0x5752B6；Producer 0x51AA5C、0x51AA70、0x51AA7F、0x51AB33/3D；key/value 來自 script reply collection|
|2|u8(2), string8 script, u32BE context|0x5752B9；無 SendReply 的 runner cleanup branch|
|3|u8(3)|0x575210 jump table；既有登入 minimal-profile 的 C6C(03) 不是任務回覆|
|4|u8(4), string8 script, u32BE context|0x5752D6；explicit client.Dispose branch|

C6C subtype1 pair_count 原內部 local \`[esi+0x220]\` 16-bit，陣列首位址 \`[esi+0x224]\`，每組 **本地** stride 0x400、key/value 的 local buffer 相差0x200，**wire 是兩個 string8，不是每組 0x400 bytes**。Producer \`0x51AA69/0x51AA70\` 由 runner \`[+0x224]\` 複製 context 至 packet \`[+0x228]\`（serializer 以對應子物件視圖 [esi+0x21c] 讀取）。0x51AB33 設 runner replied flag；no-reply cleanup 在 0x519479 查旗標，**不能**將 C6C(2)/(4) 認為可替代有 key/value 的 C6C(1)。

本輪原件 byte anchor **20/20 PASS**，包含 opcode、type dispatch、回覆的 u32/u16、pair key/value reader、SendReply/Dispose producer、replied flag、S44 opcode。完整重現 \`python tools/a012_quest_dialog_contract.py\`，14 個 unittest（含不合法 byte、str count、重送、錯 session/上下文與 duplicate-key）PASS；測試的 Server ledger 是 **designed，不是原版任務規則**。

### 原始測試 body，非原服抓包

以自行設定 \`context=0x11223344\` 和 ASCII、\`nNewJoin01\` 候選值產生的 **synthetic** C6C(1)：
\`01 0a 6e4e65774a6f696e3031 11223344 0001 05 5354415445 06 414343455054\`
= script \`nNewJoin01\`、一組 \`STATE=ACCEPT\`。此 **只是 codec 範例**，不是已抓到真實玩家按鈕而發出的固定封包，也不保證 Server 應立即入學/升級/發獎。

\`Born\` 的 OK 在先前已追通 PaperDialog close 下，原件 native producer 預期順序：
\`04 04 426f726e 11223344\`，接 \`02 04 426f726e 11223344\`。
有 SendReply 的 runner 可先送 subtype1 再送 subtype4；不應同時自動套用「無回覆 cleanup」和「有回覆完成」兩種結論。多個 native send 呼叫不保證獨立 TCP frame。

## 二、任務資料與候選對話的判讀

本次獨立核對 \`Born.dat\`：589 bytes、zlib 解包1154 bytes；**BE u16 version=1, BE u32 UTF-16LE code units=574**，完整原文在 CP950 的 CRC32 \`0x1D87B0C0\`；只含 \`Main\`，建立 \`PaperDialog_Create\` 單頁，無顯式 \`SendReply/Quest/Reward/Spawn\`。即使 XML 無 SendReply，Native Dispose 仍會送 C6C(4)/(2)。不能把資源內使用者閱讀的 (31,29) 設為原版出生點。

參照 A-023 已核對但**本工作環境沒有原始檔重跑**的 \`nNewJoin01.dat\`（SHA256 \`8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae\`）：\`MerchantTalk→JoinMessage01→02→03\`，最終 UI 候選 \`STATE=ACCEPT / REFUSE\`，透過 client.SendReply；\`Merchant.Main(args)\` 從 ServerParam 讀 \`TILE/MNAME/UGOLD/UBAL/UAGOLD/UABAL/UCOLOR\`，建立 ClientReply 與 UI。**這只是資源候選，不足以證明 Born 所指招募員就是 nNewJoin01**，也不足以證明原服接 STATE=ACCEPT 自動建立已完成 Quest。

正式 quest flag、任務步數、日誌顯示、條件（擊殺/採集/談話/任務物品）、獎勵內容/是否存在、發放與拒絕狀態、對話選項背後的原服判定均 **unknown**。不能從 C6C 可以帶 key/value 就宣稱所有 quest 使用它；也不能把 S0F/S10 庫存更新、S5F 怪物死亡、S14(2) 進圖，直接視為正式任務結算結果。

## 三、Server owner 安全契約（DESIGNED，非原作證據）

- Script catalog 是 \`(client_release_sha, script_name, textCRC, dependencyCRC, revision)\`；依實際檔案與 codepage 驗證後才可作正式 S44(1,0)。\`PaperDialog.dat\` 是 Born 的直接依賴；在缺實檔時不發正式 start；\`S44(1,3)\` 不作普通 ACK。
- \`ScriptRun\` 具 \`(character_id, session_generation, world_instance, script_name, context:u32, issued_revision, state)\`；收到 C6C(1)/(2)/(4) 先查唯一有效 run、正確 session/generation/map/可互動權限、長度與 pair_count、key 白名單；舊 run/重複回覆 fail closed / idempotent。**wire 沒有 session_generation**，必須由當前連線 Server scope 決定。
- \`ScriptChoiceObserved(STATE=ACCEPT)\` 不是 Server 對應的 \`QuestCompleted\`。由獨立、經核實的 \`QuestDefinition + QuestProgress + RewardGrantLedger\` 決定條件，原子提交任務/reward/outbox，絕不從腳本文字/Client key/value 直接授權資產；若原版規則未知，不啟用正式 completion/grant。
- C6C(4) 只標示 \`dispose observed\`，C6C(2) 只清理 \`no-reply\` runner；不同 opcode 的順序可在 TCP 同流合併。不可因兩次 close 重複觸發 mission event。重登入與切圖的舊 context 不得污染新 run。
- \`client.SendReply\` 只提供 UI 候選意圖；NPC 點擊必須另驗 map/instance/visibility/range/object-ref/Content binding，不能因同名 Script、Born 座標或 C43 ref 就認定 Quest NPC。

## 四、A gate / CT / 所需確切資料

- **CT-090**：原 EXE static producer/writer + Born UTF16/CRC、C6C subtype0..4 fixture；本輪工具已 14 tests PASS，原生 Client \`not-run\`。
- **CT-091**：原 Client Script start→PaperDialog/候選 nNewJoin 對話→按 OK/取消/選擇後擷取真正 C6C subtype1/2/4、UI 變化；缺/CRC 不合用隔離複本，禁止故意對正式 Client 送錯 CRC；\`planned\`。
- **CT-092**：兩連線（同圖）、stale context/重送 C6C/先關閉後選擇、獎勵唯一性、斷線/轉圖再開與 NPC 實例綁定；需原 Server trace 或新 Server synthetic 與原 Client 區分驗收；\`planned\`。

**精確缺件（限本次未提供的原始資料）**：\`PaperDialog.dat\`、\`nNewJoin01.dat\`、它的共用入口 \`Merchant.dat\`（此名稱在舊分析中僅見 \`Merchant.Main\`，**此檔名未獨立核實，不能當已確認缺件**）；要把對話 UI 與任務條件再推進，應提供真正 \`PaperDialog.dat\`、\`nNewJoin01.dat\` 及其已確認的 Script 依賴，另提供匿名化「點 NPC→選項→成功/拒絕/重登」雙向封包 trace。要重現真實任務完成還需 NPC/entity→Script 綁定、原服 Quest 規則/獎勵證據；這些資料**目前確切檔名未知**。已提供 \`Asgard.exe\` 和 \`Born.dat\` 不需重傳。

研究完成狀態 \`integrated / partial\`、\`native_client_validation=not-run\`。這不阻擋 DEV 使用已知協定實作安全 Script 運行狀態機，但也不代表原始任務/獎勵已還原。
