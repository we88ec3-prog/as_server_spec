# 封包與遊戲情境整合

## SCN-001 登入／進圖

raw greeting → C62 → C00/S00 → C0F/S18 → C57/S56 → C57或C4B/S60（詳見profile-login.md） → 錯誤C03/S02後可重試 → 正確C03/S03 → 新連線C10 → C25 → S02成功建立世界UI → S05建立自己 → S15地圖 → S14(1) → C35 → S04定位 → S33可見角色 → S0F背包及必要S37 → S14(2) → S19音樂。

Client收到S02之前尚不能假定MapPane存在；S15之前必須已有MapPane及自己。成功交接token是opaque bytes，須一次性且過期；目前60秒是本機策略。

## SCN-002 連續移動

C33(direction,seq,gait) → Server驗證（碰撞／速度待補）→ S0B(new_x,new_y,0x80|seq)。Client的移動狀態解除等待，才能連走；sequence模128。C11單byte方向更新面向。拒絕與校正分支、他人移動廣播尚未完成，不能從此成功情境推導全部行為。

## SCN-003 在線切圖

已授權命令 → loading狀態 → S15 → S14(1) → C35 → S04/S33/S14(2)/S19。不重送S02/S05、不重複背包。原生S15清理其他場景物件但排除自己。載入中拒絕新切圖；CRC不回、斷線、資源讀取失敗的補償策略必須在A-016完成，不可先宣稱具備無縫跨服。

## SCN-004 外觀／SCN-005 多人／SCN-006 音樂

外觀見appearance.md及items.md；多玩家目前只有S33入口，尚欠出生／移動／移除完整生命週期。音樂S19 kind1 repeat0循環、track0停止，Client仍控制開關及音量；曲1的預設不是官方map配置。

所有情境還應包含：前置狀態、參與者、輸入、輸出、Client效果、Server狀態、保存點、拒絕與取消、逾時、重送、重登／重啟、證據及CT。正常情境通過不能代替這些分支。

## SCN-007～010：首次玩家縱向情境（尚待分析/驗收）

- **SCN-007**：授權管理員獨立建帳 → 玩家原 Client C03 只登入已有帳號；停權/錯密拒絕，Client 不可建帳。
- **SCN-008**：已預建無角色帳號 → 原生創角 UI → C02/C04（完整次序與 S02 待 A-021） → 原子保存；取消、重送、同名不得留半角色。
- **SCN-009**：已保存角色 → S03/C10/C25 → SCN-001 已知初始化 → A-022 證明的新手地圖與出生座標 → loading 結束可操作。
- **SCN-010**：創角、token、進圖提交前後故障恢復；教學入口與完成狀態分離。

參見 [完整需求](../01-server-requirements/first-login-onboarding.md) 與 scenarios.json；既有 SCN-001 已驗收子集不更改。

## SCN-011～013：完整教學的新增待分析情境

- SCN-011：原生教學地圖的 NPC／怪物生成、行動及清除（A-024）。
- SCN-012：原生 Client 技能／攻擊指令、Server 判定與任務進度（A-025）。
- SCN-013：原生教學完成、存在才發的獎勵、出圖、恢復（A-026）。

scenarios.json 的對應 packets 目前為空，意思是**尚未取得有證據的教程 opcode**，不是不需要封包。

## A-022 / roy1：MAP/CRC 載圖及重連靜態證據

[完整研究](../03-analysis-requests/A-022-roy1-bin-analysis.md) / [協定子集](A-022-map-loading-crc.md)。S15 3個 BE u16+flags u8+another u8+string8；S14(1) 要求 Client C35 的**MAP file header offset+4 u16 與 MapData 結構化 CRC**（第一欄不是 map ID）；S14(2) loading callback，3 延時異常。S04 4×BE u16 定位。Server 必須以 map identity+resource version+epoch 證實相同的 C35 再定位入圖；錯圖/斷線/舊 epoch 復原，tutorial_entry 與 completed 分離。原版教程 map/spawn 未從單一 EXE 證實，需 A-015 原版 MAP/Script/Born。

