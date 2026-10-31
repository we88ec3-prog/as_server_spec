# A-023／roy2 補證：原件 Born／Basic 視覺依賴與 S44 type2 GUI 分派（2026-11-01）

> 既有 A-023 已由 [完整 Script 入口契約](A-023-script-entry-contract.md) 證實 `S44(1,0) → Script Main → PaperDialog → C6C(4)/(2)`。本頁**不是重新發明啟動封包**，而是對最新主線補充兩組獨立原始證據。結果：`integrated / handoff_status=partial / native_client_validation=not-run`；Script **Client I/O 已可交 DEV**，原服首次派送／NPC 實際身分與 quest 規則仍未有原服資料，不可標完全還原。

## 1. 本次實際可用的原始資料與獨立驗證

本輪實際讀取本地原件，**沒有上傳任何遊戲 binary**：

|檔案/成員|原始 bytes / SHA256|已核對的格式/意義|
|---|---|---|
|`Asgard.exe`|3,235,840；`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`|PE32 ImageBase0x400000；本次新增 S44 dispatch 22 個 VA byte signatures|
|`Born.dat`|589；`992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`|zlib 解包 1154B；native `BE u16 version1 + BE u32 UTF16 code units=574`；Main 建 paper 導引；CP950 text CRC32=`1d87b0c0`|
|`Basic.dat`|5,282,488；`0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`|**39 index slots（含 EOF sentinel）、38 實際 member**；首 payload offset=1408 = `4+39*36`，完整 member offset/EOF 單調/範圍驗證|
|`Basic.dat/AlertFrame.ypf`|offset **13196**，length **177648**；`b641441d1f0378de04b6f7929c333d95e6ad7df451f3927432e5c4d0305602ce`|本輪從 Basic 實際切出並比對 SHA。YPF header version **17**，header width/height **348／85**；此處不代表所有 frame group／按鈕的實機 rendering 已通過|
|`PaperDialog.dat`|**此輪本地未提供**；先前同版候選 raw SHA `5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054`|前次 A-023 已解出 `PaperDialog_Create / ShowIndexedHelp / PaperDialogProc`，本次只能引用既有可稽核證據；工具 `--paper` 提供原件時會重新驗 SHA/函式。**不得聲稱本輪已重新讀取該檔**|

`Born.Main` 的實際執行式為 `client.CreateArray() → page.Insert(msg) → PaperDialog_Create("",page)`，提示前往 `(31,29)` 點女性「招募員」。**此座標是紙張文字中的目的地，不是出生點，也不是已證的 NPC entity/map/renderer。** Born XML 沒有明確的 `SpawnNpc`、`SendReply`、quest flag 或傳送動作。它的 `PaperDialog_Create` 需 Script 依賴 `PaperDialog.dat`，而後者的 frame 引用 `Basic.dat/AlertFrame.ypf`：本輪現在能**以原件直接核實最末一段美術成員存在／版本**，但仍未能將三者視為已在原生 UI 完整演出。

本次不必要求重傳 `Asgard.exe`、`Born.dat`、`Basic.dat`、`Locale.dat`、`Map0.dat`～`Map2.dat`。若要**重跑本輪完整 PaperDialog XML 關閉依賴**，可提供**確切檔名 `PaperDialog.dat`**；它不是基本入圖／行走的 P0 阻塞。若要證實招募員的候選入學 Script，可提供 `nNewJoin01.dat`、`Merchant.dat`（先前報告有 SHA/語義，但本輪未取得原件）；**僅靠這些檔仍不能證實原服 NPC ID→Script 綁定**。

## 2. 新的 BIN-first 原件分支：S44(type2) 和 Born type1 切開

本次用同一原始 EXE 的 `0x4E0B70..0x4E0C5B` 與 `0x52C2A0` 原件反組譯、22 個 SHA-locked VA anchor 驗證，補完外層 handler 對 **type2 GUI** 的特殊處理：

