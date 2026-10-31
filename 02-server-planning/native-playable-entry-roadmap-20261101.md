# 原版 Asgard.exe 從創角到可操作進入遊戲：Server 實作路線（2026-11-01）

## 0. 範圍、基線與「成功」定義
- 規格基準：`as_server_spec/main@3cb220a2`；唯讀對照私有 Server `as_server_roy/main@a9326985b1d2`。以後續工作實際開始時各 main 為準；不要把本頁快照當成永遠最新。
- **目標是無修改的原版 `Asgard.exe`，管理後台建一筆新 Account → Client 的 NewUser 創角色（C02/S02/C04/S02）→ **第二段 S02 成功後直接自動進 World（不回登入畫面、不需再次人工 C03）** → 依 A-028/A-031 所證的實際轉場封包/連線授權與原生 World entry 入圖 → 載入地圖、定位與回應 C35 → 在地圖上至少能移動／轉向，重登仍保留角色與首次進圖狀態**。
- 首次預定進入**原版資源內已確認可用的教學地圖**；真正 tutorial map/ref/spawn 目前未知。此選擇及出生座標屬 **Server 自訂政策**，只需 Client 能載入正確配對的資源並合法出生，**不需還原原服 DB/原服首次出生政策**。若先用其他經原版 Client 驗證的地圖，僅標 `native-interim-world-entry`，不宣稱原版教學完成／CT-107 全通過。
- 入遊戲不等於完成新手教學。NPC/怪物、Born 首次對話、任務、戰鬥、技能、獎勵和離開教學是 ONB-05/06 的後續工作，**不當作第一個「可操作入圖」的前置阻塞**。進圖與完成教學旗標分離。
- 所有未知的原生欄位、S02 status、C25 layout、MAP checksum 必須保持 fail-closed；**不得用合成 C25 body=01、任意成功 S02、放過任何 C35、憑空填 MapId/CRC、虛構原版出生點** 來冒充 native-ready。原版 Client E2E 目前 `not-run`。

## 1. 最新 Server source audit：不要重做已有程式
| 位置 | 已實作的後端／合成測試 | 原生 Server 目前阻塞 |
|---|---|---|
| `SqliteAccountStore`／`PostgresAccountStore` | Admin 管理建立、驗密/停權/credential version、PBKDF2、遊戲密碼 4–8 ASCII 英數；Account `creation_email TEXT NULL` v5 | 帳號能建立**不代表**空角色帳號可直接登入世界；沒有 E-MAIL native mapping |
| `IndependentCharacterCreation`、`CharacterCreationStore` | pre-C03 創角 credential proof、限時/世代/owner、C04 transaction、新角色和教學進度、E-MAIL 同交易、重送/C15 安全 | `LoginWireSession` `case 0x02/0x04/0x15` 仍直接 `Close`（C02 reason `native-c02-fields-unknown-a030`）；所以空角帳號仍不能從原版建角 |
| `LoginWireSession` C03/S03/C10 | 正確既有 Account + **已有 persisted Character** 的 C03 可核發一次性 S03 token；新的 World TCP C10 驗 token、世代、角色；合成 smoke 已通過 | `C03` 查不到 Character 就返回 S02 generic fail；原版獨立創角入口必須先成功。S03/S02 的其他原版版本／失敗 UI 尚未全部驗收 |
| World loading / `WorldRecoveryStore` | 單一 pending epoch、原子 C35 checkpoint/outbox、S05/S15/S14/S04/S33 writer、SQLite/Pg 恢復、DEV-070 共享場景後端 | `case 0x25` **只接受 body=01 開發合成值** 且需 `Asgard:World:Fixture:Enabled` 的 Development fixture；原版 C25/其他首包尚無權威 payload；沒有實測真 MAP header+structured checksum。正式原生 World 預設拒絕 |
| `TwWorldPackets.ParseC33`／`WorldMovementWindow` | 合成 C33 3u8 / S0B 欄位與去重窗口 | `LoginWireSession` 目前沒有正式 InWorld C11/C33 route，未知 native 碰撞與回滾仍需驗證，載入成功**不等於能走路** |
| `Asgard:Game:Enabled` | 本地 Game TCP listener 支援，預設 false；現場曾以 true 執行 | 啟動／埠佔用／帳號/角色存在是運維檢查，不應和 C02/C25 封包阻塞混在一起 |

