# S44／C6C 原生 Script 生命週期：Server 開發契約（2026-10-31）

Client identity：Asgard.exe PE32 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。來源：[A-023 原生契約](../task_a/roy2/A-023-script-entry-contract.md)、[A-023 Script 靜態核對](../04-analysis-integration/A-001-A-023-merge-verification.md)。**此頁是 Server designed 規範；原服首次教學下發政策尚未證實。**

## 已確認 Client 行為（observed-static）

- **S44(1,0) start**：`u8 type=1, u8 subtype=0, string8 name, u32_be context, u32_be main_text_crc32, u8 dep_count, [string8 name,u32_be text_crc32]*, u16_be param_count, [string8 key,string8 value]*`。Client 有資源則啟動 ScriptRunner 的 `Main`；缺檔時使用 C6C(0,name) 要求下載、排隊，S44(1,1) 取得資料後重試。**不是**任意 S44 subtype 都可用於 start。
- **S44(1,1)**：`name:string8, compressed_length:u16_be, zlib bytes`。本地程式反組譯顯示有限輸出緩衝；Server 必須限制壓縮、展開長度和驗證 revision。**S44(1,3) 涉及 Script/*.dat 快取刪除；正式 Server 預設不得送**，測試需隔離備份。未知 subtype fail closed。
- **C6C Dispose**：對 Born + PaperDialog 正常 OK 路徑（未 SendReply），native API 先生成 `C6C(4,name,context)`，再由清理路徑生成 `C6C(2,name,context)`；兩個 send 呼叫的實際 TCP flush/合包時機尚未運行驗證。其他有 SendReply 的腳本會形成 `C6C(1,key/value)`，清理時若 replied=1 則不再形成 C6C2。
- 字串使用 `string8`（u8 encoded byte length，不是 Unicode 字數），u16/u32 wire 大端；CP950 CRC/vector **只有 LanguageMan index4 的 profile 條件下有效**。Script CRC 是解壓 XML 原文字串轉編碼後的 reflected CRC32，**不是 .dat raw SHA 或 zlib bytes CRC**。
- Born.Main 借用 PaperDialog 的 UI 函式，提示往 **(31,29) 找女性招募員**；此位置是導引文字，並非已確認出生點、NPC ID、map ID 或任務完成。

## Server 建議狀態機（designed）

```text
AuthorizedCharacter + WorldReady
  → ScriptStartEligible (must have proven tutorial policy)
  → ScriptRunIssued(run_id, session_generation, character_id, script_revision, context, resource_crc)
  → S44(1,0) named start
      ├─ C6C(0,name) missing dependency → authorized bounded S44(1,1) resource transfer → resume pending run
      ├─ resource mismatch/invalid CRC/timeout → Quarantine+Diagnostic (do not auto-retry unsafe mismatch)
      └─ Client Main executed → ScriptRunOpen
           ├─ C6C(4) then optional C6C(2) → ScriptClosed (lifecycle only)
           └─ C6C(1) SendReply → application reply; later C6C(4) → ScriptClosed
  → Persist script lifecycle checkpoint (idempotent)
  ≠ tutorial_completed / quest_reward_committed
```

**WorldReady 作為 Script 啟動前置是保守的 Server 設計，不是原服已證實的 S14(2) 相對時序。** 發送 Born 的首次判斷/時序尚需 A-012/A-015/A-024 的原生政策或 trace；尚未取得時只能做受控內部 mock，不可標成原版流程已可上線。

## 安全／資料模型

- `ScriptCatalog`：`client_profile, codepage, name, dat_sha256, unpacked_text_crc32, dependency_name/hash, resource_release_id, verified`；`Born` 和 `PaperDialog` 的 roy2 報告 hash 可作候選，**不可由同資料夾推定與 EXE 同發行版**。
- `ScriptRun`：`run_id, account_id, character_id, session_generation, map_epoch, script_name, context, resource_revision, state, issued_at, replied`，每次合法 trigger 只產生一次邏輯 run。
- 收到 C6C(0/1/2/4) 時驗證已授權 session／Character／run/context 和合法 subtype；重送、C6C4+C6C2、舊 session/epoch 均不得重複更改任務與初始資產。
- `ScriptClosed` != `QuestCompleted`：是否解鎖任務／獎勵只能由後續 A-012/A-026 已證的伺服器權威條件觸發。未知 NPC binding 不能用 `nNewJoin01` 名稱猜測填入。
- 不向正式 Client 測試錯誤 Script CRC 的復原分支；原 BIN 在 CRC mismatch 路徑可能釋放後返回原指標（靜態風險，未經 runtime 確證），測試先做不危險的 offline serializer validation。

## 開發與驗收對應

- **可立即做（DEV）**：按已知 body schema 的 S44(1,0)/(1,1) codec、C6C(0/1/2/4) parser、資源 hash/CRC registry、context/run 幂等 ledger、隔離的 synthetic fixtures、錯誤／長度拒絕。
- **不可宣稱已完成**：原服首次送 Born 時間、首 NPC entity/map/spawn、真實 quest flags、原版 UI/Client 成功與原服回覆。必要證據交 A-012、A-015、A-024。
- **CT**：CT-033 協定+Script 檔案風險隔離；CT-034 首次發送/GUI/NPC；CT-035 C6C4/2、失敗/重送；CT-018 原生教學出生。Native E2E 均未執行。

### 例示合成 start（不是原服封包）

`010004426f726e112233441d87b0c0010b50617065724469616c6f67f870c5740000`：Born + PaperDialog、context `0x11223344`（designed），CP950 text CRC 為 roy2 資源報告推得；**不包括** opcode、ordinal、加密與 frame。後續是否能於真 Client 顯示需 CT 隔離實測。
