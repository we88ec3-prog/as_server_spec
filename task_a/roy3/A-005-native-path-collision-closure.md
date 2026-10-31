# A-005 — roy3 最終 native-static path / collision 逆向分析（2026-11-01）

沿用 task_a/roy3（已同步 main），承接 task_a/roy2/A-005-analysis.md 與 task_a/roy3/A-005-roy3-native-movement.md。**Client 靜態研究交接 ready；原版 GUI 移動驗收仍 not-run。** 本文只宣稱原始 EXE 已證的局部路徑決策，不替官方 Server 猜速度、動態物件和實際合法出生。

## 原件與可重現驗證
- Asgard.exe 原版 PE32 SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。
- Map0.dat SHA dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761；Map1.dat SHA 8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b；Map2.dat SHA 5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb。
- 新的 task_a/roy3/a005_roy3_collision_recovery.py 對原始 EXE 驗 13/13 direct E8/E9 call/jump、18/18 exact native code anchors；Map0 原件選圖解析；8 個單元測試（真檔+合成分支）PASS。沒有 raw 遊戲素材提交 Git。
- 下文 E15..E21 為 observed-original-static、original-map、synthetic-branch-test 分級。沒執行的原生 Windows GUI 不標為通過。

## A005-E15：native 真正局部候選路徑 predicate
0x557B9B 呼叫 0x4BE470；其 0x4BE7B7 再呼叫 0x4B8B20 驗每個相鄰候選。0x4B8B20 分支由原始指令核對：

1. [0x66D1C8]+0x410 非零，0x4B8B35 直接回傳 1（全域 bypass；其實際遊戲語意未證，Server 不可當授權繞過）。
2. 其他情況 0x4B8B4F 呼叫 0x4EA900(candidate,0)，**回值恰好 1** 由 0x4B8B59 回傳 0；這是場景物件的額外限制，具體 NPC/Player 等身分需 runtime。
3. 0x4B8B71 查 destination 的有效 Tile；0x4B8B76 若 flags&0x01!=0 回傳 0。
4. 0x4B8BA0 查 source 的有效 Tile；0x4B8BA5 若 source flags&0x08==0，回傳 1；若已設，0x4431E0(dest-source) 得 direction0..7；0x4B8BB8 讀來源 Tile 方向遮罩 byte，若 byte&(1<<direction) 非零回傳 0，否則 1。

這是原生 **local path candidate** 子判定，不是「Server 完整碰撞權威」：

    if global_bypass: return True
    if object_lookup_returns_one: return False
    if effective_dest_flags & 1: return False
    if (effective_src_flags & 8) and (src_dir_mask & (1<<direction)): return False
    return True

0x4B8B20 **沒有直接把 destination 的 bit4 當阻擋**。另一個函式 0x4B4BB0 會以 bit4 檢查線段，但不能因此把 bit4 等同上述 local path gate。旗標 16 在此單獨的 bit0 測試未拒絕，不等於整個原生 Client 已實際走通。

## A005-E16：0x4C1850 先合成動態有效 flags，再供候選判定
0x4B4920 先檢查 x/y 在 0<=x<width、0<=y<height，然後 0x4C1850。越界分支只寫輸出頭四 bytes=0，不能把這個回傳當通行證明；呼叫端另有邊界限制。

0x4C1862 從 0x4B2C80 取得 Client **17-byte in-memory Tile**。0x4C186B..0x4C1883 複製 tile+6 開始的 **11 bytes**，輸出[0..3]為完整 u32 flags。落在 dynamic overlay 區域（this+8/+0xC，加 this+0x10/+0x14 界限）時，0x4C18C8→0x4C3AA0 先執行 flags |= overlay[0]，再於 0x4C18D8..0x4C18DE 執行 flags &= ~overlay[0xC]。所以：

    effective_flags = (native_memory_flags | dynamic_add) & ~dynamic_remove

0x4B8BB8 取得的是同一輸出 **第 6 byte**（考慮前一 push 造成的 stack offset），即 **native memory tile+0x0C** 的方向遮罩，並非原始 MAP 檔 10-byte tile 中已有的方向欄位。該記憶體欄位的動態寫入來源仍待 runtime / 更完整 source xref。這證明只把 raw MAP 的 bit0/bit4 設成固定全圖 mask 不足。

