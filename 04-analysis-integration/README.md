# 分析結果整合

本區是各Server實作的共同輸入，不是原始證據堆放處。分三層整理：

1. **封包契約**：Client送出／Server收到後的驗證與狀態變更；Server發出／Client收到後的parser、handler及可見效果。
2. **情境契約**：多個封包的先後、前置狀態、成功／失敗／取消／斷線與重送。
3. **遊戲系統規則**：資料模型、公式、時間、權限、資料一致性，以及哪些是原生證據或自訂規則。

packets.json以profile+direction+opcode作識別，不用opcode單獨索引。登錄34個目前相關入口，**不宣稱已包含全部126個RTTI候選或完整登入／戰鬥協定**。partial項目是分析入口，不是足夠實作的規範。補完前先連到A並禁止宣告完整相容。

每個完整封包頁應含：body offset／型別／byte序／長度單位／編碼／條件式欄位／未知值、方向與允許狀態、原生serializer/parser/handler、Server應收發之語意、Client效果、錯誤分支、Evidence ID、CT與SCN、支援profile、限制及版本變更。

閱讀順序：[transport](transport.md) → [最小登入profile](profile-login.md) → [雙向處理矩陣](packet-processing.md) → [appearance](appearance.md)／[items](items.md) → [情境](scenarios.md) → [系統規則](game-systems.md)。

既有成果補充：[覆蓋對照](analysis-coverage.md)、[資源與地圖格式](resource-formats.md)、[Client相容性](client-compatibility.md)、[Evidence身份索引](evidence-index.json)。
