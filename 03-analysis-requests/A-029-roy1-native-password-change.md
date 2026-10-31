# A-029 / roy1 — 原生改密碼 UI、C26 與 S02 回應（BIN-first）

2026-10-31；工作分支：`task_a/roy1`（fast-forward `main@6bdd13130348b2d59263da7cf598eb2f5a624bf4`，無建立新分支）。原件：`Asgard.exe` PE32 x86，ImageBase `0x00400000`，3,235,840 bytes，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。新證據 ID：`ev_a029_20261031_native_c26_password_change_static`。R-025/R-032，A-002/A-027/028 依賴。

**研究交付**：已由 EXE RTTI、UI event、native writer 與 S02 shared dispatcher 完成可核對的 **Client trigger→C2S→S2C→Client reaction**，新增合成 codec / 原件指令測試與 CT-098/099 執行指引。A gate 為 `integrated/handoff_status=partial/native_client_validation=not-run`。**C26 帳號/舊密碼/新密碼 codec 可開發**，但原版 S02 成敗 status 針對改密碼的實際語意、登出/停權/跨 regional UI 在無原版原服抓包與 native GUI 之前仍 unknown，**不宣稱完整原生 E2E 已驗收**。不修改 Client、不新增自訂 opcode、不實作 Server 或資料庫。

## 1. 入口與欄位（observed-static）

- EXE RTTI `.?AVCChangePasswordPacket@@`、原 source 字串 `packet\\cchangepassword.cpp`（ASCII/UTF16LE）實際存在；其 vtable `0x61377c` 被 `0x571a3c` 安裝。建構器 `0x571a10` 的 `0x571a29: push 0x26` 交給 `0x578600`，**原生 C2S opcode = 0x26（PKT-C26）**，不是猜的。
- `LoginDialogPane` 相關 UI callback `0x4a8950` 依 `event_code-4` jump table `0x4a8d34` 切分；**event_code=12**（table index8）在 `0x4a8a81` 進入改密碼送出路徑，`0x4a8ab1` 直接 new `CChangePasswordPacket`。**event_code=13**（index9，`0x4a8d27`）則轉 `0x4a87b0` 重設/關閉 UI，這一路沒有建立 C26。原版 UI 有在此對話窗的原生操作路徑；主選單精確中文標籤、能否在已進世界後呼叫，未經 GUI 確認，不能臆測。
- 按提交時，依序從 UI controls **8、9、10** 經 `0x441070→0x434cc0` 複製入 packet 三個 string buffer：control8→物件 `+0x24`（account 候選），control9→`+0x224`（舊密碼），control10→`+0x236`（新密碼）；**control11 是再次輸入的新密碼確認欄**，`0x4a8b23` 複製到 stack local，**不寫入 C26 packet**。原欄位畫面文字是目前推定而非 native GUI 截圖。
- `0x4a8b33/0x4a8b39` 以 UTF16 原樣比較 control10 vs control11（`0x5b4a62` 是逐字 UTF16 字串比較），不一致走提示分支 message index `0x4d`，未送 packet；一致則於 `0x4a8bf2/0x4a8bf4` 比對 control9（舊）與 control10（新），一樣則走提示 message index `0x5d`，也未送 packet。兩者不同且確認一致才 `0x4a8c73`→`0x4a8d05` 呼叫 `0x5788a0` enqueue C26。**沒有本地檢查原密碼是否真的正確**；必須由 Server 驗證。
- `0x4a9581..0x4a95e4` 控制項9、10、11 均 `push 8` 經 `0x434c50→0x54a9e0` 將 UI widget 欄 `[+0x108]` 設為8（native 8 字上限配置的靜態證據）。這個 callback **未見** 4字最小長度、ASCII 英數限定的獨立 predicate；**4～8 ASCII 英數仍由 Server product policy enforce**，不要誤稱所有 client language/region 都已證同樣限制。control8（帳號）是否可編輯、預填、大小寫規則及每 region 的字元接受集合待 GUI 追查。

## 2. C→S 真正的 0x26 writer

`0x571ac0` 為原生 serializer；呼叫 `0x45b1b0` 共三次，對象分別 `[esi+0x18]`、`[esi+0x218]`、`[esi+0x22a]`，每次先由 `0x5b4acd` 取 UTF16 code-unit 長度，再送 UTF16 buffer；`0x45b1b0` 以全域 codepage 轉為 `string8`：**u8(編碼後 bytes 長度) + bytes，不含 NUL**；本 packet **沒有 subtype、沒有第四個確認欄、沒有單獨 token/nonce**。Endianness 對三個字串長度不適用。index4 語系時 CP950；其他語系 codepage 不能從 EXE SHA 假定固定。

|body offset|格式|資料來源/語意|
|---|---|---|
|0|account:string8|UI control8，登入畫面第一欄／帳號候選；仍需 native UI 文字核實|
|1+len(account)|old_password:string8|UI control9|
|2+len(account)+len(old)|new_password:string8|UI control10|
|無|confirm|UI control11 **僅本地相等比較**，不會在 C26 body|

合成向量（純虛構帳密、**非原服封包抓取**）：

```text
C2S opcode: 26
body: 06 546573743031 06 4f6c64313233 06 4e6577343536
        Test01          Old123         New456
```

