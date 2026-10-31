# A-031／roy2 — C10 後真正 C25 與 World 入口的原始 Client 證據

> 日期 2026-11-01。**original executable BIN-first**；分支 `task_a/roy2`（先 fast-forward 合入 `main@684bcac53207636244b9dfede458b80bbb8efbc6`，不新建分支）。Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`、PE32 ImageBase 0x400000。不修改 EXE 或交付其原始碼／素材。

## 1. 關鍵更正：C25 的真實類別是 CBillingInfoPacket

- 原件 **`0x5712E0`** packet ctor，在 **`0x5712F9` push 0x25**，底層封包 ctor `0x578600`；同時指派 packet vtable `0x61360C` 與 writer vtable `0x613600`。
- native vtable 的 RTTI CompleteObjectLocator `0x62BB84` → TypeDescriptor `0x6692A4` → **`.?AVCBillingInfoPacket@@`**。這不可能只憑「WorldEntryMetadata」名稱臆測出來。
- **`0x571420`** 是其 native writer：查 Region getter `0x498000`，**`cmp eax,3`**；Region !=3 直接返回而不寫 body。Region3 則依序對三組本地 UTF-16 欄位呼叫 `0x45B1B0`（Native encoded `string8` writer），最後返回。
- `0x45B1B0` 依 Client 目前的 LanguageMan codepage 調 Windows `WideCharToMultiByte`，寫 **一個 u8 encoded-byte length + N encoded bytes**，N 上限255；不是 `u16`、固定 255B padding、也不是原始 UTF-16 on-wire。用 TW profile CP950 是相容候選，**不可硬寫所有地域版本必然 CP950**。
- 因此原規格 **`PKT-C25 name=WorldEntryMetadata` 是過度推論**。Opcode0x25 本版原生類別實為 `CBillingInfoPacket`，不是傳 map_id/map_revision、也不是獨立驗證帳密的權威封包。

### C25 decoded payload（只在 Region 3 的已證原生 sender）

|wire offset|資料型別|原始 sender 0x4A8370 的來源|原生 local C25 packet 欄位|原版語義|
|---|---|---|---|---|
|0|`u8 L0`|global `[0x66D100]+0x0C` 的 UTF-16 字串|+0x18|**opaque billing string 0**，不是已證帳號|
|1…L0|`L0 encoded bytes`|同上|同上|目前 codepage|
|1+L0|`u8 L1`|global `[0x66D100]+0x20C` 的 UTF-16 字串|+0x218|**opaque billing string 1**，不是已證密碼|
|…|`L1 encoded bytes`|同上|同上|不能擅自比對 login credential|
|2+L0+L1|`u8 L2`|global `[0x66D100]+0x40E` 的 UTF-16 字串|+0x418|**opaque billing string 2**|
|剩餘|`L2 encoded bytes`|同上|同上|不含 NUL/padding；原版欄位業務意義尚未證|

**Region3 C25 decoded body 長度：`3 + L0 + L1 + L2` bytes（3..768）；**每個 L0/1/2 0..255。即使三個欄位都是空字串，body 仍為 `00 00 00`（**不是**無 body 的 C25，也不是 `01`）。非 Region3 的函式 writer 理論上返回空 body，但已定位的全部四條**直接呼叫**都檢查 Region3，**所以不要從 serializer 支援空 body 推論其他 Region 的 Client 一定送出空 C25**。

## 2. 原生 C10→C25 真正順序（兩條獨立路徑）

### A. Login／S03 的 Region3 轉服 callback：`0x4A8370`

|VA|原始動作|Client/Server 含意|
|---|---|---|
|`0x4A8391`|`0x498000` 取得 Region，`0x4A8396` compare3|region3 才走本函式 C10+C25 的此分支；non-3 另有 UI/transfer branch|
|`0x4A83A3..`|從 S03 local packet 取地址 `[+0x24]` 與 port `[+0x28]`，呼叫 `0x53B300/0x53B360/0x54C4F0`|依 S03 建新的 TCP transfer destination；後續 check connection state|
|`0x4A8415`|建構 `CTransferServerPacket` (`C10`) `0x577330`|原始下一個 World C2S opcode0x10|
|`0x4A8426..0x4A8446`|複製 S03 `token_len=[+0x2A]` 和 raw token `[+0x2B...]`，呼叫 `0x5788A0`|C10 payload 為 raw opaque token **不加第二個長度前綴**|
|`0x4A8478`|`CBillingInfoPacket` ctor `0x5712E0`|建 C25|
|`0x4A8491..0x4A84E0`|從 global `0x66D100` 讀三段 wide 字串，複製至 C25 local +0x18/+0x218/+0x418|`0x5B364D` 拷字串，最大255 wchar；**來源位置已證，但三欄 UI label / credential purpose 未證**|
|`0x4A84F3`|call `0x5788A0` 送 C25|**同一 Region3 handler，C10 enqueue 後接 C25 enqueue，中間沒有等待 S02**|

### B. 第二條登入／轉服路徑：`0x52FAD0..`

- `0x52FB59/0x52FB5B` 建 C10、`0x52FB6C..` 複製 S03 token len/raw、`0x52FB8C` 送 C10。
- `0x52FB91` 執行本地呼叫 `0x4F1050`，`0x52FB96..0x52FBA4` 再查 Region3；如果是3，`0x52FBD6` 建 C25、`0x52FBE9..` 由 `0x66D100` 複製同三個 wide string、`0x52FC4B` 送出 C25。
- **Region !=3**：這條路徑只證 C10 queued（`0x52FB8C`），不走 C25；不等於所有非3 Client 的其後 World 協定已證。Region3 在 C10 與 C25 中間有一個**本地函式** `0x4F1050`，並非等待 S02。
- 另外兩個 C25 ctor direct caller `0x432259`（guard `0x432221`）、`0x4A92E2`（guard `0x4A92B1`）均明確 Region3，送出點分別 `0x4322D1`、`0x4A9357`。不能將其冒稱每次 C10 後均會送第二個 C25；可能是不同 UI/轉服狀態的重送／通知。
- 靜態 **已證直接 ctor xrefs 共四條** `0x432259/0x4A8478/0x4A92E2/0x52FBD6`。不排除 virtual/indirect 入口，原件完整 GUI/runtime 尚未追證。傳輸 framing/seed/ordinal 仍遵守原生 `0x5788A0` 通道及 A-001 transport；本研究只宣稱 **queued C2S decoded-body**，不猜當次 seed/ordinal 數值。

## 3. 何時進 World、Client 入圖反應與 S02 的界限

- C10 的角色身份由已認證 `C03→S03` 轉服 grant 控制（A-002），C25 三字串不能替代它；原生 Client 機制不等於 Server 應把其中一個字串當身份證明。
- **Region3**：至少上述 `0x4A8370` callback 先 enqueue C10 再 C25，沒有在這兩個送包點之間接收任何 S02／等待 S2C；**因此 Server 不得在中間硬塞「必須成功 S02 才會收到 C25」的規格**。本點不等於「S02 在轉服後所有情境都不會出現」。
- **Region !=3**：第二條 S03 callback 已確定 C10 可以單獨送出；沒有通用「C25=01」要求。原版 non3 UI 後續 S2C required order 仍待真 Client packet capture。
- **本研究未從 C25 直接確立 `S05/S15/S14→C35→S04/S33` 是否被哪一個 S2C 先喚起**：這些是 A-022 已證的後續 World-loader/角色呈現封包；但完整 `C10/C25→初始 World S2C` state transition、實際 map_ref/CRC、S02 failure result 都需專屬 native CT-108 或後續 native trace，不從 Client serializer 猜出原服的選擇與時序。
- 不會把本地 `0x4A8370` 再冒稱 C25 的 constructor。它是受 Region guard 的 **S03／transfer callback**；真正 C25 ctor `0x5712E0`／writer `0x571420`。

## 4. 實作建議交接（原生事實與 designed Server 分開）

|Dev decision / Client I/O|原始 Client 已證|Server **designed**、不得充當原服證據|
|---|---|---|
|轉服首包|S03 指地址+port+token，新 TCP `C10` raw token（S03 token_len 由外層 S03，C10 不自行多套 string8）|C10 一次性簽發/校驗角色、account/character、connection and world epoch，重放 reject|
|Region3 的緊接 packet|C25 `CBillingInfoPacket`、3 encoded `string8`，raw body `3+sum(N)`|可以解析並安全限制三欄大小，但**不可**直接當帳密、不可由 C25 自行建立角色/World session|
|非3 region|已證一些 Client transfer path 只送 C10，不送 C25|**不得**以缺 C25 拒絕正常已驗證的 non3 world entry；World loader 可依 Server 自訂流程推進，但 native GUI 必須 CT-108|
|原有 fixture|開發合成 `C25 body=01` **與原版 region3 serializer 不相容**|將 fixture 嚴格隔離 Dev-only，不得在 Native production route 吃 `01` 並標登入成功|
|C25 後服務端 S2C|沒有已證 C25→某一 S2C 的唯一必要關係，無證需要第二個 S02|由 Server 維持清楚 state/generation，按後續 S05/S15/S14/C35/S04 的 Client 相容依據輸出；先保留 native-first-world trace 未驗收|
|不合法/錯 region/C25 長度或語系|strict decode 的已證 wire 可重現；native Client failure UI 未跑|長度溢出、trailing bytes、重播、anonymous 必須拒絕；不要 fallback `01` 或改 C25 欄位含義|

**DEV-ENTRY-03 直接修正指令**：以 `C10` grant 成功作 World owner 的唯一入口；C25 僅在符合**region3 的 3×string8** 條件下作後續可讀 Client 資訊，Server policy 不以之重新認證。non3 C25 不應為必需。去除 native route 對 fake `body=01` 的依賴；不用把 C25 當 map ID 或自動觸發 tutorial_complete。實際 S05/S15/S14/C35 的時序用 CT-108 原生 Client trace 確認。

## 5. 可重跑的原件與合成驗證

```sh
python task_a/roy2/a031_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p "test_a031_world_entry.py" -v
objdump -d -M intel --start-address=0x5712e0 --stop-address=0x571485 Asgard.exe
objdump -d -M intel --start-address=0x4a8370 --stop-address=0x4a8500 Asgard.exe
objdump -d -M intel --start-address=0x52fad0 --stop-address=0x52fcd0 Asgard.exe
objdump -d -M intel --start-address=0x45b1b0 --stop-address=0x45b2a2 Asgard.exe
```

- `a031_native_probe.py` 驗證 SHA、**35 條 VA instruction signatures**，及 ctor vtable → RTTI CBillingInfoPacket（原生資料，不在 repo 上傳 EXE）。
- `a031_world_entry_codec.py` decoded-body bytes-only strict encoder/parser；`test_a031_world_entry.py` **20** 項正負向 synthetic：C10 raw、C25 3×string8、空字串 body `000000`、最大 255×3、CP950 raw bytes、每一 truncated offset、trailing、region3/非3 sender、epochless wire 界線。**不是** Native Client 擷包或 GUI pass。
- 證據 A031-E01…E09 與 CT-108 的原始 Client E2E（`not-run`）必須分開；不創造 Client packet／S02 success code／map/CRC。

## 6. 狀態與缺件

**A-031 靜態封包/C10→C25 路徑已取得，`integrated/ready` 限於 Region3 連續 sender 與 C25 decoded-body；`native_client_validation=not-run`。** 無法透過離線 EXE 宣稱已親眼看到實際網路封包，因此 A31 任務的「原版 Client 真正輸出 trace、Region0/1/2/4 成功 World 入圖、完整 first-S2C/錯誤 UI」留在 Native CT-108，而不是將合成 Server C25 當答案。

**沒有新缺的具名資料檔**：`Asgard.exe`、`Map0.dat/Map1.dat/Map2.dat`、`Born.dat` 已提供。若要精確驗證 World TCP **實際 wire bytes**、ordinal、seed、first S2C、失敗分支，缺的是同 SHA 的原版 Client **去敏 C03→S03→new TCP C10→C25/first response 擷包**（記 region、時間、Frame/Body Length 但遮罩 token、三個 billing 字串），非更多美術資源。
