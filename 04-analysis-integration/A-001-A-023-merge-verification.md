# 2026-10-31 roy1 A-001 與 roy2 A-023 合併／重核紀錄

## Git 來源

- roy1 `task_a/roy1` 新 head `0facfc2e2129597993aef730ef0c44121abca999`，相對原 main `2517e60997790891473de774440e2511b5ec5d5c` 多 A-001 提交；**fast-forward** 到 main。
- roy2 `task_a/roy2` head `ae9527003719520eaa042a6d41658b947e999889`，相對 main 分歧；將其作為明確第二 parent 的 merge commit `c544af35ceb78e2fefc2e606730235c22ce0dc10`，隨後結構化逐欄融合 `requests/packets/scenarios/evidence/vectors/traceability/work-items`，保留 roy1 的 A-001 與 CT-036。
- 不以兩份相互覆蓋的 JSON 直接取最後寫入者；只合併 A-001 或 A-023 各自擁有的欄位與原生證據，測試 IDs 保持 CT-029～032 原身份、CT-033～035 Script、CT-036 交通 codec。

## 獨立可重現檢查

- **本回合原件**：`/mnt/data/Asgard.exe` 存在，3,235,840 bytes，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；PE32 i386。
- **A-001**：objdump 指令核對 `0x53B630` seed 上界比較與跳表、`0x53BB30` key-length／複製、`0x53BE70` ordinal encoder、`0x577E80` 的 C00 欄位 writer。獨立重新實作報告所述的十種 256-byte seed mask 公式，**10 個 SHA-256 全部等於 roy1 報告**；seed0 C62 `aa000662002f171902` 向量吻合，並做 10 seed 的 XOR roundtrip。這是 static-plus-synthetic 驗證，**不是**十個 seed 都經真 Client 登入。
- **A-023**：以本地 PE section RVA→file offset 映射，抽樣比對 roy2 `verify_script_entry.py` 列出的 **18 段 EXE 原始 byte signatures，18/18 全部吻合**，包括 S44 parser `0x586410`、Main path `0x52C014/0x525090`、Dispose C6C4 `0x5268C6`、C6C2 `0x5194CE`、CP950 語系表 `0x60855C`。可支持靜態碼位置／branch；*signature 相符不取代對每條路徑的 runtime coverage*。
- **資源限制**：本次 /mnt/data 沒有 `Born.dat`／`PaperDialog.dat` 原始 bytes。Roy2 提供 `script-entry-verification.json`（宣稱 18 spans + 37 negatives + text CRC）、`entry-dependency-verification.json`（Born/PaperDialog hash）、`corpus-entry-audit.json`（316 Script 文件抽查）及可執行腳本。上述資源離線 PASS 是 **roy2 原研究交付，不是本次獨立 raw-resource replay**，且與 EXE 發行版本的配對仍 `unverified`。
- **不存在的 runtime**：未連接原服、未執行 GUI 原生 Client、未以新 Server 完成首登/入圖；CT 仍 `planned`，`native_client_validation=not-run`。

## 審核結論

A-001／A-023 均採 `integrated/handoff_status=partial`：已確認 codec/Client native Script lifecycle **可讓 DEV 依限定範圍開發**，但完整原服 seed 選擇與 onboarding Script 發送政策、NPC 實體綁定仍需分析。沒有把未知欄位補猜測值，更不以尚未實機驗收阻擋已可核查的研究交付。

細節：[A-001](../03-analysis-requests/A-001-roy1-seed-and-version.md) / [A-023](../task_a/roy2/A-023-script-entry-contract.md) / [DEV Script 狀態機](../02-server-planning/script-lifecycle-contract.md)。
