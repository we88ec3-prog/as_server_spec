# A-011／roy2 — NPC／怪物資源 ID、點擊互動、外觀／動畫原版 Client 靜態交接

- 日期：2026-10-31；既有分支 `task_a/roy2`，**不新建分支**。
- Scope：A-011 / SYS-NPC / R-012。任務要求由資源、可見物件及互動 UI 追物件類別、外觀、動畫與掉落，交付生成／移動／消失／互動對話最小可驗收鏈。原始 Server 的 NPC AI、掉落率與 spawn 政策不以猜測代替。
- 原始檔 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；ImageBase `0x400000`。已有 `Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat`。本輪**未提供 MonsterNN.dat / WorldNN.dat 實體檔**，因此不聲稱完成素材內各 NPC/sprite 動作的視覺驗證。
- 分類：**observed-static**＝上述 EXE 指令、MSVC RTTI、vtable、class constructor；**synthetic-tested**＝自造數值/封包；**inferred**＝類別功能及用途推論；**unknown**＝不存在的資源/原生 GUI/原服實際策略。

## 1. 資源 ID 真正映射：內部 Resource Library ≠ Sprite ID ≠ World EntityId

原生資源註冊器 `0x404331..0x4043AF`（遞增整數索引、`0x5B3761` 格式化檔名、`0x440720` 注冊），實際登錄：

|範圍／數量|模板（實際傳入）|已證 VA|實際例子|
|---|---|---|---|
|Client Library ID `0x1B58..0x1B6F` = **7000..7023**，24 筆|`World%02d.dat`|0x404331, 0x40434B, 0x404369|`World00.dat`…`World23.dat`（檔名可推導，**未確認提供的資源包有實檔**）|
|Client Library ID `0x1F40..0x1F6A` = **8000..8042**，43 筆|`Monster%02d.dat`|0x404371, 0x40438B, 0x4043A9|`Monster00.dat`…`Monster42.dat`|

**A-024 名稱更正**：寬字常值 `0x5F1D3A` 確實包含字面 `@Monster%02d.dat`，但 `0x40438B` 的 `push 0x5F1D3C` **跳過第一個 UTF-16 字元 @**，實際查找檔名沒有 @。請勿請使用者提供不存在證據的 `@Monster00.dat`。

**更重要：MonsterImageLib 的單張圖片 ID→資源庫 ID+檔內槽位算法已取得**（不是根據檔名推測）。原生 `0x4D7530` 將 16-bit 圖像 ID 減 `0x4000`，透過 magic multiply `0x66666667` 計算除以10之 quotient，再加 `0x1F40`；`0x4D7560` 對相同原始 ID 算余數：

```text
delta = client_image_id - 0x4000
client_resource_library_id = 8000 + floor(delta / 10)
local_image_slot = delta % 10
archive_name = "Monster%02d.dat" % floor(delta / 10)
```

只對 **目前 43 個已註冊 Monster Library** 的推定安全整數區間 `0x4000..0x41AD` 使用：這是 **designed bounded guard**，不是所有原服 sprite 合法範圍的宣告。

|image ID|resource library|asset filename|in-archive slot|
|---|---:|---|---:|
|`0x4000`|8000|`Monster00.dat`|0|
|`0x4009`|8000|`Monster00.dat`|9|
|`0x400A`|8001|`Monster01.dat`|0|
|`0x41AD`|8042|`Monster42.dat`|9|

**區分三層**：Client image ID（0x4000 基底）不是 Server EntityId；Library 8000 也不是怪物種類 8000；S07 row 的 object opaque BE u32（packet local+0x08）是**場景物件/實例識別值候選**，不是上述素材庫 ID。沒有實際資源索引表時不能從已知 Monster00 檔名給出「招募員／某一怪物就是 imageId 0x4000」。

## 2. 生成 packet 到 MonsterObject 與外觀載入

基於 A-024 已證 **S07 DrawObjects（opcode 0x07）** `0x57E310` ctor、`0x57E3E0` reader、`0x57E5D4/0x57E5E8` 14 type jump table：在原生**收包之後** `0x4F17C0..0x4F1C4A`，並非單純 RTTI 類名，實際證實：

