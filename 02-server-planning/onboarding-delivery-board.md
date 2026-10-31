# Server 進度板：規劃／分析／實作／驗收分開

截至 2026-10-31，僅以 `as_server_spec` 這份共用規格判斷；私有 Server 原始碼、最新編譯與測試不在本 repo，**不可推定它們已完成或未完成**。

|工作|規格|分析|可先做的 Server 工作|原生 Client 出場門檻|
|---|---|---|---|---|
|ONB-01 管理建帳＋登入|已規劃 R-025|A-021 子集已整合；A-027 未完成|管理 API、權限、稽核、憑證/停權、最小 C03 profile|預建帳號合法登入；Client 不可建 Account|
|ONB-02 創角與保存|已規劃 R-026|A-021 子集已整合；A-003/A-027/A-028 待補|原子建角、名稱/外觀驗證、草稿/重送|原 Client 正確創角/重登|
|ONB-03 首次入教學|已規劃 R-027|A-022 通用 Map/CRC 已整合；原生 MAP/出生待 A-015|grant、Loading/CRC 狀態機、內容版本|原版教學地圖出生且可操作|
|ONB-04 中斷恢復|已規劃 R-028|A-016/A-021/A-022 缺失分支|故障注入、幂等、重登入恢復|Client 中斷後無重複角色/錯誤進度|
|ONB-05 教學 NPC/怪物/技能/目標|規劃 R-029/030|A-023 Script/Born 部分整合；A-024/025 未完成|場景生成、AI/戰鬥架構與目標 ledger|教學真實互動流程跑通|
|ONB-06 教學完成/出圖|規劃 R-031|A-026 待分析|完成狀態/獎勵交易、轉圖骨架|原 Client 完成所有必要教學並離開|

## 下一步與狀態定義

**依最新 [分析優先順序](analysis-priority-after-A022-A023.md) 執行：A-027、A-015 先行，A-028、A-003/A-020 與資源/Script 研究並行**；A-021～023 已交付有界靜態子集，其餘 A-024～026 可讓專長人員先研究已知系統。所有 A 新增時仍為 open/unassigned，只有接手者確認才改 scoped/analyzing/review/integrated。參見 [分工包](../03-analysis-requests/onboarding-assignment-pack.md)。

- `specified`：需求已規劃；不代表已開發。
- `open`：分析任務待認領；不代表原版行為已解。
- `planned`：測試尚未執行。
- `implementation_status=not-reported`：共用規格未收到該私有實作的驗證資訊；不是斷言「沒有實作」。
- 原生 Client 驗收需要相符 Client、具體操作/輸出和測試證據；單人一般進圖通過不能算完整新手教學通過。

每次完成 A 應回寫 04 分析整合，補 CT，並更新版本與追蹤；Server 實作則由相應開發 repo 另行回報。

## roy1 合併後 P0 阻塞更新

A-021 已交付且靜態驗證其 C02 region variants、C04 五 u8、S02 status/string 及 state 0x1d→0x1e 的**部分**規格，不能解讀為原生創角路徑全部可開發/已實機通過。**新增 A-027/P0**：C02 pre-C03 身份/憑證及預建帳號認領安全證明；**新增 A-028/P0**：C04 之後的回覆/提交/重登轉服。ONB-01/02/03 的原生相容通路仍 blocked；管理端建帳、domain 唯一性、region-aware codec fixtures 可先做，禁止未驗證 C02 授權角色建立。


## A-022/A-023 合併後狀態（2026-10-31）

A-022 通用 Map/CRC 的部分可直接支援 DEV，但真正新手 map/spawn/C35 expected pair 仍無原版內容證明。A-023 有 Script C6C/S44 與 Born.Main PaperDialog 的靜態及 roy2 資源報告，**(31,29) 是文字導引而非 spawn**，首 NPC/自動觸發未知。CT-033/034/035 為 A-023 教學 Script 的測試（main 原 CT-029～032 保留給 A-021）；所有原生 Client CT 仍 not-run。

正式序列與可並行項見 [分析優先順序](analysis-priority-after-A022-A023.md)。

## 最新 A-001/A-023 分界（2026-10-31）

**A-001 integrated/partial**：seed0..9 binary codec 可先做 unit fixtures；實際 region/版本選 seed/key、S00 錯誤狀態仍交 A-020，不能宣布十種模式都真 Client 登入成功。**A-023 integrated/partial**：S44(1,0) named start、缺檔 C6C0/S44(1,1) 更新、Main 及 C6C4→C6C2 Dispose 已有靜態契約；原服首次發送時機、NPC 位置與 quest flag 仍 unknown。ONB-05 的 Script transport/run registry 可先 DEV；ONB-03/05 的原生教程全程仍 blocked。詳見 [Script Lifecycle](script-lifecycle-contract.md) 與 [本輪證據核對](../04-analysis-integration/A-001-A-023-merge-verification.md)。

## 本輪 A-002 Client 轉服解析更新

