# 變更紀錄

## 0.1.0-draft — 2026-10-30

建立共同規格與私有開發分區；整理24項需求、20項待分析問題、系統責任、34項已知封包入口、6個基線情境與合成相容性向量。保留已知未知，未將完整MMORPG實作或最後畫面驗收標成完成。

同日補充：核對舊分析，新增逐份覆蓋表、Evidence身份索引、資源／地圖與Client相容性整理；補回metadata及SScript快取清理的已知細節。大型原件與私有實作未納入。

## 0.1.0-draft 補充 — 2026-10-31

依需求方確認的「僅管理員建帳、玩家 Client 只登入」，新增 R-025～028、A-021～023（open）、SCN-007～010（analysis-required）、CT-011～020（planned）與首次玩家規範、子里程碑、測試計畫。原 Client 無角創角 UI、C02/C04/S02 完整分支、原版新手教學 map ID/座標仍 unknown；無任何新 Server 實作或實機通過宣稱。

## 0.1.0-draft 補充 — 2026-10-31

依需求方確認的 R-025「僅管理員建帳，玩家 Client 只登入」，新增 R-025～028、A-021～023（open）、SCN-007～010（analysis-required）、CT-011～020（planned）及首次玩家需求/設計/測試文檔，更新系統分工、追蹤與 manifest。原 Client 空角創角轉場與真實教學 map/出生座標維持 unknown；本次不代表 Server 已實作或 Client 已驗收。

## 0.1.0-draft 補充 — 2026-10-31 教學完成延伸

新增 R-029～031、A-024～026（open）、SCN-011～013（analysis-required）、CT-021～028（planned）；新增 ONB-01～06 工作板、work-items.json、分析人員交付包、教學執行規劃與測試計畫。原生 map/出生、NPC/怪物、技能及任務完成、出口與獎勵仍需證據，沒有宣稱新 Client 人工驗收通過。

## 0.1.0-draft 補充 — 2026-10-31／所有接案者的分階段驗收

新增通用「A 研究證據交付 → DEV 實作 → CT 原生 Client 驗收」分離契約、A-021 專屬交付清單、通用任務模板與 AI handoff 規則；更新所有 A 紀錄與 ONB 工作的機讀 gate 欄位，並增加 GitHub Actions 結構檢查。A-021/A-022 的表述不再以新 Server 的實機測試作為分析完成的必要條件；重要 unknown 仍依 partial/blocked 誠實記錄。未改變任何 A 的實際 open 狀態或 CT 的 not-run 結果。

## task_a/roy1 — 2026-10-31 A-021 分析整合

依 Asgard.exe SHA 覆核 MakeInfoDialog、C02/C04/S02 與 UI 分支，完成靜態研究及可開發的 R-025 相容規格：Client C02 可在 C03 前認領管理員已預建的 Account，不得新增 Account，C04 再原子完成 Character；精確原生 UI 跳轉及部分錯誤碼保留 unknown。A-021 integrated/handoff partial、Server 可開始實作、Client CT 尚未執行。保留 main 新增的 phase-gates/CI 與分離 A/DEV/CT 完成定義。

## A-021 roy1 merge 後審核與安全規劃 — 2026-10-31

Fast-forward merge `task_a/roy1` (d1b53b0)；獨立比對 Client SHA 與 BIN，確認 C02 region variants、C04 五 u8、S02 status/string 及 0x1d→0x1e UI path。修正 `implementation_ready=true` 的過度聲明為 partial codec-only、整體 false；新增 A-027/028 追 pre-C03 身份授權及 C04 後續回覆。R-025 admin-only Account 政策不變，禁止無身份綁定的 C02 認領。這些均非原生 Client E2E 通過。

## Merge A-022 task_a/roy1 — 2026-10-31

合併 A-022 BIN-first map/world-loading 靜態研究：S14 control 1/2/3、S15 欄位、C35 MAP header (+4) 與 structured checksum、S04 位置、MAP 16-byte 記錄及安全重連/epoch 設計。通用 World loading codec 可交 DEV；原生教學出生 map/spawn 仍依 MAP/資源佐證，native CT not-run。

