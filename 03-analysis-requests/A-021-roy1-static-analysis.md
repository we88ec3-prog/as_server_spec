# A-021 — roy1 / 原版 Asgard.exe 首次創角靜態追查

- 日期：2026-10-31（Asia/Taipei）
- 分支：`task_a/roy1`；基線：main `463e6e242a33e2dc4fe81b5a8df2622ac8410651`
- 目標：R-002、R-003、R-025、R-026；相關 A-002、A-003、A-020
- 原版樣本：`Asgard.exe`，PE32 / x86，ImageBase `0x400000`
- **SHA-256：`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`**
- Profile：`TW-seed0-local-v0.1`（既有規格基線；本次無實機確認當前 region 設定）
- 證據：`ev_a021_20261031_asgard_static`；分類 **observed-static**。本次為 PE/組語靜態檢查，**沒有原 Client 實際連線、畫面或封包抓取**。
- 任務狀態：**integrated（靜態研究及明示相容策略已整合；Client CT 尚未執行）**。nfo 建構時傳 `opcode=0x04` | observed-static |
| `0x574420` | C04 從內部 `+0x18..+0x1c` 順序寫出五個 u8 | observed-static |
| `0x57DBC0` | S02 parser：`0x45ADB0` 讀 status u8 到物件 `+0x18`；`0x45B7A0` 讀訊息至 `+0x1a`（最大 0xff） | observed-static |
| `0x4B21E0` | MakeInfoDialog 相關 UI callback；事件碼 1 分支 | observed-static |
| `0x4B229F` | 傳送對話框 `[+0x58]` 持有的封包（C02 路徑），`0x4B22A9` 設內部狀態 `0x1d` | observed-static |
| `0x4B1D60` | S02 相關 UI callback；讀狀態位元組及訊息，依對話框階段決定後續 | observed-static |
| `0x4B1F46` | **收到 status=0** 且對話框狀態為 `0x1d` 時，進入建立 C04 的分支 | observed-static |
| `0x4B2031..0x4B2055` | 從 UI 選擇值取得性別、髮型；從 `0x66422c` 配色表投影 RGB | observed-static |
| `0x4B205A` | 傳送 C04，`0x4B205F` 將對話框狀態設為 `0x1e` | observed-static |

原生偵錯字串：`.\\packet\\cnewuser.cpp`、`.\\packet\\cnewuserinfo.cpp`、`.\\packet\\scheck.cpp`、`.\\MakeInfoDialog.cpp`。名稱是追查線索，不直接構成「這是建立 Account 還是 Character」的證明。

### 最小組語摘錄（可用本 SHA 核對）

```asm
5742ec: cmp eax, 0x2
5742ef: jl  0x574338
5742f1: cmp eax, 0x4
5742f4: jg  0x574338
574330: call 0x45ab00        ; branch 2..4 尾部 byte
57434b: call 0x45b1b0        ; 其他 branch 的第三個 string8
574423: movzx eax, byte ptr [esi+0x18]
574428: call 0x45ab00        ; C04 共五個 byte writer
57dbc3: call 0x45adb0        ; S02 status
57dbd8: call 0x45b7a0        ; S02 message
4b1f46: cmp dword ptr [esi+0x4c],0x1d
4b205a: call 0x5788a0        ; UI 發送 C04
```

## 2. 封包欄位（body，不含 frame/opcode/ordinal/加密）

### C02 / NewUser（`0x5742B0`）

1. 固定先寫 `string8 field_1`（packet 內部 +0x18）與 `string8 field_2`（+0x218）。
2. 透過 `0x66D0D0 → 0x498000` 得到分支代碼 `region_code`。
3. **若 `2 <= region_code <= 4`**：再寫 `string8 field_3`（+0x618）與 `string8 field_4`（+0x816），最後 `u8 flag`（+0xA16）；合計 **4×string8 + 1×u8**。
4. **其他代碼**：只再寫 `string8 field_3`（+0x418）；合計 **3×string8**。
5. 只確認欄位的 **序列化順序及寬度**，field_1..field_4 的帳號/密碼/暱稱/確認欄位語意仍須從 edit-control 綁定或原版 UI 實測獨立驗證。不能直接將此「NewUser」視作原 Client 已登入的 CreateCharacter。
6. `string8` 的長度是單位元組「轉碼後 byte 數」；既有 transport 指定 CP950 profile。需要額外驗證實際 region code、空字串、長度超限、不可編碼字元與拒絕行為。

### C04 / NewUserInfo（`0x574420`）

確證 **固定五個 u8**，依序為 UI 的 `sex, hair, color_r, color_g, color_b`（前二個 UI 值與 RGB 配色表來源於 `0x4B2031..0x4B2055`）。目前可證明封包欄位形狀，不可據此推得合法髮型/性別集合或 Server 的建角提交時點。

### S02 / SCheck（`0x57DBC0`）

Body 是 **`u8 status, string8 message`**。S02 是多階段共用回覆，不能把登入的 status=3 錯密推論為 C02/C04 的同一錯誤意思。創角 UI 針對 status=3..31 使用跳表，其中觀察到 3、4、17、18、26、31 對不同提示路徑有分派；數值的正式意義仍未完整證明。status=0 在 MakeInfoDialog `0x1d` 階段可驅動 C04；在其他階段的後續轉場不可預設完全相同。

## 3. 已知本地控制流程及未證明的 Server 端語意

