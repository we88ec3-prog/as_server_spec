# A-030 / roy1 — C02 NAME／E-MAIL、S02 失敗對話與 C15：原版 Client 證據交接

日期：2026-11-01。工作分支 `task_a/roy1`，已與 `main` 同步；不得修改原版 Client、Server 或 DB。原始 `Asgard.exe`（PE32/x86，ImageBase 0x00400000）SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。R-025、R-026、R-035；A30-1～A30-8；CT-103/104/105/106。

**判定：原始 EXE 能證明的 Client packet / UI callback 路徑已做完，A30 = `integrated / partial`。目前仍缺 `Locale.dat` 的控制項繁中標籤對照及**未修改原版 Client** 的實機 UI/去敏 C02、S02、C15 時序，故 `native_name_email_mapping_ready=false`、`native_s02_failure_gui_ready=false`、`native_client_validation=not-run`、`implementation_ready=false`。絕不把候選字段命名或合成 S02 視為已經實機成功。**

新增證據 ID `ev_a030_20261101_native_name_email_s02_c15_strict`，獨立 Python 原始二進位驗證 40 處 native instruction bytes，包含 C02 Region、F3/F4、確認頁 label IDs、S02 status/message parser、modal callback、C15 opcode / empty writer / send、state0x1F。6 個本地 offline unit tests PASS。Repo `tools/a030_native_newuser_contract.py` 新增 26 個 S02/NAME-EMAIL 交叉簽章與 6 個 unittest case（需原 EXE 的測試在無檔環境可 skip）。原版 Client GUI、真 Server session **沒有啟動**。

## 一、Region → UI 輸入 → 實際 C02 body

原版 C02 是 **C2S opcode 0x02**，class ctor `0x574170`、`0x574189 push 02`；writer `0x5742B0..0x574352` 寫 `string8`。每字串長度為**編碼後 1 byte 長度**，後接內容，不含 NUL；絕非固定 byte offset。原版 Locale/LanguageMan 決定 codepage，TW index4 支援 CP950 測試，不應對全區域默認 CP950。

| Region | F1（候選 ID） | F2（候選 PASSWORD） | CONFIRM (local-only) | F3（NAME 候選） | F4（E-MAIL 候選） | tail |
|---|---|---|---|---|---|---|
|0|widget 1 → packet+0x24|widget 2 → +0x224|widget 3|widget 10 → +0x424（有條件清空）|**wire 無此欄**|無|
|1|widget 12 → +0x24|widget 13 → +0x224|widget 14|writer 取 +0x424，**而 UI 提交流程填 +0x624，未證 F3 的相同來源**|UI 有 widget16 → +0x822，但 writer **不送 F4**|無|
|2、3|widget 12 → +0x24|widget 13 → +0x224|widget 14|widget15 (0x0F) → packet+0x624|widget16 (0x10) → packet+0x822|u8 flag|
|4|widget 20 → +0x24|widget 21 → +0x224|widget 22|widget23 (0x17) → packet+0x624|widget24 (0x18) → packet+0x822|u8 flag|

UI 持有 C02 物件於 MakeInfoDialog+0x58；UI 本地 `0x4B27BE`（F1）、`0x4B27D6`（F2）、`0x4B27F7`（CONFIRM），`0x4B286D/0x4B2887`（Region4 F3/F4）、`0x4B289A/0x4B28B3`（其他非0 F3/F4）。writer `this=packet+0x0C`，因此 `writer+0x618 = packet+0x624`、`writer+0x816 = packet+0x822`。writer `0x5742EC` 與 `0x5742F1` 篩 Region2..4，按 F1,F2,F3,F4,u8 寫入；其他區只 F1,F2,F3。送出發生在最後確認 popup 的 callback `0x4B21E0`，`0x4B229F` enqueue `C02`，`0x4B22A9` 設 state0x1D。

**額外原證據：** `0x4B24E7` 將 packet+0x624（F3）配合 locale key **0x49** 製作確認文字；`0x4B250F` 將 packet+0x822（F4）配合 key **0x4B** 製作確認文字。**這兩個是 localization lookup ID，不是已知的英文字樣或錯誤碼。** F3/F4 不是只存在於畫面而沒有 wire。