## A-002 / roy1：登入、跨 TCP 轉服及重複登入邊界

[完整分析](../03-analysis-requests/A-002-roy1-login-transfer.md) 和 [合成模型](../tools/a002_session_model.py)。C03 兩個 string8 + u8；S03 `0x5886C0`：u32 address、u16 port、u8 token_len、token raw bytes；`0x4A8370` 的 region3/4 handler 連 World 並送 C10，其 `0x5773E0` serializer 發 raw token，**不另帶 token_len prefix**。此函式不是 C25。Server-designed：成功認證後發一個綁 account/character/generation/destination 的短效一次性 grant；**舊登入 TCP 關閉不可直接令 grant 失效**；第二個合法登入原子換 generation、舊 socket 延遲斷線不可移除新世代。原服重複登入是 kick 或 reject 仍 unknown；CT-037/038 planned，Client 實測尚未進行。

## A-028 roy1：C04 後 S02、C15/CancelNewUser 與重登邊界

[原生 S02 UI 深度分析](../03-analysis-requests/A-028-roy1-c04-terminal-analysis.md)；[Server 安全交接](A-028-newuser-terminal-contract.md)。確認 C02→S02(status0 at local0x1d)→C04(五 u8)→local0x1e；再收 S02(status0) 走 local UI `0x4b206b`，**不是此回調直接發 S03**。非零 S02 建構/送出 C15（opcode0x15，empty body），state0x1f，特定錯誤碼影響本地焦點（不是已知原服錯誤文字）。A-028 integrated/handoff partial，**原 Server 角色持久提交時點與原生預建帳號 owner 驗證仍 unknown**，SCN-008/010 不可標為原生全程可實作。新 PKT-C15、CT-041/042 planned，Server 可先做 transaction/idempotency/pending cancellation 的 designed 模組。

## A-016 / roy1：事件重放、移動 sequence 與世界 crash recovery

[A-016 原生證據和設計矩陣](../03-analysis-requests/A-016-roy1-replay-recovery.md)、[Server 契約](A-016-idempotency-recovery.md)、[SQLite 合成測試](../tools/a016_recovery_model.py)。C33 `0x573BF0` 序列化 3×u8，S0B `0x583150` 讀 BE u16 x/y + u8 status/seq；**7-bit seq 每128次回捲，不能永久作交易 ID**。C35 `0x573490` 僅兩個 BE u16，無 map epoch；當舊/新同 pair 重疊時 wire 不可判定，必須串行、fence 或 fail closed 重新 World 連線。S14(2) local callback 不是 DB durable ACK。Account/Character/World/交易/領獎用內部 generation、intent、outbox、ledger 原子性保障重送/崩潰；交易獎勵原生 opcode 尚待分析，**不可捏造原版行為**。CT-043/044 planned，A-016 integrated/handoff partial，只交證據支持的 Client 接口與 designed recovery。SCN-003/010 的失敗/重啟未原生實測，仍非 fully passed。

## SCN-014：管理操作與遊戲協定分離

[A-017 機讀管理操作](../02-server-planning/admin-operations.json)／[詳細稽核與權限規格](A-017-admin-observability-contract.md)。使用獨立 `/admin/v1` Admin 操作（Admin 認證/RBAC、停權/解封/補道具/調整/傳送），**不是新增原版 game C2S opcode**。所有 allow/deny/replay 有去敏稽核與 correlation ID；URL/IP 可達不代表授權；同 key 重送不重做副作用。CT-045/046 planned，A-017 設計研究 handoff ready、Server/原生 Client 的管理行為不宣稱已實作/通過。

## A-003 / roy1 首次創角合法集合、角色數量與重名界線

