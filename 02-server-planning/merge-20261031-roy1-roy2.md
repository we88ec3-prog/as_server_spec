# A-015／A-016／A-027／A-028 交付後 Server 最小可行架構（2026-10-31）

## 目標及信任邊界

R-025：**Account 只能管理員建立，玩家只能用原版 Client 登入**。玩家可透過原版 Client 建立 Character（R-026），前提是有可證且經 Server 驗證的 Account owner。A-027 追到 C02 的 NewUser UI，**未證明 C03 登入預建無角帳號能進此 UI**；沒有 owner proof 前，不能把帳號名相同或 UI 確認密碼的文字比較當成已登入。原版可能是「註冊/新使用者」流程，不能透過放鬆安全檢查硬套 R-025。

## 可實作的端到端分層（原版相容性仍需分項 CT）

```text
Admin.ProvisionAccount → Account(Provisioned)
 C03 Login → CredentialVerifier / BanCheck → AuthContext(account_id,generation)
   ├─已有角色 → S03(address,port,len,token) → new TCP C10(raw token)
   └─無角色 → native C03→Create UI 需補證 (A-027)
      → 僅已驗 owner 才建立 PendingCharacterIntent
      → C02 結構校驗 + 有權限的 S02(status0) → C04(5u8)
      → Server transaction: unique Account+Character+Appearance commit → S02(status0)
      → Client local UI branch (不是直接 S03) → 原生返登入路徑待 A-028 補證
 World C10 one-time grant → S15/S14(1) → C35(header+4, structured map checksum)
   → S04/S33/S14(2) → WorldReady（不代表 TutorialCompleted）
 S44(1,0) Script 'Born' with verified dependencies and text CRC (sending policy unknown)
   → Client Born.Main/PaperDialog → C6C4, optional C6C2 (cleanup != quest complete)
 NPC/Quest/Skills/Rewards → A-012/A-024/A-025/A-026 原服證據
```

這個狀態機是 **已證 Client wire + 明示 Server designed 邊界**；原服帳號／建角 transaction、何時首送 Born、原版地圖/出生位置都未被推定成 observed。Server 不改 Client frame 增加帳號、epoch 或額外 request_id。

## 需要強制的 Domain / Storage

- `AccountOwnerProof`：由 Server CredentialVerifier 建立，綁 AccountID、SessionGeneration、expiry。C02 的帳號名稱、region flag、第二欄與 confirm 字串相等都不具授權力。
- `PendingCharacterIntent`：account_id、generation、nonce、requested_name、expires_at、state。C04 需有有效 owner + pending + 合法外觀，再於 DB transaction/唯一索引一次 commit Character/Appearance。**C15 只取消尚未 durable commit 的 intent**；晚到或舊 generation 的 C15 不刪已保存角色。
- `AuthSession/TransferGrant`：S03 發出的 opaque grant 於新 World TCP 使用 C10 **raw body** 一次性 consume；Login socket 正常關閉不使合法 grant 立刻作廢。token 原文不記 log。
- `WorldLoad`：`connection_id,generation,loading_epoch,map_id,content_revision,expected_header_word,expected_checksum`。C35 wire **只有兩個 BE u16**，不含 map/epoch；同版本同 pair 的延遲回覆無法靠 server-internal epoch 分辨，單 TCP 只允許一個 pending loading，同 pair 歧義要 fail closed 並建立新的連線邊界。
- `ScriptRun`：`character_id,session_generation,context,script_revision,run_id`；Born 的 S44 named start 需精確匹配 Script text CRC / PaperDialog dependency。C6C(4) 和 C6C(2) 是清理，不是 QuestCompleted。
- `DurableLedger/Outbox`：角色、帳號安全、物品／獎勵一次性提交，回覆遺失時投影已保存結果；TCP write/Client UI 回應/DB durable commit 三類成功分開。

## 當前 Client/內容版本證據

