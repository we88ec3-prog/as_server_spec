# A-003 / roy1 — 創角合法集合、姓名／帳號關聯、C02/C04 與角色模型（BIN-first）

日期：2026-10-31；原件：使用者提供的 `Asgard.exe`，PE32 x86 image base 0x400000，size 3,235,840，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。profile：`TW-seed0-local-v0.1`，分支：`task_a/roy1`。Evidence：`ev_a003_20261031_asgard_create_palette_ui_static`。方法：objdump 原件 + 解析 .data/.rdata section bytes，交叉復核 A-021/A-027/A-028；5 個純合成 fixture 測試。**observed-static 是原 Client 可證，designed 是新 Server 安全政策；未抓原服流量、未執行原 Client 原生建角 E2E。**

## 結論速覽

1. **C02 是原生 NewUser UI 送出**，region 2/3/4 的 body 為 4×string8+u8，其他 region 為 3×string8；第一欄來自 UI `Dialog+0x26c`，第二欄來自 `+0x270`，`+0x274` 是與第二欄比對的**本地確認輸入**，不直接出現在 C02 的前二欄。欄位語意不能直接假設為新的 CharacterName / AccountPassword（A-027 的 owner 認證缺口仍存在）。
2. 新追到**第 1 欄最小窄字串長度的來源**：初始化函式 `0x498420` 在 `0x49846f` 令 EBP=12，`0x498628` region switch 中 **region=0 寫入 `[0x91fed0]=6`**（`0x4985dc`），region=1..4 寫入 EBP=12（`0x4985e8`）。實際 `0x4B1A30` 校驗時 region=0 直接返回 true、不檢查長度；region!=0 則 `0x550910` 取得 narrow 字串後掃描 NUL 得 byte 長度，再與 `[0x91fed0]` 比較 **len>=12**。這是 Client UI gate，不等於 Server 最小角色名稱長度，更不是帳號所有權證據；`0x4B1C21` 用全域值設定輸入控件的屬性，但控件 API/上限精確規則尚不能宣稱。
3. C04 `0x574420` 只輸出 **5 個 u8：預覽選擇+0x48、+0x49、按索引查色表後的三個 RGB byte**，**沒有 name 字串**。所以若原版有 CharacterName，它一定不是這個 C04 body 的獨立 name 欄位；可能來自 C02 的某欄或 Server pending context，沒有 Server 證據前不能把它確定命名或自行產生第二個名字。
4. **可證固定的十筆 Client RGB 色表**：原件 .data VA `0x66422c` 恰有 10 個連續 LE DWORD，隨後 `0x664254` 是 RTTI/vtable 類型資料，故表恰到 index9。C04 `0x4B203d` 用 signed byte `[appearance+0x4a]` 當索引，load `DWORD PTR [index*4+0x66422c]`，傳入 `CL, CH, (ECX>>16).low`。這證明**原生色盤選擇值 0..9 所代表的 10 色 RGB**，但**不證明原版 Server 會拒絕其他任意 RGB**；不可信修改版 Client 可合成 u8 內容，Server 必須另有 validation policy。
5. 性別（sex）與髮型（hair）是 C04 前兩個 u8，在本次 BIN 追到的是 Client 預覽控件選擇值，**沒有能證明 Server 可接受哪些 sex/hair 值的完整集合**；一帳號是否可建多個角色、重名判決、原服 S02 各錯誤碼的文字語意也仍 unknown。不能以一般 MMO 常識補 0/1 或髮型 0..N，也不能把 `A-028` 已找到的焦點狀態碼直接命名為「重名」。

## 原版位址／證據清單

