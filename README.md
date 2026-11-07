# Asgard Server Specification

2026-11-08：[地面保管、拾取競爭與私人掉落](04-analysis-integration/20261108-ground-item-custody-and-monster-loot.md)及[REA原生入口勘誤](04-analysis-integration/20261108-native-ground-drop-pickup-and-object-resync.md)。C08數量來源已證，真正拾取為C07，C0C只重同步；地面與背包圖源分開。持久保管／堆疊／競爭／重啟及普攻／技能私人掉落已接線，GUI仍待測；正式隊伍歸屬與全員EXP仍未完成，F13／F06及總表已同步。

2026-11-08：[怪物追擊、玩家受傷與原子復活](04-analysis-integration/20261108-monster-ai-and-atomic-character-revival.md)，以及[原生步進／墓碑證據](04-analysis-integration/20261108-native-monster-steps-player-death-and-respawn.md)。共用節拍、碰撞路徑、離線租約清理、死亡禁移動與同圖復活已接線；被動反擊、傷害與5秒復活是重建政策。原生GUI尚待驗收，F02／F06及總表已同步；完整多人引用與全地圖怪物仍未完成。

2026-11-08：[藥水、清單色差及實機回報](04-analysis-integration/20261108-consumables-color-and-manual-acceptance.md)。新增HP／MP藥水、堆疊合併、原子使用及v1→v2保留資料升級，653項回歸及真TCP通過。使用者已確認前輪衣裝買賣／銀行／排序／施法／特效結束／MP定時恢復；新藥水與禮服清單配色另列待測。

2026-11-08：[使用者指定暫行每分鐘恢復50%](04-analysis-integration/20261108-temporary-online-resource-recovery.md)，可調間隔與比例，不復活、不補BP、不累積離線回復；627項回歸通過，原生等待回復GUI待測。[特效預覽與原版對應缺口](04-analysis-integration/20261108-effect-preview-and-original-skill-binding-limits.md)另列，未將通用有限特效冒稱原版技能特效。

2026-11-08：[本輪實作與實機回報](04-analysis-integration/20261108-items-shops-ordering-and-client-feedback.md)、[物品保管與商店交易](04-analysis-integration/20261108-vault-shop-authority.md)及[原生清單契約](04-analysis-integration/20261108-native-shop-and-bank-items-contract.md)。背包／保管庫持久化、同交易買賣、舊視窗防重與重啟保存已接線；商品先限兩件明示重建衣裝，原生GUI待測。 同輪補[排序持久化](04-analysis-integration/20261108-slot-order-persistence.md)，並依新回報更正[4000循環／4006有限特效](04-analysis-integration/20261108-native-effect-lifecycle-correction.md)。

2026-11-08：[可見NPC、Spell分類、資源HUD與銀行增量](04-analysis-integration/20261108-bank-spell-and-hud-increment.md)。S08原件補證更正為u24色彩／full60B，修正上方MP／SP假滿；五類NPC可見即可交談，銀行接貨幣存提款。該增量後的最新實作及實測範圍見上方。

2026-11-07：[指定目標遠程法術與技能拒絕診斷](04-analysis-integration/20261107-targeted-magic-and-skill-feedback.md)、[原生target／Effect4000證據](04-analysis-integration/20261107-native-targeted-skills-effects-and-lasting-audit.md)、[Web測試資源補滿](04-analysis-integration/20261107-development-resource-refill.md)。相鄰格首擊回報仍待GUI複驗，不將新增遠程功能冒稱原問題已解。

2026-11-07：[五城33個導覽來源NPC配置](04-analysis-integration/20261107-five-town-npc-subsets.md)。新增四城27角色TCP走訪1010步通過；完整原服名單、精確位置外觀、交易服務與GUI另列待辦。

2026-11-07：[點選身上裝備斷線與原生卸裝修正](04-analysis-integration/20261107-equipped-click-and-native-takeoff.md)：C3A 與 C1F 分流、原子卸回背包及持久保存；479 項回歸與戰士 TCP 通過；使用者確認點選、卸裝、重新穿戴及重登保存正常（診斷Client環境）。[泳裝／禮服攻擊動畫證據](04-analysis-integration/20261107-clothing-attack-action-presence.md)保留原版戰鬥政策未知。

[Server開發追蹤 Excel](06-development-tracking/README.md)：功能總表及33份功能明細，按分析、實作、自動測試與遊戲實測分欄。2026-11-07新手流程暫緩。