A-002 新增 C03 登入欄位、S03 host/port/opaque token、C10 raw token，及新 TCP 轉服的 Client 資料流。ONB-01/03 可先做實作與 synthetic CT-037；ONB-04 可依 generation/舊 socket 安全政策先開發 synthetic CT-038。**原服採踢舊還是拒絕新登入尚未知**，本 Server latest-auth-wins 為 designed，不宣稱原版已驗收。A-027 的 pre-C03 C02 Account owner proof 仍是最重要的首登阻塞。

## roy1/roy2 最新合併後 Gate（2026-10-31）

- **ONB-01**：Admin 建帳政策 R-025 保留；C03 正常帳密可解析，但匿名 C02 不能作 pre-provisioned owner claim。A-027 integrated/partial，**原生建角身份路由 blocked**。
- **ONB-02**：C02→S02(status0)→C04(5u8)→S02(status0)→本地 UI（非 S03）；失敗會 C15(0 body)/state0x1f。DB commit/角色唯一性與 pending C15 僅能 designed，待原版帳號綁定。CT-041～044 planned。
- **ONB-03**：Map0/1/2 嚴格離線 494/494 PASS、但實際教學 Map ID/Spawn/C35 第二欄及資源發行版配對未證。CT-039 是離線子集、CT-040 原生教學 still not-run。
- **ONB-04**：C35 無 epoch，跨兩次同 pair 的延遲包原始 wire 不可辨。單 TCP 單 pending load；無法安全隔離時斷線/重新授權。SQLite/outbox/C33 seq7 皆為 Server designed。CT-045/046 planned。
- **ONB-05/06**：Born S44 start、PaperDialog C6C4/2 可依靜態契約開發；不代表任務已完成。原服發送時機、招募員 entity ID、教程怪物/技能/獎勵待 A-012/024～026。

詳見 [本輪整合規劃](merge-20261031-roy1-roy2.md) 與 [證據覆核](../04-analysis-integration/A015-A016-A027-A028-validation.md)。

## 最新 Client I/O 型開發切片（2026-10-31）

[可並行 DEV-IO-01～06](client-io-delivery-plan.md)／[6 條 Client 收發流程](client-io-flow-matrix.json)。正式 ONB 每項新增 `client_io_flows` 連結，明確分成 Client 可證事件、Server 自主決策與原生 CT。**不再把原服原始出生座標、首次 Born 派送時刻、原服驗證方式當 A/DEV 全部開工必要條件**；仍不得在沒有 C03 無角→NewUser UI 證據時宣稱原生完整創角成功，亦不可用未授權 C02 認領管理員帳號。

## 下一輪安全創角與 Native Client 的兩層出場門檻（2026-10-31）

[可繼續開發 SAFE-01～04 / 後續 WIRE-01～02](native-creation-next-iteration.md) 與 [機讀就緒關卡](onboarding-readiness-gates.json) 已建立。**Server AuthContext、登入帳號比對、PendingIntent/C04 原子性、C15/重送可立即繼續設計或合成測試**。但不能因帳號字串相同就開放 native C02：A-027 仍未證實 C03(no-character)→NewUser UI 或 C02 field1 真實帳號語意。新 CT-054 為 planned/not-run，不修改 Client，不猜非零 S02 錯誤碼。ONB-03/04 Map/CRC/Transfer、ONB-05 Script Domain 與此並行，不須推論原服出生/首次派任務政策。

## DEV-070-M 使用者最新決策（2026-10-31）

已確認「**多人進同一地圖**」；原本按 Character 建立的 DEV-070 synthetic scene 不能作為正式完成狀態。現在將 ONB-05 的 Server 場景調整為同 world/map 共用一份 NPC/怪物、每玩家獨立 Session 與教學進度。DEV-070-M 重構可立即開發，不需等原生封包；**A-004/A-011/A-024** 必須證明 Client 互見與實體封包後才加入原版 Client 傳輸，CT-055 planned/not-run。詳見 [共享地圖 ADR](shared-map-multiplayer-contract.md)。

## Roy1/Roy2 分支正式合併後（2026-10-31）

A-004/005/006/008/009/024（Roy2）與 A-007/019/020/025/026（Roy1）已回寫 main 的 `integrated` 靜態/合成有限成果。ONB-05 可由純內部 Scene 走向 **DEV-070-M 共享場景 + 可證 S07 非空 row 等 codec**，ONB-06 可建立 ScriptClose≠完成的 ledger。**原生 Client CT-055/070/080/081、R-031 真實教學出口都未通過**。看 [新開發計畫](post-roy-merge-implementation-plan.md) 與 [待分析工作](../03-analysis-requests/post-merge-analysis-queue.md)，不要要求分析者重做已證 opcode。

## P0 密碼相容性阻塞（使用者觀察，2026-10-31）

**目前原 Client 登入欄最多 8 字**，而 `as_server_roy/main` 的 `Pbkdf2PasswordHasher.ValidatePassword` 實際限制 **10～128 字**；ONB-01 即使帳號存在也可能登入失敗。**規格已更新但 DEV-030 程式尚未修正**：遊戲建帳/重設採4～8 ASCII 英數（自動產生仍建議8字）、Admin 身份/密鑰不受影響；原長密碼需管理員重設，不截斷；C03 正常登入與原始 UI 需 CT-019/037/050 驗證。此為本期**先修再測**的 P0 工作，不依賴 A-027 創角 UI。詳見 [4～8 字相容政策](native-game-password-4to8-policy.md)。

