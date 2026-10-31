# A-030 follow-up／roy1 — 創角 E-MAIL 使用哪個原生封包（C02 field4）

2026-11-01；固定分支 `task_a/roy1`；唯一原始分析對象 `Asgard.exe`，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，ImageBase `0x400000`。R-025/R-026、A-030 既有交接的精準增量，新增證據 `ev_a030_20261101_email_c02_fourth_field_static`。方法是 *BIN-first*：本次重新從原始 PE 指令完整串接控制項、packet 記憶體 offset、writer 和送出，並額外追最後確認視窗讀取欄位的來源。**原版遊戲 UI label 和實際 E-MAIL 明文字串未從尚缺的資源/實機驗證；資料含義和 byte 位置需分別標記**。

## 答案（先分來源可信度）

- **已確認的原生封包**：創角表單走 **C2S `CNewUserPacket` / `C02` (opcode `0x02`)**，由 `0x574170` 建物件，`0x5742B0` serialize，`0x4B229F` 發送；不是 C04（那是 5×u8 外觀欄位），也不是專用 C-E-MAIL packet。
- **已確認的 Region 2/3/4 寫入**：`C02` body 是 `F1:string8, F2:string8, F3:string8, F4:string8, flag:u8`。F3/F4 是表單兩個額外字串，**F4 正是額外輸入區的第二個控制項**；對於使用者看到的順序 `ID/PASSWORD/CONFIRM/NAME/E-MAIL`，F3=NAME、F4=E-MAIL 為**高度可信對應，但標籤字面尚未獨立驗證**。不應在證據索引寫成已由 EXE 字串直接確證 UI label。
- **其他 Region**：Region 0/1 的 writer **只送三個 string8**，不包含上述 Region 2..4 的 F4；Region 0 F3 由 widget `0x0A` 條件填入；Region 1 的 UI 雖填額外控制項，writer 只送 `packet+0x424`，此欄來源在已追 submit 分支有不一致。不能把 Region 2..4 的 E-MAIL 位置無條件推廣到所有區域。
- **E-MAIL 是否可空、Email 格式、原 Server 是否儲存**：從本次靜態路徑無法證明；此輪只證封包傳送路徑，不改 DB/Server/Client。

## 原版 BIN 上的實際資料流（非猜測）

|階段|原始 VA 與指令結果|證據 |
|---|---|---|
|決定 Region| `0x498000` = 讀 `LanguageMan+0x4`；`0x5742EC/0x5742F1` 判斷 2..4 走加長 C02 writer；不能從 EXE alone 確知當次 runtime region|observed-static|
|Region4 額外 UI 欄位| `0x4B286D..0x4B2882`：UI widget **0x17**（23）→ C02 packet `+0x624`；`0x4B2887..0x4B2898`：widget **0x18**（24）→ packet **`+0x822`**；複製進 UTF16 字串緩衝|observed-static|
|Region2/3 額外 UI 欄位| `0x4B289A..0x4B28AE`：widget **0x0F**（15）→ packet `+0x624`；`0x4B28B3..0x4B28CD`：widget **0x10**（16）→ packet **`+0x822`**|observed-static|
|確認畫面會使用上述兩欄| `0x4B24E1..0x4B2509` 讀 packet `+0x624`（含 locale label ID 0x49）；`0x4B2509..0x4B2532` 讀 packet **`+0x822`** 並使用 locale label ID **0x4B**；格式化確認資訊|observed-static；label 的翻譯字串尚未取得|
|C02 的原生 serializer| `0x5742B4/0x5742C9` 寫 F1/F2；`0x5742F6` 寫 F3（writer relative `+0x618`）；`0x57430E..0x574321` 寫 **F4（writer relative `+0x816`）**；`0x574326..0x574330` 寫 flag|observed-static|
|offset 差異|writer `this` = C02 packet `+0x0C`；所以 **writer+0x816 = packet+0x822**，與 UI 控制項複製目的地址一致|observed-static；不可錯用 +0x816 作 packet base offset|
|C02 真正送出| `0x4B2360` 建確認視窗，`0x4B21E0..0x4B22A9` 確認後經 `0x4B229F` 呼叫 sender 並轉 local state `0x1D`|observed-static，native E2E 未跑|
|C04 不含此欄| `0x574420` 外觀只寫五個 u8；不能期待從 C04 還原 E-MAIL|prior observed-static cross-check|

### Wire 範例（synthetic，絕非真帳號／真郵件）

`C02 body Region4 = string8(ID) + string8(PASSWORD) + string8(NAME-candidate) + string8(EMAIL-candidate) + u8(flag)`。四個 `string8` 都是「編碼後位元組長度 u8 + bytes」，依原 Client 選定 codepage 編碼，不含 NUL；**無固定欄位 byte offset**，必須依前面三個字串的長度逐段讀到第 4 個字串。Email 若被 UI 允許送空，該字串 wire 表示為 `00`（但是否允許提交尚未知）。

不能因為同是 `opcode 0x02` 而混淆 **Client→Server C02（NewUser）** 與 **Server→Client S02（登入/創角結果）**；方向不同，body 也不同。

## 本次重跑驗證與可重現命令

`sha256sum Asgard.exe` 相同 SHA。15/15 原始位址機器碼簽章 PASS（Region2..4 dispatch、F3/F4 widget、confirmation UI 第二欄、packet+0x822、writer+0x816、writer call、尾 flag 和確認送出）。

```sh
objdump -d -Mintel --start-address=0x4B2360 --stop-address=0x4B2550 Asgard.exe
objdump -d -Mintel --start-address=0x4B2750 --stop-address=0x4B2960 Asgard.exe
objdump -d -Mintel --start-address=0x5742B0 --stop-address=0x574353 Asgard.exe
```

所有觀察均為 `observed-static`；無原 Client GUI 操作/原服封包抓取，`native_client_validation=not-run`；不能把 15 個簽章 PASS 寫成真 Client 會顯示/成功建立角色。

## 缺少的精確檔案與最後一道語意證據

原始 EXE 有實際 UTF16 檔名 **`Locale.dat`**（PE VA `0x5F1F84`），而確認畫面取當地化 label ID **0x49 / 0x4B**。要把「F4 這個欄位在原版繁中畫面是否確實印成 **E-MAIL**」由高度可信推論提升為 **observed-resource**，需提供與此版 Client 發行配對的 `Locale.dat` 並核對文字索引；若 UI 控制項/版面仍不明，EXE 也引用 `Basic.dat`（VA `0x5F1FC4`），可再用它追 UI layout。兩個檔在本次分析工作目錄均未提供，**不是說已證它們一定含最終 label**。也可由未修改原版 Client 的創角畫面/已遮蔽的 C02 四欄長度差異做最後實機對應。

**DEV handoff**：對匹配 profile、確定 Region2..4 的 C02，正式 decoder 應保留 **field4** 作 E-MAIL 候選字串（不要從 C04 取）；在 label 語意與產品規格/DB 決策確認前，不應憑推測移入角色 NAME 欄或認定 E-MAIL 必填/可空。既有 A-030 維持 `integrated/partial`，不宣稱完整 Client/Server native-ready。未改原版檔或現有 Server。
