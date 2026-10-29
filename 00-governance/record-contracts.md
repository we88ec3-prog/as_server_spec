# 紀錄契約與規格完整度

JSON中ID與關聯是機讀追蹤來源；Markdown是人讀說明／表格，traceability.csv是衍生索引。修改時一併更新對應說明、索引、向量和變更紀錄，再刷新審查manifest。驗證工具能查斷鏈及hash，不能代替語意審查。

R：id、system、priority、title、acceptance、baseline、status。SYS：id、requirements、analysis_requests及責任說明。A：id、system、requirements、method、deliverable、priority、status、assignee、evidence_ids；接手時補前置依賴與Client身份。

PKT：profile、direction、opcode作wire key；id作穩定追蹤鍵。layout必須標單位與條件，client_entry指出原生入口。補完後應加逐欄offset/type/endianness/condition/unknown/evidence，以及Server語意、Client效果、拒絕情境和CT。layout_status=partial的項目不可宣稱足夠獨立實作；profile-documented也只覆蓋明示的子集，不代表全部原生分支。

SCN：id、requirements、packets、狀態及限制；成熟情境還須列順序、前置／後置、保存點、逾時、取消、重送、Client驗收及失敗輸出。CT：id、requirements、packet_ids、level、合成輸入與預期；不要把body與整條wire混淆。

Evidence：至少含目標SHA／版本、位址或資源位置、Evidence ID或重現步驟、observed-static/runtime/inferred/designed/unknown、限制及分析日期；引用要支持具體結論。原始大型證據與敏感紀錄不直接進共享repo。

進入「可供獨立實作」的門檻：欄位／狀態無必要缺口、未知已隔離、雙向處理和失敗路徑有定義、合成向量可比較、另一實作者不需存取私有程式。進入「Client驗收」還需有相符原生Client的實測紀錄。
