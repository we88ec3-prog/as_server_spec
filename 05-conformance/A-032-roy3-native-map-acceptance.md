# A-032 Roy3 CT-108/109 原版 MAP 入場與實際行走驗收

**native original Client GUI/TCP = not-run。** 494 MAP 原件 checksum 靜態計算 PASS，不可當本案玩家實際可操作。

|case|原版實驗|通過所需原生證據|
|---|---|---|
|M01|真 Server World loading 指定 S15 map_ref=6 或已確認真 tutorial map|原版 map_ref/Map member SHA、初始畫面與 Client S14 subtype|
|M02|S14(1) 觸發 C35|原版 decoded C35 完整4 bytes，map_ref6初始理論值00040F90；同 epoch/版本比對|
|M03|S15 map_ref10000 與 map_ref6 均得到同一 C35 值|Server pending identity 區分 mapRef與generation，不可由 C35 反推圖|
|M04|S04四欄座標與 S33 玩家|原版 GUI 可視地圖、合法出生 x/y、viewport x/y、方向/動作，不能借用原生未驗的(30,30)|
|M05|沿五格 raw flags0 候選路徑走路|Client C33/C11、S0B接受/rollback 和每步 native座標，原生 walking 需實錄|
|M06|撞牆、斜角、動態物件|真 Client 回滾與方向遮罩/overlay/object collision，不能 raw bit0 判通行|
|M07|重複S15、舊C35、斷線重連、同值不同 mapref|Server不因同C35值而跑錯地圖或放舊會話|
|M08|CRC/版本錯誤、未知mapRef|fail-closed，不接受任意checksum|
|M09|Map1/Map2 代表性樣本|10000重複值、18001包含7/8/16 tail、20001混合tail，確認原生載圖一致|

每例保存原始 SHA、去敏 S15/S14/C35/World C10/Session generation、S04、facing、C33/C11/S0B、GUI 動畫／截圖、TCP ordinal/seed。不得公開帳密/Token。完成每個 Native case 才標原版 E2E pass，現在全部 not-run。
