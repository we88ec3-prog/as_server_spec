# 已有資源及地圖分析整合

本頁是既有研究的整理，沒有在本輪重新反編譯。以下為指定Client版本的靜態／結構驗證；資源存在不等於遊戲功能已完成。

## DAT封裝

已盤點945個.dat，其中628個符合相同索引，合計3407成員；其餘為316個壓縮Script及獨立Server.dat，不得套此格式。

|位置|格式／檢查|
|---|---|
|0|LE u32 slot_count n，包含結尾sentinel|
|4起|n個36-byte slot：LE u32 data_offset + 32-byte名稱buffer|
|第一筆data_offset|必須等於4+n*36|
|每成員大小|下一slot offset減本slot offset|
|最後slot|EOF offset；名稱區可能為殘留資料，不是有效名稱|

628個檔已檢查首offset、單調offset及EOF等於檔案長度。名稱在首NUL截止；韓文名稱解碼為CP949屬推斷，應保留raw name bytes。這是容器索引，不是物品屬性表。

## Script

**A023-E17 原生 reader 補正**：`00010000` + BE u16 n 是本批小檔案的外觀拆法；0x529060 實際依次讀 **BE u16 version=1、BE u32 UTF-16LE code-unit count**。校驗文字時將完整 UTF-16LE XML 依 LanguageMan codepage 轉 bytes，再做標準 CRC32，並非 raw DAT 的 CRC。Born/PaperDialog 在 CP950 的文字 CRC 分別為 `1d87b0c0`／`f870c574`。詳見 [A-023 完整契約](../task_a/roy2/A-023-script-entry-contract.md)。

