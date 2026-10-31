# A-026／roy3 — 教學完成、獎勵及退圖：原生 Client 靜態交付與仍未解決的原服條件
日期 2026-11-01；工作分支 task_a/roy3；延續 03-analysis-requests/A-026-roy1-tutorial-completion.md（保留原紀錄）。原始 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。

**交付範圍：Client I/O 和已證資源的靜態研究 ready；原版 Server 如何決定完成／發獎／正常出口仍 UNKNOWN，native Client GUI not-run。這不等於完整教學系統已可遊玩。**

## 1. 原始檔取證與過時缺件更正（A026-E01/E02）

- Born.dat SHA256 992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98，zlib 解壓得到 wrapper version1、UTF-16LE 574 code units。XML 只有 Main，經 client.CreateArray/page.Insert/PaperDialog_Create 顯示往 (31,29) 點選女性招募員的指示；**不是 spawn、完成、獎勵或出口座標**。這個 Main 無明示 SendReply 或發獎指令，不代表別的 Script/原服不存在。
- 新直接驗證 Basic.dat SHA256 0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96；DAT 有 39 個 slot（含 EOF sentinel），38 個真正成員。AlertButton.ypf offset 1408 / 11788 bytes；AlertFrame.ypf offset 13196 / 177648 bytes；QuestImage.ypf offset 3883501 / 1555 bytes。這確認 UI 素材可取，不證明 NPC 來源或任務完成。
- main 的 04-analysis-integration/new-asset-samples-20261031.md 已直接驗證先前補交的 nNewJoin01.dat、PaperDialog.dat、PaperDialog02.dat。這次沒有三檔原始 bytes 在本機，**沿用已審核的資源證據，不假稱重新讀取檔案**。舊 A026 報告說 PaperDialog / nNewJoin01 尚未提供是當時情況，現已過時。
- nNewJoin01 有 MerchantTalk，三頁 JoinMessage01/02/03；最後 OK 發 ScriptReply STATE=ACCEPT，CANCEL 發 STATE=REFUSE；沒有獨立 Main。PaperDialog OK 只 Dispose，PaperDialog02 另有 PAPER02=START/NOT，**不能**把 PAPER02 或 STATE 自動視為 durable quest completion。共享 QuestDialog_Create 定義的確切來源仍未知。
- C6C(4/2) 原 Client Script close、C6C(1) reply 依 A023 Native 靜態結果；SendReply/Close 的有效 context 必須由已授權 ScriptRun 核對，重送不應生權威獎勵。

## 2. C39 原生 writer 真正 wire 與內部分支（A026-E03/E04）

原始 Asgard.exe constructor VA 0x5737C9 push 0x39，serializer VA 0x573860：
- 第一個送出的 u8 是本地 object+0x19，原生 0x573868→0x45AB00。
- 後接 object+0x1C BEu32（0x573873→0x45AC40）、object+0x20 BEu16（0x57387F→0x45AB40）。
- object+0x18 是 **只有 Client 自身用來選跳表的 selector**，範圍 1..9，跳表位於 0x5738F8。它不在上述固定 wire 頭內；Server 不可以把 Client 的內部 subtype 當成 wire 第一個 byte。
- selector 1,2,4,6,7 皆跳 0x573896，在上述固定 7B 後接一個 string8（來源 object+0x22）。
- selector 3 跳 0x5738AE，接二個 string8（來源 +0x22 與 +0x222）。
- selector 5 / 8 / 9 跳 0x5738CB / 0x5738DA / 0x5738E9，分別接一個 u8（來源 +0x22）。
- 第一種形狀不只一個 selector 共用；wire 沒有獨立 selector 欄位足以區分 1、2、4、6、7。C39 中 BEu32 欄位是不是該招募員的 object_id 仍須與 A024 原生點擊及 NPC Script binding 比對，不能直接宣稱已證。合成 body selector1、first u8=4、u32=0x11223344、u16=0x5566、string ABC 為 04 11223344 5566 03 414243；這是 offline fixture，非真抓包。

## 3. S2F 原生收到的分支（A026-E05）

原始 packet constructor 0x581BA9 push 0x2F；reader 0x581CA0 先讀 u8 subtype 至 object+0x18，再依序讀 u8、BEu32、u8、BEu16、u8 及額外 4B/text buffer；0x581D1B 由十格跳表 (0x582084) 按 subtype 0..9 解析。

