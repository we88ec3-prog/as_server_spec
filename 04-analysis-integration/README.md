# 分析結果整合

最新郵件研究：[原生MailBox是外部NMCO3 SDK](20261108-native-mail.md)，不能把C12地址簿或本地Note ABI當遊戲郵件wire。[獨立文字內核](20261108-player-mail-authority.md)已備妥資料與權限，但沒有寄件入口，原生仍未相容。另補[lasting效果的秒數、刷新及主動移除](20261108-native-lasting-effects.md)，這是原件契約，尚未代表buff數值／持久化已實作。

最新經濟增量：[玩家交易權威契約](20261108-player-exchange-authority.md)與[原生交換操作／九格限制](20261108-native-player-exchange.md)。C4A／S42與C17／S6E分流，雙方資產原子交換；既有視窗不能假作可重置ready／覆寫道具列。原生GUI與郵件分開追蹤。

最新戰鬥增量：[共同交易、游標與生命代次契約](20261108-committed-combat-observation.md)、[原生S13旁觀顯示限制](20261108-native-observed-combat.md)。補齊上輪多人互見之後的逐次戰鬥呈現；保留原生GUI與PvP等未完成範圍。

最新多人增量：[原生遠端Human](20261108-native-remote-player-lifecycle.md)與[唯讀共享玩家／移動歷史](20261108-shared-player-visibility-and-motion.md)。S33互見、S64真路徑、外觀與租約回收已接；原生GUI與完整旁觀戰鬥事件另待完成。

[2026-11-02 五城官方地理交叉核對](20261102-official-town-geography-corroboration.md)：五張官方村落圖與本地導覽／MAP預覽相符，新增SHA／座標佐證與獨立路線檢查；原服出生映射仍分開驗收。

[2026-11-02 魔法師／預言者徽章原因](20261102-occupation-rank-badge.md)：原件signed FAME=-52選到occupation.ypf object7/frame2，並非選職碼或Title；hover卡死仍待實機。

[2026-11-02 原生傳送入口與路由授權](20261102-native-portals-and-route-authority.md)：Portals.tbl全表格式與幾何驗證、游標／小地圖anchor／S07標籤分工，及未接線的Server入口路由契約。

[2026-11-02 原生能力初始化](20261102-native-status-initialization.md)：S08可見欄位與body offset、持久出生基線、進圖／重登順序與備份政策；384項Server與五職業TCP通過，hover仍待GUI。

[2026-11-02 個人帳號與能力窗問題](20261102-personal-account-admin-and-status-window.md)：既有金鑰取得、獨立帳號流程，以及 S08 初始化／職業與稱號欄位的已證映射；當機原因與修正驗收仍待完成。

[2026-11-01 原型／新版Server差距稽核](prototype-parity-audit-20261101.md)：逐項整理既有實機範圍、新版接線狀態、不能沿用的簡化，並連到Server補齊與批次回歸。

本區是各Server實作的共同輸入，不是原始證據堆放處。分三層整理：

1. **封包契約**：Client送出／Server收到後的驗證與狀態變更；Server發出／Client收到後的parser、handler及可見效果。
2. **情境契約**：多個封包的先後、前置狀態、成功／失敗／取消／斷線與重送。
3. **遊戲系統規則**：資料模型、公式、時間、權限、資料一致性，以及哪些是原生證據或自訂規則。

packets.json以profile+direction+opcode作識別，不用opcode單獨索引。2026-11-08已登錄85個相關入口，**不宣稱已涵蓋完整原版協定**。partial項目是分析入口，不是足夠實作的規範。補完前先連到A並禁止宣告完整相容。最新地面增量見[C07拾取／C08丟棄／C0C物件重同步](20261108-native-ground-drop-pickup-and-object-resync.md)。

每個完整封包頁應含：body offset／型別／byte序／長度單位／編碼／條件式欄位／未知值、方向與允許狀態、原生serializer/parser/handler、Server應收發之語意、Client效果、錯誤分支、Evidence ID、CT與SCN、支援profile、限制及版本變更。

閱讀順序：[transport](transport.md) → [最小登入profile](profile-login.md) → [雙向處理矩陣](packet-processing.md) → [appearance](appearance.md)／[items](items.md) → [情境](scenarios.md) → [系統規則](game-systems.md)。

最新社交增量：[原生聊天](20261108-native-chat-and-whisper.md)、[普通／密語／隊聊投遞](20261108-world-chat-routing-and-delivery.md)、[原生組隊](20261108-native-party-membership.md)、[正式R-033權威結算](20261108-party-membership-and-authoritative-rewards.md)。收發與顯示格式有原件證據；範圍、限流、命令及獎勵快照邊界為Server設計。好友、黑名單與公會尚未完成。

既有成果補充：[覆蓋對照](analysis-coverage.md)、[資源與地圖格式](resource-formats.md)、[Client相容性](client-compatibility.md)、[Evidence身份索引](evidence-index.json)。
