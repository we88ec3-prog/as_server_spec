# A-005 / DEV-ENTRY-05：原版行走與 S0B 原生驗收計畫

目前 native Client GUI/封包 **not-run**，離線 x86 xref 13 條、instruction windows 15 組、合成 tests 5 項 PASS 不等於 Client 實測。使用未修改原版 Asgard.exe 和 hash-pinned MAP，必須先通過 World map 的 S15/S14/C35。

|Case|原版 Client trigger|Server / 原生觀察|判準|
|---|---|---|---|
|M01|有效地面前進一格 C33(seq5)|S0B(x,y,0x85)，與本地預測位置一致|畫面/位置/下一個 C33 一致|
|M02|已證阻擋處嘗試前進|S0B(舊 x/y,0x05) 為候選回覆|原版 GUI 接受並在原位置停止路徑|
|M03|C33 已做本地預測，但 S0B bit7=1 回另一合法位置|S0B seq 相符、位置不符|Client 0x5588DC 修正並可繼續|
|M04|C33 seq127 然後0；另測 seq mismatch|S0B 0xFF、0x80、亂序 0xFE|只接受符合本地 next 的回覆，不能重複移動|
|M05|錯 map_rev/C35、未通過 World 授權、斷線舊 epoch|任何 C33/C11 皆不得變更權威位置|fail-closed，不泄露帳號/角色|
|M06|Map0 00006.map 在 tile (30,30)→(30,31)→(30,32)→(31,32)→(32,32)|逐步擷取 C33/S0B/G​UI 與碰撞、S04/面向|實際通過後才可標 PASSABLE_NATIVE_VERIFIED；flags=0 不算證據|
|M07|同圖兩 Client，A 移動和轉向、B 觀察|A 的 S0B、B 的 S06/S11|兩個帳號/位置不交叉污染|

逐例保存去識別 Client SHA、map_ref、archive SHA、S14/C35、S04 四欄、C33 三 byte、C11、S0B 5 byte、epoch/trace、畫面/撞牆前後座標。若 Client tile 使用規則不明交 A005 查 0x4C1850/0x4BE470；Server 座標/序號錯交 DEV；原生 GUI 的結果交 CT-109/CT-071/072。禁止將本測試計畫標記 passed。
