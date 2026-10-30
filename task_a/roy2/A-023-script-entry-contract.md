# A-023：封包啟動、Born 依賴與關閉回送的完整 Client 契約

2026-10-31；分支／工作目錄 `task_a/roy2`。本頁取代舊報告對「觸發方式、S44 格式、Dispose 副作用尚未知」的結論。Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。所有 native 行為均為 **observed-static**，資源為 **observed-static-resource**；沒有聲稱原服抓包或 Client GUI 通過。

## 1. 首次教學是否由封包觸發？

**Client 有完整、已追通的封包啟動機制：S44(type=1, subtype=0) 指定腳本名稱及依賴，資源齊備後執行該腳本的 Main。** 名稱指定 Born 並提供 PaperDialog 依賴，就對應本地 Born.Main 的教學紙張。不是 C6C(03) 自己啟動，也不是 S14(2) 在本次已追鏈上硬編碼呼叫 Born。

|階段|位址與觀察|證據|
|---|---|---|
|收包路由|S44 ctor 0x5862e0；parser vtable 0x615590+4 指向 0x586410；既有 dispatch 0x4e0b79→0x52c2a0|E03、E14|
|解析 start|0x586410 起讀 type/subtype；1/0 讀名稱、兩 u32、依賴及參數|E14|
|資源檢查|0x52c2a0 的 1/0 路徑用 0x529060 檢查主資源／依賴的文字 CRC；缺少時以 0x5289f0 發 C6C(0,name)，在 0x52c53f 排入待啟動佇列|E15|
|立即啟動|資源齊備時 0x52c467→0x52bd30|E15|
|建立執行器|0x52bd30 載入主 XML、依賴 XML 與參數；0x52be8b→0x521c20。建構器會把依賴的 function 節點匯入主 document|E15|
|執行 Main|**0x52c014→0x524fa0**；0x525090 push L"Main"，0x5250b8 經 script object vtable 呼叫該函式|E15|
|缺檔後恢復|S44(1,1) 更新快取後掃待啟動佇列；所需名稱齊備才於 0x52c76b→0x52bd30，執行後移出佇列|E15|

反編譯器將 heap free 錯標為 no-return，導致 0x586410 未被辨識為函式，且 0x52bd30 的 pseudocode 漏掉 0x52c014 的 Main 呼叫。此次用原件 PE section 映射與 Capstone 5.0.6 逐條核查，不能沿用截斷 pseudocode 作為「沒有啟動」的證據。驗證工具保存有限 byte signatures，不提交完整反編譯或原件。

**不能從 Client 證明的是原服的發送政策**：原服是否只在首次創角後送 Born、首次判斷用哪個持久旗標、在 S14(2) 前後的精確時序，以及是否也在其他場合重送。這需要原服 first-login trace 或原服事件／任務設定；不需要先完成新的 Server，但 Client 靜態解析本身無法重建遠端尚未提供的政策。

## 2. S44 的 wire 格式

以下順序從 body byte 0 開始，**不含 opcode 0x44、ordinal、加密或 frame**。所有多 byte 整數為 BE：reader ctor 0x45ad70、writer ctor 0x45aac0 預設 endian flag=1；S/C packet 基底 0x578730/0x578600 分別使用這兩個 ctor。不是由 x86 memory layout 推定 wire 為 LE。

`string8` 為 u8 **encoded byte count** + bytes，wire 不含 NUL；使用全域 codepage 0x66e47c。LanguageMan 0x498420 依系統語系選索引，0x4984fa 寫 codepage；index 4 的表 0x60855c 指向 CP950。**下述中文字串／CRC fixture 明確以 index4/CP950 為條件，EXE SHA 不能單獨保證目前 runtime 一定是 CP950。** ASCII 名稱不受 CP950/CP949 差異影響。

