# A-024／roy2 — 原版 NPC／怪物「Client I/O」BIN-first 交付

> **最新版裁定（2026-10-31）**：第六節更新後，S07 非空 kind1..14 與 S34 subtype11 已依原始 EXE 補齊 wire schema；前四節保留為早期研究歷程，舊的「非空 S07 未解／partial」不得覆蓋第六節結論。靜態 Client 收包交付 `integrated / ready`，Native Client E2E 尚未執行。

- 原件：`Asgard.exe` PE32 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，ImageBase `0x400000`；`Born.dat` SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`；Map0/1/2 三庫共 494 MAP。2026-10-31，既有分支／目錄 `task_a/roy2`。
- 範圍：A-024 / R-012,R-027,R-029。**Client 收到何種物件生成/移動/死亡/移除包，Client 如何解析，以及互動候選的傳送入口**。不把 Server NPC AI/重生計數當 A 任務完成門檻；不推論遠端 Server 原服策略。別將「分析已交付」與「新手教學已能跑」混淆。
- 證據分層：**observed-static**＝使用者原始 EXE 位址/組合語言；**observed-static-resource**＝原始 MAP/Born 結構；**synthetic-test**＝本機造包/epoch 模型；**inferred**＝類別名所暗示功能；**unknown**＝原服內容/行為/實測。

## 一、RTTI → vtable → opcode constructor → reader

調查方法：在 PE `.data` 取 MSVC RTTI `TypeDescriptor`，反查 `.rdata` COL 與 parser vtable，再定位 `0x578730` S2C base ctor 的 `push opcode`，確認不是單純讀 cpp 名字。reader `0x45AEB0=BE u32`, `0x45ADE0=BE u16`, `0x45ADB0=u8`。以下是**decoded body**，不含 AA frame/opcode/ordinal/XOR。

|包 / 原生類別|原生依據|已證 body|不能外推|
|---|---|---|---|
|S07 `SDrawObjectsPacket`|type name 0x669CBC；ctor `0x57E310` push 0x07；reader `0x57E3E0`|先 `count:u16 BE`，每列先取 `u16,u16,u8,u32,u16`，type 1..14 的後續走條件分支，`0x57E45A..0x57E5CD`；內部分配 `0x228` bytes/record|0x228 是 **Client local struct** 非 wire 固定長度；已於第六節補證 type1..14 非空 row 全部 decoded body；但 kind→NPC/Monster/Static 的逐項語意仍未證|
|S5F `SDieObjectsPacket`|type 0x669C9C；ctor `0x57E1B0` push 0x5F；reader `0x57E260`|一個 `u32 BE`，寫 local +0x18|這個值與 entity ID 的對應要靠 handler 證實，不能當官方死亡/掉落公式|
|S0C `SMoveObjectPacket`|type 0x669E98；ctor `0x5833A0` push 0x0C；reader `0x583450`|BE `u32,u16,u16,u8,u8`，至 packet local +0x21|座標/方向欄位名仍是**候選**，不做原版行走速度/碰撞權威宣稱|
|S64 `SMovePathPacket`|type 0x669EB8；ctor `0x583530` push 0x64；reader `0x5835E0`|BE `u32,u16,u16,u8,count:u8,count×u8 path_bytes,u16,u16,u8`|path 存本機 +0x23；後續欄始 +0x2E，留 **11 byte**；EXE 未見此迴圈對 count 的顯式 cap，對 native 發包須保守拒絕 count>11（**designed safety gate**）|
|S0E `SRemoveObjectsPacket`|type 0x66A044；ctor `0x585E60` push 0x0E；reader `0x585F10`|一個 `u32 BE` 至 local +0x18|不能因 packet 名就推論其死亡/切圖/距離/斷線原因|
|S33 `SPutHumanObjectPacket`|type 0x669F78；ctor `0x5854D0` push 0x33|已有 [appearance](../../04-analysis-integration/appearance.md) / A-004 的玩家可見/外觀路徑|**這是 Human**，不能拿 S33 當 NPC/Monster 的唯一生成包|
|C43 `CObjectInfoRequestPacket` 候選|type 0x669688；ctor `0x574500` push 0x43|Client 確實存在 object-info 請求 class；其 serializer/點擊 UI→收包回應尚待逐鏈確認|**不能因名稱直接把 C43 認定與女招募員對話**|

**容易混淆的結果**：opcode **0x07 是 DrawObjects 而不是 DieObjects**；**0x5F 才是 DieObjects**；**0x0E 是 RemoveObjects 而不是 0x3B**；**0x0C 是 MoveObject，0x64 是 MovePath**。這些由 ctor 實際 push 與 RTTI COL/vtable 比對後確定。若只依檔名排列會將相鄰函式的 opcode 錯配。

## 二、Client 物件生命週期／Server 交接契約

Client 的封包類別至少提供：**加入/顯示** S07、**動作/路徑** S0C/S64、**死亡事件** S5F、**移除** S0E；需依原版 parser 與 object registry 進一步確認 S07 type 分支和 remove/die 實際 state。確切 npc/monster type 數字、第一隻怪的 monster_id、招募員 entity_id、位置和移動 time-unit 仍 unknown。

最小**designed** Server 安全模型（與原版行為分開）：
1. 只在角色世界 session 已綁定、同 map instance 和 map epoch 完成載入後，投影同地圖可見 NPC/怪物；重複 S07 同 object key 不產生雙影。
2. 使用 `EntityKey(map_instance,spawn_generation,entity_runtime_id)`；死亡不是必然立即 remove，respawn 是新 generation，而非 reuse 舊 entity ID 造成幽靈物件。
3. Client 互動/攻擊僅是請求；Server 檢查角色/目標、距離與視野、冷卻、權限及技能資料是否已有實證。**沒有原服 NPC AI 速度、移動間隔或掉落表時絕不以設計值冒充原版**。
4. 斷線、切圖、重登撤銷舊 map epoch 的未完成廣播/AI tick/outbox；舊回包不准重現已離圖物件。支援可重播的 spawn→move→die→remove 鏈，並測延遲、截斷、重送、未知 type/op、過量路徑。

## 三、原始資源與依賴檢查：目前不存在可驗證的教學物件清單

- 原件 `Map0.dat`／`Map1.dat`／`Map2.dat` 解析為 288+184+22=494 張 MAP；可觀察 tile 與 7/8/16-byte 尾段，但這些 record 的真正 NPC/Monster spawn 語意**沒有 BIN＋內容交叉引用**。不能從任意 record 自動提取官方 NPC。
- `Born.dat` 只提供 PaperDialog 導覽去座標 `(31,29)` 找女性招募員；**不是玩家出生地、也不是已確認的 NPC spawn 位置**。A-023 中 `nNewJoin01` merchant/join script 只是候選，不是原版 entity/map binding。
- Client 可見資源 selector `World%02d.dat`、`@Monster%02d.dat`（後者有前置 `@` 字面字元）；目前未有這些**實際原始檔**或官方同版 manifest，無法確認其成員是否含 static/map sprite/NPC 清單；不可把檔名當作已知 spawn 表。
- 缺交：**指定官方教學 map_id、每隻 NPC/怪 spawn kind/id/x/y/facing、entity id 對 C43 的實際點擊事件、S07 type 分支到 registry 的完整映射、原版 AI 策略/時序與原生 client trace**。這屬 A-004/A-011/A-022/A-023 後續核心 unknown，**不是等新 Server 做好才能研究**。
- 可追加的**具體檔名**：合法持有的 `World00.dat`、`@Monster00.dat` 是已證檔名模板推導的**範例**（不保證存在），可先提供單一樣本/檔案索引，不需要整套圖片。優先證據應是原服測試帳號的去識別 packet trace 或官方配置表；不要以不相關的巨量圖像替代。

## 四、重現、下游驗收與狀態

```sh
sha256sum Asgard.exe Born.dat Map0.dat Map1.dat Map2.dat
objdump -d -M intel --start-address=0x57e310 --stop-address=0x57e5cd Asgard.exe
objdump -d -M intel --start-address=0x57e1b0 --stop-address=0x57e270 Asgard.exe
objdump -d -M intel --start-address=0x5833a0 --stop-address=0x583487 Asgard.exe
objdump -d -M intel --start-address=0x583530 --stop-address=0x583657 Asgard.exe
objdump -d -M intel --start-address=0x585e60 --stop-address=0x585f20 Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a024_npc_codec.py'
```

6 項 synthetic unit tests **PASS**（decoded fixed S5F/S0E/S0C、S64 path、S07 零列、epoch/replay negative cases），不包含遊戲資料或原版 E2E。詳見 `a024_npc_codec.py` 與測試檔。早期工具 `a024_npc_codec.py` 對非空 S07 fail closed；新工具 `a024_object_packets.py` 已解析 kind1..14 非空記錄，未知 UI handler 仍保留。

**A-024 結論**：已交付有據的 Client 收包、欄位型別和初步狀態模型，`status=integrated`，`handoff_status=ready`（目前 Client 收包靜態欄位已交付；教學 NPC/map 綁定及 Native renderer 仍未驗），`native_client_validation=not-run`。不是原生整段教學成功，也不應自稱完整生成/AI/重生的原服還原。CT-021/022/034 須在 Client/資源/內容條件可用後補測。


## 五、Client 主動動作補查：攻擊 C13 與物件資訊 C43

依 `A-XX Client I/O` 契約額外追原件 C2S native constructor + serializer，不只列 S2C：

|玩家操作候選 / C2S|Client 原生來源|已證 decoded body|觸發/反應限制|
|---|---|---|---|
|攻擊 `C13`（`CAttackPacket`）|ctor `0x570A10` push 0x13；serializer `0x570AC0` 讀 object+0x18 並呼叫 `0x45AC40`；native producer `0x55709E`、`0x557A5F`|**BE u32** 一欄|遊戲中的攻擊來源確有可送包路徑，但具體 UI 按鍵、target 取得方式及 Server 命中拒絕/傷害效果尚無 E2E|
|物件資訊請求 `C43`（`CObjectInfoRequestPacket`）|ctor `0x574500` push 0x43；serializer `0x5745B0`：`0x45AB00`、`0x45AC40`、`0x45AB00`；多個呼叫點含 `0x479DC7`、`0x4A23F8`|**u8、BE u32、u8**|這是**物件資訊請求**類別。無法由名字/存在性證明女性招募員 NPC 點擊必送 C43；需要 Client UI→handler cross-ref 及合法 trace|

這是本 A 已交付的 **Client sends**；`S07/S0C/S64/S5F/S0E` 是 **Client receives**；Client reaction 的最小可證只有將欄位讀入 Object/Path/Die/Remove packet，真物件渲染 registry 的所有分支還未逐一確認。Server 回覆成功/錯誤的具體 native codec，必須等確定 UI producer 與 parser 後再填。合成測試已補上 C13/C43 編碼檢查，共 **7 tests PASS**，不代表 native Client E2E。


## 六、A-024 追加完成：實際收包清單與 S07 非空 14-type 靜態解析（2026-10-31）

這次直接使用**同一原件** `Asgard.exe`（SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`）重新核查 `0x57E3E0..0x57E5F6`、五個額外 S2C native 類別與其 RTTI→COL→vtable→ctor/reader。下面是 **decoded S→C body**（不含 AA framing/ordinal/XOR）。此次補齊的是 Client 接收協定，不把原服 AI 或教程 spawn policy 當成 Client 靜態證據。

