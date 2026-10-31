# A-008／roy2 — 數值／狀態面板：原生 Client BIN-first 完整靜態 I/O 契約

日期 2026-10-31；唯一工作分支 task_a/roy2；SYS-STATS / R-009 / A-008。原始 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145，PE32、ImageBase 0x400000。**本報告根據實際原件指令與 RTTI，不是依據 Server 期望猜 opcode。**所有地址皆為 VA。遊戲素材及原始 EXE 不提交。

## 1. 已證 Native 入口／封包

| 類別與方向 | 入口及指令證據 | decoded body |
|---|---|---|
| SStatusPacket S→C | RTTI .?AVSStatusPacket@@ → vtable 0x61567C → constructor 0x586CD0；0x586CEB push 0x08; reader 0x586D40 | **S08 = BE u16 flags + 旗標指定區塊**；非固定 8-byte，與 S05 外觀不同 |
| CAddAbilityPacket C→S | RTTI .?AVCAddAbilityPacket@@ → vtable 0x6134F0；constructor 0x5708B0，0x5708C9 push 0x47；serializer 0x570960 | **C47 = u8 one-hot ability_choice**；唯一一次 0x45AB00 byte writer |
| Status / StatusDialog | RTTI 對應 status / GUI；Status 接收處理 0x53F8A0，StatusDialog callback 0x540640、0x540660 | 0x54066A 檢查 packet opcode **0x08**，0x540677 呼叫 0x53F8A0，之後 0x540050 刷新畫面 |
| ExpBarDialog | RTTI .?AVExpBarDialog@@；vtable 0x60663C | 經驗條類別存在，但本研究沒有將 UI 值的「經驗值比例」公式當作已證 |
| 持續效果 | RTTI SAddLastingSpellPacket / SRemoveLastingSpellPacket | 另有獨立 S2C 路徑；不可直接推論 S08 包含完整 buff/debuff 計時 |

RTTI → CompleteObjectLocator → vtable 的分析依原件指標反向定位，非僅按類別名稱猜測。原生 parser 的數位 reader：0x45ADB0 = u8、0x45ADE0 = BE u16、0x45AEB0 / 0x45AE30 = 32-bit reader（本 profile 網路 BE）；0x45AFF0(1) 消耗一個不存入物件的 byte；0x45B7A0 讀 **string8 長度 + bytes，再以 Client codepage 轉 UTF-16**。

## 2. 玩家操作 → C → S → Client 反應

| Trigger | C→S | S→C | Native Client effect / 不可超推 |
|---|---|---|---|
| 狀態視窗 ability 控件事件，UI id 0x13..0x17；0x53FD60 檢查 id 範圍 | C47，一個 u8：依序 0x01、0x02、0x04、0x08、0x10；0x53FDAE 建構，0x53FDEC 交送至 0x5788A0 | S08 是已證狀態通知路徑，但**未證每個 C47 有即時且一對一 S08 ACK** | Server 必須決定能否加點；Client 傳的是選項位元而不是加點後所有值 |
| 原生 World/Status 物件收到 S08 | 未由 S08 本身必然發 C 封包 | S08 的 BE u16 flags 與條件資料 | 0x540660 判 opcode==8 → 0x53F8A0 將欄位複製進 Status singleton 0x66D1C8 → 0x540050 UI refresh |
| HP/其他 resource 數值更新 | 傷害與技能發起路徑由 A-009/A-010 負責，不能直接稱作 C47 | S08 flags 0x40 基礎最大值、flags 0x20 四組目前值 | 0x53F8A0 會把目前值超過其最大值的欄位在 Client 顯示狀態中截頂；**Server 原版公式、何時死亡並未由此證明** |
| 查看狀態視窗／經驗條 | 尚未證每次開窗都會送封包，避免虛構 C opcode | Client 可收到 S08 | StatusDialog/ExpBarDialog 已證存在，**各 GUI 標籤與經驗顯示單位仍須 UI resource / callback XREF** |
| 裝備改變 | 依 A-007 的 C1C/C1E，與加點 C47 不同 | 已證裝備 S37，S08 是否同時送達由 Server 設計 | 裝備加成公式未知；此處不將外觀 S05 或動畫特效冒稱狀態更新 |

