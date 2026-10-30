# A-017 — 管理 API 與觀測資料的安全可交付契約

來源：[A-017 原始分析及 Server 需求](../03-analysis-requests/A-017-roy1-admin-audit.md)，證據 `ev_a017_20261031_management_contract`、需求 R-018/R-019/R-021/R-025。這是 **designed Server specification**，非原版管理指令逆向已完成；原版 Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。A-017 integrated/handoff ready **限管理 API/觀測契約**，不代表原 Server 存在此接口或已在 `as_server_roy` 實作。

## 管理入口與角色

`/admin/v1` 獨立於 Asgard 原生 C2S/S2C socket，須有已認證的 operator identity、permission、目標對象狀態與 `Idempotency-Key`。原 Client 無任何預建 Account 認領權限（A-027）。允許網路隔離/allowlist，但 URL/IP 本身不能替代有效身份。RBAC：observer=read；support=read/suspend/unsuspend；game_master=read/teleport/adjust/item.grant；admin=全部含 account.provision。最小權限、拒絕也稽核；正式部署身分取得、credential rotation/rate limiting 屬 DEV/OPS。

## Actions、交易和衝突

見機讀 [admin-operations.json](../02-server-planning/admin-operations.json)。Account.ProvisionAccount 僅後台；Suspension:N 天或 permanent，expiry 用 Server UTC，解封需 version CAS 並 reconcile 已在線 Session。GM teleport/character.adjust/item.grant 必須通過 World/Character/Inventory Domain owner/version/資料合法值檢驗，不得直接編排未授權的原 Client game wire 或對任意角色改 DB。

高價值操作須與 `unique(actor_id, idempotency_key)`、`payload_digest`、原子 domain ledger、outbox 同事務：同 key 同 body replay 原結果；同 key 異 body 409 conflict；提交後 HTTP 回覆遺失仍不可二次副作用。A-016 C35 沒有 epoch，若玩家 loading 時要傳送，要用 Server world_generation/one active epoch fencing，無法消除舊 C35 混淆就 fail closed/reconnect。

## 最小 audit/trace 白名單

Audit：`audit_id,timestamp_utc,actor_type,actor_id,auth_method,operation,target_id,request_id,idempotency_key_hash,correlation_id,decision,reason_code,committed,before_version,after_version,result_code,source_network_zone,latency_ms`；World trace：`profile,connection_id,session_generation,world_instance,map_id,loading_epoch,opcode,frame_length,parse_result`；reward/trade 只記 business operation ID/版本/commit outcome。全部使用 sanitized、必要時 hash 或 pseudonymize。**永不記錄 password、token、Authorization、cookie、全封包 body、憑證 hash、私人聊天或 script 原文**。即使 debug/error 也不能例外，原始未知 JSON keys 必須剔除。

Metrics：Admin allow/deny/replay、auth accepted/rejected、token rejected、World tick/queue、C35 mismatch/timeout、DB commit/rollback、outbox pending。健康/metrics 監看與 audit 查詢也須受 access boundary 管制。需要追查時用 correlation_id + UTC 時間窗，無需複製敏感 bytes。

## CT 與未知

[SQLite 合成測試](../tools/a017_ops_contract.py) 覆蓋 permission/identity deny、停解權、道具冪等、角色修改、紅字串剔除。CT-045（Auth/RBAC/atomic/idempotency）與 CT-046（sanitized audit/trace/metrics）為 planned；原生 Client E2E `not-run`，不推定 Server 已開發。原版 GM opcode、原服管理 UI、真正 ban/kick status、交易物品合法值仍 unknown；需 A-007/013/018 及後續 DEV/CT 或原服證據。
