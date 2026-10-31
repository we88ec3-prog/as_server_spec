# A-010／roy2 — 原版技能施放、取消與持續效果 Client I/O（BIN-first）

> **main 合併補正**：來源分支測試 CT-089/090 與已整合經濟/地圖測試同號，本版使用 **CT-095（技能離線）／CT-096（原版施法/BUFF UI）**。本報告是 Client packet/producer 靜態子集，不是原服技能冷卻、效果或原生GUI完成證明。


> 日期：2026-10-31。沿用 `task_a/roy2`，不建立 branch、不修改 `Asgard.exe`。研究交接 **integrated / partial**：已補足六種原生 Client spell packet decoded-body，包含持續效果加入/移除與取消；技能類別（單體／範圍／治療／BUFF／召喚）完整對應、原版冷卻／消耗／過期與 Native Client GUI 尚未證實，**不得宣稱原服已還原**。

## 0. 證據來源與命名防混淆

- 原始 `Asgard.exe` PE32 / I386 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；PE ImageBase `0x400000`。本次由原件反組譯對照 6 個 MSVC RTTI class、native constructor push opcode、reader/writer call 與實際 C4D callsite；`task_a/roy2/a010_native_probe.py` 在原件驗證 25 instruction VA + 6 RTTI。
- 對照 A-025（已證 C4D/C56/S52 最小子集）、A-009（C13、S13、S5F）、A-008（S08）以及 A-007（裝備／資源）。不要把戰鬥 `S13` 效果或 `S5F` 死亡與本 A 的「持續狀態」封包等同。
- 此處 `S2C` 是 **Server opcode 0x2C**，不是「Server to Client」的縮寫。所有 body 是**解密後 payload**，不含 AA framing/ordinal/opcode/XOR。wire 大端整數：`0x45AB40=BE u16`、`0x45AC40=BE u32`（writer），`0x45ADB0=u8`、`0x45ADE0=BE u16`、`0x45AEB0=BE u32`（reader）。
- 原版 Client 有 `SkillSpellDialog`、`LastingSpellDialog`、`LastingSpellInventory`、`LastingSpellEstimateDialog`、`EffectRunner`、`EffectObject` 的 MSVC RTTI/renderer class，但存在類別 **不等於**能證明指定 spell-id 是補血或召喚，也不等於 S2C→某 UI handler 的完整回調已驗收。

## 1. 六條原生 opcode→class→writer/reader

|方向|原生封包類別|native ctor/codec VA|decoded body（不含 framing）|可信度與界線|
|---|---|---|---|---|
|C→S `C4D`|`CStartCastSpellPacket`|`0x575510` push `0x4D`; `0x5755C0` writer|`BE u16 opaque_spell_value`（2B）|**observed-static**。從 Client local spell value 取值，非 Server 自認冷卻成功|
|C→S `C56`|`CCastSpellPacket`|`0x571750` push `0x56`; `0x571800` writer|`u8 opaque_cast_parameter`（1B）|**observed-static**。原生 sender 由何 UI callback 發出、是否每次跟隨 C4D，未證|
|S→C `S52`|`SCastSpellPacket`|`0x57D550` push `0x52`; `0x57D600` reader|`BE u32 opaque_reference, u8 opaque_state`（5B）|**observed-static**。u8 不可自封為 success/failure enum|
|S→C `S48`|`SCancelCastSpellPacket`|`0x57D3F0` push `0x48`; `0x57D4A0` reader|`BE u32 opaque_reference`（4B）|**observed-static**。Client 有取消/中斷通知接口；取消的來源與失敗狀態未知|
|S→C `S2C`|`SAddLastingSpellPacket`|`0x57A8D0` push `0x2C`; `0x57A980` reader|`BE u32, u8, BE u16, u8, string8, u8, BE u32, BE u32`（18+N B；N=0..255）|**observed-static**。動態字串按 encoded-byte length，native 用 `0x45B7A0` 解為本地 UTF16；不可將本地字串緩衝器 `0x200` 誤認為 wire 固定 512B；尾端兩個 u32 的時間單位未證|
|S→C `S2D`|`SRemoveLastingSpellPacket`|`0x585D00` push `0x2D`; `0x585DB0` reader|`BE u32 opaque_reference`（4B）|**observed-static**。此為持續效果**移除**，不是 `S5F` 物件死亡或 `S0E` 物件移除|

`S2C` parser 的真實 native local fields：`+0x18` u32、`+0x1C` u8、`+0x1E` u16、`+0x20` u8、`+0x22` wide string buffer、`+0x222` u8、`+0x224` u32、`+0x228` u32；reader `0x57A980..0x57A9E4`，每一步按照表內順序讀取。**本地 `+0x228` 並非 wire offset**。字串讀取 `0x45B7A0` 先讀 **一個 u8 encoded-byte length**（`0x45B7ED`），用 LanguageMan codepage 作轉換。原始 bytes 應保留；此版 CP950 是既有 profile context，不能假設所有語言版本都一樣。