|S07 row kind|world-object creation path|已證特徵／界線|
|---|---|---|
|**1**|`0x4F1A8B` test kind==1 → `0x4F1AEB` call **MonsterObject ctor `0x4D6FA0`**|傳入 local row `+0,+2` 的 u16、`+8` u32 opaque key、`+0x18` byte、`+0x222` u16 等。將物件加入 world registry 的呼叫 `0x4F1B11→0x4B6450`。|
|**2**|`0x4F1B68` → `0x4F1BC7` call `0x4D6FA0`|同一 MonsterObject constructor，不同 ctor option 值（本地傳 0）。|
|**4**|`0x4F1BD1` → `0x4F1C31` call `0x4D6FA0`|同一 MonsterObject constructor，本地傳 3；不能猜 1/2/4 分別是 NPC/敵人/寵物。|
|**14**|`0x4F1821..`（另一分支）|type14 特定狀態會先按 object key 查 registry 並更新；**不是 MonsterObject 的已證新建分支**。|
|**3、5–13**|不同物件路徑 / 部分無尾欄|不能把所有 type 都冒稱為 MonsterObject。|

MonsterObject Native `0x4D6FA0` → base `0x4A5F00`，vtable/constructor `0x60AC9C` 由 MSVC RTTI `MonsterObject` 確認；圖像庫 `MonsterImageLib` RTTI 也存在。原件 `0x4D23F0/0x4D5FB0` 由 local resource descriptor 的 **u16 第一欄**呼叫上列 `0x4D7530`、`0x4D7560`，再透過 image pool 依 library+slot 查取。MonsterObject 的 draw/update 虛函式實際呼叫 `0x4D2520` 和 `0x4D31A0/0x4D3360`（約 `0x4D63E0,` `0x4D66..`、`0x4D68..`）。**尚未逐一證明 row `+0x222` 就是最終 Monster sprite image ID**：`+0x222` 的 u16 確實傳給 MonsterObject ctor，但多個本地欄位、motion/graphics pool 的轉換仍需完整追 XREF/實際資源核對。不能把 row 的 u16 認成確定的怪物種族表 ID。

World Library 7000..7023 的註冊已證，**尚未**建立「某 S07 kind → WorldNN.dat 成員 ID」的獨立 call chain。

## 3. 動畫/方向：已證本地 motion selector，不亂命名原作動作

MonsterObject ctor `0x4D70BC..0x4D70D4` 對相關 base motion u16 加 **8**，呼叫 `0x570490` 選用本地 motion；`0x4D6BC0` 的 selector table `0x4D6C28` 有六種值：

|selector（native）|native target|以 MonsterObject `+0x270` u16 base 的偏移|
|---|---|---:|
|0 / 3|`0x4D6BD3`|+0x20|
|1 / 4|`0x4D6BE0`|+0x30|
|2 / 5|`0x4D6BED`|+0x40|

`0x4D6BFE..` 將計算出的 u16 傳入 `0x570490`，接著派送 local action `0x4FD1D0`。此處 **已證是本地動畫選擇器**，**未證**其六個值代表走路、待機、攻擊、死亡或方向數字。`MonsterImageLib` 會按 image ID 查到 DAT 檔與槽位，但 *槽位對應哪個 YPF frame/DOI direction、duration、pivot 和 event callback* 尚無實際 Monster 資料可核對；不要以魔數 0x20/0x30/0x40 當成 Server wire opcode。

## 4. 點擊 NPC／怪物：已證 C43 的兩條 producer 與待確認的 NPCChat 路徑

Native `CObjectInfoRequestPacket` `0x574500` ctor opcode `0x43`、`0x5745B0` writer，decoded C→S body 是 **u8 type, BE u32 object key, u8 subtype**。

兩條實際 Native UI／應用層 producer（比單看 ctor 更具體）：

