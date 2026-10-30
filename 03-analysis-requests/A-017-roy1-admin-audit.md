# A-017 / roy1 — 管理操作、權限與可觀測性：Server 規格分析交接

- 日期：2026-10-31。基線：Asgard.exe PE32/x86；本機 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。工作：既有 `task_a/roy1`，不建立 branch。
- 需求：`R-018` 管理/營運，`R-019` 診斷且不記敏感 body，`R-021` 長度/速率/狀態/權限安全；額外遵循 `R-025` 僅管理端建立帳號。
- 研究方法：核對原件 SHA256、原版 PE 字串中 `./packet/sblockclient.cpp` 等 debug path；交叉閱讀 `01-server-requirements/requirements.json`、`02-server-planning/interfaces-and-data.md`、A-002/016/021/027/028 的權限/交接/持久化已知事實；設計獨立 Admin API 和無敏感資訊的審計契約，建立可執行 SQLite 合成測試。
- 證據 ID：`ev_a017_20261031_management_contract`。**evidence_kind=designed**（附原 Client 靜態邊界），不能由 Client 的 `sblockclient.cpp` 檔名字串推論原版有帳號永久停權、特定 GM 指令或 Admin HTTP 端點，也不能宣稱原服內部具備此 RBAC。
- 判定：`status=integrated`、`handoff_status=ready`（**此 A 限定的 Server Admin/Observability 設計範圍**）、`implementation_ready=true`、`native_client_validation=not-run`、`original_admin_wire_evidence=unknown`。Server 是否已開發/驗收另由 DEV/CT 決定。

## 1. 信任邊界與權限

**管理入口獨立於原生遊戲 TCP/wire**；管理員身份由獨立管理認證/憑證與授權 policy 提供，不等於 Game Client 的 C03 或 C02 登入。Game Client 不得呼叫 Admin.ProvisionAccount、Ban、GrantItem、Teleport。安全層要同時檢查 `actor_id`（非空且已認證）、`permission`、`target`、`reason_code`、`request_id`、`expected_version`、輸入 bounds，且 Server Domain 真正重新驗證擁有者/狀態。只有 URL、指定 IP、可猜 API path、正確帳號名**不能構成身份授權**；本機可另採隔離 network binding，但不足以替代正式認證。

設計權限集合（**非原版遊戲管理者角色還原**）：
- `observer`：僅讀去識別狀態/診斷（`ops.read`）。
- `support`：讀、帳號停權/解除停權（`account.suspend`、`account.unsuspend`）；無權調整數值/物品。
- `game_master`：讀、角色傳送/合法屬性調整/物品補發（`character.teleport`、`character.adjust`、`item.grant`）；無權直接建帳。
- `admin`：上述全部，外加 `account.provision`、帳號狀態/操作者設定，仍須 reason/audit/idempotency。
- `operator/service`（非玩家）：只管理運行狀態、診斷管道/恢復操作，不能由 service identity 自動擁有財產增減權限。RBAC 與特定部署 token/mTLS 選擇由 DEV 決定。

**禁止**由管理 API 對 Game Client 轉發「假 C2S GM 指令」來繞過 Domain，也禁止把管理密碼明文複製到遊戲封包。僅提供後台已驗證的 `AdministrativeCommand`；登入停權由 Auth 在 C03 與 World generation/reconnect 處檢查，並使現存 session 失效/通知策略可單獨設計（原 Client 踢下線文義 unknown）。

## 2. API 與 Domain 命令（designed）

獨立前綴 `/admin/v1`，不是原生 Client endpoint：

|操作|建議 API|權限|成功/提交邊界|
|---|---|---|---|
|新增預建帳號|`POST /accounts`|`account.provision`|Account/Credential（密碼只用安全 hash，不稽核明文）原子提交；Client C02 永遠不 INSERT Account|
|停權 N 天/永久|`POST /accounts/{id}/suspensions`|`account.suspend`|`duration_days:1..3650` 或 `permanent:true` 二擇一，`expires_at` UTC 或永久；不接受負數/0/兩種同時提供|
|解除停權|`DELETE /accounts/{id}/suspensions`|`account.unsuspend`|由帳號狀態 transaction + version CAS + session fencing 寫 audit；過期政策由 DB 時鐘決定|
|調整角色屬性|`POST /characters/{id}/adjustments`|`character.adjust`|強制 expected_version、合法上限/下限、原因、同一操作幂等，不直接改封包快取|
|角色傳送|`POST /characters/{id}/teleports`|`character.teleport`|先驗 map_id/content_revision/map bounds，更新 world authority/snapshot 與當前 session generation；busy/loading 拒絕或排隊，不假定 Client 可任意 teleport|
|發放物品|`POST /characters/{id}/item-grants`|`item.grant`|合法 item_id/數量、背包空間/綁定與唯一 grant ledger；回包遺失不重複補發|
|查詢玩家/場景|`GET /sessions`, `GET /characters/{id}`|`ops.read`|僅必要字段與去識別 ID，分頁/filter、來源權限檢查|
|查詢審計與健康|`GET /audit`, `GET /health`, `GET /metrics`|`ops.read`（health 可另對 probe）|不得回傳原生 full packet/body/密碼/token/個資完整內容|

所有有副作用 API 用 `Idempotency-Key` + actor_scope + canonical payload digest，並以 owner/target/version CAS 原子寫入業務結果、唯一操作 ledger 和 outbox。相同 key、同 payload → 回原結果；相同 key、不同 payload → 409 conflict，不能二次執行。權限失敗也產生 audit，禁用 side effect。需要取證時至少保留 `before_version/after_version` 及安全摘要/變更字段而非 secret。

## 3. AuditRecord 必備內容與敏感性

