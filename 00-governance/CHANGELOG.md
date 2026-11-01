# 變更紀錄

## 2026-11-02 原生角色能力初始化與持久數值

依能力窗異常追至StatusDialog欄位，補上旗標0078的S08完整初始化，每次地圖提交後以持久狀態投影，既有角色與新角色首次缺值才建基線，重登不重置。舊SQLite缺表先一致性備份，帳號／位置／職業／金鑰保留。384項.NET、五職業完整TCP與固定環境啟停測試通過；出生數值明示為Server設計，不宣稱原版公式或hover當機已修復。見[契約與待測](../04-analysis-integration/20261102-native-status-initialization.md)。

## 2026-11-02 個人帳號及既有 Web 管理金鑰入口

依使用者需求補本機個人帳號與既有金鑰開啟管理頁捷徑，沿用 Server／資料庫，不重產金鑰或改 worlddemo。授權只讀 HTTP 200，捷徑模式／轉義及 PowerShell 語法檢查通過。另記錄完成候選教學到城鎮後的能力窗當機，確認未接 S08 初始化與職業／稱號欄位來源分離；尚未把症狀當成已證當機原因，見[契約與待修項目](../04-analysis-integration/20261102-personal-account-admin-and-status-window.md)。

## 2026-11-01 實機學校畫面錯位修正

使用者回報Map7座標30,34但場景偏右下；確認是候選產生器把S04相機偏移誤當絕對座標，22,28改回8,9。精確比對generated v1後先備份再原子更新v2，不改DB／角色／金鑰；四項遷移測試、舊設定負向與修正後五職業TCP通過，補上先前未檢查的相機公式。需原角色重登復驗GUI，見[原因與修正契約](../04-analysis-integration/20261101-tutorial-camera-offset-correction.md)。

## 2026-11-01 三層圖塊與候選地理離線核對

REA確認非零tile word減1才送影格索引，0略過，並依序畫三層；新增有界YPF圖塊預覽，八張圖引用全部可解碼。公開素材／預覽hash、精選指令與界限，不公開原圖或把地形當原版城鎮身份；待測profile與使用者進度未變。見[分析結果](../04-analysis-integration/20261101-native-tile-preview-and-geography.md)。

## 2026-11-01 完整教學固定環境與集中實機入口

提供與舊招募員測試分開的完整路線持久入口，保留profile／帳號／金鑰／進度，Server就緒後自開診斷Client。準備模式及重複準備驗證通過，尚未建立使用者DB或密碼。新增一次涵蓋創角、入學、講師、攻擊、選職、出圖與重登的[人工驗證清單](../05-conformance/20261101-complete-tutorial-manual-run.md)；實機結果pending，不升級Native CT。

## 2026-11-01 原生職業欄位與持久選職投影

REA追出StatusDialog由HumanInfo+5及BasicString455+code顯示職業，確認S05 body5／S33 body10與五職業明示數字映射。Server選職結果發保留pose的S33再發S44，切圖／重登讀保存職業；避免中途S05重建自身物件。353項測試通過，原生GUI及地圖身份仍未驗。見[證據與契約](../04-analysis-integration/20261101-native-career-appearance-projection.md)。

## 2026-11-01 五職業真實TCP完整教學路線

以真實MAP／腳本設定及獨立Host，五名角色各經C02／C04建角、加入轉學校、講師、選職、學校重登、C13扣血／死亡／靜默重生、各目的圖提交及再重登通過；唯讀核對完成時點、職業、首次checkpoint與hit audit，逐socket檢查S2C ordinal。原生嘗試因computer-use視窗核准逾時未取得畫面，沒有升級Native CT或城鎮身份。見[驗證範圍與結果](../04-analysis-integration/20261101-tutorial-route-tcp-evidence.md)。

## 2026-11-01 教學地理線索與完整候選內容入口

