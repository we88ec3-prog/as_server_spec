# A-023 → CT-033～035：教學入口 Script／NPC 測試腳本

版本 `TW-seed0-local-v0.1`，原 Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。Owner DEV/CT；所有 CT=`planned`、`native_client_validation=not-run`，且不得未取得必要 byte schema 就對真實安裝目錄任意發 S44。

## CT-033／Script 載入/回送/快取隔離

1. 在可丟棄測試目錄複製 `Script/*.dat` 並記錄清單/hash；正式 Client 安裝目錄不允許被測試封包清理。
2. 用原 SHA 的反組譯核對 C6C ctor 0x575140、serializer 0x575210 的 0..4 分支與 S44 ctor 0x5862e0／handler 0x52c2a0。
3. 在固定 fake script object/unit parser 上測 subtype 限制、未知 branch/欄位不成功，並將實際捕獲的合法 bytes 追加固定向量；**已有由 parser 推得的 S44(1,0) 合成 body，見 vectors.json CT-033；它不是原服抓包或 GUI 通過證據**。
4. type1/subtype3 僅在隔離環境或以靜態 path/mock filesystem 比對 0x52c8e5→0x5294e0 的檔案副作用；不得宣稱它是成功 ACK。
5. 紀錄 `script-cache-before/after` 的安全 hash／檔數、不記錄私有帳密／token／原始資產內容。未實測輸出為 `not-run`，禁止寫 PASS。

## CT-034／首次操作 NPC/Script 初始化

1. 先由 A-021/A-022 指定真正可用的無角色→創角→教學地圖/座標；需資源版本及原 Client hash 一致。
2. 在載入 S14(1)、C35、S14(2) 前後抓 opcode、body 長度、時間與 UI 截圖／事件；記是否自動出現首 NPC、文字、任務 UI，以及 `Born` 與 map/script 資料的對應。
3. 對照「完全不操作」、「第一次可操作後交談」、「不按完對話即重登」三組，逐一填首發封包、trigger、NPC id、quest state 和期待 UI。原服不可取得時，模擬 Server 試驗標記 `mock/designed`，不是原服事實。
4. 一切未證實欄位使用 `unknown`；不可自動 spawn 假 NPC、不得先完成教學進度。原生合格條件是 Client 行為與確定的資源/原服證據一致。

## CT-035／首互動的拒絕/重送/斷線

1. 取得 CT-034 的真實首互動封包後，分別測合法、未入圖、載入中、取消、重送、重登、舊連線、跨角色；現階段 opcode、status code 與初始 flags unknown。
2. 每組記錄 Server authoritative state、revision、event identity、Client UI/重試行為；不能因相同事件重送而二次初始化任務或重領資產。
3. DEV unit/integration 可以先驗「重送不雙計」的自訂設計，原版 Client E2E 通過僅由 CT Owner 報告。

結論連到 [A-023 報告](../task_a/roy2/A-023-analysis.md)。A-023 部分研究完成不取代 CT-034 原版教學互動驗收。

## Born.dat 離線驗證（CT 不取代原生實測）

補充 A023-E12：`python task_a/roy2/verify_entry_dependencies.py /local/Script` 同時驗 Born 與 PaperDialog hash、wrapper/XML、首頁／翻頁／關閉分支。完整資源應 PASS；缺依賴、截斷、不同版本應 FAIL。CT-033 增驗視覺資產解析／缺失處理；CT-034 若已證實觸發，檢查單頁紙張、隱藏 PREV/NEXT、預設／取消 OK；CT-035 比對關閉前後 wire 與權威 quest state，不能因 Dispose 字面名稱推測完成或斷線。離線結果不升級任何 native CT 狀態。

CT-033：`python task_a/roy2/verify_born.py /local/Born.dat` 驗 resource hash、zlib、BE 574、唯一 Main、三個 UI 呼叫、(31,29) 招募員點選指引；本輪離線 PASS、截斷檔 FAIL。**不等於 Native Client CT PASS**。

CT-034：若 Main 由原服真正觸發，應顯示 PaperDialog 引導；觸發時間、地圖、NPC ID 仍 unknown，需抓 S14(2) 前後事件及玩家點招募員時真正的封包。CT-035：Main 無直接 SendReply/quest 修改，但 client.Dispose 原生 API 會送 C6C4，再於尚未 replied 時送 C6C2；兩者不能直接當作「Born 任務完成」。三個 CT 的 native_client_validation 仍 not-run。


## E14～E18 追加：已追通的 start 與 Dispose 契約

以 [完整 Client 契約](../task_a/roy2/A-023-script-entry-contract.md) 為準；早期未解 wire／Dispose 敘述不再代表目前分析結果。

- CT-033：執行 `python task_a/roy2/verify_script_entry.py /local/Asgard.exe /local/Script`。驗 18 段 EXE bytes、CP950 text CRC、S44(1,0) start 合成 body、37 個截斷／selector／尾隨資料案例。context 11223344 是自訂測試值，body 不含 opcode/frame。缺 Born／PaperDialog 分開測 C6C(0,name) 請求；S44(1,1) 更新後應恢復等待中的 start。先備份隔離副本；CRC mismatch 在原件有釋放後返回原指標的潛在路徑，禁止把它當安全缺檔分支故意送入真 Client。
- CT-034：資源齊備時追 0x52c467→0x52bd30→0x52c014→0x524fa0 呼叫 Main，檢查 Born 單頁紙張、PREV/NEXT 隱藏與 OK；原服首次發送時間與 NPC entity 綁定仍需原服 trace／設定。自訂 Server 在 WorldReady 後發送屬 designed。
- CT-035：Born OK 的靜態送出呼叫為 C6C4(name,context)，再 C6C2(name,context)；有 SendReply 的腳本則先 C6C1(key/value) 設 replied=1，Dispose 仍送4，但清理不再送2。實際傳輸 flush/frame 行為另記 runtime。重送／舊 session/context 不得重複改 quest（designed）；不能將兩次 lifecycle 訊息各算一次進度。

離線結果見 `task_a/roy2/script-entry-verification.json`、語料檢查見 `corpus-entry-audit.json`；315 XML + NDW 一個非 XML，nNewJoin01 只列候選。所有 native CT 仍 not-run。
