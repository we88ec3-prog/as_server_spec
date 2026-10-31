# 變更紀錄

## 2026-10-31 23:51 創角送出直接原因已確認

新連線以 REA Client send 與 Server f2a4a38 本地去敏 close journal 關聯：C02 成功送出並收到，因 native-c02-fields-unknown-a030 立即關閉、未回 S02。將 RI-001 根因切片提升為 runtime-confirmed；A-030 僅補 A30-1，欄位與錯誤契約仍待研究。確認新版 FormInput idle600／absolute1800 已實作並在本次摘要生效，與舊60秒等待及前輪 send=-1 分開。不發布原始 journal／表單，Server 未由規格整合者修改或重啟；原版 CT 仍未通過。

## 2026-10-31 創角二次重現：等待輸入與送出分開

第二輪同步 TCP／程序取樣已觀察 Server 先 FIN，Client 保持回應；整合使用者提供的「登錄連線中」→「伺服器無回應」畫面摘要。明示創角合法等待不套一般60秒讀取期限，仍保留分階段資源保護；送出後 C02 fail-closed 限制獨立交 Server 開發者。尚缺本次 C02 與 close reason，未定根因；沒有發布表單截圖或憑證，沒有修改 Server。

## 2026-10-31 RI-005：視窗回應正常但遊戲已斷線

收錄使用者實測、11筆程序取樣與事後 listener／連線觀測；使用者確認手動關閉，故排除將 PID 消失直接標為 crash 的誤讀。新增程序／TCP／會話分離、分階段 idle/load timeout 與去敏 close 摘要合約。現行60秒 read timeout 只列靜態候選，不宣稱已確認根因；Server 未修改、未重啟，原版及功能驗收未通過。

## 2026-10-31 本地問題收集與規格整合角色

依需求方指定，本工作只維護 as_server_spec、對 as_server_roy 唯讀核對；新增本地問題到 A／DEV／CT 的交接流程、RI-001～004 去敏登錄、Server 修正交接與本地主選單／創角入口的既有證據整理。按 as_server_roy b8e212e 區分已實作後端／診斷與未完成原生 wire，釐清 ad84f9 的歷史根因範圍。置中／染色屬舊原型、tooltip 屬修改副本，不冒認新版 Server 或原版 Client 驗收。未變更 Server 實作、資料庫或 Client，CT-103～105 維持 not-run。

分享清單另修復五筆原有過期 hash（architecture、A-014 測試計畫／分析／封包索引、A-024 分析）；上述五份內容未修改。hash 依 repository 的 LF 文字格式核對。

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

## 2026-10-31 — 使用者新增暫行創角帳號比對限制

不修改 Asgard.exe。已驗證登入帳號與原生創角輸入帳號不匹配 → Server 直接拒絕，不建立 Character/草稿或 grant；無登入亦拒絕。ASCII 帳號大小寫不敏感、不 trim。更新 R-026/SCN-007/008/ONB-01/02、FLOW-NEWUSER 與 CT-041/044/053；Client 原生 C02 名稱欄與 UI 入口仍 unknown，不能因新限制假稱 native creation ready。

## 2026-10-31 — 下一輪 SAFE/WIRE/WORLD/SCRIPT 可開工規劃

新增 `02-server-planning/native-creation-next-iteration.md`、`onboarding-readiness-gates.json`、`03-analysis-requests/next-client-io-evidence.md`、`05-conformance/native-creation-gate-test-plan.md`。收斂 A-027/028/022 method/deliverable 為 Client UI/封包行為，保留 A integrated/partial 的實證與 unknown。新增 CT-054 planned/not-run 追原生已驗登入空角→NewUser UI/帳號欄；ONB、SCN、FLOW、traceability/manifest 更新。SAFE-01～04 不需等待原服 Server 資料庫/出生點/派任務，Native C02/C04 仍 fail-closed；沒有執行原 Client E2E。

