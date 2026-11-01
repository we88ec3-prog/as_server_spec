# ChatGPT／Claude 網頁版：技能與普通攻擊深入分析

日期2026-11-01。使用者要求先盤點既有分析，再交由其他網頁模型深入研究技能；
另提出新手場景可能需要普通攻擊打怪。這是使用者需求／線索，不能當原服任務條件。

## 既有成果，請先讀而非重做

先讀[盤點紀錄](AUDIT.md)，其中也列出歷史CT編號與S1E／S5F錯誤的更正。

|主線|已交付|真正缺口|
|---|---|---|
|[A-009](../../task_a/roy2/A-009-analysis.md)|C13、S13條件欄、S5F、部分C3D/S3D；兩個攻擊producer|輸入到target ref、效果handler／數字／HP／死亡動畫與必要時序|
|[A-010](../../task_a/roy2/A-010-analysis.md)|C4D/C56/S52/S48/0x2C/0x2D六包；C4D選取值來源|技能清單／學習／slot-ID、C56真正producer、收包到UI、計時／效果identity|
|[A-025](../../04-analysis-integration/A-025-tutorial-combat-contract.md)|教學CombatIntent邊界；C13/C4D/C56最小子集|教學是否要求擊殺、怪物／目標／完成事件與Script的關聯|
|[A-008](../../task_a/roy2/A-008-analysis.md)|S08條件狀態投影|與施法、傷害／資源更新的具體欄位和調用時序|
|[A-024](../../task_a/roy2/A-024-analysis.md)|物件生成、移動、死亡／移除的wire；招募員最新修正另有報告|可攻擊怪物kind／ref／動作、死亡callback及場景綁定|

以上relative連結自本目錄需回到repo根；實際原始路徑以[機器任務表](tasks.json)
的`baseline_documents`為準。A-009/A-010/A-025的integrated代表已有部分交付，
不是所有玩法完整；不要新開同題A-XX，也不要把正式Native CT改成passed。

原件固定：Asgard.exe SHA256
`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，
x86／ImageBase0x400000。不要把診斷副本或新Server程式當原服實作證據。

## 工作順序與分工

用tasks.json的深挖子任務，不新增正式A編號。先A009-D01普通攻擊閉環，
技能先A010-D01清單／選取值，再A010-D02施法／取消，再BUFF與其他類型。
ChatGPT與Claude可各領不同task；若獨立覆核同task，保留兩個reviewer結果
並比較證據，不用多數決把推測升級成原件事實。

原始nNewWar01確實說明滑鼠／空白鍵基本攻擊、強制攻擊及CTRL+D技能窗。
其中講義文字與關閉UI沒有證明某個kill objective。A025-D01需追實際事件鏈；
未證前不自行添加必殺某怪的畢業門檻，也不能據一份腳本斷言全教學無戰鬥。

## 網頁模型的能力與資料邊界

公開spec是任務與基線；精確偽碼／xref／指令由本地REA另行匯出至私有分析包，
不提交原EXE/DAT、原始腳本、執行期資料或私有Server程式。網頁模型不能直接
存取使用者E槽或本地REA。只有上傳／連接且實際讀到的資料才可列reviewed；
GitHub連結、檔名或manifest存在均不等於已讀完證據。

每回合只處理一個task，先讀小型輸入索引及其required資料。資料缺少時輸出
needs_evidence及精確address／function／resource selector／需要的xref方向；
不要求重傳整套EXE、全部偽碼或泛稱Skill*.dat。尤其C56直接callers只看到
factory時，不能推論UI不會使用；需追函式指標註冊及間接建立路徑。

可重用提示詞見[PROMPT.md](PROMPT.md)，結果契約見[RESULT-CONTRACT.md](RESULT-CONTRACT.md)。
輸出是候選分析，須由本地以原件／REA及必要實機驗證後才整合進正式封包表。
Server仍由本地直接開發；Web分析不接觸私有roy，也不阻塞已證部分的開發。