|VA / 分支|觀察結果|Client／Server 分工界線|
|---|---|---|
|`0x4E0B79..0x4E0B85`|從 global `0x66D13C` 取 Script manager，傳原封包到 `0x52C2A0`，保留返回值|所有 S44 Script type 先走 native Script handler；**不是**每個 S44 都執行 Born.Main|
|`0x52C2CA..0x52C2E6`|分別辨認 type1 與 subtype 0..4；既有 `0x52C014` call `0x524FA0` 執行 Script Main|Born 的正確啟動來源仍是 `S44(1,0)`、資源／CRC 檢查通過後才執行 Main|
|`0x4E0B87`|外層 handler 查 `[packet+0x24]==2`，且要求 Script manager 返回非零|額外 GUI 路徑僅與 **type2** 有關；與 type1 Born Main 不可混同|
|`0x4E0B99..0x4E0BBF`|type2 subtype0：查 `packet+0x25`，由 global UI manager `0x66D140` 檢查 **UI slot `0x23`**，必要時在 `0x535AF0` activation|此分支會觸碰既有 GUI 物件，不是「空成功回包」|
|`0x4E0BC4..0x4E0C31`|type2/0 隨後處理 pane component **4、3**，並依 `[pane+0x54]` 條件操作 component7|這是本地視窗狀態，不能由 slot ID 反推招募員、quest ID 或新手自動 UI|
|`0x4E0C3E..0x4E0C51`|type2 subtype2：對 global UI manager **slot `0x24`** 呼叫 `0x535590`，再 `0x4E3880`|type2/2 是另一 GUI 清理／控制分支，不是 Born type1/start|
|`0x586410`|S44 依已知 reader 解 body 的 type/subtype 和變長欄位|write/read body 仍應使用 [既有 A-023 契約](A-023-script-entry-contract.md)，本次不改其 endian 或 CRC|

**重要但有限的結論**：`S44(2,0)` 與 `S44(2,2)` 的**原生 UI side effects 已能定位**，然而真正對話 pane 的 UI 文案、窗口可見性與 NPC entity 綁定仍未實機驗證。它們不是 Born 的最小必備啟動封包；Server 不應把任意 S44 subtype 當「腳本已開始／已完成」ACK，也不應在未驗證事件下發 type2 包來讓新手 UI「看起來有東西」。

## 3. 現在最小教學 Client I/O 與不能當權威的事件

|觸發|Client → Server|Server → Client|原版 Client 已證結果／未知|
|---|---|---|---|
|Server 明示啟動 Born（是否首次由原服發送 **unknown**）|缺檔可能發 `C6C(0,name)`|`S44(1,0)`：指定 script name、opaque context、完整 XML text CRC、PaperDialog 依賴|本地資源／依賴通過後執行 `Born.Main`；不直接生成 NPC，不指定地圖|
|缺少或補檔|可能發 `C6C(0)`|`S44(1,1)` 壓縮 Script 更新|待啟動 Script 可依依賴恢復；**CRC 不符可能有原生 use-after-free 路徑，不能以故意錯 CRC 測實機**|
|Born 紙張按 OK|**C6C(4)**，隨後沒 SendReply 時的 **C6C(2)**|沒有由此確定的 quest ACK|僅 Script runner close/dispose；不是完成、受訓、發獎或切圖|
|另一原生 GUI／NPC 對話|依真正場景可能 C43/C39/C6C；**連結未證**|S44 type2/0 或 type2/2 有不同 UI slots|不可拿 type2 的 UI 動作冒稱 Born.Main 啟動，也不可從文字 `(31,29)` 捏造 NPC entity|
|入學 Script 的候選選擇|已記錄 `nNewJoin01` 候選 `STATE=ACCEPT/REFUSE` C6C(1)|後續教學任務／回覆需 Server 正式政策|候選 Script 是否綁定 Born 招募員未知；`STATE=REFUSE` 不改進度是 **已決 Server 設計**，非原服觀察|

