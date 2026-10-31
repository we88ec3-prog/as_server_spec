# A-005 native path／dynamic collision 原版驗收計畫

Static research ready，native Client GUI not-run；不能把 Python test 當 E2E。

|Case|測試|接受條件|
|---|---|---|
|P01|有無 destination flags bit0 (0/1/16/17)，無 actor/overlay|原生 local candidate gate 只在 bit0 有值時拒絕；不能推論 all-world passability|
|P02|來源 flags bit3 設置、source direction-byte 遮罩命中與未命中|0x4431E0 direction 與 mask 一致，命中拒絕|
|P03|raw flags0 動態 add bit0，raw flags1 動態 remove bit0|0x4C1850 overlay 區域可改變局部候選結果|
|P04|global bypass 與 0x4EA900()==1，各測|不混成 Server 登入/角色權限|
|P05|00006.map 五個 flags0 候選格，實際原版 Client 移動|只有 GUI、C33/S0B、位置都證明行走才標 PASSABLE_NATIVE_VERIFIED|
|P06|玩家/NPC 或臨時障礙存在及移除|實際 Native C33/S0B、actor lookup 和 overlay 對照|
|P07|斜角障礙、地圖邊界、重送/亂序 seq 及127→0|Server fail-closed，Native GUI 回滾與同步實際驗收|
|P08|原版兩玩家同圖，A移動/B觀察|A 的 S0B、B 的 S06/S11，不改錯權威持久位置|

逐例保留去敏 Client/Map SHA、map_ref、S15/S14/C35、S04 spawn/viewport、C33/C11/S0B、畫面及 Server trace。Native GUI not-run 的項目必須保持 planned。若是 native predicate evidence 錯回 A005；若 Server 速度/同步/權威錯交 DEV，原版實機結果交 CT。
