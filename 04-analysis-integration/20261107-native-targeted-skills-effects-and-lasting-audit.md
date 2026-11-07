# 原生指定目標技能、特效與持續狀態盤點

2026-11-07。延續 A-009／A-010 與 web skill review 的 A010-D01..D06，先讀既有成果，再以同版原始 EXE 和資源補證。原件 SHA 及精選 metadata 見 [JSON](20261107-native-targeted-skills-effects-and-lasting-audit.json)。本輪不修改技能實作或 Client；靜態可讀／素材存在與實機可用分開記錄。

## 可直接交開發的指定目標入口

S62 是加入技能清單，包含 use mode、名稱／命令文字、圖示與 CastValue；它不是施放特效包。原件 `0x46d2c0`／快捷列 `0x445200` 明確區分 mode5 直接執行與 mode2 進入選取狀態。mode8／9也有座標相關分支，不能一起當成物件目標。

本輪已追通 **mode2、CastValue0**：

1. `0x46d130` 保存技能 row 並設 GameLogic targeting state1。
2. `0x46d970` 以目前選取 ref 查 registry，取得雙方位置，檢查距離及格子阻擋，建立 CUseAction；完整 packet+0x28 寫入目標 ref。
3. `0x4b8d70` 安排 `0x4b76d0` callback，必要時先轉向，再呼叫 `0x401ed0`。
4. CastValue0 分支先送 C0E kind2／技能文字，再送原先 CUseAction。
5. `0x577aa0` mode2 writer 的 **C65 body 恰好6 bytes：`u8 kind, u8 slot, BEu32 targetRef`**。mode不在 wire，必須依 Server 已發出的 S62 row 解釋。

C0E 沒有 target，不能在收到它時就結算指定目標技能；否則後到 C65 可能造成重複攻擊或錯打面前物件。Server 應等待匹配已發 mode2 row 的 C65，再權威檢查 owner／lease、載圖、生命世代、已投影目標、距離、資源與冷卻。不能拿 C44 hover 自動當作施放意圖。

### 距離欄位的重要更正

Client 的 `ActionEntry+0x80a` 確實用於 `abs(dx)<=range && abs(dy)<=range`，但它不是本輪已證的 S62 可設定尾 byte。`0x579020` reader 在讀第三文字後，直接將本地 packet+0x622 初始化為 **100**，再讀第四文字。完整 packet+0x62e經 `0x4f2cd0`、`0x4017d0` parameter9 存入 entry+0x80a。

因此 Server 距離6等數值是重建政策，必須自行驗證；不能把未定義的尾 byte 填6並稱其為原生射程欄位。`0x4b4bb0` 是兩位置間的格子阻擋檢查，遇 tile byte+6 bit0x10便拒絕；不是目標類別枚舉。另有 entry+9==1 的玩家／PvP條件，不能省略未知語意後宣稱所有玩家目標都可用。

## 方向與「必須先普攻」問題

`0x4430c0` 搭配二欄位 constructor `0x46e500` 回傳：0=(0,-1)、1=(1,0)、2=(0,1)、3=(-1,0)、4=(1,-1)、5=(1,1)、6=(-1,1)、7=(-1,-1)，8=(0,0)。既有 Server 的方向表與此一致；把 heading2 寫成 east 是測試說明錯誤，不能據此調換方向表。

所查 S13 `0x4f2620`、Human `0x47bc20`、數字 `0x4a4b00→0x4b6850` 路徑，沒有發現「必先收到 C13 才可播放技能」的前提。來源是本地角色、目標是合格怪物時，S13 自己會設定怪物選取。Human 先依 Motion與flags呼叫動作 setter，EffectSelector0也不會阻止這段動作；來源為本地角色的傷害數字也直接建立。

這不排除尚未觀察的執行中狀態。部分入口沒有 Ghidra procedure，使用精確指令補證，沒有新增函式或修補 EXE。mode5 技能只打面前格與普攻先轉向，是需要與實際 Server 命中紀錄區分的另一個原因。

## 一個有完整靜態素材鏈的特效候選

原件 `0x458030` 將 effect ID 拆為 bank=`id/1000`、index=`id%1000`，bank須0..4；載入 library15+bank、member index+1。`0x404082..0x4040ad` 以 `Effect%01d.dat` 綁定library15..19。這是實際索引路徑，並非依檔名猜技能。

