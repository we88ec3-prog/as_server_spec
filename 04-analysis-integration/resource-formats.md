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


## A-011 原件增補：Monster / World 圖庫 ID 與動畫選擇器（2026-10-31）

原始 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145` 的 `0x404331..0x4043AF` 以 0x440720 登錄兩組 library：

- `World%02d.dat`，library ID **7000..7023（24個）**、檔名 `World00.dat`～`World23.dat`；
- `Monster%02d.dat`，library ID **8000..8042（43個）**、檔名 `Monster00.dat`～`Monster42.dat`。**重要勘誤**：EXE 的寬字常值從 0x5F1D3A 開頭是 `@Monster%02d.dat`，但原生註冊器 `0x40438B` 使用 `0x5F1D3C`，跳過字面 @，實際檔名應無 @；先前 A-024 報告中的 `@Monster%02d.dat` 是字串搜索結果，並非註冊器實際輸入。

`MonsterImageLib` native `0x4D7530/0x4D7560` 進一步將 image ID（`0x4000` 起）分為 `library=8000+floor((id-0x4000)/10)`、`slot=(id-0x4000)%10`。40xx/41xx image ID、800x library ID 與 Server object key 是不同命名空間，不能混用。只在已登錄 43 個 Monster 庫內，安全候選 image ID 範圍為 `0x4000..0x41AD`（**designed bound**）；實際每一個檔內 slot 是否存在仍需檔案原件確認。

另有 S07 receive handler native `0x4F1A8B/0x4F1B68/0x4F1BD1` 在 kind 1/2/4 時呼叫 `MonsterObject ctor 0x4D6FA0`；local motion selector `0x4D6BC0` 選出 `+0x20/+0x30/+0x40` 三組偏移（重複兩遍）。這些是**已證的程式碼映射**，不是已證的某種怪物／NPC species、動作名字或 YPF／DOI 方向圖群。

具體資料、C43 兩條原生 UI request 路徑、缺件及驗證見 [A-011 報告](../task_a/roy2/A-011-analysis.md)、[CT-067/068](../05-conformance/A-011-npc-resource-click-animation-test-plan.md)。目前尚無同版 `MonsterNN.dat`/`WorldNN.dat` 實體檔，不應假設原服掉落/AI/動畫組已還原。


## A-015／roy2 MAP 座標、碰撞來源與真正可用座標（2026-10-31）

以原始 `Asgard.exe` 與原件 `Map0.dat`～`Map2.dat` 獨立復核，**494 MAP、7,701,805 tiles**，詳見 [A-015 MAP／碰撞詳細分析](../task_a/roy2/A-015-map-coordinate-collision.md) 及 [CT-069／070](../05-conformance/A-015-map-coordinate-test-plan.md)。

- **raw tile**：MAP header 3×LE u16、width/height u8、block `ceil(w/2)*ceil(h/4)*2` bytes；每 tile `LE u16,u16,u16,u32` 佔 **10 bytes**。原生 loader `0x4B33A0` 轉成 Client 每格 **17 bytes**，`0x4B2C80` 依 `x+y*width` 尋址；超出範圍無效，`0x4B4920` 有 bounds guard。
- **畫面像素 extent**：Native `0x4B4A3B` `height*32`、`0x4B4A73` `width*48`；`pixel//(48,32)` 可作 candidate tile 對應，不等於已證玩家腳底/pivot/可行走 grid。
- **collision 分流**：tile `flags_u32` 的 **bit0** 在 `0x4B2CA0` 可被本地 set/clear、`0x4D120B` 另一 consumer 測試；**bit4** 在 `0x4B4BB0` 的線段/格列測試；`0x4B3250/0x4B2D00` 又有獨立 4 bytes/cell 網格與鄰格判斷。**沒有原生證據表明 bit0 或 bit4 是玩家唯一 walkability mask**。
- **原件 flags**：全庫只有 `0=2,701,300`、`1=496,877`、`16=12`、`17=4,503,144`、`512=472`。注意 0x200 不是 0。Born(31,29) 對應 477 張 MAP 的 in-bounds tile，分別 flags 0(242)、1(109)、17(126)，**不是原版 spawn/可用位置驗證**。
- **pixel candidate tails**：8B 尾段 `(+2,+4)` 是候選像素座標（396/396 在 bounds），16B 尾段 `(+12,+14)`（2269/2269 在 bounds）。尚未證明它們是 NPC、出生、傳送或碰撞資料。
- **驗證**：原件 EXE SHA 鎖定 26 條 VA 指令位置、三庫 494 原始 MAP 結構、合成 MAP 座標/截斷/越界測試；Native Client 撞牆與回滾 `CT-070` **not-run**。Server 只可依此讀 raw grid、檢查 bounds，不能自動從 raw flags 產出官方全地圖 passable whitelist。

**缺少新資源檔：無**。Client EXE、MAP 三庫及 Born 都已提供；要真正判定可站立與角色碰撞，缺的是指定地圖、原生 Client 行走/撞牆的去識別 packet/UI trace 或更深的 movement candidate→collision handler XREF，而非更多美術圖。