## 2. 真實 Client 開始施法的來源與 sender

`0x402034` call `0x575510` new `CStartCastSpellPacket`；`0x402045` 由 `[ebx+0x80E]` 讀 **word**；`0x40204E` 寫 packet object `+0x24`；`0x402052` 呼叫 `0x5788A0` 送包。這是**獨立於 serializer 的 native producer**，證實 Client 有從已選取狀態形成 C4D 的路徑。

同一路徑 `0x402057` 又讀取此值並呼叫 `0x4FD1D0` 派發本地 action（本地 marker `0x53507573`）；可以確定 Client 有局部動作/視覺事件，但還不能把它稱為原版技能命中、MP 扣減或 Server 認證施放成功。C56 的 u8 writer 是原件可證，但**真正 UI/handler producer 尚未與施法鏈接通**。

`S52` 等收包 native reader 已確認，然而 `S48`→`SkillSpellDialog`、`S2C/S2D`→`LastingSpellInventory` 的**完整 dispatcher→UI callback、倒數計時與 refresh 時機**尚無經跨函式驗證的 handler 證據。不要把靜態 reader 成功當實機 UI 已顯示。

## 3. 技能類型與權威規則矩陣：不能從名稱製造內容

|研究類別|原版已知 Client I/O|未證的原始內容／規則|給 Server 的設計決策（不是原版）|
|---|---|---|---|
|單體（single-target）|開始 C4D、C56、S52；基礎攻擊另為 C13、效果 S13（A009）|特定 spell ID、取得目標、距離、是否直接走 C4D/C56、傷害公式|Server 驗證 World session／目標 identity、可見性、距離與授權；不信任 Client 宣稱傷害|
|範圍（AOE）|同一 Client spell 原生介面存在|半徑、扇形/方向、最多目標、座標 wire、是否使用 C3D/S3D variant|先列為 `UNVERIFIED`，不要以 C56 u8 亂解「AOE 半徑」|
|治療（heal）|Client 有 S08 status 資源更新（A008）|正式治療 spell/target/HP回覆順序及公式|HP 變更由 Server 自行計算與投影，S08 跟特效分離|
|BUFF／持續效果|S2C `0x2C` 可新增；S2D `0x2D` 可移除；S48 可取消施法|疊加、刷新、來源、驅散、倒數、過期時間、兩個 u32 用途|設計 epoch-scoped effect ledger、防重送、重登重新投影；**不把尾 u32 當 duration**|
|召喚（summon）|A024 的 S07 可生成 World object，跟技能處理分離|哪個 spell 召喚、AI、owner、duration、S07 type/EntityId|先視為 Server 規劃選項，不宣稱原 Client 原服定義|
|取消／失敗|S48 存在，四 bytes u32|由誰觸發、失敗時 Client UI/是否先收到 S52/是否退費|Server designed: 拒絕時不改 HP/MP；失敗/取消本地 UI 顯示需 native trace|

**關鍵結論**：C4D 沒有獨立的 cooldown、resource cost、target or timestamp 欄位；C56 僅一個 u8。不能憑這兩包推導原版最大範圍、CD 毫秒、技能效果、MP 消耗、任務計數或原版單體／AOE／heal／buff／summon 官方技能 ID。原服技能定義資料可能不在 Client，故沒有來源時要保持 unknown 而不是直接判 A 未開工。

## 4. 可交 DEV 的最小 Client 操作契約

|Trigger / 原生狀態|Client sends|Client receives|Client reaction／證據界線|
|---|---|---|---|
|在 World 選技能，原生 0x4020 施法入口|**C4D** BE u16|可能 S52、S48，**正式一對一時序 unknown**|C4D 有原件 producer，之後本地 `0x4FD1D0` action 呼叫；原版 Server 判定結果 unknown|
|接續/確定施法操作（具體 UI 未解）|**C56** 一個 u8|可能 S52|只有原件 ctor/writer，未證 C56 由何按鈕或 C4D 後必送|
|Server 投影施法事件|無此 reader 自動發包證據|**S52** BE u32,u8|Client 解碼為 local +0x18/+0x1C；enum meanings unknown|
|Server 中斷施法|無由此 reader 自動發包證據|**S48** BE u32|Client 解碼 local +0x18；取消效果、UI callback 尚待 Native CT|
|Server 新增持續效果|無此 reader 自動發包證據|**S2C opcode 0x2C** 動態 18+N bytes|Client 接收本地多欄位及 wide string；疊加/時間/圖示屬另階段|
|Server 移除持續效果|無此 reader 自動發包證據|**S2D opcode 0x2D** BE u32|Client 解析一個 opaque reference；是否依 ID 匹配 S2C 第一個 u32 需 callback 證明|
|攻擊成功／HP 變動／物件死亡|C13 是獨立基本攻擊命令（A009）|S13 / S08 / S5F / S0E 是**不同**投影|不得由 S52 代替 S08 扣血，也不得把 S2D 移除持續效果誤當 object death|

