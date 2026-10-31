# 首次玩家 CT-011～020 測試計畫

這些都是 **planned**，尚未執行；未經 A-021/A-022 證實的原生 wire/status/教學 map 值不得編造成成功向量。

|ID|測試及預期|前置或阻塞|
|---|---|---|
|CT-011|非法會話直接 C02/C04/C25，資料與 World 不變|Domain 可測；Client 拒絕形式待 A-021|
|CT-012|同名或同帳號並發，只產生單個有效角色|DB / Domain|
|CT-013|C02 後 C04 前斷線不留可進 World 的半角色|Domain；Client 時序待 A-021|
|CT-014|C04 成功但回包遺失重送，角色不複製|Domain；UI 回應待 A-021|
|CT-015|過期/跨帳號角色/重用/舊 generation token 拒絕|Auth integration|
|CT-016|S02/S05/S15/S14(1)/C35/S04/S33/S14(2) 順序正確，loading 中不可操作|一般已知 profile；教程圖待 A-022|
|CT-017|C35 前後 crash/重連不留幽靈 World 或誤寫教學完成|恢復分支待 A-022|
|CT-018|原生 Client 首次在已證據確認的教學地圖出生且可操作|**必須 A-021/A-022 + 原版 Client 實測**|
|CT-019|無權管理/Client 建帳被拒絕，錯密/停權不能取得 grant|Server / Admin integration|
|CT-020|非法 profile、錯誤順序及未知分支不得冒充 success|Server unit/integration|

每次結果要記 Client SHA、Server revision、測試環境、輸入（去秘密）、期待/實際、通過/失敗、時間、證據與未解問題。Server 自動測試通過與 Client 人工通過是兩件事。未取得原生欄位證據前，vectors.json 使用 planned 狀態而非可執行的 byte-exact 成功值。

## A-021 / roy1 靜態補充（2026-10-31；**未執行 Client 驗收**）

請參閱 [逐位址分析](../03-analysis-requests/A-021-roy1-static-analysis.md) 和 [協定子集](../04-analysis-integration/A-021-native-flow.md)。現可用合成輸入為 `C02 016101620163016401`（region2..4）、`C02 016101620163`（其他 region）、`C04 0102112233`、`S02 0000`。**body only**、只檢查 parser/serializer 形狀，非原 Client 封包擷取；它們不能直接把 CT-011..014 標 passed。

原 Client 必須額外核對以下測點：C03 已存在無角帳號是否開啟原生創角 UI、C02 4 欄 UI 語意、C02/S02/C04 的所有成功失敗/取消分支、C04 後是直接 transfer 或重新登入、網路重送/並發/斷線原生效果，以及任何 Client 發起新帳號的要求都不會讓 Server 建立 Account。沒有完整資源/可執行測服與去識別動態 trace，A-021 仍為 blocked。

## roy1 合併後新增安全／協定 CT-029～032（planned）

|CT|測試標的|目前可用證據／阻塞|
|---|---|---|
|CT-029|C02 region-specific 3-string8 vs 4-string8+flag；不接受跨區錯誤 layout|A-021 observed-static，codec fixture 可先執行|
|CT-030|C02 在 C03 前出現，驗證未取得合法帳號 owner proof 絕不可認領別人的預建帳號、創角色或取 grant|A-027 必須證明 Client 使用何種憑證或安全授權方式|
|CT-031|UI local 0x1d 收到 S02(status0) 導向 C04 並轉 0x1e；不可把此跳轉當作建角已成功|A-021 observed-static；可先寫 Client-parser/sequence fixture|
|CT-032|C04 後續的 S02 終局、Character commit、合法重登或 World handoff|A-028 尚未完成前屬 native-compatibility blocked|

CT-029/031 若對已證據支持的 Client 靜態行為做 fixture，可以完成該子集測試；**不代表 CT-030/032 或原始 Client 創角進圖 E2E 通過**。

## A-022 合併後 CT-016/017/018 變更

CT-016：按既有 S15 3×u16+2×u8+string8、S14 控制碼、C35 MAP header+4／structured checksum、S04 4×u16 寫 byte fixture；明確測錯序、錯版 CRC、延遲的舊 epoch C35。CT-017：重連/token/epoch 失效，不能重領資產或把入圖當教程完成。CT-018：等 A-015 原 MAP/spawn 被證實後再做真正教程 Client E2E。所有此處均屬 planned，不報 PASS。

## A-002 C03/S03/C10 與重複登入 CT-037/CT-038（planned）

