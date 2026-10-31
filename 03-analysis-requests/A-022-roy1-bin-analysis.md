# A-022 — roy1 / 首次入圖與 MAP CRC 的 BIN-first 靜態分析

- 日期：2026-10-31；分支：`task_a/roy1`
- 樣本：原版 `Asgard.exe`，PE32 x86，ImageBase `0x400000`
- SHA256：`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`
- 證據：`ev_a022_20261031_asgard_map_static`；**observed-static**，不宣稱原 Client 實機通過。
- 需求：R-004、R-027、R-028；相關 A-015/A-016/A-021/A-023，SCN-009/010，CT-016/017/018。

## 1. 研究結論

本次已完成可從所提供 EXE 重現的**地圖入圖／校驗靜態研究**，交付通用 Loader、C35 checksum、載圖回覆及失敗／重連的 Server 介面規格。A-022 對這部分可標記 `integrated`、`handoff_status=partial`、`implementation_ready=true`，而不是因 Client 尚未實測而 `blocked`。

**重要範圍限制**：使用者提供的只有 `Asgard.exe`，未附原始 `Map0/Map1/Map2`、`*.map`、`Script/*.dat`、`Script/Born`。EXE 自身並不提供可證實的**原生新手教學 map ID、首次出生 (x,y)、面向、進度旗標**；這些欄位維持 `unknown`、`tutorial_content_ready=false`，需從 A-015/023 的原始資源證據補齊。絕不能用 `00000.map`、`00001.map` 或本地測試地圖冒充官方教學圖。

## 2. 精確原始入口（VA，非檔案偏移）

| VA | 由 BIN 確認的行為 | Server 影響 |
|---|---|---|
| `0x4A8370` | **A-002 交叉復核更正：這是 S03 交接 handler**；依 region 3/4 取 S03 的 address/port/token、建立連線並送 C10 | **不是 C25 的入口證據**；C25 實際 serializer/地區欄位仍 partial |
| `0x57FD20` / `0x57FDD0` | S14 建構 opcode `0x14`，parser 讀 1×u8 到內部 +0x18 | body=`u8 control` |
| `0x4F2300` | S14 handler 依控制 1/2/3 分支 | 1 發 C35；2 loading 回呼；3 異常處理 |
| `0x4F23CB..0x4F2428` | 控制 1 建 C35，分別呼叫 `0x4B4850`、`0x4B4890` 取得兩欄 | 不可把第一欄誤認 map ID |
| `0x4F23B5` | 控制 2 檢查 `0x91FBE0` 有效才呼叫 callback | loading 完成需狀態檢查 |
| `0x4F2333..0x4F23AE` | 控制 3 含 Sleep(0xBB8=3000ms)，之後走特殊清理/狀態路徑 | control=3 不應當作正常完成；斷線副作用為 inferred |
| `0x57FE80` | SMapSizePacket 以 opcode `0x15` 建構 | S15 是地圖描述，不是 tile 原始資料 |
| `0x57FF30..0x57FF9D` | S15 順序讀 **3×u16、2×u8、string8**；首個 u16 存 +0x18，後兩個 u16 只消耗；第二個 u8 存 +0x2C | 正式解碼須保留欄位，不可因 packet 未存就省略 |
| `0x57FF70..0x57FF98` | S15 第一個 u8 flags 展開成 `(~flags)&1`, `(flags>>1)&1`, `(flags>>5)&1`, `(flags>>6)&1` | 不能由位元名稱臆造 gameplay 語意 |
| `0x5733E0` / `0x573490` | C35 opcode 0x35；序列化為 **2×BE u16** | 有確定 byte 長度與順序 |
| `0x589990..0x5899BD` | S04 parser 持續讀取 4×BE u16 到 +0x18/+0x1A/+0x1C/+0x1E | 本地 profile 為 x/y/viewport_x/viewport_y，**沒有硬編出生值** |
| `0x4B33A0..0x4B34A0` | MapData loader 使用 `%05d.map`；資源庫依 `map_id/10000+9`；讀檔頭 3×LE u16、寬/高 u8 | Server 應以內容版本綁定 map_id |
| `0x4B3575..0x4B35E0` | MAP tile 後三段記錄依序為 `count×7`、`count×8`、`count×16` bytes | 更正原 resource-formats 最後段步長 unknown |
| `0x4B4850` | 從 `MapData +0xB4` 指標的 **file offset+4** 讀 u16 | **C35 第一欄 = 第三個 MAP header u16，不是 map_id** |
| `0x4B4890 → 0x4B3650` | 以 map 身份當 cache key，命中則取 +0x278，否則呼叫 `0x4B2EC0` 重算並存回 | C35 第二欄 = 結構化 map checksum |
| `0x4B2EC0..0x4B3246` | 校驗遍歷 block、tile、7/8/16-byte records；部分欄位有 bool/byte normalization | **不是直接對整個 .map 原始 byte 做 CRC** |
| `0x43E0A0` / table `0x664720` | 查表 256×u16，`table[0]=0`、`table[1]=0x1021`、`table[2]=0x2042` | 可寫單元測試的 primitive |

