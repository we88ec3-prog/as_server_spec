# P0 原版創角登入入圖分析派工清單（2026-11-01）

本文件只分配 **Client 可觀察操作／封包／地圖原件證據**，不要求分析者替新 Server 決定帳密策略、官方出生點、資料庫 schema 或原服第一次派任務時機。A 的靜態/實際執行成果與 Server DEV／Client E2E 分離。使用者目前已提供 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat`；**不需重新上傳這五個檔案**。原件 SHA、版本和 raw sample 不上傳 Git。

## P0-A：A-030（已有 integrated/partial，需原版 UI 動態補證）
- **為何阻塞**：現有 private Server 的 C02 明確 `native-c02-fields-unknown-a030` Close。Region2..4 F3/F4 UI→packet ordinal 已知，**NAME/E-MAIL 語意尚未證明**；Region1 UI/write mismatch；失敗 S02(status!=0) 只靜態知道可顯示訊息與送 C15，不知道可靠狀態／重試 UI。帳號正確也不會發第一個 S02(0)。
- **由 roy1 / A-030 追**：在同一原版 EXE SHA 下記錄選定 region、版號、原版 NewUser 的每個可見 label→widget ID→C02 F1/F2/F3/F4/flag；比較僅改 NAME、僅改 E-MAIL、E-MAIL 留空時，Client 是否真正發包，記去敏欄位數/編碼 bytes 長度；另檢驗原版 ID 最低輸入限制與現有 Admin Account 3..32 相容。
- **S02 與回登入**：以隔離測試帳號觀察非零 S02(status,string8) 讓 Client 顯示訊息、是否送 C15、後續能否 retry、TCP 是否仍活；成功兩段 S02(0) 後原生 UI 下一步（不可假設自動 C03）。不能用一般 C03 LoginFailure(status3) 假冒創角官方錯誤。
- **輸出**：每區域帶證據的 region→source-widget→field→NAME/EMAIL 表、空信箱 gate、正/負時序、具體錯誤 UI+回覆、遮罩 packet metadata，或明確 `unknown`；原生實機/修改 Client 測試不同標。參照原 A-030；本次**不重開相同 A 任務，也不抹除已有靜態證據**。

## P0-B：A-031（新開，Client World 入圖第一封包）
- **必須定位**：S03 完成→新 TCP C10 後，原版 Client 實際送什麼，C25 的建構/serializer/UI 觸發/region 分支與完整 body；現有 `0x4A8370` 是 S03 callback，**不是 C25 writer**。確定 C25 是否必要或其他 World C2S 先發、加密 ordinal/session phase。
- **方法**：EXE BIN-first xrefs/原生 Client 本機去敏 trace 對照；從預建且有角色的測試帳號開始，避免 A-030 阻塞 World packet 研究。必須記同版 Client SHA、可重現 opcode/位址/packet body/layout/field byte-order、region branch、下游 S02/S05/S15/S14 的可觀察 UI。
- **允許部分交付**：能嚴格證明某個 region 的 World 首包即可提供 DEV region-scoped adapter；其他 region fail-closed。不要把合成 body `01` 當原生 C25。
- **交給**：DEV-ENTRY-03，CT-108。分析來源 A-002/A-022，後續 A-031 完成時標 `integrated/partial` 亦可，不要求 Server 先通過原版 CT。

**A-031 靜態結果更新（2026-11-01）**：`task_a/roy2/A-031-analysis.md` 已從原版 EXE 證實 C25 為 `CBillingInfoPacket`，其 region3 writer `0x571420` body 是 3×`string8`，兩條 transfer callback C10→C25 （`0x4A8446→0x4A84F3`、`0x52FB8C→0x52FC4B`），而非通用 World metadata/map ID；實體 C25 發送四條路徑全檢 region3。現 A-031 `integrated/ready` 僅 Client 靜態可證的 Region3 wire，**原版 TCP/World 首個 S2C/成功進圖仍 CT-108 not-run**，追加 CT-110 offline。DEV-ENTRY-03 不得要求合成 C25=01，也不能要求所有 Region 都有 C25。

## P0-C：A-032（新開，Client-selected MapData/C35 真值 + 初始可通行地圖）
- **必須證實**：選定原版 MAP 的 `map_ref`→Map0/1/2 索引/檔名／資源修訂／Client S15 解析；真實 `header_word`（來源 MAP offset+4）及完整 `0x4B2EC0` structured checksum 的 Client C35 兩個 BE u16，不能用 raw CRC 或只驗 header；寬高、初始畫面可接受的 `spawn(x,y)/facing/viewport` 和至少一段已觀察可通行座標。
- **出生點責任**：不要求解析「官方 Server 原本選哪個出生點」；Server 負責**選一個由原始資源與 Client 實際顯示驗證**的教程入口。若無法證明教程圖，先做另一張合法地圖的有限測試，但標 interim/不稱教學成功。Born (31,29) 是引導招募員的文字，不是 spawn。
- **方法**：再用已提供 Map0.dat/Map1.dat/Map2.dat 的 494/494 離線解析結果（不重要求大資產），從 native Map loader/cache/CRC xref 還原完整 checksum，配合一次真正本機 Client C35 與 GUI 地圖/碰撞觀察；輸出精確選圖 metadata/可通行證據與一致 hash。
- **交給**：DEV-ENTRY-04/05、CT-108/109。若玩家碰撞仍未知，另外回到 A-005 當前 integrated/partial 的 native C33→撞牆→S0B/回滾追查；**不得把 bit0 或 bit4 單獨等同唯一 walkability**。

## P1：只為教學互動，不阻擋首次可操作入圖
- A-023/A-012：`Born.dat` 自動 S44 啟動與 PaperDialog／C6C 完整往返；原服何時派 Born 是 Server 設計決策。
- A-011/A-024：實際女性招募員 NPC map/外觀/EntityId/點擊、S07/S0C/S64 等；A-025/026 教學戰鬥/結束/離圖，ONB-05/06 才需要。
- **可明確索取的相關資源（非本次 P0 必需）**：`PaperDialog.dat`（Born 依賴；既有 A-023 已有 hash/分析結果）、`Basic.dat` 內 `AlertFrame.ypf`（PaperDialog 顯示）、NPC/Monster/角色所需真實 DAT 的**精確檔名待 A-011/A-024 指認**，不要求使用者先上傳整包。

## 研究交付格式
每個 P0 結果須包含操作觸發、C→S、需要的 S→C、Client 下一步/UI、原始 EXE 或 MAP/Script SHA、地址/field bytes、region/seed、可重現命令／去敏截圖/trace、觀察／推論／自訂 Server 政策分級、明列 unknown。**不提交私人的帳號/密碼/EMAIL、完整封包解密 body、遊戲素材或未經許可的修改 Client**。

## 出口
A-030：合法直接創角所需 Account/NAME/E-MAIL/失敗 S02 原生語意可映射；
A-031：C10 後確定 native World entry opcode/body；
A-032：至少一張選定地圖的正確 C35 pair、合法 spawn、可操作路徑。
三者可分工同步進行，並各自追加 CT/DEV 交接；不能因 A-030 未結束而阻止 A-031/A-032 分析。