## A-023 roy2 source integration — 2026-10-31

整合 roy2 Script/Born 研究（C6C subtype 0..4、S44 多分支含 Script cache 修改風險、Born.Main UI 導引至 (31,29) 女性招募員）。Born 資源 SHA/解析詳見 roy2 報告；原件未納入共用 repo，與 EXE 發行版的配對仍 unknown。原始教學首次觸發、NPC id/map/spawn 仍 unknown；登入後任務 CT 不可誤認已通過。原 roy2 CT-029..031 與 main 已佔編號衝突，整合時調整為 CT-033..035。

## Main 完整合併與驗證 — 2026-10-31

已將 `task_a/roy1` 以 merge commit `d239bff` 併入 main，將 roy2 實際來源分支 `analysis/A-023-roy2` 以 merge commit `7dd8d86` 併入 main。以指定 Asgard.exe 實體 SHA 及原生函式位址覆核 A-022 MAP/S14/S15/C35 與 A-023 C6C/S44；Born.dat 原件本次無法再次取得，因此 Born hash/XML 為 roy2 提供且可重跑的報告證據，非本次獨立 raw replay。已解 CT-029～031 編號撞號：roy2 Script CT-033～035，保留 A-021 原 CT-029～032；重新整理分析優先順序與 ONB 依賴。
 
## task_a/roy1 — 2026-10-31 A-001 seed0..9 / 版本/字串分析

發現 A-001 尚無正式分析，採提供的 Asgard.exe SHA 做 BIN-first 復核，解得 `0x53B630` 十種 256 項 seed 遮罩公式、`0x53BB30` key、`0x53BE70/0x53BD90` XOR、`0x53C460/0x53C130` binary/ASCII framing、`0x577E80` C00 與 `0x589B60` S00 0/1/2 分支及 `0x45B1B0/0x45B7A0` string8 byte 長度。新增可執行無外部依賴 Python golden vectors，原本 seed0 C62 fixture 不變。A-001 `integrated/handoff=partial`，十個 binary seed 算法可交付，region/version/error/ASCII 的原生未知維持 partial，Client CT not-run。

## 2026-10-31 — task_a/roy1 (A-001) + task_a/roy2 (A-023) 新分析 merge

主線由 2517e60 fast-forward 至 roy1 0facfc2（A-001 seed0..9 binary codec）；另以兩 parent commit c544af3 將最新 roy2 ae95270 合併（A-023 S44 named start、PaperDialog 依賴/CRC、C6C4/2 Dispose、候選 NPC Script），後續整合原 JSON/CT 而不覆蓋 A-001；留存 CT-029～032、CT-033～035 和 CT-036。原本 A-023 之「Script 如何啟動未知」修正為「Client 端啟動機制已有靜態契約、原服首次發送政策未知」。新增 ScriptRun 安全狀態機、檔案版本/語系/CRC 前提及分派更新。EXE SHA 和 18 個 roy2 byte signatures 複核通過，roy2 Born/PaperDialog 完整資源離線 PASS 非本次獨立 replay。

## 2026-10-31：最新 roy1 A-002／main 安全交接規劃

A-002 C03/S03/C10 static Client contract 及 roy1 更正的 A-022 C25 handler 誤標已 merge；增加 CT-037/038 與 TransferGrant/WorldBinding/generation、錯密／重複登入／跨 TCP 正常關閉的 designed policy。原服 duplicate 行為及 Client E2E 仍 unknown/not-run。已保留 A-001、A-023 與 CT-033～036。

## A-015／roy2 — 2026-10-31：內容來源、格式、權利範圍的 BIN-first 研究

由 `c544af35ceb7` latest main 起建立 `analysis/A-015-roy2`；用原始 EXE 逐指令確認 Basic/Map0..2/Human 資源庫映射、MAP 10B tiles/7/8/16B 尾段、YPF flags bit0 optional 512B palette，並實測 Born.dat zlib/UTF-16LE 文件。新增 metadata-only 探針、A-015 報告、欄位目錄與 CT-039/038；不推送原作素材。原版完整 Map/Human/skill/item 載荷未提供，故限定格式子集 integrated / handoff partial / native E2E not-run。權利可處置性不因解析成功而自動成立。