## 2026-10-31 — 使用者確認多人同圖（ADR-007）

明確採用 Public Shared Map：同 world/map 的玩家互見並共用 NPC/怪物、死/生/移動、AI 與 Actor EntityId，玩家自身進度獨立。新增 DEV-070-M 重構計畫、機讀共享地圖契約與 CT-055 (planned)，更新 R-007/R-029、ONB-03/05/06、SCN-005/011/012、CT-021/022；原版 Client 相容仍待 A-004/011/024，不修改 Asgard.exe。

## 2026-10-31 — 整合 task_a/roy1 與 task_a/roy2 並依新證據更新 DEV

以三父 merge commit `078b0d1d8aab9f443ba630f43b7e5c904dd5f3fb` 保留兩分支來源歷史與原始報告/測試；11 新 A 分析 static/partial 回寫、72 PKT、12 Client I/O flows。CT 原編號衝突避讓至 056～081；main CT-054/055 保留。標記 Roy1 S1E vs Roy2 S5F 死亡 parser 歸屬疑點，不猜 Native Death opcode。按共享地圖 ADR-007 重排 DEV-070-M actor wire/DEV-080/DEV-090，列出剩餘 A-027/024/004/022/005/009/025/026 及資源缺件。

## 2026-10-31 P0：原版遊戲登入密碼八字限制與 DEV-030 修正規劃

使用者觀察原版 Client 密碼框只輸入8字；核對 `as_server_roy/main` `Pbkdf2PasswordHasher.ValidatePassword` 實際最少 **10** 字（不是敘述的最少12字），造成管理員建帳與原版 Client 登入不相容。R-025/ONB-01 新增遊戲用恰好8 ASCII 英數的臨時安全相容 profile，與 Admin key 分離，並要求相應 DEV-030 SQLite/Postgres/重設/測試與8字短密碼防濫用補強；不截斷舊密碼、不更新原始 Client、不宣稱私有 Server 已修。詳 [政策](../02-server-planning/native-game-password-8char-policy.md)。

## 2026-10-31 P0 密碼需求改版：4～8 字（取代固定 8 字）

依使用者最新決策，R-025/ONB-01 遊戲帳號密碼由上一版「**恰好 8 位 ASCII 英數**」調整為**4～8 位 ASCII 英數**、大小寫敏感；自動產生仍推薦最長8位安全亂數。管理後台 key 規則與玩家帳號分開，短密碼加強限速、防暴力登入，原長密碼不可截斷。未來**可能**調整 `Asgard.exe`，但本次未授權/未修改；須獨立驗證修改版 Client build/profile 再提高上限。舊文件保留導向 [最新版](../02-server-planning/native-game-password-4to8-policy.md)，驗收測點更新至4、8及上下界；私有 DEV-030 尚未依此修正。

## 2026-10-31 Roy1/Roy2 最新分支整合與 A-022 勘誤

將 task_a/roy1 新 A-011/A-022/A-013 與 task_a/roy2 A-015 的最新驗證成果以保留歷史方式整合到 main。原件 Asgard.exe 的 MAP 26/26 VA + 交易 18/18 VA/6 RTTI，地圖 Map0/1/2 共494/494/7,701,805 tile；更正 Roy1 把首 MAP 起點多4 bytes、誤判成491/494 的錯誤。CT碰撞分配 A-013交易087～089、A-015地圖090～091，原版 Client native not-run。建立 DEV-060/070-M/090 與經濟 Domain 下一階段 Server 需求；原Client不改、4～8字密碼、多玩家同地圖共用 NPC/怪物政策不變。

## 2026-10-31 追補 Roy1 A-012 / Roy2 A-010（第二輪增量）

