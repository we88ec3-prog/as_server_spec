# A-032 / roy3：原始 MAP 的 C35 雙值與出生、路徑證據邊界（2026-11-01）

分支 task_a/roy3；依 main 的 A-032 P0。此交付為原件靜態重算與可重現離線工具，**不是**原版 Client GUI/封包實測，**不得**宣稱 A-032 所有驗收門檻已完成。Server 原始 Client 相容進度 native_client_validation=not-run。

## 1. 原件與方法（A032-E01）
- Asgard.exe，SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。
- Map0.dat SHA256 dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761；Map1.dat SHA256 8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b；Map2.dat SHA256 5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb。
- Native CRC byte primitive VA 0x43E0A0，查表 VA 0x664720（PE file offset 0x264720）。CRC 初值 0；每 byte 更新：crc = (table[(crc>>8)&255] ^ (crc<<8) ^ byte) & 65535。原表前 3 項 0、0x1021、0x2042；原生合成向量 01 02 03→0x1222、ABC→0x1AA6 通過。
- MapData loader VA 0x4B33A0..0x4B35F6：MAP 前 8 bytes 為三個 LEu16、u8 寬、u8 高；接 block 2B/entry、tile 10B/entry 和尾段 7/8/16B。0x4B3250 建構額外 u32 grid，**不直接變更 tile flags**。0x4B3650 cache 返回 0x4B2EC0 的重算值。C35 第一欄由 0x4B4850 讀 header offset+4；C35 序列化 VA 0x573490 為兩個 BEu16。
- 本次離線已對 SHA 鎖定的原件重算指定地圖，不導出資源 bytes。與 A-015 494/494 結構解析保持一致。

## 2. 0x4B2EC0 按 Native 指令還原（A032-E02）

逐區間直接核對 0x43E0A0 call 數與資料值（不要直接對整份 MAP 做 CRC）：

| Native VA | 原資料 | 每筆實際餵入 CRC 的資料 |
|---|---|---|
| 0x4B2EF0..0x4B2F21 | blocks | 逐 2 bytes 原順序；共 ceil(w/2)*ceil(h/4)*2 bytes |
| 0x4B2F50..0x4B2FC6 | tiles | 每 tile +0..+9 共 10 bytes，與原始 MAP 相同；Client 內存 stride 17B |
| 0x4B2FE0..0x4B3083 | 7B tail | byte0 非零→1；+1 LEu16 兩 bytes；+3/+5 的 LEi16 **各 sign-extend 為 4-byte LEi32**；合計每筆 11 bytes |
| 0x4B30B0..0x4B312C | 8B tail | 四個 LEu16 各 2 bytes；共 8 bytes |
| 0x4B3150..0x4B3239 | 16B tail | +0 LEu16 2B；+2 LEu16 是否非零 1B、+3 高 byte 是否非零 1B；+4 **只用一個 byte**；+8..+11 四 bytes；+12/+14 LEu16 各 2B；合計 **13 bytes**，跳過 +5..+7 |

特別注意 tail16 的第一個 bool 是完整 LEu16 是否非零，不是單獨低 byte；tail7 有 signed 16→32 擴張。這些是實際反組譯指令的資料流，非通用 CCITT(raw)。離線工具附合成「bool 同值、跳過 +5..+7、bit 擾動、截斷拒絕」回歸。初始 MAP 的 computed pair **尚未以原生 TCP C35 實測確認**；若 Client 在發包前有動態修改 MapData，仍可能改變觀察值。

## 3. 選定真 MAP 的雙值（A032-E03）

| map_ref（S15 第一個 BEu16） | 實際 DAT 成員 | tiles | header+4 | checksum | 預期 C35 body hex |
|---:|---|---:|---:|---:|---|
| 0 | Map0.dat / 00000.map | 20×20 | 0x0000 | 0x63A9 | 000063A9 |
| **6** | **Map0.dat / 00006.map** | **60×60** | **0x0004** | **0x0F90** | **00040F90** |
| 10000 | Map1.dat / 10000.map | 60×60 | 0x0004 | 0x0F90 | 00040F90 |
| 18001 | Map1.dat / 18001.map | 150×150 | 0x0012 | 0xF892 | 0012F892 |
| 20001 | Map2.dat / 20001.map | 60×60 | 0x0016 | 0xE9B9 | 0016E9B9 |

本次選 map_ref=6 作 **interim 靜態候選**，不是官方教程圖；不能從兩個 checksum 值推算 map_ref。6 與 10000 雖 MAP payload SHA256 相同（bd92c86632a7d23894d21f97571e2829428c608a8647f95211df27e578ce1760），**Server 上仍是不同 map identity**；相同 C35 不等於可互換視野/角色。18001 同時有 7/8/16B 尾段，可覆蓋全部重算分支。詳細 member SHA／證據分級在 a032_c35_fixture.json。

## 4. 出生與可走路徑：已證 vs 未證（A032-E04）

