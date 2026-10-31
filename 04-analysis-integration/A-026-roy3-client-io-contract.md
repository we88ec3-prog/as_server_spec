# A-026 roy3 原生 Client I/O 交接契約

來源：task_a/roy3/A-026-roy3-native-tutorial-completion.md，Evidence A026-E01..E07；基準 03-analysis-requests/A-026-roy1-tutorial-completion.md。

- Trigger：S44 Born Main 顯示 PaperDialog；招募員點擊/Script 來源待驗。nNewJoin01 MerchantTalk 第三頁選 STATE=ACCEPT/REFUSE。
- Client sends：C6C subtype1 ScriptReply；subtype4/2 ScriptClose；C39 固定 body = object+19 u8, object+1C u32BE, object+20 u16BE，再有 selector 1/2/4/6/7 的 string8、3 的二個 string8、5/8/9 的 u8。selector 本身存在 Client object+18，**沒有做為固定 wire byte 發送**。
- Client receives：S2F opcode 0x2F，subtype 0..9 多變體 parser；0/1 有字串+u16 列表，2/5/8/9 為追加 u16，3 為字串+u16，4/6/7 是字串/數值複合陣列。S15/S14(1)/C35/S04 仍僅 map load；S44 Script runner 不能當畢業。
- Client reaction：Born OK 僅 PaperDialog Close；nNewJoin01 是入學意圖，PAPER02=START/NOT 是不同資源和 key；S2F UI/獎勵顯示不具官方 quest binding。
- Evidence：原始 Client SHA db3df616...729e1145 的 14 Native E8 call/17 exact anchors、C39 9 / S2F 10 跳表；Born SHA 992e...f98 引導；Basic SHA 0da3...b96 38 個原始 UI 成員；main/new-asset-samples-20261031.md 先前驗證三個 Script 的精確 reply。
- Unknown：官方完成任務 rule、NPC/quest/scene mapping、必要戰鬥條件、獎勵存在及內容、出口 map_ref/xy/revision、原 Server 的斷線回復語意、原版 GUI 全程行為。

## Server designed / CT separation
不得在 C39、C6C Close、STATE=ACCEPT、PAPER02=START、S5F、C0B、C35 上直接 commit quest completed、reward 或 exit。需 verified authoritative event、current account/character/generation、script context+NPC binding、原子完成 ledger 與可選一次性 reward/outbox。沒有 confirmed destination map+coords+C35 保持 ExitPending 或 refuse；C35 無 epoch，限制重疊 load，重連以 durable checkpoint 恢復。

A026=integrated；handoff=ready 僅限上述靜態 Client I/O，native-client E2E=not-run；native_tutorial_complete_ready=false、reward_proven=false、exit_destination_proven=false。CT-028 測試見 05-conformance/A-026-roy3-native-acceptance.md。
