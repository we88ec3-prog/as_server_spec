# Roy1/Roy2/Roy3 整合後 Server 可執行開發規劃：創角成功直接進圖並移動
2026-11-01 · 以 [ADR-008](post-create-direct-world-decision-20261101.md)、[原始證據整合](../04-analysis-integration/roy123-verified-evidence-review-20261101.md) 為規範來源。

## 目標定義與兩段出場
**完整必達**：管理 Web 預建 Account → 原版 Client NewUser C02 帳密驗證 + NAME/E-MAIL → S02(0) 觸發 C04 → C04 commit Character/Appearance/onboarding/Account.creation_email → S02(0) → **不回登入畫面、不人工再輸入 C03** → 原生自動 World 轉場 → S05/S15/S14(1) → 真 C35 → S04/S33/S14(2) → Server 有權威位置，Client C11 轉向、C33 移動得到正確 S0B、原版 GUI 真正走動且重登資料不遺失。
- **Milestone P（原件可玩地圖）**：先把選定原件（如 Map0/00006.map）做 native profile，可供原始 Client 確實載入並能操作；**未證原版初始教學圖時只稱 interim-playable，不宣告官方教學出生或完成新手教學**。
- **Milestone T（原版教學入口）**：另取證 tutorial map_ref/初始安全 spawn/觀察路徑與首次 Born Script/NPC；Server 自選首次派送時機、任務決策，不要求恢復原服 DB policy。教學怪物、技能、獎勵及畢業仍是 ONB-05/06 後續，不阻擋 Milestone P。

## 最新已完成後端（不得重做）
私有 `as_server_roy/main@a9326985`：Account/Admin/CredentialVerifier、SQLite/Pg v5 `creation_email TEXT NULL`、`IndependentCharacterCreation` 與 proof/draft/角色原子提交、已存角色 C03/S03/C10、WorldRecoveryStore C35 epoch/DB 寫入／復原、synthetic Scene 及多人共享 Actor Runtime、C33 解析與 `WorldMovementWindow` seq 去重**後端**存在。原版 Host live C02/C04/C15 仍 Close、C25 只收合成 body01、沒有 C11/C33 InWorld route；合成 CI pass ≠ 原版 Client pass。

## 交 DEV 任務／邊界／驗收
|開發順序|工作、具體位置|立即可做（已證）|需要 Client/native gate 之後才能標完成|
|---|---|---|---|
|**DEV-ENTRY-01**|Host `LoginWireSession`、Protocol `TwCharacterPackets`、Auth/Creation|對**已證 Region2..4** 的 C02 {ID/PASSWORD/NAME/EMAIL/flag} 四個 CP950/profile string8+u8 開 strict decoder；現有共用 CredentialVerifier 對 Admin Account 驗密+停權，C02 creation-only proof 綁 owner/credential_version/socket/generation；禁止 Client 新建 Account；Region0/1 不套 F3/F4 定義|當次 Region/seed、帳號 UI 本地 gate、是否可空 email 的原版 Client GUI；不可因静態 NAME/EMAIL 已證就自動宣告全部 native C02 成功|
|**DEV-ENTRY-02**|Host C02/C04/C15/S02、IndependentCharacterCreation、CharacterCreationStore|合法 stage1 S02(0)→C04 5u8→原子 commit Character/Appearance/onboarding/`creation_email`→stage2 S02(0)；C15 只取消未提交 draft，idempotent、跨 owner/missing proof/停權/錯密 fail closed；不把 C02 proof 當 World grant|S02 非零 status/message/focus 的原版 GUI 和 C15 retry/socket 行為；合法 C04 不應立即由 Host Close，成功保留 PostCreateEntryContext|
|**DEV-ENTRY-03A**|Host World `case 0x10/0x25`、Protocol region-aware C25 codec |已存角色一般 C03/S03→新 TCP C10 raw token 是 World grant authority；Region3 可緊接接受 C25 **三個 opaque string8**，非3 **不得要求 C25**；取消原版 Native Host 對 `body=01` 的依賴（原 dev synthetic fixture 仍隔離 Development）。C25 不含 map_id/帳號，不能視作額外登入證明|C10/C25 後第一個原版 Client 可接受的 S2C/S05/S15/S14 時序與加密 framing，Region0/1/2/4 原生動態|
|**DEV-ENTRY-03B**|NewUser 成功後 PostCreateEntryContext + World grant/phase state|只有 C04 commit 已成功且 owner/version/generation 有效才可安全轉場，完成一次性 World lease；同 Socket/新 TCP 狀態均不可重播；**不回 LoginDialog／不要求人工 C03**|A-028 0x4b206b 後 Region3 `LoginDialogPane` 實際 callback 與 A-031 首個自動 C2S/S2C；若確證背景 C03/S03/C10 才接，不猜 S03 送出時機／C25 作 postcreate 身份|
|**DEV-ENTRY-04**|World `WorldFixtureConfiguration` → NativeVersionedMapCatalog、WorldRecoveryStore|依 SHA 鎖定 archive+member/map_ref；嚴格解析 MAP index/metadata；原件 `map_ref6` 60×60、初始 header4+structCRC0x0F90（C35 `00040F90`）只作靜態內容 profile；對照原版 C35 exact pair、epoch/generation、持久角色及所選 map；錯版/逾時/CRC mismatch fail closed；成功後 S04/S33/S14(2) 不誤標 tutorial_completed|原版實際 C35 值、S15/S04/Viewport/Facing、可用 spawn；Map6 不等於原版 tutorial map，亦不可把 (30,30) 或 Born (31,29) 硬填成已證 birth|
|**DEV-ENTRY-05**|Host InWorld `case 0x11/0x33`、SharedMap + WorldMovementWindow + S0B|嚴格 C11 direction u8、C33 {direction,seq7,movement_mode}（第三 byte 可能 bit7），Server 權威更新、per-socket seq/window/epoch、重送 idempotent。原生 S0B `BEu16 x,y + u8 (seq | flag7)` 回**本次 C33 sequence**，bit7=0 為本地權威校正/停止路徑，bit7=1 進預測差分比對（Client 不符仍校正）。向其他玩家依已證 S06/S11 投影，Client 自報位置不可信|實際方向/步幅/timing、Client 首 seq、blocked tile/動態 block 判斷，至少 5 步走動+撞牆/回滾的原版 Client native CT；map6 flags0 候選路徑不證可走，碰撞 unknown 保持隔離/安全拒絕|
|**DEV-ENTRY-06**|整體 E2E、兩 DB、普通登入回歸|合成 unit/integration：Domain/SQLite/Pg v5、重複 C04、錯密/ban/C15、C10 重放、C25 Region3 3×string8/non3 no C25、C35 錯 pair、C33 seq=127→0、S0B 正/負 bit7，World generation 舊連線不能污染新狀態|原始 unmodified Client 真 GUI `CT-105/107/108/109` 連續 PASS；另測已創角日後 C03/S03/C10 的一般登入、重連恢復及多人同圖；無 runtime trace 不宣稱 native-ready|

