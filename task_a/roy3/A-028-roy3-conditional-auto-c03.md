# A-028 roy3 — 創角最終 S02 成功後，Region3 有條件自動 C03 原生閉合證據

日期：2026-11-01；工作分支 task_a/roy3。原始 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。承接 task_a/roy2/A-028-postcreate-ui-native-followup.md、A031 及 ADR-008。此處新增 A028-E10..E16；原始 Client 不修改、私有遊戲檔不入 Git。

**重要新結論：原版 Region3 final S02 成功 callback 建立 LoginDialogPane 時，constructor 有一條具完整 Native x86 direct call graph 的有條件、非人工 C03 發送路徑。先前「LoginDialogPane 是否能自動觸發 C03」靜態缺口已解，不能再把「玩家不需重新手動登入」解釋成「Client 絕不會自動送 C03」。但實機是否滿足條件、原版 S03/C10/World 是否真的成功，仍 not-run。**

## 1. Native caller→constructor→event→C03（A028-E10）

- 原版 MakeInfoDialog state0x1D 收第一 S02(0)，0x4B205A 送 C04 五個 u8 並在 0x4B205F 轉 state0x1E；第二段 S02(0) 走 0x4B206B，清四個 UI slot（Roy2 已證）。
- 0x4B20C0 調 0x498000 取得 Region；0x4B20C5 只允許 Region3 繼續；0x4B2109 direct call 0x4A9380 建 LoginDialogPane，vtable0x609BBC、COL0x625970、TypeDescriptor0x6665D8 確認類別。
- 0x4A95E9 呼叫 0x4A87B0 初始化 UI 後，ctor 0x4A95EE 讀全域物件 [0x66D10C]；0x4A95F3 要求該物件 +4 的首 UTF16 code unit 非0，0x4A95FA 要求 +0x204 亦非0。兩者缺一就跳過下述 auto。
- 0x4A9604 push 0x11（VK_CONTROL），0x4A9606 間接 call [0x5F144C]；**原始 PE USER32 import 明確是 GetAsyncKeyState 而非 GetKeyState**。0x4A960C test ax,ax，0x4A960F jl 跳過；若傳回 signed SHORT 非負，繼續。
- 0x4A9611 push0、0x4A9613 push4，0x4A9617 direct call 0x4A8950。該函式 0x4A8977 讀首參數4，0x4A897E 減4→index0，0x4A898F 使用 0x4A8D34 的10-entry native switch table；slot0=0x4A8996。slot0 分支 0x4A8A29 push0、0x4A8A30 direct call 0x4A7D10 C03 producer。
- 0x4A7D6E direct call 0x573060 C03 packet ctor（0x573079 push opcode0x03）；0x4A7DDE direct call 0x5788A0 C2S enqueue。
- **確切呼叫鏈**：0x4B2109→0x4A9380→0x4A9617→0x4A8950（arg4,0）→0x4A8A30→0x4A7D10（arg0）→0x573060→0x5788A0。8字元以上 PE 地址是 native VA，不是 C2S bytes。

## 2. 自動登入的 C03 與另一 callback 的差異（A028-E11/E13）

0x4A7D10 透過 LoginDialogPane widget2/3 取得兩個 UTF16 值並寫入 C03 packet+0x24 與 +0x224，並在 0x4A7DA2 將最後一個 boolean arg 寫入 packet+0x236。原生 writer 0x573110 將其分別編碼 string8、string8、u8，最後 flag writer 從 +0x22A（其 this 是 packet+0x0C，等於 packet+0x236）讀取。

因此 **ctor auto branch 在 0x4A8A29 push0，C03 最後 u8=0**。先前 A028-E06 單獨的 0x4A8890 callback 在參數非零時 0x4A889B push1、0x4A889D call 同一 0x4A7D10，尾 u8=1。兩條路徑不能合併為「有登入按鈕才會送 C03」，也不可將 auto u8=0 當作無須驗證帳密的 Server grant。

## 3. Guard 資料來源和 Region 限制（A028-E12/E14）

0x4A948E constructor 有 Region 0..4 的5-entry 跳表，位址 0x4A9654，依序 0x4A9495 / 0x4A9549 / 0x4A9495 / 0x4A9508 / 0x4A9495。Region3 在 0x4A9508 從 ctor 參數（非零時）或 [0x66D100]+0x810（參數為0時）填 login widget2；Region0/2/4 在 0x4A9495/0x4A94B4 自 [0x66D10C]+4、+0x204 初始化 widget2/3。**用來判斷自動化的兩個 cache 欄位不等於已確認的 C03 widget2/3 有效帳密**。真正值、是否明文、Server 回覆仍需去敏原版 Client trace。

這條 callback 建 pane 的分支 **只有 Region3**；不能套用 Region0/1/2/4，亦不能宣稱只要成功 C04 一定會發 C03。GetAsyncKeyState(VK_CONTROL) signed negative（Ctrl pressed）在此 constructor 會跳過 auto case，但其它 GUI 送包入口仍可能存在。

## 4. 與 A031 World 入口正確銜接（A028-E15）

若這個 Region3 自動 C03 取得有效 S03，A031 已靜態追出一般 Login/S03 transfer callback 的 S03 address/port/token → 新 TCP C10（raw token），Region3 C25 CBillingInfoPacket（3×string8）。但**只證明這些原生函式各自的條件鏈，不能假稱本次創角 runtime 一定收到 S03 或已拿到 World**；第一個 post-create S2C、map/C35 和完整連線仍 CT-105/107/108 not-run。

ADR-008 仍要求創角後直接 World、不能要求玩家手動再打帳號密碼。Server 可以允許被原版 Client 實際觸發的背景 C03，但需重新驗證可信 account/character/session-generation/credential，已提交 C04 的 context 不等於匿名 C03 或免驗證 World grant。

## 5. 可重現驗證與完成邊界（A028-E16）

本輪 SHA-locked 原始 PE32 靜態驗證：7條 E8 call edges、42處 exact x86 opcode anchors、5-entry Region constructor table、10-entry event jump table、MSVC vtable/COL/RTTI；12個 Python offline 原件/合成測試 PASS。可執行：
- python task_a/roy3/a028_region3_autologin_probe.py Asgard.exe
- python -m unittest discover -s task_a/roy3 -p test_a028_region3_autologin.py -v
- objdump -D -M intel --start-address=0x4a95ee --stop-address=0x4a9635 Asgard.exe
- objdump -D -M intel --start-address=0x4a8996 --stop-address=0x4a8a38 Asgard.exe
- objdump -D -M intel --start-address=0x573110 --stop-address=0x573154 Asgard.exe

**A-028：status=integrated，handoff_status=partial（包含實際直接入 World 與第一個 World TCP/S2C 的整體驗收仍未跑），native_postcreate_conditional_auto_c03_static_ready=true，native_client_validation=not-run。** 本輪完成 Region3 背景 C03 的原始 Client x86 子分析，但不能把 static/合成測試冒充原版 Windows GUI / Server E2E 已登入。

**缺少的新檔案：無。** Asgard.exe 原件已提供；需要原始未修改 Windows Client 的 C02→S02→C04→S02→C03（auto0）→S03/newTCP C10/Region3 C25→World S15/S14/C35/S04 去敏帧、region/seed/時間和畫面 trace，不需要再上傳更多猜測的 DAT。