技能／普通攻擊新增[Web深入分析工作台](03-analysis-requests/web-skill-review/README.md)：已先盤點A-009／010／025等既有成果，列8個子任務及ChatGPT／Claude共用提示詞、結果契約；不重複建立正式A編號。

2026-11-07：[角色成長／七職業重建技能／持有裝備整合](04-analysis-integration/20261107-career-support-and-playable-integration.md)。能力窗診斷副本由使用者確認數值／懸停通過；預言者／阿修羅是職業名稱，本版Client支援待確認。

2026-11-07：[斯歐米NPC第一版配置](04-analysis-integration/20261107-suomi-npc-configuration.md)：導覽六角色、原生唯讀介紹、位置來源及通行核對；完整原版名單與交易服務仍分列待辦。

版本：0.1.0-draft · 日期：2026-10-30

這是本作者及其他開發者共同依循的、與實作語言無關的 Server 規格專案。任何實作，包括作者的私有 Server，都應依同一版本實作與驗收。此 repository 不包含作者的 Server 原始碼、部署憑證、帳號資料庫或原始遊戲檔案。

本版是可繼續補完的規格基線，**不是完整遊戲協定已還原的宣告**。目前主要證據來自指定台灣版 Client 與單人原型；戰鬥、多人、經濟等缺口明確列在分析需求。原型的實作行為不得直接當成原服規則。

## 本地問題與 Server 修正交接（2026-10-31）

本工作收集本地測試問題，現在亦依最新授權**直接開發私有 `as_server_roy`，同步補分析與公開規格**。目前入口：[問題紀錄](03-analysis-requests/runtime-issues.json) → [修正合約](02-server-planning/runtime-feedback-handoff.md) → [直接開發流程](00-governance/direct-development-workflow-20261101.md)。使用者直接回報即可，不需在分析與開發之間代傳。

交接已按 `as_server_roy@b8e212e` 唯讀核對：後端創角驗證及部分診斷已有實作，原生創角 wire 仍待 A-030。舊原型的置中、獨立衣色及修改 Client 的主選單預覽分別標記，不能當成新 Server 原版驗收。以下保留的歷史進度應按所載 commit／日期閱讀；帳號入口的最新政策是 Login／NewUser／ChangePassword 獨立，不要求 C02 前先 C03。

## 從這裡開始

直接開發首個World增量：[參考原型的S02／C43分析整合](04-analysis-integration/world-ui-prelude-c43-20261101.md)／[Server交付與使用者測試範圍](02-server-planning/world-ui-prelude-increment-20261101.md)。合成回歸與HTTP/TCP已通過，原生畫面另待使用者操作。

**2026-11-01 工作方式更新**：[直接開發、同步分析與規格](00-governance/direct-development-workflow-20261101.md)。本對話現在可在私有roy直接實作，不受下方歷史僅分析分工限制；spec仍公開且不收私有實作。使用的正式本地spec路徑為 `E:\Asgard\asgard_server\as_server_spec`。

需求來源請見 [使用者需求／程式分析／Server設計的歸因規範](00-governance/requirement-origin-policy.md)。R與PAR逐項附來源，保留使用者提出的功能目的；封包證據與實作建議另列，不把兩者混為需求起源。

2026-11-01 新增：[Python原型／新版Server能力差距](04-analysis-integration/prototype-parity-audit-20261101.md) → [補齊批次與Server合約](02-server-planning/prototype-parity-delivery-plan-20261101.md) → [機讀待辦](02-server-planning/prototype-parity-backlog.json) → [批次驗收](05-conformance/prototype-parity-regression-20261101.md)。按 `as_server_roy@e93c9a17` 區分已實作後端、未接通原生操作與未驗收；不將原型捷徑或EXE patch列為正式Server要求。

1. [共同開發流程](00-governance/workflow.md)：需求到驗收的固定編號與交付規則。
2. [Server需求](01-server-requirements/README.md)：完整系統範圍、優先序、驗收及非功能需求。
3. [Server規劃](02-server-planning/architecture.md)：系統邊界、資料責任、狀態機與階段路線；另見[邏輯介面與資料](02-server-planning/interfaces-and-data.md)。
4. [分析需求](03-analysis-requests/README.md)：依系統／功能／情境分派問題。
5. [分析結果整合](04-analysis-integration/README.md)：封包、Client行為、遊戲規則與情境整合。
6. [獨立實作指南](05-conformance/implementer-guide.md)：共用測試向量及相容性宣告。
7. [目前基線及已知缺口](00-governance/baseline.md)：先讀以免沿用歷史文件的舊結論。