## Server 狀態機（設計，不是未證原生封包）
```text
AdminCreatedAccount
 ├── FutureNormalLogin: C03 owner verified → S03 grant → new TCP C10 → World
 └── FirstNewUser: C02 credentials verified → CreationIntent(proof)
       → S02(stage1 success) → C04 valid & atomic COMMIT (+creation_email)
       → S02(stage2 success) → PostCreateEntryPending (only committed owner)
       → native Client *actually observed* auto transfer / world entry (A-028/A-031)
       → authenticated WorldLease → S05 / S15 / S14(1)
       → native C35 exact map pair under one pending loading epoch
       → durable WorldEntryCommitted → S04 / S33 / S14(2) → InWorld
       → C11 facing + C33 move(seq7,mode) → server-authoritative step → S0B
```
**禁止**把 `S02(stage1)`、C15、登入後合成 C25=01 或只記收到 C35 當作 Character/World 成功。初次自動轉服的 wire unknown，不能以猜測「自動 S03」越權替 Client 送未證封包。

## 所需具體原版驗收／失敗分類
- **CT-104/105/106/107**：只限已確認 region-profile C02 mapping；成功角色+email 同交易、原版 GUI final S02 後無人工回登入；非零 S02 在表單可顯示、C15 後可安全處理失敗；同一 account 不重複角色。
- **CT-110**：Roy2 C10/C25 region3 靜態+synthetic codec；**CT-111**：Roy2 C04 success callback/Region3 LoginDialogPane static，這兩個不冒充 native CT-108。
- **A-032 offline**：5 個 SHA 原件 MAP pair 已獨立重算；只有 **CT-108** 原版實際 C35 及 S04/畫面通過才算可入圖；map6 是 interim candidate，原生被拒必回資源/CRC/版本查。
- **A-005 offline**：S0B bit7 / low7 seq handler 已證；**CT-109** 需原始 GUI 真的移動和撞牆 rollback，不能只做 C33 parser test。
- **Transport**：正常 S03 舊 TCP close vs 非預期 C02/C04/C25/C35 FIN；紀錄 op/time, region/seed, DB checkpoint，而不記 ID/password/NAME/EMAIL、billing strings 或原始 token。
- **資料保護**：Email 僅儲存 Account.creation_email，無認證/寄信/驗證/管理 UI 用途；只有授權 Account 通過 create 才可更新。
- **多人共圖**：共享 world_id/map_ref/revision 的 NPC/Monster Registry，但 Player 自己 lease/pos/quest。最小一人走動無需先做全部 NPC/怪物/技能系統。

## 結果交付責任
- A 研究輸出 Client 可證的 Field/Opcode/VA/Asset/region、未知下游，**A-030 Region2..4 label、A-031 Region3 C25、A-032 靜態 CRC、A-005 seq/correction 不要重開**。
- Server 編碼執行 DEV-ENTRY-01..06，在 `as_server_roy/main` 與目前安全機制相容；原版 Client 不修改，無請求則不開 branch。
- CT 原生 GUI/TCP 是最終阻塞；開發期間仍可先提交 static/dry-run subset。所有 native 未跑的標記必須保留 `not-run`。

[後續 Client 研究/實測所缺的真證據](../03-analysis-requests/roy123-remaining-playable-blockers-20261101.md)。
