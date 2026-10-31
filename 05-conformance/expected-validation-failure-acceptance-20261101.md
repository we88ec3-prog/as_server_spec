# CT-112／CT-113：預期驗證失敗回原生錯誤、保留連線與去敏原因 Log
2026-11-01｜R-036／ADR-009｜`planned`／原版 `Asgard.exe` `native_client_validation=not-run`。完整契約 [預期驗證失敗政策](../02-server-planning/expected-validation-failure-policy-20261101.md)。

## CT-112（創角與原 Client GUI）
|步驟|輸入／情境|Server 要求|原版 GUI/連線驗收|
|---|---|---|---|
|1|Region2～4 的 Admin 已建帳，NewUser C02 故意輸錯密碼|拒絕，`[VALIDATION_FAILED] AUTH_INVALID_CREDENTIALS`，沒有草稿、角色、token、email 改寫；按**已證**原生狀態發 S02(nonzero,string8)，不因普通錯密 Close|原版顯示明確錯誤，S02→C15 若實際存在，必須記真實 opcode、socket、GUI|
|2|帳號不存在／停權／達到正常限流|不洩露帳號存在與否；不發成功 S02；持久資料不變；限流與安全濫用分級|Client 可以看見正確原版錯誤 UI；普通失敗保留重試通道|
|3|C02 通過但角色重名／已存在；C04 外觀非法／資料競爭|S02 合法非零＋去敏 `CHAR_*` reason；C04 不半寫、C15 不撤銷已提交角色|原版可以正確顯示，取消後不誤跳 World；若 native C15/new socket 規則不同必須記錄|
|4|重試合法資料後 C02→S02(0)→C04→S02(0)|原子提交一次、Email 隨 C04 提交；遵守 ADR-008 成功直入 World|**不**要求玩家人工再輸入 C03；失敗前原本正常 socket 的合法恢復路徑必須由原件證據定案|

若 Native S02 失敗碼尚未從 A-030 取得，前述所有「Client 錯誤可見」仍 **blocked**；不得隨便發 `status=3` 或以 `Close` 當測試通過。採合成碼測試只能證 Domain 安全，不能標 native PASS。

## CT-113（各功能 + Log + 安全）
- `C03` 密碼錯／限流；對應 S02 失敗、保持 TCP、`[VALIDATION_FAILED]` 含 reason_code、response_sent、TraceId；不得只出現 `[PACKET]`。
- 後續已實作 native adapter：移動碰撞／太快、技能 CD／無 MP、任務條件不足、道具容量不足、交易取消等，只要是正常的拒絕，就回**該功能原生可辨的**權威校正或錯誤，而非無條件 Close。缺原生映射則標 blocked／相容缺口。
- 所有 expected/business reject 不得計入 `[UNEXPECTED_PACKET]`；未知 opcode/畸形 frame/加密異常、權限竄改/持續濫用可依明定安全策略斷線，但有具體 reason、phase、close_policy。
- 對 `data/diagnostics/game-packets-YYYYMMDD.jsonl` 和預計的拒絕事件：每拒絕一次一筆，與相同 TraceId 之 C2S/S2C/Close 對應；檢查沒有密碼、Token、帳號、EMAIL、Client 原文 body、SQL 敏感例外。
- SQLite/PostgreSQL 的 pending、重送、失敗後重試／重登狀態與資產 ledger 保持冪等；僅網路錯誤時不得假造已送到 Client 的錯誤 UI。
- 區分 `response_sent`（Server 成功寫入）與 `client_ui_observed`（真人原版 GUI 證據）。前者不能代替後者。

完成標準：原版 CT-112 和安全／Log CT-113 的各負向案例逐項通過，不以合成封包或 CI 通過冒充原版 GUI。