### 6.1 生成／移動／資訊更新／消失收包矩陣

|動作分類|封包／Client 類別|實際原生 ctor → reader|已證明 decoded body|適用範圍／不可超推|
|---|---|---|---|---|
|生成／初始放入地圖|**S07 DrawObjects**|0x57E310→0x57E3E0|BE u16 count；每項 11-byte 起始欄＋type 1..14 的完整分支列於 6.2|這是原版 Client 的非 Human 物件生成候選；沒有證明每個 type 分別是 NPC/怪物/道具。|
|單次移動／位置更新|**S0C MoveObject**|0x5833A0→0x583450|BE u32、BE u16、BE u16、u8、u8（10B）|u32 為 object key 候選；兩個 u16 位置欄為候選，實際 callback/單位未驗。|
|路徑移動／連續動作|**S64 MovePath**|0x583530→0x5835E0|BE u32,u16,u16,u8,count:u8,count×u8,BE u16,u16,u8；共 15+count bytes|本地 path 空間 11 bytes，超出 11 的拒絕是 **designed** 防記憶體覆寫護欄，不是原服已證合法上限。|
|物件細節狀態更新／顯示資訊|**S34 ObjectInfoReply**|0x5844B0（push 0x34）→0x584540|u8 kind、BE u32 key 候選、u8 flags；kind 6 多 10B，kind 11 視 flags 而定（見 6.3）|類別存在但尚未追到「具體哪個 NPC 顯示」的 GUI handler，不把它當無條件 NPC 屬性更新。|
|物件資訊提示|**S3C ShowObjectInfo**|0x586A20（push 0x3C）→0x586AD0|BE u32、u8、u8、u8（7B）|三個 byte 的人類可讀意義與 UI renderer 未完全查證。|
|新增動作／畫面互動狀態候選|**S62 AddAction**|0x578F70（push 0x62）→0x579020|u8、u8、BE u16、3×u8、4×string8、u8、BE u16、u8|Action 不一定是怪物 AI；其四段文字是 CP950 string8 bytes，不是四個固定 wchar。|
|移除動作／互動狀態候選|**S63 RemoveAction**|0x5858A0（push 0x63）→0x585950|u8、u8（2B）|不等同物件消失；本地動作 ID 角色與 object 關聯未知。|
|視覺效果／狀態效果候選|**S29 Effect**|0x57E6A0（push 0x29）→0x57E750|BE u32×2、BE u16×2、u8（13B）|不能把 effect 當 HP、AI state 或硬性 spawn。傷害另有 A-009 的 S13。|
|死亡事件|**S5F DieObjects**|0x57E1B0→0x57E260|BE u32（4B）|不是立即移除；死亡狀態的 object registry callback 尚需 E2E。|
|物件移除／離視野|**S0E RemoveObjects**|0x585E60→0x585F10|BE u32（4B）|可供物件退場投影，具體事件原因（死亡、切圖、AOI、斷線）未知。|