- map_ref=6：真原件寬 60、高 60；tile x/y 各在 [0,59] 是合法**座標邊界**。tile (30,30)、(30,31)、(30,32)、(31,32)、(32,32) 全部 **原始 flags_u32=0**，彼此正交相鄰且在圖內，作為離線 **candidate_path**。沒有任何一格經原生角色實際走過，因此全部 player_walkable=unknown，**不可標記 PASSABLE_NATIVE_VERIFIED**。
- (30,30) 可作實際 CT 的待驗測試起點候選，**不是已確認合法出生點**。地圖渲染、角色腳底座標的單位、S04 的 x/y/viewport_x/viewport_y 四個 BEu16 正確數值、facing/S33 實際值、動畫與阻擋回滾均未取得 GUI 或封包證據；不能填猜測數值上線。
- Born.dat 的 (31,29) 僅是文字引導的女性招募員位置，沒有 tutorial map_ref/spawn；即使 map_ref=6 該格 flags=0，也不能證實是新手圖或 NPC 存在。
- 原生 A-015 已辨 tile bit0 可動態設置、bit4 被線段測試用、另有 4B grid。**flags=0 不是可走語意的證明**；不能用它生成正式 Server passable mask。

## 5. Trigger / C→S / S→C / Client 效果與 DEV/CT

| trigger | Client C→S | Server S→C | Client effect / 證據 |
|---|---|---|---|
| 選定 map_ref=6，World 已進 Loading | 原 Client **尚未實測**進入時第一個 World 封包；另待 A-031 | S15 三個 BEu16、兩 u8、string8 title；第一 u16 map_ref=6。S14(1) | 根據 0x57FF30/0x4F23CB 靜態，Client 載入本地 MAP；缺實機 UI |
| 收到 S14(1) 且 MAP 已有效載入 | C35：2×BEu16；本 SHA 的離線預期 0004 / 0F90 | 必須比對同 epoch/同內容版本的預期 pair，不可只比第一字或放行所有 C35 | C35 writer 0x573490 和 checksum 0x4B2EC0 已證；**未錄到任何原生 C35 封包** |
| 通過 C35 | 尚未有玩家 move C33 的原生擷取 | S04 4×BEu16、S33、S14(2) 等，具體數值待 GUI 驗證 | 預期 Client 進場、顯示／移動；CT-108/109 not-run |
| 嘗試沿 candidate_path 行走或撞牆 | A-005 C33/C11；具體 client 行走與回滾 trace 未擷取 | S0B/位置校正依已驗行為實作，不得想像 | 原版 Client 是否接受移動 **unknown** |

**DEV-ENTRY-04**：可採 map_ref + archive SHA + member SHA + 雙值的 versioned lookup，作 SHA 鎖定的 C35 靜態參考 fixture；不得把 map_ref=6 當官方新手圖，亦不可在缺原生確認時宣告完成入圖。**DEV-ENTRY-05**：僅提供候選路徑做 CT，不能據此設定「玩家一定可走」的 Server 權威判定。C35 不含 map_ref/epoch，仍須單一 pending 及 generation isolation。

## 6. 可重現操作（A032-E05）

本地放置原本提供的五個檔案；不需要重新提供 Asgard.exe、Map0/1/2.dat、Born.dat：

~~~
python task_a/roy3/a032_c35_probe.py --exe Asgard.exe --map-dir . --map-ref 6 --candidate-path "30,30;30,31;30,32;31,32;32,32"
python task_a/roy3/a032_c35_probe.py --exe Asgard.exe --map-dir . --map-ref 10000
python task_a/roy3/a032_c35_probe.py --exe Asgard.exe --map-dir . --map-ref 18001
python -m unittest discover -s task_a/roy3 -p "test_a032_c35_probe.py" -v
objdump -d -M intel --start-address=0x4b2ec0 --stop-address=0x4b3247 Asgard.exe
objdump -d -M intel --start-address=0x43e0a0 --stop-address=0x43e0bf Asgard.exe
~~~

工具只輸出本地 MAP metadata、hash、雙值及指定候選格旗標；不提交原始遊戲素材／全文封包／敏感帳號。合成測試只證解析/CRC 邊界；真資料 metadata 不可當作原生 E2E。

## 7. 明確剩餘驗收與結論

- **已完成**：原件 hash、MAP 索引版本、完整 0x4B2EC0 靜態資料流、原始 MAP 的離線 C35 pair、跨庫相同 payload 的 CRC 一致、嚴格 bounds 與未驗候選路徑。
- **尚未完成（A32 全量 Gate）**：原版不修改 Client 擷取一次 C35 body 核對 00040F90；驗證 S15 選 map_ref=6 的 UI 正常顯示；從一個經本地 GUI 觀察到的合法 spawn（含原生 S04 viewport/facing）成功沿候選點移動、撞牆並觀察 S0B/回滾。這些需要先打通 A-031/DEV World Loading 後由 CT-108/109 進行，否則任何「安全出生」聲稱都缺證。
- 原版實機測試 **not-run**；沒有新的 A32 必要資源缺檔。缺的是 Client GUI/World 連線封包/測試執行記錄，而不是 Map0/1/2 重新上傳。需要的去敏 trace 欄位：Client SHA、map_ref、S15 摘要、S14(1)→C35 兩個 BEu16、S04 座標四欄、facing 封包、C33/C11/S0B、屏幕畫面及撞牆前後位置。
- 研究階段建議：A-032=review、handoff_status=partial、native_client_validation=not-run、implementation_ready=false（就出生/可走路整體而言）；**不要宣稱整個 A32 已驗收完成**。
