# A-015／roy2 — 資源格式、可重現來源盤點與散布邊界：研究結案審查

**日期：2026-10-31。分支／目錄：`task_a/roy2`。R-016 / SYS-CONTENT。**

## 決議及嚴格界線

**A-015 研究交付 `integrated / handoff_status=ready`，範圍僅為「可驗證的 Client 原始資源載入格式、檔案名稱／來源盤點、解析／身分核對工具、版權與版本邊界」**。根據 `00-governance/phase-gates.md`，A 研究結案不等於 DEV 已具備全部遊戲內容、不是 CT 實機通過，也不代表未知的原服 Server-side 技能/物品權威公式已解。

`implementation_ready=false`（完整遊戲內容仍不足），`original_tutorial_content_ready=false`，`native_client_validation=not-run`，`asset_release_match=unverified` **不變**。若把本 A 誤解成「還原全部遊戲規則／所有資源逐張繪圖」，該擴張範圍並未完成，必須另由下游 A 負責，不能冒稱成功。

## 原始來源、驗證、字段來源矩陣

|族群|檔名／來源及定位|已證格式／抽取步驟|未知及後續 owner|
|---|---|---|---|
|Client registry|原始 `Asgard.exe` SHA `db3df616...`；`0x403FA4..0x4043B0`；EXE UTF-16LE 常值池|登記 `Basic.dat`、`Font.dat`、`Icon.dat`、`Locale.dat`、`Video.dat`、`Portrait.dat`、`MSO.dat`、`Script.dat`、`Map%01d.dat`、`World%02d.dat`、`@Monster%02d.dat`、`Effect%01d.dat`、`Sound%01d.dat` 等字串|名稱可觀察不代表檔案內容、同版或授權；技能/物品原始定義的確切檔名 **unknown**|
|DAT index|真實 `Map0.dat`、`Map1.dat`、`Map2.dat`|LE u32 slot count 含 EOF sentinel，36B offset + raw name[32]；第一 offset=`4+36*n`、最後等於 EOF；未通過必拒絕|其他 DAT 是否為同型容器要逐檔確認|
|MAP|三庫 `%05d.map`；Native loader `0x4B33A0`|494/494 MAP 經離線驗證；3×LE u16 header、2×u8 w/h、block、w*h×10B tile、7/8/16B 三尾段；330 unique payload，164 alias|碰撞、spawn、NPC、傳送、封包 C35 第二欄 checksum → **A-005、A-022、A-024／CT-040**|
|MAP 深入|EXE accessors `0x4B2D70`、`0x4B2DE0`、`0x4B2E40`|7B = u8(bool)/u16/i16/i16；8B=4×u16；16B=u16/u16/u32/u32/u16/u16，數量 74032/396/2269|48×32 畫素座標僅 inferred，不是證實 NPC/spawn|
|Human/YPF|EXE `0x4040B2..0x404340` 中的 `Human\\mb0%02d.dat` 等男女衣服／髮型／w/s 路徑；YPF `0x56EA20`|loader 的 version/flags/palette/offset 與既有首幀樣本有證據；由 Server 保存同步外觀識別，不需整庫圖片|合法外觀 ID 及完整幀/DOI/動作映射 → **A-006、A-007**；本 A **不要求上傳整包 Human**|
|Script|真實 `Born.dat` 589B SHA `992e6d...`，入口 `0x529060`|zlib 解壓 1154B：`BE u16 version=1`、`BE u32 units=574`、UTF-16LE 1148B；可讀 XML/Main；修正先前錯誤 `BE u16 length` 假設|玩家出生位置、腳本首次觸發、quest/獎勵 → **A-012、A-023、A-026**|
|技能／物品|原始 EXE 的 UI/Packet 類別 `SkillSpellDialog`、`ItemInventory` 等，不是本機資源 schema；此次 UTF-16LE 常值池有 26 種資源路徑候選|已盤點可觀察路徑；**沒有明示 `Skill*.dat`／`Item*.dat` 的靜態資源選擇字串**，只在「可列印 UTF-16LE 字串」的搜索範圍內成立|技能、物品的 definition 檔名與欄位 **unknown**。`Basic.dat`、`Icon.dat`、`Locale.dat` 只是候選，**不能確認**為定義表；真正規則／Server-only 數值 → **A-007、A-010、A-011、A-025**|

EXE 上實際列有 `MServer.dat`、`R%s\\Script\\%s.dat`、`%s\\Script\\*.dat` 路徑字串，不可把所有 .dat 當索引封包，也不可把它們當成完整技能／物品規則表。對沒有資源原件的家族只輸出 selector 與 unknown，不捏造原始欄位。

## 新的可靠版資源核對／負向測試

`python tools/a015_content_probe.py /path/to/owned/resources` 支援本機 metadata-only 檢核；`python -m unittest discover -s tools -p 'test_a015_content_probe.py'` 含合成 DAT/MAP 和 **超過 65535 UTF-16 units 的 Script**，以防原先 `BE u16` 長度誤讀。

原始 EXE/Born/Map0～2 已在此分析環境獨立核對 SHA，且 Map 共 494/494 合法。新 `BE16+BE32` Script parser 的測試及原始 Born 亦通過；如果未取得其他原件，不宣稱其結構驗證成功。CLI 只輸出 metadata（私有日誌中避免原文字）；Git 不含遊戲 raw payload。

### 正常/失敗／版本策略（Server 合約邊界）

1. **正常**：僅已辨識的索引/Script/MAP 允許擷取 metadata；記錄原檔 SHA、來源權限、格式 header、檔名與索引範圍，版本旗標與未知值留原樣。
2. **壞資料**：錯誤 offset/EOF、被截斷尾段、錯 Script zlib/BE32 長度、unknown version 均 **fail closed**，不以空值或另一版本資源補齊原版語意；單元測試只證 parser 行為。
3. **資源錯版**：SHA mismatch → 標明 version mismatch / not verified，不要從相似名字認定同一個官方版本。EXE、Born、Map 三份雖有各自 SHA，**沒有原廠 release manifest 可以證明同一發行版**。
4. **重送/斷線/重登入**：這是 Client/Server world/session、inventory 或 quest 層議題，不是檔案格式本身的協定反應；正確的狀態/冪等性追 **A-016**，不要用讀檔成功當成遊戲處理成功。
5. **版權**：格式解析及個人本機來源分析不授予散布、重製或公開營運權；共用 repo 只放 hash、欄位、統計、可重現程式／測試，素材留在合法私有來源。最終合法使用／分享需另外取得權利依據。

## 可供獨立實作者使用的本 A 結案範圍

- 已有穩定可用的 **檔案身分／版本隔離、DAT/MAP/Script 格式讀取、失敗拒絕與不公開原件**契約；A-015 可在這個明確界定的研究範圍內完成交接。
- **不能用這份 A-015 實作出完整世界／任務／技能／物品**：原始 tutorial ID/spawn、碰撞/物件、Client 同版歸屬、技能物品 definition 與原服權威仍未知，皆保留對應分析責任，不能因 A-015 ready 清掉這些 blockers。
- 這次**不改** `CT-039.status=planned`、`CT-040.status=planned`；只記錄 offline subset PASS，原生 Client E2E not-run。
- **不需大量 Human 圖像**；若日後需要原始定義定位，可先請提供特定 `Basic.dat`、`Icon.dat`、`Locale.dat` **作排查候選**，並不聲稱其內一定有技能/物品資料。