**先修真正阻塞，再增加內容**；上述為 2026-11-01 程式碼審閱，合成 CI `a9326985` 通過不等於 original Client 通過。

## 2. 分段 DEV 派工（每一段都必須可獨立驗收）
| 優先 | DEV 任務 | 依賴與落地模組 | 完成定義 |
|---|---|---|---|
| P0-00 | **DEV-ENTRY-00：原版 Client/TCP 的安全追蹤基線** | A-030。記 EXE SHA、region/seed、Server build、traceId、C02 字串長度而非值、S02 status、C15/close reason；檢查既有 `GameTcpDiagnosticJournal` | 可區分未送 C02、收到 C02 後 fail-close、S02→C15、C03 S02 reject、S03 expected close、C10 拒絕、C25/C35 拒絕；禁止洩漏密碼/信箱 |
| P0-01 | **DEV-ENTRY-01：native NewUser C02 身份與欄位映射** | 先用 A-030 的正式 UI→region→C02 帳號/密碼/NAME/E-MAIL 對照確認後，在 `LoginWireSession`、`TwCharacterPackets` 接現有 verifier / proof / pending | 直接開 NewUser，不要求先 C03；本次既有 Account+正確密碼才能授權；正確 NAME 與 EMAIL 保留到 pending；未證 region/欄位、未知 Owner 全部安全拒絕；不能直接建立 Account |
| P0-02 | **DEV-ENTRY-02：C02→S02→C04→S02/失敗 C15 UI** | A-028/A-030 的原版 S02 非零 GUI／C15 證據；`IndependentCharacterCreation.CommitC04Async`、v5 Account Email transaction | stage1 S02(0) 僅在合法 owner proof + draft 後；C04 必須同 connection/generation/credential version/TTL；一次交易提交 Character+Appearance+onboarding+`creation_email`；成功後第二 S02(0)；錯密/重名/取消/失敗不建角，原版 UI 可理解結果而非一律 TCP 斷線；重登角色仍在 |
| P0-03 | **DEV-ENTRY-03：創角後自動入 World／日後登入雙路接線** | A-028/A-031 證明 final S02 後 UI/背景 auth/轉服／World first C2S；與已存角色的一般 C03/S03/C10 入口分開。合法已提交 Character 的 PostCreateEntryContext 才能接世界 | 創角後原版 Client **無 LoginDialog/人工 C03** 直接轉 World，安全 grant 只能按實證發送；已有角色日後一般 C03→S03→C10 保留；兩路均不使用合成 C25=01，不允許無身份或重放 |
| P0-04 | **DEV-ENTRY-04：真 MAP 初始位置＋S15/S14/C35＋入圖** | A-032 由已上傳 Map0/1/2 同版原件取得 `(map_ref,archive SHA,resource revision,map header word,structured checksum,width,height,spawn,viewport,facing)` 的驗證 fixture；`WorldFixtureConfiguration` 與 `WorldRecoveryStore` 改接正式版本化 MapCatalog/入圖政策 | Server 選定已驗 map，S05/S15/S14(1)→Client 真 C35 pair→atomic commit→S04/S33/S14(2)，原版真的能看到地圖/人物；失敗校驗、錯版本、重登入不能偷過，舊 epoch 不得污染新 Session |
| P0-05 | **DEV-ENTRY-05：原版地圖最小操作** | A-005 Client C33/S0B、C11/S11、A-032 map geometry；Server 明示安全移動政策，逐項 native 驗證 | InWorld 接受已驗連線的 C33 3u8／C11 1u8，Server 權威位置/朝向、合法速度及不可越界；S0B 原生客戶端能正確移動/校正；至少一條已驗證可通行路徑可來回，重登無穿牆/重複移動；未知 collision bit 不得強行認成 passable |
| P0-06 | **DEV-ENTRY-06：跨段 E2E 與故障回歸** | CT-103～108/109；Admin+原版 GUI 操作及 SQLite/PostgreSQL | 一次從空帳號建角到原 Client 原生可操作；錯密/停權/重名/取消/C15、C02/S02/C04/S03/C10/C35 斷線與重送、Server 重啟不重複角色/E-MAIL/入圖/World grant；雙 DB 同規格；分開記合成、實機、正式部署狀態 |