### S15（Server→Client）body

```
u16_be map_ref
u16_be field_b       # 既有 profile 稱 width，未從此次 parser 證實
u16_be field_c       # 既有 profile 稱 height，未從此次 parser 證實
u8 flags
u8 field_d
string8 title        # CP950 bytes；u8 長度不含 NUL
```

network 的 u16 是 **BE**；MapData 原始檔的 header u16 是 **LE**，兩種來源不可混用。S15 parser 保留的 flags 分別是 inverted bit0、bit1、bit5、bit6；其語意仍 unknown。

### S14（Server→Client）body

`u8 control`：1 觸發 client C35（須本地 map data 存在）；2 進 loading callback；3 為 3 秒延時的異常分支。未知 control 不得假裝已知成功。**S14 2/3 的原服應用政策不是目前靜態觀察能證明的 Server 實作**。

### C35（Client→Server）body

`u16_be map_header_word_at_file_offset_4, u16_be computed_structural_checksum`。第一欄 **不是 S15.map_ref**；第二欄由 `0x4B2EC0` 對解析後 MapData 依序更新 CRC，不是 raw-file 標準 CCITT。Server 必須對同版本 map/resource 使用確定的 expected pair，不得接受任意 C35 或把值硬填 0 當作已驗證。

## 3. 校驗運算的最小可重現 primitive

```python
# 只還原 0x43E0A0 的單 byte 更新，不是完整 MapData checksum。
# T = 0x664720 中 256 個小端 u16，T[0]=0, T[1]=0x1021
def crc_step(crc, value, T):
    return (T[(crc >> 8) & 0xff] ^ ((crc << 8) & 0xffff) ^ (value & 0xff)) & 0xffff
```

`crc=0` 更新 `01 02 03` 得 `0x1222`；更新 ASCII `ABC` 得 `0x1AA6`。兩例是**從原版 BIN 查表推導、以合成資料驗證的 primitive fixture**；**不是**任何真實 MAP 的 C35 期待值。`0x4B2EC0` 的資料流先用兩 byte block 再走 10-byte tile，最後依序處理 7/8/16-byte records，部分欄被 canonicalize。因此不能使用 `binascii.crc_hqx(raw_map_bytes)` 冒充原 Client checksum。

## 4. Server 可先開發的 World Loading 狀態機（designed）

```
CharacterCommitted
 -> S03 IssueTransferGrant
 -> C10 ConsumeTransferGrant(one-time)
 -> C25 WorldEntryMetadata
 -> Loading(epoch, map_ref, content_version, spawn)
 -> S02 establish UI -> S05 self -> S15 map
 -> S14(1) -> await C35 for this epoch
    | wrong length / old epoch / mismatch / timeout / disconnect => Reconcile
    | exact match => S04 position -> S33 self/visibility
      -> S0F/S37 required inventory -> S14(2) -> InWorld
```

**此狀態機是對現有已知 SCN-001 加入保護的 Server 設計，不代表原服唯一流程已實測。**

- 進圖由 Server 先決定角色所屬 map/resource/spawn，不是由 C35 自報的第一個 u16 推定 map identity。
- transfer token 與 `epoch` 綁 Account/Character/MapContent，一次性；C25 只能在成功交接後，C35 只能在同 epoch S14(1) 後接受。舊圖延遲 C35 不能讓新圖完成載入。
- `tutorial_entry_committed` 與 `tutorial_completed` 是分離事件；loading 中、只收到 C35、或把 map 送給 Client，**都不能誤標整個教學已完成**。
- 斷線或 crash：撤銷 pending epoch 與可見物件，用已保存角色/位置/進度重建；初始資產 ledger 避免重領。map CRC 失敗只能進安全拒絕／重傳／重連 policy，不能放行未知值。
- `local-fixture` 可用來先驗證通用入圖；但上線前需有同版真實 MAP/Script/Born map/ref/出生/內容版本的確證映射，**不可把測試地圖當原版教學地圖**。

