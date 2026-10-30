# A-016 / roy1 — 事件重送、斷線與崩潰恢復（BIN-first + designed contract）

- 日期：2026-10-31；原件：Asgard.exe，PE32/x86，ImageBase 0x400000，3,235,840 bytes；SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。
- 證據 ID：ev_a016_20261031_asgard_replay_static；分支 task_a/roy1（沿用，不新建）；方法：objdump -D -M intel 原始 EXE + repo 已有 A-002/A-022/A-028 交叉驗證、SQLite 合成 crash/reopen 測試。
- 結果：integrated / handoff_status=partial / implementation_ready=true（只限可證 Client codec + 明示 designed 的 Server 防重/持久化骨架）/ native_client_validation=not-run。原服交易、獎勵、切圖/重登重試政策 unknown，不能宣稱相容性完全還原。

## 1. 可稽核原生 BIN 證據（observed-static）

|VA|實際 Client 行為|A-016 意義|
|---|---|---|
|0x53C130、0x53C1A8..0x53C245|AA frame 的 u16 BE length 和 payload 逐 byte 緩存；完整才處理|TCP recv 不代表一筆命令，需處理 split/coalesced frames|
|0x53C25D..0x53C2C6|整包後 decoder 0x53BD90、packet parser 0x5788D0/0x578810|wire ordinal 是 transport 狀態，不是跨重啟交易 ID|
|0x573BF0..0x573C16|C33 writer 依序 3×u8（direction、sequence7、gait）|7-bit seq 回捲，每 128 次可能重複|
|0x583150..0x583172|S0B reader 讀 BE u16 x、BE u16 y、u8 status/sequence|回覆座標/sequence；不證明 DB fsync|
|0x4F2300..0x4F232D|S14 control 1/2/3 switch|三個值不能都當成成功 commit|
|0x4F23CB..0x4F2428|control1 建 C35，取 0x4B4850 MAP header+4 u16 與 0x4B4890 structured checksum|C35 不是角色/地圖切換已持久化證明|
|0x573490..0x5734AA|C35 writer 只有兩個 BE u16|**C35 沒有 map_id、epoch、request_id**；同內容不同載入不能靠本包區分|
|0x4F23B5..0x4F23C9|control2 只有 0x91FBE0 有效才調 loading UI callback|S14(2) 不是 Client 已完成畫面的回執|
|0x4F2333..0x4F23B3|control3 含 Win32 Sleep(3000ms) 及特殊 UI/清理|不能當成原服的 3 秒 CRC timeout|
|0x5773E0..0x5773EE|C10 writer 用 internal length 送 raw token（wire 不另送長度）|一次性 grant 和期限需 Server 自行設計，不得重複 consume|
|0x574420..0x574442|C04 serializer 五 u8（性別/髮型/RGB）|wire 無全域 request ID，不能靠外觀 bytes 做跨重登唯一性|
|0x4B1F1B..0x4B1F34、0x5715F0、0x5716A0|C15 CancelNewUser opcode0x15、空 body，在 S02 error 後 Client 送|沒有指定原 Server 哪筆 DB commit 撤銷；晚到 C15 不能假定可刪已建角|
|A-023 C6C/S44 靜態成果|Script Dispose 回覆/清理可單獨到來|Dispose 不是 Quest 完成或獎勵可領的證據|

已知 profile 的成功 S0B body 000b000aff 是 x11/y10/status0xff；成功與 bit7 語意沿用既有 profile，**本輪新增 observed-static 僅欄位型別**。C33 移動 7-bit sequence 只適用該 World session，不能作永久去重鍵。

## 2. C35 的重要不可判定性

C35 body 僅 2×BE u16（map header word、MapData structured checksum），**沒有 map epoch、session generation 或 map_ref**。兩次載入同版本同地圖時，一個延遲到達的舊 C35 與本次合法 C35 可能 byte-identical；即使 Server 在內部有 epoch，也無法從該 wire 本身辨認。這是字段上的技術限制，不是原版 Server 已觀測到 BUG。

Designed 安全處理：每條 World connection 只容一個 pending loading epoch；所有新命令都受當前 generation、expected map/version/pair 與狀態閘限制。若同 TCP 上舊 epoch 的同 pair C35 仍可能在途，**不能宣稱單靠 epoch 能消除歧義**；須序列化完成舊載入並建立可辨識的 handshake 邊界，不能安全排空時直接中止舊連線、重授權並重建 world snapshot。禁止假造 C35 未傳送的 epoch 欄位。

## 3. 每種操作的 dedup key、提交點、成功定義（designed；不是已知原服）