- Asgard.exe 3,235,840B，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
- Map0.dat 288、Map1.dat 184、Map2.dat 22，**494/494 MAP 結構驗證可重現**，共有 330 distinct payloads；header+4 在 32 張值不同；未知 MapID→教程、spawn/heading、C35 structured checksum 正式配對、NPC/地圖碰撞語意。
- Born.dat 原始 SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`，589B zlib → 1154B；頭部是 `BE u16=1 + BE u32=UTF-16LE code-unit count 574`，不是固定位元組 `00 01 00 00` 再 u16。文案 (31,29) 只是引導到女性招募員。
- 與 EXE 的正式發行版配對身份仍待原始 release manifest 或相等原版 Client 測試；能解資料不等於有散布授權。

## Gate、CT 與下一輪交付

|分析|研究交付|目前不允許宣稱|測試|
|---|---|---|---|
|A-015|MAP 494/494 offline; 格式/尾段型別|原生教程 map/spawn/碰撞/出圖|CT-039（離線）、CT-040（原生未跑）|
|A-016|重播/斷線/崩潰可設計的 Server key 與 Client 限制|原服交易/恢復政策已還原|CT-045/046（planned）|
|A-027|C02 UI 欄位/region/確認比對與 fail-closed|未認證 C02 可以認領已預建帳號|CT-041/042（planned）|
|A-028|S02 state 0x1d/0x1e，C15 零 body 失敗轉場|C04 後立即 World／角色已 durable commit|CT-043/044（planned）|

現在先分兩條人力：**A-027+ A-003/A-020（原生身份與可達 UI）**、**A-015+A-022（真教學 map/spawn/CRC）**；A-028 的 UI 回登入、A-012/A-024 的 Born 首次發送及 NPC 綁定可各自並行。A-016 的 Domain/DB/CT 不需等原版 UI 完整，直接開始設計級自動測試。

**尚缺檔名/來源**：若要獨立驗證 Born 的完整視窗/造型與原版 Client 內容，需要 `PaperDialog.dat`、`Basic.dat`、`Human/*.dat`（如 `mb*`、`wb*`、`mh*`、`wh*`）；技能／物品的真實資料表檔名仍未知，須先 BIN-first 定位，不能憑空命名。原始 Server 的首次事件/身份授權政策需原服追蹤或服務端設定；**不可因沒有這些而停止已可進行的 Client/資源靜態分析**。

## A-017 管理操作規格與 Native Client 封包的隔離（2026-10-31）

A-017 已從 `task_a/roy1` 合併；其 `integrated / handoff_status=ready` 僅表示 **Server designed** Admin API/RBAC、審計及敏感資料遮蔽已可交 DEV，**不是**還原原服 GM/Admin opcode、也不是管理後台已部署。獨立的 `/admin/v1` 提供管理員建立帳號、停權 N 天／永久及解封；不可透過原版 Client C02 創建 Account。管理員調整角色、傳送及補發道具須 world/session version CAS、原子 ledger/outbox、權限與稽核驗證；只有 IP/URL 不等於身份驗證。測試 **CT-050** 管理員權限與冪等、副作用拒絕，**CT-051** 審計去敏和關聯追蹤；兩個 CT 均 planned，不得將合成 SQLite PASS 當原 Client/Server runtime 已驗收。參見 [管理操作機讀契約](admin-operations.json)／[A-017 分析](../03-analysis-requests/A-017-roy1-admin-audit.md)。

## A-003 創角合法集合新增 Client 靜態證據（2026-10-31）

A-003 最新 `integrated/handoff_status=partial`：C02 第一 UI 欄位的 region1..4 原生本地 narrow byte length gate >=12（region0 走不同判斷），不能把它推作原服角色名稱的全域合法長度；C04 只送 5 個 u8，沒有獨立姓名欄位。原 Client 在 VA `0x66422c` 的 **10 色 RGB palette** 已提取，可做 native-color 子集 fixture，但 Server 可接受的 sex/hair/RGB、同帳可建幾角、角色名來源及原生錯誤碼仍 unknown，不能把 Client UI gate 當伺服器授權。R-025 Account admin-only 與 A-027 preauth fail-closed 完全不變。官方新測試：**CT-052** 十色/CP950/region 欄位，**CT-053** owner/同名/唯一性/C15 重送；roy1 原 CT-047/048 與 main A-014 社交衝突，已保留社交並重編。參閱 [A-003 原始分析](../03-analysis-requests/A-003-roy1-create-legal-values.md)／[創角合約](../04-analysis-integration/A-003-character-create-contract.md)。
