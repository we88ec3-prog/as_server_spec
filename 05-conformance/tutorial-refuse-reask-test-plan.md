# CT-102：拒絕入學＝無副作用、可再次點 NPC 問

來源 R-034、SCN-019、[三項新決策](../02-server-planning/three-policy-adjustments-20261031.md)，Server Domain planned，Client Native E2E not-run。資源 `nNewJoin01.dat` 內 `STATE=ACCEPT/REFUSE` 為**已取得 Script 候選欄位**，NPC→Script mapping/原版選項回送仍需 A-012/A-023/A-026。

|情境|預期|
|---|---|
|首次點 NPC，點「不入學」|可結束本次視窗，但 Account/Character/Quest/Admission/Onboarding/Map/Inventory/EXP/Reward/SharedActor **均不變**；沒有拒絕後永遠不能問的旗標|
|再點同 NPC|重新建立**合法的新 ScriptRun/context**，再次顯示相同入學選擇；沒有因先前 REFUSE 而被拒絕|
|拒絕 N 次然後選接受|前 N 次零變更，第 N+1 次 ACCEPT 可走既有合法入學流程；**ACCEPT 只是意圖**，不可直接當 QuestCompleted、發獎/切圖|
|玩家甲拒絕、乙同時詢問或接受|甲不影響乙，兩人各自 Dialog context/進度，NPC 仍全圖共享|
|相同 REFUSE 重送、舊 context、斷線重登|不重複創建任務/獎勵/轉圖，也不永久禁掉重新互動。舊 context 回覆應依 Client protocol 安全處理／忽略，不可執行其他人的回答|
|Client C6C4/2 Dispose/no-reply|只能表示本次 Script closure，不可當成拒絕/入學/完成的 domain 事件；不透過此 callback 寫權威 Quest 狀態|

Native UI 測試要記錄 `Asgard.exe` SHA、腳本資源 hash、NPC/S44/C6C 的去敏通道、Dialog 回覆與再點擊反應。原生 unknown 不可被標成已知錯誤/完成 opcode。
