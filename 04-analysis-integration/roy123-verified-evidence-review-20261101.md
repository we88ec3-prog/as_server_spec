# 2026-11-01 Roy1 / Roy2 / Roy3 增量分析核對、證據分級與整合報告

## 基準與合併形式
- 共同祖先 `as_server_spec/main@d68dc28eb02bd3c514d531caded16aa07603b0d8`；合併來源 `task_a/roy1`、`task_a/roy2`、`task_a/roy3`，保留各分支原 commits 作 merge parent；遇到共同 `requests.json`／`evidence-index.json`／`packets.json`／`vectors.json` 的變更按 ID 與欄位合併，不能用最後一個 branch 整檔覆蓋其他研究。
- 原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`、`Basic.dat` `0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`、`Locale.dat` `813f2800696555f16ec6c4bfc5975b649332340b5a6975d7aeba4c4e77380161`；原始 `Map0.dat` `dcaf8ab5...`、`Map1.dat` `8681dc75...`、`Map2.dat` `5320a095...`。已對本輪可存取的七份原件執行 SHA256 比對，均與分析報告一致。
- 外部 GitHub Actions `validate-phase-gates` 對合併三分支之主線成功；Python 靜態 probes/unittest 視各分支報告，仍需分清 **GitHub 無遊戲原件的合成 PASS** 與 **本機原件執行 PASS**。本輪獨立自原始 EXE 的 CRC table 和 Map0/1/2 重算五張地圖 C35，與 roy3 fixture 全一致；`Basic.dat` 實際取出 `BasicString.txt` 和 `SkinString.txt` 原文確認。
- **沒有執行未修改 Client 的 Windows GUI/TCP E2E，所有原版入遊戲／行走 CT 仍 not-run**。使用者描述「創角後直接進入遊戲、不回登入頁」是需求，非 static bytes 已證的 World wire。

## 證據合併表（決策可直接採用的部分）
| A 與來源 | 已驗證：可以交 DEV 的 Client 靜態／原件結論 | 仍不能當原版實際可用 |
|---|---|---|
| **A-030 roy1** [原件證明](../03-analysis-requests/A-030-roy1-original-resource-proof-20261101.md) | `Basic.dat/BasicString.txt` 73=NAME、75=E-MAIL；確認頁查 label 0x49、0x4B，Region2/3 widget15/16、Region4 widget23/24 對 C02 F3(NAME)/F4(EMAIL)；四段 string8 + u8 flag。C04 不傳 email。S02 非零 message→對話框建構→C15(empty)/state1F 原生路徑 | 原版 GUI 裡當次 selected region、是否必填 E-MAIL、S02 status 的原服 business mapping、C15 後 socket/retry 未實測；Region0/1 wire 與 2..4 不可混用 |
| **A-028 roy2** [深入追查](../task_a/roy2/A-028-postcreate-ui-native-followup.md) | final C04/S02(0)→`0x4b206b`，清 0x0B/0x0C/0x0D/0x07 UI slots；只有 **Region3** 會建 MSVC RTTI 確定的 `LoginDialogPane`；建構子無直接 C03 sender；獨立 callback 0x4A8890 具 C03 sender 呼叫 | UI 物件存在 ≠ 玩家可見「回登入畫面」；後續 callback 是否自動發背景 C03／何時 World 連線仍 unknown；ADR-008 明定**創角成功不能要求手動重登** |
| **A-031 roy2** [世界入口分析](../task_a/roy2/A-031-analysis.md) | C25 真類別 `CBillingInfoPacket`（ctor0x5712E0/writer0x571420），Region3 三個 codepage string8，原始來源是三個 opaque billing buffers，**不是 map_id、帳密或角色授權**。Region3 已證 S03→C10 raw token enqueue 緊接 C25（中間不等 S02）；non3 某已證 callback 只 C10 | 非3 Client 不得強制 C25；新角色完成 C04 的自動轉服 route ≠ 已證的一般登入 S03 callback；C25 後第一個 S2C 及實際畫面仍待觀察 |
| **A-032 roy3** [地圖/C35](../task_a/roy3/A-032-roy3-native-map-c35.md) | 以原件重算 `0x4b2ec0` structured checksum，C35=BEu16 header+4 / BEu16 checksum，非 raw CRC；`map_ref=6` 是 Map0 / `00006.map`（60×60）初始 pair `00040F90` | 仍無原版 Client 回 C35 的實際擷取；MAP 在 runtime 可能改變，無已驗證 spawn/view/facing／walkability；map_ref6 **不是**已證教學地圖 |
| **A-005 roy3** [移動補證](../task_a/roy3/A-005-roy3-native-movement.md) | C33 {direction:u8,seq7:u8, movement_mode:u8}；Client 本地送完 seq=(seq+1)&127。S0B {x:BEu16,y:BEu16,status/seq:u8} handler 0x558670：**必須回當次 C33 seq**，bit7=0 走權威校正／停止路徑，bit7=1 走預測座標比對，若不同也校正。C11 轉向 body u8 | 不能從 bit7 直接得出原服碰撞類型或速度，bit0/bit4/tile flags=0 皆不是唯一「可走」判定；native C33 S0B/GUI 回滾未測 |

### 獨立 C35 離線重算表（不是 native packet capture）
| map_ref | 真原件 DAT/member | width×height | 理論 C35 body | 客戶端已動態驗證？ |
|---:|---|---:|---|---|
|0|Map0.dat/00000.map|20×20|`000063A9`|否|
|6|Map0.dat/00006.map|60×60|`00040F90`|否|
|10000|Map1.dat/10000.map|60×60|`00040F90`|否|
|18001|Map1.dat/18001.map|150×150|`0012F892`|否|
|20001|Map2.dat/20001.map|60×60|`0016E9B9`|否|

map6 和 map10000 的原始 MAP member SHA 相同，但 Map identity 不同；Client C35 body 相同**不能**當跨地圖授權。map6 候選旗標 0 路徑 (30,30)→(30,31)→(30,32)→(31,32)→(32,32) 只能供 CT 測，不證合法 spawn/腳底座標。

## 最新 Server source 稽核（只讀，非新實作）
`as_server_roy/main@a9326985b1d2899677d95bdb5a8496502b7e4bb1` 內 `LoginWireSession.HandleAsync`：
- `case 0x02`: **Close("native-c02-fields-unknown-a030")**。此原因的 NAME/EMAIL **Region2..4 靜態門檻現在已部分解除**，但尚未連線改程式，且 S02 錯誤實機仍缺。
- `case 0x04`、`case 0x15`：仍 Close，不動現有 safe creation backend。
- `case 0x25`：依賴 Development-only World fixture 且 body 必須等於 **01** 才可入 World；**與 Roy2 原生 Region3 C25 3×string8 不相容**。
- `case 0x35`：已具 C35 two u16/epoch/DB checkpoint 但使用合成 fixture，**原件雙值可供後續嚴格 native MapCatalog 接入**。
- `case 0x33 / 0x11`：Live Host 並無 InWorld 移動/轉向 route；現有 `TwWorldPackets` codec / `WorldMovementWindow` 只是支援程式。
- Database v5 `accounts.creation_email` / PG `asgard_accounts.creation_email`、獨立 create proof、C04 原子提交、C03/S03/C10 及共享 scene domain 已有實作，不重做。

**整合結論：A 的已證子集現在足以開更多 native codec、MapCatalog 和 movement ACK 的 DEV 工作；但不能把原版 GUI 首次創角直接入 World、真出生、真步行、錯誤 UI 當已驗收。**

[接續完整 DEV 計畫](../02-server-planning/roy123-playable-world-implementation-20261101.md) · [待分析](../03-analysis-requests/roy123-remaining-playable-blockers-20261101.md)。
