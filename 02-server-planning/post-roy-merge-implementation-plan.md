# 2026-10-31 Roy1+Roy2 成果整合後的 Server 接續開發計畫

規格基準：`as_server_spec/main` 已 merge `task_a/roy1@258f5ba2dd845314a43ddb428aafad26a0533ca0` 和 `task_a/roy2@9e3b0ce1f5121909ea2760e8a2ceadb47abeb90b`。**既有決策不變**：`Asgard.exe` 不修改、管理員建帳、創角輸入帳號必須等於已驗登入帳號、**多人同 world/map 共用 NPC／怪物**。本文件是設計及交付；不是 Server 程式已實作，也不是原版 Client 已完成 CT。

## 研究可直接轉給 Server 的部分

|A|已證原 Client 送包／收包子集|立即可開發的 DEV|缺口／不能外推|
|---|---|---|---|
|A-020 Roy1|C0F(type3/other)→S18(kind0/1)，C57(0/1)→S56 多項壓縮清單，C4B(empty) 與 S60(type0/1) parser|DEV-020/030 codec、長度/解壓上限、會話狀態機與拒絕|原服何時送 S60、各 region seed/key、異常 UI 未證|
|A-004 Roy2|Player S33、S06/S11/S0E，C33/C11／自身 S0B 的可見/移動子集|**DEV-070-M** 玩家 Participant＋AOI Snapshot/Delta|Client 真 ObjectRegistry key、生/消回調和兩原 Client 互見仍未證|
|A-005/006 Roy2|C33/C11/S0B 的移動回覆、S05/S33 的已知外觀欄、MAP 格式/旗標候選|可信 Server 座標（與 Observe 解耦）、玩家入視野外觀投影|碰撞 bit 真語意、方向/動畫資源及原生 UI|
|A-008 Roy2|S08 conditional status/Stats；C47 能力點候選|DEV-080 Status projection／非授權變更拒絕|Client UI 屬性欄/回血/死亡全部狀態|
|A-009 Roy2、A-025 Roy1|C13 攻擊 BE u32，C3D/S3D battle variants，S13 傷害，S5F 死亡；C4D/C56 等 Roy1 已證子集|DEV-080 攻擊命令/target 校驗／傷害結果/技能測試骨架|原生戰鬥 subtypes/冷卻/技能/教程是否需擊殺未證|
|**A-024 Roy2**|**S07 DrawObjects 1..14 type 非空 row、S0C/S64 移動、S34/S3C 信息、S62/S63 Action、S29 Effect、S5F 死亡、S0E 移除；C13/C43 是 C2S**|**DEV-070-M 第二段 Native Actor Adapter 的 decoded-body codec**|S07 1..14 何 type 是 NPC/Monster、資源/sprite/EntityId/點擊UI 完整路徑尚未知|
|A-007 Roy1|物品 C1C/C08/C0C、S0F/S37 可變內容子集|物品 Domain/安全校驗，可獨立開發|原版物品定義/實際堆疊、裝備規則、回包 UI|
|A-019 Roy1|S19 音樂與 Music/%05d.mp3 selector、MAP 目錄索引|合法 map audio cue registry/版本 gating|map→track original mapping、原版音檔取得不明|
|A-026 Roy1|Born Main 僅引導 (31,29) 找招募員；C6C(4/2) 關紙、C39/S2F merchant 候選、通用 S15/S14/C35/S04 切圖|DEV-090 ScriptClose/QuestCompleted/Exited 分離，完成/獎勵唯一 ledger 和復原|任務完成條件、官方 NPC/出口 map/位置/獎勵皆未證|

**原生 Opcode 爭議必須隔離**：Roy1 將 `S1E` 標為 `DieObjects`，其引用的 parser `0x57E260` 卻是 Roy2 從 RTTI/ctor 指到 **S5F DieObjects（0x5F）** 的 reader。同一 parser 不能憑 Roy1 類名認定 S1E 也為死亡；`PKT-S1E` 登錄已標 disputed，**Native Monster Death 暫僅按已證 S5F**，需 A-009/A-025 補對 `0x57E030` S1E 真正 vtable/reader。對象死亡與離開視野不可混用 S5F/S0E。

## 分段工作順序（不額外產生正式 DEV 編號或 Git branch）

**第一段：DEV-070-M，Server 共享 Actor 與可靠 AOI（現在可做）**

1. 原本 `TutorialSceneRuntime` 以 `CharacterId` key 的私有 Scene → `SharedMapKey(world_id,map_ref)`，同 map 同 revision 只有**一份** Actor Registry/Monster Tick。保留每 Character 獨立 Auth/Lease/Quest/Observer；A 登出不能抹掉 B 的 Monster 或 Instance。
2. `Join/Leave` 必須針對 `account+character+generation+connection` 做 fencing；重登同角色替代舊 Session，舊 logout 不能操作新玩家；Server 確認 C35 durable commit 才 Join。
3. `Observe` 不允許改玩家權威座標；`CommitValidatedMove` 只接受已驗 Session／合理速度與 MAP collision。A-005 的 bit4/bit0 仍候選，未驗證碰撞設 Development-only fixture、正式相容 fail closed。
4. `EntityId` 對同地圖所有玩家一致；每個 NPC/怪物有 `life_generation` 和 `event_seq`。先建立共享 Snapshot 和 per-player AOI Diff 的**內部**事件，不直接送未知 Client native packet。用 CT-055 + CT-070/075 測 A/B 共同 Actor、移圖、重連、舊包、重生不重複。

