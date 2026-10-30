# A-001 / roy1 — Asgard.exe 原生 transport seed0..9、版本分支與字串（BIN-first）

分析日期：2026-10-31。樣本：使用者提供的 **Asgard.exe**, PE32/x86, ImageBase 0x400000，檔案大小 3,235,840 bytes，SHA-256 = `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。既有 profile：`TW-seed0-local-v0.1`。證據 ID：`ev_a001_20261031_asgard_seed_tables_static`（observed-static），實際原版登入測試未新增。依 00-governance/phase-gates.md，分析可 integrated / handoff partial，不要求新 Server 實機 CT 先通過。

## 1. 結果摘要

原本 A-001 為 open、evidence_ids 空，只有 04/transport.md 的既有 seed0 最小子集。本次**實際查驗此 SHA EXE**，找出 0..9 的 switch / 256 元素遮罩生成函式與 XOR 編碼/解碼，將 seed0 推廣成十個**可自動驗證的候選 native codec profile**；另補 C00、S00(0/1/2)、ASCII 分支及 string8 writer/parser 的證據界線。

已確認：seed0..9 mask generation、一般 binary frame 的 `AA + payload_length:u16 BE`、opcode+ordinal+encoded body、串流 XOR 公式、C00 8-byte body 寬度、S00 0/1/2 parser 分支、string8 的**編碼後 byte 長度**。仍未知：原伺服器在何版本/region 選哪個 seed/key、完整 S00 拒絕語意、ASCII on-wire 相容解碼、版本欄位全部定義。因此 **integrated / handoff_status=partial，僅已證部分可直接交付**；沒有把分析 partial 等同 blocked 或把合成測試等同 runtime。

## 2. 函式與原生位址（VA，非檔案 offset）

| 地址 | 由原始 BIN 觀察 | 確定性 |
|---|---|---|
| `0x53B630` | 接受 seed index；`cmp edx,9` + 跳表 `0x53B734`，迴圈 `esi=0..255`，每項結果重複成 4-byte word 存到 `[this+0x140e4+i*4]` | observed-static |
| `0x53B734` | 10 項 jump table 指向 `0x53B65B,662,667,673,694,69E,6B0,6B4,6CD,6E2`（完整 VA 加 0x53B000） | observed-static |
| `0x53BB30` | 取金鑰文字的 NUL-terminated byte 長度，複製 **4 份**至 `this+0x140b4`，`this+0x140b0` 為 key length | observed-static |
| `0x53B8B0` | 按 4-byte mask 循環 XOR，含剩餘 1–3 bytes 尾部，對輸入長度非 4 倍數也處理 | observed-static |
| `0x53BE70` | binary encode：先寫 opcode + ordinal（`this+0x140ae` 每包遞增），後三層 key/每個 key-length block/ordinal mask XOR | observed-static |
| `0x53BD90` | binary decode：從 incoming opcode/ordinal 取對應 mask，逆向相同 XOR 三層 | observed-static |
| `0x53C460` | 由 `this+0x90` 分 binary/ASCII 出站；binary frame 寫 `0xAA`、BE payload length；opcode 0 和 0x10 走不加 ordinal 的特殊 raw payload | observed-static |
| `0x53C130` | binary 入站狀態依 `AA` 找 frame、讀 BE 長度、按 opcode decode 後派發；另一套 ASCII 分支識別 `*`、`.` | observed-static |
| `0x53C800` | socket dispatch 跳表；`0x53C8CF` 呼叫 `0x53BB30` 設 key，`0x53C8E9` 呼叫 `0x53B630` 設 seed mask | observed-static |
| `0x577E80` | C00 依序 `write_u16,write_u8,write_u8,write_u16,write_u16`（body 8 bytes） | observed-static |
| `0x589B60` | S00 首先讀 status，0→`0x589D60`、1→`0x589C2D`、2→`0x589B8F` | observed-static |
| `0x45B1B0` | string8 writer：Win32 codepage 轉碼後計算 byte 長度，最多 255 encoded bytes，寫 u8 長度再寫 bytes | observed-static |
| `0x45B7A0` | string8 parser：先讀 u8 encoded length，檢查剩餘資料量，轉碼至輸出 | observed-static |

Seed switch 裡的 `esi=i`、`ebp=2*i`、`edi=255-i`。表內「元素」是 **同一個 u8 複寫四次的 DWORD**；程式 mask 運算的值應取其低 8 bits。不是十張外部下載表，也不是 10 個固定 XOR 常數。

## 3. 十張遮罩表精確生成式

令 `i=0..255`、`u=2*i`、`tdiv0(x,d)=truncation_toward_zero(x/d)`。表每項先取 u8；在原 Client 中複寫至 4 bytes：

| seed | `T_seed[i]`（0..255）| BIN 分支 |
|---|---|---|
| 0 | `i` | `0x53B65B` |
| 1 | `128 + (-1 if i odd else +1)*floor((i+1)/2)` | `0x53B662→675` |
| 2 | `255-i` | `0x53B667` |
| 3 | `128 + (-1 if i odd else +1)*floor((255-i)/2)` | `0x53B673→675` |
| 4 | `(i>>4)^2` | `0x53B694` |
| 5 | `(2*i) & 0xff` | `0x53B69E` |
| 6 | `255 - ((2*i)&0xff)` | `0x53B6B0→6F3` |
| 7 | `255-2*i if i<=127 else 2*i-256` | `0x53B6B4` |
| 8 | `2*i if i<=127 else 511-2*i` | `0x53B6CD` |
| 9 | `255 - ((tdiv0(i-128,8)^2)&0xff)` | `0x53B6E2→6F3` |

**重要**：seed9 使用 x86 有號整數除法的 toward-zero 效果，不是 Python 對負數的 floor division。`0x53B64B` 的 seed >9 會略過上面跳表而保留其他值；該路徑沒有已驗證協定語意，本相容實作 **拒絕 seed >9**，不假裝未知 seed 有效。seed0 的 `T[i]=i` 對應舊版 transport.md 的 ordinal/block XOR；不是全零表。

十張 `T` 的**前 12 bytes**及完整 256-byte SHA-256（用於獨立比較）：

|seed|前12 byte hex|SHA-256|
|---|---|---|
|0|`000102030405060708090a0b`|`40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880`|
|1|`807f817e827d837c847b857a`|`9928e9c8bc8135d230139fc07490277429a6f3ccdfb5e71d3d3c052f526baee4`|
|2|`fffefdfcfbfaf9f8f7f6f5f4`|`cd6816b77f68d70001fc3eaa4d42bdd67cb5973b3151cc5292ecc02a3daac6ab`|
|3|`ff01fe02fd03fc04fb05fa06`|`ea45b66f266752a18712d6ad62fc6a40fd26039d601e67b7d0b60da29a54bc0a`|
|4|`000000000000000000000000`|`6c0b229c4b4bb0d4c5b0d8be465a491b034167557629a32a363de03de899f62c`|
|5|`00020406080a0c0e10121416`|`65dec14522fe046d969c58f32f7bbfb486ceb48378d7b89c22b2f152b229cdba`|
|6|`fffdfbf9f7f5f3f1efedebe9`|`63f1ebfc2efe0b94a165ba3da8d1e0459def42b8d53d11467e45abbad1830e21`|
|7|`fffdfbf9f7f5f3f1efedebe9`|`9d61788315757a5a4945c92455032859e0379aa963174b9c355aec781daea37f`|
|8|`00020406080a0c0e10121416`|`b2dab527d5b3533b06dd606b34f65dd880cb52870326ee05eeeddc11714c5ad4`|
|9|`ff1e1e1e1e1e1e1e1e3b3b3b`|`80682999340209d29522e975c9eb32a2b6e03f886572536f43670daa679301ea`|

## 4. Binary frame & XOR：body-only 可實作公式

前置 plain greeting fixture `1b 43 0a` 後，正常 binary frame：

```text
AA | payload_len:u16 BE | payload (payload_len bytes)
一般 payload = opcode:u8 | ordinal:u8 | encrypted_body
例外 C2S opcode 00/10；S2C opcode 00/03：payload=opcode:u8 | raw_body
```

opcode 例外集採原有 `transport.md` 的方向特定 profile；BIN 的 socket codec `0x53C460` 另明確有 opcode 00/0x10 不加 ordinal 分支，方向與完整上層選擇仍按 profile 分離，不能因此宣告兩方向皆一律相同。

對 body 第 `i` 位（從 0 起），非空 key 長度 `L`，ordinal `o`（u8）、`block=(i//L)&255`，十種 seed 的合成 XOR：

```text
cipher[i] = plain[i] XOR key[i % L] XOR T_seed[o]
            XOR (T_seed[block] if block != o else 0)
```

`0x53BE70` 先以 key 遍歷 body，再以各 block mask XOR（block 等於 ordinal 時跳過），最後整體 XOR ordinal mask。解碼 `0x53BD90` 執行對稱逆操作。封包本身的 opcode/ordinal 不包含在 body XOR 範圍。socket 每個連線維持自己的 ordinal；不能用步行的 7-bit sequence 替代。

**已知原始相容 signature fixture**（seed0、key `NexonInc.`、ordinal0、body `aram`）：

```text
plain body = 61 72 61 6d
cipher body= 2f 17 19 02
full wire  = aa 00 06 62 00 2f 17 19 02
```

seed 1..9 的其他全部向量是 **BIN 推導出的 synthetic fixtures，非 Wireshark/原服捕獲**。同一 body `aram`、ordinal0 下，cipher body 依 seed 0..9 為：
`2f171902,af979982,d0e8e6fd,d0e8e6fd,2f171902,2f171902,d0e8e6fd,d0e8e6fd,2f171902,d0e8e6fd`。

為驗證跨 key-length 邊界及 ordinal=2 的區塊差異，取合成 body `00..13`（20 bytes），seed0..9 ciphertext：

```text
0 4c66786e684e6a6624446c7060604462703c5e74
1 4f657b6d6b4d696527b9918d9d9db99f8dc1ddf7
2 4c66786e684e6a6624446c7060604462703ca18b
3 4f657b6d6b4d696527b8908c9c9cb89e8cc0a288
4 4e647a6c6a4c686426476f7363634761733f5c76
5 4a607e686e486c60224169756565416775395872
6 4a607e686e486c6022416975656541677539a78d
7 4a607e686e486c6022416975656541677539a78d
8 4a607e686e486c60224169756565416775395872
9 af859b8d8bad8985c7476f7363634761733f4268
```

對上述輸入做二次 XOR 可精確還原原 body，另測試 ordinal 0/1/2/9/127/255 與跨 256 mask block。見 `tools/a001_codec_vectors.py`，可用標準 Python3 執行。

## 5. C00 / S00 版本協商和拒絕路徑

- C00 `0x577E80` **8 bytes**：`BE u16 f0, u8 f1, u8 f2, BE u16 f3, BE u16 f4`。從 serializer 可證寬度/順序；**尚不可把 f0..f4 命名為準確版本／區域／修訂語意**。
- S00 `0x589B60`：先讀 `u8 result`。result 0 經 `0x589D60`：`BE u32 opaque_value, u8 seed, u8 key_len, raw key[key_len], u8 message_count, repeat string8[message_count]`。`u8+key bytes` 在結構上等同 string8，但 key 是 codec bytes，不應經無根據的 CP950 轉碼。
- result 1 `0x589C2D`：先 `string8`，後含多組以 u8 數量引導的 string8 清單；具體 UI 意義 unknown，不得回 S00(result1) 模擬「一律成功」。
- result 2 `0x589B8F`：先 `BE u16`，再讀 `u8 count` 和每個 `string8`，意義 unknown。其他 result 進 default path，仍可能讀尾隨 message list；不應將其他值默認成功或無條件清理。
- 已測本機最小 profile `S00 body=00 00000000 00 09 4e65786f6e496e632e 00` 使用 seed0、key `NexonInc.`。原 Client 發送 C00 後改用何 seed/key 的**完整**生命週期、錯誤版本跳轉/提示與不同 region 策略尚未有 runtime 證據，屬 A-020（前置/公告/Script）交叉分析，暫不得宣告所有十種 seed 的 E2E login 都已通過。
- Parser 不會替 Server 安全性兜底：不支援的 seed/key/result、過短 body、key 長度為 0、過長封包、沒有前置狀態的 C03，都應以**designed 的嚴格 profile 政策**拒絕；不能把未觀察到的原服錯誤碼寫死。

## 6. 字串型別、語系與長度

`0x45B1B0` 透過 Win32 文字轉碼 API 將來源字串轉成 wire bytes（使用程序內 codepage global `0x66E47C`），encoded length **clamp 至 255**，前置 **u8 長度**。`0x45B7A0` 先讀 u8，再按剩餘長度讀/轉碼；它不是固定 255 個 UTF-16 字元，也不含 NUL。台灣最小 profile 依既有研究採 **CP950**；其他 region codepage 須透過來源配置確認，不能自動套用 CP950。合成 `中文` 以 CP950 編碼為 `a4a4a4e5`（4 bytes，非字元數2）。另有 string16 寬度/用途，不得與 string8 混淆。

發現編碼失敗、U+ 不可轉碼、encoded byte 超限時正式 Server 依自訂保守政策拒絕，不得截斷不同使用者帳號到相同位元序列。此為 **designed** 安全性策略（Client writer 可以截到 255）。

## 7. ASCII framing 分支與未解範圍

`0x53C130` 接收端 mode `[this+0x90]` 分流 binary `AA` 與 ASCII `*`/ `.`。`0x53C460` 另一輸出分支使用 `0x2A`、`0x3B` 偏移的 6-bit text packing 和序號字元（`0x53C5B3` 起）。**證明分支存在，不表示 ASCII 完整可互通**。此專案宣告只支援 binary profile；如需 ASCII，必須額外解碼/編碼 fixture、錯誤/長度測試及新 profile，不可混用同一條連線的 frame state。

## 8. 下游 DEV/CT 交接與剩餘未知

可以直接實作：十張 256-byte seed masks；依 seed/key/ordinal 的 binary XOR、C00/S00(result0) packet codec、u8 變長字串、frame 串流切割/黏包、key/seed 重協商的 state gating。**保守先用已人工驗證的 seed0/login profile；seed1..9 開始 codec/單元測試，但未曾原 Client 實機 E2E。**

建議測試：
1. `CT-002` seed0 C62 known fixture，全部 TCP split/coalescing；
2. `CT-A001` 工具內 0..9 mask 指紋、cross-key/ordinal synthetic roundtrip，明示不作 runtime 通過；
3. C00 8-byte 精確欄位、S00 result0 keylen/count/seed0/不支援 seed 門檻；非零 result 應保持明確拒絕，不假成功；
4. CP950 byte 長度、空字串、非法編碼、encoded 255 邊界；ASCII * / . 不在 binary profile 接受；
5. 已建 Server 後，再由 CT 接原版 Client 查 seed1..9 版本宣告/拒絕，發現 mismatch 回開相應分析及 DEV issue。

待續 A-001 或 A-020：原版 S00 非零結果每個 UI 文字/轉場語意、各 region 實際 codepage、seed/key 選擇策略、ASCII 完整格式。缺實機 **不是**本輪 BIN-first 分析結案障礙；有具體未知則 `handoff_status=partial`，不能假充完整原生行為。
