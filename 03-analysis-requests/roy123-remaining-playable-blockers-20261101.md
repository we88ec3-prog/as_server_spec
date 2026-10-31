# Roy1/2/3 合併後 P0 分析／原版動態驗收缺口（2026-11-01）

## 已有原件，不應再重複要求
`Asgard.exe`、`Basic.dat`、`Locale.dat`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat` 均已提供且 SHA256 已核對。創角 NAME/EMAIL 原版資源 label 映射 **Region2..4 已解**；真 MAP 靜態 C35 pair **已解**；Region3 一般轉服 C25 是 `CBillingInfoPacket 3×string8` **已解**。不要再把它們列「完全未知」或要求重分析。

## P0 仍需分析／取得的具體證據（先後可並行）
|順序|任務|真正剩餘問題／觸發→C2S→S2C→Client 行為|可交付 DEV 的出口|
|---|---|---|---|
|1|**A-028 + A-031，首次創角成功的自動 World 轉場**|原版 `state0x1e+final S02(0)→0x4b206b` 之後何者在**沒有可見 LoginDialog 人工再登入**的情況下發起 World？是否背景 C03/S03/新 TCP C10？Region3 `LoginDialogPane` 是否只建構隱藏 UI／觸發 callback0x4A8890？先後的 C2S/S2C、TCP ID、body shape 必須從原版動態 trace 或更多 EXE dataflow 定案|依 region/狀態證成最小 PostCreateEntryContext → 正確 Client 原生 grant/transition；不能憑 user-visible flow 自造封包|
|2|**A-030／CT-104/105，原生 S02 非零 UI 與 C15**|Region2..4 NAME/F3 EMAIL/F4 已證，但 E-MAIL 是否空白仍會送 C02？S02 status=1 + text 是靜態候選，不是官方錯密碼狀態；原版 GUI 會提示/發 C15/留 socket 可重試嗎？所選 runtime region/seed 與帳號 Client ID 長度 gate 是否相容？|只啟用匹配 verified region/label/profile；驗 owner + credential version；合法 S02 stage1/2；失敗可見且不冒充 TCP 業務斷線|
|3|**A-031 + CT-108，一般登入的 World entry 回覆**|已證 Region3 S03→C10→C25 三個 opaque string8、non3 某路徑只 C10；**C10/C25 後原版到底何時接受 S05/S15/S14，是否另需 S02/S2C、transport phase？**|World routing 不再硬等 C25=01；C10 token 是唯一權威，依 profile 接 C25 optional；原版收到真正地圖資料|
|4|**A-032 + CT-108，真 MAP/S04/S33/出生可視**|初始 `map_ref=6` 的理論 C35 `00040F90`，但尚未觀察原版真正 C35；選定地圖的原生 S15/title/flags 與 S04 viewport/facing 是否讓 Client 顯示？**合法出生位置未知**，map6 不代表教學圖|版本/原件 SHA 鎖定 MapCatalog，capture true C35，原版可見人物與地圖；能在已驗出生座標停留|
|5|**A-005 + CT-109，原生玩家移動碰撞/校正**|C33 seq 回覆與 S0B bit7 分支已證，但 Client 的真正移動 step/方向、collision `0x4BE470→0x4C1850`、flags/動態 block、撞牆 rollback 與實際速度/回包時間仍不明|最小有界 Server-authoritative C11/C33+S0B，經原版 UI 實測可走5步與一次阻擋，禁止單靠 tile flags=0 判定可走|
|6|**A-015/023（首次真正教學圖，非 interim 走路的先決）**|目前無原版教學 map_ref/出生點/招募員實際 spawn，Born (31,29) 是文字引導；若最終必須進原版教學圖，需其證據，不能把 map6 擅當官方|先讓原版 Client 在原件已確認的安全地圖可操作，標 `native-interim-playable`；再把教學圖/首次腳本接入後才宣告 ONB-03 原教學圖通過|

## 要求的現場資料（沒有真帳密／信箱）
一段 **未修改原始 Asgard.exe SHA、選定 region/seed/Client version** 的本機 UI + TCP 去敏 trace：
1. 新建帳號：C02 收發 ordinal/field count/各欄編碼長度 → S02 status/message length → C04 body length → final S02 → **接下來 10 秒**所有 C2S/S2C opcode、frame length、時間、TCP connection ID、畫面是否出現 LoginDialog。
2. 一般既有角色登入：C03→S03（**遮蔽 token**）→新 TCP C10→Region3 C25（只記 body shape/長度）→第一個 World S2C。
3. 原版 World：S15(map_ref)/S14(1)→C35 二組 u16、S04 四欄、S33 角色、S14(2) → C11/C33(seq/mode)→S0B(status_seq,x/y)，包含合法 5 步和一次阻擋畫面。
4. 可另做錯密/停權／重名/空 E-MAIL：只記 S02(status/message length)、C15、socket timeout/FIN/RST，**不記原始明文/解密 C02 body**。異常斷線與正常 S03 transfer close 分開。

動態實測是 Server/CT 出場門檻，A 靜態子集已可交 DEV；不要因無法同時做原版 Client E2E 而將已證 A 分析全重開。若提供額外**教學互動**資源可再指定 `PaperDialog.dat`，但**首次成功創角→可移動的 P0 沒有新必缺原件檔名**。

## 2026-11-01 A-005 靜態結案後剩餘精準工作（覆蓋舊「位元全不明」）

**已證**：局部 path gate 目的地 bit0、來源 bit3 + direction mask、場景 actor lookup、overlay add/remove、八鄰方向索引；map6 flags0=902/flags17=2698，bit0-clear 的 raw-only 候選 component=900。**未證**：dynamic overlay 寫入者、方向遮罩實際來源/更新、原版角色腳底／安全出生與 C33 方向是否全部同 path helper、合法速度與 GUI 真走路/撞牆回滾。DEV 可以依已證 read-side 設計候選/合成測試，但**不能僅憑 raw bit0 就讓正式玩家行走**。交 CT-109/E2E；完整補證 [Roy3](../task_a/roy3/A-005-native-path-collision-closure.md)。本追加**沒有新缺的原始檔名**。

## 2026-11-01 A-030／A-028 新優先：可顯示的失敗回覆與 C15 後恢復

使用者已明確決策 **一般驗證失敗不可由 Server 無回覆直接踢線**。A-030/A-028 需更精確交：原 Client NewUser state0x1d 與 state0x1e 各自的 `S02(nonzero,string8)` status → 本地錯誤訊息/焦點 → 是否送 `C15(empty)` → TCP 保留/Client 正常關閉 → 重新點「創角」時的第一次 C2S。錯密／停權／重名／C04 失敗對應的 **具體 status 尚無原版動態證據**，不用猜或從普通 C03 status3 複製。若原 Client 資料不足，交 `native-error-mapping-unverified` 和具體 Client 原始 TRACE 取樣步驟。

原版 CT-112 負向 UI/C15、CT-113 Server 原因 Log，按 [ADR-009 規劃](../02-server-planning/expected-validation-failure-policy-20261101.md) 驗收。此工作可與 DEV-ENTRY、教學 A-012/023/026 並行；**沒有新增必缺的具名 DAT**。

## 2026-11-01 真實創角後異常的新實測：S02(0)×2 → io-error，下一條 C42 是原版例外回報

使用者提供三份本機 JSONL，已分析出 `2026-11-01 03:38:13 (UTC+8)` 的原始 Client C02→S02(0)→C04→S02(0)，Server 同 socket 4.313 秒後只記 `io-error`；另一條 Socket 30 秒後 C62→C42(body39) 被 Server 標 unknown 後斷線。**經相同 SHA 原版 EXE 靜態查證 C42 其實是 `CExceptionPacket`（ctor `0x5723C0`、RTTI `0x66940C`），屬 crash log 回報路徑，非 World 入口**。沒有同條連線的 S03/C10/C25/C35，也沒 Client PID/exception cause。成功建角回覆不能宣稱進地圖，不能把 io-error 當 Server 主動踢線，更不能假設 C42 是轉服。詳 [這次分析交接](../04-analysis-integration/20261101-postcreate-c42-exception-report-evidence.md)，P0 補查 A-028 final S02 callback、A-031 native World first socket、Client `Crash_as*.log`／WER；Server 修正交 DEV，分析者不修改程式。

## 2026-11-01 RI-007：新增登入 Log 定位 World C25 後無回覆，Windows preview 當掉證據

新附件（三份 `(2).jsonl`）確認 **03:47:31 C03→S03(成功) 正常轉服關線**、03:47:32 新 TCP C10→WorldGranted、03:47:33 Region3 C25(body_len16) `handled` 但 Server 沒有任何 S05/S15/S14，也沒有 C35、World trace 亦無 close summary。對照唯讀 `as_server_roy@e93c9a17` 的 `LoginWireSession.case 0x25`：`_worldFixture==null` 時只解析 Region3 billing C25、設定 `_billingSeen=true`、`return Continue()`（零回包，留 WorldGranted），**這就是登入後「伺服器無回應」的第一優先實作缺口**，不是 C03 帳密錯、C25 格式錯或 C35 CRC。不能用 synthetic `C25=01` 或合成 World fixture 替代原生證據。

使用者 Windows Log 另顯示 03:38:13 的 `Application Error 1000` 為 **`Asgard-main-menu-preview.exe`**、03:38:17 WER1001；因此先前 RI-006「原版 Client 創角後崩潰」需要訂正為**預覽副本的 runtime 崩潰**，其完整 exception code/module/offset 尚未取得。`.NET Runtime 1000` 的 `GameTcpDiagnosticJournal` 標籤可能是 Server 日誌事件，並不能證明 Server 程式 crash。詳 [RI-007 整合報告](../04-analysis-integration/20261101-native-c25-wait-and-preview-app-error.md)。本次只更新規格與分析，不更改 Server/Client。

## 2026-11-01 修改版 Client 的分析隔離要求（使用者明確更正）

`Asgard-main-menu-preview.exe` 是**僅供排錯**的修改版。它的 WER `APPCRASH` (`0xC0000005`、RVA `0x00141264`) 及其 C02/C04/C25 操作只能當 `modified-preview-debug-only` 的現場線索，不能標為原版 `Asgard.exe` 任何動態行為已證、或把 RVA 直接對上原件同地址推定原版崩潰原因。原版 A-028/A-031 靜態證據仍由原始 SHA 鎖定 EXE 產生；若要原版 Native CT，須另外以**未修改的原件**執行。本輪 Server code `C25→Continue()` 零回包屬 source-proven，與 Preview 是否原版無關。完整隔離註記見 [RI-007](../04-analysis-integration/20261101-native-c25-wait-and-preview-app-error.md)。
