# A-005 / roy3：原版 C33 行走、S0B 回覆與碰撞鏈追查（2026-11-01）

作業分支 task_a/roy3，已先合併最新 main。這是 task_a/roy2/A-005-analysis.md 的補證，不覆寫 A005-E01..E08。結論：**C33 原生 producer、C11 producer、S0B native receiver 的序號和座標修正已追出；玩家真實 tile walkability / 原服 speed policy 尚未證實。** A005 = integrated / handoff partial / native Client not-run。

## 原件與檢查

原始 PE32 Asgard.exe SHA256 = db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。Map0.dat SHA256 = dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761，Map1.dat = 8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b，Map2.dat = 5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb。BIN-first 逐一反組譯原始 VA；新增 task_a/roy3/a005_native_move_chain.py 的 13 組 E8/E9 呼叫／跳轉與 15 組指令視窗 PASS，5 個 unittest PASS（包括 hash-pinned 原版 EXE）。不提交原始資產。

## A005-E09 / C33 生產與序號

- 0x557AC0 從 0x55819C / 0x5585F2 / 0x558859 呼叫。0x557B41→0x4B63F0→0x4EA900 是本地 object lookup/條件，不能假稱 tile passability；0x557B9B→0x4BE470 組成 route，0x557C1F→0x4B4920 查 path waypoint tile。
- 0x557DB2→0x573B40 產生 C33（constructor opcode 0x33）；0x573BF0 serializer 寫 3×u8，0x557DE6→0x5788A0 送 packet。0x557DC4..0x557DE1：packet+0x24=local+0x274 direction，packet+0x25=local+0x518 sequence，packet+0x26=local+0x534 的 movement mode 低 byte，且條件滿足時 OR 0x80。此前抽象稱 gait_flags，**實際來源是 movement state 與本地路徑條件，不應自行賦予跑步倍率**。
- 0x557DEB..0x557E03：發送後本地 next_sequence = (sequence + 1) & 0x7f；127→0，不需先等 S0B。
- 0x555B07 / 0x555EAE → 0x5718B0 是 C11 constructor 的兩個 caller。0x571960 writer 是 1×u8；0x555B17 填 direction 並 enqueue。原生鍵盤/滑鼠事件到 callback 的全部細節仍可再追。

## A005-E10 / S0B 真實 handler 的重新定位

原生 S0B parser 0x583150，body = BE u16 x, BE u16 y, u8 status_sequence。0x4F1606 和 0x4F4904 都跳轉 **0x558670** native consume handler；handler 收的 packet 子物件用 +0x24/+0x26/+0x28，對應 parser 本體 +0x18/+0x1A/+0x1C。

- 0x558678 的 signed bit test 分支：status_sequence bit7 **清除**進 0x558688..0x558772；bit7 **設置**進 0x55877E..0x55897D。
- **兩條分支**均先做 ((status_sequence & 0x7f)+1)&0x7f，再與本地已前進的 next_sequence (local+0x518) 比對：0x558695/0x55878B。不符不能走正常認可路徑。Server 回覆必須是觸發的 **當次 C33 sequence**，不是本地的下一序號。
- bit7 清除且 seq 符合：0x5586A4..0x5586D1 自 S0B x/y 更新座標；0x5586F2..0x55875C 停止／重置既有路徑或進校正處理。這是「權威更正」靜態分支，不足以斷定原版 Server 哪個錯誤碼屬於碰壁。
- bit7 設置且 seq 符合：0x5587A2..0x5587E0 用 0x4430C0 依方向與 movement state 取得 local 預測增量，先比對 S0B x/y。相符則依狀態繼續路徑/回呼（0x5587E6..0x5588D9）；不符則 0x5588DC..0x55896B 重定向至 S0B 座標並調整路徑。**bit7 設置不等於盲信 Client 當前位置**。
- bit7 可解讀成「正常步伐與校正分支 selector」（interpreted-static），真正原版 Server 成功/失敗官方語義和 native GUI 呈現仍 not-run。

| 已送 C33.seq | 本地 next_seq | S0B status byte | Client 靜態路徑 |
|---:|---:|---:|---|
|5|6|0x85|bit7 設，預測位置比較|
|5|6|0x05|bit7 清，權威位置回復/停止路徑|
|5|6|0x04|seq mismatch|
|127|0|0xFF|bit7 設，127→0 wrap 符合|
|127|0|0x7F|bit7 清，127→0 wrap 符合|
|126|127|0xFF|seq mismatch|

