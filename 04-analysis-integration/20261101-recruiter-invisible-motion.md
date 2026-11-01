# 招募員不可見：動作初始化與空白方向

## 問題來源與實際觀察

使用者回報獨立教學試驗看不到 NPC，截圖位置為 31,29。此為使用者實機回報，並非 EXE 推導的需求。舊試驗 Server 為 36c71fd，診斷 Client SHA256 為 `874c83db4840af6db584c1814fdda107e02713f0bb26204a3c6decec9b0fc3ef`；未修改原始 Client 的正式驗收仍未執行。

同一 Client 重新登入時，以 REA 被動探針觀察到 S07 reader、handler、MonsterObject 建構與登錄依序發生：kind1、ref0x1001、image0x4037、31,29、方向欄0。sprite 指標非空，library8005、slot5，當前動作8、幀數0。這排除該次重登入場「沒有收到 S07／完全沒有建構」的假說，但不將先前一次登錄表讀取未找到物件擴大為所有入場都未生成。探針已卸載並脫離，未更改遊戲資料或呼叫遊戲函式。

實機觀察 Evidence：`ev_92f855f842c3964b6e51e59782e1964ef5ba2ea3bcb4049e66654ebcc30cc045`、`ev_b4a40ba1483540d956fbacf45c4a81853c68cd17f359cbf079a54274530d609e`。原始觀察與指標只保存在私有分析區。

## Client 與資源合約

原件 EXE SHA256 沿用 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

- S07 handler `0x4F17C0` 將第五個 variant byte（本地 row+0x18）傳入建構子的方向／基底動作參數；`0x4D2340` 初始選取該值+8。
- 原生 S1A handler `0x4F1C60..0x4F1D14` 讀取 object ref、u8 動作與 u16 參數，找到物件後呼叫虛擬表+0x44；Monster 分支為 `0x4D63E0`。
- `0x4D2520` 對動作0選取方向+0x20；其他動作有不同映射，不能據此建立未分析的通用動作列舉。u16 參數的正式時間單位仍未確定。
- Monster05.dat 的已核對 helper 成員第一 channel 有69個圖片幀與730個動作項。動作8／10無序列；32、33雖各有14項，但引用的圖片 bounds 全為0。動作34有13項，引用幀全有非零 bounds；第一張為 frame18，bounds=(-72,-15,5,17)。該幀已經 RLE 行寬、非零像素及 palette stream 消耗檢查，成功離線預覽；先前只試前16幀的預覽失敗不代表素材不支援或損壞。

## 修正政策與驗證邊界

復原版試驗設定將第五個 variant byte 設2，保持其餘四 byte 為0。S07 後立即發 S1A，decoded body 為 `ref:u32BE=0x1001, motion:u8=0, parameter:u16BE=1000, tail:u8=0`，使此候選資源選到動作34。不能只補動作0而繼續方向0，後者仍引用空白圖片。1000 沿用本地試驗數值，不宣稱原服計時規則。

入場順序為 S04、S33、S14(2)、S07、S1A，之後可選 S19 及 Born S44。此修正不修改 EXE/DAT，也不改候選 NPC 的官方身份未知結論。Server 的 ref、距離、runner context、加入與畢業分離政策維持既有合約。

279項 Server 測試及隔離真 HTTP/TCP 通過，包含動作封包順序、拒絕／接受／重送、移動、保存與重登。這些測試不執行 renderer；診斷 Client 的可見性及點選對話正在等待使用者重測。學校、選職及職業城鎮尚未完成。