**玩家與 NPC 分流**：`S33 PutHuman`、`S06 MoveHumanAck`、`S11 ChangeDirection` 依 A-004 是 **Human / other-player** 資料鏈，不應拿來取代 S07/S0C/S64。Client 發出的 `C13 Attack`（BE u32）與 `C43 ObjectInfoRequest`（u8、BE u32、u8）不是上述 Server→Client 生成／更新包；C43 未證為特定招募員點擊。

### 6.2 S07 每個非空 row 原生 type 分派：先前未知部分已解

原件 `0x57E3E5` 先讀 **count:BE u16**；`0x57E3F1` 按 count×**0x228** 分配**本地記錄**；迴圈 `0x57E428..0x57E456` 逐列讀相同 **11B 前綴**：

```text
BE u16 field_a; BE u16 field_b; u8 kind;
BE u32 opaque_object_key; BE u16 field_c;
```

`0x57E45A` 對 kind 減 1，限 1..14；依 byte jump-index table `0x57E5E8` 與 dword jump-target table `0x57E5D4`：

|kind|native jump target|**prefix 之後**的 decoded body|每列總長度|
|---|---|---|---|
|**1,2,4**|0x57E476|5×u8、BE u16、BE u32 flags；bit0 加3×u8、bit1 加u8、bit4 加 BE u16；最後 string8（u8 編碼長度＋長度個原始 CP950 bytes）|23＋文字 bytes＋(bit0?3:0)＋(bit1?1:0)＋(bit4?2:0)|
|**3**|0x57E538|5×u8＋string8|17＋文字 bytes|
|**5..12**|0x57E5B1|**沒有**其他 wire 欄位|11|
|**13**|0x57E57E|string8|12＋文字 bytes|
|**14**|0x57E592|2×u8＋BE u16|15|

