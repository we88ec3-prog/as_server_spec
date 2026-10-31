# A-026 / roy1 — 原版教學完成／獎勵／出圖／復原研究

**日期**：2026-10-31；**Branch**：task_a/roy1（沿用，不創建）。**Client**：Asgard.exe PE32/I386，SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145；**Resource**：Born.dat 589 bytes，SHA256 992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98。Evidence ID：ev_a026_20261031_born_merchant_exit_bin_static；需求 R-013/R-017/R-031；參照 A-012/015/016/022/023/024/025。

**交付判定**：A-026 integrated / handoff_status=partial，implementation_ready=true **只限觀察到的 Client 通用協定、設計的交易/防重/出口恢復骨架**；native_client_validation=not-run；native_tutorial_complete_ready=false、native_reward_proven=false、native_exit_destination_proven=false。沒有原版 Server 的完成/獎勵/出口政策原件，不能冒充完整原服教學復刻。

## 1. Born 直接解包的結果（observed-static-resource）

Born.dat 經 zlib 解壓為 1,154 bytes，前六 bytes 是 BE u16 version=1 和 BE u32 UTF-16LE code units=574，後面是 UTF-16LE XML，唯一 entry function 為 Main。此 Main 呼叫 client.CreateArray、page.Insert、PaperDialog_Create 顯示單頁引導，指示前往 **(31,29)** 點選女性招募員。這是紙上引導座標，**不是原版 spawn、exit map/coord、教學完成點**。XML 沒有明確 SendReply、quest completion、reward grant、teleport/exit 或必要擊殺條件。**單份 Born 不含戰鬥條件不代表所有教學流程都不需要戰鬥**。

依 A-023 交叉核對 PaperDialog 的關閉：dialog.Dispose 後的 client.Dispose 先送 C6C subtype4，再於未 SendReply 時清理送 C6C subtype2。以合成 context 0x11223344，body 分別是：
- 04 04 426f726e 11223344
- 02 04 426f726e 11223344

這只表示 **Script lifecycle close**，既不自動完成任務，也不觸發獎勵；Client 的兩次 send call 不保證兩個獨立 TCP frame。若另有 C6C(1) SendReply，須按 runner/context/實體和被 Server 核准的任務條件判讀其 key/value，不能直接由文字 STATE=ACCEPT 判定畢業。

## 2. 本輪補做的原始 Client BIN-first 入口

|Native VA|Client 證據|不能推論的原服政策|
|---|---|---|
|0x5737c9|CMerchant constructor opcode **C39**|不能保證它就是該女性招募員的專屬封包|
|0x573860..0x5738f6|CMerchant writer 先 u8、u32 BE、u16 BE；依內部 subtype=1..9 再附加變長 string8／u8 欄位|u32 目標對應哪個 NPC、各種 subtype 的業務意義和畢業條件未證|
|0x581ba9, 0x581ca0..0x58207f|SMerchant constructor/reader 有 opcode 0x2f 與各種類型的 u8/u32/u16/文字欄位|其 class/opcode 和既有 SMapSize 名稱存在交叉引用疑點，暫不補全 S2F 為單一完成回包|
|0x57fe99, 0x57ff30..0x57ff9d|S15 map description 3×BE u16 + 2×u8 + string8；有原生載圖入口|未提供任何原版 tutorial exit map ID|
|0x57fdd0, 0x4f2300|S14 1 要求 C35；2 local loading callback；3 為異常分支|S14(2) 不等於資料庫中畢業已提交|
|0x573490|C35 2×BE u16：本機 MAP header+4 欄與 structured checksum|沒有 map id/epoch，跨世代相同 pair 不能靠封包區分|
|0x589990..0x5899bd|S04 四個 BE u16，本機 profile 為 x/y/viewport_x/y|不含官方教學出口座標證據|
|0x574bb9, 0x574c50|CQuit constructor opcode **C0B**，writer 空 body|離線/退出 Client 不代表完成新手教學|
|0x57e260|S1E DieObjects 讀 u32 object ref（A-025）|物件死亡通知不等於 quest objective 完成|

與 A-022/A-016 一致：S15、S14、C35、S04 可組成**通用**切圖與定位，但不能以切圖動畫或 C35 回傳直接推論教學完成。C39 是與 A-023 nNewJoin01.dat「school join／STATE=ACCEPT/REFUSE」候選對話**可能相關**的 Client 通道，不存在已證的 NPC entity→Script→完成事件映射。

## 3. 候選步驟與未知項嚴格分層

