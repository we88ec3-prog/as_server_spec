# task_a/roy1 A-021 合併後獨立審核與規格邊界（2026-10-31）

目標：`Asgard.exe` PE32 i386，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。來源：已 fast-forward 合併的 `task_a/roy1`，merge head `d1b53b0c732abd76674d9ada00fcb6bb8cf31f38`。審核方式：本次對提供的二進位檔核驗 hash，使用反組譯核對對應 RVA/VA 的寫入及狀態邏輯。下列均為 **observed-static**，非原生 Server runtime 證據。

## 已獨立確認的核心結論

1. **C02** serializer `0x5742b0` 存在 region 分支：region code 2～4 使用四個 string8 加旗標的布局；其他區域另有三個 string8 變體。不能使用單一全區域固定欄位布局。已驗證實際 writer 分支；各 string8 的**語意和身份/憑證用途尚未確認**。
2. **C04** writer `0x574420` 輸出五個 u8 欄位（性別、髮型、RGB 的 profile mapping 仍依既有證據）。例如五 bytes `01 02 11 22 33`。
3. **S02** parser `0x57dbc0` 讀取 status u8 和 string8 訊息；含 `00 00` 的 body 可表 status 0、空訊息，不意味所有狀態與 wire 全欄位均完整。
4. **Create Info UI** 存在 C02 傳送後 local state `0x1d`，該 state 收到 S02(status0) 後觸發 C04 並進 `0x1e` 的靜態路徑。這是 Client 在符合某回覆時的反應，**不證明原服真的回了這個值**，亦不證明 C04 後角色建立已成功。
5. **C02 可在 C03 之前出現**。舊規劃不能假設「C03 已登入」是每次 Client 發 C02 的必要前置條件；但**先發 C02 不等於已認證的 Account 認領/擁有者身份**。

## 高風險缺口與必須修正的推論

- A-021 報告提出 `ClaimExistingAccount` 的 provisional Server 設計，但 C02 字串字段的身份/密碼/授權意義未證實。**單憑 Client 發送一組帳號名或 C02 格式，Server 不得視為管理員預建帳號的有效所有者**；這會違反 R-025 安全邊界，也可能讓惡意 Client 在已存在的他人帳號下建角色。
- **A-027/P0** 專門追究 pre-C03 C02 的身份來源、既有帳號認證，及無角色 UI 入口；若無法證明可安全綁定 owner，原生註冊/創角相容路徑必須 fail closed，不允許假憑證/免認證分支。
- **A-028/P0** 專門追 C04 後 `0x1e` 的 S02/error/result 與 CharacterReady/World handoff；C02 的 S02 status0 只代表進入發送 C04 的局部門檻，不等於創角完成。

## 審查裁定、交付與驗收

- A-021：保留 `status=integrated`（限已審核的靜態 C02/C04/S02/UI 子集），`handoff_status=partial`、`native_client_validation=not-run`，將整體 `implementation_ready=false`，避免下游錯誤地把它理解為「首次創角 wire 已完全可實作」。
- 開發可**先**寫 region-aware C02 decoder、C04 五欄 parser、S02 結構與無權限的 UI transition fixtures、DB 角色唯一性；不能在未經證實的 C02 上直接建立 Account、賦予 Account owner、核發 World grant 或回傳承諾 C04 建角成功的授權狀態。
- 預定測試：CT-029（C02 region variant）；CT-030（C02 非法認領/前認證保護）；CT-031（state 0x1d 收 status0 只觸發 C04）；CT-032（C04 最終回覆/重登/交接，待 A-028）。
- **研究完成**和**Client E2E 驗收**仍分離：未來 CT 失敗可新增分析/DEV 修正，不會抹除本次可重現的 BIN 證據。

參考 `03-analysis-requests/requests.json`、`02-server-planning/first-login-onboarding.md`、`00-governance/phase-gates.md`。