核對生活講義的五職業城鎮名稱，REA追出WorldMap依runtime metadata選HTML或內建圖像；提供的HTML／7z已有本地修改，不能當官方綁定。私有工具新增明示候選profile，含六張真實MAP、教學NPC／戰鬥／選職／五條目的地，獨立Host整體載入及seed0 greeting通過；城鎮身份與完整GUI仍未驗，正常開發入口未變。見[分析與候選契約](../04-analysis-integration/20261101-tutorial-geography-and-content-profile.md)。

## 2026-11-01 教學戰鬥啟動設定與TCP背景投影

啟動流程傳遞明示戰鬥profile，新增固定producer的傳送條件selector；每連線串行poll共享死亡／重生，保持單一socket read、ordinal與寫入順序，背景輸出不延長Client期限。新增loopback TCP與啟動拒絕測試；既有啟動器與使用者Server未變動，完整教學及原生戰鬥GUI仍未完成。見[TCP與設定契約](../04-analysis-integration/20261101-training-combat-transport.md)。

## 2026-11-01 共享教學怪物與普通攻擊結算

新增持久共享HP、攻擊冷卻、生命編號與重生，以及C13 Host結算；成功扣血才原子寫入practice事件。343項Server測試涵蓋並行單次死亡、重登、舊ref失效、回滾與五職業流程取消直接注入。Program／啟動器及TCP背景投影仍待接線，沒有宣稱原生GUI可玩或完整教學完成。見[權威結算契約](../04-analysis-integration/20261101-training-combat-authority.md)。

## 2026-11-01 普通攻擊目標與S13／S5F接收入口補證

REA確認鍵盤攻擊producer可收到0，補兩階opcode派送表到S13／S5F handler及動畫參數流；新增嚴格14/31-byte S13 codec，333項Server測試通過。公開精選原件指令與identity，沒有啟用Host扣血或攻擊完成事件；普通攻擊仍待可信怪物／距離／頻率結算及GUI驗證。見[分析與契約](../04-analysis-integration/20261101-native-combat-target-and-effect.md)。

## 2026-11-01 生活與戰鬥教學NPC

接上原始nNewLife01／nNewWar01的Merchant對話與固定版本觀察事件；原件初頁取消與最後關閉都可能只Dispose，因此只據實記TALK後關閉，不宣稱讀完／戰鬥通過。329項Server測試涵蓋取消、偽造完成、對話互斥與五職業傳送流程經真實Host處理產生兩項教學事件；攻擊仍是明示合成注入，未啟用未知學校地圖或宣稱完整GUI驗收。見[教學NPC契約](../04-analysis-integration/20261101-tutorial-lesson-npcs.md)。

## 2026-11-01 分職業傳送師與目的圖提交

接上已保存職業的原生傳送對話、顯式五職業目的地與版本化教學條件；正確C35才將位置、transfer事件、教學完成旗標及完成事件同交易提交。318項合成／SQLite測試涵蓋五條路線、條件缺漏、錯C35／中斷、重登、計畫竄改、備份及事件寫入失敗整筆回滾。教學事件在測試中注入，尚未接生活／戰鬥NPC及實際戰鬥；原版地圖綁定、職業投影與完整GUI仍未完成，不能以旗標寫入能力宣稱整體目標達成。見[完整契約](../04-analysis-integration/20261101-tutorial-town-departure.md)。

## 2026-11-01 招募員點選與原生加入對話

追通S07 kind1互動模式及C43 subtype0，核對helper候選素材與Merchant依賴；roy36c71fd接招募員顯示、近距離點選、原有加入對話、拒絕／重開及持久接受紀錄。275項測試與招募員／基準TCP通過，GUI待驗。綁定明示本地復原試驗，加入不當作畢業；完整教學、選職與各職業城鎮目標保持未完成。

## 2026-11-01 新手教學優先與正常玩法切圖歸因

依使用者明示改以教學完成為主，測試空檔續做換衣／獨立衣色。管理傳送與NPC／技能／傳送點入口分開，共用載圖核心。核對19份原始Script資源及候選加入／選職／傳送介面，訂正舊缺檔限制；roy e12cec2補C6C選項回覆解析，273項測試通過。NPC綁定、職業數值與原服完成／出圖仍待分析接線，不把Born關閉或codec通過當教學完成。

