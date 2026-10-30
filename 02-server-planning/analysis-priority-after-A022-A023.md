# A-022/A-023 合併後：Server 逆向分析執行順序（2026-10-31）

版本 `TW-seed0-local-v0.1`；Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。以管理員建立帳號、玩家僅用 Client 登入（R-025），目標為「登入 → 創角 → 原版教學可操作 → 完成教學」排序。**以下為優先建議，不是把原有 A 任務的 status 改成已完成，也不要求 A 研究者先把 Server 實機做出來。**

## 目前已取得的研究基線

- **A-021 integrated/partial**：C02 地區差異、C04 五 u8、S02 status/string 與 UI 0x1d→0x1e 已靜態覆核；C02 可在 C03 前出現，不能單憑聲稱的帳號字串認領預建帳號。
- **A-022 integrated/partial**：S15 3×u16+2×u8+string8、S14 控制碼、C35 header(+4)/structured checksum、MAP 16-byte 尾段與世界 Loading/epoch 策略可供 DEV 開發。**原版教學 map_id、出生點、正式 CRC expected pair 未知**。
- **A-023 integrated/partial**：C6C/S44 Script 分支和 S44 可能觸及本機 Script cache；Roy2 Born.dat 解析報告顯示 Main 打開 PaperDialog，文字要玩家前往 (31,29) 點女性招募員。**(31,29) 不是已驗證出生位置；首次自動觸發、NPC id、實際任務均未知**。此輪未取到 Born 原始 bytes 進行獨立重跑，版本配對未證。

## 優先順序及可並行工作

|隊列|工作|優先|必須解答的原生問題|解鎖的 DEV/CT|
|---|---|---|---|---|
|第一批（並行）|**A-027** 配合 A-003/A-020|P0|C02 pre-C03 身份／憑證哪裡來？如何證明管理員預建 Account 的合法 owner？空角原生 UI 怎麼進？|ONB-01/02、CT-030，禁止未授權 claim|
|第一批（並行）|**A-015**（回補 A-022 原生內容）|P0|與 EXE 可配對的實際 MAP/resource 版本、教學 map_id、出生 x/y/heading、MapData checksum、Script/NPC 定義來源？|ONB-03、CT-018、A-024 場景定位|
|第二批（可先靜態並行）|**A-028**|P0|C04 後 state0x1e 的 S02/錯誤、重登/transfer、角色原子提交時序？|ONB-02 完整建角、CT-032|
|第二批（平行支線）|**A-016** 與 A-022 補原生 MAP CRC/重連|P0|初入圖失敗、斷線、重送與內容版本不一致如何恢復？|ONB-03/04、CT-016/017；不需先有教學任務|
|第三批（並行）|**A-012** + A-023 殘餘 Born 觸發|P2（可依關鍵路徑提前）|哪個 event 觸發 Born.Main？S44/C6C 的真實 subtype/byte layout、紙張取消/再次觸發及任務 flag？|CT-033/034/035、ONB-05 的 Script/NPC|
|第三批（並行）|**A-011/A-024** 配合 A-004/A-005|P1|招募員的實際 NPC id/map/位置與第一批可見 NPC/怪物 spawn、行動、消失、互動？|ONB-05、CT-021/022|
|第四批|**A-025** 配合 A-008/009/010|P1|是否必需戰鬥？哪個技能/攻擊、目標、傷害、任務計數事件和回包？沒有則提出可重現反證|ONB-05、CT-023～025|
|第五批|**A-026** 配合 A-012/A-016|P1|原生教程完成觸發、獎勵唯一性、出口轉圖、重登恢復？|ONB-06、CT-026～028|

## 解析與開發並行，不混合成果級別

