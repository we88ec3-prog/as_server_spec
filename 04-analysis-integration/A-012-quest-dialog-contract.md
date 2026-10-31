# A-012 — Script Dialogue / Quest Server handoff

來源：[A12 原版 BIN-first 報告](../03-analysis-requests/A-012-roy1-quest-dialog.md)、A-023 [S44/C6C 原生契約](../task_a/roy2/A-023-script-entry-contract.md)；Client SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；A12 evidence `ev_a012_20261031_script_reply_choice_client_static`。

**OBSERVED Client**：S44(1,0) 指定 Script name/context/textCRC/依賴/參數，驗證後 Client 呼叫 Main；缺件 C6C(0) + S44(1,1) 重新載入。腳本 UI `client.SendReply` native producer 0x526626→0x51a9f0 組 C6C(1,string8 name,u32BE context,u16BE count,count*(key:string8,value:string8))；writer 0x575210/0x575240..0x5752B6；local pair stride0x400 與 wire variable strings 不同。Client Dispose 建 C6C(4)；未 SendReply 時 generic cleanup C6C(2)，受 runner replied flag gate；Born 只建立 PaperDialog(31,29 文字導引) 並非 QuestCompleted。紙張 Close 的 Client body 順序在 A23 已證。所有資料都是同 SHA 原件 `observed-static` 或 `observed-resource`；nNewJoin 的 STATE ACCEPT/REFUSE 是 **先前 A23 資源研究候選**，不是本輪取得官方 NPC bind 或 native GUI runtime。

**DESIGNED 安全界線**：
1. Server-run context 綁定 `(character_id,connection_generation,world_epoch,script_name,context:u32,content_revision,valid_target?)`；C6C 除 type3 外要解析合法 string8/BE fields。C6C(1) 要驗 context/key whitelist/count/大小/過期/已回覆；同 context 重送冪等、不同 payload 重播拒絕。
2. `ScriptReplyObserved` ≠ `QuestCompletionAuthorized`。NPC interact 必須另外驗 world/map/visibility/range/模板與被允許的 Script；任務進度、可得獎勵與退出由 Server-only verified QuestRule（若存在）原子判斷；未知 rule 時不宣稱有正式任務獎勵。
3. C6C(4) 是 Dispose；C6C(2) 是無回答清理；都不是完成任務或獲得金錢／物品的觸發。ScriptClose 後過期事件不影響其他世代或另一角色。Server session 問題/設計與 Client 原生可見 UI 分層。
4. 不在正式 Client 使用不明 S44 variant；特別是 type1/subtype3 會觸碰本地 Script cache。Script text CRC 是 CP950 等特定 language profile 下 XML 原文轉碼後 CRC32，不是 raw `.dat` CRC；錯誤 CRC 存在 native 潛在 unsafe 路徑，先離線檢查。
5. `QuestDefinition`, `QuestProgress`, `RewardGrantLedger`, `ReplayFence` 是 **DESIGNED domain types**，不是原始 Client/Server DB schema。Server 真正開通任務結果須附 NPC→Script→UI event→權威條件→持久結果的來源和原 Client CT。

**驗證**：`tools/a012_quest_dialog_contract.py` 20 個 Client x86 byte anchor、Born SHA+UTF16 wrapper/CRC、14 個 unittest PASS（synthetic codec/negative/reply replay/close/context）；CT-092 offline，CT-093 選項 GUI、CT-094 安全與雙連線均規劃並保持 native Client not-run。A12 `integrated / partial`，`native_quest_rule_ready=false`。PaperDialog.dat、nNewJoin01.dat 已提供並驗過內容，NPC/quest/reward/腳本引用來源的確切檔名仍未知；正式 NPC spawn/quest/reward 定義的確切檔名未知。


## 2026-11-01 A-012 最終 Client I/O 交接更新

[新增完整原件驗證](../03-analysis-requests/A-012-roy1-quest-script-closure-20261101.md) 與 [離線探針](../tools/a012_quest_resource_bridge.py)：以 Asgard.exe/Born.dat/Basic.dat 固定 SHA，15 x86 C6C/S44/SendReply/Dispose/S44 script-cache 指令簽章、4 個 Basic 內嵌資源 hash、Born XML/CP950 CRC、12 個 unittest 本地 PASS。Basic.dat 的 Script/Quest UI **只有 UI 文字與圖像**：BasicString[101/198]、SkinString[2263/2264]、AlertFrame/QuestImage；沒有官方 quest ID/完成條件/獎勵。C6C4→未回覆 C6C2 的 native sender 順序再核對，C6C1 不可授權 reward。**Client I/O 靜態 handoff=ready，original Client GUI CT-093/094 not-run，official Server quest/reward/NPC script binding unknown**；DEV 只開有原生證據的 ScriptRun/lifecycle/context codec 和安全防重子集。