**逐欄對應**：kind1/2/4 的 5×u8 到 native row +0x14..0x18（+0x17 另以 0xFF 本地預設值寫入）、u16 到 +0x222、flags 到 +0x10；bit0 的3個 byte 到 +0x21A..+0x21C、bit1 到 +0x224、bit4 的 u16 到 +0x21E（未設 bit4 則填0）、字串放 +0x1A。kind3 五 byte 到 +0x11..+0x14 及字串 +0x16；kind13 只有 +0x10 的字串；kind14 的2 byte及 u16 放 +0x10,+0x11,+0x12。**這些都是 local object offset，不是 wire offset**。

**實務重點**：kind 5–12 不需要一張圖就發一個固定 0x228 大小的 blob；那是 Client 在記憶體使用的 stride。可依 above schema 生成真正的 decoded S07 多筆資料，但 type→NPC/Monster 分類、sprite 載入、地圖與 id 綁定尚未證明，故不能隨意把 type1 聲稱是怪物。原版對 kind 在 1..14 外落 default，不額外讀欄位；安全 codec 對此類型採 **designed fail closed**，避免未定位類別誤顯示。

### 6.3 S34 / S3C / S62 / S63 / S29 資訊與動作 packet 補證

- **S34** reader `0x584540`：通用前綴 **u8 subtype, BE u32, u8 flags（6 bytes）**。subtype **6**（`0x58492A`）另外依序讀 **BE u16、u8、BE u32、u8、u8、u8（10B）**，總共16B。subtype **11**（`0x584571`）根據 flags：bit0 string8+2u8+u32；bit1 BE u16 count 及 count bytes raw block（`0x45BAB0`）；bit2 count u8，依每筆 u8,u8,string8；bit3 count u8，依每筆 u8,u16,三個 u8,u8,string8；bit4 count u8，依每筆 2×string8+2u8+string8；bit6 count u8，依每筆 u8；其資料在 Client 以 0x202/0x40E/0x602 等 stride 存於本地，不可當 wire row size。**subtype11 的全部六種 flags 資料組合已加入安全 decoded-body codec**（`a024_object_packets.py`），但各組的 GUI 顯示語意與實際用途仍需 Native CT。
- **S3C** 0x586AD0 依序 0x45AEB0（BE u32）＋3 次 0x45ADB0（u8），完整為7B；不是 S34。
- **S62** 0x579020 先兩個 u8、一個 BE u16、三個 u8，接續四次 `0x45B7A0` 解析 string8，再 u8、BE u16、u8；`S63` 0x585950 只有兩個 u8。這是「動作選項」資料鏈，不代表怪物每一步移動都必發 S62。
- **S29** 0x57E750 先2×`0x45AEB0`、2×`0x45ADE0`、1×`0x45ADB0`，後在本機條件將部分 u32 拆半保存；**不額外讀 wire**。因此 S29 的固定13B不等於任何當前 HP 修改。
- **持續狀態**：原版另有 `SAddLastingSpellPacket`、`SRemoveLastingSpellPacket`（A-008/010），但目前未證定向 NPC/怪物的完整該兩包 schema；不把它們當本輪完整怪物 AI 狀態更新。

