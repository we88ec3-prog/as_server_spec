# A-020 / roy1 — 登入前 Metadata／Script／選服／條款分支（BIN-first）

- 日期：2026-10-31；Branch：既有 `task_a/roy1`；不建立分支、不修改原始遊戲檔。
- 原件：`Asgard.exe`，PE32 x86，ImageBase 0x400000，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
- 原始證據：`objdump -D -M intel`、PE .rdata 中 UTF-16 packet 檔名字串與**緊接在其前**的 packet vtable（以相應 constructor 中安裝的 vtable VA 交叉驗證），再對照 A-001/A-002/A-023 的研究。
- Evidence ID：`ev_a020_20261031_asgard_prelogin_branch_static`。性質：**observed-static**；本機登入 profile 已有 **prior manual-pass-subset**，不是本輪 native E2E。A-020 `integrated/handoff_status=partial/native_client_validation=not-run`；`implementation_ready=true` **僅對已證序列化/解析的受限分支和明示 designed 的 Server fail-closed 協定**。原版 Server 的先後次序、異常錯誤碼與地區 key 選擇仍未知。

## 1. 重要交叉核對：保留既有 packet 類別/opcode 正確映射

容易誤判的陷阱：.rdata 裡 packet RTTI/vtable 是緊貼**下一個** UTF-16 `./packet/<class>.cpp` 文字路徑之前，而不是之後。必須用 constructor 內 `mov [this],vtable` 與 `push opcode → 0x578600(C2S)/0x578730(S2C)` 雙重交叉驗證，不能拿檔名字串後面那個 vtable 指認本類。

|Opcode/direction|原生類別|Constructor/reader-writer|BIN 分支結果|
|---|---|---|---|
|C0F|CMetaData|ctor `0x5739c0` push0x0f，writer `0x573a70`|先 `u8 type`；**type=3 時 body 只有此 u8**；type≠3 寫 `u8 option,string8 text`|
|S18|SMetaData|ctor `0x582c60` push0x18，reader `0x582dc0`|先 `u8 kind,u8 subtype`；**kind=0** 時讀 `BE u16 count`、重複 `string8 name,BE u32 value`；**kind=1** 時另走 `string8 name,BE u32 value,compressed content helper`，其他 kind 沒有本次已證的通用 payload|
|C57|CMultiServer|ctor `0x573e90` push0x57，writer `0x573f40`|先 `u8 type`；type=0 再 `u8 selected_id`；type=1 只送 type；其他 type 會將 packet internal result/status 清零，不應視為有效 selection|
|S56|SMultiServer|ctor `0x584040` push0x56，reader `0x584190`|原始 wire 是 **compressed block**，解壓後先 `u8 count`，每個 entry 依序 `u8 id,BE u32 IPv4,BE u16 port,u8 flag,3×string8`；既有本機僅測一筆|
|C4B|CStipulation|ctor `0x575670` push0x4b，writer `0x575720: ret`|**空 body**。由此不能單憑 C4B 判定原服公告語意或請求次數|
|S60|SStipulation|ctor `0x5870e0` push0x60，reader `0x587190`|先 `u8 type`；**type=0 → BE u32 value**；**type=1 → zlib/compressed string helper**（本 profile 使用 `BE u16 compressed_len,zlib NUL CP950`）；其他 type 進 Client 非成功/早退路徑|
|C6C|CScript|ctor `0x575140`、writer `0x575210`|subtype0/1/2/3/4 的完整欄位由 A-023 已證；最小登入時 C6C(3) 不等同 Script start|
|S44|SScript|ctor `0x5862e0`、reader `0x586410`|type1/subtype0 start、1 update、2 stop、3 **會刪/清 Script 快取**、4 checksum list；type2 是其他對話流程，非通用 ACK|

### 特別注意既有登入 fixture 的語意

