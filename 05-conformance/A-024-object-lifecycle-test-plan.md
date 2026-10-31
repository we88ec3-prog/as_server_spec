# A-024 NPC／怪物原生 Client 收包鏈：驗證規範（CT-065/CT-066）

原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；唯一工作分支 `task_a/roy2`。此文件只檢查原版 Client 可讀取與投影哪些包；不假設原服怪物 AI、掉落、重生時間或官方 tutorial spawn 資料。

## CT-065：Original EXE 靜態驗證 + synthetic decoded-body（可離線跑）

```sh
python task_a/roy2/a024_object_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p "test_a024_object_packets.py" -v
python -m unittest discover -s task_a/roy2 -p "test_a024_npc_codec.py" -v
```

- Native probe：原始 EXE SHA 鎖定；20 native instruction bytes、S07 的 14 type 跳表及六個 MSVC RTTI 類別。**本輪原件檢查通過**。
- Synthetic scope：S07 count=0、多筆非空記錄、type 1/2/4 optional flags bit0/bit1/bit4、type3/5..12/13/14、CP950 string8 length bytes、row 總長度與截斷/未知 type/超量拒絕；S3C 7B、S34 subtype6 16B and subtype11 six flag-dependent groups、S62 variable strings、S63 2B、S29 13B；前輪 S0C/S64/S5F/S0E。**GitHub Actions run 41185085803 已確認全部通過**：19 個新增 decoded-body 測試 + 7 個既有 NPC 測試，另 phase-gate PASS。
- `S07 row 0x228`、`S34 0x202/0x40e/0x602` 是 Client 記憶體 stride，禁止作 wire length；unknown subtype/kind 以 designed fail-closed，不依此宣稱 Client 原生拒絕相同值。

## CT-066：Native 原 Client 生成／移動／資訊更新／死亡／離視野 E2E（not-run）

1. 同版 Client 登入/切圖完成，具體 map 和物件準備好之後抓 decoded S07（非零 count），確認 each row 的 kind、flags、string8 CP950；錄影對應 Sprite / NPC / Monster 的實際顯示與 ID。
2. 對同一物件送 S0C 與 S64 各一次及多次；確認 BE u32 key 與位置、path count、行動/動畫、移動時間單位，跨圖與 removed id 不影響新物件。S64 path count 超 11 在 Server 端禁止測試對原版 Client（避免可能 buffer overwrite）。
3. 使用同一合法 object 對照 S34、S3C、S62、S63、S29，找到原生 GUI/UI 消費端與顯示差異，區分提示、動作變更與視覺特效；針對 S34 subtype11 已證六組變長陣列補抓實際 body 和 GUI 對應，核實欄位業務語意。
4. 以攻擊 C13 等觸發實際死亡時，記錄 S13/S5F/S0E 的先後、死亡動畫、物件是否留在 registry、移除後重出現/新 generation，不能把 S5F 直接當 S0E。
5. 雙玩家不同可見範圍、NPC/怪物移動中斷線/重登/切圖，驗證 Human S33/S06/S11 不會錯套到 S07/S0C/S64。
6. 失敗案例：原生有效/無效 kind、未載入 map、重覆生成、已移除 id 的延遲 S0C、不同 epoch 的舊事件、非法 count/長度、同 id 不同 generation；拒絕與重送策略屬 **Server designed**，以具體 trace 區分 Client 行為。
7. 保存原版 Client 擷取畫面、去識別的收包紀錄（opcode、body、object id、map、時間）、binary VA/UI callback、對應驗收結果；有欠缺應回報分析 A，Server 權威邏輯／生成政策問題回 DEV。

**工作界線**：CT-065 靜態收包研究與 CT-066 實機 GUI 是兩個獨立關卡。沒有實測不能標原版 NPC sprite/動畫已通過，也不能宣稱新 Server 已完成怪物 AI。
