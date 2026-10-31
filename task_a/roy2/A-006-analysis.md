# A-006／roy2 — 螢幕置中與獨立染色 Client I/O（BIN-first）

日期 2026-10-31；原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，PE32 ImageBase 0x400000。只使用既有 `task_a/roy2` 分支，不創新分支。R-006、SCN-004/005、CT-003/007/008。

## 判定及證據強度

**13 個原生指令特徵**直接從原始 EXE VA 核對 PASS（`a006_look_probe.py`）；**10 項合成測試** PASS（`test_a006_look.py`）。已交付 Client S05/S33/S04 解析欄位、可選 flags 的真正原生讀取分支、服裝與頭髮 RGB 的相互獨立性，及指定畫面 profile 的鏡頭錨點測試。**沒有以原生 Client 執行兩角色八向移動／換裝／切圖／重登的 GUI 截圖驗收**，故人工 CT 應保留 `not-run`。S05/S33 的原生 parser 可確證收了哪些欄位，不能由此單獨保證渲染層每個 YPF frame/染色遮罩已正確繪製。

## 操作 Trigger → C→S → S→C → Client 反應

|Client 事件（Trigger）|Client 送出的封包|原版 Client 接收|可證反應及缺口|
|---|---|---|---|
|NewUser UI 選擇性別、髮型、髮色|C04：`u8 sex,u8 hair,RGB3`，在 A-003/A-028 所證的 NewUser 第二階段|創角結果 S02；進 World 後依 profile 接 S05/S33|C04 只證初始外觀送包；Server 角色儲存和認證另屬 DEV，不得把 C04 當 World 換裝封包|
|穿衣／用物品|C1C UseInventory：`u8 kind,slot,flag,use_kind`，但裝備成功的完整 UI producer/尾欄尚待 A-008|S37 AddEquipment，及可能更新的 S05 自己外觀、S33 他人外觀|C1C 對哪件衣服何時產生 S05/S33 的原服對應未證；不能因 S37 存在宣稱必定刷外觀|
|Client 接 S05（SelfAppearance）|此事件本身不需要再送 C2S|S05 body 本 profile `29 bytes`（flags 0/0x1000）：offset0 BE u32 actor、4 sex、7..8 BE u16 cloth、9 hair、10..12 hair RGB、14..16/18..20 附件 RGB、21..24 BE u32 flags、25..27 cloth RGB、28 tail|原生 reader `0x5895A0`，髮色和衣色各讀三個獨立 bytes；`0x589674` 的 flags bit0 **另讀 3 bytes**，bit4 **另讀 u16**，bit1 **另讀 u8**，bit7 **另讀 u8**。所以 29B **不適用所有 flags**；`0x1000` 在此 reader 不觸發那些低位可選分支|
|Client 接 S33（PutHuman）|此事件本身不需要 C2S|flags=0 本 profile：`x:BE u16,y:BE u16,dir:u8,id:BE u32`，外觀 hair RGB offset15..17，服裝 RGB offset30..32，flags BE u32 offset26..29，CP950 名稱 string8 offset34，後接 7B profile tail；body=`42+名稱byte數`|reader `0x585570`；flags bit0/bit4/bit1/bit7 增加額外欄；flags bit13(`0x2000`) 附加第二組名稱／標籤資料；全部變體尚未驗證，不可用固定長度或固定 offset 的 decoder 解析任何 flags|
|收到位置／地圖包，更新鏡頭|沒有獨立被證實的鏡頭設定 C2S；先前 S15/S14/C35 地圖校驗有自己的協定|S04 `4×BE u16`: x,y,viewport_x,viewport_y；自身 S0B 更新位置；另一玩家 S33/S06|前述既有 profile 的 tile `48×32`、pane 偏移 `(-56,-36)`、viewport `912×672`：`viewport=(8,9)` 站立與移動錨點均為 **(400,300)**；`(9,9)` 站立 x=448。**這是原 native 公式與 profile 的投影推導，並非 GUI 截圖驗收**|
|八向移動、切圖、重登|C33/C11；切圖 C35 由既有 A-022|S04/S05/S33/S0B/S06/S11|A-006 靜態收發已知；連續八向動畫 frame/染色層、0/0x1000 flags 切換和重新登入 appearance restore 需要真 Client CT 驗證|

## BIN-first 重點及更正

- `0x5895A3` 先讀 S05 BE u32；`0x5895D...` 讀 base hair/clothing/三色群。flags 放 native packet local `[esi+0x2c]`；`0x589674 = test BYTE PTR [esi+2c], 01`，`0x589698` test 10h，`0x5896A9` test 02h，`0x5896B9` test sign bit，均為 **wire 可選欄位讀取**。
- `0x585573` S33 先 BE u16 x，`0x58557E` 再 BE u16 y；`0x585589` u8 direction，`0x585593` BE u32 actor。S33 `0x585667` bit0=額外三色 bytes，`0x58568B` bit4=額外 u16，`0x5856A4` bit1=額外 u8，`0x5856B4` bit7=額外 u8。名稱以 `0x5856DC→0x45B7A0` 讀 string8；`0x585719` test AH 0x20＝`0x2000` 有額外欄＋string8。**這些已知變體至少不能直接照 42+n 解**。
- `0x585780..0x5857F4` 對多組三原色進行 `000000→FF00FF` sentinel 正規化，只將群組第一和第三 bytes 改 FF。**不能由此宣稱所有黑色畫面不支援**；僅此 parser 對特定群組做轉換。原資料也可能使用 `FF00FF` 表達原色保留，須與 YPF 染色遮罩實測。
- Hair RGB 與 cloth RGB 是兩組不同 wire offset，不是同一全身 tint；S05 `flags=0x1000` 的衣色值屬此 profile 實作慣例，原生完整 renderer/mask 效果仍待 GUI 佐證。S33 的 flags=0 profile 同樣可以含獨立 hair/cloth bytes；不可照搬 S05 flags 邏輯。
- 預設組合 `Human\mb0%02d.dat`, `Human\wb0%02d.dat`, `Human\mh0%02d.dat`, `Human\wh0%02d.dat` 等是 EXE 路徑樣板；完整 8 向動作還要真 YPF/DOI frames 才可判定，**不需為了 A-006 的 Client wire 分析要求整包美術資源**。

## 可重跑與 DEV／CT 分界

```sh
python task_a/roy2/a006_look_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a006_look.py' -v
```

13 個原件 byte-pattern static check PASS；10 個 synthetic test PASS（S05 29B/旗標、S33 CP950 長度/flags、獨立染色、S04 8/9 中心與 9/9 偏移、非法值）。兩者均**不是** GUI 渲染證據。CT-058 為 offline 子集，CT-059 為原生站立/八向/換裝/切圖/重登雙角色截圖與 UI 錯誤驗收，兩個整體仍標 `planned`（native Client 未執行）。

**A-006：`integrated`；本輪 Client I/O 靜態研究 `handoff_status=ready`；`native_client_validation=not-run`**。此 scoped ready 不代表完整原生顯示功能已人工驗收。仍未知完整 optional flags、YPF/DOI 動作與 palette 染色遮罩的真實呈現、某些 C1C→S37/S05/S33 原服路由、重登入外觀持久化 Server 行為。若要把 CT-059 轉成通過，缺的不是新資源檔，而是**原生 Client 八向動作及雙角色外觀畫面／合法去識別封包 trace**；完整素材驗證才另需求 Human YPF/DOI 對應檔。