原已手測本機 profile：
```text
C6C body03                       -> designed: no response in minimal login
C0F body03                       -> S18 body 00 03 00 00
C57 body01                       -> S56 single-list zlib body
C57 body00 00                    -> S60 local notice
C4B empty                        -> S60 local notice (local compatibility mapping)
```
以原生解析器再核：**S18 的 `00 03 00 00` 為 `kind=0,subtype=3,count=0`**，不是錯誤地把 S18 當其他 packet。原 Client 會以 type0 讀 `count=0`（`0x582dfd..0x582e37`），不會執行 kind1 內容解壓。`C57 type0/1` 與 S56 entry layout 也有原生函式依據。`C4B` 在最小本機 profile 被當作追加公告請求是**本機 Server 的 handler 映射**；從 C4B serializer **無法證明原服必回 S60**，不得把 local behavior 寫成 original Server 契約。S60 type1 本機測試公告是可用的例子，不代表它是原版條款或所有 region 固定公告。

## 2. C0F 請求分流、S18 成功/失敗界線

**C0F** (`0x573a70`) 先以 `0x45AB00` 輸出 `[+0x18]`，只有當 type≠3 才多送 `[+0x19]` 與 `string8 [+0x1A]`；因此 `03` 的最小 fixture 有原版實作直接支持。其他 type 的 option/text 用途、原伺服器回覆映射和允許時間 **unknown**，不能因 schema 可寫就自動代表完整服務。

**S18** (`0x582dc0`) 先收兩個 byte `kind/subtype`。kind=0 讀 `count:u16_be` 並對每一項讀 `string8,u32_be`，可比對本機空清單 `00030000`。kind=1 讀文字欄、u32，再進入 compressed payload helper `0x45BB00`，需要隔離 test payload/reader 長度和記憶體上限後才能擴充；不要把此分支寫成 kind0 的 list。其他 kind 在原件現有 reader 跳離分支，語義不明，Server 自訂處理 fail closed，不發原生未知 status。name/u32 的業務語義尚未確證，不把 CRC/name 的命名猜測變成原服確定 metadata 認證。

## 3. C57/S56 選服、公告 C4B/S60

**C57** (`0x573f40`) type=1 只有一個 byte，type=0 再送 selected_id byte；對非0/1 原生 writer 不是合法未知擴充，會重置 packet 內部結果狀態。Server 只應在版本協商/清單狀態與 id 有效後回 S56 或處理選服。不可由 C57 body01 推斷唯一的官方 server list。

**S56** (`0x584190`) 呼叫 `0x45AF30` 讀取壓縮資料，`0x45B020` 在內層 reader 開始解碼；count 是 **u8**，entry `u8,BE u32,BE u16,u8,string8,string8,string8`，本機 `S56` 已知 fixture 只有一項且 CP950 名稱是測試資料。原生列表可有多項，但 byte counts/壓縮大小/總長必須 Server 端明確限制，不能憑原 Client 曾分配 1 MiB buffer 就接受任意 zip bomb。

**C4B** (`0x575720`) serializer 空 body；**S60** (`0x587190`) type=0 在 `0x58727d` 讀 u32；type=1 在 `0x5871d9..0x587267` 讀 zlib 壓縮文字並轉 Unicode。本機 local notice 是 type1 一種 fixture，不能用它覆蓋原生 type0 的變體，也不能把 type=0 的 u32 解釋為成功/退出原服認證。

## 4. Script lifecycle：A-023 已證，不重做、不誤標登入權威