## 2026-11-01 重登驗收、背景音樂接線與後續待測

使用者確認同Client連續兩輪離開重登、位置與最後關閉正常。royfdb4d81補S19音樂分支、單圖版本綁定本地選曲及播放／停止／停用設定；270項測試與三模式TCP通過，聽覺仍待驗。規格補下一批換衣／獨立衣色、在線兩圖、Web工作台的交付順序與集中待測表；不把舊原型或副本結果升級原始CT。詳見[下一批佇列](../02-server-planning/next-increments-and-test-queue-20261101.md)。

## 2026-11-01 同Client離開後重登修正

使用者確認完成提示與首次退出不再當機、重啟登入位置正確；另明確回報回登入頁後同Client登入卡住。修正先前C0B一律關TCP的策略：撤銷精確世界lease、清世界權限、保留同TCP回LoginReady，後續C03重新驗證。roy7c35793的265項測試與同socket重登入場TCP通過，GUI待驗；原始Client CT不升級。詳見[同Client重登合約](../04-analysis-integration/20261101-same-client-relogin.md)。

## 2026-11-01 創角完成提示與首次退出例外

使用者確認C44修正後持續在線、重登位置正確；另回報Born後空白框與新角色退出卡住。補最終S02原生MessageDialog作用、C0B正常退出合約，以及Windows當機與快捷列數未初始化證據。royfd3ffeb提供非空提示、正常退出分類及獨立Client相容副本；265項測試與本機TCP通過，副本GUI重測待完成。原始Client正式CT不升級。詳見[分析與合約](../04-analysis-integration/20261101-creation-notice-and-quit.md)。

> 2026-11-01 勘誤：C35 第一欄為 MapData 的 map_ref，不是 MAP 檔頭+4；地圖6為 00060F90。以下舊值／推論由[第一欄勘誤](../04-analysis-integration/c35-map-reference-correction-20261101.md)取代，其他證據限制仍適用。


## 2026-11-01 直接開發：本地原型UI前置／C43回補

依使用者最新要求，參考Python原型的已觀察一般登入入圖順序，在roy的native-map trial補S02 UI初始化與loading C43精確六bytes的有界延後處理；公開新增證據／Server合約與測試入口用途，不含私有實作。248項合成回歸及真loopback HTTP/TCP smoke通過，已準備獨立DB／埠由使用者操作。原版GUI、正式走路與ADR-008創角後World仍未宣稱完成。

## 2026-11-01 改為直接開發與同步規格；自行監測工具

依最新使用者指示，實作直接放私有roy，分析／規劃放公開spec；更新根AGENTS、工作流程與歷史限制的覆蓋關係，使用指定的asgard_server兩個repo路徑。延續使用者自行使用監聽工具的需求，roy新增程序／TCP採樣入口與可選的Client socket metadata探針；公開spec只收行為與驗收合約，不收實作或runtime原件。舊分析／原版CT結果不因此升級。

## 2026-11-01 需求來源歸因更正

依使用者要求，R與PAR補來源分類、對話／既有決策索引及user／analysis／design分欄；特別標註立即切圖、Web管理、BGM、獨立衣色、人物置中、動畫可恢復及批次／監測為使用者意圖。S66/C75與5秒政策不冒稱使用者逐項要求，epoch等技術方案不冒稱原服規則或使用者原話。找不到原始訊息者保留來源待補或既有spec決策歸因；功能、優先序、驗收與Server實作均未因此改動。

## 2026-11-01 Python原型與新版Server差距整合

