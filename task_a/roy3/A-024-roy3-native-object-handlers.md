# A-024／roy3 — 原生 NPC／怪物 Client object handler、scene registry、C43 互動追查

2026-11-01；分支 task_a/roy3。接續 task_a/roy2/A-024-analysis.md 的 S07 kind1..14 decoded-body 及各封包 reader，不重複申稱只因 packet class 存在就證實渲染。原始 Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。新證據 A024-E20..E27。本輪完成 native-static Client I/O handler 交接；原版 GUI E2E、原 Server NPC AI／出生／重生仍未知。

## 1. Client opcode 分派至真正 handler（A024-E20）

原始 Client 0x4F48A0 讀 packet+8 的 opcode，0x4F48A7 減 3、0x4F48AA 限定 <=0x6E，0x4F48B3 以 0x4F4B30 的 byte group table 索引，再由 0x4F4A78 的 DWORD jump table 取得 trampoline。各 trampoline 先將 packet 指標置於 [esp+4]，再 E9 跳至原生處理器：

|S2C opcode|Trampoline VA|Handler VA|用途|
|---|---|---|---|
|S07|0x4F492D|0x4F17C0|批次顯示物件|
|S0C|0x4F4912|0x4F1610|單一物件位置及狀態|
|S64|0x4F4924|0x4F1750|物件路徑|
|S0E|0x4F493F|0x4F1DA0|物件移除|
|S5F|0x4F49B3|0x4F2BB0|死亡事件|
|S29|0x4F4948|0x4F1DC0|特效|
|S62|0x4F49D7|0x4F2CD0|新增動作|
|S63|0x4F49E0|0x4F2F10|移除動作|

注意此為特定 Client phase dispatcher；S34/S3C 在此表走 default，不足以證明另一階段完全不支援它們，Roy2 原生 parser 仍有效。這八組是原版指令/table 證據，不是僅看 RTTI 名稱猜測。

## 2. S07 收包後如何改變畫面物件（A024-E21）

S07 parser 0x57E3E0 解出每列 prefix（兩 BEu16、kind u8、BEu32 object_key_candidate、BEu16），每筆 Client local row stride 0x228，與 wire 長度不同。處理器 0x4F17C0 以 0x4F1810 索引列，0x4F181C 呼叫 0x4EAC70 對 row+8 的 key 做本地登錄輔助清理（不是已證直接移除實體），不同 kind 行不同場景路徑：

- kind14：0x4F1821/0x4F182B 分別查 kind14 及 row+0x11 狀態。0x4F183F→0x4EAC30 找已有 key；找到時 0x4DC240 和 0x4DB420 更新；另一條依 map lookup 0x4F1896→0x4B80D0、新物件初始化 0x4F1914→0x4DC030，然後 0x4F192E→0x4B6450 加入場景。
- kind13：0x4F194E 判斷 kind=13，0x4F196B→0x4C0640 處理 x/y 及本地 row+0x10 指向的資料。
- kind1/2/4：0x4F1975/0x4F197D/0x4F1985 分支；flags bit0/bit1/bit4 用於準備本地可選欄位；0x4F1AEB、0x4F1BC7、0x4F1C31 分別呼叫 0x4D6FA0 使用不同的建立參數，成功後 0x4F1B12→0x4B6450 加入場景。kind2 還有 0x4F1B17..0x4F1B36 的 focus-key 比對及 0x4B7CA0 其他呼叫。
- 其他 kind：0x4F1991/0x4F199B 對 row+0x0C u16 檢查 0x8000..0xBFFF，符合才走 0x4F19F4→0x496540 條件建立及場景加入。不能說每筆 kind5..12 必定可顯示，更不能把此 field 當 NPC 的官方資源 ID。

上述是 Client 靜態場景操作，不足以唯一判斷 kind1..14 對應 NPC／Monster／靜態圖像／掉落物。

## 3. 移動、路徑、死亡與移除原生執行（A024-E22）