## 5. 原版教學圖與首次定位：本樣本不能證明的值

| 應交付欄位 | 現況 | 必需證據 |
|---|---|---|
| 真正新手教學 map ID | unknown | A-015 原始 Map0/1/2 資源 + Born/相關 Script 引用 |
| 真正出生 X/Y、面向 | unknown | Script/Born 傳送／座標指令、MAP 邊界和 S04 來源 |
| 首次入圖判定與教學進度旗標 | unknown | A-016 持久化規則 + A-023 Script/任務分支 |
| 真實教程圖 header u16+map checksum | unknown | 正確 map bytes 對照 0x4B2EC0 完整重算 |
| 原服 CRC/逾時錯誤回覆 | partial | S14 異常路徑已知；完整原 Server 政策 unknown |

這是**原始資源缺失**，不是「沒實機所以不分析」。A-022 的可證靜態協定已可給 DEV；教學地圖原始內容須另由 A-015 提供，沒有證據時明示 `tutorial_content_ready=false`。

## 6. 下游測試與 BUG 回饋（不作 A-022 結案前提）

- CT-016：S15/S14/C35/S04 合成封包、錯序、截斷、C35 mismatch、跨 epoch、第二次入圖不重建角色。
- CT-017：C35 前後 crash、token 失效、重送/重連，保留角色/進度與避免幽靈物件。
- CT-018：**待原生 MAP/Script/Born 取得後**，Client 真正教學出生、正確地圖、能操作；仍 `not-run`。
- 出 BUG 時收集去識別 packet、角色/epoch、map resource version、Client SHA、expected/actual，修改規格或 DEV，再驗收。

## 7. 重現命令

```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x57fd20 --stop-address=0x580020 Asgard.exe
objdump -D -M intel --start-address=0x4f2300 --stop-address=0x4f2450 Asgard.exe
objdump -D -M intel --start-address=0x5733e0 --stop-address=0x5734b0 Asgard.exe
objdump -D -M intel --start-address=0x4b33a0 --stop-address=0x4b367e Asgard.exe
objdump -D -M intel --start-address=0x4b2ec0 --stop-address=0x4b3246 Asgard.exe
objdump -D -M intel --start-address=0x43e0a0 --stop-address=0x43e0bf Asgard.exe
objdump -D -M intel --start-address=0x589990 --stop-address=0x5899c0 Asgard.exe
```

只提交研究文字及精簡的原生位址，不提交原始 EXE、MAP/DAT 資產或遊戲帳號資料。

## A-002 交叉驗證勘誤（2026-10-31）

先前把 `0x4A8370` 的 S03 區域路由誤稱成 C25 metadata。已由 [A-002](A-002-roy1-login-transfer.md) 確認：S03 parser `0x5886C0` 讀 addr/port/token，`0x4A8370` 的 region3/4 分支把 token 傳給 C10 constructor `0x577330` 並送出；它不是 C25 codec。**此前對 C25 的此一行不能再作為 observed-static 證據**。其餘 A-022 的 S14/S15/C35/MAP 研究不因本次更正而更動。


## A-022 後續原始 MAP 補充（2026-10-31，取代當時「僅有 EXE」資源缺口）

此原研究進行時只見原 Client；**現在**已收到 `Map0.dat`、`Map1.dat`、`Map2.dat` 並核對 SHA/解析。追加 [A-022 MAP 幾何／碰撞資料報告](A-022-roy1-map-geometry-collision.md)、[Server 交接](../04-analysis-integration/A-022-map-geometry-contract.md)、[491 MAP 機讀清單](../02-server-planning/map-geometry-evidence.json)、[獨立探測工具](../tools/a022_map_geometry_probe.py)。原件 archive 36-byte record 結尾是 payload **end offset**，494 命名項目中 491 份完整 tile 資源，`00000.map`／`10000.map`／`20000.map` 為零維特殊資料；8-byte MAP header 有3 u16LE+w/h u8、2-byte block grid `ceil(w/2)*ceil(h/4)`、10-byte raw tiles→17-byte local、7/8/16-byte 尾段。原 Client `0x4B4BB0` 線段測試 tile+6 bit0x10，`0x4B2CA0` 可修改 tile flag bit0x01；**不能因此推論原 Server 可走格／原生新手出生點**。原 C35 第二字 structured CRC 尚未逐圖計算。A-022 integrated/handoff partial，map geometry 可用，native 全部 collision/原版 tutorial map/spawn 仍 unknown；CT-069～071 planned。