|S2F local receive subtype|入口|增量 Native reader shape，業務用途尚未知|
|---|---|---|
|0|0x581D22|u8 count，循環 string buffer 與 BEu16，記憶體 stride 0x202|
|1|0x581DB2|string，再 u8 count，循環 string + BEu16，stride 0x202|
|2/5/8/9|0x58206F|BEu16|
|3|0x581E52|string + BEu16|
|4|0x581E79|BEu16、string、BEu16 count，循環 BEu16/BEu32/兩個 string buffer，stride 0x408|
|6/7|0x581F4E/0x581FE0|BEu16、BEu16 count，循環 BEu32/string buffer，stride 0x204|

以上都是 **Client 解析器形狀**，尚無原服資料把任何 subtype 證實為「教學畢業」或「獎勵」。S2F 的 UI handler、完整 field 業務語意和該 NPC 對話的唯一關聯未經實機。

## 4. A-026 完成條件／獎勵／出圖的證據界線（A026-E06）

|原生可見事件|可採用的證據|Server 權威完成事件？|
|---|---|---|
|S44/Born 主腳本|Born 原文與 A023|否，僅教學提示|
|C6C(4/2) 關閉 PaperDialog|Script runner Native Close|否，僅 ScriptClosed|
|NPC 互動與 C39/S2F|本輪 serializer/parser 與 A024|否，NPC/entity/quest 綁定仍未知|
|STATE=ACCEPT/REFUSE|nNewJoin01 Script 原始資源在 main 已驗|否，只是入學意圖，拒絕不等於永久拒絕|
|PAPER02=START/NOT|PaperDialog02 已驗|否，與 STATE 不同 key|
|S5F 死亡顯示、C0B 退出|A004/A025、A026 Roy1|否，非 quest 完成|
|S15/S14/C35/S04|A022/A032 與 A016|否，僅通用原生載圖、CRC、位置流程|
|正式任務完成、獎勵內容、目的 map_ref/xy/revision|**未取得原 Server handler/config 或完整 trace**|UNKNOWN，不能假稱已還原|

Server designed (非原服觀測)：只有綁定 verified quest_rule/NPC/authoritative event 且角色、Script context、world_generation 與 session 均吻合才提交 CompletionLedger once；reward 若有原版證據才寫 RewardGrant once。出圖必須具已核實 destination map/xy/revision/expected C35 pair、single pending loading epoch 和 durable checkpoint，無資料 fail closed；斷線後不重賞，不把 C35/S14(2) 當完成 ACK。沒有原版 reward 依據則「獎勵存在與否」=null，不能填 0 或假商品。

## 5. 可重跑測試、完成度與下一步（A026-E07）

本輪直接使用 SHA 相同的 Asgard.exe / Born.dat / Basic.dat：14 個 Native E8 call 目的位址、17 個 Native 指令位置、C39 9 格分支表、S2F 10 格分支表全部 PASS；Born zlib/XML、Basic 嚴格 DAT 索引 PASS。新增 10 個 unittest PASS（其中合成 C39/S2F 分支與原件驗證分開標記）。

    python task_a/roy3/a026_roy3_native_probe.py --exe Asgard.exe --born Born.dat --basic Basic.dat
    python -m unittest discover -s task_a/roy3 -p test_a026_roy3_native_probe.py -v

CT-028 原版 GUI 必須保留 not-run：新角色第一次入 World → S44 Born → 真招募員點擊/C39/S2F/C6C → STATE=REFUSE、ACCEPT 分支 → 真正 quest completion 的 authoritative trace → 若有獎勵，錄 item/exp/gold → 真正 S15 exit map_ref、S04 xy、C35 → 重登/斷線 recover。測試前不得宣稱官方的 exit map、位置、reward 已知。

**研究交接狀態：integrated；handoff_status=ready（Client 原生靜態 I/O 與 unknown 範圍）；native_client_validation=not-run；native_tutorial_complete_ready=false；native_reward_proven=false；native_exit_destination_proven=false。** 這是 A026 Client 研究交付完成，**不是**原服教學流程已復刻。

**所缺資源：** 本輪離線不缺新檔；如要求同回合重新獨立分析已在主線驗證的入學 Script 原件，具名檔案為 nNewJoin01.dat、PaperDialog.dat、PaperDialog02.dat。若要真相需原版 Server 的 Quest/NPC/Exit handler/config 或原服從新角色→畢業→退圖→重登去敏封包與狀態 trace；尚無證據指向單一官方規則檔名，不可杜撰。
