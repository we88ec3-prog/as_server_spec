# A-016：斷線、重送與崩潰恢復 Server 交接契約

資料來源：[A-016 原版 EXE 分析](../03-analysis-requests/A-016-roy1-replay-recovery.md)，證據 ev_a016_20261031_asgard_replay_static；profile TW-seed0-local-v0.1，樣本 SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。

**Provenance 規則**：C33 / S0B / S14 / C35 / C10 / C04 / C15 的 opcode、body 與 Client callback 是 BIN observed-static（另有 prior profile 輔證）；以下 Session generation、交易 ID、outbox、durable commit 是 **designed Server policy**，不是原版 Server 原生機制。不要擅自把這些 ID 加進 Client wire。

## 一、三種 success 必須區分

- transport_sent：只成功送到 Socket/queue，還不能保證 Client 處理。
- client_observed：例如 S0B 移動確認或 C35 資源校驗；表示特定畫面/世界操作有觀察，但**不等於資料庫 durable commit**。
- committed：Domain 權威狀態及需要持久化的角色/經濟/獎勵已成功 transaction commit，產生唯一 ledger 和可重試 outbox。

不可在只送 S15、S14(2) 或收到 C35 時標示玩家已完全進世界/已完成新手教學。世界 Map/Position 的 safe checkpoint、S04 發送先後需由 DEV 定義且測試 crash boundary。

## 二、idempotency key / 永續資料

|操作|Server internal key|唯一性與交易|
|---|---|---|
|AuthenticateExistingAccount|account_id + auth_generation|錯密不變更世代；合法登入才原子加 generation|
|ConsumeTransferGrant|SHA256(token)+destination+character+generation|一次性 CAS consume；登入 TCP 關閉不能直接清 pending grant|
|CompleteCharacter|verified account owner + pending intent + generation + body digest|角色/外觀一次 commit，unique owner；C04 相同 intent 重送不重建，C15 不能倒刪 committed|
|MoveIntent|world connection_id + generation + expected seq7 + movement body|回送 cached S0B 同 step，seq7 回捲須獨立 expected state；World authoritative 判定|
|EnterMap / MapCRC|character_id + world_generation + loading_epoch + resource revision|single active pending epoch；C35 2×u16 只有 header/checksum，無 epoch。同 pair 舊包與新包無法區分，必要時斷開並重建 session|
|TradeConfirm / Purchase|trade_id / purchase_intent + owner, participant, payload digest|錢包/物品/ledger/outbox 同一 DB transaction；同 key 異 body 拒絕|
|ClaimReward / Quest|character_id, objective_id, claim_revision|唯一 RewardLedger，Quest/Inventory 一次提交；Script Dispose 不觸發領獎|

## 三、重啟、失敗回覆及安全回復

1. 非持久的 pending map epoch、Client UI focus、socket、移動 ack cache 可清；重登後以最後 durable Character/Map/Position 重建 snapshot、可見性與內容版本。
2. 所有舊 socket callback、逾時、斷線事件都須比對 generation/connection_id。不得在舊事件清掉新世代角色/World。
3. DB transaction 尚未 commit：沒有可宣告成功的結果，重試可再判定。已 commit 但成功回覆遺失：按唯一 ledger/outbox 重新產生對外投影，不得再次扣款/給獎/建角。
4. C35 無 map epoch，當同 pair 的舊回覆仍可能在途時，不能假設內部 epoch 足以分辨；避免同 TCP 重疊載圖，無法確證時 fail closed/重建新 World 連線。
5. 遇到非法角色、CRC、位置、交易、帳號/世代與未知原生 status，拒絕副作用；不要擅自使用未證實的 S02 錯誤碼。交易/獎勵 wire 映射待 A-012/A-013/A-026。

## 四、CT 實施

合成驗證工具 [tools/a016_recovery_model.py](../tools/a016_recovery_model.py) 採 Python3 標準庫 sqlite3，測 create ack lost、C10 consume、C33 seq127→0、C35 wrong epoch/same pair ambiguity、SQLite crash/reopen 後的 outbox、兩錢包交易一次及領獎 ledger。

CT-043/044 為 planned、非原生 Client E2E。既有 CT-015/016/017 保留；A-016 integrated/handoff partial 表示**已知 Client interface 與安全 Server 實作子集交付**，不等於原版 Server 的 DB/重登/經濟政策已還原。A-015 原始 tutorial map/spawn 依舊獨立。
