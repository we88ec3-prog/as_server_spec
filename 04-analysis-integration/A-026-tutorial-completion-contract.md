# A-026 — 新手教學完成/獎勵/退出圖 Server 交接

[完整 A-026 BIN-first](../03-analysis-requests/A-026-roy1-tutorial-completion.md)；Evidence ev_a026_20261031_born_merchant_exit_bin_static。原 Client SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。以下**設計**，不是原始 Server 的完成判定。

## Client 輸入與結果

S44(1,0) 可啟動 Born.Main；PaperDialog OK 依 native Dispose 產生 C6C(4,Born,context)、再依 replied flag C6C(2,Born,context)。C39 Merchant 是另一個原生互動入口：u8,u32 BE,u16 BE，再依 type 選不同 payload，**尚無 NPC entity binding**。C6C1 的對話回答及候選 nNewJoin01 STATE=ACCEPT/REFUSE 沒有自動畢業權限。攻擊 C13、S5F 死亡顯示與 C0B Quit 也都不能作 completion proof。

## Domain 與持久化（designed）

- QuestRuleCatalog：client_profile、resource_release、rule_id、quest_id、npc_entity_binding、required_flags、authoritative_event_kind、reward_spec（optional）、exit_map_ref/xy/revision，只有 origin_verified=true 才可啟用。
- ScriptRun：account/character/session_generation/world_instance、name/context/issued_at、close4/close2/replied；僅腳本結束狀態，不能更新 tutorial_completed。
- CompletionLedger UNIQUE(character,rule_id) + RewardGrant UNIQUE(character,grant_reason) + Outbox + Character.TutorialStatus：**單一事務**寫入。只有 Server 已核驗 authoritative_event、Rule、NPC、quest/generation、前置完成條件才開始；同事件重播不再發獎，不同 body 的同 idempotency key conflict。獎勵**未證存在就不發**。
- ExitIntent：character、generation、loading_epoch、origin/dest map、dest xy、revision、expected C35 pair；**必須原服 verified** 合法出口，並且角色已 durable completed。S15/S14(1)/C35/S04/S33/S14(2) 通用原生 Client 載圖需 serial/epoch fence；C35 本身無 epoch；同 pair 重疊無法在 wire 解開則 fail closed/reconnect。
- 失敗和重登：若完成已提交而 exit 尚未生效，回存已提交 completed、原 durable map/pos，不重賞；只有成功驗證本次 map loading 並達安全確認邊界才做 durable exit checkpoint。C6C 關閉、C39 互動、普通傳送與 Client Quit 不能取代該 transaction。

## 驗收

CT-026：未有原版完成 rule、角色不合法、無證實事件、重送時不可 completion/duplicate reward；獎勵 optional。
CT-027：未取得原版 exit map/xy/revision 不切，錯 C35、stale/overlapping epoch、斷線後不錯遷座標。
CT-028：全程原生 Client 從首次登入到教學出圖，**仍 not-run**，不可由 synthetic fixture 代替。
CT-054～056：離線 Script close、optional reward once、crash/exit checkpoint 的設計測試。

A-026 integrated/handoff partial；implementation_ready 限 codec/safe Domain skeleton；native_tutorial_complete_ready=false、native_reward_proven=false、native_exit_destination_proven=false。缺的具名資源 PaperDialog.dat、nNewJoin01.dat（只補 Script 候選驗證）；原服 NPC/Quest/Exit 綁定和事件 trace 仍必要。原始 EXE/DAT 不上傳共用 Git。

## A-004 opcode 勘誤

DieObjects 的正確 Client constructor opcode 是 **S5F (0x5F)**，ctor `0x57e1b0` 在 `0x57e1c9 push0x5f`，reader `0x57e260` u32BE ref 不變；不是舊版 S1E。S0E RemoveObjects 是獨立的物件移除封包。DieObjects 也不能視為 Quest 完成證明。詳 [A-004](../03-analysis-requests/A-004-roy1-world-visibility.md)。