**原生語意證據的最後界線：** 使用者明確觀察畫面順序 `ID / PASSWORD / CONFIRM / NAME / E-MAIL`，因此在有 5 欄的 Region2..4，`F3=NAME、F4=E-MAIL` 是「高度可信、適合安排資源/實機驗證」的候選，**但從目前 EXE 指令不能證明 locale key 0x49 內容是「NAME」、0x4B 內容是「E-MAIL」**。原件二進位直接搜尋並無 `E-MAIL` ASCII/UTF16LE literal，實際有 `Locale.dat` UTF16LE 文件路徑。沒有匹配版的 `Locale.dat`，絕不能把猜測當 verified native mapping、繼而寫入 Account.creation_email。Region1 的 UI/writer 差異也不能忽略。

## 二、S02 失敗真的走哪裡？C15 是否送出？

原生 S02 是**S2C opcode 0x02**（與 C02 方向不同，不能混為一談）；parser `0x57DBC0` 以 `0x45ADB0` 讀 u8 status，`0x45B7A0` 讀 string8 message。NewUser UI 收包 dispatch `0x4B2340/0x4B235B` → callback `0x4B1D60`。

1. `0x4B1DA9..0x4B1DEB` 讀 status，focus switch 覆蓋 3..31 共 29 項。**status3/4/18/26/31** 針對 UI 第1輸入欄設焦點；**status17** 針對第2輸入欄，其餘無此明確焦點效果。這**不是** server error business reason mapping。
2. `0x4B1DFF` 若 message UTF16 首字非零會進展示分支（`0x4B1E2E/0x4B1E77..0x4B1EC3`，`0x442570` 與 widget factory），**但是** local state0x1E 且 Region3 會經 `0x4B1E1E..0x4B1E21` 略過文字對話分支。若 message 空，亦不建立這段文字窗。
3. `0x4B1EE9..0x4B1EEE` 再讀 status；**非零**時 `0x4B1F1D` ctor `CCancelNewUser`、`0x4B1F2F` enqueue、`0x4B1F34` 設 local state **0x1F**，然後跳離成功路徑。C15 ctor `0x571609 push 0x15`、writer `0x5716A0: ret`，因此 **C2S C15 body 為空**；並非 S02 在 wire 上回傳 C15，也非 Client 必定自行關 TCP。
4. **status0** 才可走 `0x4B1F46` state0x1D → `0x4B2021` 建 C04／`0x4B205A` send → state0x1E；若原本 state0x1E，走 `0x4B206B` 本地完成 UI。沒有此處自動送 C03/S03 的證據。依使用者最新 ADR-008 決策，成功後應**直接進 World（無手動重登入）**；下一個真正原生 World C2S/S2C 封包由 A-028/A-031 分析，不能依本回調猜測。

### 可以給 DEV 的「靜態可走、尚未 GUI 驗收」失敗回覆

只在已合法進入 NewUser `state0x1D` 且 Client UI 上下文正確、加密/ordinal framing 有效時，*離線設計的* S02 **body**：
```
01 10 52 65 71 75 65 73 74 20 72 65 6a 65 63 74 65 64
```
= status `1` + string8 `Request rejected`（16 ASCII bytes）。status1 不在 3..31 的特殊焦點表內；依原碼能走通用文字提示、C15、state0x1F。**這只是 synthetic vector，不是原服對帳密錯、重名、停權的既定 status，不是已實測成功顯示，也不代表目前 Server 已實作或 Socket 會存活**。

|Response / local context|原生靜態 UI 路徑|Client outgoing|後續狀態|實機是否驗證|
|---|---|---|---|---|
|state1D，S02(1,非空字串)|通用文字 dialog 建構路徑（沒有特殊焦點）|C15 empty|0x1F|未執行|
|state1D，S02(3,非空字串)|dialog + 第1欄 focus|C15 empty|0x1F|未執行|
|state1D，S02(17,非空字串)|dialog + 第2欄 focus|C15 empty|0x1F|未執行|
|state1D，S02(1,空字串)|不建文字 dialog|C15 empty|0x1F|未執行|
|state1E，Region3，S02(1,非空)|文字 dialog 被 suppress|C15 empty|0x1F|未執行|
|state1D，S02(0,任意)|成功第一階段→C04|C04 5×u8|0x1E|未執行|
|state1E，S02(0,任意)|成功第二階段本地 UI|無必然 C03|後續 UI 路徑|未執行|

