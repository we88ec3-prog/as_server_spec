# 2026-10-31 新原件驗收增量（A-011/A-023/A-026 → DEV-070-M/090）

**資產離線解析已執行**：5/5 新來源原始位元組可讀；3 個新 Script 均通過 zlib、BE 2+4 wrapper、UTF-16/函式檢查；Monster00/World00 均通過 6 slot、第一 offset=220、offset 單調、sentinel=EOF，各 5 個 YPF 索引。數值與 SHA 見 [資源報告](../04-analysis-integration/new-asset-samples-20261031.md)。**不表示原版 Client 畫面或 Server 實機驗收已通過。**

|驗收切片|方法／預期|目前狀態|
|---|---|---|
|OFF-01 Script text|對原始 zlib blob 驗 `BE u16=1, BE u32 units, len=6+2×units`，CP950 文字 CRC：nNewJoin01=d9390353、PaperDialog=f870c574、PaperDialog02=42683546；truncated/wrong version 拒絕|**offline checked**（原件）|
|OFF-02 Dialog decision|解析 nNewJoin01 三頁及 `STATE=ACCEPT/REFUSE`，PaperDialog02 `PAPER02=START/NOT`，PaperDialog 普通 OK 無明示 SendReply；同名 callback 衝突須標示|**offline checked**（原件）|
|OFF-03 indexed archives|Monster00 4431969、World00 44573870；各 6 slots 含 sentinel/5 個 payload；首 offset220、最後 EOF；CP949 名稱僅供檢索|**offline checked**（原件）|
|DEV-090-01 intent|合法 ScriptRun/context，接受/拒絕存私有 intent；重送、重連、跨帳號、跨地圖、不同值拒絕或冪等；不修改 TutorialCompleted、ExitCheckpoint/獎勵|**planned synthetic**|
|DEV-090-02 script lifecycle|S44 main/依賴版本匹配、C6C(1)/C6C(4)/C6C(2) 按原生靜態規則；02 需自己的上下文與 callbacks，不與 PaperDialog 共用錯誤 callback|**planned synthetic**|
|DEV-070-M-01 visual|原版 S07 kind1/2/4 → MonsterObject → image slot → 實際 YPF member/motion；NPC 與怪不同；多人同一 NPC/Monster|**native not-run / A-011/024 partial**|
|CT-055 / CT-080/081|雙原版 Client 進共享地圖、怪物出現/消失/互見，資產版本一致，驗畫面與收包|**not-run**|
|CT-061～063、CT-026～028|原版 NPC 點擊→三頁選擇（ACCEPT/REFUSE）→真正入學/完成/出圖，實證回包與地圖|**not-run**|

**原版 Client 測試的 Gate**：仍需 NPC entity→Script 綁定、合法地圖/出生/CRC、Client 發出 C6C1 真值與 UI、與原服或可證設定支持的入學轉場；這次僅提供資產／腳本證據。不要用合成 Server 成功模擬冒充 Client 原生驗收。此表是既有 CT 工作的新增用例，不新增正式 CT ID 以避免與並行分析重號。
