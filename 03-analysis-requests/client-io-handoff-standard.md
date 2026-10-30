# A-XX 正式研究範圍：Client 操作 → 封包 → Client 反應

2026-10-31 校正。分析對象是 `Asgard.exe` 和原始 Client 資源；**不要求分析者推導原版 Server 的帳號權限、資料庫寫入、出生點選擇、任務派送策略或 NPC AI。** A-XX 的靜態研究、Server DEV 決策、原生 Client CT 驗收是三種不同交付。

## 全部 A-XX 應交的 Client I/O 表格

每一條玩家操作或收到封包所引發的事件，必列：
1. **Trigger**：哪個 UI、按鈕、場景、輸入、handler 或收包引發？Client state、EXE VA/RVA？
2. **C→S**：送哪個 opcode、type/subtype，body 每欄 offset/型別/endianness/string8 codepage、資料從哪個 UI 取得；無發包則明示。
3. **S→C**：Client 需要哪個 opcode、必要的 body 與順序才會進下一狀態？成功/錯誤與取消分支？
4. **Client effect**：渲染哪個畫面/人物/地圖，state 改成什麼，會不會再發 C→S；逾時/重試/斷線如何？
5. **Evidence/unknown**：原始 opcode handler、parser/writer、原件 SHA、資源檔名、重現步驟及 observed-static/resource/runtime/inferred/unknown；未查到的分支要列清，不准補猜。
6. **DEV/CT handoff**：可直接開發的已知 Wire/UI 子集與測試；尚未有原生 Server 的實機驗收不得使已證 Client 子集研究失敗。

## 現有部分已證 Client 互動

|操作或收到的事件|Client 發出|Client 接收／反應|證據界限|
|---|---|---|---|
|玩家提交登入 UI|C03：string8 帳號、string8 密碼、u8 flag|S02 status+message 錯誤；S03 addr/port/token 時重建 TCP，再送 C10 raw token|A-002；原服帳號驗證政策不是 Client 研究|
|玩家在 NewUser UI 提交欄位|C02：region2–4 為 4×string8+u8，其他 3×string8|在 state0x1d 收 S02(status0)，Client 自動送 C04，轉 state0x1e|A-021/027；**NewUser 不能擅自等同 C03 無角色後自動進入的角色創建畫面**|
|C02 成功回覆後 UI 送出外觀|C04：兩個 u8 選項 + RGB 三個 u8；沒有獨立角色姓名欄|在 state0x1e 收 S02(status0) 走本地 UI 成功分支；非零回覆可能送 C15 空 body、進 state0x1f|A-003/028；無法從 Client 得知原服 DB commit|
|Client 收到地圖載入控制包|依 S15/S14 載入本地 MAP，再送 C35 的兩個 BE u16|接 S04／S33／S14(2) 等更新位置並顯示 World|A-022；**哪張圖、哪個出生點是 Server 要選擇，A 只查 Client 接受／顯示條件**|
|收到 S44(1,0) Script start|資源缺少時 C6C(0)；Born/PaperDialog 關閉會 C6C(4)，無 SendReply 時可能隨後 C6C(2)|S44(1,1) 更新資源後重試，資源足夠則執行 Main|A-023；「首次發 Born 的時機與任務旗標」是 Server 政策，不是 A 必答|
|操作 NPC、技能與任務 UI|A-024/025 繼續追操作對應的 C→S|追生成／動作／任務顯示所需 S→C|伺服器 AI/掉落/任務計數不能取代封包研究|

## A-XX 與 Server 工作的明確切割

- **A-027**：查使用者如何開 NewUser、欄位從哪個 UI 取得、提交 C02 前本地條件，以及 C03 收成功/失敗後如何進到什麼 UI；**不要求證明原服如何辨識管理員預建帳號**。
- **A-028/A-003**：查 C04/S02/C15 的收包→UI/再送包、畫面輸入值、合法 Client 選項；不以原服重名資料表或 durable commit 為 A 完成門檻。
- **A-022/A-015**：查 S15/S14/C35/S04、MAP 文件格式/CRC、Client 座標／渲染及無效地圖反應；**不要求從 Client 推出原服固定的「新角色出生座標」**。Server 可自訂合法 map/spawn，必須選 Client 確實能載入的版本。
- **A-012/A-023**：查 S44/C6C、腳本解析、所需資源及 UI 關閉回包；**不要求找原服首次派送 Born 的營運政策**。
- **A-024～026**：NPC spawn/AI、技能傷害、任務是否完成、獎勵選擇等權威邏輯屬 Server；A 必查 Client 收哪些 S→C 才能顯示、做哪些動作會送 C→S。
- **安全**：R-025 保留 Admin 建 Account。Server 必須驗證既有帳號和 C02 的合法 owner；不能單憑 C02 字串開權限。這是 **DEV 的驗證責任**，A 必須提供其可觀察的輸入／狀態，但**不以原服 owner 演算法為完成條件**。

## 資源及測試界限

本回合可直接核對的使用者原件：`Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat`。Born.dat raw 589 bytes SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`；本輪已獨立 zlib 解壓 1154 bytes UTF-16LE XML，包含 Main／PaperDialog 和 (31,29) 導引文字。若需要 PaperDialog 函式定義，具名缺件是 `PaperDialog.dat`；不要重複要求已提供的 Map0/1/2/Born。仍須辨別 Client 原件與資源的官方版本配對。

A-XX 交付已證子集可 `integrated/partial` 或限定 ready，**native_client_validation=not-run 是另一個 CT 的狀態**。未知原服內容可標 server-policy-unknown，不應導致整個 Client I/O 分析 blocked。
