# A-026 原版 Client CT-028 教學完成與退圖原生驗收（roy3 增量）

靜態研究 ready，但原生 Client GUI E2E **not-run**，不能使用合成 Python PASS 假冒原服測試。

|Case|原生操作|應留存證據與 gate|
|---|---|---|
|T01|新角色不重新登入，直接進 World|S15 map/ref、S14/C35、S04 x/y/viewport、Born S44、真 spawn，不把 (31,29) 當出生|
|T02|Born PaperDialog OK|C6C4/2 ScriptClose；不視為完成|
|T03|到女招募員點選|真 entity id、Client Cxx Click/C39 payload、S2F、S44 Script name/context/NPC 綁定|
|T04|nNewJoin01 按 REFUSE、再互動、再按 ACCEPT|C6C1 STATE=REFUSE/ACCEPT 真 wire；不因 REFUSE 永久封鎖、不因 ACCEPT 當成已畢業|
|T05|PaperDialog02 START/NOT|與 STATE 意圖分開、紀錄真正 Server 觸發|
|T06|真正達到原服教學終局|Server quest flags/verified event，若 reward 存在錄真 item/EXP/gold/quantity；若不可觀察則維持 unknown|
|T07|原服出圖|目的 S15 map/ref、S04 x/y、S14/C35 對應版本，經入圖安全確認後持久化 exit|
|T08|在關閉對話、ACCEPT、完成、ExitPending、出圖中／後斷線|重登/重播、不同角色/generation 不錯領、不重賞、不錯圖、不漏 checkpoint|
|T09|錯 Script context、未知 C39 形狀、重複 C6C、stale C35|不造成無權畢業、跨帳號發獎、錯誤 map exit|

保存原始 Asgard.exe 和 Map0/1/2 SHA、Script release hashes、匿名化封包 raw decoded body、GUI/物件/任務狀態、Server epoch/commit trace。nNewJoin01.dat、PaperDialog.dat、PaperDialog02.dat 的 bytes 在 repo 沒有入庫；之前資源分析證據已收錄 main。若需本回合原始檔重檢，可指定三個檔名。原版 Server quest/exit authority 仍需額外來源，不能由 Client 靜態分析代替。
