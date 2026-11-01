# A-028／roy2 — C04 第二段 S02 成功後的 UI／背景 World 入口再追查

- 日期：2026-11-01；原版原件：`Asgard.exe` PE32/i386，ImageBase `0x400000`，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
- 依據：[Roy1 A-028 原先分析](../../03-analysis-requests/A-028-roy1-c04-terminal-analysis.md)、[ADR-008 直接入 World 決策](../../02-server-planning/post-create-direct-world-decision-20261101.md)、A-021/A-027/A-030、[A-031 Region3 C10/C25 靜態證據](A-031-analysis.md)。
- **重要區隔**：使用者確認的成功創角後**直接進入遊戲、不需再次手動登入**是現行產品需求／觀察；本次可靜態證明 UI 清理與 Region3 特定 dialog 重建，**不能從單一 callback 斷言會自動發 C03、S03/C10 或已進 World**。`native_client_validation=not-run`。
- 工作分支 `task_a/roy2`；原件無修改、未在 GitHub 上傳任何遊戲 binary。同步 main 後驗證，無新增 branch。

## 一、從 C02→C04→最終 S02 的原版程式追蹤

|Client 當時狀態、收到封包|original opcode／native VA|確定事實|
|---|---|---|
|MakeInfoDialog state `0x1d` 收 **S02(status=0)**|`0x4B1F46` state guard；`0x4B2031..0x4B205A` 產 C04；`0x4B205F` 寫 state `0x1e`|第一段 S02(0) **只證明 Client 送出五個 u8 的 C04**，不能認為此時 Server Character 已 commit|
|state `0x1e` 收 **第二段 S02(status=0)**|`0x4B1F46 → 0x4B206B`|進入成功的 UI 完成分支；**沒有直接 C03/C10 sender 或 new TCP ctor 位於這個函式切片**|
|state `0x1d` 或 `0x1e` 收 **S02(status≠0)**|`0x4B1EEC` 判 status；`0x4B1F1B` C15 ctor；`0x4B1F2F` send；`0x4B1F34` state `0x1f`|Client 送 **C15 空 body** 並切換本地失敗/取消狀態；不是 Server DB rollback 證據|
|state `0x1e`、**Region3**、文字訊息非空|`0x4B1E0D..0x4B1E21`|message/modal path 被略過，但非零 status 仍進 C15；不能推導為 Region3 的成功或放行|
|其他 local state、收到 S02(status=0)|`0x4B1F46` 的 `jne`|也會進 `0x4B206B`；**此成功分支不能單獨證明前面必定有合法 C04 或角色提交**|

S02 讀取為 `u8 status,string8 encoded message`，native parser `0x57DBC0`；C04 writer `0x574420` 五 u8；C15 `0x5715F0` constructor push opcode0x15／`0x5716A0 ret` body0。status3/4/18/26/31 focus 第一個輸入、17 focus 第二個，其餘 default，**不代表原版 status 的文字錯誤語意**。本次沿用 Roy1 已證內容，不重複將登入錯密 status3 移植到建角失敗。

## 二、新發現：final S02 success `0x4B206B` 的全部可見 UI 動作

已重新反組譯 `0x4B206B..0x4B217A`，可稽核：