### 原生 flags 與嚴格 wire 讀取順序

mask = S08 首欄 **BE u16**（0x586D49→0x45ADE0）。byte 0 高位元段使用 BL，bit9 使用 BH bit1。當本輪沒有該區塊時，**不消耗該區塊的 byte**。

| flags bit | body 中緊接的內容 | 本機 parser 地址 |
|---|---|---|
| 0x0040 | **61 bytes**：skip/reserved u8；u8；BE u32×4；BE u16×2；u8×2；BE u16×2；u8×6；BE u32；u8；BE u32；u8；BE u32×2；u8×3；BE u16；u8×4。精確順序見下方 offset 表 | 0x586D7B..0x586EE8 |
| 0x0020 | **16 bytes**：BE u32×4 currently displayed resource candidates | 0x586EEB..0x586F1C |
| 0x0010 | **16 bytes**：BE u32 + BE u16×4 + BE u32 | 0x586F22..0x586F6D |
| 0x0008 | **5 bytes + string8**：u8×5，接 u8 string length + CP bytes | 0x586F75..0x586FD4 |
| 0x0200 | **1+N bytes**：u8 count (0..255)，後續 N×u8；native vector | 0x586FD9..0x587054 |
| 0x0001 / 0x0002 / 0x0080 / 0x0100 | flags 中轉為本地布林值，**不另消耗 body** | 0x586D6B..0x586D8B、0x587056..0x58705D |
| 其他 bits | 已知本段 parser 未讀專用 payload；其業務語意 unknown，不能猜成 HP/MP | 待版本差異驗證 |

flags 0x40 時，wire 讀取到 Packet 本地 object offsets，**不是 wire 相對 offset**：

| Wire 連續型別（依順序） | Packet object offset / 相關用途 |
|---|---|
| skip u8、u8 | skip；+0x28 |
| u32×4 | +0x2C,+0x30,+0x34,+0x38；0x53F8A0 複製為 Status +0x420,+0x428,+0x430,+0x438（四組上界） |
| u16,u16,u8,u8 | +0x3E,+0x3C,+0x69,+0x68（注意 native 賦值**不是**升序） |
| u16×2；u8×6 | +0x42,+0x44；+0x46..+0x4B |
| u32,u8,u32,u8,u32,u32 | +0x4C,+0x50,+0x54,+0x58,+0x5C,+0x60 |
| u8,u8,u8,u16,u8×4 | +0x64（native store 為 u16 zero-extend）、+0x66,+0x67,+0x6A,+0x6C..+0x6F |

0x20 四個 u32 存 Packet +0x74,+0x78,+0x7C,+0x80，再由 0x53FB25..0x53FBB2 依各 Status 最大值裁切，寫至 Status +0x478,+0x47C,+0x498,+0x480（其中第 1 組也使用 +0x474 前值，涉及顯示/插值）。**這是 Client 值域限制，不是 Server 權威數值公式。**

0x10 資料留在 Packet +0x88、+0x8C..+0x98 (4×u32 本地槽但 wire 各 BE u16)、+0x9C；Status 接收時映射至 +0x484,+0x488,+0x48C 等欄位。0x08 的 5 byte 放 +0xA4..+0xA8、string8 放 +0xAA。0x0200 放 +0x2B0 dynamic list。flags 0x0100 存 Packet +0x2C0 的布林值。

**長度例**：flags 0x0000: 2 decoded body bytes；flags 0x0020: 18；flags 0x0040: 63；flags 0x0010: 18；flags 0x0008: 8+N；flags 0x0200: 3+N。多個旗標並存，依 **0x40→0x20→0x10→0x08→0x200** 串接，不是以 flags 數字大小排序。

### C47 GUI bit 判斷與安全性

0x53FD60 的事件 id 介於 0x13..0x17（含），switch 對應寫入 Packet +0x24 的值 {1,2,4,8,16}。0x570960 只透過 0x45AB00 寫 **一個** byte（Packet +0x18 是 base class serialization view）。**不包含目標角色 ID、增加幾點的 u16、預計新數值或 Server 權限 token。** Server 根據認證 session 持有角色及合法可分配點數自行裁定；C47 的任意位元組皆屬 untrusted。

## 3. 初始、溢位、死亡及更新邊界