**C15/TCP 分界**：Client `C15` 發出後 socket 保留與否，取決於 **Server 處理**、後續 callback、斷線/異常；目前 DEV/Client E2E 無證據可聲稱「不斷線」或「可直接重試」。既有 Server source 曾在 C02/C04/C15 直接 Close，該行為不是原版 Client 自行決定。測試要記兩邊時間戳、C15 後是否有 Server TCP FIN/RST、是否可重新送新 C02。

## 三、交付 DEV 的最小合法範圍與阻塞

- **已可採用的 wire**：Region2..4 C02 F1/F2/F3/F4/u8 body，Region0/1 C02 F1/F2/F3；S02 status+message; C15 zero-body；成功 C02→S02(0)→C04→S02(0) 的 Client 本地轉場；nonzero S02→可能提示→C15/state0x1F。
- **尚不可宣告原生可用的語意**：真正 NAME/E-MAIL label→widget、Region1 第3欄來源、EMail 是否必填/可空、原版特定錯誤 status semantics、未改 Client popup/render、C15 後 retry/是否維持同 TCP、依 ADR-008 成功直接進 World 的原生封包與 Client 下一個狀態。
- R-035 產品已決定**建立角色成功後，只將 E-MAIL 保存於 Account，沒有其他用途**；但 Server 必須等 REGION/profile/原生 label mapping 真正通過，才把 F4 解釋成 creation_email，不能把 F3 寫為 email。DB commit 和認證屬 DEV，不是 A30 客戶端實證；此輪沒有修改 Server/DB。
- **缺少的確切原件**：`Locale.dat`（EXE 0x5F1F84 原字串，需 matching release，resolve localization keys 0x49/0x4B）；`Basic.dat`（EXE 0x5F1FC4 原字串，供必要時核對 UI layout/widget identifiers）。**可能還需對應 GUI 皮膚內的具名 layout 成員，名稱須等資源解析後再指認，不猜。**
- **CT-104 P0 必要補證**：1) 未改 Client 原始 SHA、region/locale／UI 五個標籤→widgets；2) 不洩露明文的 F3/F4 長度比較：只改 NAME、只改 E-MAIL、E-MAIL 留空；3) 真正在已進 state1D 以正確加密/序號送 S02(nonzero,非空) 並截畫面、C15 帧/ordinal、Socket close origin，包含 Region3/state1E 例外；4) 第二次 C02 及重登入可否使用，分開記。
- **CT-103/105/106**：由 DEV 另驗 C02 不無故關線、成功第一／第二段 S02+ C04 後 durable Character、E-MAIL 同 transaction，C15／錯密/重名/停權 rollback、重送/重登入無重複。**沒有完成任何真 Server DB E2E**。

## 四、重現指令／測試

```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x4b2360 --stop-address=0x4b2569 Asgard.exe
objdump -D -M intel --start-address=0x4b2764 --stop-address=0x4b2918 Asgard.exe
objdump -D -M intel --start-address=0x5742b0 --stop-address=0x574353 Asgard.exe
objdump -D -M intel --start-address=0x57dbc0 --stop-address=0x57dbdf Asgard.exe
objdump -D -M intel --start-address=0x4b1d60 --stop-address=0x4b217a Asgard.exe
objdump -D -M intel --start-address=0x5715f0 --stop-address=0x5716a1 Asgard.exe
python tools/a030_native_newuser_contract.py
```

本地 EXE 原件雜湊 PASS、40/40 追鏈簽章 PASS、6 個針對本次證據的 offline unit tests PASS；新增工具嚴格簽章 26 處與 6 個測試。若沒有 EXE 檔，工具須 skip native signature 而非導致 CI 因缺遊戲私有素材失敗。不要在 Git 提交 EXE、Locale、Basic、原始帳密、EMAIL、整份解密 C02 或包含敏感值的擷取。