1. `0x4B206B` 讀 MakeInfoDialog `+0x26C` 的 widget handle；`0x4B2084` 呼叫 `0x441070`，`0x4B208B` 再呼叫 `0x434CC0` 對這個 UI 物件執行本地操作（精確可見標籤未證）。
2. `0x4B2090/0x4B209B/0x4B20A6` 依序以 index `0x0C/0x0B/0x0D` 呼叫 UI manager `0x535510`，並傳入 flag=1；`0x535510` 會對 `[manager+0x1100+index*4]` 做 release/清零。**這是三個 UI 槽的清理，不是帳號/角色或網路 session 的刪除。**
3. `0x4B20B1` 以 index `0x07` 呼叫 `0x5354B0`，後者釋放 `[manager+0x11B8+index*4]` 並清零；也是本地 UI/物件生命週期。
4. `0x4B20BA..0x4B20C8` 查全域 Region `0x66D0D0→0x498000` 並 **`cmp eax,3`**。若 **Region!=3**，直接跳 `0x4B217A` 離開 success callback，這一支沒有接 C03/C10 的直接 call。
5. 若 **Region=3**，`0x4B20CE..0x4B2112` allocate 0x20060-byte UI object，`0x4B2109` **call `0x4A9380` constructor**；再呼叫 `0x541250`（`0x4B212A`，含 local tag `0x4C44756E`）、`0x442570`（`0x4B216E`）配置/掛入 UI component。**這裡沒有新增網路連線或直接 C03。**
6. **本次比 Roy1 更進一步確認了 `0x4A9380` 真實類別**：constructor 在 `0x4A93B5` 寫 vtable `0x609BBC`；vtable[-4] 的 MSVC COL `0x625970` → TypeDescriptor `0x6665D8` → **`.?AVLoginDialogPane@@`**。因此 Region3 成功 callback 的確會*建立*一個 `LoginDialogPane`，不能再含糊稱「另一個未知視窗」。
7. `LoginDialogPane` constructor `0x4A9380..0x4A9651` 本身有 UI 初始化 `0x4A95E9→0x4A87B0`、條件式本地 event `0x4A9617→0x4A8950`、`0x4A9631→0x4FD1D0` 本地 dispatch；其本身**沒有直接呼叫 C03 sender `0x4A7D10`**。另一獨立 `LoginDialogPane` callback **`0x4A8890`** 在參數 nonzero 時會於 `0x4A889D` 呼叫 **`0x4A7D10`**（C03 送包路徑），但**缺少「C04 最終成功後，這個 callback 必然被觸發」的證據**。不得宣稱自動 C03 已證，也不得把 LoginDialogPane 建構等同使用者看見重新登入畫面。

**原版可證的 state／事件界線**：final S02(0) 不會在這段函式立刻清成 `0x1f`（那是 S02 非零的 C15 路徑）；Region3 建立 LoginDialogPane 是**特定地區的本地 UI 控制路徑**。Region0/1/2/4 本函式沒有該建構行為；這不代表其稍後不會走不同背景授權。

## 三、Client I/O 四段式交接（不假造 Server/World）

|trigger|Client sends|Client receives|Client reaction / unknown|
|---|---|---|---|
|NewUser C02 送出、state0x1d|C02（region欄位依 A030）|S02(status0,string8)|Native `0x4B1F46` 建 C04 五 u8、state0x1e；只有合法 Server owner proof 才可 S02(0)（後者是 designed policy）|
|state0x1e 的 final S02 成功|**此 callback 無新增 C03/C10**|S02(status0,string8)|`0x4B206B` 本地 UI 文字操作、release 0B/0C/0D/07；Region3 建 LoginDialogPane；實際第一個 World C2S/初次 S2C **未追到**|
|NewUser S02 非零|C15（body=0）|S02(status!=0,string8)|根據 status/region 作 focus/message 分流，state=0x1f；原生錯誤文義與實機 popup/斷線未知|
|已完成創角後真正轉 World（**使用者確認正常行為**）|**unknown；不可硬塞 C03 或 C10**|**unknown；不可硬塞 S03**|A031 已證常規已有角色 S03→C10、Region3 可續 C25，但它**不證明**首次 C04 成功一定走相同路徑；需實際去敏 Client trace 確認 post-create grant/first S2C 和載圖|

## 四、對 DEV-ENTRY-02/03 與 CT 的必要修正

