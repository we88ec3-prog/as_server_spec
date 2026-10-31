# A-015／roy2 — 資料檔格式、語意與分享權利界線（BIN-first）

> **2026-10-31 最新 MAP 座標／碰撞研究**：三個 MAP 原件已取得且獨立驗證 **494 地圖／7,701,805 tile**；原生 MAP tile 是 10B，Client 內部展開為 17B，index `x+y*width`。Client 有合法 tile 範圍檢查、48×32 畫面幾何，以及三種分離的碰撞相關資料（bit0、bit4 線段、獨立 u32 grid），但**原版玩家 passability/出生位置不可從 flags 自動推出**。詳見新增 [A-015 MAP 解析、碰撞與座標原件報告](A-015-map-coordinate-collision.md) 與 [CT-087/070](../../05-conformance/A-015-map-coordinate-test-plan.md)。以下歷史段落提到「未收到 MAP」的說明已被後續驗證取代。


- 日期：2026-10-31；來自最新 `main` c544af35ceb7；現行既有 branch `task_a/roy2`，提交目錄 `task_a/roy2`（早期誤用 branch 已關閉 PR）。
- 問題：R-016/SYS-CONTENT；清點 MAP、外觀 Human/YPF、Script、技能／物品資料的格式／欄位，給可重現的 **metadata-only** 抽查方式，釐清素材分享限制；下游 A-022/A-023/A-024、ONB-03、CT-018/CT-040。
- 原始檔：`Asgard.exe` PE32 i386, 3,235,840 bytes, SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；`Born.dat` 589 bytes, SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`。**未收到** Map0/1/2、Human 及原版技能／物品資源庫，原始完整客戶端配對版本仍不足。
- 報告依 `observed-static`、`observed-static-resource`、`prior-research`、`synthetic-test`、`unknown` 分層，不會將歷史 corpus 數量當作本輪實際重掃。

## 1. 新一輪從 EXE 直接重現的證據

|ID|證據|意義與限制|
|---|---|---|
|A015-E01|本機 `sha256sum/file/objdump -p`，PE ImageBase 0x00400000，SHA 如上|Client profile 身分相符；不證明其他獨立資源與 EXE 同一發行|
|A015-E02|`0x403FA4..0x40401D` 把 Basic(0)、Font(1)、Icon(2)、Locale(3)、Video(4)、Portrait(5)、MSO(7)、Script(8) 登記到 `0x440720`；`0x404022..0x404050` 迴圈將 `Map%d.dat` 0/1/2 對應 library index 9/10/11|是 Client **檔案池登記與名稱**，不是哪些物品/技能定義必然在 Basic、MSO 或 Script 的證明|
|A015-E03|`0x4040B2..0x404340` 迴圈依次組合 `Human\\mb0%02d.dat`、`mb%03d.dat`、`wb0`、`wb`、`mh0/mh1`、`wh0/wh1`、`s`、`w` 類名稱，透過 `0x440720` 登記|存在多個外觀資源名稱／library ID 範圍；**不能**把 ID 範圍等同玩家可選衣服／原版掉落清單|
|A015-E04|`0x4B33A0` 地圖 loader：`0x4B3466..0x4B3497` 取 header 3×u16、width/height；`0x4B3520..0x4B355C` 每 tile 取 3×u16 + u32、10 bytes；`0x4B3575` count×7、`0x4B35AD` count×8、`0x4B35BC` 開始 count×16|MAP 佈局與欄位**寬度**可靠；撞牆、區域、NPC spawn / 16B 段語意未由此證明|
|A015-E05|`0x56EA20` YPF loader：`0x56EACD..0x56EAEF` 讀 2×u16+2×u32；`0x56EAFF` 檢查 flags bit0；`0x56EB07` 附帶讀 512-byte palette；`0x56EB15` 後讀 4-byte 影像位置|可復核 YPF header / optional palette；完整 DOI/動作組/角色圖層掛接 unknown|
|A015-E06|`Born.dat` 當場 zlib 解壓：BE u16 version=1 + BE u32 count=574 + UTF-16LE Script XML `Main`，原始與解壓 SHA 如 catalog|證實 Script 格式可與資源版的真檔實測；**(31,29)** 文字導覽不代表出生點|
|A015-E07|既有 `resource-formats.md` 先前掃描 945 .dat、628 可索引、3407 成員、316 Script、Map0/1/2=288/184/22、YPF 首幀 RLE 樣本|prior-research，這些完整檔本輪不在場，不能說已重新驗證全量|
|A015-E08|合成 4×4 map、索引 DAT、Script，與真 Born.dat 經 Python stdlib scanner 成功；截斷 MAP/DAT、DAT 內含損毀 MAP 與無效 zlib 拒絕|只驗證 **offline parser**、不是碰撞、出生、原生 E2E、技能物品功能|

重現原始定位：

```sh
sha256sum Asgard.exe Born.dat
objdump -p Asgard.exe
objdump -d -M intel --start-address=0x403f80 --stop-address=0x4043c0 Asgard.exe
objdump -d -M intel --start-address=0x4b33a0 --stop-address=0x4b3600 Asgard.exe
objdump -d -M intel --start-address=0x56ea20 --stop-address=0x56eb30 Asgard.exe
strings -el -t x Asgard.exe
```

## 2. 欄位級格式表：已知位置≠已知遊戲規則

|資源|格式與欄位位置（byte）|本次可供實作的內容|未知／嚴禁猜測|
|---|---|---|---|
|大多數 indexed `.dat`|file +0: LE u32 n slots **含末筆 sentinel**；+4 起 n×36-byte slots，每項 +0 LE u32 offset +4 raw filename[32]；第一個 member offset = 4+36n；最後 sentinel 指向 EOF|離線抽成 index/count/hash 和檢核單調偏移、EOF；非 ASCII 名稱保留原 raw bytes、不誤判一定 CP949|這種格式不適用獨立壓縮 Script/Server.dat；內部 ID 意義 unknown|
|`Map0/1/2.dat` 成員 `%05d.map`|0..5: 3×LE u16；6,7: width/height u8；8 起 block = ceil(w/2)*ceil(h/4)*2；接 w*h×10 byte (3×u16 +u32)；3 尾段依序 u32 count + 7/8/16 bytes 每筆|可安全作 bounds/size/EOF 檢查；例如 w=20,h=20 => tiles start=108；124×185=>5836|三個 header u16 全部語意仍需個別證明；依 A-022 第三個可用於 C35 header 欄，但不代表 map_id；碰撞、出生、NPC、傳送、16B欄位未解|
|Human/YPF|native `0x56EA20` u16 版本(既有樣本=17)、後兩個 u16、u32、flags u32；flags bit0 提供 512-byte RGB565 palette，後有 absolute image offset；frame bounds/RLE/alpha 見既有 resource-formats|可建立「version / flags / palette present」識別及本機版資源 identity|原版全部帧動作/DOI、雌雄及道具 wearable mapping、染色圖層意義不完整|
|Script/*.dat|壓縮 zlib；解壓 +0..3 `00010000`；+2..5 BE u32 UTF-16 code units n；+6 起 UTF-16LE 長度 2n。部分 XML，NDW 可能非 XML|讀版本/長度/是否 XML，列 function name，不發布對話全文|Script 不是 Server quest/award/AI 原始資料的保證|
|技能/物品定義|EXE 有 SpellSkill、Inventory 等 UI 路徑與 S0F/S37 packet parser，但**沒有驗證原始定義檔的名稱/結構**|先將檔案來源、欄位、功能關聯設 `unknown`；等待使用者本機內容盤點|不可把 Icon.dat、Basic.dat 或 Packet 裡的 icon ID 當官方 skill/item row id；Server-only 公式/掉落等不必然存在 Client|

更完整 machine-readable schema：[`content-resource-catalog.json`](../../04-analysis-integration/content-resource-catalog.json)（相對請由 repo root 開啟）。

## 3. 與新手出生路線的交接

`A-022` 已知 C35 是 **MAP header(+4) + parsed MapData structured checksum**，不是 raw CRC。`A-023 Born.Main` 只寫 **(31,29) 招募員的文字目的地**，沒有提供 map_id、出生 x/y、facing、NPC entity ID 或原版進圖觸發。這些不能由外觀檔或含有 `.map` 的名稱推導。

A-015 本次沒有原始 `Map0.dat`～`Map2.dat`，所以 **沒有任何可宣稱完成的真正教學 map ID / C35 expected pair / spawn**。一旦有檔案，跑 `tools/a015_content_probe.py` 取得每個 `.map` 尺寸與 7/8/16 段 count，再用 A-022 BIN loader 對照條件/地圖引用；招募員的生成與互動仍屬 A-024/A-012。

## 4. 可重現 metadata-only 素材檢查（不輸出原始素材）

```sh
python tools/a015_content_probe.py /path/to/owned-client/resources --json a015_local_inventory.json
python tools/a015_content_probe.py /path/to/owned-client/Script/Born.dat
```

- **工具可重現性**：Python 3 標準庫；依據 offset/endianness 做 archive/map/script 結構校驗；輸出檔名、長度、SHA256、結構欄位及 XML function names 等 metadata，絕不寫原始 member/完整 XML/圖片或原始數值表。
- 已在本輪本機跑合成 DAT/MAP/Script + 真實 Born.dat，正向 PASS；截斷 DAT/MAP 與無效 zlib 負向拒絕。所有模擬地圖數字都**只是 synthetic fixture**，不是官方 MAP。
- 如果仍沒有客戶端素材，只驗證 EXE 檔名映射與 Born Script。檔案名稱是定位線索，不可將「不存在於本輪測試目錄」誤判為遊戲永遠沒有該資源。
- 檔案格式範圍與功能行為分離；完成目錄索引 **不代表** 原生Client可登入/可走地圖。

## 5. 權利邊界（技術分享政策，不代替法律意見）

1. 本共享 repository **不得**包含原始 `Asgard.exe`、`*.dat`、`*.map`、原圖、模型/動畫、完整 XML/腳本文字、可還原素材的長段位元組、Server 私有源碼、帳密與封包。工具不自動解析後回傳全部原文。
2. 可以分享非素材本體的重現步驟、介面欄位、部分經必要性控制的格式規格、原始檔 hash、Evidence ID、受限的名稱索引與人工合成 fixture；即使如此，公開發佈前仍須檢查是否包含第三方著作受保護的表達、個資或契約/所在地規範限制。
3. **能逆向讀到資料 ≠ 擁有散布權、修改權、公開營運權**。本 repo 規格授權仍未決定（`sharing-and-license.md`）；不要以本專案授權授予第三方遊戲素材的權利。若要公開發佈包含原作素材/相容客戶端，先由權利人或專業法律顧問確認權利與限制。
4. SHA256 是相同 bytes 的身分，**不是**合法權利或原服內容正確性的保證。個人本地持有並執行腳本，也不代表可推送至 GitHub。
5. 權利人/來源、原始版本/發行、取得方式、檔案 hash、是否允許公開、派生品範圍與用途記錄於**私有**的 `ContentProvenance`；共用 repo 僅記 minimal schema/未決策 flag。

## 6. Handoff / 原生完整相容的實際缺口

|誰|必要後續證據 / 操作|本 A 可立即交出的子集|
|---|---|---|
|A-022/ONB-03|同 SHA 發行版 `Map0/1/2.dat`，實際教學地圖原始定位、合法出生 x/y/facing、C35 expected pair；A-005 撞牆/通行語意|MAP parser stride/guard、資源 id/hashes 與檢查工具|
|A-024/A-011|原版 `World*.dat`、`Monster*.dat` 或來源中對應 NPC 定義、招募員的原生 entity ID/生成/互動封包|Client 資源池的 World/Monster 命名證據、資料來源待追清單|
|A-006/A-007|同版 Human/YPF 素材與全部 frame group、物品/裝備定義對照|YPF loader header/flag/palette 已證片段|
|A-010/A-012|技能/物品與 Script 的真正定義檔/欄位、Client UI/原服權威責任的區隔|不得把 local UI 顯示誤當 Server公式；安全的空白 schema|
|CT-039/040|只有 CT Owner 可宣布原版資源入圖/服端行為驗收；先做 offline/synthetic tests，再跑原生 Client E2E|可重現的對照步驟與驗收邊界|

**Gate 決議：`A-015.status=integrated`（已核對並整合的 EXE/Script/resource metadata 範圍），`handoff_status=partial`（原生教學資料與物品/技能語意未解），`implementation_ready=false`（整體遊戲內容），`content_format_probe_ready=true`（離線格式工具），`native_client_validation=not-run`。** 沒有因 Server 不存在而停工，但本次不把缺原始 Map/Human 資源的部分冒稱完成。

### 自包含測試

```sh
python -m unittest discover -s tools -p 'test_a015_content_probe.py'
```

此測試全部自造 4×4 地圖、索引及 Script，不需要遊戲資產；檢查 **DAT 封包內壞掉的 MAP 也必須整體判定為不合法**，不得報成功再悄悄忽略。另可另行用合法本機 Born.dat 做原件版對照；本項僅證明格式解析不證明 Server／原生 Client 行為。

## 補收原始 Map0.dat／Map1.dat／Map2.dat — 全量離線驗證（2026-10-31）

本節取代本檔先前的「未收到 MAP」描述；**原件已取得並實際解析**。只儲存大小、SHA/結構摘要，不推送任何原始 MAP bytes。

|原始檔|大小(bytes)|SHA256|MAP 數量|全部嚴格 EOF|尾段 count 合計（7／8／16-byte）|
|---|---:|---|---:|---|---|
|Map0.dat|44,863,691|`dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761`|288|288 PASS|39,481／0／4|
|Map1.dat|30,817,997|`8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b`|184|184 PASS|30,523／306／523|
|Map2.dat|3,856,650|`5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb`|22|22 PASS|4,028／90／1,742|

**A015-E09～E13：observed-static-resource**。494 名稱索引全數符合既有外層 DAT slot / `%05d.map` 及內層 MAP 版面：無重複檔名、無 offset/長度失配、無缺失三尾段、494/494 結尾精確落於 EOF。Map0/1/2 檔首 slot 含 EOF sentinel 分別為 289/185/23。實際 `Map2.dat` sentinel 的 name bytes 有非空殘留，證明 sentinel **不能**當正式資源名稱。

- 逐個 MAP payload 計算 SHA：**494 筆名稱索引、330 份不同 bytes**；有 164 個額外相同內容別名，分布在 33 組。跨庫相同例：`Map0.dat:00006.map` 與 `Map1.dat:10000.map` 內容 SHA 一致；這**不是**證明兩個地圖 ID 遊戲身分相同、互通或同一 NPC 配置。
- `Born.Main` 文字提示 `(31,29)`；**477/494** 張 MAP 的寬高都足以包含它（Map0 284、Map1 171、Map2 22）。這只證實尺寸範圍並不能靠這個座標鎖定教程 MAP、出生點或招募員。並非檢查過 477 張的該位置可通行。
- MAP offset `+4`（第三個 LE u16）在 A-022 已證是 C35 第一欄來源。這次可直接從任一已知檔取得該欄原始值，**第二欄 structured checksum 仍須依原 Client 演算法計算**，不得把 MAP SHA 或一般 raw CRC 當 C35 的正式 expected pair。
- 7／8／16-byte record 只能確認數量與寬度，**目前不能叫它們 NPC、事件、物件或怪物出生表**；用影像/名稱比對、引擎存取交叉引用與原版封包再補語意。

可在持有資源的本機重新執行：
```sh
python tools/a015_map_corpus_verify.py Map0.dat Map1.dat Map2.dat --json /private/a015-map-metadata.json
```
工具只輸出 metadata，不匯出任何 MAP 原始資料。合成 4×4 地圖及截斷/尾段錯誤負向測試 PASS；494/494 原件結構驗證 PASS。**A-015 仍 integrated / handoff partial，Native Client CT-040 not-run**；A-022/A-024 的真 tutorial map/spawn/NPC 與 A-005 碰撞語意仍需其他證據。機讀摘要 [`a015-map-corpus.json`](../../04-analysis-integration/a015-map-corpus.json)（請由 repo root 開啟）。

### 原始三庫驗證器／合成回歸檢查

`python tools/a015_map_corpus_verify.py Map0.dat Map1.dat Map2.dat` 會以索引、MAP dimensions、tile 與尾段作嚴格完整性檢查，並統計 identical-map alias、位置邊界。報告不包含任何原始地圖或完整內容。合成失敗案例由 `python -m unittest discover -s tools -p 'test_a015_map_corpus_verify.py'` 執行；**執行離線 parser 不是 Client 原生 CT**。

## 2026-10-31 維持 A-015 深入分析，不切換 A-016

原版地圖 tail accessor `0x4B2D70/0x4B2DE0/0x4B2E40` 的 7／8／16-byte 欄位型別已逆向核實。實際 494 張 MAP 的三尾段總數為 74,032／396／2,269；header 第三個 u16 在 32 張不是前兩個的值；8B 的候選位置 (+2,+4) 與 16B 的候選位置 (+12,+14) 均符合目前 48×32 的地圖像素範圍，但此為 **inferred**，**不是** NPC/spawn 或可通行點結論。新詳細資料在 [A-015-field-audit.md](A-015-field-audit.md)，附本機工具及單元測試。專案指定工作目錄與既有分支均為 `task_a/roy2`，未新建分支。**因 Human/技能物品原始定義來源未完成，A-015 仍 partial，A-016 未開工。**

## 2026-10-31 研究範圍限定結案補正

修正前面歷史文字中的「未收到 Map0/1/2」與「技能／物品與 Human 未研究完整」：三個 MAP 原件已全量通過 494/494；Human 全量圖片**不是 Server 資源格式交付的必要輸入**。技能/物品真正定義表與權威公式仍未知，交 A-007/A-010/A-011，不宣稱任何候選檔必含定義。Script 長度原先誤寫 `BE u16`，現更正為 `BE u32`（version `BE u16`）。A-015 的 **研究交接 ready 僅指來源盤點／格式／權利邊界**，完整遊戲內容 `implementation_ready=false`、原生 Client CT 尚未執行。正式完成條件／來源與待辦參照 [A-015-closure-review.md](A-015-closure-review.md)；舊段落保存為歷史分析記錄，不應引用其已被更新的缺檔／Script header 敘述。


## 本次 A-015 MAP/碰撞追加研究已整合（2026-10-31）

原版 `Asgard.exe` SHA 鎖定 26 native VA patterns PASS；`Map0.dat/Map1.dat/Map2.dat` 三庫 494/494、7,701,805 格原件解析 PASS。原生 `0x4B2C80` 將 `x+y*width` 展開成每格 17B 記憶體 tile，原件磁碟每格為 10B；`0x4B4920` 邊界檢查及 `0x4B4A3B/0x4B4A73` 的 32/48 像素 extent 已定位。tile bit0、線段 bit4 與 +0x258 u32 auxiliary grid **不是同一個已證玩家碰撞旗標**。(31,29) 在 477 張地圖尺寸內，該格 raw flags 0:242、1:109、17:126，不能視為可出生或可走座標。

離線解析器 `a015_map_coordinate.py`、原生 PE 探針 `a015_map_native_probe.py`、測試 `test_a015_map_coordinate.py` 已提交並通過 [GitHub Actions run 41188097214](https://github.com/we88ec3-prog/as_server_spec/actions/runs/41188097214)：**18/18** 新增 MAP 合成測試 PASS，既有 phase gates 同樣成功。`CT-087` offline evidence 已收；`CT-088` Native Client 撞牆/原生可通行點驗收 `not-run`。

A-015 資源格式／索引與 tile bounds 研究 `integrated/ready`，**但完整玩家可用座標列表尚未得證，`implementation_ready=false`**（針對原版行走權威）。這不是因缺 Server NPC AI，而是原生 Client 對玩家步行／旗標的實際使用路徑與動態 trace 未證。**本回合不缺已指定的 MAP/EXE/Born 資源**；未來需要 native 成功/撞牆/回滾封包/錄影，或再追 player movement call graph。