| VA | 實際證據 | 結論限制 |
|---|---|---|
| `0x49846f, 0x4985cd..0x4985ee` | EBP=0xC，switch 後把 6 或 EBP=12 存 `[0x91fed0]`；`0x498628` jump table 0→`0x4985dc`，1..4→`0x4985e8` | 動態 region UI 參數，不是原 Server 拒絕碼 |
| `0x4b1a30..0x4b1a83` | region0 skips；else `0x550910`、逐 byte 尋 NUL、`cmp 0x91fed0, byte_count` | Client narrow string length >=12 (region1..4), 不代表 Unicode code points |
| `0x4b1c21..0x4b1c8a` | 設定第一 edit 的 `[0x91fed0]`、第二及確認 edit push8 | 顯示 UI 控件參數，不能把它當 wire string8 長度；C02 上限 byte 最大255 另由 codec |
| `0x574170;0x5742b0..0x574352` | C02 ctor opcode0x02；serializer region2..4 4×string8+u8，其他3×string8 | region1 之 UI 額外控件與 serializer 分支不一致（A-027），語意 unknown |
| `0x4b27b5..0x4b2811` | 第一/第二 UI 文字複製到 C02，確認文字存 stack；byte buffer cap 寫入0xff | C02 field1/field2 對應來源已知，character_name/credential 語意只 inferred |
| `0x4b28fd..0x4b2916;0x5b4a62` | C02 第二欄與 confirmation 在本地以 UTF-16 逐 word 做 equality | 本地確認不是 Server 密碼驗證 |
| `0x4b2031..0x4b205a` | UI 預覽來源 `+0x48/+0x49/+0x4a`，C04 byte+0x24/+0x25/+0x26..28，sender `0x5788a0` | C04 沒有角色姓名/自訂 token/冪等鍵 |
| `0x574420..0x57445e` | 5×`0x45ab00` write-u8 | wire body=5 bytes |
| `0x4b0d10,0x4b0d20,0x4b0d30` | 預覽選擇 state `+0x48` / `+0x49` / `+0x4a` 的 accessor；最後者查色表 | 不能單靠 getter 說明枚舉合法總數 |
| `0x66422c..0x664253` | 10×little-endian DWORD，緊接 `0x664254` 非顏色資料 | Client 原色表 0..9 |
| `0x56084b,0x560b9f` | 顯示/預覽 renderer 也查同色表 | 不是只有網路 writer 使用的偶然資料 |
| `0x4b1f46..0x4b2066` | C02 後 S02(status0) in state0x1d→C04→state0x1e | 第一成功不是角色已提交 |
| `0x4b206b..0x4b217a` | state非0x1d 收成功 S02 時做 UI 操作、region3 建額外視窗 | 此 callback 不直接 S03，登入/重登仍 unknown |
| `0x4b1da9..0x4b1ded` | S02 status 3..31 的 focus 跳表 | 3/4/18/26/31 focus first edit、17 focus second edit，但**錯誤碼的原始字義 unknown** |
| `0x4b1f1b..0x4b1f34;0x5715f0;0x5716a0` | S02(nonzero)→C15 (opcode0x15, empty body)→state0x1f | Cancellation 未帶 account/intent，不能撤銷已持久角色 |
| `0x4aef08;0x4b0b67` | 兩條建構 MakeInfoDialog 路徑 | C03 已登入無角色能否到此畫面未證實 |

### 原始十色表（C04 線上 RGB byte 次序）

|Index|原 DWORD (LE)|C04 RGB bytes|Hex RGB 表示|
|---:|---|---|---|
|0|`0x00285A91`|`91 5A 28`|`#915A28`|
|1|`0x006464FF`|`FF 64 64`|`#FF6464`|
|2|`0x00FAB482`|`82 B4 FA`|`#82B4FA`|
|3|`0x00FFFFB9`|`B9 FF FF`|`#B9FFFF`|
|4|`0x00E6B4FA`|`FA B4 E6`|`#FAB4E6`|
|5|`0x000096FF`|`FF 96 00`|`#FF9600`|
|6|`0x0064BE82`|`82 BE 64`|`#82BE64`|
|7|`0x0064FFD5`|`D5 FF 64`|`#D5FF64`|
|8|`0x0095C8FF`|`FF C8 95`|`#FFC895`|
|9|`0x005A5A5A`|`5A 5A 5A`|`#5A5A5A`|

**byte-order 勘誤**：不能把原小端 DWORD 的高位優先讀成 RGB；C04 使用 little-endian dword 的前三個 bytes，順序如表。若 UI color index 越界會涉及原版不可預測查表，所以本地合成工具嚴格限制 index0..9；不表示 Server 的原生「顏色失敗碼」已確認。

## 合法值、重名與角色數量的證據分級

|項目|已確認範圍|仍 unknown|
|---|---|---|
|C02 文字 wire|每個 `string8` 單 byte encoded length 0..255；TW profile 以 CP950 編碼可用合成測試|具體 username/character name 語意、Server 可接受 CP950 字符/保留字/重名大小寫、所有其他 region 編碼|
|C02 第1欄 UI|region!=0 narrow byte 長度至少12，region0 skip；UI 有長度/其它條件，field1 來源對應|原服最小角色名長度、是否等於 account name（不能假定）|
|C02 第2欄 UI|必與另一個確認 UI text 相等；控件曾 push8 參數|Server 是否視為帳密、其真正 credentials、其他欄位作用|
|C04 sex|單 u8 (0..255 wire representable)|原生選單、角色性別代碼真實合法集合及對照|
|C04 hair|單 u8 (0..255 wire representable)|真正髮型選單數、性別/地區依賴與角色資源合法性|
|C04 hair color|原版 Client 預設選色表 index0..9（10個 RGB；由 Client 查表後傳 bytes）|原服是否接受其他 RGB／變體或保護規則|
|帳號角色關係|C04 無 name/list/slot；原本 UI NewUser 而非現代式角色清單可證|原服是否同帳多角、角色列表/選角/刪角；一帳一角只可設計保守 policy|
|成功與失敗|C02→S02(0)→C04→S02(0) UI；S02(nonzero)→C15；部份狀態碼 focus|各 S02 status 的「重名」「姓名非法」「已有角色」「停權」語意、原服 transaction 時點|
|斷線與重送|C04 無 request id；C15 無 body；S02 UI 分流|原服是否保留 pending/timeout；安全新版 Server 要 owner+intent+generation/unique constraints|