可機讀資料：requirements.json、systems.json、requests.json、packets.json、scenarios.json及traceability.csv。它們與說明文件放在各分區。

開發原始碼在另一個獨立 repository。共享規格不引用該 repository 的函式或私有套件作為行為定義。別人不需取得作者原始碼即可實作已完整指定的profile。

授權條款尚待專案擁有人選擇，見[分享與授權決策](00-governance/sharing-and-license.md)。本repository只維護可分享規格；作者的私有Server實作不發布在這裡。

已有研究的整合情況請看[既有分析覆蓋表](04-analysis-integration/analysis-coverage.md)：逐份列出舊文件、新規格落點及哪些只保留摘要／身份索引。

## 首次玩家流程：登入 → 創角 → 進入新手教學（2026-10-31）

已確認：**只有管理員能建立 Account；玩家透過原 Client 登入及自行建立 Character，不得自行註冊 Account**。閱讀 [R-025～028 需求](01-server-requirements/first-login-onboarding.md) → [ONB-01～04 規劃](02-server-planning/first-login-onboarding.md) → [A-021～023 待分析](03-analysis-requests/README.md) → [SCN-007～010 情境](04-analysis-integration/scenarios.md) → [CT-011～020 計畫](05-conformance/onboarding-test-plan.md)。目前為規劃，不是原 Client 已完成驗收。

## 首次玩家：管理建帳 → Client 登入 → 創角 → 新手教學（2026-10-31）

已確認使用者需求：**帳號由管理員透過獨立後台建立，玩家只能使用原始 Client 登入並建立角色，不能由 Client 註冊帳號**。新的規格鏈： [R-025～028](01-server-requirements/first-login-onboarding.md) → [跨系統 ONB 規劃](02-server-planning/first-login-onboarding.md) → [A-021～023](03-analysis-requests/README.md) → [SCN-007～010](04-analysis-integration/scenarios.md) → [CT-011～020](05-conformance/onboarding-test-plan.md)。目前是規劃／待分析，不是新手地圖已通過原 Client 實測。

## 首次玩家流程已規劃延伸至教學完成（2026-10-31）

本次新增 **R-029～031**（教學 NPC/怪物、技能/目標、完成/退出）、**A-024～026**（待逆向）、**SCN-011～013**（分析必要）與 **CT-021～028**（planned）。

[最新 Server 進度板](02-server-planning/onboarding-delivery-board.md) · [A-XX 分析交付包](03-analysis-requests/onboarding-assignment-pack.md) · [ONB-01～06 開發批次](02-server-planning/work-items.json) · [教學 Server 詳細規劃](02-server-planning/tutorial-runtime-plan.md) · [CT-021～028 驗收計畫](05-conformance/tutorial-test-plan.md)。

管理員建立 Account、玩家只用原 Client 登入的 R-025 決策不變；本次規劃仍不代表教程已開發或跑通原 Client。

## 分析交付與開發／實機驗收分離（所有新舊任務）

為防止 A-021 類「逆向分析等新 Server 的實機驗收、Server 又等逆向分析」的循環依賴，**所有 A/DEV/CT 接案者都需按 [phase-gates.md](00-governance/phase-gates.md) 的獨立出場條件工作**。A-021 有專用 [交付清單](03-analysis-requests/A-021-acceptance.md)；共用要求由機讀 requests.json、work-items.json 以及 CI [validate-phase-gates.py](tools/validate-phase-gates.py) 驗證。分析可完成並保留 CT=not-run，前提是證據支持範圍與未解事項如實交代。

## roy1 A-021 合併後 review（2026-10-31）

`task_a/roy1` 已 fast-forward merge 並經 Asgard.exe BIN 靜態核對；已確認 C02 region variants、C04 五 u8、S02 status/string 及 UI 0x1d→0x1e。**A-021 只達靜態 partial handoff**，新開 A-027（前認證身份／帳號權限）及 A-028（C04 最終回覆/轉場），CT-029～032 計畫中。詳見 [roy1 review](04-analysis-integration/A-021-roy1-review.md)。未經認證的 C02 絕不能認領管理員已建立的帳號。

## 2026-10-31 A-022/A-023 整合後的分析優先順序