這是依原版反組譯的本地分支測試向量，不是實際封包 capture。S0B 不能用來廣播其他玩家移動：他人位置依 A004 S06/S11。

## A005-E11 / MAP 與移動路徑的關聯及其界線

0x4B4920 對 x/y 有範圍檢查，進到 0x4C1850 的 tile consumer；0x557B9B 的 0x4BE470 規劃路徑，但尚未把所有 0x4BE470/0x4C1850 的條件資料與玩家腳底、block、tile/aux grid 關聯完全還原。另有 0x46D813、0x46D8D3、0x46DB0E 三個 native caller 使用 0x4B4BB0 (bit4 線段檢查)，與 0x557AC0 不是同一個直接玩家步行 mask。tile flags bit0 動態更新、bit4 線段測試、另一 4B/grid 各須維持分離；不以 flags=0、bit0 或 bit4 單獨認定 PASSABLE_NATIVE_VERIFIED。

A32 的 map_ref6 / Map0 00006.map 60×60 五步候選 (30,30)→(30,31)→(30,32)→(31,32)→(32,32)，全是 in-bounds 且原始旗標=0，但**完全沒有實測成功走過**。Born (31,29) 非玩家出生座標。

## Client I/O six-field handoff / DEV-ENTRY-05

- Trigger：角色 local path 行走觸發 0x557AC0；Native C11 producer 有 0x555B07 / 0x555EAE；具體 UI 按鍵事件仍未驗。
- C→S：C33 {direction:u8, sequence:u8, movement_mode:u8}；第三欄 bit7 有 native OR 分支。C11 1×u8。
- S→C：S0B BEu16 x/y、u8 seq+bit7；序號低七位回送 C33 的當次序號，錯序或 bit7 分別進不同 client handler branch。S06/S11 為其他角色位置/面向。
- Client reaction：S0B bit7=0 走權威位置校正／路徑停止；bit7=1 會比較本地預測與回覆位置、不符時 rebase；正確本地 next_seq 必須是 (C33.seq+1)&127。
- Evidence：A005-E09..E14、本報告、附程式、可核對的 native VA；原版 GUI native E2E **not-run**。
- Unknowns：玩家碰撞與穿牆判定的完整 native tile/block/dynamic-object predicate、方向實際格位/步幅與瞬時速度、原版 Server tick/拒絕訊息、原版 Client 走路及撞牆畫面、S0B status 真正官方錯誤語意。

可立即交 DEV 的是 codec/seq/bit7 correction 以及 fail-closed 審核，**不是**以此替 Server 自動選 passability。Server auth/session、map epoch、speed/step/diagonal、去重、耐重連與 collision source 是設計選擇，不能宣稱恢復原服權威政策；錯地圖或未驗 native map 不放行玩家 durable position。

## 驗證方式與尚缺事項（A005-E12..E14）

- python task_a/roy3/a005_native_move_chain.py /path/to/Asgard.exe
- ASGARD_EXE=/path/to/Asgard.exe python -m unittest discover -s task_a/roy3 -p test_a005_native_move_chain.py -v
- objdump -d -M intel --start-address=0x557ac0 --stop-address=0x557e04 Asgard.exe
- objdump -d -M intel --start-address=0x558670 --stop-address=0x55897e Asgard.exe

**完成：新增 Client send/receive/correction 靜態子集、原始檔 xref 驗證與本地合成回歸。未完成：玩家真正 collision mask 全量語意、GUI 過圖/成功/撞牆回滾與真正 Server 速度/tick。** 要追真正玩家碰撞下一步集中於 0x4C1850 與 0x4BE470 的來源欄位與 0x557AC0 的跨函數資料流；原生 E2E 交 CT-109 和 CT-071/072。

**缺檔：無**，已提供 Asgard.exe、Map0/1/2.dat、Born.dat；缺的是同版原生 Client 連入 World 後的去敏 C33、S0B、S04、S15/C35 和畫面 trace。A005 登錄為 integrated / partial，native_client_validation=not-run。