## Server 可交 DEV 的最小安全規格（designed，不冒認 native）

- R-025：**Admin 獨立建 Account**；C02 永遠不得 `INSERT Account`。A-027 尚未證實原 Client 無角預建 Account 的安全登入/認領，因此無可信 AuthContext 時 **不得**透過 C02 直接 claim、回 S02 success 觸發 C04 或建立 Character。
- 倘若取得 native compatible 且已驗證的 Account owner（credential verifier 或 C03 已綁定的 session），Server 設 `PendingCharacterIntent(account_id,character_candidate,session_generation,expiry,body_digest)`，在 C04 收到 five-u8 後做按資源版本的合法值檢查（當前 Client 色盤十色是可支援子集，其它原服 RGB 政策 unknown）。
- 在新的 TW 相容安全 profile 可**暫定**一帳一角色（`unique(account_id)`），但這只是缺原生多角色列表證據前的保守**Server 設計**，不是原版確有一帳一角；角色名稱只有在確定來源及 owner 後才儲存，正規化/unique name policy 需獨立標 designed，不可從 S02 focus status 硬猜重名錯誤碼。
- 同帳號兩連線、同名並發必須用 DB transaction/CAS 唯一約束裁定；同 verified owner/pending/body 重送回已保存結果，改 body/跨 owner 拒絕；C15 只清未提交 pending，不刪已提交角色；C04 durable transaction commit 後才回對應成功（designed，原服 commit 未知）。
- 沒有原生錯誤碼證據就保留 internal validation enums，待 A-027/028/Client CT 取得真正 S02 status/message 映射才回相容 response；不能把登入錯密 status3 移植為創角重名。
- **即使 A-003 的有限色盤/codec 子集可實作，也不能解除 SCN-008 的原生身份/轉場阻塞**。

## 流程矩陣（Client vs Server）

|情境|Client proven|Server design|native ready?|
|---|---|---|---|
|NewUser 登入前顯示、提交 C02|可送 C02|只 decode/記安全診斷；無 owner 不建角|no|
|Region2/3/4 C02 extra fields|四 string8+flag|依 profile parser，未知含義不當授權|codec subset|
|Region1 C02 UI 額外兩欄|與 serializer 第三欄 branch 不完全對應|不要猜輸入語意，依 wire variant 鑑別|partial|
|C02 first field region!=0 長度11/12 bytes|11 會 local gate fail、12 才通過該 gate|Server 仍獨立檢查 owner/name|input gate only|
|C04 hair color選第9色|傳送 5a5a5a|按 Client ten-color fixture 可支持|UI subset|
|兩次同名不同 owner|Server 決策不可由 Client code 證實|pending/unique name identity transaction|designed|
|成功 C04 後收到 S02(0)|只 UI transition，不直接 S03|原子提交後成功回覆，再依合法登入路由轉服|partial|
|S02(nonzero)→C15|確定 C15 empty+state1f|只取消同 owner/generation 未提交 pending|partial|

## 驗收/重現

新增 `tools/a003_create_contract.py`（5項 unittest）：C02 region2..4/else layouts、CP950 byte count、第一欄 UI narrow-length gate、十色表及 C04 RGB bytes、pre-auth 無權建角、同帳/同名唯一與 C15 不撤銷已提交角色。此為 **bin-derived synthetic + designed** 模型，不代表真實原版 Server/Client 執行。

新增 `CT-052`（原版 C04 色盤、CP950 與區域 codec）和 `CT-053`（同名、同帳、C15、重送、無憑證拒絕）。原有 `CT-011～014`、`CT-029～032` 更新 A-003 對照；原生 E2E 仍 not-run。

重現命令：
```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x498420 --stop-address=0x498630 Asgard.exe
objdump -D -M intel --start-address=0x4b1a30 --stop-address=0x4b1c90 Asgard.exe
objdump -D -M intel --start-address=0x4b27b5 --stop-address=0x4b2950 Asgard.exe
objdump -D -M intel --start-address=0x4b1f46 --stop-address=0x4b2066 Asgard.exe
objdump -D -M intel --start-address=0x574420 --stop-address=0x57445f Asgard.exe
objdump -D -M intel --start-address=0x4b0d10 --stop-address=0x4b0d44 Asgard.exe
objdump -s -j .data --start-address=0x66422c --stop-address=0x664254 Asgard.exe
python3 tools/a003_create_contract.py
```

**確切缺失資源/證據**：要把 character name/重名/同帳角色數/sex-hair 枚舉從 unknown 變 native-proven，必須有相同 client SHA 的原服 C02/C04/S02 正負案例封包截錄與原版建立 UI/角色選單畫面（或更深 Client 髮型/性別列表資源）。目前沒有可確認的特定 `*.dat` 檔名會單獨提供原服的帳號唯一性／拒絕政策，不應虛構缺失檔名。原版 EXE 與完整資產不推送 Git。