## 5. 自動化重現、測試與證據

```sh
python task_a/roy2/a010_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a010_skill_codec.py' -v
objdump -d -M intel --start-address=0x401ffe --stop-address=0x402079 Asgard.exe
objdump -d -M intel --start-address=0x571750 --stop-address=0x57180b Asgard.exe
objdump -d -M intel --start-address=0x575510 --stop-address=0x5755cb Asgard.exe
objdump -d -M intel --start-address=0x57a8d0 --stop-address=0x57a9e4 Asgard.exe
objdump -d -M intel --start-address=0x57d3f0 --stop-address=0x57d4ad Asgard.exe
objdump -d -M intel --start-address=0x57d550 --stop-address=0x57d617 Asgard.exe
objdump -d -M intel --start-address=0x585d00 --stop-address=0x585dbc Asgard.exe
```

|證據 ID|原件 VA / 動態解碼證據|
|---|---|
|A010-E01|`C4D` RTTI + ctor `0x575510` opcode4D, writer `0x5755C0` BEu16|
|A010-E02|C4D 真實 producer `0x402034..0x402052` 讀 `[ebx+0x80E]`、送 `0x5788A0`|
|A010-E03|`C56` RTTI + ctor `0x571750` opcode56, writer `0x571800` u8|
|A010-E04|`S52` RTTI + ctor `0x57D550` opcode52, parser `0x57D600` BEu32,u8|
|A010-E05|`S48` RTTI + ctor `0x57D3F0` opcode48, parser `0x57D4A0` BEu32|
|A010-E06|`S2C` RTTI + ctor `0x57A8D0` opcode2C, reader `0x57A980` 8 fields + encoded string8|
|A010-E07|`S2C` local wide name `+0x22`, `0x45B7A0` string8 byte-length / codepage conversion, not fixed wire UTF-16; local u8/u32 follow|
|A010-E08|`S2D` RTTI + ctor `0x585D00` opcode2D, reader `0x585DB0` BEu32|
|A010-E09|Original SHA-locked `a010_native_probe.py`: 25 VA anchors + six class RTTI; `test_a010_skill_codec.py` offline synthetic validation (CI status linked separately)|
|A010-E10|Original Native UI handler not-run and server spell taxonomy/cost/cooldown/range/expiration unknown; explicit source boundaries and test CT-095/090|

**驗證語意**：原件 SHA + instruction anchors 是 native **static**，unittest 是 **synthetic decoded bodies**，均不會證明原 Client 已連線施放成功；Native Client E2E 另屬 CT-096。原版 EXE、技能定義與遊戲素材 **不推至 Git**。

## 6. 真正缺口與檔案需求

- **此輪無新增必要檔**：`Asgard.exe` 已能證以上六類 native wire；`Born.dat` 和 `Map0/1/2.dat` 不能證原版官方技能表。
- **原始技能定義檔名未知**：尚未從已確認 Client 選擇器找出明確 `Skill*.dat` 或 `Spell*.dat`；不得要求使用者盲傳。應先用原始 `Basic.dat`（候選，不保證含技能定義）、實際持有的技能 UI/技能清單畫面、或原版合法 packet capture 反查具體 skill ID 對應與來源。缺失應表述為「尚無已證名稱的技能資料表」，不是創造檔名。
- 對完成原版 UI 閉環最有用的是去敏的 **native 原服遊玩 trace**：技能選取與 C4D/C56、S52/48、LastingSpell 新增/取消/自然過期的收包、UI 畫面/時間順序；另需 actor+spell target 追原生 UI dispatcher XREF。
- 原 Server 的 cooldown、damage/MP、buff stack、召喚存活／有效期可以由 DEV 設計安全規格，但不能稱其為 original; Server 的數值歸屬不要阻塞已證 Client wire 靜態研究。

**A010 結案判定：`status=integrated / handoff_status=partial / native_client_validation=not-run`。** 六包精確 native decoded body、真實 C4D producer、持續效果新增/移除/中斷接口與可重現工具已交；技能型別／完整施法時序、持續效果本地 UI 路徑及原服數值仍待證。這是 A-010 的**靜態 Client 交付結案**，不是聲稱全部單體／AOE／heal／BUFF／summon 已具官方完整資料。
