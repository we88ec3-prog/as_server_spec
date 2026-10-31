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

## A-027 身份與 C02 前認證安全（CT-039/040，planned）

[完整 A-027](../03-analysis-requests/A-027-roy1-identity-ui-security.md)：CT-039 對任意 pre-auth C02（包含正確已存在帳號名、非法/停權/跨 session）驗證 Server 不建立 Account、不認領 owner、不建立 pending C04 草稿、**不回 S02 status0**、不改 Character；只有真實已認證 owner 的獨立路徑可開放。CT-040 驗證各 region writer body 3 vs 4 string8+u8、UI +0x270 與 +0x274 的本地字串相等、UI 欄位來源；region1 UI/serializer discrepancy、原版 C03 空角色→UI 仍 unknown。

[安全與合成 codec 工具](../tools/a027_pre_auth_contract.py) 只驗合成 body/拒絕策略，**不是 Client 真實互動成功**。A-027 integrated/partial 與 native claim route blocked 同時成立；後續 A-028 才確認 C04 終局/提交回覆。

## A-028 針對 C04 終局分支的測試設計（2026-10-31）

[原版 BIN-first 證據](../03-analysis-requests/A-028-roy1-c04-terminal-analysis.md)／[不越權的 Server 設計](../04-analysis-integration/A-028-newuser-terminal-contract.md)：CT-031 驗 state0x1d + S02(status0) 才發 C04/state0x1e；CT-032 驗 **state0x1e + S02(status0)** 只觸發 local `0x4b206b` UI 分支，不直接建立 S03/C10；CT-041 驗 S02(nonzero) C15 CancelNewUser（opcode0x15、空 body、normal binary C2S frame）及 state0x1f/focus status；CT-042 驗有經過 Server owner credential 的角色 transaction、重送/重複名稱/晚到 C15 不破壞已提交角色。Python `tools/a028_newuser_response.py` 為合成模型測試，**非真實原 Client 通過**。仍需 A-027 原生 owner proof、A-003 合法欄位與原生登入/World UI 出場證據。

## A-016 / roy1：R-017 回覆遺失、斷線與持久化（CT-043/044 planned）

[A-016 原版可核對函式](../03-analysis-requests/A-016-roy1-replay-recovery.md) 和 [Domain/DB 恢復契約](../04-analysis-integration/A-016-idempotency-recovery.md)。執行 `python3 tools/a016_recovery_model.py` 做 SQLite synthetic crash/reopen：角色提交回包遺失仍唯一、token 原子一次性、C33 seq7 replay/127→0、C35 拒絕錯 epoch/同 pair ambiguity、交易雙邊入帳與領獎 unique ledger；**不代表原 Client 或原服驗收通過**。CT-043/044 是 designed/negative contract，原始 Client 世界載圖/重登入仍需後續 CT-016/017/018。

## A-017 管理 API／稽核測試（CT-045/046）

[詳細分析](../03-analysis-requests/A-017-roy1-admin-audit.md) 與 [契約](../04-analysis-integration/A-017-admin-observability-contract.md)。

- CT-045（planned）：只允許具有獨立 operator identity 與 permission 的 Admin 命令；未登入/越權/相同 key 不同 body 皆拒絕，副作用不可發生；同 key 同 body 的 item grant 只存一次；停權 N 天/永久/解封、角色調整與傳送須由 Domain 驗證與唯一 ledger 保護。
- CT-046（planned）：允許與拒絕、重播、錯誤均寫入 sanitized audit/trace；不得洩漏 password、S03/C10 token、原始 packet body、Cookie 或 Authorization。管理 metrics/health 不向公開 Game Client 露出敏感維度。

合成 Python `tools/a017_ops_contract.py`（五個 unittest 通過）是 designed 參考，不是原版 Admin UI/新 Server 上線驗收，也不是原服擁有同樣的權限政策。

## A-003 合法欄位與重名／角色模型（CT-047/048 planned）

[BIN-first 原版研究](../03-analysis-requests/A-003-roy1-create-legal-values.md) / [合成 Python 工具](../tools/a003_create_contract.py)。CT-047 依 region 測 C02 string8、TW CP950 encoded byte length；region0 UI 第一欄 length gate skip，region1..4>=12；C04 5×u8，色彩查原版十筆色表 index0..9，確切 RGB 與報告一致。CT-048 在 **designed Domain** 以驗證 owner/pending intent/unique name/one-character-per-account 保護無權、雙線同名、同 intent 重送、C15 晚到不刪角；此一帳一角策略不是原服已證。原版重名 S02 status/真實角色選角與 sex/hair 列表仍 unknown，所有 CT 的 `native_client_validation=not-run`，不可假裝實機成功。

