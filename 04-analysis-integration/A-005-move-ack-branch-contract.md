# A-005 原生 C33 / S0B 語意交接（roy3）

**原件** Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。來源 task_a/roy3/A-005-roy3-native-movement.md，新增 A005-E09..E14。A5=integrated / handoff=partial / native Client=not-run。

1. C33 本地 producer 0x557DB2 / writer 0x573BF0 / enqueue 0x557DE6，三個 u8：direction、7-bit sequence、movement state byte（有條件 OR 0x80）。本地 send 之後 sequence 進位 1 modulo128；不是收到 ack 才加一。
2. C11 的原生 constructors 由 0x555B07 / 0x555EAE 呼叫，writer 0x571960 單一 direction:u8。
3. S0B parser 0x583150：x/y BEu16 與 status_sequence u8；consume handler 0x558670 由 0x4F1606 / 0x4F4904 跳轉。兩條高位元分支都驗證 ((status&0x7f)+1)&0x7f == Client local next sequence。Server 回覆的是**剛收到的 C33.seq**，不是它的下一個。
4. 高位清除：驗 seq 後權威更新座標/停止或重設 path。高位設置：驗 seq 後比較方向預測位置與回覆 x/y，相等走路徑後續，不等重新校正。原版 Server 成敗狀態語義未實機驗證。勿把 0x80 當 sequence 最高位。
5. S0B 自身沒有 map_ref/epoch/entityId。Server 必須獨立驗證 auth、session、當前 map/revision/C35、速度/位移、碰撞/重播；其他玩家使用 S06/S11。Server 自定禁止穿牆/斜向/速度政策不得假託原服。
6. Map0 00006.map 五個 flags0 候選只是 CT 目標；不代表已證 spawn/path、可通行旗標。A032 C35 仍須原版 Native 測試。

具體實測與回報見 05-conformance/A-005-native-movement-ack-test-plan.md。未通過 CT 前整體 native world movement 仍 fail-closed。
