# 初級學校入口／雙 PaperDialog 的 Server 可開發契約

來源：[2026-10-31 新資源驗證](../04-analysis-integration/new-asset-samples-20261031.md)。這份文件是 **ONB-05/06、DEV-070-M/090 的 Server 設計交接**；不是原版 Server 的選校政策。使用者決策維持：**不修改 Asgard.exe；帳號只能管理員建立；創角輸入帳號≠已登入帳號必須拒絕；同 world/map 玩家共享 NPC/怪物**。

## 玩家看到的候選體驗（分辨已證與待證）

1. 入世界後，在 Server 自定且版本化、**已被地圖合法性驗證**的安全點出現；如 Server 選擇推送 Born，依 S44(1,0) + 實際文字 CRC、PaperDialog 依賴開始指引。Born 文字指向 (31,29) 女性招募員，但不是已證出生點/NPC ID。
2. 和疑似入學招募員對話：`nNewJoin01.dat` **確實含**初級學校三頁對話，MerchantTalk 呼叫第一頁，NEXT/NEXT 到第三頁選入學；**究竟哪個 NPC、哪個 Client click 與 S44/其他 UI 訊息啟動此 script，未證**。
3. `STATE=ACCEPT` 表示 **玩家選擇願意進入初級學校**；`STATE=REFUSE` 表示拒絕。兩者都僅為 ScriptReply，不等於出生、直接切圖、任務完成、發獎。這些後續決策必須配置 Server policy，與 native Client 載圖、NPC 互動的證據 gate 分開。
4. `PaperDialog02` 的 `PAPER02=START/NOT` 是另一個**獨立來源**的選擇，不可當 `STATE=ACCEPT/REFUSE`，也不可在目前無來源時假定它是初級學校的下一步。
5. 設計階段不能同一 ScriptRun 同時無條件 import `PaperDialog.dat`、`PaperDialog02.dat`：二者都宣告 `ShowIndexedHelp`/ `PaperDialogProc`；要依版本與本次 Script dependency 區分，避免 callback 名稱衝突。

## Server 的 Session/Script admission policy（designed）

```text
Authenticated + WorldReady + SharedMapParticipant
  → NPC target validated (same world/map/AOI, current life_generation)
  → verified NPC→script binding, otherwise native dialogue blocked
  → ScriptRun(account,character,world,conn_generation,script_name,context,release_sha,state=RUNNING)
  → C6C subtype1 reply, exactly one recognized key/value for this run
      nNewJoin01: STATE=ACCEPT / STATE=REFUSE
      PaperDialog02: PAPER02=START / PAPER02=NOT
  → session/context/script/release/one-time reply validation
  → AdmissionIntent(ACCEPTED / REFUSED / PENDING), idempotent transaction
  → optional next script/map/quest ONLY if independently configured and validated
  → C6C subtype4 closes runner; subtype2 cleanup only if native state allows
```

- `C6C` client reply 是**使用者意圖**，不是 Server 授權。Server 透過 account/session/character/ScriptRun/context 綁定；`STATE`、`PAPER02` 及其值均須白名單，拒絕亂序/逾期/跨場景/跨角色/重送不同值。
- `AdmissionIntent` 唯一鍵建議 `(character_id, script_run_id, intent_type)`；首次合法 `ACCEPT` 只記錄選校意圖。重複同值為 idempotent；不同值或舊 generation 為衝突／拒絕。拒絕/逾期不動 `TutorialCompleted` 或物品。
- `STATE=ACCEPT` 後如要讓玩家真正進入初級學校，Server 必須能綁 `source_npc → entrance_rule → approved_destination(map_ref,x,y,revision)`、有權的世界切圖 `S15/S14/C35/S04/S33`、以及更新 WorldReady 的 durable checkpoint；**目前原版 destination/map/生效時機未知**，只准用 Development fixtures 合成測試，不准用虛構原版 ID 進 native profile。
- `STATE=REFUSE` 不改世界與任務完成；允許再次交談需新 ScriptRun/context，避免過期封包復活上一個選擇。
- `PAPER02=START/NOT` 保存在獨立的 `Paper02Intent`，只有確認它的上游 trigger / script name / 原 Client 事件後才賦予具體玩法語意。
- `Born` 普通 OK 是 close；`nNewJoin01` reply 是選擇；`TutorialCompleted` 要由**獨立且有證據的任務條件**寫入 unique ledger；`TutorialExited` 要另經合法地圖 checkpoint。不能以 C6C(4)、C6C(2)、`STATE=ACCEPT`、`PAPER02=START` 或 C0B 直接標畢業。
- `SharedMapKey(world_id,map_ref)` 的 NPC/怪物只生一份；玩家 A/B 各有私人的 ScriptRun/AdmissionIntent/TutorialProgress。A 的對話、拒絕、斷線不可改 B 的 NPC/任務狀態。
- `Monster00.dat` 含 5 個 YPF 成員、`World00.dat` 含 5 個場景 YPF 成員，作內容檔指紋與索引；**不推斷**角色種類/怪物生成點/演出 motion，也不把 archive member index 當 native image slot。

## 安全分段交付