## A-015 roy2 Map0/Map1/Map2 原始庫補驗 — 2026-10-31

使用者補上三份原生 MAP archive，SHA256 `dcaf8ab5...`／`8681dc75...`／`5320a095...`；以相同格式全量解析 **288+184+22=494/494** 份 .map，嚴格索引/區段/EOF 均 PASS。494 名稱對應 330 份 unique payload（33 組完全重複，164 個 alias）；(31,29) 在 477 張圖尺寸內，不能當教學圖 ID 或出生點證據。新增機讀摘要和私有檔 metadata-only 掃描器，未上傳任何原素材。A-015 仍 partial，CT-039 離線 MAP 範圍 PASS、CT-040 原生教學 E2E not-run。

## task_a/roy2／A-015 native MAP record field audit — 2026-10-31

遵守原指定 `task_a/roy2` 既有分支／目錄，未開新分支。由原版 EXE accessor 直接確認 MAP tail 7B=u8/u16/i16/i16、8B=4×u16、16B=2×u16+2×u32+2×u16，對 Map0/1/2 原件 494 MAP 重新驗證：32 張 header 第三值獨立；7/8/16 totals 74032/396/2269；8B/16B 疑似座標 100% 符合 48×32 pixels 的尺寸界線，但僅 inferred，不是 NPC/出生點。附 4 項合成回歸測試。A-015 保留 integrated/partial、CT-040 not-run、A-016 open；未上傳遊戲素材。

## 2026-10-31 最新 roy2 A-014／A-015 增量整合與版本核對

延續 roy1 A-016/027/028 與 roy2 A-015 格式研究，以雙 parent commit `f73da39cf3121d19bf0d9ddf5a4ab021d8be222b` 合併新增的 roy2 `c97bf22c040b6ae1676b772f8b351284d9ee38a4`：A-014 社交 Chat/Whisper/Group/Guild BIN 子集、A-015 有界範圍格式研究結案。A-014 報告原 S0D text string16 誤標，已由 Asgard.exe `0x5861F2/0x58620D` 的 `0x45B7A0` 確認為 **string8**；S0A 才使用 `0x45B890` string16。社交測試原歷史 CT-041/042/043 與主線創角撞號，重編 CT-047/048/049，主線共 49 CT 且原生 Client not-run。A-015 `handoff_status=ready` 只代表格式／來源／檔案身份範圍可結案，教程 map/spawn/NPC/技能仍未解。最新 manifest 校對及社交規劃已記錄。

## 2026-10-31 A-017 admin ops traceability conclusion

A-017 administrative account provisioning, ban/unban and sanitized audit integrated as designed Server API (not native GM wire), native Client not-run. CT-050/051 are management security/audit (old roy1 names CT-045/046 conflict with A-016); linked R-018/R-019/R-021/R-025 and SQLite synthetic tool `tools/a017_ops_contract.py`.

## 2026-10-31 — A-XX 統一改以 Client 收發分析

依需求方指正，修正此前 A-027/022/023 混入 Server 內部政策的錯誤：Client 分析只交操作/畫面觸發、C→S、必要 S→C、Client 狀態/自動回覆及失敗路徑。Account 驗證、角色 durable commit、出生 map/spawn、首次 Script 派送、NPC/AI/任務權威交 DEV/Server 設計；原始 Client 可用 opcode/field/state 仍須遵守。未改既有 A integrated/partial 或 CT not-run；增加兩份規範並更新 A 交接。Born.dat 原件已在本次環境驗 SHA/zlib，Map0/1/2.dat 也已提供。

## 2026-10-31 — Client I/O Server 實作路線與驗收矩陣