## 2026-11-01 A12 補件閉環（PaperDialog／PaperDialog02／nNewJoin01 三份原件）

新 [原件＋Client I/O 契約](../03-analysis-requests/A-012-roy1-new-script-resources-20261101.md) 與 [離線重驗工具](../tools/a012_dialog_option_native_probe.py)：`PaperDialog` 單頁無 SendReply 的 OK -> native C6C(4)+未回覆 C6C(2)；`PaperDialog02` OK/CANCEL 的 `ClientReply.Add(PAPER02,START/NOT)` + SendReply，`nNewJoin01` 三頁 MerchantTalk 終頁 OK/CANCEL 的 `ClientReply.Add(STATE,ACCEPT/REFUSE)` + SendReply -> native C6C(1)；兩者 SendReply 後 native replied flag 排除 no-reply C6C2。四份 Script 原件 SHA＋CP950 CRC、9 x86 簽章、20 local unittest PASS；這些是**原件與靜態 wire 可用證據，非原版 GUI/Server reward E2E**。`nNewJoin01` 無 Main，ScriptRun.name/context 和 NPC 真綁定仍須 Server 授權/原生 trace；`PaperDialog02` 的 cancelControl=OK 和同名 PaperDialogProc 引用需隔離 GUI 驗。A12 handoff=ready 僅限 Client I/O。


## 2026-11-01 A-012 Merchant.dat 原件完成：共用 Script 執行環境補證

[新 Merchant 原件報告](../03-analysis-requests/A-012-roy1-merchant-original-bridge-20261101.md)／[原始資源 probe](../tools/a012_merchant_bridge_probe.py) 完成原件比對：Merchant.Main(args) 先在 Script VM 中 AddGlobal(ServerParam,ClientReply,MerchantTile,MerchantName 等)，參數字段 `TILE/MNAME/UGOLD/UBAL/UAGOLD/UABAL/UCOLOR/GREETING/TYPE`；nNewJoin01 沒有 Main，透過 DoesTalk/BuildMuttering/MerchantTalk hook、JoinMessage01..03 最後 STATE ACCEPT/REFUSE 使用 ClientReply，再由原版 C6C subtype1 writer 送出。**這是 resource-dependency + observed-static C6C 合約，不足以證實固定 NPC/S44 執行時機與原服QuestRule**。TYPE=DIRECT 所呼叫的 MerchantDirectTalk、QuestDialog_Create、MerchantDialog_Create 的真正提供者不在現存原件中，確切檔名未知。加測 25/25 unit tests、7 x86 anchors，原生 GUI/TCP not-run；A12 Client I/O ready, quest-policy not-ready。

## 2026-11-01 A12 原件補證：MerchantDialog / QuestDialog / QuestDialog2

已由三份真正原始 DAT 解壓、驗 SHA256/CP950 XML CRC、逐函式證實 MerchantDialog_Create 在 MerchantDialog.dat、QuestDialog_Create 在 QuestDialog.dat、QuestDialog2_Create 在 QuestDialog2.dat。此前將前兩個實作提供者標為「檔名未知」是過時的歷史限制。MerchantDialogProc 的 TYPE=BUY/SELL/REPAIR/IDENTIFY/TALK/ABORT 直接 SendReply；**TYPE=BANK 只有 Add 後進 MerchantBank，沒有在此 case 直接 SendReply**；TALK 則 SendReply 後本地呼叫 MerchantTalk。與 nNewJoin01 後續 STATE 回覆的同個 ClientReply 所含全部 pair 仍必須真正 GUI/TCP 驗；不能把 synthetic 單一 STATE 封包當作實測。QuestDialog/QuestDialog2 是外部 proc 驅動的 UI factory，自身不 SendReply；第二版以 SetPortrait(tile,color) 渲染。新 8/8 離線測試 PASS，原版 GUI/TCP not-run，Server QuestRule/Reward/NPC binding unknown。詳細見 [原件分析](../03-analysis-requests/A-012-roy1-new-dialog-resources-20261101.md)、[可重跑工具](../tools/a012_new_dialog_original_probe.py)、[CT-092～094 補充](../05-conformance/A-012-new-dialog-resource-fixtures-20261101.md)。