## 3. 角色／資料提交與安全不變條件
1. Account 只由 Admin 建立；C02/C04 不建 Account，不以單純同名建立 owner；原生 ID/PASSWORD/CONFIRM/UI 由已證 profile 解析。遊戲密碼 4–8 ASCII 英數、Client 可能有 region>=1 ID 最低 12 的 UI gate，須先選定符合的帳號測試值，不悄悄改 Admin 的 3–32 政策。
2. 創角開始只持有 `CreateAuthProof`（`account_id/credential_version/connection/generation/TTL`），未完成 C04 前不能發 World grant；`creation_email` 只能與 Character 同交易保存，未證明 wire 源就保持 NULL、不猜 F4。
3. C04 原子提交成功才最終 S02(0)，成功後原生 UI **直接進 World，不回登入頁**（不能擅自假定/冒充背景 C03/S03）；C15 只刪同帳號同世代**未完成**的 pending。
4. C03 認證及**持久角色存在**才發 S03；S03 後舊 TCP 正常關閉是轉服流程，不是未處理的業務中斷；C10 原樣 opaque token，不可跨帳號、過期、重播。
5. 實際 World entry 不依賴猜測的 C25=01；同一張原生已驗證 MAP 才有 C35 expected pair。S14(2) 是 Client loading callback，不代表教學已完成。Server 只以驗證的 Account/Character/World lease 控制玩家。
6. 進地圖後角色是共享地圖中的一位 player；不同 Account 相同 map 共享 NPC/怪物（R-007/ADR-007），但自己的進度/視野/World generation 獨立。首個可操作入圖不要求先完整產生怪物與任務 Script。

## 4. 原版最終驗收與出場定義
- **GATE-N0（已實作的一部分）**：`dotnet build`、`dotnet test`、現有 dev020/dev030/dev050/dev070 smoke 和 DB v5 合成測試。這只能證 domain，不等於成功創角入圖。
- **GATE-N1（CT-107）**：全新 Admin Account、無角色，原版 GUI 開 NewUser → C02/S02(0)/C04/S02(0) → 角色與 E-MAIL 正確存 DB → **原生 Client 無人工再次登入地自動接續 World（下一封包待 A-028/A-031）**；失敗表單不是 generic socket disconnect。**原版 Client not-run**。
- **GATE-N2（CT-108）**：新 World C10 後真的收到/送出原版 World entry（C25 或實證的替代）、選已驗證 map，C35 真 checksum，S04/S33/S14(2) 顯示人物地圖；断線/CRC 錯有恢復，非合成 fixture。**not-run**。
- **GATE-N3（CT-109）**：原版 Client 能轉向和沿已驗證格移動，Server 處理 C11/C33/S0B 並正確持久化/校正，重登入維持合法位置；只算成功畫圖或 ACK 而不動不通過。**not-run**。
- **GATE-N4（完整 E2E）**：一個無角帳號完成 N1→N2→N3、首次創角直入 World，重啟後另以一般登入流程回到同一角色繼續操作，至少再測一個同圖帳號不互相冒用 owner；無改版 EXE、沒有硬編測試封包。只有 N1+N2+N3 全部原版 GUI 通過，才能稱「創角後成功登入遊戲且可操作」。

**開發優先順序：A-030 的 native 欄位與錯誤 UI；A-031 的 C10 後原生入圖封包；A-032 的真 Map/C35；然後 DEV-ENTRY-01/02/03/04/05。可並行做不依賴未知欄位的測試與資料處理，但不得跳過 native gate。**

## 2026-11-01 ADR-008 覆蓋前述舊規劃

**首次創角成功後直接進世界，不返回登入畫面，不得要求人工第二次 C03。** A-028 目前只靜態證實 state0x1e S02(0)→0x4b206b，沒有立即 S03 不代表一定回登入或絕無背景轉服。A-031 必須追自動入 World 的第一個真封包，日後已存角色一般 C03/S03/C10 路由獨立保留。DEV-ENTRY-02/03 與 CT-105/107/108 以 [ADR-008](post-create-direct-world-decision-20261101.md) 為新完成定義，原版 Client E2E 仍 not-run。