316個Script/*.dat均可zlib解壓：解包 offset0..1 為 BE u16 version、offset2..5 為 BE u32 UTF-16 code-unit數 n，offset6 後為 UTF-16LE，總長必須 6+2*n；以先前的 BE u16 解讀僅偶然適用於長度小於 65536 的 Script。315個為可解析XML，NDW為純文字。CDATA含Client腳本與介面API，不能視為完整Server任務／獎勵／AI邏輯。

BarberShopDialog的Gender、HairShape、HairColor與CreateHairShape/SetHairObject提供外觀預覽入口；Born為新手對話／座標導引，不能當登入或創角處理器。

## MAP結構

原生loader 0x4b33a0，檔名%05d.map，資源庫選擇map_id/10000+9。Map0/1/2分別有288/184/22個map，共494個；已全量驗證布局，0個結構錯誤。

|offset或順序|格式|目前語意|
|---|---|---|
|0..5|3個LE u16|讀取寬度已知，欄位語意未知|
|6、7|u8 width、u8 height|寬高已由native確認|
|8起|ceil(width/2)*ceil(height/4)*2 bytes|區塊大小已知，位元語意未知|
|區塊後|width*height筆，每筆10bytes：3個u16+1個u32|圖層／碰撞語意未完成|
|tile後|u32 count + count*7bytes|結構已知，語意未知|
|之後|u32 count + count*8bytes|結構已知，語意未知|
|之後|u32 count + count*16 bytes|A-022 確認最後段 record 步長 16 bytes（0x4B35BC、0x4B3230），欄位語意仍需分析|

00000.map為20×20、tile offset108、共400格；00001.map為124×185、tile offset5836。不能用這些結構驗證宣稱已完成碰撞或出生點可通行判斷；A-005/A-015負責補完。

## Human / YPF / DOI

Human有男女衣服mb/wb各102檔，髮型mh/wh各36檔；管理目錄在可用資源範圍內篩選，並非所有原始編號都已實測。w/s系列用途尚不能只靠檔名認定。

原生YPF loader 0x56ea20。已解出第一組frame，12個衣服／髮型樣本通過RLE行寬、非零alpha pixel數與palette stream消耗檢查；首幀預覽不是完整行走／動作還原。格式已知：u16版本17、兩u16 header尺寸、u32欄、u32 flags；flags bit0有512byte RGB565 palette。palette後u32為圖片資料absolute offset；metadata含group/frame數與額外區域。frame含4個signed u16 bounds、u32 frame flags及條件區塊。

alpha區有height個u32 rowoffset及u16 RLE run（高byte count，低byte alpha）；非零alpha pixel依序取palette index。樣本alpha為0..248，預覽工具縮放到255，但原引擎rounding仍未完整追查。DOI動作／方向、其餘frame group與替代通道仍未知，不能據首幀自行補動畫映射。

Evidence：MAP ev_e166a44f01c9de3b7eff7457a30e6279b8571b5a76afc7354812c14bf1331e27；YPF ev_118f7890a0a4321dda8b83065142403499e707a3620831c41800a1b4164b4be1。原始資產及抽取工具不隨規格分享；本頁描述格式以利各實作者自行驗證其持有的相符資料。

## A-022：C35 校驗不是全檔 raw CRC

同 SHA Client `0x4B4850` 讀 MAP header +4 的 LE u16；`0x4B4890→0x4B3650→0x4B2EC0` 對解析後 block、10-byte tiles、7/8/16-byte records 做結構化 checksum，部分值正規化。`0x43E0A0` 查表 `0x664720`（table[1]=0x1021），單元 primitive 合成 `01 02 03→0x1222`。無原版教學 MAP/Script/Born bytes，真 tutorial map ID、出生與完整 C35 checksum 仍 unknown。參見 [A-022 證據](../03-analysis-requests/A-022-roy1-bin-analysis.md)。

## A-023 Born.dat 原件報告（roy2，獨立重現尚需來源檔）

**2026-10-31 續查已在本地原件獨立重跑**：Born 與 PaperDialog hash／解析通過，並追通 S44(1,0)→Main 與關閉 C6C4/2 原生副作用。下段「本地只有 EXE」是早期 review 狀態，不再適用；目前缺的是原服 first-login 政策與 NPC/quest 綁定證據，非缺 Born 原件。重現工具及目前限制見上引完整契約。

Roy2 提供 Born.dat 原件校驗報告：raw 589 bytes SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`；zlib 解包 1154 bytes、header `BE u16 version=1` + `BE u32 units=574` UTF-16LE units；唯一 `Main` 建立 PaperDialog，文字引導 (31,29) 女性招募員。未觀察到顯式 quest/SpawnNpc/SendReply；不能推論引擎沒有其他副作用，更不能把 (31,29) 當成出生點。此回合本地只有 Asgard.exe，原 Born.dat 尚不可獨立重跑；報告與 validator 已入版，日後以原件 SHA 重現，版本對應仍未驗證。

## A-015 本輪 BIN-first 更新（2026-10-31，roy2）

與已記錄的舊 corpus 相比，本輪直接以原始 EXE SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145` 重查：`0x403FA4..0x40401D` 為 Basic/Font/Icon/Locale/Video/Portrait/MSO/Script 註冊，`0x404022..0x404050` 為 Map0/1/2 → library9/10/11；`0x4040B2..0x404340` 為 Human 各系列；Map loader `0x4B33A0` 與 `0x4B35BC` 讀 10B tiles /7/8/16B 尾段；YPF `0x56EAFF` flags bit0 條件 512B palette。這些是讀檔格式和資源池，不代表遊戲功能/素材授權。

本輪有 Born.dat 原始 589B（SHA `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`）可實際重跑 Script 格式；未取得 Map0/1/2、Human/YPF、技能/物品定義全量資產，因此原新手 map_id、spawn、NPC、collision 與 item/skill schema **仍為 unknown**。新增 [A-015 來源分析](../task_a/roy2/A-015-analysis.md)、[結構化欄位目錄](content-resource-catalog.json)、[本機 metadata 探針](../tools/a015_content_probe.py) 與 [CT-039/040](../05-conformance/A-015-content-test-plan.md)。

## A-015 原始三庫 MAP 實證補充（2026-10-31）

這次獨立收到 Map0.dat（44,863,691 B；SHA256 dcaf8ab5...）、Map1.dat（30,817,997 B；SHA256 8681dc75...）、Map2.dat（3,856,650 B；SHA256 5320a095...）。直接解析 288／184／22=**494** 個 MAP，完整索引、block/tiles/7/8/16 尾段與 EOF 皆通過。**494 個檔名只對應 330 個不同的 SHA256 地圖實體內容**（33 個重複群、164 個別名）；00006.map 與 10000.map 是跨庫同內容案例。**477 張地圖**尺寸涵蓋 Born 的 (31,29) 引導點，因此無法單靠該文字決定教學地圖或出生位置。原版版號配對、C35 第二欄 structured checksum 和 NPC/碰撞/遊戲語意依然 unknown；[機讀結果](a015-map-corpus.json)。

## A-015／roy2：MAP 三種尾部 record 的欄位級 accessor 確證

原版 `Asgard.exe` `0x4B2D70` 逐欄讀取 **7-byte** `u8(bool), LE u16, LE i16, LE i16`；`0x4B2DE0` 讀取 **8-byte** 四個 LE u16；`0x4B2E40` 讀取 **16-byte** `LE u16,u16,u32,u32,u16,u16`。這是 BIN 直接確認的 layout，而非以史料推測。

494 張 MAP 實測：header 第一/第二 u16 皆相等，但第三 u16 在 **32 張**為例外 `(1,1,4)`；7B／8B／16B 尾段筆數為 **74,032／396／2,269**。後兩種 record 裡疑似 (x,y) 的 `(+2,+4)` 與 `(+12,+14)` **396/396、2269/2269** 全符合 `x < width*48, y < height*32`，僅能推斷為與圖形座標有關，**不能視為已確認原版 NPC 出生點、地圖阻擋、傳送或任務位置**。7B 首旗標的原始取值為 `0=72,577`／`1=1,455`。詳見 [A-015 欄位級報告](../task_a/roy2/A-015-field-audit.md)。

## A-015 研究格式與來源交付結案（範圍限定，2026-10-31）

Script 既有簡化 `BE u16 length` 的錯誤已更正為 **BE u16 version + BE u32 code units**；原 Born.dat 驗證通過，並加入大於 65535 code units 的合成回歸測試。原 EXE UTF-16LE 常值池的 resource selectors（Basic/Icon/Locale 等）可確認存在，但技能/物品定義的真正檔名 **unknown**，不能把候選檔案當成已解。完整資料盤點／來源／授權／下游邊界見 [A-015 結案審查](../task_a/roy2/A-015-closure-review.md)。

## 2026-10-31 Monster00/World00 與三份新 Script 的實體補證

已收到並離線解出 `Monster00.dat`、`World00.dat`：各自 `LE u32 slots=6`（含 sentinel），五筆 YPF payload，offset0=220、最後 offset=EOF。Monster 索引為五個 M_00_*（모스／모스워리어／나이트모스／드라스／모스캡틴）；World 索引為 TS_000_AnimStatic、AnimStaticShadows、Static、StaticShadows、Tile 的 .ypf。**這是索引存在與 member 名稱，不是 NPC spawn 種類、World 物件資料表或完整動畫解碼**；A-011 的「每 Monster archive 十個 client image slots」**不是**「十個 YPF member」。資產 SHA、長度詳 [實證](new-asset-samples-20261031.md)。

`nNewJoin01.dat`、`PaperDialog.dat`、`PaperDialog02.dat` 以既有 Script `BE u16 version + BE u32 UTF16 units` 及 CP950 CRC 驗證：nNewJoin01 `d9390353`，PaperDialog `f870c574`，PaperDialog02 `42683546`。初級學校三頁選擇是 `STATE=ACCEPT/REFUSE`；PaperDialog02 另外產生 `PAPER02=START/NOT`，其同名 callback 不可與 PaperDialog 直接合併。資源行為不證明原服的學校 NPC 綁定／切圖政策。完整 Server 交接見 [入學規劃](../02-server-planning/novice-school-admission-flow.md)。

## Roy1/Roy2 MAP 4-byte offset 誤判更正（2026-10-31）

Roy1 曾以 `8+36*n` 起始解出首 MAP，實際 indexed DAT 是 `LEu32 n` + `n×(LEu32 start + 32B name)`，首資料起點 **`4+36*n`**。三庫 494/494 MAP 都符合原始完整 payload/EOF，7,701,805 tiles；`00000/10000/20000.map` 不是被證實的三張無效特殊圖。bit0 runtime/bit4 line test/aux u32 grid 分離；格子可讀≠原版角色可走/出生。參見 [整合審查](merge-review-roy1-roy2-20261031.md)。