```text
MakeInfoDialog UI（何時顯示、是否預建帳號可觸達：UNKNOWN）
  └─ 事件 1 → C02（0x4B229F）→ local_state 0x1d
       └─ S02 (0x57DBC0 parse；0x4B1D60 UI callback)
            ├─ status!=0 → UI 顯示/錯誤分支；重試 policy 未全解
            └─ status==0 且 state==0x1d
                 └─ C04 (0x4B205A) → local_state 0x1e
                      └─ 後續 S02 / S03 / 重登 / 角色保存：UNKNOWN
```

**這不是「已預建帳號成功建角」的 runtime trace。** 尚未確認：
- 原 Client 在 `C03` 登入 **已由管理員建立但角色數為 0 的 Account** 後，是否進入 MakeInfoDialog，或先進其他登入/註冊分支。
- C02 的 4 個字串各自真正語意，是否包含「新帳號註冊」而不是「僅建立角色」；Server 不得從未授權 Client 訊息建立 Account。
- 完整成功/取消/失敗狀態表、C04 後是否需要再 S02、如何取得 S03 與一次性 World token、是否重新登入。
- 同名、並發、timeout、斷線、回包遺失、重送與 Server crash 後的原生可見效果。
- 顯示的角色屬性合法集合、Server 持久化的不可逆提交點、後續第一次 World 入口。

## 4. R-025 的不得違反界線

已確認的**需求**：只有管理後台可 `ProvisionAccount`，玩家 Client 僅登入已存在帳號。C02 的「NewUser」與建帳語意仍屬 **unknown**。Server 不可實作「任何連線送 C02 即新增 Account」；在缺乏**已預建帳號、憑證認證、正確 pending 階段與角色 owner** 時必須拒絕 C02/C04 的 Domain 寫入。C02 可以位於 C03 之前，不能要求「已登入 C03」作為唯一授權途徑。這是本專案的 **designed** 安全政策，並非原版 Client 原始行為已實測。

可將 `C02` 建模為只認領已由後台建立的帳號，並開啟 `PendingCreateHandshake`（僅狀態暫存、不建帳），C04 再一次性提交 `CreateCharacter`；這是 designed 相容策略。角色最終寫入需以帳號/角色唯一約束、交易及冪等控制，絕不可只憑一次正常 static path 定稿。

## 5. 合成 codec 向量（非 Client 實測）

- region_code=2..4, 四個 ASCII 單字元欄位 `a,b,c,d`, flag=1：**C02 body = `01 61 01 62 01 63 01 64 01`**。
- 非 2..4, `a,b,c`：**C02 body = `01 61 01 62 01 63`**。
- C04 (sex=1, hair=2, R=0x11,G=0x22,B=0x33)：**body = `01 02 11 22 33`**。
- S02 (status=0, 空訊息)：**body = `00 00`**。

以上僅根據靜態 writer/parser 與 string8 規則推導的**測試合成值**，不能當成抓包；更不能由此宣告相關 CT passed。

## 6. 下游 Client CT 測試清單（不是 A 靜態分析停止條件）

1. 使用上述 SHA 的**未修改**原版 Client、完整原生資源、獨立測試後台與測試用伺服器。預建 `Account`，確認其 `CharacterCount=0`，且 Client 不能透過任何封包建立 Account。
2. 記錄 C03 認證前置、S02/S03 回應，觀察是否**自動進入**原生 MakeInfoDialog；對照 `0x4B21E0` / `0x4B1D60` handler 的動態斷點。
3. 正常 UI 填入可識別合成欄位，捕獲 C02、S02、C04、其後所有回應（僅存去識別摘要）。同時查 region 值，建立欄位-UI 對照及 status 表。
4. 分別測：取消、空/非法值、重名、已存在帳號新角色、C02 重送、C04 重送、C02→C04 中途斷線、C04 ack 丟失、同帳號兩 Client、重登。檢查角色/owner/外觀只提交一次。
5. 在有效帳號但無 Session、停權帳號、未管理建帳的帳號測試 C02/C04 拒絕，保證 Account 沒有變更。
6. 確認創角完成是直接 S03/C10 轉 World 或重新登入，將時間順序及後續 S02/S03 的每個狀態碼、畫面效果登錄；更新 SCN-008、PKT、CT-011..014/018/019。
7. 另一位分析者根據 SHA/VA 複核，再由規格負責人審查，作為後續 CT/BUG 回饋，不能阻止 A 靜態分析整合。

## 7. 重現命令、可信度與邊界

本檔記錄的是與目標 SHA 綁定的 PE32 原始位址；在 Linux 可用：

```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x574170 --stop-address=0x574460 Asgard.exe
objdump -D -M intel --start-address=0x57dbc0 --stop-address=0x57dbe0 Asgard.exe
objdump -D -M intel --start-address=0x4b1d60 --stop-address=0x4b2370 Asgard.exe
objdump -D -M intel --start-address=0x45b1b0 --stop-address=0x45b280 Asgard.exe
```

- x86 位址為 VA（image base 0x400000）；不可當作 file offset。
- 原版 EXE、本機解碼素材、帳密/token、原始巨大反組譯不入共享 Git。
- 只有此處列出及可重現的靜態路徑是此次**新增證據**；先前 profile 規格與人工登入正常路徑不可擴大成首次建角實機成功。
- 本次單檔靜態分析已交付；A-021 已可由靜態證據與設計相容方案供 Server 開發；沒有宣稱 Client 實測或「C03 後自動進 UI」已確認，詳見 [後續深入追查](A-021-roy1-followup.md)。