[A-002 靜態分析](../03-analysis-requests/A-002-roy1-login-transfer.md) 已追 S03 addr/port/u8 token_len/raw token 與 C10 raw token；[合成 Domain fixture](../tools/a002_session_model.py) 實際測錯密不踢人、同帳號世代替換、一次性 token、跨角色拒絕、過期、login socket 在 transfer 中先斷、舊 World 清理不影響新 World，以及 crash fail closed。**這是 designed 測試，不是雙原版 Client 實機 passed**。CT-037/038 用以提醒 DEV 依真實 DB、mock wire 與 Client 再驗；S02 的原服重複登入錯誤碼未知，禁止拿錯密 status3 直接代用。

## A-027 身份與 C02 前認證安全（CT-041/040，planned）

[完整 A-027](../03-analysis-requests/A-027-roy1-identity-ui-security.md)：CT-041 對任意 pre-auth C02（包含正確已存在帳號名、非法/停權/跨 session）驗證 Server 不建立 Account、不認領 owner、不建立 pending C04 草稿、**不回 S02 status0**、不改 Character；只有真實已認證 owner 的獨立路徑可開放。CT-042 驗證各 region writer body 3 vs 4 string8+u8、UI +0x270 與 +0x274 的本地字串相等、UI 欄位來源；region1 UI/serializer discrepancy、原版 C03 空角色→UI 仍 unknown。

[安全與合成 codec 工具](../tools/a027_pre_auth_contract.py) 只驗合成 body/拒絕策略，**不是 Client 真實互動成功**。A-027 integrated/partial 與 native claim route blocked 同時成立；後續 A-028 才確認 C04 終局/提交回覆。

## A-028 針對 C04 終局分支的測試設計（2026-10-31）

[原版 BIN-first 證據](../03-analysis-requests/A-028-roy1-c04-terminal-analysis.md)／[不越權的 Server 設計](../04-analysis-integration/A-028-newuser-terminal-contract.md)：CT-031 驗 state0x1d + S02(status0) 才發 C04/state0x1e；CT-032 驗 **state0x1e + S02(status0)** 只觸發 local `0x4b206b` UI 分支，不直接建立 S03/C10；CT-043 驗 S02(nonzero) C15 CancelNewUser（opcode0x15、空 body、normal binary C2S frame）及 state0x1f/focus status；CT-044 驗有經過 Server owner credential 的角色 transaction、重送/重複名稱/晚到 C15 不破壞已提交角色。Python `tools/a028_newuser_response.py` 為合成模型測試，**非真實原 Client 通過**。仍需 A-027 原生 owner proof、A-003 合法欄位與原生登入/World UI 出場證據。

## A-016 / roy1：R-017 回覆遺失、斷線與持久化（CT-045/044 planned）

[A-016 原版可核對函式](../03-analysis-requests/A-016-roy1-replay-recovery.md) 和 [Domain/DB 恢復契約](../04-analysis-integration/A-016-idempotency-recovery.md)。執行 `python3 tools/a016_recovery_model.py` 做 SQLite synthetic crash/reopen：角色提交回包遺失仍唯一、token 原子一次性、C33 seq7 replay/127→0、C35 拒絕錯 epoch/同 pair ambiguity、交易雙邊入帳與領獎 unique ledger；**不代表原 Client 或原服驗收通過**。CT-045/044 是 designed/negative contract，原始 Client 世界載圖/重登入仍需後續 CT-016/017/018。

## P0 / DEV-030 密碼長度相容性驗收（2026-10-31；未執行）

原 Client 使用者回報登入密碼欄**最多 8 字元**，現私有 Server `Pbkdf2PasswordHasher.ValidatePassword` **10～128** 不相容。依 [原生 4～8 字遊戲密碼政策](../02-server-planning/native-game-password-4to8-policy.md) 在既有 **CT-019/CT-037/CT-050** 增列測試，不新增測試編號：管理員建帳及重設 4/5/6/7/8 字 ASCII 英數成功；3/9/10/12 字、控制/空白/非 ASCII、非法字元拒絕；大小寫敏感；SQLite/PostgreSQL 一致；舊 10+ 字密碼不截斷、需重設；重設後舊 grants/token 失效但角色保留；Admin X-Admin-Key 不縮短。**真正原版 Client** 必須親自鍵入4字及8字並證明 C03 不丟字，成功/錯密/停權與 transfer，否則 Client CT=not-run；合成 C03 fixture 成功只能算 unit/integration。