1. A-027 身份授權尚未證實時，開發只能解析 C02、作 domain-level Account/Character model，**不得**由 pre-auth C02 直接授權認領、寫角或發 grant。A-028 的狀態分析可開始，但原生 E2E 要遵守身份 gate。
2. 通用 S14/S15/C35/S04 和安全 Loading/重連可直接 DEV（只限已知 layout）；沒有資源就採明示 local-fixture，不能填猜測教學 map/spawn/CRC。
3. Born.Main 的導引目的地 (31,29) 不能替代出生點，也不推論一定要發 S44 或初始化 quest。因 S44 某分支涉及 Client Script 目錄操作，測試僅在可丟棄 sandbox。
4. 任何 A 任務以 `observed-static`／`observed-static-resource`／`inferred`／`designed`／`unknown` 分層交接；尚未驗證的內容維持 partial。每次新證據補 04/PKT/SCN 與對應 CT，失敗則發 DEV/分析修正；**不會因新 Server 未完成而停止進一步逆向**。
5. CT-029～032 保留 A-021/Auth/創角；CT-033～035 對應 A-023 C6C/S44、首次 Script/NPC、重送冪等；**全都尚未原生 Client E2E 驗收**。

## 最短關鍵路徑

`A-027 → A-028 → ONB-02 創角` 和 `A-015 → 真正 map/spawn → ONB-03 進圖` **兩條 P0 路徑並行**；兩條收斂後才可測真正「原 Client 新帳號進教學」。接續 `A-012/A-024 → A-025（若必須戰鬥） → A-026`，再以原生 Client 完成全教程驗收。

報告：[A-022](../03-analysis-requests/A-022-roy1-bin-analysis.md) / [A-023](../task_a/roy2/A-023-analysis.md) / [核對紀錄](../04-analysis-integration/A-022-A-023-merge-validation.md)。

## 2026-10-31 第二輪調整（以本節為最新，覆蓋前面未完成項）

- **A-001 已 integrated/partial**：seed 0..9 mask／binary XOR／C00/S00 初步解析交 DEV；A-020 不再重複這些已證項，改優先分析原生版本/region 的 seed/key 選擇、S00 非零結果 UI 與其餘 metadata。CT-036 保留為 synthetic codec（native not-run）。
- **A-023 Client 入口機制已解到 S44(1,0) → Main → C6C lifecycle**，不是「不知道如何觸發 Script」。**仍不知道原服何時／依何旗標送 Born**，以及女性招募員真正 entity/script/quest。A-012 接原服首次腳本排程和 quest，A-015 接原版資源版本/出生，A-024 接 NPC 實體綁定；將這三條可並行安排在 A-027/A-028 的帳號關鍵路徑外。
- **最高優先仍是 A-027 + A-015 並行，接 A-028**。同時可以開發 transport 通用 codec + S44/C6C Script 生命週期（受控 mock／安全測試）；不得把 Born 的文字座標 (31,29) 當出生點，也不得把 C6C2/4 當完成任務。
- 說「沒有 Script／MAP 資源」不精確：roy2 的本地研究已核對 Born/PaperDialog 以及 Script corpus，並報告存在 Map0/1/2 與 Basic；**目前欠缺的是版本配對和原服 NPC/任務綁定**。本次合併檢查環境沒有完整原始資源可供獨立再跑。

## A-027 交接後精準剩餘工作（2026-10-31）

A-027 已追完可核對的 C02 UI 欄位來源（field1 名稱候選；field2 密碼候選+確認控制）、本地長度/相等/region 檢查，但未能證明 pre-C03 Account owner 如何經原生 Server 認證，亦無 C03 無角色→MakeInfoDialog 的原生跳轉。**研究 A-027 integrated/handoff partial，但預建帳號認領路由禁止開發啟用**；後續拿 UI 真標籤／原服認證/失敗 evidence，或規劃別的原 Client 可達且具獨立身份驗證的安全入場方式。A-028 追 C04 後結果/commit，A-003 追合法角色；A-015 仍補原教程 map/spawn。詳見 [A-027](../03-analysis-requests/A-027-roy1-identity-ui-security.md)。

## A-016 交付進度（2026-10-31）

重送/崩潰恢復的 BIN-first 子集已整理成 [A-016](../03-analysis-requests/A-016-roy1-replay-recovery.md)；既有 C33/S0B/C35/S14/C10/C04/C15 的回覆邊界、同版 C35 無 epoch 的不可辨識性與 designed 的 durable commit/unique ledger/outbox 皆可交 DEV。研究 `integrated/handoff partial` 不等於原版 Server 的交易/Quest/登入恢復 policy 已證明，亦不解除 A-015 教程 map/spawn、A-027 帳號 owner 的必要資料條件。CT-043/044 planned，原版 Client not-run。
