# A-025 / roy1 — 原生 C3D/S3D 全分支表與新手戰鬥 Client I/O 靜態結案（2026-11-01）

本次沿用 task_a/roy1，根據原始 Asgard.exe 與 Born.dat 及已合併 A-008/A-009/A-010/A-024/A-026 證據補正原版 Client 戰鬥介面。**交付為已證的 Client I/O 靜態範圍；不是原版實際技能/怪物/任務完成成功，也不是原 Server 的原始公式**。不改 EXE、不建新分支、不提交私有資產。

## 原件和現有依賴

- Asgard.exe PE32 3,235,840 bytes，SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145，ImageBase 0x400000；22/22 新增 native instruction windows 和 32/32 C3D/S3D jump-table entries 經原件比對 PASS。
- Born.dat SHA256 992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98；zlib 解開 XML Main 僅含 PaperDialog_Create 與往 (31,29) 女性招募員的文字導引。這一份腳本沒有顯式 attack/skill/quest/reward/SendReply，但**不能推論其後所有官方教學腳本都不需要打怪**。
- A-009 另已證 C13、S13 DamageEffect 的 14/31B bit0 optional 分支、S5F DieObjects，以及 C3D/S3D 的基本 selector。A-010 另已證 C4D/C56/S52/S48/S2C(0x2C)/S2D(0x2D) decoded wire；這些不等於 spell catalog/原服 CD/MP/命中。A-024 的物件生成/怪物資源還沒有官方首次教學 NPC→怪物的權威綁定。
- 本輪新增 tools/a025_battle_variant_probe.py 與 14 個 unittest（含真 EXE 靜態與合成正反向 codec）**14/14 PASS**，舊工具 tools/a025_tutorial_combat_model.py 原有 14 anchors/7 tests 是不同基線，不冒稱本輪重新驗證所有既有測試。

## 原版 Client 六欄 I/O 交付

|trigger|Client sends|Client receives|Client reaction / confirmed boundary|evidence|unknown|
|---|---|---|---|---|---|
|0x55709E / 0x557A5F 攻擊候選，通過本地狀態/timer|C13 BEu32 opaque target|可能 S13/S08/S5F（**非已證必然順序**）|C13 enqueue 表示意圖，不代表命中、扣血、死亡或任務目標|A025 初輪、A009 native producer|UI 滑鼠/鍵盤完整觸發、Server 距離/目標/冷卻|
|0x402034..0x402052 開始技能候選|C4D BEu16 selected spell|S52 BEu32+u8、S48 BEu32 為可能的獨立 Server 投影|有 C4D producer 和本地 action；u8 result/status enum 未解|A010|合法技能列表、技能效果/CD/耗魔|
|C56 writer 0x571800 的已證封包|C56 u8 opaque parameter|可能 S52|native 直接 ctor call 0x57185C 是 copy factory，未由此證明真 UI sender 或與 C4D 必然序列|A010/A025/新增 native 指令窗|C56 到 UI 的 producer、stage 與 value 來源|
|戰鬥多型互動 (C3D writer)|C3D u8 subtype 0..15 + branch payload|S3D 是不同的 incoming selector|native jump 16/16 已對照；未知用途不能變成傷害或 quest 進度|本次 C3D table|每種 subtype 的玩法與官方 Server 授權|
|Server 投影物件傷害/死亡|沒有因收此包自動送攻擊的證據|S13（效果）、S08（狀態）、S5F（死亡）|S5F 不是 S1E，也不是 S0E RemoveObjects；不能當 Quest kill ACK|A009/A004|何時/何順序/怪物動畫、真正 Server hit/kill|
|Server 派送腳本與對話|C6C(1) 是 ScriptReply，C6C(2/4) 是關閉|S44(1,0) 腳本啟動|NPC 對話/關閉不等於擊殺或教程完成|A012/A026|原版教學是否必打怪、objective ID、獎勵與官方完成條件|

## C3D 原生 writer 16-way：確定的 decoded-body 欄位型別

原始 VA 0x570DE0 先寫 subtype 的 u8（local +0x18），0x570DEC cmp 0xF、0x570DF8 以 0x570F2C jump-table 選分支；下列全部指 **subtype 後** 的欄位，不含 opcode/frame/encryption。string8 指按編碼後位元組長度計數，沒有原版 Client GUI 證明必是特定 CP。

|subtype|jump destination VA|已證 body after subtype|
|---|---|---|
|0|0x570DFF|u8|
|1|0x570E0D|string8, string8, u8, BEu32|
|2|0x570E5F|string8（本地空文字替代指標分支）|
|3|0x570F2A|無額外寫入|
|4|0x570EB2|u8|
|5|0x570F0E|u8|
|6|0x570EC0|u8|
|7|0x570ECE|u8, u8|
|8|0x570F2A|無額外寫入|
|9|0x570EEE|u8, u8|
|10|0x570F0E|u8|
|11、12、13、14|0x570F2A|無額外寫入|
|15|0x570F1C|BEu32|

