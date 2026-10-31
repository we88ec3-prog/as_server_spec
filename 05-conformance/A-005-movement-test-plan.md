# A-005：碰撞／移動校正 Client I/O 驗收（CT-056、CT-057）

與 [A-005 BIN-first 報告](../task_a/roy2/A-005-analysis.md)、[MAP 旗標統計](../task_a/roy2/A-005-corpus-flags.json) 同一原 Client SHA。依 A-XX 交接標準，已證 Client 構造與解析、Server 自訂防護及原生 Client 最終 CT 分開記錄。

## CT-056：原始原件／合成 decoded-body 測試

```
python task_a/roy2/a005_native_probe.py Asgard.exe
python task_a/roy2/a005_collision_probe.py --verify-original-sha Map0.dat Map1.dat Map2.dat
python -m unittest discover -s task_a/roy2 -p 'test_a005_move.py' -v
```

原始 7 個 native PE code pattern、494 MAP（7,701,805 tile）、10 個 synthetic unittest 已通過；`status=planned`, `offline_subset_result=PASS`, `native_client_validation=not-run`。須核對 C33 3×u8、C11 u8、S0B BE u16/u16/u8，以及 0x4B3520 原 MAP flags→17B tile，bit4 是 0x4B4BB0 線段檢查，bit0 另有動態 set/clear，**不可混為玩家通行 enum**。

## CT-057：原生遊戲 Client 校正與拒絕流程（未執行）

|實際情境|Client 送出|預期觀察／紀錄|
|---|---|---|
|正常一格移動|C33 direction,sequence,gait|S0B raw x/y/status_seq，畫面位置/動畫/再送包，確認 success high bit 和序號對照|
|撞牆／禁走座標|C33（不包含 x/y）|Server 安全拒絕及回 S0B 是否可將 Client 校回舊座標；具體失敗 high bit / UI 不可先宣稱已證|
|方向變更|C11 u8|自身轉向 vs 其他 Client S11 的作用範圍，方向 0..7 是否仍有其他條件|
|序號重送與環回|C33 的 0x7f 後 0x00、重播 0x7f|是否雙步、回包對應、延遲亂序 Client 效果；Server generation/epoch 是 designed 防重|
|過速、邊界、切圖、斷線|多 C33；跨 MAP S15/S14/C35|原版 S0B 拒絕/校正 GUI 與回復狀態；Server 不得超速越圖或套舊 instance|
|多人旁觀者|A 發 C33／C11，B 收 S06／S11|B 位置與方向跟隨更新；不能對 B 發 A 的自身 S0B 當第三人廣播|

對 `Map0.dat`、`Map1.dat`、`Map2.dat` 的 `flags` 只取得穩定可重跑的原件值與兩個原生 bit consumer，**尚無證據將 bit4 或 bit0 指定為角色平地唯一阻擋位元**。Server DEV 應以明確可測的碰撞 policy 起步並隔離於已證 raw flag 讀取；只有原生 Client 端成功/拒絕畫面與對應 BIN handler 才能標 `CT-057` 通過。測試來源不可含個資或遊戲素材。