|原生 producer|Client 對 Packet 寫入|effect|界線|
|---|---|---|---|
|`0x479DC7`|Packet +0x24 type **1**、+0x28 從 `[esi+0x48]` 得 BE u32、+0x2C subtype **4**；`0x479DEB` 送 queue `0x5788A0`|物件資訊/選取路徑帶既有 object key 發 C43|此路徑與原版「點哪一隻 NPC」還需輸入事件上游追證。|
|`0x4A23F8`|Packet +0x24 type **1**、+0x28 由 `[esi+0x4C]` 得 u32（`0x4A240D`）、+0x2C subtype **4**；後續 `0x4A2553`|另一個 UI 路徑組裝同規格 C43|不應宣稱所有 NPC 點擊都送 C43。|

Packet body 在 writer 以 base `+0x18/+0x1C/+0x20` 寫出（與 producer 的物件偏移不同，是多重基底視圖）：`[01] + [BE u32 opaque key] + [04]`，合計 6 bytes。

原件也有 `NPCChatDialog`、`NPCHistoryDialog`、`NPCChatControlPane`、`NPCPortraitControlPane` 的 RTTI／類別與 GUI 方法（例如 `NPCChatDialog 0x4E0B70`），說明 **資訊封包、聊天視窗、歷史記錄各屬不同層**。A-024 已證 Client 可讀 `S34 ObjectInfoReply` subtype6/11（多組動態字串）及 `S3C ShowObjectInfo`，但本輪**沒有**從 C43 producer→S34/S3C receiver→NPCChatDialog 的無中斷 callback 鏈，不能當成原版 NPC 點擊一定收到 S34 或某個選單。對話腳本傳送另參 A-023 S44/C6C；不要把 Born PaperDialog 當已證 NPC 點擊。

## 5. 最小事件表（Client I/O 與 Server policy 分開）

|Client trigger / state|C→S|S→C|Native Client effect / 可信度|
|---|---|---|---|
|已入 World 收到 S07 非空 type1/2/4|無 Client 必然回包|**S07** kind+object instance+local visual fields|創 `MonsterObject`、加入 World，接 image pool 處理；**observed-static**。|
|收到同一 object 的移動／路徑|無需另發 C|**S0C / S64**（A-024）|解析移動；motion selector 是物件內部路徑，究竟哪個 opcode 導致何種動畫仍未完整 XREF。|
|玩家透過已證的兩條資訊 UI 路徑送 request|`C43 01 BE-u32 04`|S34/S3C **可讀**，但是否一對一回覆 **unknown**|已證 C43 serializer / producer；NPCChatDialog 的開啟前置未完成。|
|點擊招募員觸發聊天／腳本|**可能**走 C43 或其他 C2S；不可假設|S44 可以開始 PaperDialog 腳本；是否 NPC trigger 未證|Born.dat 僅指引去 (31,29)，不提供 recruiter entity id/map或互動 opcode。|
|攻擊 NPC/怪物|`C13 BE u32`（A-009）|S13、S08、S5F、S0E 互為不同事件包|Client 特效、生命、死亡和真正移除分開；沒有原服掉落規則證據。|
|怪物動作/外觀資訊變動|無必然 C 包|S29/S62/S63/S34 可能按情境送；不全是 MonsterObject 必需|先看各 native reader，不能把名字當已證 Monster animation sync。|

ServerOwner (**designed, not original Server**)：Actor instance 分配、視野、距離、click target、互動權限、NPC dialog script/flags、monster AI、技能冷卻、攻防/死亡、掉落及同時事件排序由 Server 管理；依驗證的 Client 畫面/素材 resource ID 投影。不得把資源檔名當 Server role、也不得把 C43 當自主授權。

## 6. 本輪證據、測試、缺件與真正未解項

