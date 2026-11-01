# 地圖標題的來源與城鎮身份驗證

本輪以REA重查原始Asgard.exe（SHA256
`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`）。
工具提供Ghidra靜態結果，沒有執行Client或改動EXE。
[精選機讀證據](native-map-title-provenance-20261101.json)保留Evidence ID、
provider／analysis profile及限制；完整原始輸出留在本地分析暫存區。

## 正面讀取證據

1. S15 reader `0x57ff30` 依次讀三個u16、兩個u8與字串，字串目的地為
   reader物件`+0x2e`。這與既有S15契約一致，並非新增封包欄位。
2. 派送入口`0x4f48a0`讀取參數物件`+8`並減3。對opcode0x15而言索引18，
   `0x4f4b30+18`的byte是0x11；跳表`0x4f4a78+0x11*4`（0x4f4abc）
   的LE指標是0x4f48ca。該分支把EAX保留作參數、載入MapPane指標，
   `0x4f48d4`跳至`0x4bd750`。此處依指令與資料表核對，未把provider
   未建立的函式邊界當作已存在函式。
3. `0x4bd750` 以handler參數`+0x24`選圖，並把`+0x3a`文字傳給
   MapData建構子`0x4b33a0`；換圖分支也將同一文字傳給名稱視窗
   `0x4b3e50`。reader與handler使用不同基址，不把它們的欄位offset直接混用。
4. `0x4b33a0` 把傳入map_ref保存到MapData`+4`、傳入文字複製到`+6`，
   再以map_ref格式化`%05d.map`讀取素材庫。名稱先由呼叫參數提供，
   這條建構路徑沒有從MAP header反查城市文字。
5. `0x4b3e50`接受文字及顯示時長；時長-1走4000的預設值。
   它不依文字核驗實際MAP，不能把名稱視窗當作城市身份驗證器。

關鍵證據：reader `ev_b59329b3579a3d327647ad2aafeb5f44a68a4a120bdbc4e1d9a5a07304338889`；
MapPane `ev_9106f9d4342fa6cc8801822092929e636bfcf0645b8b11588d612f92b2484709`；
MapData `ev_aa370ad5a14bbecf7250c46192c0fa73f984fd3a07e1b7542b37b90543ee5979`；
名稱視窗 `ev_56f6a10f0445d8b32ee9e11162f3d7ce9c907e1727b62ed0b4a8ac423cece669`。

## 對目前復原Server的影響

Server可以在S15提供名稱，因此畫面出現「路爾斯」或其他目標城鎮名稱，
只能證明名稱投影，不能證明該map_ref就是同版原服的城市。
目前候選名稱由復原設定提供，屬Server設計；不應把自己設定的文字
再當成原始資料的獨立佐證。

完整教學驗收須分開記錄：傳送協議／角色位置／職業保存、場景正常可行走、
原版城鎮身份。前兩者可由實機流程及持久資料核對；第三者需同版綁定或
可追溯的場景／地標證據，不能只看標題。現有五職業候選仍保持未確認。

這是已追查路徑的正面結論，**不是**整套Client沒有其他地名表的負面證明。
Locale／WorldMap metadata、其他UI或資源仍可能另有資料；原服metadata尚缺。
本輪不改S15格式、使用者地圖配置、帳號、角色、金鑰或測試環境。
