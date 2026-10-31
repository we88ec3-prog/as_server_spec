# A-015 / roy1 — Basic.dat Portal／檔案版本盤點補證（2026-11-01）

## 研究範圍與目前狀態

延續 task_a/roy2/A-015-closure-review.md 的 R-016、SYS-CONTENT 原件格式／資源來源／分享權限研究；工作分支維持 task_a/roy1，沒有另開分支。A-015 的 bounded scope 已 integrated、handoff=ready，但「原版玩家可以走／出生／傳送」不包含於這個完成範圍。此次不改 Asgard.exe，不提交私有 DAT/MAP、完整 Portal 座標表或遊戲素材。

## 新取得的原件依據

|檔案|bytes|SHA256|
|---|---:|---|
|Asgard.exe|3235840|db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145|
|Basic.dat|5282488|0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96|
|Map0.dat|44863691|dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761|
|Map1.dat|30817997|8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b|
|Map2.dat|3856650|5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb|

Basic.dat 以 LEu32 slot_count 及每格 LEu32 offset + raw name[32] 索引，38 個資源成員加一個 EOF sentinel。Map0、Map1、Map2 以相同檔案身分核對 288+184+22=494 張 MAP，內部 10-byte raw tile、三個尾段、完整 EOF；此為 observed-original-resource。

## Portals.tbl — 候選的 map_ref / x / y 關聯

Basic.dat 內的 Portals.tbl 是 17,046 bytes，SHA256 b63c4f07765271baf83c9a5104fafe21070e2e3ca7926aec23c17eda84047d00。解碼 header：LEu16 version=1；LEu32 count=2840；其餘 2840 筆，每筆 6 bytes，依序三個 LEu16。若將其解釋為 map_ref / tile_x / tile_y，與真 MAP 對照的交叉驗證結果如下：

|觀測|結果|
|---|---:|
|record rows / 唯一三元組|2840 / 2840|
|不同 map_ref|312|
|Map0 / Map1 / Map2 筆數|1500 / 1170 / 170|
|指向不存在 map_ref|0|
|x/y 越出 MAP width/height|0|
|三元組所在 raw tile flags=0 / 1 / 17|2837 / 1 / 2|

原始檔案位置及二進位結構屬 observed-resource。這些三元組是地圖上存在且 in-bounds 的 **座標候選**，並非已追到 EXE 的 Portal 消費函式；Portals.tbl 名稱只能支持用途假說。**不可稱 2,840 點均為原版傳送點、原服出生點或 player_walkable**，尤其有三筆 raw flags 不是零；即使 flags=0 仍可能受 A005 動態遮罩/物件/方向限制。

## FileSizeInfo.txt — 版本配對強化與不可解的第三欄

Basic.dat 內 FileSizeInfo.txt 是 24,648 bytes，SHA256 43a46e680e445dfb4fb4a63fcfefa3aadc763f01827a209cac8b3ba51ba06e0c；UTF-16LE BOM，416 個無重複列。每列三欄：檔名、十進位數值一、十進位數值二。真實 MAP 三筆：

|檔名|數值一|本次真實檔案大小|數值二|
|---|---:|---:|---:|
|Map0.dat|44863691|44863691|63117|
|Map1.dat|30817997|30817997|24085|
|Map2.dat|3856650|3856650|37444|

數值一對 Map0/1/2 實際 byte length 全部吻合，提升 Basic 與 MAP 的資料配對可信度。但**只有 size match，沒有官方 release manifest**；不能宣稱官方發行版本已確認。數值二演算法尚不明，不能稱它等於原生 C35 checksum、CRC16、CRC32 或 SHA。其他 413 個檔案未因出現在名單就被宣稱原件已取得。

## 跨 A 工作交接

- task_a/roy3/A-005-native-path-collision-closure.md 已有 EXE native-static 局部判定：目的地 bit0、source direction mask、動態 overlay、物件 lookup 不可與只看 raw MAP 的 flag=0 合併成原生 passable。
- task_a/roy3/A-032-roy3-native-map-c35.md 已另外證明 C35 第二欄採原生 MapData structured checksum（非 raw MAP CRC），並重算 map_ref=6 的理論 C35 body 00040F90；它仍缺原版 GUI/TCP 實測，和本次 FileSizeInfo 第二數值不能混淆。
- Server 可實作嚴格 DAT/MAP 基礎解析、Portal 候選 metadata 對照和資料版本守門，但原服傳送／進圖策略、正式合法出生、玩家路徑、NPC/Quest/Reward、技能物品定義表與外觀動作映射等都不能由本表授權。A015 的格式／來源範圍完成，不等於全原服遊戲內容可開發。

## 重現與測試

在本機放置合法持有的原件，於 repo 根目錄執行：

    python tools/a015_portal_manifest_probe.py --basic Basic.dat --map-dir . --verify-original-sha
    python -m unittest discover -s tools -p 'test_a015_portal_manifest_probe.py' -v

原件 4 DAT（Basic + Map0/1/2） SHA/結構交叉驗證通過；新增 13/13 Python 測試包含原件回歸及格式壞檔、越界、重複、版本錯誤等離線拒絕案例。程式只輸出 SHA 與 aggregate，不輸出原始 MAP、全量 Portal tuple。缺原件時原件回歸為 SKIP，不得報原生 PASS。

結論：A-015 bounded handoff=ready，native_client_validation=not-run，release_match_to_client=unverified，implementation_ready=false（全遊戲素材、玩家出生／走路／傳送權威仍非就緒）。本輪**沒有缺少原件**；若需確認 Portal 原生語意及玩家行走，缺的是實際 Windows 原版 Client 的互動畫面、雙向封包 trace 和消費函式 XREF，而不是再次上傳 Map0/1/2 或 Basic.dat。
