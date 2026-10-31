# A-005／roy2 — 移動、地圖位元、碰撞判斷與校正：Client BIN-first 交付

**日期**：2026-10-31。**唯一作業分支**：`task_a/roy2`，工作目錄 `task_a/roy2/`。系統 SYS-MOVE／R-005、SCN-002。原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`（PE32 ImageBase 0x400000），三個原始 Map DAT SHA 見下表；原始遊戲資產**沒有**上傳 Git。

## 研究結論（四類證據不得混淆）

- **observed-static Client**：C33 動作 Body 是 3×u8；C11 轉向 1×u8；S0B 校正 Body 是 BE u16 x、BE u16 y、u8 狀態/序號。已沿 native writer/reader 位址重新核對。3 條操作流程的 UI producer、失敗時重試節點並沒有完整 native handler 連結。
- **observed-static MAP**：`0x4B3520..0x4B355C` 將原始每格 `3×LE u16 + LE u32 flags`（10B）的旗標直接複製到 Client **17B 內部 tile 的 +6 u32**；`0x4B2C80` 以 `17*(x+y*width)` 取此 tile。`0x4B2CA0` 動態 set/clear bit0；`0x4B4BB0` 一條跨格線檢查使用 bit4/0x10；`0x4D1206` 在另一條路徑測 bit0/0x01。**沒有足夠證據把其中一個 bit 宣告成角色移動的唯一可通行判定**。
- **observed-static-resource**：原始 `Map0.dat/Map1.dat/Map2.dat` 全 494 MAP、7,701,805 格已跑完整索引／tile／尾段、EOF 校驗，旗標唯一完整 u32 值為 **0、1、16、17、512**，相同 profile 內各庫分布詳下。
- **designed（非原服）**：認證 session、序號 modulo 128、map epoch、速度／碰撞拒絕、最小步距、碰撞策略由 Server 明確決定，舊訊息和重送不得導致雙重移動。原版速度 tick 時間、方向→座標增量、位元旗標完整語意皆仍未知；不能把可執行的 synthetic gate 當成原生 Server 政策。

## 1. 操作→封包→Client 解析／反應

|Trigger/狀態|Client C→S|Server S→C（Client 原生 parser）|Client 效果與缺口|
|---|---|---|---|
|已入 World 玩家移動操作，真正按鍵/搖桿 dispatch 待追|**C33** writer `0x573BF0`：`direction:u8,sequence:u8,gait_flags:u8`；3 次 `0x45AB00` writer，原始類別 constructor push 0x33|**S0B** parser `0x583150`：`x:BE u16,y:BE u16,status_sequence:u8`（native `0x45ADE0`×2，`0x45ADB0`×1）|前 4 bytes 可提供位置更新/校正；最後 u8 的 bit7=success、低7 bit=sequence 是既有 profile/CT-004 證據，與 0x7F→0x00 wrap 對照。**原生 GUI 失敗/回滾/碰撞效果未跑**|
|本地玩家轉向|**C11** `0x571960`：`direction:u8`，native `0x45AB00`|可見他人的 **S11** `BE u32,u8`，自己的 S0B 不是轉向 ACK 的等價物|C11 的所有原服回覆分支未知，動作是否 local optimistic 未完整反編|
|移動後其他人可見|本玩家 C33／C11 |其他 Client 可收 **S06** `BE u32,u16,u16`、**S11** `BE u32,u8`；S33 用於人型初次顯示|A-004 指出 S0B **沒有**第三方 ID，不能直接把自身 S0B 廣播為遠端移動封包；u32→ObjectRegistry 查找仍未完全還原|
|Server 拒絕非法/過快/阻擋移動|C33 只有 3×u8，**沒有 Client 傳入座標、地圖 ID、速度或時間戳**|依既有 profile 可構造 S0B `BE u16 authoritative x/y + u8 status_sequence`；例如既有 CT-004 正常 `C33 01 7f 01 → S0B 000b000aff`|被拒絕時的**精確 native bit7/序號/失敗 UI**及是否立即重試仍待 handler 路徑證明，故「失敗 S0B 回原座標並清 bit7」只能是 **designed** 測試提案，不可標 observed native|

**序號與重送**：C33 第二 byte 的低7位及 S0B 後 byte 的低7位是既有 A-016/CT-004 對應 profile，原 native writer 只證 byte 寫入，沒有原版 Server exactly-once/request-id。解碼器保留 raw u8/highbit；Server 以 epoch/generation 和單步 outbox 做防重策略（designed）。在既有測試中 `0x7F→0x00` 是候選環回；速度與 gait 未知，不能硬編毫秒值。

## 2. MAP 原生載入 + tile 旗標真實語料

原始地圖外部每格 10 bytes，`0x4B3520..0x4B355C` 每格 copy `LE u16,u16,u16,u32` 至 stride=17 的 native 結構，`0x4B2C80` 回傳 `base+17*(x+y*width)`。`0x4B2CA0` 在該 17B 記錄 `+6` 的 u32 設/清 **bit0**，說明 Client 有動態位元運算；`0x4B4BB0` (0x4B4BEB,0x4B4C8B,0x4B4D2D) 使用 `bl=0x10`，三處 `test byte [eax+6],bl` 檢查跨格/線段上的 **bit4**，可識別線段遇旗標的 native test，但它不必然等於一般角色平地「能否走過」規則。`0x4D1206..0x4D120F` 在另一條 Map grid 遍歷以 `test [tile+6],1` 判斷 bit0，並有 `0x4B2D00` 另一個鄰格條件路徑。這些是不同的 consumer，**不可把 bit0、bit4 或 0x200 混成同一碰撞 enum**。

|原始資產（SHA256 前綴）|MAP數|總tile|flags=0|flags=1|flags=16|flags=17|flags=512|
|---|---:|---:|---:|---:|---:|---:|---:|
|Map0.dat (dcaf8ab5)|288|4,347,940|1,567,556|364,583|8|2,415,331|462|
|Map1.dat (8681dc75)|184|2,983,365|997,116|109,919|1|1,876,319|10|
|Map2.dat (5320a095)|22|370,500|136,628|22,375|3|211,494|0|
|**合計**|**494**|**7,701,805**|**2,701,300**|**496,877**|**12**|**4,503,144**|**472**|

`flags=512` 的 472 格只在 Map0/Map1；若只統計 flags 低位元組會把它錯算到 0，故應以完整 **LE u32** 統計。A-005 研究是直接使用既有 Map0/1/2 原件，不需再次提供大量地圖／圖像。**有旗標值不代表它是原生玩家碰撞**；沒有確定原服地圖選擇、map_id/出生點／版本配對，就不能宣稱某一張確定是教程碰撞地圖。

## 3. 供 Server 採用的負向案例（均 designed，不能推論原服策略）

1. **正常**：world session 有效、方向 0..7、下一序號、Server 判定碰撞/速度合法後，更新權威座標並回 S0B；其他玩家走 S06/S11。方向的 0..7 和每次最多 1 tile 只作本 profile 安全模型，**不是已證原版最大速度**。
2. **阻擋**：Server 採自己有明確來源的 collision policy；拒絕時維持舊座標，不改 durable position；產生對應原生 S0B 的**候選**校正，Native GUI 尚待測。不得以 bit4（觀測於線段遮擋）無條件代表角色阻擋。
3. **越界**：未載入／負座標／超出 selected MAP width,height、未通過 map checksum/version 或不相容 instance：拒絕、不轉移 epoch。
4. **過速**：Client C33 沒有絕對座標與 timestamp；Server 按自己的 tick / 最短間隔 / 合法步幅判定並保存監控，沒有原始 speed-ms 證據。
5. **重複、亂序與環回**：示例 sequence 127 後 0；同一 session 重送 127 不二次移動；不同 generation 0 不等於舊連線重送。
6. **斷線/切服**：撤銷舊 map epoch 的 C33 outbox/路徑事件；不得以原生無 request-id 的 C33 保證跨 Server exactly-once；必要時 Server 做單連線最小重播護欄。
7. **MAP 損壞**：資料檔 index 未對齊、tile/7/8/16 尾段截斷、EOF 不符、版本 SHA 不符全部 fail closed；不根據壞地圖任意放行碰撞。

## 4. 可重跑工具與交付 gate

```sh
python task_a/roy2/a005_native_probe.py Asgard.exe
python task_a/roy2/a005_collision_probe.py --verify-original-sha Map0.dat Map1.dat Map2.dat
python -m unittest discover -s task_a/roy2 -p 'test_a005_move.py' -v
```

**已獨立跑過**原始 EXE static pattern 7 組 PASS、494 MAP / 7,701,805 tile metadata+tail 校驗 PASS、10 項合成 codec/設計護欄 unittest PASS。工具只輸出原件 SHA、資料統計和原生 VA，不導出任何遊戲素材。需明確說明：合成 Server 安全 gate 不是原版 Client GUI E2E，也非原版 Server 地圖通行權威規則。

後續原生驗收 **CT-056（離線資料/decoded body）**、**CT-057（native movement reject/correction）** 應保留 `planned / native-client-validation=not-run`；A-005 研究證據 `A005-E01..E08`。**交接狀態 `integrated / partial`**：已知 Client movement/turn/ack codec、MAP 旗標來源與本版位元 consumer 可交 DEV，未知「角色走路精確碰撞 mask、UI 回滾、原版速度與 handler」尚未補齊；不可將已證靜態子集說成原版碰撞規則 fully recovered。

缺件：**沒有新的必需檔名**。提供的 `Asgard.exe` 和 `Map0.dat`～`Map2.dat` 已足以完成這輪靜態研究；要提高原生碰撞交付完整度，需同版原生 Client 的移動成功／撞牆／回滾封包與畫面 trace 或更深入 MapPane handler 逆向，非大量美術檔。
