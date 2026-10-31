# A-006 原生外觀、置中、獨立染色驗收表

必須先區分 **CT-058 離線已證子集** 和 **CT-059 原生 Client 端到端**；研究可先交接，不等待 Server 新功能全部完成。原始 Client SHA256 `db3df616...`；不修改 Client。

|場景|Client 操作/觸發|收/送封包|預期與需記錄的觀察|驗收類型|
|---|---|---|---|---|
|角色站立置中|合法世界 S04，切 viewport(8,9)、(9,9) 對照|S04 4×BE u16|8/9=(400,300) 錨點；9/9=(448,300)；世界座標不變|CT-058 合成公式，CT-059 真截圖|
|八向移動|按 0..7 八方向各 5 格|C33, S0B；另一玩家 S06/S11|角色仍以既定 pane 錨點定位；8 方向/動畫 frame 正確；錄 raw seq/方向，不能假設 8 向圖檔已解|CT-059 原生|
|獨立髮色|保持衣色 2878c8，只調髮色 e66030→其他|C04（僅創角階段）；S05、S33|hair RGB 改；衣色 bytes、衣服染色層不應變|CT-058 合成，CT-059 原生|
|獨立衣色|保持髮色 e66030，衣色從自訂變預設|裝備候選 C1C/S37；S05/S33|S05 flags 0x1000/0 的 29B profile 切換；默认 ff00ff；原色 sentinel/近黑對照|CT-058 合成，CT-059 原生|
|自己及他人一致|A 換衣、B 同地圖觀看|S05 self、S33 other（具體發送時序未證）|同衣服、髮型、色彩；同 object ID，B 不變成 A；截圖並保存去識別 hex|CT-059|
|跨地圖、重登入|先更衣染髮，再切圖、斷線重登|S14/S15/C35/S04/S05/S33|不亂用上一張圖的 S33；外觀是否持久及發送順序由 Server 實際 trace 證明|CT-059|
|錯誤/異常|錯誤 flags、長度、CP950、未知資源 id|禁止用猜測可選欄位喂原 Client|合成 parser fail-closed，不進入 native 黑盒不安全測試；CT-059 只用合法輸入|CT-058/059|

重跑：`python task_a/roy2/a006_look_probe.py Asgard.exe`；`python -m unittest discover -s task_a/roy2 -p test_a006_look.py -v`。13 處原件靜態特徵和 10 項合成測試 PASS。**CT-058/059 都保留 planned/native-not-run；offline subset PASS 不能冒充原生 UI 驗收**。

需要記錄：Client SHA、S04 x/y/vx/vy、S05/S33 flags、hair/clothing RGB、CP950 名稱、角色 A/B ID 與 map epoch（去識別）、8 向截圖、站立與移動影格、服裝切換前後。若實際顯示失敗，再回交 A-006 解析 renderer/YPF/DOI 或 DEV Server 相容回包問題。未用到任何原始美術素材，且不將它們放 Git。