- S0C 0x4F1610：從 packet+0x24 u32 取 object key，0x4F1623→0x4EAC30 找物件；非 self 物件由 0x4F167C→0x46E3F0 取得當前座標，比 packet+0x28/+0x2A 的兩 BEu16；不同時呼叫 object vtable+0x34 位置更新；又以 0x4A4630 比方向，必要時呼叫 vtable+0x3C，並呼叫 vtable+0x40 處理後一 u8。找不到物件時另走 fallback；不代表原版 Server 速度已知。
- S64 0x4F1750：以 packet+0x24 object key 從 0x4EAC30 查出已有場景物件，非 self 物件時 0x4F17AC→0x47C9C0 傳入整筆 path packet；找不到亦有 scene manager fallback。path 的方向與時間單位仍須 native Client。
- S0E 0x4F1DA0：packet+0x24 u32 經 0x4F1DB1 E9 tail-jump 到 0x4BA0C0，使用 map manager 0x66D0D8；該處按 registry 和場景型別處理退出。不能當作官方永久刪除 NPC。
- S5F 0x4F2BB0：packet+0x24 u32 由 0x4F2BC0→0x4EAC30 找物件，進一步 0x4A6700 runtime-type check、0x46E2E0/0x4EA240 scene path；另一情況走 0x4F2C01→0x4BA310。其 handler 明確不同於 S0E，死亡不等於立即 remove。
- S29、S62、S63 另分派 0x4F1DC0、0x4F2CD0、0x4F2F10，body 仍參照 Roy2；不可直接宣稱它們就是怪物每次 AI tick。

## 4. 原版 C43 兩條物件資訊發送端（A024-E23）

C43 constructor 0x574500、writer 0x5745B0 body=u8,BEu32,u8。兩條實際 Client 原生 producer：
- 0x479DC7 ctor；0x479DDB packet+0x24 填 01，0x479DDF..0x479DE2 以 caller local+0x48 填 packet+0x28 u32；0x479DE7 packet+0x2C 填 04，0x479DEB→0x5788A0 queue。
- 0x4A23F8 ctor；0x4A2409 填 packet+0x24=01；0x4A240D/local+0x4C 給 packet+0x28 u32；0x4A2410 填最後一 byte=04；0x4A2558→0x5788A0 queue。

故這兩條的 decoded body 可表示為 01 + 4B BE object_key + 04。合成 key=0x11223344 的 body=011122334404。真 target 必須從 runtime 讀；不能證明女性招募員專屬點擊、也不能代表所有 C43 都採相同值。C13 另為 BEu32 攻擊 request。

## 5. DEV 可用與 CT 必須分離（A024-E24..E27）

已具 Client SHA pin、S07 kind1..14 reader、8 個實際 handler、S0C/S64 真 registry+object callback、S0E 與 S5F 不同執行鏈、C43 有兩條 producer；能交 Server 的是這些封包欄位和物件生命週期。Server 自行決定 NPC/怪物 AI、路徑時序、同圖可見性、ID generation、碰撞、攻擊、重生、掉落和安全去重；原版是否有相同 epoch 是未知，不能說成已觀察。

Native CT-081 not-run：真 Client 在已載圖/同圖兩玩家下，使用合法圖像資產實測 S07 kind 和 image ID、NPC/怪物生成，S0C/S64 路徑，S5F 死亡，S0E 移除，之後 stale move/重送；招募員點擊時收集 S15/S07/C43/S34/S2F/S44/C6C，對照 nNewJoin01、Born 指路 (31,29)，證明或否證具體 EntityId 與 Script 綁定。S34/S3C 的其他 phase/UI handler 待 CT 補證。沒有原版 Server 的 NPC AI/出生資料不能聲稱完全復刻遊戲內容。

**驗證**：原始 Asgard.exe 8 組 dispatcher、21 個 native E8 call edges、39 個 instruction anchors 全 PASS；10 個 unittest PASS（含原件 SHA 規格）。重跑：
    python task_a/roy3/a024_roy3_handler_probe.py Asgard.exe
    python -m unittest discover -s task_a/roy3 -p test_a024_roy3_handler_probe.py -v

**狀態**：A-024 integrated，handoff_status=ready（Client native-static scope），native_client_validation=not-run，original_tutorial_spawn_ready=false，native_npc_interaction_ready=false，npc_ai_parameters_known=false。缺新檔案：本輪 Client handler 研究無；若要重新核對素材，原始 Monster00.dat 和 World00.dat 的 container metadata 已在 main 有證據，本分析環境未載入這兩個 bytes。仍缺真原版 GUI/封包 trace 或官方教程 NPC spawn／腳本配置。不能從素材檔自行猜 NPC ID。