- 初始狀態：必須先能正確初始化 Client Status；S08 0x40 是具有四組最大值的完整資料子集，0x20 只能更新目前值，**不得把 0x20 當成全量初始化**。是否還有必要的初始 flag/序列需 Native CT 判定。
- 更新：0x53F8A0 的 0x40/0x20/0x10/0x08 等分支執行不同本地欄位更新，接收回調 0x540660 不直接再送 C47。不能把 S08 模擬成單一固定 schema。
- 邊界：wire u32 保留 0..4294967295，native 受值域限制的 resource 欄位會取 min(current,max)（以無號比較 jbe/ja 執行）。這**不**證明 Server 原版允許此極端值。若 Server 以 signed int32 實作，必須先檢查溢位；固定寬度/合理最大值屬 **designed**。
- 死亡：0x53F8A0 只證數值映射及裁切，**沒有從此函式證實 hp==0 就是原服死亡協定**；S5F DieObjects、戰鬥包與 A-009 是另一條鏈，不能把 S08 0x20 更新等同死亡廣播。
- 裝備修正：換裝與 C47 不相同，尚無「一件裝備增加多少 HP」的客戶端權威值；此數學問題列 Server 專用 unknown，不阻擋已證 C/S wire 子集。
- 成功／拒絕：C47 不是要求 Client 本地改點數的可信來源；S08 是獨立狀態投影。未證 Server 對非法 C47 的特定錯誤碼，**不發明固定錯誤 S 包**。
- 重送與多點：C47 沒有序號或 nonce，Server 必須用自己的請求邊界、餘額、角色狀態及去重/transaction 規則防止重複增點（designed），不能宣稱原服 exactly-once。

## 4. 可重跑 evidence、CT 與結果

執行：
- python task_a/roy2/a008_native_probe.py Asgard.exe
- python -m unittest discover -s task_a/roy2 -p 'test_a008_status.py' -v

離線原始 EXE 的 15 個 native VA 指令 byte pattern + 4 類 RTTI 检查 **PASS**；10 個 pure synthetic decoded body / failure boundary tests **PASS**。測試驗證 read order、max string8 255、vector count 255、truncate/excess、C47 one-hot 值；**沒有**把 synthetic 當成 native Client online E2E。具體靜態證據定位：A008-E01 S08 class/ctor；E02 reader flags + field groups；E03 Status::update；E04 UI on S08；E05 C47 class/ctor/serializer；E06 StatusDialog ID mask UI；E07 15 native checks；E08 10 synthetic tests。

原版 Client 驗收建議：CT-STATS-01 初始化 S08 full + partial UI、CT-STATS-02 C47 五種按鈕、CT-STATS-03 正常/滿點/非法與重複送、CT-STATS-04 HP/其他顯示超最大/歸零/死亡分離、CT-STATS-05 裝備修正/重登。狀態 **planned / native_client_validation=not-run**，與 A 的靜態交付可分離。

## 5. 交付範圍與真正未知項

**本輪已完成 A-008 的 Client I/O 靜態 wire/trigger/receive/reaction 主要鏈**，足以讓 DEV 實作 S08 核心編碼與 C47 最小安全接收器；不需原服、原版伺服器 DB 或出生 policy 才可結案其靜態子集。

必須維持 unknown，不得猜：四組 resource 的畫面標籤/HP-MP 精確映射、所有能力欄標籤、ExpBarDialog 經驗值公式及單位、裝備加成公式、失敗錯誤字串/是否直接回 S08、原服起始上限與數學公式、死亡/復活與 S08 相對順序、完整非 TW profile、原生 Client E2E。這些不應作為 **A-008 Client I/O 核心靜態研究** 的假阻塞，但需要在 DEV/CT 開發和下次原生資料驗收中追蹤。

原始檔案需求：**本輪無新增缺件**。Asgard.exe 已有；地圖 DAT/Born.dat 與此狀態 packet 無必需關係。遇到 UI 獨立配置檔必須在 Client 讀檔程式中確定實際檔名後再提出。

**研究狀態**：A-008 status=integrated、handoff_status=ready、implementation_ready=true（僅 S08/C47 靜態 wire subset）；native_client_validation=not-run。未知 Client 文字/原版數學與真機 CT 不應被表述為已完成。