|切片|現在可以做|必須等待的原生證據|
|---|---|---|
|DEV-070-M/Content|依 SHA、包內 member 名稱/大小驗證內容 release；避免資產錯版、錯索引；仍共享一張 map|A-011/024 imageID→YPF member→motion、NPC type/renderer/點擊|
|DEV-090/Script|Script text CRC32(cp950 profile) 與依賴版本 pin；`STATE` / `PAPER02` 分開 decoder/Domain；reply+close、逾期、重送、不同值、跨玩家 synthetic tests|原版 dialogue Main/QuestDialog_Create 依賴、C6C 真 UI 事件與 NPC 綁定|
|DEV-090/Admission|AdmissionIntent、拒絕後重試、斷線恢復、安全 Server policy hook；不直接寫 QuestComplete|A-023/026：原版入學後何時、往哪張圖、Client 如何處理|
|DEV-050/060|已有 map loader/C35 gate；僅版本化可驗內容；不得硬編未證 map id|(A-022/A-005) 真可用 map_ref/spawn/碰撞/CRC|
|CT|離線 Script/容器檢查 + Server synthetic 可先跑；原版 CT 保留 not-run|兩原始 Client 有 NPC 對話選擇、入學切圖、怪物/動畫可見的實機證據|

**尚缺具名來源**：本次要求的五檔已齊，**不再要求重傳**。如需完整 `QuestDialog_Create`，必須先查真正的 Script dependency 清單，確定檔名後再請使用者提供；`Basic.dat` 與其他 YPF 動畫可從已有庫證據比對。不得憑此檔宣稱招募員外觀或地圖已還原。

## A-023／2026-11-01 靜態 Script 與素材可用性修正

新增 [A-023 本地原件補證](../task_a/roy2/A-023-born-basic-native-dispatch-20261101.md)：原始 `Basic.dat` 確實含 `AlertFrame.ypf`（offset13196、177648B、SHA b641441d…、YPF17），Born.Main 的文字 CRC `1d87b0c0` 可從本輪實際原件復算。**PaperDialog.dat 為 Script 真正依賴**（既有 SHA/解析報告，這次沒有重新收到其原件）；要實際讓原生 Client 顯示紙張，必須有相符依賴及正確 S44(type1,subtype0)，並另驗原 Client GUI。

原始 Client `S44(type2,subtype0)`、`S44(type2,subtype2)` 在外層 handler 各操作 GUI slot0x23/slot0x24；**不能拿兩者當作 Born 的 type1 Script 啟動、回覆 ACK 或原服初始任務已建立**。Client 的 Script wire/快取/關閉是可交付子集，但原服「第一個 NPC 是誰、是否第一次進圖自動下發 Born」依然沒有 Server 事件/NPC binding，因此仍按 **ONB-05/06 P1** 待查，不影響 P0 入圖和基本可移動。

已驗證原生靜態補證為 CT-112；CT-033～035 原版 Script GUI／NPC 仍 not-run。需要具名 Script 原件做獨立重跑可請提供 `PaperDialog.dat`，對照學校入學候選另可用 `nNewJoin01.dat`、`Merchant.dat`；本專案已留原始 SHA 及歷史解析，**不能用資源名字推論 NPC ID/Spawn**。

## A-023 2026-11-01 原始四 Script 對話連接與選校風險

已直接取得 [PaperDialog、PaperDialog02、nNewJoin01、Merchant 四份原件](../task_a/roy2/A-023-four-script-native-dependencies-20261101.md)。SHA、原生 BEu16+BEu32 UTF16LE 包裝、CP950 文本 CRC 與原始函式全部核對；此前的 Script 選項只按名稱推測，現在已能確定：

- `Merchant.Main(args)` 建立 global `ServerParam`／`ClientReply`，但沒有證明原服哪個 NPC／S44 root 引用 `nNewJoin01`。`nNewJoin01` 自身**沒有 Main**，只提供 `DoesTalk=true`、`MerchantTalk` 和 3 頁的 `QuestDialog_Create` 互動；選擇 OK → `STATE=ACCEPT`、CANCEL → `STATE=REFUSE`，為 C6C(1) 的 Script reply 意圖，並非 QuestCompleted 或入學已核准。
- `PaperDialog02` 是**不同的輔助紙張腳本**，按 OK→`PAPER02=START`、CANCEL→`PAPER02=NOT`，不能與 nNewJoin 的 STATE 混為單一控制。原 Script 竟將 `dialog.cancelControl` 設為 `OK`（仍有 CANCEL 按鈕），故 ESC 按鍵可能作 START：Server 只能以真 C6C1 作選擇，鍵盤路徑待 Native CT-035。
- `PaperDialog.dat` 與 `PaperDialog02.dat` 都宣告 `PaperDialogProc`／`ShowIndexedHelp`；需按 root/依賴明確選其中一個，**不可不分場合雙匯入**，同名碰撞原版處理未知。
- `Merchant` root + `nNewJoin01` dependency **若如此配置**，C6C1 封包 script name 應是活躍 root `Merchant`；不要直接期待 `nNewJoin01`，必須根據 Server 自己發出的 S44 名稱與 context 驗證。這個配置尚未由原服 trace 證明。
- **真正缺件**：四份檔沒有 `QuestDialog_Create`、`MerchantDialog_Create`、`MerchantDirectTalk` 的函式定義；可能的 `QuestDialog.dat`／`MerchantDialog.dat` 只能列來源待驗候選。缺乏女招募員原服 NPC EntityId/map/spawn→Script root/依賴、任務條件與後續地圖流程；不因已讀入四檔就自造 NPC/quest。
- 既定 R-034：REFUSE 是無副作用的意圖、允許合法重新互動；ACCEPT 也只能先建安全的 AdmissionIntent，沒有已證的 Server 終局權威規則與 destination 就不能標教程完成、切圖或發獎。

目前 DEV-090 的 Script codec/資源 registry/ScriptRun reply/close 和選項 idempotence **可開發**；原版 NPC 對話 renderer、QuestDialog 依賴與原服綁定**未通過 Native CT-034/035**，不改變 P0 的 World 可移動優先順序。