1. 保留已決策 ADR-008：C04 最終 S02(0) 後**不要求玩家回 LoginDialog 或再次手動 C03**；Server 原子提交 Character/Appearance/Onboarding 和已驗明的 E-MAIL 後，再保存可靠的 pending post-create owner/generation 以支援原生自動轉場。這是 **Server designed**，不是 Client 建構 `LoginDialogPane` 的因果證明。
2. Region3 可能構造 `LoginDialogPane` 但沒有證明一定顯示手動登入、一定觸發 C03；Server 必須按 native trace 確定其實際 next packet/連線。其他 Region 不可模擬 Region3 login ctor。
3. **不可**在 S02 final success callback 內直接假定有 S03/C10，更不能復用 A031 的 C25 `CBillingInfoPacket` 作 pre-verified World 入口。日後已有角色普通登入 C03/S03/C10 與第一次創角 direct World 是兩條需獨立驗證的流程。
4. C15 只能取消未提交草稿（Server designed），不能回滾已 durable committed Character；S02 非零錯誤文義及 region3 final-state 消息 suppression 仍需 native UI capture。
5. **不依賴原服 DB schema**：Client static 不提供「角色落 DB commit」時刻；Server 以自己的 transaction/unique owner/version/generation 設計冪等，必須讓原版 Client 看得懂合法 S02 結果和後續原生入圖。
6. Native CT-105/107（首次創角→直接入 World）、CT-108（World 首包/地圖）**仍 not-run**。本輪追加 **CT-111** 可執行 31 PE VA + Region3 RTTI + 合成回歸，但不能冒充 CT-105/107/108 PASS。

## 五、可重跑證據與限制

```sh
python task_a/roy2/a028_native_postcreate_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a028_postcreate.py' -v
objdump -D -M intel --start-address=0x4b1d60 --stop-address=0x4b2185 Asgard.exe
objdump -D -M intel --start-address=0x5354b0 --stop-address=0x535555 Asgard.exe
objdump -D -M intel --start-address=0x4a9380 --stop-address=0x4a9655 Asgard.exe
objdump -D -M intel --start-address=0x4a8890 --stop-address=0x4a88ad Asgard.exe
```

|evidence ID|觀察與界線|
|---|---|
|A028-E01|state1d S02(0)→C04五u8→state1e (`0x4B1F46/0x4B205A/0x4B205F`)|
|A028-E02|state1e S02(0)→local `0x4B206B` success callback; not direct C03/C10|
|A028-E03|success callback `0x535510` 清 0B/0C/0D，`0x5354B0` 清 07 UI slot|
|A028-E04|Region3 guard `0x4B20C0..0x4B20C8`; `0x4B2109` ctor `0x4A9380`，native COL→RTTI `LoginDialogPane`|
|A028-E05|LoginDialogPane ctor `0x4A95E9/0x4A9617/0x4A9631` local init/dispatch，沒有直接 C03|
|A028-E06|獨立 LoginDialogPane callback `0x4A8890` 的 nonzero branch `0x4A889D`→C03 sender `0x4A7D10`；**未證 final success 觸發**|
|A028-E07|S02 非零 → C15(empty) `0x4B1F1D/0x4B1F2F`／state1f `0x4B1F34`；Region3 state1e 的 message suppression `0x4B1E0D/0x4B1E1E`|
|A028-E08|原始 Asgard SHA 鎖定 **31 個 instruction VA + LoginDialogPane RTTI** 與 Python 合成狀態測試；**native GUI/world E2E not-run**|
|A028-E09|產品要求 ADR-008：創角完成直接 World／無手動二次登入；user-observed/Server decision，**不是已證自動 C03/S03/C10/World wire**|

**狀態**：原始 Client 的 `C02→C04→S02 success/failure→UI cleanup/Region3 LoginDialogPane` 已有**可交付靜態子集**；A-028 `integrated/partial`，不能把未證的成功**直接 World 網路動作**標 complete。首次 post-create 真正 first C2S/S2C、異常返回/UI、C15 native E2E 需 CT-105/107/108 的原版擷包，無法僅靠離線 EXE 假裝成功。

**缺少具名原件檔：無。** 已提供 `Asgard.exe`、`Born.dat`、`Map0/1/2.dat`；要解決最後阻塞需去敏的原版 Client **C02→S02→C04→S02 後至少 10 秒內 UI + C2S/S2C opcode/time/region/seed/連線 ID**。遮蔽 ID/PASSWORD/NAME/E-MAIL/token/raw decoded body；不可在 GitHub 公開原始私人資料。

## 後續條件式自動登入補證

最新REA已接通constructor內的快取／鍵盤條件→event4→C03 sender，並核對S03分派沒有prior-C03 guard。這不代表每次創角必然自動C03，Runtime仍待驗，詳見[補證](../../04-analysis-integration/postcreate-conditional-autologin-audit-20261101.md)。