|type/subtype|body 中 selector 之後的欄位|Client 效果|
|---|---|---|
|1/0|script:string8、context:u32、main_text_crc32:u32、dependency_count:u8、重複 (name:string8, text_crc32:u32)、parameter_count:u16、重複 (key:string8,value:string8)|檢查本地資源、缺檔請求／等待，齊備建立 runner 並呼叫 Main|
|1/1|script:string8、compressed_length:u16、compressed bytes|0x45af30 以 zlib 解壓，最大輸出 buffer 0x100000；按 codepage 轉 Unicode，更新 Script 快取、重試等待中的啟動|
|1/2|script:string8|定位 runner 後呼叫 0x519450 清理；可能產生 C6C(2)，見第 4 節|
|1/3|無額外欄位|0x5294e0 列舉／刪除 Script/*.dat；不是 start 或 ACK|
|1/4|count:u16、重複 (name:string8,text_crc32:u32)|檢查資源清單，缺檔發 C6C(0)；不等於啟動 Born|
|2/0|name:string8、context:u32、count:u16、重複 (key:string8,value:string16)|另一個對話資料路徑；value 使用 u16 byte 長度字串 helper 0x45b890；不是本次 Born XML 啟動路徑|
|2/2|name:string8、context:u32|原生對話 pane 控制路徑；不能當 Born 啟動|

memory offsets 注意：0x586410 parser 的 ECX 是 packet+0xc reader 子物件，故 `[esi+0x18]` 對應完整 packet+0x24；handler 收到完整 packet。不可把這些 memory offsets 直接當 wire offsets。

start 的 count 雖為 unsigned wire 型別，原件某些迴圈／配置使用 signed short（例如 parameter_count 的配置有 movsx）；Server 應限制到其實際允許的內容數量，不向原 Client 送 0x8000 以上的參數數量或不受控大小。離線驗證器的嚴格截斷／尾隨資料拒絕屬本專案測試規則，不冒稱原版所有錯誤處理完全相同。

另外不能假設 checksum mismatch 會安全返回 null：0x5291fe..0x529215 的原指令在 CRC 不相等時釋放 EDI 指向的文字，0x529254 仍將 EDI 作為返回值；本次未看到釋放後清零指令。這是靜態可見的潛在 dangling-pointer 路徑，實際執行後果未測；**不得對真 Client 故意用錯誤 CRC 試驗並期待它可靠重抓**。缺檔的 null 路徑與 checksum 不相符要分開。合成 start 使用精確匹配的資源 CRC，先離線比對。

## 3. Born 的最小資料與可重現向量

必要 Script 函式：Born.Main 與 PaperDialog 的 PaperDialog_Create、ShowIndexedHelp、PaperDialogProc。Born 不建立 NPC，不明確寫 quest flag；其一頁紙張引導往 (31,29) 點女性招募員。此座標不是 spawn 或已證 NPC 實體位置。

主／依賴資料的校驗不是 raw .dat hash：0x529060 將 zlib 解壓後讀 **BE u16 version=1、BE u32 UTF-16 code-unit count**，再讀 UTF-16LE XML；0x550910 將完整 XML 原文字串依 codepage 轉成 bytes；0x58a210 做標準 reflected CRC32（table 0x615a10、初值與結尾 complement；相當於 zlib.crc32）。不含結尾 NUL，不重排／重序列化 XML。過往「00010000 prefix + BE u16」是本批小檔案的等價外觀，現在已釐清 native 欄位實為 u16+u32。

|資源|raw SHA256|CP950 文字 CRC32|
|---|---|---|
|Born.dat|992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98|1d87b0c0|
|PaperDialog.dat|5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054|f870c574|

合成 start body（context **11223344 為自訂測試值**、參數 0、依賴 PaperDialog 一筆）：

```text
01 00 04 426f726e 11223344 1d87b0c0 01 0b 50617065724469616c6f67 f870c574 0000
```

這是從 parser 推出的固定 byte 向量，不是原服抓包，不代表已在 Client 成功顯示，也不含任何原遊戲文字／素材。主與依賴的發行版配對尚未獨立證明，仍須 hash 固定／版本化。

視覺直接引用也已核查存在：Basic.dat SHA256 `0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`，索引中的 AlertFrame.ypf 位於 offset 13196、177648 bytes，成員 SHA256 `b641441d1f0378de04b6f7929c333d95e6ad7df451f3927432e5c4d0305602ce`。按鈕 object 11/12/13 的實際呈現與 frame 解碼仍屬原 Client CT；沒有因檔案存在就標畫面通過。

## 4. 關閉 Born 不是「沒有回包」

**修正先前結論**：只搜尋 Script XML 裡的 SendReply 不足以推定 wire 行為。PaperDialogProc 的 OK 呼叫 dialog.Dispose，再呼叫 client.Dispose。兩者的 native 分支不同：

1. dialog.Dispose：0x5278b2→0x51df80 從 runner 的 dialog 清單移除並釋放 UI。
2. client.Dispose：0x526873 比對 API 名稱；0x5268c6 建立 C6C subtype **4**，複製 runner 名稱及 context，0x5268f4 呼叫送出。
3. 隨後 0x5268fc→0x519450；runner 的 replied flag（+0x23c）初值由 0x521cfb 設 0。未 SendReply 時，0x5194ce 再建立 C6C subtype **2**，0x5194f1 呼叫送出，再排程 runner 清理。
4. SendReply 0x51a9f0 則建立 C6C subtype **1**、回傳 key/value 清單並把 replied flag 設 1；這時清理路徑不再送 subtype2，client.Dispose 的 subtype4 仍存在。

因此在上述 CP950/start context fixture 下，Born 正常 OK 路徑的**靜態送出呼叫順序**為：

```text
C6C body: 04 04 426f726e 11223344
C6C body: 02 04 426f726e 11223344
```

這兩筆是 Client script lifecycle 訊息，**沒有證據可直接視為教學任務完成、發獎或招募成功**。兩次呼叫在傳輸層如何 flush／合併仍須 runtime；不要把它們錯稱為已抓到兩個 frame。Server 應依 session、script name/context 檢查、接受合理清理序列並作冪等處理（designed），不得對每個 close 各增加一次 quest 進度。

## 5. 第一個 NPC 的資源線索與真正缺口

已追加檢查全部 316 個 Script 外層；315 個 XML、一個 NDW 文字，沒有找到其他 Script 以 Born 字面名稱呼叫此 Main。原 EXE 全檔 ASCII／UTF-16LE 搜尋也沒有 Born 字面 bytes。這支持「名稱由訊息提供」的已追通路徑，**不證明所有構造字串／其他資源／原服事件皆不存在**。

另找到 nNewJoin01.dat（SHA256 `8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae`）是初級學校加入對話的候選：MerchantTalk→JoinMessage01→02→03；最終 OK 回 STATE=ACCEPT、CANCEL 回 STATE=REFUSE，透過 client.SendReply；它不是具有自己 Main 的獨立 Born 替代腳本。**目前無 NPC entity ID→此腳本的原版綁定資料，不能將它確定標成 Born 所指女性招募員。** 名稱／對話相符只屬 inferred；生成／身分由 A-024、任務政策由 A-012/A-026 接續。

已繼續核查 generic Merchant.Main(args)：它把 args 設為 ServerParam、建立 ClientReply，讀 TILE/MNAME/UGOLD/UBAL/UAGOLD/UABAL/UCOLOR，並依 GREETING/TYPE 或 DoesTalk 等 hook 建立商人介面；nNewJoin01.DoesTalk=true、MerchantTalk 呼叫 JoinMessage01。這說明候選加入對話如何接入共用框架，仍沒有填補 entity→Script 的原服綁定。原件 SHA 與參數清單見 `corpus-entry-audit.json`，未將整段原腳本提交。

本地實際已有 Map0/1/2.dat、Script 及 Basic 資源，不再沿用「完全沒有地圖資源」作為不能分析的理由。但 Born 本身沒有 map ID、NPC entity ID、spawn 或任務旗標；可得的地圖／視覺資料存在，仍不等於提供了原服 NPC／事件綁定。

## 6. 已完成檢查與無法由現件回答的事項

已追完本次 Client 端「S44 start→資源／依賴→Main→紙張 UI→關閉回送」，補出原先漏掉的原生副作用；已完成 parser 原始位元組、reader/writer endian、語系 codepage 表、Script text CRC、缺檔佇列／更新及候選 NPC Script 檢查。原生教學首觸發的**傳輸機制**不再是 unknown。

仍不能宣告原服首次教學完整還原的具體缺件：

|未決事項|所需的原始證據|為何目前不能推出|
|---|---|---|
|原服首次登入的發送條件與順序|包含 first login 與 returning login 的原服封包／事件追蹤，或原服 onboarding handler／設定|Client 接收任意名稱的 start，不包含原服帳號旗標資料庫與發送決策|
|招募員真正 entity/map/spawn 與 Script 綁定|原服 NPC／spawn／互動映射，或進圖與點擊招募員的原服 trace|Born 只有導引文字；nNewJoin01 是候選，未含 entity mapping|
|任務初始化／完成條件與權威旗標|原服 quest/event 定義或對應收發與狀態證據|Client lifecycle 關閉訊息不能證明 Server 變更哪個 quest|
|Client／資源發行配對|可信版本清單或配對發布原件身份|同一工作目錄與 matching 個別 hash 不是發行版證明|

這些屬於實際證據邊界，不是以可交接為停止點，也不是等待新 Server／CT。A-023 的全部原生內容驗收仍不得改 ready；已完成 Client 契約供 DEV 開發已知子集，native Client CT-033～035 保持 not-run。

重現：`python task_a/roy2/verify_script_entry.py /local/Asgard.exe /local/Script`。驗證 18 段原始 bytes、資源 SHA、CP950 text CRC、完整 start fixture 與 37 個截斷／selector／尾隨資料拒絕案例。結果在 `script-entry-verification.json`。這是離線靜態／合成測試，不是執行 Client。

## 證據索引

- **A023-E14**：原件 parser 0x586410..0x5867bb、jump table 0x5867bc；reader/writer ctor 0x45ad70/0x45aac0，LanguageMan 0x498420/0x60855c。重現 signatures 見 verify_script_entry.py。REA `ev_cb9fae76509bd4ffa248f653d781ec6c1d9251e4ae1c96392b7e43c2aba71c52`、`ev_8c2fba91d228a8db3e1817c411c5d6650f93fc512aee8d7b9079bc9df6897dc3`、`ev_2a786c432e25020497cabb0dc50b3de0723f8d0c8cfd5bbd1dafaf40585bf371`。
- **A023-E15**：start／佇列 0x52c2a0，runner 0x52bd30/0x521c20、Main 0x524fa0；REA `ev_c401e6ffc5154151aa851abb1f0319e927d966cebe50c892c0384f0ef225d100`、`ev_5fb143265f24725afe319f26c95d56a0aa5de20cf02a6ed5b00841ed7f220c3b`、`ev_66d7a0d5a6b9c659c2141fece7535036c69277229dc1cde7b2473d8a399b1947`。在 0x52c014 的原指令補足 pseudocode 的 no-return 截斷。
- **A023-E16**：Dispose／SendReply 0x526873、0x5278b2、0x519450、0x51a9f0；REA `ev_4b996827af5f1223e5fcc48e0cad8fb5bad26232f0aaa2409431b088c6524eef`、`ev_9a787ea4c7979a2613ada40688897136c0294d3db4d3d6374ae72102ecec93be`、`ev_bc494ea10ecb485e3416ec5f631b1993f2c3612fc93da08f1c61da0ae2a0e676`。
- **A023-E17**：0x529060→0x550910→0x58a210 的資源校驗；REA `ev_b3e310605487e1abb7bdadcbde96afbddc5a8399e25f6ca124362e719459caf5`、`ev_61ca2a6dbd6fe098c0f4cb74d0b4f5600eb0e8e3cadf4a917eb4dd6ae0e27584`、`ev_4e1d766e643b16a39a29603019445c83787fe8e4783889ee65d8432daae27ba5`。
- **A023-E18**：全部 Script 資源檢查、nNewJoin01.dat 的函式／回覆分支及 Basic.dat 索引；各原件身份及限制見本頁第 3、5 節。原件不提交。
