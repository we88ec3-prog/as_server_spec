# A12 新三資源 CT-092～094 補充（2026-11-01）

[三檔原件分析](../03-analysis-requests/A-012-roy1-new-dialog-resources-20261101.md) 與 [離線 probe](../tools/a012_new_dialog_original_probe.py)。

|CT|目前已證|仍待原版 Client/Server|
|---|---|---|
|CT-092|原 MerchantDialog、QuestDialog、QuestDialog2 三檔 SHA、zlib/UTF16LE/CP950 CRC、函式 callback、8/8 offline tests PASS|真正的 Script dependency load / Windows GUI/TCP|
|CT-093|BUY/SELL/REPAIR/IDENTIFY/TALK/ABORT 在 MerchantDialogProc 直接 SendReply；BANK 分支 **不直接 SendReply**；QuestDialog/Create 的 proc 由 caller 提供|TALK 與 nNewJoin STATE 的完整 C6C pair_count/pairs 和時序、BANK→MerchantBank 下游、SetPortrait(tile,color)、按鍵和 EDIT 空字串行為|
|CT-094|Server 可按原有 C6C/ScriptRun 契約驗 reply intent；沒有確認任何 quest/經濟實際變動|雙玩家共享地圖、跨世代/錯 NPC/重送、Quest/Shop authority 和獎勵與貨幣冪等|

**不應為求驗收用錯誤 CRC 或 S44(1,3) 直接刺激正式原 Client。** QuestDialog_Create、MerchantDialog_Create 的 Script provider 現已找到；MerchantBank/MerchantDirectTalk 實作來源檔名仍未知。
