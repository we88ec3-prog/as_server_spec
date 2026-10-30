# A-021 follow-up：分析先行、原生 NewUser 分支與可實作設計

日期：2026-10-31；工作分支 `task_a/roy1`；原版 Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。本篇為 **observed-static + 明示 designed 相容方案**，不是 Client 實測。

## 靜態深入追查（BIN-first）

| VA | 靜態觀察 | 使用意義 |
|---|---|---|
| `0x4B1A90` | MakeInfoDialog 建構，初始 `[esi+0x4c]=0x1c`，依 region 配置 `+0x268..+0x27c` UI 控制 ID | 新使用者建立/資料輸入畫面 |
| `0x4B2764→0x4B279E` | 提交控制 `[esi+0x278]` 分支建構 C02 (0x574170) | C02 不是必須在 C03 後發送 |
| `0x4B27B5..0x4B27F2` | UI 控制 `[esi+0x26c], [esi+0x270]` 對應文字複製到 C02 第一、第二欄；內部封包存放位置為 +0x24/+0x224 | 與 stream 子物件 serializer 所見 +0x18/+0x218 相差 0x0c，不代表欄位變更 |
| `0x4B2825..0x4B28D2` | region 選擇後續文字欄（+0x424 或 +0x624/+0x822），並從 `[0x66D110+0x219]` 放入旗標 | 不能在未確定 region 時使用單一格式 |
| `0x4B21E0→0x4B229F` | UI 發 C02，local_state 設 0x1d | 確認 C02 已送出 |
| `0x4B2340→0x4B1D60` | 收到 opcode 0x02 回覆進 S02 UI handler | 必須保持會話階段 |
| `0x4B1F46→0x4B205A` | status=0 且 local_state=0x1d 時送 C04 (sex/hair/RGB)，改設 state 0x1e | **C02→S02(成功)→C04** 可由原生碼支持 |
| `0x4B206B` | 非 state 0x1d 的 S02 成功 UI 分支 | 不是直接發 S03 的證據 |
| `0x4AEF08 / 0x4B0B67` | MakeInfoDialog 可由兩條上層建構路徑建立 | 尚無證據表明 C03 已存在無角色帳號會自動切至此 UI |

S02 status 3..31 的 jump table `0x4B21A8 / 0x4B21BC` 有不同 UI 處理分支；應保留 status 原始數值，**不要沿用登入對話框的錯誤文義猜測創角錯誤碼**。上述為 VA（不是 file offset），可在相同 SHA 以 `objdump -D -M intel --start-address=0x4b2700 --stop-address=0x4b2b00 Asgard.exe` 複核。

## Server 必須採用的暫定相容策略（designed，非宣稱原服）

```text
Admin.ProvisionAccount(name, credential) -> existing Account { character=null }
   ├─ Client 原 NewUser UI：C02 → 檢查「已存在、未停權、未初始化」帳號與憑證
   │       → PendingCharacterInit（短期 lease；無 INSERT Account）
   │       → S02(status0) → C04(外觀五 byte)
   │       → 單次交易建立 Character + Appearance；消耗 lease
   │       → S02(success) → 以原生登入畫面走 C03 → S03/C10/World
   └─ Client C03：
           已有 Character → 正常 S03/C10/World
           沒有 Character → 不可進 World；安全回覆並提示使用原生 NewUser UI
```

C02 **可在 C03 之前發送**。不能把「必須先有已登入 C03 Session」當成 C02 的通用前置規則。C02 只允許認領後台已預建帳號，嚴禁自行 INSERT Account；驗證帳號認證、停權狀態與 pending lease。C04 必須與同一條合法 pending session/owner 綁定，transaction/唯一約束保證重送、競態、斷線、回覆遺失不重複建立角色。C02 內四個欄位暫以 field1..field4 命名，不能假造特定帳密/名字語意；需以實際 UI 控制和合成向量逐一完善。

**重要相容風險**：User 要求的「管理員建帳 → Client **先 C03 登入** → 原生 UI **自動**創角」沒有靜態證據足以證明；若原版 Client 只允許從 NewUser 畫面啟用，那就是目前 **designed** 的替代操作流程。這個限制不應妨礙 Server 先完成可實作的協定與 Domain；Client 實測或 BUG 後再查證 UI 路徑與更新規格。不能聲稱 UI 已經正確呈現。

## 分析結案與實測分離

本 A 的靜態流程、可還原欄位、Server 安全方案與未知分支已整合；`A-021=integrated`、`implementation_ready=true`、`Client CT=planned`。實機 CT-011..014/018/019 不屬 A 的先決門檻；若實際發生 BUG，按封包/UI 回傳證據修訂規格與實作。不得以「無實機」設 `blocked`。

尚待其他分析或下游 CT 回饋：C02 各文字欄真實用途、C03 no-character → 原生 UI 的完整跳轉、C04 後 S02 狀態語意、合法外觀選項，以及 C02 新使用者 UI 和 R-025 僅後台建帳的交互方式。