唯讀稽核 as_server_roy e93c9a17 與本地Python原型，新增逐項能力對照、可機讀缺口／source hash索引、P0/P1交付合約與連續批次回歸。補在線切圖、權威移動／最新位置、更衣／衣色、S66/C75、S19 BGM、角色管理與回報更正；原型C35寬鬆、夾邊界、無限衣櫃及Client patch不帶入正式Server。修正P0 Web「尚不存在」與C02「一律Close」的過期進度，ONB保留原版CT not-run並附分組實作快照。Server／DB／Client均未修改或執行測試。

新增CT-115時間同步／階段邊界驗收與R-001/019/021追蹤；A-001/A-020只補S66/C75第二欄／phase／重送的增量問題，不重開同義分析或拿prelogin測試冒充時間同步通過。
## 2026-11-01 不裝 WinDbg 先派 Client 分析任務：A-028/A-031/A-020

使用者要求以既有 WER、修改版 EXE 的差異、Server JSONL 和原件分析派工。已建立 GitHub Issues [#7 A-028/Roy2](https://github.com/we88ec3-prog/as_server_spec/issues/7)、[#8 A-031/Roy2](https://github.com/we88ec3-prog/as_server_spec/issues/8)、[#9 A-020/Roy1](https://github.com/we88ec3-prog/as_server_spec/issues/9)；更新 `requests.json` queued follow-ups、`runtime-issues.json` 新 RI-006/007、[統一派工文件](../03-analysis-requests/dispatch-20261101-preview-crash-and-world-entry.md) 與 Runtime feedback handoff。保留既有 A 的 integrated 靜態成果，修改版僅排錯，不需要 WinDbg 作靜態分析前提；GitHub 人員尚未認領。**僅變更 as_server_spec/main，不更改 Server/EXE/DB，也未建立分支**。

## 2026-11-01 RI-008：實際比對修改版 EXE 的 0xC0000005 崩潰位址

讀取用戶提供的 Preview 與原件，確認修改版新增 .tipfix、.text 8 個差異區塊；Windows WER RVA 0x141264 的實際 Preview 指令為 mov [eax+4],edx。創角 S02(0) Region3 callback 是其可能 caller 之一，缺 EAX/stack 無法證實真正根因。列出 Preview Region3 條件跳轉等 Patch 候選，只供排錯，不能當原件 Client 研究成果。詳 [RI-008](../04-analysis-integration/20261101-preview-exe-crash-debug-diff.md)；未修改 Server 或任何 EXE。

## 2026-11-01 修改版 Preview 僅供排錯，不得冒認原版遊戲分析

使用者明確更正 `Asgard-main-menu-preview.exe` 經調整僅供排除錯誤；WER APPCRASH `0xC0000005` / RVA `0x00141264` 僅是修改版 debug evidence，不可直接套到原版 `Asgard.exe` 的 VA `0x00541264` 當成已證原版 faulting instruction。更新 RI-006/007 與 P0 分析隔離標記。Server C25 後 `Continue()` 零 S2C 屬程式碼事實，但原版 Native Client E2E 仍 not-run。只修改 `as_server_spec`；沒有修改 Server/遊戲 EXE。

## 2026-11-01 RI-007：登入成功但 Native World C25 後沒有回覆；Windows preview.exe 當掉證據

新上傳 84 packet／17 close／4 validation 累積 Log，確認一般 C03→S03(轉服)→新 TCP C10/C25 成功，卻停 WorldGranted 零 S2C。唯讀核對 Server `LoginWireSession.case 0x25` 的 `_worldFixture=null` → `return Continue()`，定位 DEV-ENTRY 原生地圖載入未接通；不是密碼、C25 或 C35 錯。Windows Application Error 1000 指向 `Asgard-main-menu-preview.exe`，校正先前 RI-006 原版 runtime 標示；例外模組/碼未提供。詳 [RI-007](../04-analysis-integration/20261101-native-c25-wait-and-preview-app-error.md)。只改 as_server_spec，沒有修改 Server/Client。

## 2026-11-01 RI-006：C02/C04 成功後 Client 異常、C42=原件 CExceptionPacket

從使用者 70 packet/16 close/4 validation JSONL 查出 03:38:13 C02→S02(0)→C04→S02(0)，03:38:17 Server io-error，03:38:47 另一 socket C62→C42 被擋；由未修改 Asgard.exe RTTI/constructor 取證 C42 是 exception report、非 World 登入，Client 可能另有 Crash_as*.log；沒有 OS crash dump 不能確認 fault cause，也未觀察到 World 包。新增 [RI-006 原始證據整合](../04-analysis-integration/20261101-postcreate-c42-exception-report-evidence.md)，追加 A-028/A-031、DEV-ENTRY、CT-107/108 缺口。**僅更新規格，未修改 Server/EXE**。

## 2026-11-01 R-037：補登分析者越界寫入的 TCP 逐包日誌／預期外標記，明確禁止後續直改 Server

使用者糾正本工作應是分析與 Server 規劃，並問先前直接實作是否回補規格。確認已發生的 `as_server_roy/main` commits `95977823`（收發 Log、UNEXPECTED marker）與 `71ebd259`（log 文件修正）；先前 ADR-009/R-036 僅涵蓋驗證失敗原因 Log，未補完整逐包 contract。新增 [R-037 詳細規格／事實回補](../02-server-planning/game-packet-log-contract-and-backfill-20261101.md)、[CT-114](../05-conformance/game-packet-observability-acceptance-20261101.md)，更新需求、工作板、追蹤與角色確認關卡。純規格修改、**本次未觸碰 Server／DB／EXE、未撤銷他人開發變更**。舊程式僅記 source-implemented，原 Client E2E 仍 not-run。

## 2026-11-01 ADR-009／R-036：預期內驗證失敗回覆、保留會話與原因 Log

使用者要求 C02 正常錯密等不應直接踢線，而應按原版 S02(非零,錯誤文字)→Client 可見錯誤→C15/重試；以此延伸至其他正常功能驗證拒絕。獨立規劃 `EXPECTED_VALIDATION_FAILURE`／`PROTOCOL_UNEXPECTED`／`SECURITY_FATAL`，增 `[VALIDATION_FAILED]` 結構化去敏 reason_code/s2c_status/response_sent/connection_action，不能用既有 `[UNEXPECTED_PACKET]` 或 Close 摘要代替；尚未證原版 error status 與 C15 retry 故 A-030/A-028 增量及 CT-112/113 保留 not-run。新增 [ADR-009/DEV-REJECT-01..06](../02-server-planning/expected-validation-failure-policy-20261101.md)、[原版驗收](../05-conformance/expected-validation-failure-acceptance-20261101.md)，更新規格索引、ONB 工作、DEV-ENTRY 與分析缺口。**本次沒有更動 as_server_roy/DB/Asgard.exe，也沒有聲稱原版 Client 已顯示錯誤。**

## 2026-11-01 Roy3 追加 A005 局部路徑 / 動態碰撞補證（E15–E21）

在首次 Roy1/2/3 合併後，Roy3 另有新提交（已補 merge）還原 `0x4BE470→0x4B8B20` 候選路徑阻擋、`0x4C1850` 動態 Tile flags overlay 與來源方向遮罩；Map6 raw flags0=902/flags17=2698、raw-only 4鄰可達900候選。已更新統整報告、DEV-ENTRY-05、A005 P0 缺口、Client I/O、PKT-C33、CT-109；這些是 static candidate，不等於可走原版 World，E2E remains not-run。

## 2026-11-01 Roy1/Roy2/Roy3 合併驗證與創角直入遊戲／可移動下一階段規劃

三條 task_a 分支 merge commits 保留原歷史，按 A/PKT/CT/evidence ID 整合交集，不以全檔覆寫其他研究；更新 [整合原件稽核](../04-analysis-integration/roy123-verified-evidence-review-20261101.md) 與 [完整 Server DEV-ENTRY-01～06](../02-server-planning/roy123-playable-world-implementation-20261101.md)、[剩餘 Client 分析](../03-analysis-requests/roy123-remaining-playable-blockers-20261101.md)。原件校核新事實：A-030 Region2..4 C02 NAME F3/E-MAIL F4 已由 Basic.dat + EXE 確證；A-028 Region3 final S02 callback 建 LoginDialogPane，但**非**已證可見回登入；A-031 Region3 C10 後 CBillingInfo C25(3×string8) 且 non3 不強制；A-032 原始 MAP 理論 C35 map6=00040F90 等五張重算已核；A-005 S0B bit7/seq7 Client 行為補證。私有 Server a9326985 仍 live native C02/C04/C15 Close、C25=01 synthetic、沒有 C11/C33 Host 路由；CT-105/107/108/109 original Client 均 not-run。只改 spec/main；沒有修改 Server、DB 或 Client。

## 2026-11-01 ADR-008：使用者確認創角成功直接進遊戲、不返回登入畫面

以本輪使用者明確要求覆蓋先前規劃錯誤：新角色 C02→S02(0)→C04→S02(0) 後直接由原版 Client 自動入 World，**不得要求回 LoginDialog 人工再次 C03**；日後有角色的一般 LoginDialog C03/S03/C10 仍保留。新增 ADR-008，調整 R-026/027、ONB-02/03/04、A-028/030/031、SCN-008/009/010、DEV-ENTRY-02/03、readiness/Client I/O matrix、CT-105/107/108 與相關文件。已知 C04 callback 0x4b206b 不立即 S03，但其後原版自動入世界 packet 仍需取證；不因此標記原生 Client E2E 成功。只修規格、不改 Server/DB/EXE。

## 2026-11-01 原版 Client 完整創角至可操作入圖 P0 實作規劃

對照 `as_server_spec/main@3cb220a2` 及私有 `as_server_roy/main@a9326985`，區分已有 Account/E-MAIL v5、Character/proof、C03/S03/C10、World DB/scene 合成後端，與未完成的 live C02/C04/C15、真 World C25、真 MAP C35、InWorld C11/C33。新增 DEV-ENTRY-00..06、P0 A-030 現有任務續查與新 A-031/032、CT-107..109、ONB/ready gates/traceability。原版 Asgard.exe 不修改；Server 原始碼/DB 未由本次 Spec 工作改動；原版 Client E2E 仍 not-run；NPC/怪物/任務不設為首次可操作入圖的先行阻塞。

## 2026-11-01 R-035：創角 E-MAIL 開啟單純儲存規劃

已決定原版創角 E-MAIL 應保存，暫無其他用途。新增 R-035、DEV-CREATE-EMAIL 設計、CT-106、ONB-02/traceability 與相關資料契約；SQLite/Pg Account nullable creation_email schema v5，僅隨 C04 角色成功原子提交。A-030 NAME/E-MAIL 對照仍需 native 實證，不能把猜測當結果。只改 Spec main，不修改 Server/DB/Client；原 Client E2E not-run。

## 2026-10-31 23:51 創角送出直接原因已確認

新連線以 REA Client send 與 Server f2a4a38 本地去敏 close journal 關聯：C02 成功送出並收到，因 native-c02-fields-unknown-a030 立即關閉、未回 S02。將 RI-001 根因切片提升為 runtime-confirmed；A-030 僅補 A30-1，欄位與錯誤契約仍待研究。確認新版 FormInput idle600／absolute1800 已實作並在本次摘要生效，與舊60秒等待及前輪 send=-1 分開。不發布原始 journal／表單，Server 未由規格整合者修改或重啟；原版 CT 仍未通過。


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

## 2026-10-31 Roy1/Roy2 分支同步與原始 Client 核對

Roy1 A-029 C26 三字串與 A-030 C02 地區 control ordinals、S02 UI/C15 研究已整合，新增 packet/evidence/status machine/readiness 引用，保持 A-029/A-030 integrated/partial、Client E2E not-run；Roy2 全部原提交先前已在 main。依最新 `as_server_roy@f2a4a38` 調整規劃：獨立創角 backend 已實作、Host native C02/C04/C15 仍 fail-closed，RI-005 表單 idle=600s/absolute=1800s 且原版 Client 未驗，RI-001 的 C02 提交斷線與事後 send=-1 不可混淆。見整合審查與新版 DEV 計畫；本次只更新規格。


## 2026-11-01 / A-030 roy1 native field and error UI evidence

在既有 `task_a/roy1` 追通原始 `Asgard.exe` Region2..4 C02 F3/F4 資料流、確認視窗 locale keys 0x49/0x4B、S02(u8/string8) 失敗訊息 dialog 建構、C15 opcode0x15 empty body 送出和 state0x1F；Region3/state0x1E 抑制訊息是例外。原件40個 x86 anchors PASS + 離線6 tests PASS；擴充工具原生簽章 26 個、合成 unit case 6 個，native original GUI not-run。新報告 `03-analysis-requests/A-030-roy1-native-fields-failure-c15-handoff.md` 與 requests/packets/evidence/scenarios/CT-103～106 交接更新。仍需 `Locale.dat` label 與原 Client CT；R-035 只保存 email 產品決策不受影響。無 Server/DB/EXE 修改，無新分支。


## 2026-11-01 A-030 原版 Basic.dat 語系資源交叉驗證（取代先前 label unknown）

已核對使用者新提供 `Basic.dat`、`Locale.dat` 原件 SHA；Basic.dat 的 UTF-16LE archive resources BasicString[73]=NAME、[75]=E-MAIL，SkinString[2153]=名字、[2154]=E-Mail；原始 Asgard.exe confirmation lookup 0x49(F3)/0x4B(F4) 和 C02 UI+writer 相對偏移交叉證實 Region2..4 NAME 第三字串、E-MAIL 第四字串。更正舊 A30 只推論 label 或要求從 Locale.dat 找 label 的陳述。提交 Python 資源解析+三原件 SHA/26 x86 anchors 測試，本機 7 PASS；S02 非零原生對話／C15(empty) 靜態路徑已核對，原版 GUI/TCP native E2E not-run，A30 `integrated/partial`。不修改 Asgard.exe/Server/DB，沿用 `task_a/roy1`。

- 2026-11-01：REA勘誤 C35 第一欄為 MapData map_ref，更新 active lookup／離線分析工具與跨地圖 fixture；map6=00060F90。Server 248項回歸與本機TCP通過，GUI待測。使用者要求啟動預填ID另列為測試便利性需求。

- 2026-11-01：私有roy399f09e實作創角後試驗自動S03交接、靜態地圖權威移動、v6目前位置保存及SQLite升級備份；公開規格區分使用者目標、靜態Client證據與Server政策。255項測試／真TCP回歸通過，Native GUI需修正ID後重驗，新手地圖身份尚未證實。

- 2026-11-01：私有roy5da03dd接入已驗雜湊與CP950文字CRC的Born/PaperDialog，S44(1,0)後以C6C4→2確認；與教學完成／獎勵分離，無新schema或Client資源修改。260項測試／本機TCP通過，原版教學場景身份及GUI仍未驗收。

- 2026-11-01：補證LoginDialog條件式自動C03與S03無prior-C03分派guard；仍不宣稱原生創角轉場已通過。使用者不記得草地圖身份，外部資料未與本地版本／Map6綁定；新增身份待查範圍記錄。無Server／Client行為變更。

- 2026-11-01：修正短角色名的自訂3-byte下限造成創角C02斷線；現行1～24 CP950 bytes屬Server政策。加入精確名稱拒絕診斷及實驗S02/C15重試，261項回歸／完整短名TCP通過，使用者GUI待重驗。

- 2026-11-01：使用者診斷副本已證短名創角、自動進場、Born關閉及移動；約169秒後C44物件資訊請求被未知opcode關閉。REA確認4-byte BEu32形狀，roy51bed5b補上受權限限制的處理；264項回歸／本機TCP通過，物件詳情回包未實作、穩定遊玩與重登GUI待驗。