[下一輪分析順序與 DEV/CT 解鎖條件](02-server-planning/analysis-priority-after-A022-A023.md) | [BIN 靜態驗證與 Born 來源限制](04-analysis-integration/A-022-A-023-merge-validation.md)。A-027/A-015 為首批並行，A-028 隨後；Script 相關 CT 使用 033～035，保留原有 CT-029～032。

## A-001/A-023 最新可實作交接

[2026-10-31 roy1/roy2 新成果驗證](04-analysis-integration/A-001-A-023-merge-verification.md) · [Script 啟動/關閉 Server 規劃](02-server-planning/script-lifecycle-contract.md)。A-001 seed0..9 binary codec、A-023 S44(1,0) named start／C6C2/4 close 子集可先開發；原服 first-login policy／NPC mapping 未確認，原生 Client CT 均 not-run。

## A-002 登入／轉服規劃

[SessionTransfer 契約](02-server-planning/session-transfer-contract.md)／[A-002 新證據驗證](04-analysis-integration/A-002-merge-verification.md)：S03 addr/port/token 引導新 TCP，C10 只寫 raw token。已勘誤 0x4A8370 真正是 S03 handler 而非 C25。CT-037/038 native not-run。

## task_a roy1/roy2 最新分析合併（2026-10-31）

[A-015/A-016/A-027/A-028 首次登入、創角、恢復、地圖的 Server 整合規格](02-server-planning/merge-20261031-roy1-roy2.md) · [原始二進位與 MAP/Born 覆核報告](04-analysis-integration/A015-A016-A027-A028-validation.md) · [A-014 聊天／密語／組隊／公會安全開發契約](02-server-planning/social-contract.md) · [A-015 格式與盤點研究結案界線](task_a/roy2/A-015-closure-review.md)。保留原 client/S02/C15/Script 與 494 MAP 的部分已證成果，沒有將建角原生 owner proof、首次出生、群組 type/op 或 Client E2E 宣稱通過。CT-039～040 為地圖內容、041～046 為創角／恢復、047～049 為社交。

[A-017 管理端 API／停權解封／去敏稽核](02-server-planning/admin-operations.json) · [A-017 原始報告](03-analysis-requests/A-017-roy1-admin-audit.md)。主線測試 CT-050/051 planned，不冒認實機通過。

## 新版工作規範與 Client 收發導向 Server 路線（2026-10-31）

**所有接案者先讀**：[工作軌／責任／禁止自行建分支](00-governance/task-ownership-and-client-io.md) → [Client I/O 交付規範](03-analysis-requests/client-io-handoff-standard.md) → [新版任務模板](03-analysis-requests/request-template.md)。新增 [Server 可開發的 DEV-IO-01～06 縱切規劃](02-server-planning/client-io-delivery-plan.md)、[6 條機讀 Client I/O／Server decision 矩陣](02-server-planning/client-io-flow-matrix.json) 與 [分段驗收計畫](05-conformance/client-io-verification-plan.md)。CI 將強制 A 任務分類與交付要求；實機 CT 全部仍須獨立執行。

## 暫行創角帳號一致性政策

玩家在原 Client 創角輸入的帳號與已驗證登入帳號不同時，Server **拒絕創角**；無登入也拒絕。Client 不修改、輸入框不鎖定。詳見 [創角帳號比對規劃](02-server-planning/character-account-match-policy.md)；A-027 的原生 UI 入口仍 partial。

## 下一階段安全創角規劃與 A-027 精準證據

已新增 [Server SAFE-01～04 / WIRE-01～02 / WORLD / SCRIPT 的可開發切片](02-server-planning/native-creation-next-iteration.md)、[機讀就緒關卡](02-server-planning/onboarding-readiness-gates.json)、[A-027/020/022/028 必答的 Client 收發/畫面問題](03-analysis-requests/next-client-io-evidence.md)、[CT-054 原版 Client UI 路徑驗收](05-conformance/native-creation-gate-test-plan.md)。登入帳號與創角輸入帳號不同必須拒絕；原 Client 不修改；即使 Server SAFE 工作可做，Native NewUser route 未證時仍 fail closed，CT-054 目前 not-run。

## 2026-10-31 決策：多人同世界同地圖

[ADR-007 多人共用場景](02-server-planning/shared-map-multiplayer-contract.md)：新手教學和一般公用地圖，所有進同一 world/map 的玩家共享同一份 NPC/怪物狀態；玩家各有角色 Session 與進度。DEV-070 現有每角色 synthetic Scene 須做 DEV-070-M 重構；原版 Client 互見/怪物同步待 A-004/011/024，新增 CT-055 planned/not-run。

