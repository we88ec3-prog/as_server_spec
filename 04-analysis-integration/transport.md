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
 
## A-001 / roy1：十種 seed mask 與版本/字串靜態整合（2026-10-31）

[可稽核原生入口、公式、向量](../03-analysis-requests/A-001-roy1-seed-and-version.md)；[純 Python 合成測試](../tools/a001_codec_vectors.py)。對指定 SHA 的原版 Asgard.exe，seed 0..9 的 `0x53B630` switch 實際生成 256 項遮罩 `T[0..255]`（每個 byte 重複 4 次為 DWORD）；`0x53BB30` 重複 key 4 份並記長度；`0x53BE70` encode、`0x53BD90` decode、`0x53B8B0` word/尾部 XOR。

若 `L=len(key)`、`ordinal=o`、`block=(i//L)&255`，任意 seed=0..9 的一般 binary 封包 **body byte**：

```
cipher[i] = body[i] XOR key[i % L] XOR T_seed[o]
            XOR (T_seed[block] if block != o else 0)
```

此式對 seed0 退化成上述既有 `ordinal / block` 公式；body 不包括 opcode/ordinal，本地已知 C62 seed0 fixture `aa000662002f171902` 不變。seed1..9 向量是 BIN-derived **synthetic**，未宣稱全數原版 Client/Server 實機通過，且不得據此無條件接受任意 seed 或 key；Server 依已選用 profile 驗證合法性。

C00 `0x577E80`：`BE u16,u8,u8,BE u16,BE u16` (8 bytes)；欄位語意尚未逐一確證。S00 `0x589B60`：先 result u8，result0 讀 `u32 opaque,u8 seed,u8 key_len,raw key,u8 message_count,string8...`；result1 先 string8 後多組清單，result2 先 u16 + u8 count + string8 清單。失敗時的 server 政策/UI 未完整還原，**不能把非零結果當成功**。`0x45B1B0 / 0x45B7A0` string8 的長度是轉碼後 **byte count 0..255**，codepage 依地區 profile（台灣已知子集 CP950）。`0x53C130 / 0x53C460` 有另一個 ASCII framing 分支，本次不宣告可互通；binary 與 ASCII 不能混用。

A-001 `integrated/handoff partial/implementation_ready` 指 **通用 seed0..9 binary codec 可開發**，原版版本拒絕語意、地區 codepage 及 ASCII 仍需要後續 A-020 / 開發後 CT/BUG 回饋。