規劃 DEV-IO-01～06，建立 6 條 Client 事件→C2S→S2C→Client 效果與 Server Authority 兩層機讀矩陣，連結 ONB-01～06、PKT/SCN/CT；新增分段驗收表並更新 README/roadmap/進度板。CI 對 Matrix 做 PKT/SCN/CT/A/ONB 參照完整性和原生 CT 不可假通過的欄位檢查。本次不修改任何 CT 的執行狀態，也不宣稱私有 Server 已實作。

## A-024：NPC/怪物 Client I/O 已證子集（2026-10-31）

原版 `Asgard.exe` SHA `db3df616...`：C13 Attack (`BE u32`)、C43 ObjectInfoRequest (`u8,BE u32,u8`)，S07 DrawObjects、S0C MoveObject、S64 MovePath、S5F DieObjects、S0E RemoveObjects 的 native ctor/reader；[A-024 分析](../task_a/roy2/A-024-analysis.md)、[7 項合成測試](../task_a/roy2/test_a024_npc_codec.py)。正式 Client I/O 矩陣的 `FLOW-GAMEPLAY` 已補收發欄位，但 **C43≠已證女招募員點擊**、S07 物件非空完整 row/原版 UI/封包操作還不完整；A-024 `integrated/partial`, CT-021/022/034 planned，Native E2E not-run。Server AI/重生規則由 DEV 設計，不是 Client A 完成條件。

## A-004／roy2：原始 Client 多人視野／移動／移除（2026-10-31）

以原版 `Asgard.exe` SHA256 `db3df616...` 的 RTTI、vtable 與 native reader，確認 **S33 PutHuman** 起首 BE u16 x/y、u8 facing、BE u32 actor 欄，**S06 MoveHumanAck** BE u32,u16,u16，**S11 ChangeDirection** BE u32,u8，**S0E RemoveObjects** BE u32，**S0B MoveAck** BE u16,u16,u8 **不含第三方 actor ID**。C33/C11 是 Client 移動／轉向送出方向；S33（玩家）與 S07（其他圖上物件）的資料路徑不可混淆。

5 種 S2C native opcode constructor + 5 reader sequence 以實際 PE 及 SHA 鎖定 probe 全部 PASS；9 個合成 CP950/欄位長度/選配 flags/epoch/重送測試 PASS，**不是** native 兩 Client E2E。已更新 [A-004 分析報告](../task_a/roy2/A-004-analysis.md)、[機讀 locator](../task_a/roy2/A-004-native-locators.json)、[CT-060/CT-055](../05-conformance/A-004-visibility-test-plan.md)、SCN-005 與 FLOW-VISIBILITY。

目前未追通完整原生 MapPane/ObjectRegistry callback、跨包 u32 ID 的實際 key 查找和 Native UI 的離視野效果。Server 可按 map_instance/epoch/id 做權威可見集合和斷線 fencing（**designed**），但原服 AOI 範圍、重用規則不得聲稱已證。`A-004.status=integrated`, `handoff_status=partial`, `native_client_validation=not-run`。

## A-005／roy2 角色移動、地圖旗標與校正研究（2026-10-31）

原始 `Asgard.exe`：C33（0x573BF0）連續寫 3×u8、C11（0x571960）寫 1×u8、S0B（0x583150）讀 BE u16 x/y + u8。S0B 是**自己的位置／序號回覆**，沒有第三方 actor ID，其他玩家應使用 A-004 的 S06/S11。C33 不含絕對座標、地圖 ID 或 timestamp；原服速度 tick、拒絕失敗的 bit7/UI 重試規則並未全證。

原始三份 Map DAT 494 張／**7,701,805** 個 tile 的 `LE u32 flags` 只出現 0、1、16、17、512。`0x4B3520` 以每格 10B 原始 tile 轉成 17B native tile，`+6` u32 flags 原樣複製；`0x4B4BB0` 使用 bit4(0x10) 做線段遮擋測試，`0x4B2CA0` 動態設/清 bit0，`0x4D1206` 另一處用 bit0。**這些位元 consumer 不足以證明玩家走路唯一碰撞位元。** 不得直接以 `flags & 0x10` 決定移動通行；Server 的行走碰撞、最大速度、重送/epoch 保護必須明標 **designed**。