**判定：16/16 native writer 結構已可正確列出，不等於 16/16 全部能對外送或是成功戰鬥。** 尤其 subtype3/8/11..14 沒有額外欄位，不能直接被 Server 當成無條件獎勵/攻擊成功。

## S3D 原生 reader 16-way：安全可用子集與應拒絕的分支

原始 VA 0x57C890 讀 u8，0x57C8C5 cmp 0xF，0x57C8D1 讀 0x57CD98 jump-table。32 個跳轉指標均直接從原始 PE 所屬資料位址比對，不只假設 switch 連續。固定/可界定的 11 個 subtype 保留 decoded-body 檢查，支援負向截斷/多餘位元組拒絕：

|subtype|native reader VA|subtype 後的確定 decoded body|
|---|---|---|
|1、8、12|0x57CD73|無欄位|
|3|0x57CA00|string8 + BEu32 + u8 + 26×u8|
|4、5、6、10|0x57CA4C|u8|
|7|0x57CA5B|u8 + u8|
|11|0x57CB93|u8|
|15|0x57CD59|BEu32 + BEu32|

S3D 的 **0、2、9、13、14** 屬於複雜 variable-count / list、字串等 reader；雖已證其原生目的地分別為 0x57C8D8、0x57C95C、0x57CA74、0x57CBA2、0x57CC88，但尚不能把其中所有容器欄位、玩家 UI 語意/容量上限直接做成已核准的 Server emit API。新 codec 對上述五類 **fail-closed**。S3D 3 的固定26 bytes 是 reader 實際逐次 u8，不是官方物件陣列數量。

## 原生行為 vs Server designed 權威邊界

- 伺服器依已授權 World generation、actor+target 有效性、同 map instance、存活、相對範圍/LOS、資源/冷卻、spell allowlist 及 replay policy 確認 CombatResolved；任何 C13/C4D/C56/C3D 一律只是 Client 意圖。
- S13 是視覺效果、S08 是 HP 等狀態、S5F 是死亡通知；這三者不能單獨作為 Server QuestObjectiveCompleted。任務 objective 必須是由有明確來源的 verified quest mapping 指向權威 CombatResolved event，使用唯一事件鍵和原子 ledger/Outbox。A025 原有 SQLite synthetic model 能示範去重，**不是原 Server 內部表結構**。
- 共享同一地圖的多人怪物生命與死亡由單一 Server instance/ActorRegistry 管理；個別任務進度分開，拒絕其他角色重複計算或斷線後 replay。這是專案既有使用者決策/DEV 規劃，不是原版怪物獎勵演算法。
- 無已確認官方 tutorial objective mapping 時，合法攻擊也**不能**產生入學/教學完成、獎勵或出圖。Born 的紙張是引導不是殺怪任務；同時不能從 Born 的缺字推論官方教程不打怪。

## 重跑命令、CT 與 Gate

    python tools/a025_battle_variant_probe.py Asgard.exe
    python -m unittest discover -s tools -p 'test_a025_battle_variant_probe.py' -v
    python tools/a025_tutorial_combat_model.py
    objdump -d -M intel --start-address=0x570de0 --stop-address=0x570f2c Asgard.exe
    objdump -d -M intel --start-address=0x57c890 --stop-address=0x57cd98 Asgard.exe

- **CT-058**：C13/C4D/C56/S52/**S5F** 靜態 codec 與原生頁面/送收 GUI 尚分開；主線曾誤寫 S1E，須更正。
- **CT-059**：C3D 16 writer 分支、S3D 11 safe reader + 5 refused complex；本輪 native-static+synthetic offline 14/14 PASS，真 GUI/TCP/Server response replay **not-run**。
- **CT-060**：錯 target/map/generation/replay、未 verified objective 不增加進度；designed model tests 與原 Client 正式 objective、獎勵需分開。
- 歷史 A25 文字使用的 CT-051/052/053 是舊分支來源編號，**當前主線以 CT-058/059/060 為準**；不得覆寫主線 CT-051 其他任務。
- A25 本次 Client static **bounded handoff ready**；original-native-tutorial-combat-required=false? **否，應為 unknown**。native_tutorial_combat_requirement_proven=false、native_quest_progress_mapping_ready=false、native_combat_e2e_ready=false、native_client_validation=not-run，整個官方教程可玩性與公式不以此宣稱完成。

## 精確缺口 / 缺件

此次沒有新增有確切名稱、必須上傳的原件；Asgard.exe、Born.dat、Basic.dat 與 Map0/1/2.dat 均已提供。原始特定教學 Monster/NPC/Quest 定義與技能表的可證**實際檔名仍未知**，不能臆造。下階段所需是經遮罩的真實未修改 Windows Client World 遊玩 trace（C13/C4D/C56、S52/S13/S08/S5F、S3D、攻擊與技能 UI、S15/C35/S04、怪物與 NPC entity、首次任務出現／完成前後），再補 C56 producer xref、複雜 S3D handler/consumer，才能把 unknown 升級為 original-native-verifiable。
