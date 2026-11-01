# C35拒絕的非敏感欄位診斷

使用者測試已到C35但原先只得到一般close reason，因此補充R-019/R-037的診斷設計；這是Server設計增量，不是使用者指定解密／記錄所有封包正文的要求。

CloseSummary可附`MapCheck`：ExpectedHeaderWord、ExpectedChecksum、ReceivedHeaderWord、ReceivedChecksum均為u16，Accepted為bool。僅在有授權角色、有效pending load且成功解析C35後產生；缺少時保留null，不能填造收到值。保留同TraceId、phase、Server build與時間，對照操作及資源／profile。

嚴格兩欄不符與狀態／期限拒絕分流固定原因碼；兩種情況都不允許提交entry。不記raw/解密bytes、帳密、E-MAIL、billing或token；此處是明確允許的非敏感語意欄位，不能擴大成一般body dump。格式／身份檢查未到此點時，不能以MapCheck缺省宣稱CRC錯。

測試同時覆蓋正確與錯誤pair、拒絕後無entry commit，以及journal型別／非秘密欄位；原版Client與特定地圖checksum的動態結果獨立，不因Server合成pair通過便宣稱地圖已載入。參考 [本輪實測與限制](../04-analysis-integration/world-ui-prelude-c43-20261101.md)。
