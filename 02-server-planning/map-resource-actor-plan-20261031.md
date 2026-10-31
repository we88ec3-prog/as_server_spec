# Server 需求下一輪：從合法地圖到多人 NPC、新手教學及交易

本計畫參考 [Roy1+Roy2 經原件驗證的合併報告](../04-analysis-integration/merge-review-roy1-roy2-20261031.md)，是**Server 規格及開發交接**，不宣稱私有 Server 已實作、官方原服政策已還原或原始 Client 完成驗收。

## DEV-060 / ONB-03：嚴格地圖內容與 TileQuery（最高優先可實作）

- 由 `(client_profile,map_archive_sha,map_ref,revision)` 唯一定位地圖，解析必須 `LEu32 slots`、從 `4+36*n` 第一資料、每個36B `u32LE start + name32` 和末端 sentinel EOF。Map0 288 + Map1 184 + Map2 22 = **494** 張都可嚴格讀取，原件 7,701,805 tile。
- `TileQuery(x,y)` 僅在 map 實際存在、revision/hash 正確及 `0<=x<width,0<=y<height` 時回傳 10B原始 tile/flags/座標狀態；無負值/溢位/惡意長度接受。可以回答「這是圖內哪一格」，**不能回答「玩家一定可走或可出生」**。
- 顯示坐標像素 48×32 只作候選 view transform；bit0 runtime、bit4 line test、aux 4B grid 拆開，不能統一成 CanWalk mask。原版真正 C33/S0B 格距/回滾與 C35 第二欄 checksum 都有 Client evidence gap；正式 native map traversal 對未知配置 fail closed。原始出生點也不能用 Born(31,29) 推定。

## DEV-070-M / ONB-05：一張共用地圖的玩家與怪物

- `SharedMapKey(world_id,map_ref,content_revision)` **只有一份** NPC/怪物 registry/tick，所有進同地圖的人看到相同怪物死亡／重生；玩家各自有 Session、Observer、QuestProgress 和腳本上下文。A 斷線不重置 B 的怪物。
- `ValidatedMove` 驗 Auth/Session generation、同 world/map/revision、合理距離/速度、幾何 bounds 和已有 native-verified 或明確批准的碰撞資料後才修改權威位置；`Observe` 不得改玩家位置；跨圖/過期包一律拒絕。
- Player S33/S06/S11、Monster/NPC S07/S0C/S64、S5F death 和 S0E remove 的已證分支可先做 decoded-body codec；ObjectRef vs Server EntityId vs ClientImageID vs Monster archive 10 slots vs YPF member5 是不同 namespace。未知 kind、動畫或 NPC click/UI 不編造原生輸出。
- 以 CT-055/070/080..086 開發共享場景/雙原 Client 可見性回歸（原生測試尚未做）。

## DEV-090 / ONB-05～06：初級學校選擇不等於畢業

- `nNewJoin01.dat` 的 `STATE=ACCEPT/REFUSE` 與 `PaperDialog02.dat` 的 `PAPER02=START/NOT` 各在自己的 ScriptRun/context/character/epoch 保持冪等；入學選擇只是 AdmissionIntent。
- 必須先證 NPC entity→script binding、合法 map/spawn、原版 Client 的載圖/完成事件與出口，再行授權進圖/完成/發獎；不把 `C6C` script close 或接受按鈕誤算教學完成。

## R-014 / Economy：已可並行的交易安全領域（初步）

- A-013 可提供 C4A/S42 Exchange、C39/S2F Merchant、C17/S6E Trade 的**原版有限 serializer/reader 子集**；新 Server 可以先有 Inventory/Wallet/OfferLedger，雙方同一份交易狀態、準備／確認版本、金錢/道具一次性原子提交、重試冪等與過期/斷線取消。
- **未知且禁止硬編**：原版 TradeDialog 點哪個按鈕送 type、商店價目/貨幣上限、Exchange 是否倉庫、S42/S6E 的 UI 結果與原服政策。只有官方 GUI/封包觀測可開 native shop/trade。CT-087～089 分開離線/原生，不把 Server-designed ledger 當原版協定。
- 此迭代不要求先決定商店售價、手續費、怪物掉落率；這些是後續需求方決策而非從 Client 類別名稱推測。

## 保留的 P0 原則

- 帳號只能管理員建，**遊戲密碼4～8字**、Admin key獨立，私有 Server DEV-030 仍需同步修改；不修改 `Asgard.exe`，未來若另行批准新版 Client，才擴大密碼字數。
- 沒有驗證身份的 C02/新角色申請一律 fail closed；無法用匿名字串認領管理預建 Account。
- MAP 原件能讀取 ≠ 可登入原版新手圖、可行走或同圖多人實機已通過。所有相關原版 Client CT 繼續 not-run。

**下一輪分析重點**：A-022 C35 每張 MAP 第二個 checksum、A-005/A-015 Client C33→碰壁→S0B、A-011/A-024 實際 imageID→YPF/motion→NPC點擊、A-013 C17/S6E 交易 UI 動作，A-027 空角建立入口。現有原件已足供下游離線研究，新的資源檔應按確切引用再要。