|遊戲步驟|Client/資源已證|Server 依據|
|---|---|---|
|初入新手教學|一般 World loading 協定 S15/S14/C35/S04|原服首次 flag / map / spawn：unknown|
|看到 Born 紙張|S44(1,0) 能按名稱啟動 Main|原服何時及依哪個角色旗標下發：unknown|
|按 Born OK|C6C(4) 後 C6C(2)|ScriptClosed，**非 Completed**|
|抵達 (31,29) 點女性招募員|文字指示 + C39 一般 NPC/商人通道|招募員 object/map/Script 綁定：unknown|
|加入對話候選 STATE=ACCEPT|A-023 的 nNewJoin01 candidate|是不是該 NPC、是不是教學畢業：unknown|
|攻擊/施法/死亡|A-025 C13/C4D/C56/S1E 等 generic codec|是否必要、怪物目標／擊殺計數：unknown|
|完成／獎勵|原 Client 無可證的畢業原服判定|原服完成 rule、獎勵存在與內容：**unknown**|
|出圖／再次登入|一般 S15/S14/C35/S04 與斷線交接|目的地 map/ref、exit x/y、重登復原原服政策：**unknown**|

R-031 是**新 Server 需求規劃**，不是原服一定發裝備/金錢/經驗的觀察。原版是否有任何畢業獎勵亦未證。World 事件與任務旗標須有原 Server/內容證據，不以常見 RPG 劇情猜想。

## 4. Server 安全設計（DESIGNED，非原服規則）

角色狀態：TutorialEntered → ScriptRunning → ScriptClosed / NPCInteractionObserved → AwaitVerifiedCompletionRule → TutorialCompleted (durable) → ExitPending (valid original exit map/version/coord) → WorldLoading → TutorialExited (durable)。

- C6C(2/4) 只更新有權限的 script_run、context、generation 的 lifecycle，重送冪等；C6C1/C39 不直接發獎。
- 只接受 Server authoritative event，在 **verified original NPC/quest/rule** 下原子寫 CompletionLedger UNIQUE(character,rule,event)，optional RewardGrant UNIQUE(character,grant_reason)（**獎勵需證據確定存在才 grant**），Progress CAS 與 Outbox；HTTP/封包回覆遺失不重領。
- 只有得到版本綁定、真正原版目的 map/ref、出口 x/y、MAP checksum expected pair 才允許退出。Born (31,29) 不可當出口。建立單一 pending loading_epoch；C35 wire 沒有 epoch，若同一連線重疊同 pair，必須排他/barrier/fail closed/reconnect。
- TutorialCompleted 與 TutorialExited 分開提交。crash 在切圖中保留之前 durable map/pos，完成及獎勵仍不重複；重登復原或安全重新切圖，不能把失敗當已出圖。
- 客戶端 C0B Quit、S1E DieObjects、S14(2)、C35、C6C Close 都不能單獨當作事件權威或畢業證明。

## 5. 交付與驗收

本輪原始 EXE 11 個 byte signature、Born wrapper/XML 與 C6C(4/2) 合成 body + SQLite 狀態/唯一 ledger/crash test：**本地 10 項 unittest passed**，詳見合成測試工具與報告。這是離線靜態/設計模型，原生 Client E2E 沒執行。

更新 CT-026/027/028（planned/not-run），新增 CT-054（ScriptClose 不得畢業）、CT-055（原服證實的 completion/optional reward once、crash/replay）、CT-056（只有原版合法出口及 map epoch/CRC 可出圖、checkpoint recovery）。SCN-013 **維持 analysis-required** 而非宣稱原版成功。

缺少的**具名檔案**：本次本機沒有 PaperDialog.dat 與 nNewJoin01.dat；另需取得包含教學首次登入→招募員對話→完成/失敗→正常出圖→重登的原版 Server 封包/事件紀錄，或原版 Server 的 NPC/quest/exit handler/config。無證據可以確認單一「Quest*.dat」即可補齊原服規則，**不能虛構檔名**。Asgard.exe、Born.dat、Map0/1/2.dat 已有，**不是缺失**。

重現：sha256sum Asgard.exe Born.dat；objdump -D -M intel --start-address=0x5737b0 --stop-address=0x573910 Asgard.exe；objdump -D -M intel --start-address=0x57fe80 --stop-address=0x57ffa0 Asgard.exe；objdump -D -M intel --start-address=0x574bb0 --stop-address=0x574c55 Asgard.exe；python3 tools/a026_tutorial_completion_model.py。