## A-020 / roy1：登入前封包型別、解析安全與狀態（CT-049/050 planned）

[原件 BIN-first](../03-analysis-requests/A-020-roy1-prelogin-branches.md) 與 [合成測試](../tools/a020_prelogin_contract.py)：CT-049 分別驗 C0F(3)、C0F(other)、S18(0,3,empty)／kind0 一筆 name+u32、C57(1)/C57(0,id)、S56 multi entry(zlib)、C4B empty、S60(type0 u32/type1 compressed text)，另需拒絕過長/截斷/尾隨／壓縮異常。CT-050 驗原生 C6C3 不會建立帳號所有權、Script cache destructive S44(1,3) 不得作 ACK、C57 不可錯序選服、未驗證 C03 不可 World。此測試是 designed local Server state + BIN-derived codec，不是完整原服 policy 或 Client E2E。

## A-026 原生教程完成/可選獎勵/出口（2026-10-31）

[原件分析](../03-analysis-requests/A-026-roy1-tutorial-completion.md)、[完成與退出安全契約](../04-analysis-integration/A-026-tutorial-completion-contract.md)、[測試工具](../tools/a026_tutorial_completion_model.py)。CT-026/027/028 仍 planned、native E2E not-run；CT-054/055/056 是 synthetic/designed。先用受控 sandbox/合法身份和同版資源確認 Born.Main→PaperDialog→C6C4→C6C2 **只做 ScriptClose**；再真正進行招募員 NPC C39 互動與完整 Script/Quest reply capture，不可把 STATE=ACCEPT 候選當官方完成。沒有 original verified quest rule 時拒絕 completed；沒有 verified reward 時 reward=NULL；有驗證後以唯一交易 + outbox 保證回覆丟失/重登不重發。只有原服確定的 exit map/ref/coord/revision 才可 S15/S14/C35/S04，C35 不含 epoch，負面測同 pair overlap、錯 CRC、crash/reopen 位置/狀態恢復。完整 Client「登入→教學互動→完成→正常出圖→重登」仍需 CT-028；原始 Server 資料未提供，不可把離線測試標成 Client 已通關。

## A-007 物品與裝備的原生 Client 驗收補強（CT-057～059 planned）

[A-007](../03-analysis-requests/A-007-roy1-inventory-lifecycle.md) 列出已證 opcode：C1C type1..9 變長，C1E，C08 Drop，C0C PutRequest，S0F/S37 變長，S10/S38 removal。CT-057 核所有 branch 的 body length/字段與截斷拒絕；CT-058 在原 Client 具真實 resource/catalog 的環境確認 S0F mode0/1/2、S37 descriptors 並測 bag sync/remove。CT-059 在獨立 Server DB 測 item owner、slot+instance unique、split/consume、滿背包卸裝、不同 owner/replay/斷線/重啟及 outbox；再以原 Client GUI 確認物品顯示與裝備外觀。離線 Python 12 unittest 通過只證設計模型，**未執行原版 Client 真實物品生命週期**；不能把衣櫃的 01 slot 00 05 當全部物品 use packet。

## A-004：CT-063～065 物件可見性/更新/消失驗收（planned）

[原版 BIN-first 與 ID lookup](../03-analysis-requests/A-004-roy1-world-visibility.md)：CT-063 驗 S07 逐 kind 變長、S33 u32 ref、S0E/**S5F**（先前 S1E 勘誤）兩種事件、S0C/S64/S11/S1A 解析與長度拒絕。CT-064 以**兩個原版 Client** 同圖互見、連續移動、出視野、斷線、重登、切圖、死亡/復活，比對每個封包 ref/地圖實例及 UI 殘影；CT-065 Server-synthetic 測不同 observer/WorldGeneration/epoch 的 ID 回收、重複 spawn/leave、先死後消失、stale ref/reconnect。離線 20 signature +18 unittest pass 不是 native E2E；原服 AOI radius、NPC 資源與 wire ref scope unknown。