[完整 A-003 證據](../03-analysis-requests/A-003-roy1-create-legal-values.md) / [安全交接](A-003-character-create-contract.md)。已證 C02 的第一 NewUser UI 欄位 region0 skip narrow-length gate／其他 region >=12，C04 只含 sex/hair/3×RGB u8，十筆固定 Client 色盤；**C04 並無單獨 character_name 欄位**。原服是否帳號同名角色、是否支援多角色、sex/hair 正式枚舉、重名錯誤碼均無原服證據，Server 的 unique(account)/name 和 IdempotentCreate 屬 designed 保護，不能由此開放匿名 Client C02 建角。SCN-008 保持 analysis-required；CT-047/048 planned。

## A-020 / roy1：SCN-001 登入前已知多分支

[完整資料流](../03-analysis-requests/A-020-roy1-prelogin-branches.md) / [Contract](A-020-prelogin-contract.md)。C0F type3 body03 → S18 kind0 subtype3 count0（00030000），C57 type1 list、type0 selected id，S56 多記錄 zlib，C4B empty 與 S60 type0/u32、type1 compressed 可由原本 Client reader/writer 支持。**原版 Client code 並不證明原伺服器在所有 region 依這個順序發公告或要求 Script；最小本機 SCN-001 通過的測試數據和全原生服務需分開**。C6C3 local no-op 並非 Born start；未經授權 S44(1,3) 會影響本機檔案。CT-049/050 planned，Client E2E not-run。

## A-025：SCN-012 教學技能/攻擊到任務目標（條件式；非原服必需戰鬥已證）

[詳細研究](../03-analysis-requests/A-025-roy1-tutorial-combat.md)。Client C13 攻擊 target u32、C4D 開始施法 u16、C56 CastSpell u8；S52 CastSpell u32+u8、S5F DieObjects u32，C3D/S3D Battle 的 u8 subtype 0..15 多態（每個 subtype 尚未完整）。**不能把 S5F 消失、C13 攻擊指令或 Script C6C 關閉直接算 quest success**。Born 引導找 (31,29) 女性招募員、未宣告殺怪需求，但其他未知任務 Script/原服可能另有戰鬥。Server 對已驗證目標/怪物/原服任務 mapping 才可生成 unique event 並計進度；目前 `native_tutorial_combat_requirement_proven=false`、`native_quest_progress_mapping_ready=false`，SCN-012 維持 `analysis-required`。A-024、A-008/009/010、A-012/026 接續；CT-051/052/053 planned。

## A-026 / roy1：SCN-013 完成教學／發獎／出圖的有界證據

[A-026 原版 Client/資源核對](../03-analysis-requests/A-026-roy1-tutorial-completion.md) / [安全 Domain 設計](A-026-tutorial-completion-contract.md)。Client 只證：S44 指名 Born Main → 紙張引導 (31,29) 招募員 → C6C4/C6C2 lifecycle close；另有 C39 generic Merchant NPC、C0B Quit empty、S15/S14/C35/S04 generic map load。**沒有**證實的 Server quest completion、npc id/script binding、可選獎勵、退出目的 map/x/y 或重登入恢復政策。SCN-013 不得因 C6C close、C39 click、S5F death、C35 或 S14 control2 標 completed。只在 verified original rule + authoritative event 時做單事務 Complete+optional Reward+Outbox，only verified exit map/revision 能切圖；失敗時保留 durable completion 並按上次 map/pos 恢復。CT-026～028 仍 planned，另 CT-054～056 synthetic/design；原 Client not-run。

## A-007：SCN-015 物品實例、裝備、背包數量/移除及重登

