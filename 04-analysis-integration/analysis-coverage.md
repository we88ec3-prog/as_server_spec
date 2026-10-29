# 既有分析整合覆蓋表

本表回答「以前分析過的內容有沒有放入新規格」。**已放入經整理的結論與必要欄位，但不是將所有原始檔案完整搬入。** 下表逐一列出舊整理文件及新落點；舊文件SHA僅用來追溯本次整理來源。

|舊整理文件|整合程度|新規格落點|涵蓋／限制|
|---|---|---|---|
|assets.md|結論摘要|[resource-formats.md](resource-formats.md)|DAT、Script、Human/YPF與資源盤點；未整包複製抽取工具或素材。|
|background-music.md|結論摘要|[packet-processing.md](packet-processing.md)、[scenarios.md](scenarios.md)、[vectors.json](../05-conformance/vectors.json)|S19循環／停止、Client音量與原地圖曲目未知；有聲音已人工確認。|
|clothing-colors.md|已知細節子集|[appearance.md](appearance.md)、[vectors.json](../05-conformance/vectors.json)|S05/S33獨立RGB、0x1000旗標及原始配色sentinel。|
|cross-client-handoff.md|新交接流程接替|[ai-analysis-handoff.md](../00-governance/ai-analysis-handoff.md)|舊工具交接改用A任務、PKT／SCN／CT交付格式，不帶私有實作入口。|
|equipment-flow.md|已知細節子集|[items.md](items.md)、[appearance.md](appearance.md)|C1C/C1E、S0F/S37、衣櫃與正式物品限制。|
|evidence-index.md|證據身份索引|[evidence-index.json](evidence-index.json)|整理Evidence ID與原生入口；沒有整包複製完整REA或偽碼。|
|intro-switch.md|結論摘要|[client-compatibility.md](client-compatibility.md)|原生影片完成轉場與保留動畫選項；不分享改版EXE或私有建置工具。|
|login-flow.md|已知細節子集|[profile-login.md](profile-login.md)、[packet-processing.md](packet-processing.md)|metadata／清單／公告／登入／交接；已補SScript清快取副作用。|
|map-transition-native.md|結論摘要|[scenarios.md](scenarios.md)、[packets.json](packets.json)|S15清舊物件、保留本地玩家；C11原地轉向入口。|
|maps.md|已知細節子集|[resource-formats.md](resource-formats.md)|MAP header／區塊／tile／尾區布局；碰撞語意仍未知。|
|protocol.md|結論摘要|[transport.md](transport.md)、[packets.json](packets.json)|binary、table0、byte序、CP950及雙向opcode；其他seed未完成。|
|README.md|結論摘要|[baseline.md](../00-governance/baseline.md)|目前功能及限制已整合，舊歷程不直接當最新狀態。|
|recovery-plan.md|新規劃接替|[roadmap.md](../02-server-planning/roadmap.md)、[requests.json](../03-analysis-requests/requests.json)|舊四目標路線由共同Server規劃取代，保留歷史不重複作現行計畫。|
|screen-centering.md|已知細節子集|[appearance.md](appearance.md)、[vectors.json](../05-conformance/vectors.json)|鏡頭公式及48px差；靜態／測試通過，最後畫面驗收仍待回報。|
|stability-investigation.md|結論摘要|[client-compatibility.md](client-compatibility.md)、[scenarios.md](scenarios.md)|移動確認／時間檢查／提示懸停及延遲候選；原始執行緒與操作日誌不分享。|
|startup-runtime.md|結論摘要|[client-compatibility.md](client-compatibility.md)、[transport.md](transport.md)|HKCU隔離副本、啟動讀檔、raw問候與framed簽章。|
|user-testing.md|驗收摘要|[baseline.md](../00-governance/baseline.md)、[scenarios.json](scenarios.json)|人工通過與待驗收分開；私人測試紀錄、角色資料不附。|
|validation.md|驗收摘要|[baseline.md](../00-governance/baseline.md)、[scenarios.json](scenarios.json)|歷史正常路徑與限制整理；不把單人通過當成完整MMO通過。|
|world-flow.md|結論摘要|[scenarios.md](scenarios.md)、[appearance.md](appearance.md)|世界初始化先後、自己顯示、外觀與移動；採較晚鏡頭8/9校正。|

## 哪些沒有整包放進來

- 作者的Server實作、帳號DB、token及執行日誌仍不分享。
- 原始EXE/DLL/DAT、隔離修改版、全部偽碼及大型REA原件保留原工作區；本repo只放規格所需結論、身份索引及經整理的欄位。
- Evidence ID是原本本地分析紀錄的身份，不是外部開發者可直接下載的公開連結。若要逐指令複核，可依Client SHA和函式位址重現，或另行審查所需摘錄後分享。
- 戰鬥、技能、完整碰撞、多人可見性、經濟等尚未完成的分析仍列於A任務，不會因搬到新目錄就變成已完成。

## 目前驗收

登入／所測創角與衣服／正常移動／在線切圖／動畫開關／位置保存／更衣面向／背景音樂已有人工驗收。最後的置中與獨立衣色修正維持「服務測試通過，Client畫面待回報」。

本次核對 19 份舊整理文件，索引 211 個不同Evidence ID；數量不是功能覆蓋率或完整逆向完成度。