### 6.4 行為鏈與 DEV 可交付範圍

|先後（範例，不是原服已證發送順序）|Server 投影→Client|Client 已證／未知|
|---|---|---|
|進入地圖／AOI 出現|S07（非空種別 row），可見 Human 另走 S33|Native reader 有完整 type1..14 body，**物件 registry/renderer 完整 callback 未追通**|
|目標移動|S0C 單次 / S64 路徑|原生 parser 有序讀取；移動時距/速度/朝向狀態欄的精確單位需 Native CT|
|物件顯示資訊或動作改變|S34／S3C／S62／S63／S29（依業務功能選擇，**不是全部必要**）|各原生 parser 存在；哪個 UI 或 object type 消費，尚待 callback XREF|
|受擊與死亡|傷害效果 S13 (A-009)、死亡 S5F|S5F 只有 BE u32；原服如何認定死亡屬 Server policy|
|物件離開|S0E|單一 BE u32；是否即時從 Client object registry 删除尚需 runtime trace|

Server 若要避免 bug，需依**自行設計**的 `(map instance, entity id, generation, epoch)` 做 id 分配、可見集合、去重和斷線 fencing；需要驗證 target 不跨圖、死亡不必然 remove、移動不覆蓋被移除物件。**此為 designed，不可宣稱原服有同樣 epoch 機制**。Client 已證只處理 wire，不決定怪物 AI、原服 spawn 位置／數量、攻擊冷卻或掉落。