## 2026-10-31 — Roy1/Roy2 最新成果合併

已合併 `task_a/roy1`、`task_a/roy2` 的歷史與原始證據並統一 A／PKT／SCN／CT，保留 **CT-054 原生創角、CT-055 多人共圖**；分支重號測試重新編為 CT-056～081。新增 [Server 經分析更新的接續規劃](02-server-planning/post-roy-merge-implementation-plan.md)、[剩餘 Client A 工作](03-analysis-requests/post-merge-analysis-queue.md)、[CT 來源對照](05-conformance/ct-id-remap-roy1-roy2.md)，原 Client 不修改、無新 native E2E pass。

## 2026-10-31 新手教學與素材五檔補證

已實際檢查本輪上傳的 `nNewJoin01.dat`、`PaperDialog.dat`、`PaperDialog02.dat`、`Monster00.dat`、`World00.dat`。初級學校三頁/接受拒絕、獨立 PaperDialog02 開始取消、Monster/World 各五個 YPF 成員的 SHA/索引已證；**尚不能宣稱原生 NPC 綁定、怪物畫面、官方目的地、教學畢業或 Client E2E 已通過**。

[原件分析](04-analysis-integration/new-asset-samples-20261031.md) · [Server 就學流程規劃](02-server-planning/novice-school-admission-flow.md) · [驗收項目](05-conformance/new-asset-validation-plan.md)。

## P0：原版 Client 遊戲密碼允許 4～8 字（2026-10-31 最新決策）

使用者發現遊戲登入框最多 8 字；實際私有 Server `as_server_roy/main` 的憑證驗證目前卻要求**至少10字**，因此不相容。已新增 [原生 4～8 字遊戲密碼相容政策／DEV-030 修正清單](02-server-planning/native-game-password-4to8-policy.md)：新建／重設遊戲密碼採4～8 ASCII 英數（自動產生建議8字）、**不截斷舊密碼**，管理 API key 不受此規則限制，加入線上登入限速等補償；未來可能修改主程式延長長度，必須另立已驗證 Client profile，現在不修改。A-020/A-002 仍需證實原 Client UI/送包；本次是規劃與交接，**Server 程式未在本 repo 修改，Client CT 未驗收**。

## Roy1/Roy2 當前分支最新成果再整合（2026-10-31）

Roy1 A-011/A-022/A-013 及 Roy2 A-015 已交叉核對；原件 MAP 494/494，Roy1 491/494 由索引+4B錯誤造成，已修正。新增商店/玩家交易部分 Client I/O (CT-087～089) 與地圖原件/實機驗收 (CT-090/091)。詳 [整合審查](04-analysis-integration/merge-review-roy1-roy2-20261031.md)、[Server 下一輪需求](02-server-planning/map-resource-actor-plan-20261031.md)。保留 Client 不改、4～8字遊戲密碼、多玩家共用地圖決策；原生 Client E2E 尚未完成。

## 2026-10-31 第二輪增量：A-012 任務選項與 A-010 技能／BUFF

Roy1 新增 C6C(1) name/context/key-value ScriptReply 與 C6C(4/2) close/cleanup 研究，Roy2 新增 C4D/C56/S52/S48/S2C/S2D 技能/持續效果協定。保留經濟 CT-087～089 與地圖 CT-090～091，新 quest CT-092～094、skill CT-095～096。對話選擇不是已完成 Quest，S2C 是 opcode0x2C（AddLastingSpell）；Server 新規劃見 [技能與任務](02-server-planning/new-quest-skill-dev-iteration-20261031.md)，[新增研究核驗](04-analysis-integration/merge-review-roy1-roy2-new-quest-skill-20261031.md)。原 Client 不修改、4～8字密碼、原生 E2E still not-run。

## 管理 WEB 介面：只完成規劃（2026-10-31）

現有私有 Server 只有可呼叫的 `/admin` JSON API，**沒有管理網頁**。本次使用者更正為「只規劃不實作」，已整理 [UI P0/P1/P2 設計](02-server-planning/admin-web-management-interface-plan.md) 與 [驗收案例](05-conformance/admin-web-management-acceptance-plan.md)，並建立 [日後實作前必須提醒確認的規則](00-governance/explicit-implementation-confirmation.md)。Roy1/Roy2 增量 [審查](04-analysis-integration/roy-branch-web-admin-sync-20261031.md) 只同步已證離線資料，未修改 Server/Web/Client 程式。