建議 machine-readable fields：
`audit_id`、`timestamp_utc`、`actor_type`、`actor_id`、`auth_method`（方法 enum，**無憑證本身**）、`operation`、`resource_type`、`target_id`（必要時 pseudonymize）、`request_id`、`idempotency_key_hash`、`correlation_id`、`source_network_zone`（不記未必要的完整 IP）、`decision` (allow/deny/error/replay)、`reason_code`、`before_version/after_version`、`committed`、`latency_ms`、`result_code`、`server_build/client_profile`。

**絕不可記錄**：原始 C03 密碼、C02 第二欄疑似 secret、S03/C10 transfer token、HTTP Authorization/Cookie、完整封包 body、憑證 hash、玩家私訊/chat 原文、完整 Script 原文、原生記憶體 dump；只允許 opcode、direction、sanitized packet_length、result、hashed correlation。未知/非白名單 JSON fields 完全丟棄；不得因 debug log 級別放寬。Audit 以 append-only/不可任意竄改為目標，可附防竄改鏈/集中儲存、retention/access policy 由營運需求定。

同一請求可能出現「被拒絕」「成功提交但 API 回覆遺失」「相同 key 重播」「業務超時」；Audit 需分清 `received`、`authorized`、`committed`、`notified` 四種狀態，不能把傳送 Client ack 視為 DB commit。

## 4. Ops correlation 與世界事件（designed）

- Gateway：`connection_id`、`account_ref`（去識別）、`session_generation`、`direction`、`opcode`、`frame_length`、`parse_result`、`client_sha256/profile`；保證不輸出封包原文。
- World：`character_ref`、`world_instance_id`、`map_id`、`loading_epoch`（Server 內部）、`content_revision`、`C35 expected_pair_hash/result`；**C35 wire 沒有 epoch，不能假稱原 Client 送了該值**。
- Commands：`idempotency_key_hash`、`domain_command_id`、`db_transaction_id`、`outbox_id`、`recovery_reason`、`state_version`；C33 sequence7/移動 ACK 不等於 durable DB commit。
- 指標：登入成功/失敗與 rate limit、活躍 session、transfer grant consume rejected、opcode parse/reject、queue depth/backpressure、World tick p50/p95/p99、C35 mismatch/timeout、DB transaction latency/rollback、管理操作 allow/deny/replay、outbox pending age。禁止以未量測指標聲稱實際容量。
- 導出 trace 只使用小範圍 opcode+結果+時間窗、hashed identity，並提供 TTL/刪除與操作者稽核。A-018 另外負責基準負載與 tick/capacity 數據。

## 5. 角色傳送與線上操作的重要前置

Admin 身份已授權亦不代表可直接修改線上角色的 map/position：World authoritative state 與 DB snapshot 必須同一個 `character_version/world_generation` 上 CAS；載圖途中等 pending epoch 完成或 fail closed（A-016）。S15/S14/C35/S04 的已知 layout 是 Client world 介面，不是 Admin 發送封包的入口。角色屬性/物品種類的完整合法值受 A-003/A-007/A-013，地圖合法座標受 A-015/A-005 限制；資料還沒證明時只能實作 domain validation 和拒絕，不能用假 data 通過原生遊戲驗收。

## 6. 失敗與拒絕矩陣（示意操作測試）

|Case|行為|
|---|---|
|未登入、停權操作者、觀察者發 item.grant|拒絕；audit decision denied；沒有 items/ledger/Client packet|
|IP 在 allowlist，但無有效 admin identity|**仍拒絕**；URL/IP 是 network gate，不是權限|
|相同 Idempotency-Key 的 item.grant 重送|返回首次已提交結果，不再次產生物品|
|相同 key 異 payload|409 conflict；無第二次 side effect；audit retained|
|停權 0 天/負數/錯誤格式/已解除重送|輸入拒絕或安全冪等；不讓原 Client C02 自動建帳|
|線上角色 map 正在 loading，GM 要傳送|需 version/generation world authority 原子協調；不能強制雙重 S14 或接受舊 C35|
|Server commit 但 HTTP response 遺失|重送同 key 返回 durable ledger 結果；audit 標 replay，不能重扣/增發|
|trace/debug 開啟|即使 error 也不留下 password/token/完整 sensitive packet；只採去識別白名單字段|

## 7. 成果、範圍與驗收

- `04-analysis-integration/A-017-admin-observability-contract.md`：API、RBAC、稽核 Schema、信任/傳輸與狀態機 contract。
- `02-server-planning/admin-operations.json`：機讀行政操作 + 權限 + 驗收依賴；**不是新 game opcode**。
- `tools/a017_ops_contract.py`：SQLite 合成 tests（permission denied、未認證、suspend/unsuspend、teleport+adjust、item.grant idempotency/conflict、敏感字串剔除），單次執行五測 passed；**不代表 GitHub Server 的真實測試或原生 Client 互動**。
- `CT-050`：Admin 副作用的身份/權限/ledger/重送；`CT-051`：trace/audit redaction & correlation。預設 status planned，native_client_validation=not-run。建議創建 `SCN-014` 獨立管理 API 情境，與 Game Client SCN-007 分離。
- **未知**：原版遊戲服務端管理者身分模型/GM 專用封包、帳號停權/踢人原服 status、在線世界傳送完整原生動態回覆、各職能細粒度資料合法集合、正式 admin service 部署與權限實測。此 A 不該擅自新增猜測的 PKT opcode；後續 A-003/005/007/013/018 和 DEV/CT 會補實際行為。

重現：`sha256sum Asgard.exe`、`strings -a -el Asgard.exe | grep -i 'sblockclient.cpp'`、`python3 tools/a017_ops_contract.py`。原件遊戲檔、任何玩家憑證/封包不可提交至共用 Git。
