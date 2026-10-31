# 下一輪 A-XX 精確證據清單（以 Client 發包/收包/畫面為準）

不要等待原服 Server 原始碼或要求分析者推論原服資料庫、出生點政策、首任務派送。所有結論要附原始 `Asgard.exe` VA/RVA、呼叫路徑、Client 觸發/收包、資料欄位及 UI 反應；unknown 可以 partial 交付。

|先後|A|具體要證明的 Client 行為|可從哪裡追|
|---|---|---|---|
|P0|**A-027 + A-021**|C03 有效登入但角色為空時 Client 是否能打開 NewUser/MakeInfoDialog？若能，具體按鈕/UI/封包路徑如何走？C02 第一個輸入欄是否真正是登入帳號？|C03/LoginDialog `0x4A7D10`、MakeInfoDialog 建立 `0x4AEF04` / `0x4B0B60`、C02 UI `0x4B2764..0x4B2A37`、S02 UI `0x4B1D60`|
|P0 並行|**A-020**|登入前 Client 何時送 C0F/C57/C4B、收到 S18/S56/S60 之後會否自動再送，以及其他 region seed/key 與 S00 拒絕 UI|C00/S00、metadata/list/notice 的 Client writer/handler；已知 A-001/002 不重做|
|P0 並行|**A-022（利用 A-015 已交資源）**|S15 的 map_ref 如何載入 MAP，S14(1) 怎樣觸發 C35 header+4 與 structured checksum，S04/S33 座標怎樣顯示；C25 真實 body/觸發是什麼|S15 `0x57FF30`、S14 `0x57FDD0`、C35 `0x573490`、S04 `0x589990`，Map0/1/2.dat|
|P1|**A-028**|C04 送出後收 S02(0)/非0，Client 如何結束成功畫面、按什麼才返回 Login 或再送包；C15 的時序|C04 `0x574420`、S02 `0x57DBC0`、UI `0x4B1D60..0x4B217A`；不要猜原服 DB commit|
|P1|**A-024 / A-004 / A-011**|NPC/怪物 S→C 生成、移動、消失，玩家點選 NPC 的 C→S 與對話 UI S→C|world object parser、mouse event → writer、render handler；不是 NPC AI 決策|
|P2|**A-025/026**|玩家攻擊/施法/交任務的 C→S 和收到效果/完成/獎勵包後 Client UI 變化|技能/任務 handler 和 parser；Server 判傷害/發獎自己設計|

**A-027 的最小結論格式**：列出已查的 C03-success/no-character callback、兩個 MakeInfoDialog 的 xref、Client UI/操作步驟；能追出 authenticated route 就提供 state/packet chain；追不出就明列「找不到原生可達性」及所查位置，不可把匿名 C02 當 Account owner。它**不是**研究原服怎麼驗證管理員預建帳號的 DB。

**資源**：目前已有 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat`。A-027/020/022 不需要新檔案；若需 Script 依賴再指定缺件 `PaperDialog.dat`。