## Roy1/Roy2 再同步後的進度（2026-10-31）

ONB-03 MAP 494/494 可安全讀取，原版 Client 26/26 VA錨點核對，Roy1 的491是假陰性；可開始 DEV-060 MapResourceCatalog/TileQuery，但真正合法可走/出生/C35尚未證。ONB-05 多玩家共圖的 Monster00/World00各5個 YPF member已取得、Roy1 A-011資源庫與 S1A/C39可用；NPC imageID→YPF/motion及點擊畫面不明。R-014 商店/玩家交易 A-013已證部分 C4A/S42 C17/S6E C39/S2F，可先 Domain transaction，不能宣稱原 Client 可交易。詳 [新規劃](map-resource-actor-plan-20261031.md)。

## 第二輪 A-012/A-010 技能與教學選項（2026-10-31）

Roy1 A-012 補齊 C6C(1) 任務選項回覆的 ScriptRun context/key/value 與 C6C(4)/(2) 關閉/清理差異；Roy2 A-010 補齊技能開始/取消及 Add/Remove LastingSpell 六種 native packet 靜態子集。ONB-05/06 可先做 DEV-090 Script intent、DEV-080 cast/effect ledger；但 NPC→Script 綁定、官方冷卻/耗魔/施法動畫/狀態顯示/原始 Client E2E 尚未知。新的 CT-092～096 planned/not-run，詳 [下一階段規劃](new-quest-skill-dev-iteration-20261031.md)。

## 管理員 WEB UI（2026-10-31）：已規劃／未實作

已核對私有 Server 現有 `/admin` JSON 管理 API，但**瀏覽器 UI 不存在**。使用者明確要求此輪**只規劃**；P0 帳號建查停權/解封/重設與稽核用既有 API，P1 搜尋/角色需新 API，P2 GM/遠端管理需新安全設計。詳 [規劃](admin-web-management-interface-plan.md)、[驗收](../05-conformance/admin-web-management-acceptance-plan.md)、[未來實作前先確認](../00-governance/explicit-implementation-confirmation.md)。原版 Client E2E 與 Web UI 測試均 not-run。

## 新用戶決策：登入與創角是獨立入口，改密碼必須用遊戲 UI

ONB-01 C03 登入原有 Account 及 ONB-02 C02 直接創角為**互不要求事先操作的兩個 Client 入口**；管理端仍獨占 Account.Create。創角要直接驗證本次 UI 的 existing 帳號＋密碼，錯密/不存在/停權應回原版可理解錯誤、不建任何草稿/角色/grant；不再要求先有 C03 AuthContext，原 C02 field1/field2 和錯誤 S02/status 待 A-027/028 native 證據。新增 ONB-07 玩家正常改密碼只走遊戲內原生 UI（A-029），管理端密碼 reset 僅救援。見 [主規格](three-native-account-entry-policy.md)；原版 Client 未修改、Server 邏輯修改尚未獲授權、Native E2E not-run。

## 2026-10-31 三項新決策的交付欄

- **ONB-02／DEV-040**：移除 **「先 C03 Authenticated Session」的必要條件**，改 `C02` 帳號＋密碼認證後限本次創角 proof；目前私有 Guard 仍使用 `loggedIn`，**尚未修改程式**；A-027/028 + CT-100。
- **ONB-05／DEV-080**：怪物同 life 聚合每隊有效傷害、總傷害最高隊伍獨占、全員完整 100% EXP、各人獨立一次掉寶；其他隊伍無獎；需 party roster／winner/death/loot ledger；A-014/009/025/007 + CT-101。
- **ONB-06／DEV-090**：「不入學」不修改進度/任務/資產/場景，可再次點 NPC 重新詢問，反覆拒絕後仍可接受；A-012/023/026 + CT-102。
- 權威合併 [三項最新決策](three-policy-adjustments-20261031.md)；原生 Client CT 未執行，沒有修改私有 Server/Web/Asgard.exe。

## ONB-02 / DEV-040-NATIVE：Client 創角斷線（2026-10-31，僅規劃）

已核對 private Server 最新 source：C02/C04 一律 Close()（不發 S02），C15 empty 後 Close，TCP Host CloseConnection 即關 socket；CharacterCreationAccountGuard 的 loggedIn 要求另與產品政策不符，但 live C02 並**未執行 Guard**。優先在開發前做去敏 trace 辨 C02 前/後/C04 後/C15；後續改獨立 C02 AuthProof（無 prior C03）+ 欄位/地域 + 兩段 S02/C04/DB commit + C15 未提交清理 + native error mapping。A-030/CT-103..105 planned/not-run，正式 Server 實作仍需使用者另外確認。權威詳 [修正規劃](native-newuser-disconnect-remediation-20261031.md)。