[原版 Client packet 分流](../03-analysis-requests/A-007-roy1-inventory-lifecycle.md) / [安全開發接口](A-007-inventory-domain-contract.md)。C1C use_kind1..9 變長、C1E slot、C08 Drop 3u8、C0C PutRequest u32BE、S0F/S37 變長加物品與裝備、S10 3u8 和 S38 2u8 移除／更新。這些都是 Client 協定能力，不代表原服堆疊上限、拾取地面物件 id 或卸裝 UI 已知。Server-only ItemInstance/owner+revision+unique op ledger 用來保障物品不可複製/重領/跨帳移動；滿背包卸裝需原子拒絕且原裝備保持，Client C1C 無原生 globally unique transaction ID，無法只靠重送 raw bytes 永遠識別重複指令。SCN-015 `analysis-required`、CT-057/058/059 planned，原版 Client 全程/物品 economy 仍未實機驗收。

## A-019 / roy1：SCN-006 地圖背景音樂配置仍只有通用原版播放能力

[A-019 native S19/Map 索引報告](../03-analysis-requests/A-019-roy1-map-music.md) / [音樂來源安全契約](A-019-map-music-contract.md)。原 Client 會依 S19 kind1+repeat+u16BE track 決定播放編號並組 `%05d.mp3`；kind!=1 是另一個音效處理分支，不含 repeat。Map0/1/2.dat 確認有 494 個索引 *.map 名稱、無 MP3 filename 或官方 map→track table，因此**任何地圖的 track 設定均未經原始 Server/資源證實**；未知時不要自動播放 track1，若選擇換圖 stop，須標示為 designed fallback。已通過的本地「聽見音樂」只限 manual-pass-subset，不能說原服背景音樂對應完成；正式驗收應取同版本多張地圖的 Server→Client S19 與 map_id 對照 trace。CT-060～062 planned，原版 Client E2E not-run。

## A-004 / roy1：SCN-005/011 多人視野、其他物件消失

[完整原件研究](../03-analysis-requests/A-004-roy1-world-visibility.md) / [Server Domain](A-004-entity-visibility-contract.md)。Client 對其他 human 使用 S33；generic object 使用 S07(count/type/u32 ref＋變長尾欄)；S0C/S64 同步他人位置/路徑，S11 同步方向，S1A 動作，S0E u32 ref 離開/移除，**S5F u32 ref 是獨立死亡相關事件**（勘誤舊 S1E opcode）。MapPane ref lookup 0x4eac30、S15 換圖清舊場景其他物件。新 Server 每個 observer/WorldGeneration/map_instance 維護 visible ref→stable entity 綁定，不允許跨地圖、跨 generation 刪除；同 TCP 原生 wire 無 epoch，重用 ref 前需排序/屏障。不把 S5F 視為 Server quest progress 或把 S0E 視為永久刪除。SCN-005/011 分析仍需原版雙 Client/runtime 與 A-024 NPC/Monster mapping；CT-063～065 planned。


## A-011 / A-022：NPC／怪物與原版 MAP 資源對接

[A-011](../03-analysis-requests/A-011-roy1-npc-monster-resources.md)：Monster bank 指標格式 `Monster%02d.dat`（`Monster00.dat`～`Monster42.dat`、resource index 0x1f40..0x1f6a），S07 kind + appearance_candidate:u16BE + object_ref:u32BE 另屬不同命名空間；S1A/ S11/S0C/S64 動作／方向／位置，C39 subtype 商人操作。沒有 Monster 檔及 NPC 原始 Script/Server trace 前，不能聲稱物件 ID→某個怪物模型/動畫/點擊/掉落成立。SCN-011、A-024 原生 NPC 教學仍待分析。

[A-022](../03-analysis-requests/A-022-roy1-map-geometry-collision.md)：已核對 Map0/1/2 原件 491 個完整格子 MAP，寬高、10B raw tile、17B local tile 與 7/8/16B records；`00000.map,10000.map,20000.map` 是特殊零維。任意 map 的 `0<=x<w,0<=y<h` 只證可索引，不能當可走、合法 NPC spawn、官方 tutorial map 出生點。Client line-test bit0x10 不是原服移動真值；SCN-009 首生、SCN-011 NPC 仍 analysis-required，CT-066～071 planned。
