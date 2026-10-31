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

## 2026-11-01 A-023 補證：原始 nNewJoin01／PaperDialog02 回覆與 C6C 根名稱

目前 `PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat`、`Merchant.dat` 已全部取得並由 A-023 **原始 SHA + Script XML + CP950 CRC** 重驗；前述「尚缺此四檔」歷史說法不再適用。[A-023 四檔原件完整契約](../task_a/roy2/A-023-four-script-native-dependencies-20261101.md)。

`nNewJoin01` 23 函式/無 Main；最終加入頁面 OK `ClientReply.Add("STATE","ACCEPT")`／CANCEL `STATE=REFUSE`。 `Merchant.Main` 為主 Script 入口候選並初始化 `ClientReply`。**C6C(1) 的 script 名稱取當次 S44 ScriptRunner root，而非 nNewJoin01 依賴來源檔名**：報告中 `Merchant+STATE=ACCEPT` 向量是 conditional synthetic fixture，不宣稱原服真 root 已知。`PaperDialog02` 由 OK／CANCEL 送 `PAPER02=START/NOT`，兩者送 C6C1 後 Dispose→C6C4；原 `cancelControl=OK`，ESC 效果待 native GUI。 `PaperDialog` 是未回覆關閉，原生 C6C4→C6C2。不能將上述任一回覆當成 quest completion/reward。

四檔 **沒有** `QuestDialog_Create`、`MerchantDialog_Create`、`MerchantDirectTalk` 函式定義，缺真正 helper 來源與招募員 NPC binding；原版 Client CT-093/094/CT-034/035 未通過。研究 Client I/O 子集可交 DEV，原服 quest authority、原始 NPC/World 綁定維持 unknown。