## 最新玩家帳號流程：登入、創角、遊戲內改密碼是獨立入口（2026-10-31）

**使用者已確認**：管理員先建 Account，原版 Client 的 **登入 C03** 和 **創角 NewUser C02** 是兩個獨立入口。玩家創角直接輸入預建帳號及密碼，Server 驗同一 CredentialStore 才能建角色；錯密/不存在/停權應回原版 UI 錯誤、無草稿/Character/Grant。**舊「創角一定先 C03 登入」假設作廢**。玩家正常改密碼必須使用原版遊戲內 **修改密碼 UI**，管理端重設僅救援；其真正 opcode/回覆目前待 A-029。新增 [三入口權威契約](02-server-planning/three-native-account-entry-policy.md) 與 CT-097..099 規劃。**本輪只規劃，不修改 Server/Client/Web 程式，Web 日後實作仍需再次確認**。

## 最新三項 Server 規則（2026-10-31；僅規劃）

1. **創角 Guard** 不須先登入 C03：本次 C02 既有帳號+密碼驗證，產生僅限創角授權 proof；私有 Guard `loggedIn` 依賴目前仍是舊實作，待另行確認開發。
2. **共享怪物**：累加各隊有效傷害，**最高總傷害隊伍**得獎；隊伍全員各得完整怪物 EXP，並且每人**獨立判定一次掉寶**，不平分，也不是每人必掉。
3. **新手入學**：選「不入學」是沒有任務/獎勵/場景副作用的拒絕，可再次點 NPC 重問，也可以稍後接受。

完整 [最新決策](02-server-planning/three-policy-adjustments-20261031.md)、[CT-101](05-conformance/party-monster-reward-test-plan.md)、[CT-102](05-conformance/tutorial-refuse-reask-test-plan.md)。新增 R-033/034、SCN-018/019、CT-100～102 仍 planned/not-run；**這輪不修改 Server/Client/Web 程式**。

## 2026-10-31 創角提交斷線源碼追查及修正規劃（僅設計）

原版 Asgard.exe 創角輸入 ID/PASSWORD/CONFIRM/NAME/E-MAIL 提交後顯示重新連線；核對 private as_server_roy/main@ad84f9 後，LoginWireSession.HandleAsync 的 C02/C04 **無條件 Close（0 S02 frames）**，GameTcpProbeService 立即退出並關閉 Socket；C15 合法 body 後也 Close。現有 CharacterCreationAccountGuard 另有過時 loggedIn 要求，**但 live C02 根本未走到 Guard**，不能錯誤聲稱 Guard 是立即斷線的已證呼叫點。現場首個封包/斷點仍缺原始 Client 去敏 trace，未證帳密錯。見 [開發交接及根因](02-server-planning/native-newuser-disconnect-remediation-20261031.md)、[A-030 UI/EMAIL 補證](03-analysis-requests/A-030-native-newuser-disconnect-fields.md)、[CT-103..105](05-conformance/native-newuser-disconnect-acceptance-plan.md)；A-021/027/028/020 沿用已證部分。**全部規劃，沒有修改私有 Server/DB/Web/Client、沒有新分支**。

## 2026-10-31 Roy1/Roy2 新增 A-029/A-030 來源證據整合

已同步現有 `task_a/roy1` A-029 改密碼 C26（三個 string8）、A-030 C02 地區 widget 與 S02 非零文字/C15 靜態分析；`task_a/roy2` 原研究提交先前已在 main。保留最新私有 Server 已實作的獨立創角 Domain／RI-005 分階段 timeout/診斷，不宣稱 Native Client 創角已完成。完整 [分支整合與驗證](04-analysis-integration/roy1-roy2-password-newuser-sync-20261031.md)、[更新的 DEV 交接](02-server-planning/roy1-roy2-new-evidence-dev-plan-20261031.md)。

最新開發：[新角色自動進場與權威移動](02-server-planning/native-new-character-movement-increment-20261101.md)，含位置保存、v6備份／遷移及GUI驗收界線。

[Born 原生引導增量](02-server-planning/born-intro-implementation-20261101.md)：精確資源／CRC驗證、S44啟動與C6C關閉、獨立持久確認；260項測試及本機TCP通過，GUI仍待驗。
