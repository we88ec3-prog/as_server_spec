# A-024／roy2 — 原版 NPC／怪物「Client I/O」BIN-first 交付

- 原件：\`Asgard.exe\` PE32 SHA256 \`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145\`，ImageBase \`0x400000\`；\`Born.dat\` SHA256 \`992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98\`；Map0/1/2 三庫共 494 MAP。2026-10-31，既有分支／目錄 \`task_a/roy2\`。
- 範圍：A-024 / R-012,R-027,R-029。**Client 收到何種物件生成/移動/死亡/移除包，Client 如何解析，以及互動候選的傳送入口**。不把 Server NPC AI/重生計數當 A 任務完成門檻；不推論遠端 Server 原服策略。別將「分析已交付」與「新手教學已能跑」混淆。
- 證據分層：**observed-static**＝使用者原始 EXE 位址/組合語言；**observed-static-resource**＝原始 MAP/Born 結構；**synthetic-test**＝本機造包/epoch 模型；**inferred**＝類別名所暗示功能；**unknown**＝原服內容/行為/實測。

## 一、RTTI → vtable → opcode constructor → reader

調查方法：在 PE \`.data\` 取 MSVC RTTI \`TypeDescriptor\`，反查 \`.rdata\` COL 與 parser vtable，再定位 \`0x578730\` S2C base ctor 的 \`push opcode\`，確認不是單純讀 cpp 名字。reader \`0x45AEB0=BE u32\`, \`0x45ADE0=BE u16\`, \`0x45ADB0=u8\`。以下是**decoded body**，不含 AA frame/opcode/ordinal/XOR。

|包 / 原生類別|原生依據|已證 body|不能外推|
|---|---|---|---|
|S07 \`SDrawObjectsPacket\`|type name 0x669CBC；ctor \`0x57E310\` push 0x07；reader \`0x57E3E0\`|先 \`count:u16 BE\`，每列先取 \`u16,u16,u8,u32,u16\`，type 1..14 的後續走條件分支，\`0x57E45A..0x57E5CD\`；內部分配 \`0x228\` bytes/record|0x228 是 **Client local struct** 非 wire 固定長度；type→NPC/Monster/Static 的逐項語意未證，不能假裝完整非空 S07 可安全編碼|
|S5F \`SDieObjectsPacket\`|type 0x669C9C；ctor \`0x57E1B0\` push 0x5F；reader \`0x57E260\`|一個 \`u32 BE\`，寫 local +0x18|這個值與 entity ID 的對應要靠 handler 證實，不能當官方死亡/掉落公式|
|S0C \`SMoveObjectPacket\`|type 0x669E98；ctor \`0x5833A0\` push 0x0C；reader \`0x583450\`|BE \`u32,u16,u16,u8,u8\`，至 packet local +0x21|座標/方向欄位名仍是**候選**，不做原版行走速度/碰撞權威宣稱|
|S64 \`SMovePathPacket\`|type 0x669EB8；ctor \`0x583530\` push 0x64；reader \`0x5835E0\`|BE \`u32,u16,u16,u8,count:u8,count×u8 path_bytes,u16,u16,u8\`|path 存本機 +0x23；後續欄始 +0x2E，留 **11 byte**；EXE 未見此迴圈對 count 的顯式 cap，對 native 發包須保守拒絕 count>11（**designed safety gate**）|
|S0E \`SRemoveObjectsPacket\`|type 0x66A044；ctor \`0x585E60\` push 0x0E；reader \`0x585F10\`|一個 \`u32 BE\` 至 local +0x18|不能因 packet 名就推論其死亡/切圖/距離/斷線原因|
|S33 \`SPutHumanObjectPacket\`|type 0x669F78；ctor \`0x5854D0\` push 0x33|已有 [appearance](../../04-analysis-integration/appearance.md) / A-004 的玩家可見/外觀路徑|**這是 Human**，不能拿 S33 當 NPC/Monster 的唯一生成包|
|C43 \`CObjectInfoRequestPacket\` 候選|type 0x669688；ctor \`0x574500\` push 0x43|Client 確實存在 object-info 請求 class；其 serializer/點擊 UI→收包回應尚待逐鏈確認|**不能因名稱直接把 C43 認定與女招募員對話**|

**容易混淆的結果**：opcode **0x07 是 DrawObjects 而不是 DieObjects**；**0x5F 才是 DieObjects**；**0x0E 是 RemoveObjects 而不是 0x3B**；**0x0C 是 MoveObject，0x64 是 MovePath**。這些由 ctor 實際 push 與 RTTI COL/vtable 比對後確定。若只依檔名排列會將相鄰函式的 opcode 錯配。

## 二、Client 物件生命週期／Server 交接契約

Client 的封包類別至少提供：**加入/顯示** S07、**動作/路徑** S0C/S64、**死亡事件** S5F、**移除** S0E；需依原版 parser 與 object registry 進一步確認 S07 type 分支和 remove/die 實際 state。確切 npc/monster type 數字、第一隻怪的 monster_id、招募員 entity_id、位置和移動 time-unit 仍 unknown。

最小**designed** Server 安全模型（與原版行為分開）：
1. 只在角色世界 session 已綁定、同 map instance 和 map epoch 完成載入後，投影同地圖可見 NPC/怪物；重複 S07 同 object key 不產生雙影。
2. 使用 \`EntityKey(map_instance,spawn_generation,entity_runtime_id)\`；死亡不是必然立即 remove，respawn 是新 generation，而非 reuse 舊 entity ID 造成幽靈物件。
3. Client 互動/攻擊僅是請求；Server 檢查角色/目標、距離與視野、冷卻、權限及技能資料是否已有實證。**沒有原服 NPC AI 速度、移動間隔或掉落表時絕不以設計值冒充原版**。
4. 斷線、切圖、重登撤銷舊 map epoch 的未完成廣播/AI tick/outbox；舊回包不准重現已離圖物件。支援可重播的 spawn→move→die→remove 鏈，並測延遲、截斷、重送、未知 type/op、過量路徑。

## 三、原始資源與依賴檢查：目前不存在可驗證的教學物件清單

- 原件 \`Map0.dat\`／\`Map1.dat\`／\`Map2.dat\` 解析為 288+184+22=494 張 MAP；可觀察 tile 與 7/8/16-byte 尾段，但這些 record 的真正 NPC/Monster spawn 語意**沒有 BIN＋內容交叉引用**。不能從任意 record 自動提取官方 NPC。
- \`Born.dat\` 只提供 PaperDialog 導覽去座標 \`(31,29)\` 找女性招募員；**不是玩家出生地、也不是已確認的 NPC spawn 位置**。A-023 中 \`nNewJoin01\` merchant/join script 只是候選，不是原版 entity/map binding。
- Client 可見資源 selector \`World%02d.dat\`、\`@Monster%02d.dat\`（後者有前置 \`@\` 字面字元）；目前未有這些**實際原始檔**或官方同版 manifest，無法確認其成員是否含 static/map sprite/NPC 清單；不可把檔名當作已知 spawn 表。
- 缺交：**指定官方教學 map_id、每隻 NPC/怪 spawn kind/id/x/y/facing、entity id 對 C43 的實際點擊事件、S07 type 分支到 registry 的完整映射、原版 AI 策略/時序與原生 client trace**。這屬 A-004/A-011/A-022/A-023 後續核心 unknown，**不是等新 Server 做好才能研究**。
- 可追加的**具體檔名**：合法持有的 \`World00.dat\`、\`@Monster00.dat\` 是已證檔名模板推導的**範例**（不保證存在），可先提供單一樣本/檔案索引，不需要整套圖片。優先證據應是原服測試帳號的去識別 packet trace 或官方配置表；不要以不相關的巨量圖像替代。

## 四、重現、下游驗收與狀態

\`\`\`sh
sha256sum Asgard.exe Born.dat Map0.dat Map1.dat Map2.dat
objdump -d -M intel --start-address=0x57e310 --stop-address=0x57e5cd Asgard.exe
objdump -d -M intel --start-address=0x57e1b0 --stop-address=0x57e270 Asgard.exe
objdump -d -M intel --start-address=0x5833a0 --stop-address=0x583487 Asgard.exe
objdump -d -M intel --start-address=0x583530 --stop-address=0x583657 Asgard.exe
objdump -d -M intel --start-address=0x585e60 --stop-address=0x585f20 Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a024_npc_codec.py'
\`\`\`

6 項 synthetic unit tests **PASS**（decoded fixed S5F/S0E/S0C、S64 path、S07 零列、epoch/replay negative cases），不包含遊戲資料或原版 E2E。詳見 \`a024_npc_codec.py\` 與測試檔。對 S07 **非空物件**和未證 native handler，驗證器刻意 fail closed。

**A-024 結論**：已交付有據的 Client 收包、欄位型別和初步狀態模型，\`status=integrated\`，\`handoff_status=partial\`（真正教學 NPC/map 綁定和非空 S07 對應仍不完整），\`native_client_validation=not-run\`。不是原生整段教學成功，也不應自稱完整生成/AI/重生的原服還原。CT-021/022/034 須在 Client/資源/內容條件可用後補測。
