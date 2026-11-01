# 教學怪物共享狀態與普通攻擊結算

## 需求與原件邊界

**使用者需求**：新手場景可普通攻擊打怪，完整教學接好後才安排人工測試。
本輪完成持久結算核心及Host C13處理，尚未在現有啟動器啟用，也未GUI驗收。
原件證據沿用[目標與效果分析](20261101-native-combat-target-and-effect.md)。
原服HP、傷害、冷卻、重生及必殺條件未知；以下為明示的**復原Server政策**。
測試的HP3、傷害1／2及2秒重生不是原版資料。

## 可信內容與共享識別

內容含精確map/ref與revision、policy／admission revision、固定每擊傷害、
間隔、重生延遲及1..32個spawn。每個spawn含key、ref區段、位置、面向、
image及最大HP。傷害1..10000、HP1..100000、間隔100ms..5s、重生1s..10min
是本地界限。Host另驗可信地圖及spawn可站立；不是由Client提供內容。

目前單realm內，怪物依`map/ref + map revision + spawn key`共用DB狀態，
不是每Client各一份。完整排序後內容契約與地圖版本綁定；變更policy字串或
傷害欄不能重設HP，內容不同需明示遷移，不靜默覆寫。

Server自訂reference base區段0x20000000..0x3fff0000，低16位為0，同圖唯一。
wire ref為base OR life_sequence；sequence初始1，重生加1。達65535或version
耗盡則保持死亡，不循環重用舊ref。此區段不是Client推得的官方ID範圍。

## C13與命中權限

C13只有BE u32參數，不含傷害、HP或milestone。Host要求WorldReady、當前
owner與載圖已提交，只在顯式教學地圖結算；對話進行中不攻擊，未配置地圖
不開放任意NPC／PvP。零值不自動選最近目標，也不造成傷害。

非零值必須先由本連線投影為活目標。猜中的未發行ref最多取得場景投影，
不直接命中；講師與招募員不在可攻擊集合中。交易再次核對owner、generation、
connection、同版本入學事件、無pending載圖、來源map與完整位置version。
目標需為目前生命的確切ref、HP>0，max(abs(dx),abs(dy))<=1。這是教學近戰
政策，尚無視線／射線、怪物反擊或技能範圍，不能稱完整戰鬥系統。

冷卻讀角色最近已提交hit的UTC時間，換目標、重登或重開Server不清空。
快速重送不再扣血；時間倒退不提早放行。C13沒有原生request ID，相同body
在間隔過後仍是新嘗試，不能宣稱靠body達成無期限exactly-once去重。

## 同一筆命中交易

實際傷害=min(設定傷害, 當前HP)，HP不為負。依目標方向設定角色面向，
來源position version加1但不移動座標。以下原子提交：

1. 共享HP、actor version及死亡後respawn deadline。
2. 來源面向／位置version。
3. 唯一hit audit：前後HP、實際傷害、life sequence、actor version及來源version。
4. 固定`practice-attack-resolved` milestone，revision使用policy revision。

只有實際扣除正數HP才有攻擊紀錄；TALK／Dispose、零值、陌生／遠／死目標及
冷卻拒絕都不能產生它。不改教學完成旗標、首次checkpoint或發經驗／掉落。
完成仍由出圖交易與其明示條件決定。

SQLite交易序列化寫入，PostgreSQL另設共享內容列鎖；owner鎖及actor version
比較防兩人各自從同一舊HP寫入。場景讀取／攻擊時檢查重生deadline，回滿HP、
增加sequence／version並保留hit歷史。舊ref不能傷害新生命。拒絕攻擊可能同時
處理已到期的重生維護，但不新增hit或milestone。

## Client投影與尚未啟用的部分

活目標以S07 kind2及S1A站立初始化；命中回S11自身面向與S13效果，死亡投影
S5F。重生先S0E清舊ref，再S07／S1A發新ref。kind2及helper4037是靜態線索
支持的候選，尚未Client GUI確認。S13不填猜測的扣血數字，HP顯示仍待確認。

現有native trial的自身S05／S33視覺ref為1，自己的攻擊沿用它；沒有當成全服
唯一玩家ID，沒有向別人發ref1來源動畫。共享HP與多玩家即時可見性是不同交付。

已提供須與HandleAsync串行呼叫的場景poll，維持每連線已見ref／生命狀態。
**TCP listener尚未掛背景poll，Program／啟動器尚未傳入combat profile**。
不能宣稱停著不操作的其他Client已即時收到死亡／重生；後續需序列化ordinal
與寫入。合法舊C13在切圖中沿既有64次雜訊預算解析後丟棄，不扣血或誤斷線。

## Schema、驗證與剩餘工作

World v6增共享內容、actor、hit audit三表。actor以map/revision/spawn唯一，
reference base同圖唯一；hit以map/revision/spawn/actor version唯一。已有帳號
的file-backed SQLite缺擴充時先一致性備份；本輪未動運行中的DB，PostgreSQL未實測。

343項Server測試通過，包含傷害夾限、無效／遠／死目標、冷卻與重登、舊owner／
舊位置／loading、內容不符、兩角色經barrier啟動並行攻擊只一次死亡、共享重生／
舊ref失效、sequence不循環，以及milestone寫入失敗時HP／面向／hit／冷卻一起回滾。

五職業Host出圖測試已由C13→實際Server扣血產生practice，不再直接注入；
另驗命中／死亡封包、死亡後重登、新舊ref隔離及切圖舊攻擊丟棄。這些是合成
Host／SQLite驗證，不是原始Client已玩完教學。

主線仍缺啟動配置、TCP即時投影、學校／各城鎮確認、數字職業投影及完整GUI。
原生動作、死亡時序與kind也要實機確認；整體目標保持未完成。
