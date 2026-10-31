# CT-115：原生 S66/C75 時間檢查與階段邊界

2026-11-01；status=planned，原版Client not-run。PAR-004的專屬增量，不能拿CT-009(zlib server list)或CT-056/057(prelogin)當時間同步驗收。

既有本地研究定位：SCheckTime ctor0x57DC80／reader0x57DD30，handler0x4F13C0..0x4F1491；CCheckTime ctor0x571DD0／writer0x571E80。S66讀一個u32，C75寫兩個u32；原型使用BE u32，第二欄語意及各region完整行為仍須A-001/A-020核對。原型InWorld每5秒challenge曾有往返紀錄，**5秒是自訂政策，不是原服常數**。

交付與回驗：

1. 靜態／codec：確認u32的byte序、精確長度、第二個C75欄位來源、允許phase、截斷／尾部／重送；解不出的語意明示unknown，不把時間欄位當owner、移動速度或獎勵授權。
2. Server合成：有限outstanding與TTL、challenge唯一／環回、一次匹配、失配／過期／重播分類及限流；不以任意bytes或TCP keepalive重設合法遊戲動作時鐘。記metadata，不記原始payload。
3. 原版InWorld：取Client SHA／region／Server build，在站立、移動、切圖前後對照S66→C75／phase／時間及UI回應；計畫窗口須跨越舊退出時間。沒有C75不能單獨判定crash，須結合程序及TCP。
4. FormInput獨立：不要求尚未證實的創角／登入畫面回覆S66/C75，停留超過60秒依已設定表單政策處理；不能用遊戲內時間同步取代RI-005階段期限修正。
5. observer／舊世代／重連隔離：不讓上一連線challenge或另一角色回覆延長本會話，也不讓切圖未完成時過期結果改變新epoch。

合成通過、修改副本往返與原版GUI三欄各自記錄。本次只新增驗收合約，未執行遊戲或Server測試；未證的phase或欄位保持研究缺口。對應 [補齊合約](../02-server-planning/prototype-parity-delivery-plan-20261101.md) 與 [原型差距](../04-analysis-integration/prototype-parity-audit-20261101.md)。