### 可交給 Server 的明確政策

1. **基本 World 進圖、地圖顯示、移動**不以未驗證的 Born NPC/quest 主動啟動作為硬性前置；該部分屬 P0 Client→World，A-023 為 ONB-05/教學內容 P1。若規劃要原版教學紙張，必須以已鎖定資源／代碼頁／正確 S44 type1 start 和合法 Script context 發送。
2. 任何 C6C script payload 先校驗已認證 account/character、world generation、runner name/context、原生 payload schema；C6C(4)/C6C(2) 以冪等清理 runner，**不自動修改 QuestCompleted**。`nNewJoin01 STATE=REFUSE` 的「不副作用、可以重新點 NPC」是 R-034 Server 政策。
3. type2/0 與 type2/2 預期觸發 native GUI slot，**不可**當測試回覆／空的 Script lifecycle ACK。未確認 NPC binding、原版 UI 及完整依賴前 fail-closed。
4. **不需要逆向原服 DB 來完成 Client 收包解碼**；但如果要求完全復刻「第一次登入自動進指定教學任務、女性招募員在原本 NPC entity/map/spawn、正確 quest flags」，就**必須有原服首登入→NPC 點擊→Script start→回覆的去敏 trace 或原服 NPC/quest/spawn 設定**。現有 EXE/地圖/Basic/Born 不能提供 Server 遠端決策。

## 4. 驗證方法與工作狀態

```bash
# 不執行遊戲腳本；本地須提供原件，CI 無版權資源只跑 synthetic tests
python task_a/roy2/a023_born_basic_probe.py --born Born.dat --basic Basic.dat
# 取得 PaperDialog.dat 原件後可額外核對
python task_a/roy2/a023_born_basic_probe.py --born Born.dat --basic Basic.dat --paper PaperDialog.dat
python task_a/roy2/a023_native_script_dispatch_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a023_born_basic.py' -v
```

本次 **原件驗證**：Born/Basic/AlertFrame 版本與 SHA 皆 PASS；**22 個新 native VA anchor PASS**，type1/2 分支不同。**合成測試**：新增 21 個邊界測試 PASS，包含 DAT header/index/sentinel/duplicate/path、Script UTF16 BE header、zlib 截斷與 trailing、7萬字元的 32-bit code-unit count 等。CI 不持有原件，所以不在 CI 執行原始檔 SHA 驗證；本地通過不能冒稱 Native Client GUI。

**新增 evidence**：
- `A023-E19`：本次 Born.dat 原件、CP950 text CRC32 及唯一 Main/紙張/提示。
- `A023-E20`：本次 Basic.dat indexed DAT 39 slots/38 members，AlertFrame.ypf offset/size/SHA/version17。
- `A023-E21`：S44 outer handler 原生 type2/0 UI slot0x23、components3/4（VA 0x4E0B87..0x4E0C31）。
- `A023-E22`：S44 type2/2 UI slot0x24（VA 0x4E0C3E..0x4E0C51），與 S44 type1/start分離。
- `A023-E23`：22 original VA SHA-locked probe、21 synthetic DAT/Script tests，Native Client/not-run。
- `A023-E24`：缺少原服 first push／NPC script binding，並且本輪 PaperDialog 未重驗，明確維持 partial。

### A-023 結案界線

**可完整交接的 Client 靜態部分**：S44 type1 start、Script cache/CRC/依賴、Born Main/紙張、C6C(4)/(2) lifecycle、type2/0／2 的 GUI slot 分支與 Basic 可用素材 metadata。

**仍未能宣稱原服完整新手教學**：第一次登入是否必須自動發 Born／在哪個 map 時刻、真正女性招募員 NPC EntityId／首次點擊→具體 script 綁定、原服 quest 初始化／完成及退出／重登政策、原生 UI/網路端到端。這些不從資源檔名字／推論補猜，CT-034／CT-035 native **not-run**；A-023 保持 `integrated/partial`，**不是「全部內容已知」**。