|操作|Server 內部 Idempotency/Fencing key|提交點及回覆邊界|
|---|---|---|
|C03 登入|account_id + auth_generation（只有密碼驗證成功才 CAS）|失敗認證不撤銷原 World；合法的新 generation 才替換舊|
|S03→C10 轉 World|digest(token)、account/character/world/generation/expiry unique|C10 原子 consume 一次才綁 World；Login socket 斷線不直接撤銷尚有效 grant|
|C04 建角|verified_owner + pending_intent_id + generation + body_hash；DB unique owner/character|經 A-027 owner 安全驗證後才能 transaction 保存 Character+Appearance；**durable commit 後**才可產生 S02 success（設計策略）；回包丟失不重建|
|C15 取消|current owner/session/generation/pending intent|只取消尚未 durable commit 的 pending；舊 C15 不刪已持久化角色|
|C33/S0B 移動|world_session + character + generation + seq7 + complete move body 的短期快取|Server authoritative position 已裁定才送 S0B；相同重送回 cached ack、不走第二步；seq7 回捲須以 expected state 校正|
|S15/S14/C35/S04 切圖|character + world_generation + loading_epoch + map_id + content_revision + DB position_version|C35 僅驗地圖，**不是** durable 入圖；何時 DB 存 map/pos 由 Server 設 commit boundary；斷線從最近已提交的位置恢復|
|商店/交易/物品移轉|內部 purchase_intent_id/trade_id、owner、payload_digest、version|錢、物品、雙方 owner、outbox 一個 DB transaction 成功後才可對 Client 宣告結果；原版 opcode 與回覆未在本 A 證明|
|領獎/任務|character_id + objective_id + claim_revision 的唯一 ledger|任務狀態/RewardLedger/Inventory 原子成功後只發一次；Script Dispose 不能直接完成 quest|

**三層成功必須分開**：transport_sent（只是 socket 寫出）/ client_ui_callback（本地畫面有有限回覆）/ server_authoritative_committed（已裁定/持久交易）。S0B 和 C35 都不能替代資料庫 durable commit 證據；若 DB commit 後 success response 遺失，用持久 ledger/outbox 重建可見結果，不能再执行副作用。

## 4. 中斷與重啟故障矩陣（designed）

|時間點|期待的保護與恢復|
|---|---|
|登入驗證前或錯密時斷線|generation、舊 World 不變；不發 transfer grant|
|S03 已發、Login TCP 正常關閉|合法 grant 可在 TTL 內由新 World C10 消耗，否則 Client 可能永遠轉服失敗|
|C10 消耗前/後崩潰|未消耗的 grant 按安全 policy 失效/恢復；已消耗不重用；重連重新認證/恢復，不留下幽靈 World entity|
|C04 durable commit 前 crash|回滾半角色、不發 S02 success；pending 逾期清除|
|C04 durable commit 後 S02 遺失|重啟仍只有一個角色、相同 intent 返回既有結果；outbox 保留需投影的回覆|
|晚到 C15|不刪已提交 Character/Appearance/Reward|
|C33 重送、sequence127→0 或舊 generation|原本同一步回 cached ack；回捲不當作永遠相同命令；跨 generation 舊指令拒絕|
|C35 之前/之後斷線或 crash|清暫存 loading epoch/visibility，按 durable map/position 與內容版本重建；C35 成功不等於 tutorial_completed|
|同 pair C35 跨 epoch 延遲|單靠 wire 無解，重疊 load 必須 fail closed／重連；不得誤認可完美去重|
|交易或領獎 commit 後回包遺失|依 trade/claim unique ledger 返回已提交結果，不再扣款、增發獎勵|
|重播 C6C Script Dispose|不當作任務完成或可再領一次獎勵|

## 5. 可實作規格與不可宣稱之處

Gateway/Session 可以生成 server-internal connection_id, account_generation, loading_epoch, request_intent_id, expected_state_version；**Client 沒有這些 wire 字段，不能擅自擴充原版封包**。所有舊 socket cleanup 須比對 generation；高價值副作用以唯一索引、原子 DB transaction、outbox 與可重建 read model 保證。玩家移動可選適當持久 checkpoint，但絕不能從 S0B 推斷原 Client 要求每步 fsync。

本輪沒有可核對的原版 trade/purchase/reward opcode、原伺服器 DB commit/timeout/重登政策，這些工作只交可執行 designed Domain/DB 方案，仍需 A-012/013/026 與 Server CT；原生教程 map/spawn/CRC version 依 A-015/A-022，不能用 Born (31,29) 指引文字當出生點。

## 6. 測試與交接

- tools/a016_recovery_model.py：Python stdlib sqlite3 合成測試。登入 grant 一次性、C04 未授權拒絕/成功重送、SQLite 重啟後 outbox/角色唯一性、C35 epoch/fail closed、C33 7-bit seq127→0、錢包雙邊移轉與獎勵唯一 ledger。
- CT-045：持久狀態/idempotency crash/reopen（designed, native Client not-run）；CT-046：C35 無 epoch 的限制與同 pair 模糊重送（BIN-derived bound + designed fallback）。
- 既有 CT-015/016/017、SCN-003/010 更新 provenance 與故障注入，不因人工正常切圖/一般登入通過就宣布重啟恢復已 passed。

## 7. 復核（VA，不是 file offset）

sha256sum Asgard.exe
objdump -D -M intel --start-address=0x53c130 --stop-address=0x53c2e7 Asgard.exe
objdump -D -M intel --start-address=0x573bf0 --stop-address=0x573c17 Asgard.exe
objdump -D -M intel --start-address=0x583150 --stop-address=0x583173 Asgard.exe
objdump -D -M intel --start-address=0x4f2300 --stop-address=0x4f2442 Asgard.exe
objdump -D -M intel --start-address=0x573490 --stop-address=0x5734ab Asgard.exe
objdump -D -M intel --start-address=0x5773e0 --stop-address=0x5773ef Asgard.exe
objdump -D -M intel --start-address=0x5715f0 --stop-address=0x5716a1 Asgard.exe
python3 tools/a016_recovery_model.py

原始 EXE、MAP/DAT 資產、帳號/token 與巨大 dump 不入 Git；缺少原服 trace 不可由此填造原服交易/獎勵/CRC 錯誤碼。
