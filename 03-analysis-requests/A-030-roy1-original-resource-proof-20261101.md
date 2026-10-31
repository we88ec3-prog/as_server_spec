# A-030 2026-11-01 — 原始 Basic.dat 確認 NAME/E-MAIL 真實 C02 來源與 S02/C15 原生分支

**來源分級：原始資源 + 原始 x86 EXE cross-reference（已完成）、純離線合成 S02 測試（已完成）；未修改原版 Client GUI/TCP 實機 E2E（未執行）。** 對應 A-030、R-025/R-026/R-035、CT-103/104/105/106；提交至既有 `task_a/roy1`。無原始遊戲素材隨 Git 公開。

## 一、固定原件

|原件|SHA256|用途|
|---|---|---|
|`Asgard.exe`|`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`|MakeInfoDialog / C02 writer / S02 parser / C15 constructor 和 sender|
|`Basic.dat`|`0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`|實際 NAME、E-MAIL 原版繁中語系字串，Archive resource|
|`Locale.dat`|`813f2800696555f16ec6c4bfc5975b649332340b5a6975d7aeba4c4e77380161`|本檔含 `Servers.txt`、伺服器清單；**不是** NAME/E-MAIL 文字表|

`Basic.dat` 結構是 `u32LE entry_count=39, u32LE metadata, array[39](char filename[32],u32LE member_end_offset)`；每個資源的開始位置是**前一筆**的 end_offset，不是檔名當筆 end_offset。本次離線抽取並解析 UTF-16LE BOM 文字，沒有修改來源：
- `BasicString.txt`：**[0x2E97C, 0x32356)**，解碼是 `#Chinese` / `Language 3`，key **72 `ID`**、**73 `NAME`**、**74 `身份證字號`**、**75 `E-MAIL`**、25 `E-Mail地址錯誤，請重新輸入。`。member SHA256 `fa92f7a3cf544ff9e141d98620943b362e2d3dcc6e327878a818ebaa6ac3123b`。
- `SkinString.txt`：**[0x3CCBC9, 0x3CF08D)**，UTF-16LE BOM，`Language 3`；keys **2150 `角色名稱`、2151 `密碼`、2152 `確認密碼`、2153 `名字`、2154 `E-Mail`**。member SHA256 `7ba039919300dccf595fc5f4e6d79156b8b96c23a56fa3118d1e55847f199c`。
- `Locale.dat` 不含 `BasicString.txt`、`SkinString.txt` 這些字串表；過去要求單獨靠 `Locale.dat` 解決 NAME/E-MAIL 標籤屬不完整判斷，**此處以 Basic.dat 原始文字與 EXE cross-reference 更正**。

## 二、已證的 NAME/E-MAIL 原生資料流（Region 2～4）

|原版位置 / Region|NAME|E-MAIL|
|---|---|---|
|Region 2、3 表單|widget **0x0F**（15）|widget **0x10**（16）|
|Region 4 表單|widget **0x17**（23）|widget **0x18**（24）|
|MakeInfoDialog 複製到 C02 packet 基址|**packet+0x624**|`packet+0x822`|
|C02 serializer 的 this 指標（packet+0x0C）|`this+0x618`|`this+0x816`|
|Writer order|第 **3** 個 string8|第 **4** 個 string8|
|確認視窗呼叫 `0x498010` lookup|**0x49**（decimal 73 → `NAME`）|**0x4B**（decimal 75 → `E-MAIL`）|

**可精確核對的 x86：** `0x4B2877/0x4B2896` region4 widgets、`0x4B28A3/0x4B28C2` region2/3 widgets，`0x4B24E7: add eax,0x624` → `0x4B24ED: push 0x49` → `call 0x498010`；`0x4B250F: add edx,0x822` → `0x4B2516: push 0x4B` → 同 lookup；`0x5742F6` F3 serializer、`0x57430E` F4 serializer、`0x574321` 真 string8 writer，`0x4B229F` confirm/send `C02`（C2S **opcode 0x02**）。

因此先前 A-030 的 `F3=NAME/F4=E-MAIL 僅 inferred` **已被此版原始 Basic.dat 的標籤 ID + EXE 確認頁 xref 正式提升為 `observed-resource-and-static`**。適用區域**明確限 Region2～4**，不代表 Region0/1 同版映射：Region0/1 writer 只送 3 個 string8；Region1 GUI extra widgets 與 writer 取的第3字串 offset 仍有差異。CONFIRM 在原 Client 本地比對 F2，沒有第5個 password confirmation wire string。

