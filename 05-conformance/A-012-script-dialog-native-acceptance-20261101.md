# A-012／CT-092～094 原版 Script／Dialogue 驗收清單（2026-11-01）

**A12 的 Client I/O 原生靜態契約已 ready；本文件的 GUI/TCP 原版實機驗收仍 planned/not-run。** 研究主報告：[A12 完整交接](../03-analysis-requests/A-012-roy1-quest-script-closure-20261101.md)；可重現工具：[原件 Basic/Born/EXE 檢查](../tools/a012_quest_resource_bridge.py)。

| 測試 | 已通過的離線部分 | 尚需完成的原生 Client 實驗 |
|---|---|---|
|CT-092|Asgard.exe/Born.dat/Basic.dat 固定 SHA；15 native sender/dispatcher instruction signatures、四個 Basic 嵌入資源 SHA、Born 原文 CP950 CRC；12/12 new unittest PASS。沿用 A12 原先已驗的 C6C serializer/S44 入口|原始 Client GUI、Socket E2E 不以離線 PASS 視為通過|
|CT-093|Server 合法 S44(1,0) Born+PaperDialog，CRC 必須與發行版吻合；已知缺檔 C6C(0)，Dispose C6C(4)/(2)，有回覆 C6C(1) 等 wire|在隔離、可丟棄的原版 Client 確認 PaperDialog 實際出現；點單頁 OK 看是否依序送 C6C(4) 與 C6C(2)，檢查附帶的 script context/ordinal。候選 nNewJoin01 的接受/拒絕 UI 需另核 NPC 真綁定。對照一組「已 SendReply」不送 cleanup2。**勿用假 CRC 嘗試強迫原 Client 修復**|
|CT-094|C6C(1) pair/name/context 與 server-designed connection-generation/replay fences 已有 synthetic 模型；C6C(4/2) 不授權 QuestCompleted/RewardGrant|原 Client 二連線同圖、NPC/entity 正式綁定、重複 ACCEPT、先 Dispose 後重送、斷線/重登入、舊 context、腳本版本/資源欠缺、任務有無獎勵及官方判定條件的真正 E2E；Server domain 只在 verified rule 下核准|

## 安全保護

原生 S44(1,3) 會觸及本地 Script cache 清理；只可在備份且可丟棄的 Sandbox 試。原生 CRC 不合可能有 dangling-pointer 風險，優先用離線工具校驗與對版內容。所有真實測試只記時間戳、opcode、去敏 script name/context/field length（context 如需保留須遮罩或測試合成）、session generation、原 Client GUI、Socket close 來源；不提交原 DAT/EXE、玩家帳密、商業資產或未授權腳本全文。

## 本次精確缺件

- `PaperDialog.dat`：Born.Main 呼叫的 PaperDialog_Create 原件，A23 曾解析/驗 hash，但**本次容器未提供，未重驗**。
- `nNewJoin01.dat`：原本 A23 核對的學校加入對話候選，**並非已證女性招募員 Script 綁定**，本次未重驗。
- 原服 NPC/entity→Script 與 QuestRule/Reward 的正式定義/綁定檔名目前**未知**；需原服 trace、內容索引或可證來源，不能任意要求不存在的「Quest.dat」。原版 Client Windows GUI/Server 診斷 trace 亦未取得。

**責任切分：** A12 原 Client I/O 靜態 scope `ready`；A24 追 NPC id→Script、A26 追是否真有任務 completion/reward、DEV 規劃真正 Server identity/progress/ledger；CT-093/094 做原版 Native runtime。任務完成不等同對話視窗關閉。