# task_a/roy2 ← main 同步與 A-015 CT 編號衝突處理（2026-10-31）

- Source main: `8e4f42ddd1338890386c4f6bf4ebcdbfe3916c99`。
- Target original task_a/roy2: `3302651ba7fbc20089ff25a8fd69f341bed159ba`。
- Merge commit must have BOTH as parents. No new branch. No changes to `main`.
- Main's `CT-069` is map audio epoch/fallback; `CT-070` is two-client AOI/ID lifecycle. **Retain** these IDs, untouched.
- A-015's branch-local `CT-069` (native MAP offline) is reallocated to **CT-087**. A-015's `CT-070` (native player collision validation) is reallocated to **CT-088**. Both are documented in `05-conformance/vectors.json`, A-015 requests/flow and standalone A-015 reports.
- Main's more recent A-004/A-005/A-006/A-007/A-008/A-009/A-011/A-019/A-020/A-024/A-025/A-026 integrations, CT remaps, Server plan and additional resources are preserved. A-015 unique files and its MAP/flow evidence are retained.
- This is a Git tree-level semantic three-way merge: main tree baseline, preserve Roy2-only files, reconcile six shared files by per-ID additive merge. Check final branch ancestor status, cross-document CT IDs, CI and phase gates.

## main 最終同步時的 CT 編號更正

Roy2 當時暫定 A-015 CT-087/088；Roy1 最新 A-013 同時建立交易 CT-087/088/089。**main 最終採交易 CT-087/088/089、Roy2 A-015 MAP 改為 CT-090（離線）／CT-091（原生移動）**。以上原生 Client E2E 仍 not-run；其他文件以整合後 main 的編號優先。