在第一輪 Roy1/Roy2 MAP與經濟研究合併成功後，兩分支又提交 A-012 任務腳本 C6C 回覆/Dispose 與 A-010 技能施放/取消/持續效果。同步最新來源研究與測試、增加 Client packet S48/S2C/S2D，完成衝突 CT ID：A-012→CT-092～094、A-010→CT-095～096（此前經濟087～089及MAP090～091不變）。更新 Server DEV-090 Quest 和 DEV-080 Skill/BUFF Domain 的下輪交接；官方技能效果/原版 quest/Client GUI 尚未證。原始 Client 不改，遊戲密碼4～8字，Admin-only Account、多玩家共享 NPC/Monster 不變。

## 2026-10-31 Roy1/Roy2 再同步與 Web 管理介面規劃（非實作）

使用者要求只規劃管理頁面；此輪沒有寫 Web/Server 程式碼。核對 `as_server_roy` 現有 /admin JSON API 與4～8字密碼實作，新增 P0–P2 UI 設計、WEBUI-P01..P10驗收計畫（未測）及「日後實作必須先提醒並取得使用者確認」規範。Roy1 無新增，Roy2 A-010離線結果增量同步且主線 CT-095/096 保留，原版 Client E2E not-run。見 [審查](../04-analysis-integration/roy-branch-web-admin-sync-20261031.md)。

## 2026-10-31 玩家更正：三個原生帳號入口 + 舊創角身份假設作廢

使用者確認**登入、創角兩獨立 UI 入口**；管理先建立 Account，創角直接以既有帳號＋密碼對後端同一 CredentialStore 驗證，錯誤需回 UI 而不寫角色，**不要求先 C03**。另原版有**更改密碼 UI**，玩家正常修改必須用此入口，管理 `credential-reset` 改定位為救援。新增 R-032/A-029/ONB-07/SCN-017/CT-097..099 與三入口安全、原生測試文件；A-027需核 C02 field1/field2 與 native error status，A-029需定位 change-password opcode/回覆，未證一律 unknown。維持4～8密碼、原 Client不修改、僅設計不實作、後續 Web 實作前必須確認。

## 2026-10-31 使用者最新三項規劃覆蓋：C02 Guard、最高隊伍傷害、拒絕入學可重問

核對私有 `CharacterCreationAccountGuard.RequireMatch(loggedIn,...)` 仍需已登入身份，標記 DEV-040 未實作最新要求：創角直接核對 C02 既有帳密後發限創角授權 proof，免 C03；原生失敗碼待 A-027/028。共享怪同 Monster life 依**隊伍總有效傷害**選唯一贏家，贏家**所有成員每人完整 EXP + 各人一次獨立掉寶判定**， ledger 冪等；party/tie/offline/中途異動保留實作前決策。 `nNewJoin01 STATE=REFUSE` 代表 Server 不入學 no-op、NPC 可再點擊/再拒絕/稍後接受，無其他角色副作用。新增 R-033/034、SCN-018/019、CT-100/101/102，保留現有 A-014/A-009/025、A-012/023/026 精準取證，不新 branch，不改程式，不宣稱 native CT passed。

## 2026-10-31 原生創角「連線中斷」P0 調查與規劃

讀取 private as_server_roy@ad84f9 source 確認 LoginWireSession C02/C04 進分支直接 Close、不送 S02、不驗帳密；C15 empty 也 Close，transport 在 CloseConnection 時退出 Socket。創角 Guard loggedIn 依賴是另一個尚未接到 live handler 的程式缺口。原本 A-021/A-027/A-028 的 Client state0x1D→0x1E、C15、region serializer 照舊；原本使用者觀察的連線中斷究竟在 C02 前後仍無 live trace，保留 unknown。新增 A-030 精準核查 ID/PASSWORD/CONFIRM/NAME/E-MAIL 逐 region UI/wire、E-MAIL 必填、S02 native fail UI/取消/重試、第一個斷點；新增 CT-103..105，規劃 DEV-CREATE-01..10 及分階段通過條件，補 machine-readable ONB-02/R-026/SCN-008/Client flows/readiness/traceability。無私有程式或 DB/Client 異動；未來實作必須向使用者確認範圍。
