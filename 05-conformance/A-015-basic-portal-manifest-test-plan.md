# A-015 原件 Portal / FileSizeInfo 增量 CT（2026-11-01）

來源：03-analysis-requests/A-015-roy1-basic-portal-manifest-20261101.md；原始資產不入 Git。

|CT|已證離線|尚需原版 Client / Server|
|---|---|---|
|CT-039 / CT-090|Basic.dat 38 個成員、Portals.tbl 2840 三元組（312 MAP）；全數在 494 張原件 MAP 的正確地圖範圍；FileSizeInfo.txt 416 個檔案與三份 MAP 大小符合。13/13 新 tests PASS。|官方同版 release manifest、其他資源定義仍缺|
|CT-040 / CT-108|跨庫 map_ref 與座標可解析；A032 另外有 native-static C35 公式。|S15/S14/C35/S04 實際進圖、實際 Portal callback/回覆與出生點|
|CT-091 / CT-109|A005 本地 path predicate 為 native-static；這不證明任何 Portal 坐標 player_walkable。|原版 C33/S0B 成功移動、碰壁回滾、dynamic collision|

原始原件離線檢查：

    python tools/a015_portal_manifest_probe.py --basic Basic.dat --map-dir . --verify-original-sha
    python -m unittest discover -s tools -p 'test_a015_portal_manifest_probe.py' -v

注意：CT-040、CT-091、CT-108、CT-109 仍 planned/not-run。不要因 Portal 名稱、座標 in-bounds 或原始 flag=0 就授權伺服器出生／傳送／任務完成；也不要盲發錯誤 C35／不明 S44。