## A005-E17：路徑格與方向
0x4BE470 使用 21×19 局部搜尋工作區、0x18F(399)筆候選，每筆 stride12；0x4BE7A7 以 0x03 檢查 local candidate state；0x4BE813/0x4BE814 迴圈走 8 鄰居，先由 0x46E740 檢查 rectangle，再呼叫 0x4B8B20。方向 helper 0x4431E0 依斜率/象限計算；八鄰格的確定索引：
- 0: (0,-1)；1: (+1,0)；2: (0,+1)；3: (-1,0)
- 4: (+1,-1)；5: (+1,+1)；6: (-1,+1)；7: (-1,-1)

這是 native **path direction**，不能假稱所有 C33 狀態的 directions 必相同。斜角切邊、完整尋路最佳化及角色的物理半徑尚未以原版 GUI 驗證。

## A005-E18：Map0 原始實測（raw-only 界線）
Map0.dat/00006.map；map_ref=6、60×60=3600 cells，原始 tile 全量 flags 只有 0:902、17:2698。raw bit0-clear=902 cells；從 (30,30) 以 **四鄰、raw bit0-only** flood fill 可達 900 個候選格。A32 的 (30,30)→(30,31)→(30,32)→(31,32)→(32,32) 各格原始 flags0。這裡的 900 是沒有導入動態 overlay、source direction mask、0x4EA900 場景阻擋的 **離線候選集合**；沒有一格可標記 PASSABLE_NATIVE_VERIFIED，未證官方新手圖／出生點。

## A005-E19：C33、C11 與 S0B 靜態雙向處理（沿用 roy3 前輪）
- Trigger: 原版局部 path caller 0x557AC0；C33 由 0x557DB2 建 ctor、0x557DE6 enqueue，wire 3×u8(direction,seq,local-mode byte)；Client 發送後 local next_seq=(seq+1)&127。
- C11 由 0x555B07/0x555EAE 建 ctor，body 1×u8。
- S0B parser 0x583150: BEu16 x/y + u8 status_sequence；0x558670 native handler 的兩條 bit7 分支都比較 ((status&127)+1)&127 == local_next_seq。bit7 清：權威位置/路徑停止；bit7 設：本地 predicted-position 比對、符合繼續或不符 rebase。Server 回覆當次 C33 seq 而非下一個。
- 其他玩家用 S06/S11，不能把 S0B 當廣播。Server 認證、map epoch、speed/tick、持久化、重送權威策略不是 Client 研究能直接得出。

## A005-E20／E21：結案、重現、剩餘驗收
在 repo 根目錄，以使用者已有原件本機執行：

    python task_a/roy3/a005_roy3_collision_recovery.py --exe Asgard.exe --map0 Map0.dat
    # PowerShell
    $env:ASGARD_EXE=".\Asgard.exe"
    $env:ASGARD_MAP0=".\Map0.dat"
    python -m unittest discover -s task_a/roy3 -p "test_a005_roy3_collision_recovery.py" -v
    objdump -D -M intel --start-address=0x4b8b20 --stop-address=0x4b8bd5 Asgard.exe
    objdump -D -M intel --start-address=0x4c1850 --stop-address=0x4c18e4 Asgard.exe

**A005 研究結案：status=integrated、handoff_status=ready（Client 已證 native-static 子集）、native_client_validation=not-run、implementation_ready 只包含 decoded-body/path predicate/seq/correction。** 未完成的 **Client 真正成功行走、撞牆/S0B 回滾、原生 dynamic object、實際出生與 C35** 由 DEV/CT-109 等執行；無可假稱的原服 speed/ms 或完整 dynamic collision whitelist。碰撞方向 mask 的來源寫入者也尚未全量追到，只能採用 Client read-side contract。

**缺少檔案：無。** Asgard.exe、Map0/1/2.dat、Born.dat 均已提供；目前剩餘是原生 World 已能載圖後的去敏封包與畫面觀測。