### 6.5 交付與驗證

- [metadata-only 原件驗證](a024_object_native_probe.py)：SHA 鎖定，**20 個 native instruction anchors、14 個 kind jump-table entry、6 個 RTTI** 均已從原始 Asgard.exe 獨立核對通過。
- [非空 S07 與資訊封包 decoder](a024_object_packets.py)，包含 kind1..14、S3C/S34 subtype6＋subtype11 六組動態欄位、S62/S63/S29；[合成測試](test_a024_object_packets.py) 包含所有 kind、條件欄、CP950 原始 bytes、count、截斷、未知 subtype，與早先的 [NPC 測試](test_a024_npc_codec.py) 分離。
- 既有 S0C/S64/S5F/S0E 由 `a024_npc_codec.py` 檢查，不使用新 opcode 冒充舊物件更新。**Native Client 端對端 GUI 未執行；不能據此宣稱所有物件圖片／動畫／AI 已正常運行。**
- **已可交 DEV**：S07 非空 type1..14 decoded body、安全序列、已證單步／路徑／死亡／移除與補充資訊／動作封包，附 CT-065 靜態／合成、CT-066 Native 客戶端鏈路驗收。
- **剩餘 unknown**：各 type 真正 NPC/Monster/非生命物件分類；object key 與 renderer/registry 的消費端 XREF；S34 subtype11 各欄的原生 GUI 顯示語意；NPC 具體貼圖/定位/動畫與第一次教學實際 NPC 設定；原 Client native E2E。故 A-024 可標**靜態 Client 收包清單已完成**，原生 GUI、教程內容與 Server 原服 AI 仍列獨立驗收，不可標已全解。
- **缺件**：完成此收包結構研究**無需新增檔案**。若要補具體 NPC/怪物內容與圖像綁定，原件可查的檔名模板是 `World%02d.dat`、`@Monster%02d.dat`，欲進一步對照可提供**實際存在**的 `World00.dat`、`@Monster00.dat` 範例（不保證原版真的有這兩個數字）；不要再要求已有的 Asgard.exe / Map0..2 / Born.dat。


### 6.6 S34 subtype11 六組資料完全解碼與 CI 結果

新增 decoder 已依 `0x58457D..0x584913` native parser 的 **flags 0x01/0x02/0x04/0x08/0x10/0x40** 順序執行：
- bit0：string8、u8×2、BE u32；
- bit1：BE u16 count、count 個 raw bytes；
- bit2：u8 count、每項 `u8,u8,string8`；
- bit3：u8 count、每項 `u8,BE u16,u8×4,string8`；
- bit4：u8 count、每項 `string8,string8,u8×2,string8`；
- bit6：u8 count、count 個 u8。

可空組、混合 flags、255 元素、截斷與尾段過量均由 `test_a024_object_packets.py` 檢查。**GitHub Actions 2026-10-31 run [41185085803](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41185085803) 成功**：phase-gates PASS、**19 個新增 S07/S34/S3C/S62/S63/S29 測試 PASS + 7 個舊 NPC 測試 PASS**。另已對本地原始 EXE 直接核對 **20 個 native instruction anchors、14 個 S07 type 跳表、6 個 RTTI PASS**，這是原件靜態而非真實封包 E2E。

**A-024 最終靜態交付**：`integrated/ready` 代表「Client 收到哪些包以及能安全解碼其已追查 S2C body」已解，**不代表** Client 真的載入哪一種怪物圖、NPC 點擊事件一定對應 C43、原版怪物 AI 與資料表還原，或 native Client CT-066 已通過。缺少新增必需檔案：無。
