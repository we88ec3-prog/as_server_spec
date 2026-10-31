# A-008／roy2 — 狀態面板與數值更新：原版 Client 靜態研究

- 日期：2026-10-31；分支：`task_a/roy2`。
- 原件：`Asgard.exe`，SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，PE32 i386，ImageBase `0x400000`。
- 追蹤：SYS-STATS／R-009／A-008。**這是可交付的靜態子集，尚未證明完整欄位 wire layout。**

## 已核對的實際原件線索

獨立使用本次提供的原版 EXE 的可列印 MSVC RTTI 字串搜尋，並非由 Server 設計反推：

|項目|原件 RTTI 名稱|觀察及限制|
|---|---|---|
|角色數值模型|`.?AVStatus@@`、`.?AV?$Singleton@VStatus@@@@`|observed-static：有 Status 類別與 singleton；尚未定位每個狀態欄位 offset。|
|數值 UI|`.?AVStatusDialog@@`、`.?AV?$PlainMemberFunctionObject@P8StatusDialog@@AEXK@ZV1@@@`|observed-static：狀態面板及其 callback 型別存在；尚未證明點開 UI 是否送網路封包。|
|經驗值 UI|`.?AVExpBarDialog@@`、`.?AV?$PlainMemberFunctionObject@P8ExpBarDialog@@AEXK@ZV1@@@`|observed-static：經驗條另有 UI；尚未證明經驗值的數值寬度、單位及更新封包。|
|狀態 S2C 類別|`.?AVSStatusPacket@@`|observed-static：原生 SStatusPacket 類別存在；**opcode、欄位長度、endianness 未核實**，不得宣稱是 S05 或任何現有 opcode。|
|狀態相關類別|`.?AVSMapStatusPacket@@`、`.?AVSAddLastingSpellPacket@@`、`.?AVSRemoveLastingSpellPacket@@`|observed-static：不同狀態／持續效果封包類別存在；不可在未追 vtable / parser 前把它們等同 HP/MP/BUFF 數值。|
|玩家點數操作|`.?AVCAddAbilityPacket@@`|observed-static：Client 具有 AddAbility 類別；**尚不能確認操作 UI、opcode、各能力值及是否扣點**。|
|戰鬥變化|`.?AVSDamageEffectPacket@@`、`.?AVSBattlePacket@@`|observed-static：戰鬥相關類別；不能據此推出 HP 扣減規則或死亡閾值。|

## Client trigger → C2S → S2C → UI 矩陣

|Trigger / 前置條件|C→S|S→C|Client 效果|信心水準|
|---|---|---|---|---|
|玩家打開數值／狀態面板|未證實；不假定一定送包|不應假定每次開啟都需要回包|StatusDialog 有原件 RTTI，但其讀取 Status 的 callback 尚待 XREF|UI 類別 observed-static；流程 unknown|
|玩家查看經驗條|未證實|經驗值更新 opcode unknown|ExpBarDialog 存在；百分比／等級表示未知|UI 類別 observed-static|
|玩家分配能力點|CAddAbilityPacket 類別存在，writer/opcode/欄位尚待核對|SStatusPacket 是否為回覆尚未證明|成功／拒絕更新與剩餘點數 UI 未證|packet class observed-static；流程 unknown|
|登入初始化世界狀態|C03→S03→C10 登入交接依 A-002 已證子集|已知 S05 是**自身外觀**而非完整狀態表；SStatusPacket 路徑待確認|不能將 S05 的 RGB/flag 欄位視作 HP/MP|A-002/A-006 已證；stats unknown|
|受傷、回復、死亡、BUFF 更新|戰鬥／施法送包分屬 A-009/A-010，具體觸發待查|DamageEffect、Add/RemoveLastingSpell 類別存在；生命值同步 packet 與順序待驗|動畫不等於已證的數值更新或 Server 權威|類別 observed-static；wire unknown|

## DEV 最小交接及防止資料錯判

1. **可立即利用**：Client 存在獨立 Status、StatusDialog、ExpBarDialog、SStatusPacket、CAddAbilityPacket 等 native 類別；因此 Server 數值模型不應直接與人物外觀 S05 或戰鬥特效相混。這是結構性證據，**不是足以發送 SStatusPacket 的 wire specification**。
2. **禁止猜測**：HP/MP、最大值、經驗/等級、體力、攻防、能力點、裝備加成、數值小數位、u8/u16/u32、signedness、buff 疊加、上限與死亡臨界均未取得 native parser/writer 的逐欄證據。
3. **designed 安全策略（不是原服規則）**：Server 自行保持 authoritative HP/MP/等級/經驗、範圍檢查及 saturating arithmetic；非法或重複能力點請求不得重複扣點；死亡之後的動作命令須有明確狀態門檻。無已證 wire 時不應傳送猜測的 SStatusPacket。
4. **CT 建議**：離線核查 RTTI/EXE hash；後續 native 驗證需登入前後開狀態窗、分點前後、換裝前後、受傷/死亡/復活/重登各一次，擷取 decoded opcode＋body＋UI 差異，再交叉追 parser VA。這些測試尚未執行。

## 未解項與後續具體分析入口

- 由 MSVC RTTI `SStatusPacket`、`CAddAbilityPacket` 反向尋找 TypeDescriptor → CompleteObjectLocator → vtable → constructor（opcode）→ reader/writer → Status 欄位 offset → StatusDialog 更新 callback。
- 對 `StatusDialog`/`ExpBarDialog` 追 UI 入口與資料來源；補 byte-for-byte 合法、超界、死亡邊界測試。
- 對裝備修正交接 A-007、戰鬥傷害 A-009、BUFF A-010，**缺完整 status wire 時不可擅自標 implementation-ready**。
- 沒有新必需檔名：本輪的 `Asgard.exe` 已提供；若後續 UI 需要獨立配置資源，必須先由原件引用定位檔名，不泛要求整包美術資源。

**結案界線**：A-008 的原件類別及責任邊界已完成一輪可重現靜態調查；完整 HP/MP/狀態封包及 UI callback **尚未解析**。保持 `status=open / handoff_status=partial / native_client_validation=not-run`，不得將這份初步證據標為 A-008 完全完成。
