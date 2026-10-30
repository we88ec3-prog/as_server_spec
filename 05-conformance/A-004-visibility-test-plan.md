# A-004 → CT-054 / CT-055 多玩家視野與 ID 生命週期驗收

此計畫根據 `Asgard.exe` SHA256 `db3df616...` 的原生 constructor/reader static evidence；兩台原生 Client E2E 尚未執行。研究與 Server 設計清楚分離。相關 [`A-004` 報告](../task_a/roy2/A-004-analysis.md)、[`a004_native_probe.py`](../task_a/roy2/a004_native_probe.py)、[`a004_visibility.py`](../task_a/roy2/a004_visibility.py)。

## CT-054 — metadata-only 原生 EXE 靜態核對及合成解碼

```
python task_a/roy2/a004_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a004_visibility.py' -v
```

已在原件核對：5 native ctor + 5 native reader 序列 PASS。9 synthetic cases PASS，含 CP950 的 S33 flags0 變體、S06(u32/u16/u16)、S11(u32/u8)、S0E(u32)、S0B(u16/u16/u8) 完整長度，錯誤的 length/string8/flags、重送/ID 重用與舊 epoch 防護。這些數據不代表原生 Client GUI 或 Server 視野回覆真實成功；整體 CT-054 `planned`，offline subset 通過。

## CT-055 — 兩台原生 Client，必須真實檢驗

|事件|應擷取的 C→S / S→C（預期候選）|驗收畫面/紀錄|
|---|---|---|
|Client A 入 map instance，B 後入場|B 到場後 A 收第三方 S33；B 收 A 的 S33；自身 S04/S0B 不可冒充他人|兩邊可看見名字/外觀/相對座標，記原始封包 opcode/hex（去個資）|
|A 移動/轉向|A C33/C11、A S0B，B S06/S11 可能|畫面遠端 A 位置及方向確實更新；S06/S11 的 u32 與 S33 id 對照|
|A 離開可見範圍|B 的 S0E 候選|B 不再渲染 A；需確認真 native ObjectRegistry 受 S0E 影響|
|A 斷線/重新登入|新 A 的 S33、舊 A 的 S0E 或 world reset|舊影消失、重登一次，沒有誤認成別人；看實際 ID 是否重用|
|A/B 切圖及跨 map instance|S14/S15/C35/S04 與 S33/S0E 交叉|兩地圖不互見，載圖未就緒不得先顯示其他 actor；新 epoch 不受舊廣播污染|
|失敗/重送/異常|錯序 S06/S11/S0E、重複 S33、name 截斷、非法 flags|Server 不得 crash/洩漏其他玩家；原 Client 對錯包行為不做危險注入假設|

**原版未證**：可見距離、裁切形狀、Server 選收件對象、斷線清除的原服 policy、native 人物 registry 的 u32 等價、S33 optional flags 分支、兩 Client 真正渲染。這些不得因離線測試通過直接標 `native_pass`；原服 Server 策略可由 DEV 自行設計，標記 `designed`。

## 回報與分工

CT 出錯需記 profile/Client SHA、world epoch、map_id、sender/observer ID 的去識別映射、sent/received decoded body、Client 畫面與錯誤，重新分配至 A-004 可觀察 handler 或 DEV visibility policy；不要求先完成新 Server 才能繼續 Client 靜態解析。原始遊戲程式與私人角色資料不可推送到共享 Git。
