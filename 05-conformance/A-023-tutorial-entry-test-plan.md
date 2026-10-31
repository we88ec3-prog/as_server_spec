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

## 2026-11-01 原件靜態補測 CT-117（原 CT-033～035 不升級 native PASS）

本次已實際核對原版 Born.dat、Basic.dat 素材與 `AlertFrame.ypf` metadata：Basic 39 index slots 含 sentinel、Frame offset13196 size177648 SHA `b641441d...`、YPF17；Born XML CRC CP950 `1d87b0c0`。新 22 個 EXE 原生 VA anchor 證實 `S44(type2/subtype0)` 會觸碰 UI slot0x23/component3/4，`S44(type2/subtype2)` 會操作 slot0x24，**不是 Born 的 type1/subtype0 Script Main 啟動**。

```bash
python task_a/roy2/a023_native_script_dispatch_probe.py Asgard.exe
python task_a/roy2/a023_born_basic_probe.py --born Born.dat --basic Basic.dat
python -m unittest discover -s task_a/roy2 -p 'test_a023_born_basic.py' -v
```

GitHub CI 只執行 21 個合成資源格式邊界測試；原件 SHA/22 VA 為本地獨立驗證。完整請看 [CT-117 細則](A-023-original-born-basic-ui-test-plan.md)、[原始 Client 與資源證據](../task_a/roy2/A-023-born-basic-native-dispatch-20261101.md)。**PaperDialog.dat 的原件此輪未在本地，依賴只能沿用歷史已登記報告，不冒稱重跑全 GUI**。首次原服 Born 下發條件／女招募員 EntityId／Script 綁定與真正 Native GUI 必須在 CT-034/035 找到原始記錄或動態 UI 證據，不能以 synthetic S44／fake NPC 完工。

## 2026-11-01 已取得四份 Script 原件後新增 CT-115

**不需再要求** `PaperDialog.dat`、`PaperDialog02.dat`、`nNewJoin01.dat`、`Merchant.dat`：本輪四檔全部 SHA、XML wrapper、CP950 CRC/函式表均已由 [A-023 原始資料驗證](../task_a/roy2/A-023-four-script-native-dependencies-20261101.md) 確認，新增 [CT-115 專項](A-023-four-script-verify-test-plan.md)／28 項 synthetic CI。
```bash
python task_a/roy2/a023_script_bundle_probe.py --script-dir <原件所在目錄> --born <Born.dat>
python -m unittest discover -s task_a/roy2 -p 'test_a023_script_bundle.py' -v
```

**新 native GUI 驗收點**：PaperDialog02 button OK→PAPER02 START、CANCEL→NOT，但 cancelControl=OK，應另測 ESC；nNewJoin01 MerchantTalk 三頁最終 OK→STATE ACCEPT/CANCEL→REFUSE；抓 C6C(1) 的**ScriptRunner root + context**，不是盲填依賴檔名。成功 SendReply 再 Dispose 原生 C6C1→C6C4，unreplied Born 普通 OK C6C4→C6C2。多 ScriptRun 依賴名稱碰撞和缺 `QuestDialog_Create`／`MerchantDialog_Create`／`MerchantDirectTalk` 真定義時 fail-closed。

CT-034/035 的原版首 NPC 身分/map/Script 綁定/首 Born 發包與可見 UI、選校／quest 權威狀態仍未驗；CT-115 的原件離線 PASS 不能升級這些 Native Client CT。