**第二段：DEV-070-M 原生 Actor Codec/Adapter（有據子集現在可做；發送依證據 gating）**

1. 以 `PKT-S07` 1..14 的**decoded body** 作嚴格 serializer；不把 local 0x228 stride 當 wire；依 A-024 type 1/2/4 flags conditional、type3、5..12、13、14 補測 CP950/string8、長度/計數/未知 type fail closed。
2. `S0C` 單次移動、`S64` path count（**保守限制 ≤11** 是 Server designed safety gate）、`S5F` 死亡、`S0E` remove 可先實作 codec/序列。S34 subtype11 動態 flags、S3C、S62/63、S29 僅按有證 UI/語意使用，不因 packet 存在就發。
3. 對玩家使用 S33/S06/S11 與 NPC 非人 S07/0C/64 的不同路徑，不能拿 S33 代替怪物。NPC/Monster visual kind→資源及 Client ObjectRegistry 真 handler **由 A-024/A-011** 補證後，才允許原始 Client 看見，CT-080/081/native CT-055 仍 not-run。

**第三段：DEV-080 戰鬥／狀態／技能（Domain 可先做）**

`AttackIntent(C13 target BE u32)` → 驗 Session/同圖 EntityId/存活/距離/合法目標 → 單一 WorldEvent → 共享怪物 HP/死亡 → AOI 效果；`S13` 傷害與 `S5F` 死亡對不同觀察者投影分離。S08 角色狀態、C3D/S3D subtype 加入安全白名單；技能清單、實際動畫/公式、體力/冷卻在 A-010/A-025 內容前不得宣稱原版。掉落/經驗/多人擊殺貢獻**尚未有使用者決策**，保持獨立 policy hook，不預發獎。

**第四段：DEV-090 任務／出圖（Domain 可先做）**

Script `Born` 顯示/關閉只更新 `ScriptRun`，不更新 `TutorialCompleted`。NPC C39/Script reply 僅能作候選 Client 意圖；Server 只在確認的任務事件下提交 `TutorialCompletionLedger`、可選獎勵 ledger（**不假定獎勵存在**）、`ExitCheckpoint`；重試/崩潰不重複。原版出口地圖/座標/quest 配置及必做戰鬥都尚未知，Native CT-026～028 與新增 CT-061～063 保持 not-run。

## 原版 Client／程式碼驗收分離

- 已取得：兩分支來源報告、原始 EXE 靜態位址/封包 codec、部分合成測試；沒有新完成的原版 Client E2E。
- CT-054：原版已登入空角色→NewUser 尚未證；無效 C02 不可授權；登錄主政策不變。
- CT-055：**多人同圖共同 NPC/怪物**仍 planned，需兩原版 Client 和 A-004/024 renderer/原生消息完整對應。
- CT-056～081：兩個分支新增的 test-plan（部分 static/offline）；**新編號不代表實際執行或通過**。原始來源號碼對照 [CT remap](../05-conformance/ct-id-remap-roy1-roy2.md)。
- 原服不知道/未提供的 Server AI、掉落、任務、版本及 map 資料可先自行 design；不要求 A 反推原服 DB。Client 沒有原生可達的 UI/封包不可為了排程強行虛構。

## 仍需分析的 Client 問題

詳見 [下一輪可發給 A 開工的精確清單](../03-analysis-requests/post-merge-analysis-queue.md)，只列真正的 Client trigger→C2S→S2C→reaction、資源 identity/renderer 證據；不再籠統要求「完整還原 Server」。

## Roy1 A-004 / Roy2 A-011 最新補證（2026-10-31）

- **A-004**：原始 S07 decoded `u32 object_ref` 進入 `0x4F17C0` DrawObjects handler，再由 `0x4EAC30` 查 MapPane registry；補 S1A Motion，且更正先前錯把 S1E 認作 DieObjects 的說法。Native death packet 是 **S5F**，死亡≠S0E 離場。
- **A-011**：S07 kind **1/2/4** 會建立 `MonsterObject`（ctor `0x4D6FA0`），但不能因此宣稱三種 kind 分別代表何種 NPC/怪。Resource Library **World IDs 7000..7023** → `World%02d.dat`、**Monster IDs 8000..8042** → `Monster%02d.dat`；Monster Image ID `0x4000+` 按每檔 10 槽：library=8000+floor((id-0x4000)/10)，slot=(id-0x4000)%10。0x4000..0x41AD 是 Server designed 安全範圍，不是原服官方全域值。
- **檔名更正**：原 EXE 寬字 literal 以 `@Monster` 開頭，但查檔呼叫指向第二個字元，實際使用 **`MonsterNN.dat`，沒有 `@`**。
- **C43** 兩條原生 producer `0x479DC7`、`0x4A23F8` 都可構造 `01 BE-u32 04`，仍未證明 NPC 點擊一定送 C43、也未連成 S34→NPCChatDialog 的完整路徑。

DEV-070-M 可以立即增加 `MonsterResourceCatalog` 及由原始 id→檔名/槽的安全映射、原生 S07 kind1/2/4 to MonsterObject adapter 設計、共享地圖 AOI；**實際原版 Client Sprite、NPC 對話與原生 CT-082～086 仍 not-run**。
