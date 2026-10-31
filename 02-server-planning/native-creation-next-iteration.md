# Server 下一階段規劃：登入帳號一致性與原版創角 UI 安全橋接

日期：2026-10-31。限制：**不修改 Asgard.exe**；帳號欄維持原始可輸入狀態，輸入帳號與已驗證登入帳號不同就拒絕創角。此為新 Server designed 政策，不是已證的原服政策。

## 目前能立刻繼續的工作

|工作切片|Server 交付|阻擋原生相容性的 A 證據|
|---|---|---|
|SAFE-01|C03 成功身份產生可信 AuthContext(account_id,account_name,connection_id,generation,expiry)；過期、停權、換世代即無權|不需要新 A；原生無角色 UI 仍待 A-027|
|SAFE-02|C02 依 region 解 string8，保留各欄來源與 unknown；不可從 Client 字串建立認證|A-003/021/027 已足夠開發 codec；field1「帳號」仍待 A-027 證|
|SAFE-03|輸入帳號與登入帳號不同/無有效登入/跨連線/停權 → 禁止 PendingDraft、Character、TransferGrant，且**不得回會誘發 C04 的 S02(0)**|Server 可先做檢查及 SQLite 合成測試|
|SAFE-04|已驗證 Owner+generation 綁 PendingIntent；C04 原子提交，重送只提交一次；C15 只能取消未提交同 owner 草稿|已知 A-016/028 子集可做，不能宣稱原生 Client 完整創角|
|WIRE-01|驗證「C03 已登入、無角色」後真的能用原版 Client 進 NewUser/MakeInfoDialog，並確認 C02 首欄意義|**A-027/A-021 定點補 Client xref 與 UI 事件；未證則 native C02/C04 不開放**|
|WIRE-02|依 state0x1D→S02(0)→C04→0x1E→S02 / C15→0x1F 的有證分支回覆；追 C04 成功後操作/登入返回|**A-028** 補最後 UI callback；錯誤 status 不猜|
|WORLD-01|S03→C10 一次性 token、可用 MAP 的 S15/S14→C35→S04/S33；Server 自訂合法出生座標|A-022 只需 Client MAP/CRC/呈現條件，**不需還原原服出生選擇**|
|SCRIPT-01|Server 自訂 Born 首次發送政策，執行 S44/C6C 生命週期；關閉不是任務完成|A-023 已有子集；真 PaperDialog UI 可另驗|

## 強制安全狀態

`Unauthenticated` → C03 成功 → `AuthenticatedNoCharacter`（Server **內部**）→ **僅有 Client 證據支持的入口**進 `NativeNewUser` → C02 第一欄與已驗證 account name 比對 → `MatchingDraft` → C04 → `CommittedCharacter` → **依 A-028 有證 Client UI**返回登入/進 World。

只有帳號名稱相同不足以取得 owner；角色 owner 永遠取 Server account_id。沿用 Admin 帳號 canonical 比較（3～32 ASCII 字母/數字/底線、大小寫不敏感、不修剪、不接受別名）。如果有未登入或舊世代的 C02，即使欄位剛好填了 A 也必須拒絕；密碼/停權/一帳一角/名稱唯一/appearance 都需其他獨立檢查。

**開發與原生啟用是不同門檻**：SAFE-01～04 可立即繼續規劃或實作；NativeNewUser 必須先取得 A-027 的原生 UI 可達性與 C02 欄位意義，才能開放 Host C02/C04。未知時保持目前的 fail-closed，不為了測試改 Client 或虛構 S02 錯誤碼。C04 最終成功 UI 並不等於直接 S03；C15 晚到不能刪已提交角色。

## 對應現有 Server 程式與後續交接

已核對 `as_server_roy` 的 `CharacterCreationAccountGuard.cs`／`CharacterCreationStore.cs`／`LoginWireSession.cs`。安全守衛及草稿持久化是已存在的開發基線，但 Host 目前拒絕原版 C02/C04，且沒有證據證明空角登入可由 Client 進原生創角。**本輪只更新規劃，不宣稱 Server 實作或測試已執行。** 正式追蹤仍為 ONB-01～06；SAFE/WIRE 僅是交接切片。

短期並行：A-027（登入後 UI/帳號欄）、A-020（登入 metadata）、A-022（MAP/C35）、A-028（C04 後續 UI）。下一階段 A-024（NPC 點擊/生成）、A-025（技能）、A-026（任務完成）；Server AI/任務/出生點決策由 DEV，不用要求 A 找原服內部設定。

參考 [分析者精準問題](../03-analysis-requests/next-client-io-evidence.md) · [就緒關卡](onboarding-readiness-gates.json) · [驗收計畫](../05-conformance/native-creation-gate-test-plan.md)。
