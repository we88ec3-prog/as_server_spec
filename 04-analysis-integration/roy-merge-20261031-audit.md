# task_a/roy1 + task_a/roy2 Git 合併驗證與證據裁定

2026-10-31。來源 `task_a/roy1@258f5ba2dd845314a43ddb428aafad26a0533ca0`、`task_a/roy2@9e3b0ce1f5121909ea2760e8a2ceadb47abeb90b`；merge commit `078b0d1d8aab9f443ba630f43b7e5c904dd5f3fb` 具有兩個來源分支和 main 三個 parent，保留各自歷史/原文，不另建 branch。

- **A integrated/handoff**：Roy1 A-007/019/020/025/026；Roy2 A-004/005/006/008/009/024；均只限已證靜態/合成子集，Native E2E not-run。原有 A-027/028/022 的 partial、原 Client 不修改、預建帳號匹配、共享公用地圖 ADR-007 均保持。
- **封包**：合併成 72 PKT。最重要的 native NPC S07 type1..14 的真 wire bytes（**0x228 本地 stride 非 wire**）、S0C/S64、S5F、S0E、S34/S3C、S62/S63、S29、C43，以及攻擊 C13、戰鬥 C3D/S3D；沒有把各 kind 強制指定為怪或招募員。
- **衝突裁決**：Roy1 `PKT-S1E` 使用 0x57E030 push0x1E 但援引 0x57E260 作 DieObjects parser；Roy2 `PKT-S5F` 以 0x57E1B0 push0x5F 指向 **同一 parser**。本版將 S1E 標 `disputed-cross-analysis-reader-attribution`，不准以它發 Native Monster Death，交 A-009/025 精查 ctor/vtable/handler；S5F 的 reader 仍有靜態依據，Client GUI 未驗。
- **CT 與規劃**：main 保留 CT-054/055；Roy1 CT49..62 → CT56..69、Roy2 CT55..66 → CT70..81，總 CT=81。資料與原始報告都保留，見 [對照表](../05-conformance/ct-id-remap-roy1-roy2.md)。Client I/O 由6擴至12 flows，未測 original client。
- **Server**：DEV-070-M 以 SharedMapKey 及每玩家 Observer/Session，S07/S0C/S64/S5F/S0E 引入 Native Adapter 但只在 object kind/renderer 完成後發送；DEV-080 把 C13/S13/S5F 與 S08/技能串成 Domain；DEV-090 不把 Born/ScriptClose 當 quest complete，C39/S2F 只是 Merchant candidate，獎勵/exit 保持 unknown。

需後續原生研究清單見 [A-XX 交接](../03-analysis-requests/post-merge-analysis-queue.md)。整合報告沒有聲稱任何新的 native Client CT Pass 或私有 Server 代碼已更改。