此例的三個 encoded byte lengths 均為 6。沒有把 packet framing/encryption/ordinal 夾入 body；以既有 Server packet framing 架構處理。不可以拿 C03 或 C02 改造為改密碼訊息，更不可新造 Client opcode。

## 3. S→C 回覆及原 Client 表現

`0x4a9670` 接 LoginDialogPane 中 packet/event object，於 `0x4a967a` 依 `packet->header_or_class[+8]` selector 0..0x68 跳轉；**selector 0x02** 由 `0x4a968d→0x4a9694` 轉 `0x4a8d60` callback。對應既有 **PKT-S02**（已由 A-002/A-028 獨立研究）；其資料 reader `0x57dbc0` 及格式 `u8 status, string8 message` 依主線 packets.json。此 UI callback `0x4a8da2` 取 `[ebp+0x24]` 的 status byte，`0x4a8da6` 允許 0..0x23、`0x4a8daf` 分類多個狀態：
- status0：`0x4a8dbd` 分支依 UI control7 的現有狀態而 `0x4a87b0` 重設 UI，或轉另一個登入畫面狀態（`0x4a8dca..0x4a8dee`）；**不能推導 status0 必然代表 C26 改密成功**，因同一 S02 handler 也服務登入/創角。
- status1、2、3：`0x4a8df0`、`0x4a8ead`、`0x4a8e20` 選 UI focus/state，受 region/控制項狀態影響；不能直接將其中一個認作錯舊密碼。
- status4/5：`0x4a8eb6/0x4a8f3e` 進入通用 message presentation；`0x4a8e3f/0x4a8e85` 能組翻譯 label offset，但 **哪個 status 是改密碼成功/失敗，未見原服對應封包**。
- status 0..0x23 之外走 default；錯密、帳號不存在、被停權、重送/斷線等具體 UI 文字/Focus/是否退回原畫面須原 Client + 原服/新 Server 可控 S02 測試，不能從 generic callback 猜出。

不能把回覆包的 S02 status 語意當成 Server 已知的「改密成功」保證；正式 Server 回包狀態選擇必須與 CT-098 的 native Client 行為對齊，避免向 Client 回錯誤的成功動畫/轉頁。

## 4. 失敗/取消、攻防與 DEV/CT 交接

|情境|已觀測 Client|Server-design 要求（不當作原服證據）|
|---|---|---|
|確認欄與新密碼不同|本地比較不相等 → message 0x4d；無 C26|Server 收不到此操作；不可寫 DB|
|新舊密碼相同|本地比較相等 → message 0x5d；無 C26|若惡意直接送 C26 也應依自訂 policy 拒絕|
|舊密碼錯、帳號不存在、停權|C26 三字串，但原服 S02 status/顯示 unknown|驗帳號+原密碼/ban/速率限制，不變更帳角；統一公開錯誤，不洩露帳號存在性|
|成功|C26 C→S 可確認，回 S02 generic handler 可確認；原生成功文字未實機|同一 Account credential hash/version 原子更新；舊 grant/預建身份授權無效、角色/進度保留|
|取消|UI event13→0x4a87b0，不在此分支建 C26|不得有 credential 變更|
|重送／同時兩端／斷線|原生網路重送與 commit outcome **unknown**|防重/衝突判定、交易一致性與去敏 audit；不可在 TCP 斷線時主張舊密碼一定有效|

**需要的原件／非檔案證據**：本輪 **不缺** `Asgard.exe`；也不需要地圖或 Born 資源。要將原版 UI 各 status 的語意從 partial 提升到 ready，請取得同版本 **native Client 按實際 UI「進入/取消/舊密碼錯/改密成功/停權」的去敏雙向封包 trace + 遮蔽帳密的畫面/選單截圖**，以及原服對 C26 的 status 映射（伺服器 handler 或記錄，確切檔名未提供、不可虛構）。分析需求不要求使用者交出明文密碼；任何 packet capture 必須遮蔽或僅保留欄位長度與狀態。

## 5. 驗證、可重現

```sh
sha256sum Asgard.exe
objdump -d -M intel --start-address=0x571a10 --stop-address=0x571b0c Asgard.exe
objdump -d -M intel --start-address=0x4a8950 --stop-address=0x4a8d40 Asgard.exe
objdump -d -M intel --start-address=0x4a8d60 --stop-address=0x4a8fc8 Asgard.exe
objdump -d -M intel --start-address=0x4a9670 --stop-address=0x4a96c4 Asgard.exe
python tools/a029_password_change_contract.py /absolute/path/Asgard.exe
```

本輪已在原始 `/mnt/data/Asgard.exe` 離線 PASS：SHA256、RTTI、UTF16 source-path、**19/19 EXE x86 native signatures**、三欄 synthetic body vector。工具另包含 14 個標明 synthetic/designed 的 unittest；提交工具不等於原 Client GUI 已執行。CT-098 native UI/failed status 與 CT-099 設計的 Server transaction/多 session 仍 `planned/not-run`；不把 CT-098 的操作者密碼存在測試日志。

**A gate**：`integrated`；`handoff_status=partial`（真正 native C26 wire ready，回 S02 的 status-to-success 尚未確認）；`native_client_validation=not-run`；`native_password_change_e2e_ready=false`。現有三入口一致性政策不改。