A-023 roy2 已實證 `S44(1,0)` 會以 name/context/main text CRC/依賴/參數執行本地 Script.Main；缺依賴時 `C6C(0)` 要求資源，`S44(1,1)` 更新後再啟動。Born+PaperDialog OK 產生 C6C4，再依未 replied 狀態 C6C2（Client send call order）。`C6C(3)` 可出現在最小登入，但不是「啟動 Born」；`S44(1,3)` 有清理本地 Script/*.dat 副作用，**不得當作通用空 ACK 或直接向真 Client 發送測試**。unknown Script subtype、CRC 不匹配、壓縮內容異常一律安全拒絕/隔離，完整欄位和風險以 `task_a/roy2/A-023-script-entry-contract.md` 為唯一已整合參考。

## 5. Server 可交 DEV 的相容狀態機（designed）

```text
Connected → raw greeting → C62 signature → C00/S00 seed+version negotiated
  → C6C(3) minimal allowed no-op (no quest/start)
  → C0F(3) → S18(kind0,subtype3,count0) → MetadataSatisfied(local fixture)
  → C57(1) → S56 zlib list → ListPresented
  → C57(0,id) → SelectedServer
  → C4B(empty) → optional S60(type1,local notice) → LoginReady
  → C03 credential verified → S02 failure OR S03 transfer → C10 World
```
箭頭是**本機可用 profile/設計**，不是從原 Client alone 證明唯一的原服時序。可允許特定 profile 多入口/重試，但要寫白名單狀態轉移；不存在的先後/未知 region key 不得全域接受。之前通過的最小 profile 不應因本次靜態研究直接被替換成假想原服序列；新增的 kind0 list、C0F 額外欄、S60 type0 是 codec/分支測試，**未有 native Runtime**。

安全：版本不符、非法 C57 選擇、超出長度/壓縮比或 Script 資源版本 mismatch、C0F subtype 不合 profile、C4B 在錯誤會話階段、未驗證帳密的 C03/World 要 fail closed。S18、S60、S56 的 compressed 結構必須用上限 + 完整消耗檢查；Session 認證只靠 C03 VerifiedCredential/transfer grant，Metadata 和空 Script reply 都不產生 owner 權限。禁止將 C0F 文字欄記 log（可能含敏感／未確證資料）。

## 6. 已解與未解、完成關卡

**A-020 的已證靜態研究**：C0F type3 vs other、S18 kind0/kind1、C57 0/1、S56 多 entry、C4B 空 body、S60 type0/type1、C6C/S44 由 A-023 引用。下游 `CT-049`/ `CT-050` 針對 codec、未知/錯序 fail-closed、壓縮負面案例的合成測試。

**不因缺新 Server E2E 取消既有研究成果**，但未解需明列：
1. 原服 region seed/key 選擇、S00 非零分支真正 UI 及其 metadata 開始時機（屬 A-001 的殘餘）。
2. C0F type≠3 的 option/text 業務用途與對應 S18 kind1／其他型別的真實原服下發政策。
3. S18/S56/S60 壓縮資料每種發行版完整字串/清單、錯誤與重試策略；name/CRC/u32 真正語意。
4. 原版 Server 是否在 C57 selection 或 C4B 後送 S60，以及所有 region 的時序/timeout；沒有原服正負封包 trace 不能確定。
5. C6C/S44 原服首次腳本下發政策、缺檔/CRC 例外時原 Client 行為；A-023 的 Parser 不等於 quest 或 owner proof。
6. 尚未執行原版 Client 的各類正常/異常/重複 metadata/Script/選服分支（CT not-run）。

要將這些從 partial 變 native full-ready，缺的證據是**同一 Asgard.exe build 的原服登入/選服/metadata/Script 正負案例封包與 UI trace，或原 Server 該服務程式/設定**，不是重新索取已有的 Asgard.exe、Born.dat、Map0.dat、Map1.dat、Map2.dat。無法給出單一確定遊戲資源檔名來取代原服 policy，不能捏造缺檔名。

## 7. 可重現

```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x5739c0 --stop-address=0x573aa0 Asgard.exe
objdump -D -M intel --start-address=0x582c60 --stop-address=0x582f10 Asgard.exe
objdump -D -M intel --start-address=0x573e90 --stop-address=0x573f70 Asgard.exe
objdump -D -M intel --start-address=0x584040 --stop-address=0x5842f5 Asgard.exe
objdump -D -M intel --start-address=0x575670 --stop-address=0x575725 Asgard.exe
objdump -D -M intel --start-address=0x5870e0 --stop-address=0x587295 Asgard.exe
python3 tools/a020_prelogin_contract.py
```
不提交原版 executable、大量 dump、原始 Script/密碼或完整遊戲封包。
