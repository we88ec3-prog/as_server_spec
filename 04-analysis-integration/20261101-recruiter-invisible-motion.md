# 招募員不可見：動作初始化與空白方向

## 問題來源與實際觀察

使用者回報獨立教學試驗看不到 NPC，截圖位置為 31,29。此為使用者實機回報，並非 EXE 推導的需求。舊試驗 Server 為 36c71fd，診斷 Client SHA256 為 `874c83db4840af6db584c1814fdda107e02713f0bb26204a3c6decec9b0fc3ef`；未修改原始 Client 的正式驗收仍未執行。

同一 Client 重新登入時，以 REA 被動探針觀察到 S07 reader、handler、MonsterObject 建構與登錄依序發生：kind1、ref0x1001、image0x4037、31,29、方向欄0。sprite 指標非空，library8005、slot5，當前動作8、幀數0。這排除該次重登入場「沒有收到 S07／完全沒有建構」的假說，但不將先前一次登錄表讀取未找到物件擴大為所有入場都未生成。探針已卸載並脫離，未更改遊戲資料或呼叫遊戲函式。

實機觀察 Evidence：`ev_92f855f842c3964b6e51e59782e1964ef5ba2ea3bcb4049e66654ebcc30cc045`、`ev_b4a40ba1483540d956fbacf45c4a81853c68cd17f359cbf079a54274530d609e`。原始觀察與指標只保存在私有分析區。

## Client 與資源合約

原件 EXE SHA256 沿用 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

- S07 handler `0x4F17C0` 將第四個 variant byte（本地 row+0x18）傳入建構子的方向／基底動作參數；`0x4D2340` 初始選取該值+8。
- 原生 S1A handler `0x4F1C60..0x4F1D14` 讀取 object ref、u8 動作與 u16 參數，找到物件後呼叫虛擬表+0x44；Monster 分支為 `0x4D63E0`。
- `0x4D2520` 對動作0選取方向+0x20；其他動作有不同映射，不能據此建立未分析的通用動作列舉。u16 參數的正式時間單位仍未確定。
- Monster05.dat 的已核對 helper 成員第一 channel 有69個圖片幀與730個動作項。動作8／10無序列；32、33雖各有14項，但引用的圖片 bounds 全為0。動作34有13項，引用幀全有非零 bounds；第一張為 frame18，bounds=(-72,-15,5,17)。該幀已經 RLE 行寬、非零像素及 palette stream 消耗檢查，成功離線預覽；先前只試前16幀的預覽失敗不代表素材不支援或損壞。

## 修正政策與驗證邊界

復原版試驗設定將第四個 variant byte 設2，保持其餘四 byte 為0。S07 後立即發 S1A，decoded body 為 `ref:u32BE=0x1001, motion:u8=0, parameter:u16BE=1000, tail:u8=0`，使此候選資源選到動作34。不能只補動作0而繼續方向0，後者仍引用空白圖片。1000 沿用本地試驗數值，不宣稱原服計時規則。

入場順序為 S04、S33、S14(2)、S07、S1A，之後可選 S19 及 Born S44。此修正不修改 EXE/DAT，也不改候選 NPC 的官方身份未知結論。Server 的 ref、距離、runner context、加入與畢業分離政策維持既有合約。

279項 Server 測試及隔離真 HTTP/TCP 通過，包含動作封包順序、拒絕／接受／重送、移動、保存與重登。這些測試不執行 renderer；診斷 Client 的可見性及點選對話正在等待使用者重測。學校、選職及職業城鎮尚未完成。


## 實機後更正：wire 欄位定位（優先於舊結論）

使用者回報看不見但能點選、交談與接受。舊輪次 SQLite 有一筆持久加入事件，故「接受後沒有傳送」是尚未實作學校流程，不是遺失接受封包。重開仍相同加入對話也尚未接入階段分流。

再次重啟仍不可見後，原件 0x57E470..0x57E4D3 精確 bytes 證明：五次 ReadU8 依序存 row+0x14、+0x15、+0x16、+0x18、+0x220；row+0x17另填FF。先前把第5個 byte 當方向，及將實機仍為0解讀為未使用新版，均為分析錯誤，現明確撤回。最後一個 byte 不可自訂為方向；其正式語意待分析。Evidence `ev_89416b899e282153cab8a1bd7c43e40041d889040b86ddbc95fd571cf395089d`。

修正為 variant5=[0,0,0,2,0]，保留後續 S1A(0,1000,0)。282項測試通過；新的診斷GUI正測可見性與30秒後是否消失。Server測例的wire roundtrip只能證明編解碼一致，不能證明native欄位定位，需與實際reader/運行觀察並用。S1A動畫結束後的預設動作仍需長時間觀察，不因第一次看見就宣稱永久站立已驗。

使用者推測接受後應切另一教學地圖、再與NPC互動。原始 Join 文案確實指向初級學校，但腳本未提供 map_ref；此線索與原服精確綁定仍分開記錄。


## 最新實機結果與動畫／頭像修正

使用者確認第四個byte修正後NPC可見、30秒後仍存在，且能對話接受。使用者另回報初段動畫很慢、後來正常，以及對話框無NPC頭像。30秒只是人工觀察時間，沒有Server定時切速。

原件動畫排程0x56FCF0：0x56FD4E讀浮點參數，0x56FD58乘VA0x613220的double0.01，後續將累積frame時間乘該倍率後排程。舊S1A參數1000造成10倍時間，新設定S07 word與S1A parameter都用100（100%），不再把該欄當未知毫秒值。

動畫指令 Evidence：`ev_19a2547b4704534a3b054210f2a20d2fb9a385ee074fa36d2b0a8abe31e4cb59`。

原始MerchantDialog_Create與QuestDialog資源明定TILE在有效範圍時讀Portrait.dat，(TILE-16384)/10選informationNN.ypf，餘數選object，frame0。TILE0刻意不建portrait，解釋截圖的左側空框。現改為4037十六進位／16439十進位，選information05.ypf/object5/frame0；該原件YPF有10個channel。Portrait.dat SHA256 `541c34a97867b57949b7e3350cda43c3a503a5f8f9b3b042ef73d7fa43040432`，啟用前新增整庫hash核對。這是候選helper配套圖像的復原版設定，並非找回原服NPC實體表。

Server282項測試、原生新角隔離TCP與持續啟動器跨重啟／key輪替檢查通過。100%動畫與頭像仍待合併實機驗收；完整教學／學校傳送仍未完成。後續可改用[持續開發環境](../02-server-planning/persistent-local-development-20261101.md)，不用每次重建帳號及管理key。
