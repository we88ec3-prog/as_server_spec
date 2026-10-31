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

## 2026-10-31 需求更正：不要再要求 C03→NewUser 為獨立創角前置

使用者觀察登入與創角為獨立 UI。更新 A-027 核查項目：直接操作 NewUser→C02 field1+field2 與管理員預建 Account/name/password 的原始 UI/封包對應；追錯密／未知帳號的 S02 非零回覆如何顯示，且 C02(成功)→C04 final 行為。**不應為了規劃要求先登入 C03 才能創角。** 新增 **A-029**：定位原版更改密碼 UI→C2S native opcode/field→S2C reply/Client UI，提供 VA/字串/狀態與負面 case；未查出前標 unknown。現有 `Asgard.exe` 已提供，沒有新增已確認缺件。見 [三入口正式需求](../02-server-planning/three-native-account-entry-policy.md)。

## 三項新決策的 Client 追查方向（2026-10-31）

1. A-027/028：直接 NewUser（無 C03）C02 帳密/錯誤 UI；不用追一個必須先登入才有的 Guard。注意 Server `CreationAuthProof` 是設計而非原版封包 token。
2. A-014：Party/Group 的 native 成員/變更 Client 包和 UI（目前 C12/C2E/S58/S3A partial）；A-009/025 怪物 hit/death 的 Client 可觀察 UI；A-007/013 經驗/掉落顯示/領取。**隊伍獎勵分配屬 Server designed，不要求原服 Server 原始碼**。
3. A-012/023/026：招募 NPC click→`nNewJoin01` Script→C6C(1) `STATE=REFUSE` 的 native 選項反應與再點擊；Server 拒絕入學 no-op，不假設 UI 自己有持久拒絕旗標。現有資源 `Asgard.exe`、`nNewJoin01.dat`、`PaperDialog.dat` 已提供，缺少其他具名檔案目前無新證據。

## A-030 創角斷線定點補證（2026-10-31）

關鍵已證：Server LoginWireSession.HandleAsync C02/C04 對任何 body 都立即 Close()，經 TCP Host 退出並關 socket；不等於帳密錯。**Client 實際是否發 C02、在哪條 socket 斷仍要查**。A-030 請按 existing A-021/027/028/020 已證址追 ID/PASSWORD/CONFIRM/NAME/E-MAIL UI widget、地域欄位(3 strings 或4+flag)、region1 差異、EMAIL 空字串 gate、非 region0 第一欄 min12、S02 非零 status/message→focus/C15/重試，並追 C04 成功後的原生回 Login UI。只接受遮罩後的 opcode/len/VA/Client UI；不能猜 S02 錯誤碼。見 [A-030](A-030-native-newuser-disconnect-fields.md)。
