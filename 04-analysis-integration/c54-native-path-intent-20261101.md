# C54：進場後斷線與原生路徑通知

使用者在修正 C35 後回報「有角色但馬上斷線」。本地去敏 journal 顯示
C35=6/3984 通過，S04/S33/S14(2) 已送，接著 C11(body1) 通過，
**C54(body11)** 被目前 Server 的 unknown-opcode 處理關閉。不是 C35
再次失敗。使用者畫面顯示測試地圖與人物，仍不等於可持續遊玩。

## 原始 Client REA 證據

樣本 SHA256 沿用 C35 勘誤的原始 EXE，Ghidra 12.1.4：

- `0x573CC0` constructor 呼叫 packet base(0x54)，vtable 對應
  CMovePathPacket。證據 `ev_ec43273d80da6564e6df069b34d61388307bbb2837a740787b4ce5eeac811e61`。
- writer `0x573D70` 依序寫 startX/startY BEu16、u8 direction、u8 count、
  count 個 run byte、destinationX/destinationY BEu16、u8 finalDirection。
  完整 body 長度=11+count。證據
  `ev_df104fd250b2b1da0d4e0eb1b74cc018722262c9a97830791f89675403c6af74`。
- producer `0x555BE0` 以 `(direction<<4)|(runLength&15)` 填 run；同向
  run 最多 7，目的欄位位於物件+0x36，run 陣列從+0x2B起，佔11bytes。
  因此此版本嚴格限制 count≤11、每 run 方向≤7、長度≤7。
  證據 `ev_169a4788a62002452f81d1786eb8933c96053c76ea57ae97a5b7e3a313d51118`。
- stop producer `0x555E30` 將 start/destination 同設為目前角色座標、
  count=0、起終方向同設為角色方向，再送 C11。故零段的 11-byte C54
  不是格式錯誤。證據
  `ev_1ecb4c5042a8e2298dfcd174f9e9f323767531ba0c647ec97acfc7298f85448e`。

觀察只有長度與順序，沒有保留使用者該包 body；不能斷言該輪全部內容
等於 stop producer。原生靜態證據足以要求 Server 支援合法零段形狀。

## Server 行為與界線

啟用原生 map trial、WorldReady、owner/lease 仍有效、loading 已完成後，
嚴格解析 C54；畸形、截斷、多餘 bytes、超量 count／非法 packed run 拒絕。
此增量接收路徑通知，不發明專屬 ACK，不以 Client 給的起終座標修改
權威位置，也不讓它繞過 C33 的序號與後續碰撞檢查。
其他階段不允許 C54，未開啟原生試驗時標為已知但尚未實作。

本次解除進場後 unknown-opcode 的已知中斷點；完整移動仍須實作權威
逐步 C33/S0B、路徑阻擋、速度、持久化及實機回驗。不能把不再因
C54 斷線宣稱新手教學或行走已完成。

本次驗證：251 項 Server 回歸通過；隔離本機 HTTP/TCP smoke 涵蓋 C35通過後 C54→C33，無 C54 專屬虛構回覆。使用者畫面重驗仍待回報。

實作追溯：私有 roy commit `367f442`。

## 2026-11-01 後續開發

已實作可驗測的 Development Region3 自動交接與獨立 Server 移動政策，255項測試／本機TCP通過；不是原服封包順序或原始GUI驗收宣告。最新狀態見[新角色與移動增量](../02-server-planning/native-new-character-movement-increment-20261101.md)。
