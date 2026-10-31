# A-032 roy3 — 原始 494 MAP 的 C35 全庫重算、真 S14→C35 發送鏈

日期 2026-11-01；branch task_a/roy3；原始 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。接續 task_a/roy3/A-032-roy3-native-map-c35.md 與 A005 原生碰撞，新增 A032-E06..E12。原版 EXE 未修改。

## 一、完整 494 MAP 實際數據（A032-E06）

已直接以原本使用者給的 Map0.dat / Map1.dat / Map2.dat 和原始 EXE 0x664720 的 CRC table，重算所有 MapData 結構 CRC。所用解析器是本 repo 前輪 a032_c35_probe.py 的 original MAP 正規化，而非 raw file CRC。三份 DAT 的 SHA：Map0=dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761；Map1=8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b；Map2=5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb。

- Map0=288、Map1=184、Map2=22，**總計 494/494** 原件解析/CRC PASS。
- 僅 **330** 組不同 MAP payload SHA256，且 330 組不同 C35 雙值；**33** 個同值重複群組，總計 **164 個額外 map_ref** 共用 C35 pair，最大一群 23 個 map_ref。
- 這一組原件中，未發現不同 payload SHA 卻相同 C35 pair 的自然撞值；**不代表 CRC16 安全或可識別 map_ref**。
- 494 行按數字 map_ref 升序排列，以每行五位十進位 map_ref、冒號、8 字元大寫 C35、LF 的文字串接，共 7410 bytes，SHA256 = **8a0ba7ebe767385db7296de1ca0c3b999aa620e05e6ab1793db0e640f30c375a**。新工具會驗證此 atlas 指紋，避免只測 5 筆示例。
- 真實例：map_ref0→000063A9 (20x20)、6→00040F90 (60x60)、10000→00040F90 (60x60)、18001→0012F892 (150x150)、20001→0016E9B9 (60x60)。
- **map_ref6 和 map_ref10000 不同地圖身份，但 payload SHA 一樣且 C35 pair 一樣**。不能只憑 C35 body 選出 Server 地圖、出生點或所在 map instance。

## 二、原始 Client S14(1)→C35 完整靜態 sender（A032-E07）

從 0x4F2300 原版 S14 handler 的 packet+0x24 subtype 讀取到 0x4F231F 分支；subtype=1 進入 **0x4F23CB**。依原生 direct x86：
1. 0x4F23F5 direct call 0x5733E0，C35 packet ctor 0x5733F9 push0x35。
2. 0x4F240E direct call 0x4B4850，讀目前 active [0x66D0D8] Map manager+0xB4 的 MapData header +4 LEu16，0x4F2413 寫 C35 packet+0x24。
3. 0x4F241D call 0x4B4890，再 0x4B4896 tail-jump 0x4B3650，取得同一 active MapData cached 0x4B2EC0 structured checksum；0x4F2424 寫 C35 packet+0x26。
4. 0x4F2428 direct call 0x5788A0 enqueue。
5. C35 native writer 0x573490 兩次呼叫 0x45AB40（0x573498 / 0x5734A4），依序輸出兩個 BEu16。decoded body **正好 4 bytes**；沒有 map_ref、epoch、spawn、身份欄位。

原版 EXE SHA pinned 7 native direct E8/E9 edges 和 15 opcode anchors 全數 PASS，C35 sender 自 S14(1) 到 MapData 兩個 getter 和 queue 靜態證明已閉合，**但未在 Windows 原版 Client 抓到 TCP 真包**。

## 三、Server 安全要求（A032-E08）

- C35 不是 map identity。Server **必須從自身 session 的單一 pending S15 map_ref** 得知當前載圖目標，並綁 generation、archive/member SHA、C35 4 bytes 再逐一比對；不能根據 C35 回查 map_ref，也不能視其為登入驗證或 World 授權。
- 同一個 C35 值可以由 map_ref6 和10000 產生，切圖重送 C35 若脫離原 pending map epoch 必須拒絕。只有目前已授權 World loading context 才能使用此資料；CRC 失敗不得無聲容錯放行。以上屬 Server-designed 閘門，不是原服 Server 實際策略。
- 程式 task_a/roy3/a032_roy3_full_c35_atlas.py 的 accept_c35_for_pending 提供**designed** 窄範圍對照，用於驗證錯 mapRef、generation、SHA、checksum、body length fail closed。

## 四、出生、安全路徑和仍缺的 Native 證據（A032-E09）

map_ref6 原始 MAP 60×60、原 tile flags=0 902格、flags=17 2698格；raw bit0-clear 地理候選902格，(30,30) 4-neighbor 可達900格，不是原生走路 PASS。原候選路徑 (30,30)→(30,31)→(30,32)→(31,32)→(32,32) 五格 flags=0，僅 **raw geometry**。A005 native 0x4B8B20 仍會看目的有效 bit0、來源有效 bit3/方向 mask、動態 overlay、0x4EA900 物件阻擋。Born.dat (31,29) 只是文字中招募員指路，不能宣稱 map_ref6 是官方教程/出生圖，或 (30,30) 合法出生。未修改原版 Client 的 S04 viewport/facing、S33 和 C33/C11/S0B 走路/撞牆實機 not-run。

## 五、工具、測試和交接狀態（A032-E10～E12）

新增四個 Python 原始碼／測試檔：
- task_a/roy3/a032_roy3_full_c35_atlas.py — SHA 鎖版掃描全部 494 MAP，產生整份 metadata atlas JSON（選用 --output），不保存遊戲素材，驗 330 種 pair、33 clusters、版本指紋。
- task_a/roy3/test_a032_roy3_full_c35_atlas.py — 12 項原件／合成測試，包括同值不同 map_ref 的 Server fail-closed。
- task_a/roy3/a032_roy3_native_c35_emit.py — SHA pinned S14(1) handler 7 edges /15 anchors。
- task_a/roy3/test_a032_roy3_native_c35_emit.py — 8 項 producer/BEu16/拒絕不合法 body 測試。

重跑：
    python task_a/roy3/a032_roy3_full_c35_atlas.py --exe Asgard.exe --map-dir . --output a032-494-map-atlas.json
    python task_a/roy3/a032_roy3_native_c35_emit.py Asgard.exe
    python -m unittest discover -s task_a/roy3 -p "test_a032_roy3_*.py" -v

**本輪原件全庫 C35 靜態資料與 S14→C35 sender 已完成交接；A-032 任務仍 status=integrated, handoff_status=partial, implementation_ready=false, native_client_validation=not-run。** 原需求還含 GUI 可見的正確 spawn/viewport、實際 C35 capture 和原生可走路徑，沒有 Windows 原版 Client/實測封包不能標真正全完成。Native CT-108/109 見 05-conformance/A-032-roy3-native-map-acceptance.md。

缺少檔案：**無新增需要的 .dat 或 .exe**。仍需 Windows 原版 Client 在合法測試 Server 路徑擷取 S15→S14(1)→C35、S04/viewport、facing、C33/C11/S0B/撞牆及 GUI 截圖；去敏遮罩 session/token。