**注意：** `SkinString.txt` 的 `2150 角色名稱` 與確認頁 `72 ID` 都是原件文字；不能因此將 C02 F1 自動視為 Server 已建立的 Account identity 或新建 Account 的授權憑證。原 Client 可呈現的欄位名不是新 Server 的 owner 驗證；須走本次 C02 的帳密 verifier/creation-only proof/ACL。這項 A-027 的安全疑點仍由 Server 負責。

## 三、S02 失敗文字與 C15 的可證行為

- `S02` 是 **S2C opcode 0x02**（不同於 C2S `C02`），reader `0x57DBC0` 讀 `u8 status, string8 message`。MakeInfoDialog callback `0x4B1D60`。
- `0x4B1DA9..0x4B1DEB`：非零 status 的 focus mapping：3/4/18/26/31 → 第一欄，17 → 第二欄，其餘沒有該特別 focus；**這不是原服「錯密／重名／停權」status 意義的證明**。
- `0x4B1DFF` 檢查 `message[0]`，若非空會進 `0x4B1E77..0x4B1EC3` 的 native dialog 建構並將 S02 的 message 字串傳入 `0x442570`；只有 **Region3 + state0x1E** 在 `0x4B1E0D..0x4B1E21` 跳過文字 dialog；空字串也不產生此文字提示。
- `0x4B1EE9..0x4B1EEE` status!=0：`0x4B1F1D` 建 `CCancelNewUser`；ctor `0x5715F0`（opcode `0x15`）+ empty body serializer `0x5716A0`；`0x4B1F2F` enqueue `C15`，`0x4B1F34` local state **0x1F**。**Client 發出 C15 不表示原 Server 必定維持 TCP 或 Client 已可同連線重新送 C02**。
- `status=0` in state0x1D → 原生送 `C04` 五個外觀 u8、轉 0x1E；state0x1E 的 status0 → `0x4B206B` 本地成功路徑。依最新 **ADR-008**，Server 必須安排**建角後直接進 World、不回登入、不再手動 C03**；新 World 協定/安全 grant 另依 A-028/A-031，不可從 A30 猜測。

**合成失敗候選，不是原服 status 實測：** 在已處 state0x1D 且 framing/加密有效時，`S02 body = 01 10 52 65 71 75 65 73 74 20 72 65 6A 65 63 74 65 64` 即 status=1 + string8 `Request rejected`，靜態可走 generic message dialog + C15(empty)。由於此輪沒有在 Windows 原版 Client 實際注入／看到畫面，**只能宣告原始程式碼能走這條提示路徑，不能宣稱「已實機正確顯示」或此碼屬官方錯密錯誤碼**。Server 一般認證失敗不應靠 Socket 無理由 Close 冒充回覆；要以實機隔離環境對應 status/error/UI/C15/TCP。

## 四、A-030 交付與剩餘驗收

- **完成且可給 DEV 的 A30 核心**：Region2/3/4 真實 NAME/E-MAIL → C02 F3/F4 的雙來源交叉證據，S02(status/message) 非零文字 dialog path、C15 empty 發送/state0x1F、成功兩階段；不造新封包。不更動 Client/Server/DB。
- **R-035 已定**：E-MAIL **只在 C04 建角成功的同一個 DB transaction** 寫入同一 Account 的 `creation_email`，無其他用途；是否為空依原 Client UI gate，**不可從文本「E-MAIL」證明非空必填**。
- **仍待真 Client / Server E2E**：實際執行所選 region、空 E-MAIL 是否能發 C02、S02 status1/text 在原版 Windows GUI 是否如預期顯示及焦點、C15 後 TCP 是否保持/能 retry、完成後直接入圖，以及官方錯密/停權/重名失敗 status 對應。若沒有實測，不標 `native_client_validation=passed`。
- **檔案狀態**：`Asgard.exe`、`Basic.dat`、`Locale.dat` 現已齊，**目前沒有為靜態分析而缺的檔案**。Win32 GUI/本機測試 Server 與遮蔽帳密的 trace 屬**動態驗收環境與證據**，不是缺另一個可猜的檔名。

## 五、可重現驗證

`python tools/a030_resource_labels.py` 使用上面三份原始檔的 hash，解析 Basic archive end-offset/UTF16LE、檢查兩份字串表各 key 與 EXE 26 處機器碼指令；另含不需原件的 synthetic archive/codec 負面測試。原件不在 checkout 時原件驗證應標 `skipped`，不能偽稱 PASS；這輪本機 **7 unittest PASS、26/26 x86 anchors + 三份 SHA256 PASS**。完整報告不含真帳密／郵件內容或原遊戲素材；禁止把原 EXE/DAT 或 UI sprite 原件提交進 Git。
