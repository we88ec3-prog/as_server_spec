# 台灣版binary、seed/table0 profile

範圍：已觀察的binary分支及預設key/table0。未完成的ASCII分支與seed1..9不得宣告支援。

1. Server連線問候是raw `1b 43 0a`，不是AA frame；Client轉binary後的第一包是C62，decoded body=`aram`且ordinal0。固定wire例：`aa000662002f171902`。
2. frame：`aa | payload_length:u16 BE | payload[payload_length]`。長度只計payload，不含3-byte frame header。TCP可切割任意位置或合併多frame。
3. plaintext例外：C2S opcode00、10；S2C opcode00、03。其payload為opcode+body，沒有ordinal。
4. 其他payload為opcode+ordinal:u8+XOR(body)。方向不能混用。每條連線維持自己的wire ordinal；移動的7-bit sequence是另一個欄位。
5. table0預設key bytes=`NexonInc.`。對body第i個byte，block=floor(i/key_length) AND 255；輸出=input XOR key[i MOD key_length] XOR ordinal XOR (block若block!=ordinal，否則0)。此式僅定義本profile，不適用其他seed表。
6. 多byte整數依欄位指定；一般stream為BE。S03 address應按已有0100007f向量確認host語意，不從hex外觀猜整數IP轉換。
7. string8=u8編碼後byte數+CP950 bytes，不含NUL。另有string16，不能混用。對非法編碼、截斷、長度超限、狀態不合法必須明確拒絕。

原型採payload最大0x3fff，是實作界限，不是原Client上限的證據。各實作應公告自己的界限，測試工具不可把此值寫成原服限制。加密key、密碼與token不得進入一般分享log。

原生入口：發送0x53c460、接收0x53c130、XOR0x53b8b0、string8 0x45b1b0。更完整版本協商待A-001。