`.eff` 內部是 **little endian**：loader 明確呼叫 `0x45ada0(0)`，`0x45ade0` 在該模式直接讀原生u16。網路 wire 的 BE不可套用到這份資源。type2 節點的 imageKey 經 `0x459680→0x44ffb0→0x44cc60/0x44eec0` 映射到 library15+imageKey/1000、member0、object=imageKey%1000。EffectSelector與imageKey即使數值相同，仍是不同欄位。

本輪最小候選 **EffectSelector4000**：

|項目|原件與檢查|
|---|---|
|archive|Effect4.dat，SHA `5cac55442e8504786bf9e8b7be73eed2a1cd05a65970739e1fdf24df0f7e58dc`|
|runner member|slot1 `Effect04000.eff`，offset11707188，1979 bytes，SHA `85f197f104e3716fff798aaa4205d193a977963d194f48a0af57d2aa2edc9bac`|
|runner結構|version9，恰好type0＋type2；完整節點／引用表解析至1979，無尾隨；沒有type7音效節點|
|圖片member|slot0 `effect04.ypf`，offset4216，11702972 bytes，SHA `e5c9d3990b9b40012812eb466ee630da58473db9ff44700d754fd1ed9aa4c867`|
|imageKey4000|object0，共12 physical frames、1 action、1 state；全部52 objects的有界metadata掃描恰好到data base35618，所有影格channel範圍均在member內|

這可作 **Development通用特效候選**，仍需實機確認可見形狀、方向、附著／飛行與時序。沒有命名為原版火球、補血或buff，也沒有由此推導傷害／治療公式。來源 S13 EffectSelector 可進入此原生 runner；S13 擴充中的接收者效果是另一投影通道，需分開驗收。

另外1001、2001、3000也完成version9 runner結構與對應YPF object metadata核對，機讀檔保留精選資料；這三者含type7節點，本輪未完成其音效依賴鏈，不能與4000一樣視為最小封閉候選。selector1的資源是version7，本輪version9 reader明確拒絕，不冒稱全ID均支援。

## 真正詠唱、遠程與buff仍缺哪些證據

|接口|目前能證明|仍不能宣稱|
|---|---|---|
|C4D|CastValue非0時送BEu16並保留待用技能packet|已解完整詠唱／完成／失敗／退費握手|
|S4D|本輪沒有建立對應技能意義|不能把C4D誤稱S4D，或以S4D代替S62清單|
|C56|已知u8 writer|何時發出及與target／phase的完整對應|
|S52|BEu32＋u8 reader|u8是成功枚舉、或收到後必送C56；本輪World派送表落default，另層handler未接通|
|S48|World派送slot32→0x4f2a70；存在ref呼叫actor virtual+0x48，否則走缺物件fallback|SkillSpellDialog pending清除／詠唱退費已完成|
|S2C opcode0x2C|持續效果新增wire `BEu32,u8,BEu16,u8,string8,u8,BEu32,BEu32`|尾u32是duration、stack／refresh／重登倒數規則已證|
|S2D opcode0x2D|移除wire BEu32|完整LastingSpellInventory identity匹配及自然到期callback已證|

因此 **可指定遠方物件** 與 **可播放原版遠程投射物** 是兩個完成條件。mode2 Cast0提供前者；某個原版法術的投射物、詠唱、音效、buff持續圖示與數值仍需各自閉環。類別名、RTTI存在與reader可讀，都不取代實際dispatcher／handler／資源／GUI驗收。

後續沿既有 A010-D02／D03／D04 深入，不另創重複A編號：先定位S52與S2C/S2D的非World接收者，追pending use packet釋放／C56 producer，再核對lasting identity、圖示與計時。原服技能名稱→effectID、消耗、範圍與持續時間沒有原始表時維持unknown；可玩的重建規則另外標示。

## 可重現與驗證界線

原始證據與有界讀取腳本僅存本地 `workspace/anal-roy-temp/warrior-skills-20261107`。公開JSON提供原件SHA、函式、精選資源offset／SHA、節點及frame計數，可依同版原件重建讀取器；不包含圖片或完整資源。

本輪已完成mode2 writer／producer交叉證明、常數range來源、四個version9 runner完整長度檢查及四個YPF完整metadata界線檢查。沒有操作遊戲、沒有原服流量、沒有修改Host／技能／Client，也沒有把這些靜態檢查稱作GUI通過。
