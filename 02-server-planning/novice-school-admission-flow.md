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