來源 [A-005 報告](../task_a/roy2/A-005-analysis.md)、[完整旗標統計](../task_a/roy2/A-005-corpus-flags.json)、[原始 PE 驗證](../task_a/roy2/a005_native_probe.py)、[10 項 synthetic test](../task_a/roy2/test_a005_move.py)、[CT-056/057](../05-conformance/A-005-movement-test-plan.md)。`A-005 integrated/partial; native Client not-run`；已知 Client I/O 子集可交 Server DEV，仍需進一步原生 MapPane 失敗校正／實際角色碰撞 handler 驗證。

## 2026-10-31 — 使用者新增暫行創角帳號比對限制

不修改 Asgard.exe。已驗證登入帳號與原生創角輸入帳號不匹配 → Server 直接拒絕，不建立 Character/草稿或 grant；無登入亦拒絕。ASCII 帳號大小寫不敏感、不 trim。更新 R-026/SCN-007/008/ONB-01/02、FLOW-NEWUSER 與 CT-041/044/053；Client 原生 C02 名稱欄與 UI 入口仍 unknown，不能因新限制假稱 native creation ready。


## A-006／roy2 原版 S05/S33 flags 補證與置中驗收（2026-10-31）

原始 `Asgard.exe` SHA `db3df616...` 以實際 binary VA 核對 13 組 native instruction patterns；`S05` `0x5895A0` 先 BE u32，按 flags 低 byte `bit0`（額外 RGB3）、`bit4`（額外 BE u16）、`bit1`（額外 u8）、`bit7`（額外 u8）條件讀取。**29B S05 僅能用於已知本版 `flags=0/0x1000`**；不適用全部 flags。自身 `S05` 髮色 RGB +10..12、衣色 +25..27 是兩個獨立值。

`S33` 原生 parser `0x585570` 已確認前段 BE u16 x/y、u8 facing、BE u32 object；flags=0 的 CP950 string8 名稱與髮色 +15..17、衣色 +30..32；`0x585667` bit0 額外 RGB、`0x58568B` bit4 額外 u16、`0x5856A4` bit1 額外 byte、`0x5856B4` bit7 額外 byte、`0x585719` bit13 額外 string8。**`42+CP950-name-bytes` 僅 flags=0 profile**。另在 `0x585780..0x5857F4` 有三色全零→FF00FF 的原生 sentinel 正規化分支，但不能據此推論所有黑色顏色禁用或 YPF 完整染色層行為。

已知 profile viewport `(8,9)` 在 48×32、pane(-56,-36) 計算錨點 `(400,300)`，`(9,9)` 則 `(448,300)`；**此為畫面座標投影/既有公式，非原生截圖完成證據**。13 組原件 PE checks 與 10 項合成測試 PASS；CT-058 offline subset 已驗，CT-059 原生 8 向動作／髮衣獨立染色／換裝／切圖／重登**未執行**。參見 [A-006 原生 Client 報告](../task_a/roy2/A-006-analysis.md) 與 [驗收腳本](../05-conformance/A-006-appearance-test-plan.md)。A-006 `integrated / ready` 是 Client I/O **靜態交付完成**，不代表 renderer/YPF/DOI/native GUI fully validated。

## 2026-10-31 — 下一輪 SAFE/WIRE/WORLD/SCRIPT 可開工規劃

新增 `02-server-planning/native-creation-next-iteration.md`、`onboarding-readiness-gates.json`、`03-analysis-requests/next-client-io-evidence.md`、`05-conformance/native-creation-gate-test-plan.md`。收斂 A-027/028/022 method/deliverable 為 Client UI/封包行為，保留 A integrated/partial 的實證與 unknown。新增 CT-054 planned/not-run 追原生已驗登入空角→NewUser UI/帳號欄；ONB、SCN、FLOW、traceability/manifest 更新。SAFE-01～04 不需等待原服 Server 資料庫/出生點/派任務，Native C02/C04 仍 fail-closed；沒有執行原 Client E2E。