- `A011-E01`：World/Monster 24+43 個資源庫註冊 VA `0x404331..0x4043AF`。
- `A011-E02`：檔名常值兩種起始 VA：`0x5F1D3A @Monster...` 與 **實際** `0x5F1D3C Monster...`；`World 0x5F1D5C`。
- `A011-E03`：`0x4D7530/0x4D7560` Sprite image ID quotient/remainder。
- `A011-E04`：S07 handler `0x4F1A8B/0x4F1B68/0x4F1BD1` 及 ctor `0x4D6FA0`。
- `A011-E05`：Monster motion `0x4D70C1`、`0x4D6BC0..0x4D6C28`。
- `A011-E06`：C43 native `0x574500/0x5745B0`、producer `0x479DC7/0x4A23F8` 及 1/4 選項。
- `A011-E07`：NPCChatDialog/NPC History/Dialog RTTI、`0x4E0B70` GUI callback 存在，尚未串起收包/點擊。
- `A011-E08`：原件 Hash-locked probe `task_a/roy2/a011_native_probe.py` **29 VA byte anchors、4 RTTI、3 UTF-16 literals 本地 PASS**；codec 與 synthetic unit tests 見 `a011_resource_codec.py` / `test_a011_resource.py`。**沒有執行 Native Client E2E**。

重跑：
```sh
python task_a/roy2/a011_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p "test_a011_resource.py" -v
objdump -d -M intel --start-address=0x404331 --stop-address=0x4043b0 Asgard.exe
objdump -d -M intel --start-address=0x4d7530 --stop-address=0x4d7588 Asgard.exe
objdump -d -M intel --start-address=0x4f17c0 --stop-address=0x4f1c50 Asgard.exe
objdump -d -M intel --start-address=0x4d6bc0 --stop-address=0x4d6c43 Asgard.exe
objdump -d -M intel --start-address=0x479d9a --stop-address=0x479df0 Asgard.exe
objdump -d -M intel --start-address=0x4a23ce --stop-address=0x4a2419 Asgard.exe
```

**還缺的具名資源**（只在要確認真實 NPC 圖像及動畫時需要）：實際原版同版 `Monster00.dat`（或你擁有的任一 `MonsterNN.dat`）及 `World00.dat`（或任一 `WorldNN.dat`）樣本、可對應的 UI/動作 DOI/YPF 資料索引與版本來源；欲驗證招募員對話腳本實現還需要確切引用的 `PaperDialog.dat`（A-023 已點名，不能直接假設對應 C43）。**不要上傳整包圖像，也不用重傳已有 Asgard.exe、Born.dat、Map0..2.dat**。

**完成/界線**：本輪取得可重現的「Client Resource ID→Monster archive/slot」、「S07 kind1/2/4→MonsterObject」、「C43 兩條 UI request path」及「Monster motion selector」靜態子集；因缺實際 Monster 資產、NPC 類型／SpriteID 最終欄位 XREF 與完整 click→chat callback，`A-011 status=integrated / handoff_status=partial`、`native_client_validation=not-run`；**不是宣稱 NPC/怪物全部外觀、方向動畫、掉落或實機對話已還原**。


## 7. 正式 GitHub CI 校驗與交付結論

GitHub Actions [run 41186221751](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41186221751) 狀態 **success**：原專案 phase-gates 檢查通過，A-024 先前 19＋7 項 regression tests 通過，A-011 **16/16 synthetic unit tests PASS**。A-011 SHA-locked 原始 `Asgard.exe` 本地 native verification **29 VA anchors、4 RTTI、3 UTF-16 literal checks PASS**；這些是程式碼與 resource ID 結構驗證，不是 Monster 素材、Sprite 動畫或 Client GUI 的原生 E2E 驗收。CT-067 offline subset checked；CT-068 native validation **not-run**。

**最終分工狀態：`integrated/partial`。** 已取得可交 DEV 的原生 ID 算法、S07→MonsterObject factory、C43 兩條 producer、Monster 本地 motion selector。要讓「某隻特定 NPC/怪物的外觀及每個動作如何播放」達到可執行的原作相容規格，仍需要實際持有的 **`Monster00.dat`**（或任一實際存在的 `MonsterNN.dat`）及可能的 **`World00.dat`**（或任一實際存在的 `WorldNN.dat`）對照 Client reader；NPCChatDialog 的必要腳本在引用已證前不能假定就是 **`PaperDialog.dat`**。已提供的 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat` 不需要重傳。
