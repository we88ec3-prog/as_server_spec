# 從原型可操作能力補齊到正式 Server 的交付規劃

2026-11-01；依 [差距稽核](../04-analysis-integration/prototype-parity-audit-20261101.md) 與 [機讀待辦](prototype-parity-backlog.json)。這是語言／儲存獨立的合約，分析角色不修改Server、Web或DB。既有 [DEV-ENTRY](native-playable-entry-roadmap-20261101.md)、[ADR-008](post-create-direct-world-decision-20261101.md)、[ADR-009](expected-validation-failure-policy-20261101.md) 與 [R-037](game-packet-log-contract-and-backfill-20261101.md) 優先適用。

## 批次與先後順序

以下批次與技術合約是Server設計；其中多項功能目的來自**使用者明確需求／回報**，不歸因為程式分析新提出的需求。各PAR的`provenance`分列user_scope、analysis_scope與design_scope；精確來源見 [歸因規範](../00-governance/requirement-origin-policy.md)。使用者未指定S66/C75或5秒週期等細節。

|批次|差距項／現有責任|交付內容與完成條件|
|---|---|---|
|P0-A 入圖阻塞|PAR-001/002；DEV-ENTRY-01～04；RI-001/006/007|先對已存在角色打通C03/S03/C10後的原生World初始化；與新角C04後自動入World獨立驗證。重用opt-in C02/C04成功路徑，補負向S02/C15及原版callback，不能讓manual C03代替ADR-008。|
|P0-B 基本操作／恢復|PAR-003；DEV-ENTRY-05／ONB-04|接C11/C33/S0B、合法路徑、最新位置及面向持久化。最後ACK、權威接受序號、已持久序號明確；正常重登恢復最新接受位置。崩潰恢復窗口若非零要明示，不能永久回首次spawn。|
|P1-A 可操作外觀|PAR-005/006；R-006/008|衣櫃fixture與真物品實例分開，接穿戴、S05/S33/S37與保存；衣色獨立，轉向後更衣保方向。僅有ClothingId或codec不算可換衣。|
|P1-B 地圖與聲音|PAR-007/008；R-004/022|有權限的在線傳送、版本化map/spawn／CRC、失敗恢復與AOI；播放／停止及每圖音樂政策。先已驗1～2圖，不宣稱494圖全可用。|
|P1-C 穩定性及測試工作台|PAR-004/009/010；R-018/019/037|已證S66/C75時間同步只在允許階段；角色查詢／外觀／傳送／音樂的真API接受權限與版本檢查；UI呼叫API、回報更正與trace關聯。既有WEB-P0保留，不重建。|
|後續完整遊戲|PAR-011/012；ONB-05～07、M2～M5|原生改密碼、雙人可見與NPC／怪物／戰鬥／任務、經濟、社交、容量與恢復；原型沒有完整實作，不能算回歸倒退。|

這裡的P1表示原型能力恢復優先度；Web文件的P1/P2是畫面交付範圍，不能因此把本機切圖推遲到公網RBAC/MFA完成後。若仍限localhost與單一既有Admin Key，可先設計該安全邊界內的角色操作；外網／多人管理權限另案。

## 原生 World 與位置合約

- **同版資源**：MapCatalog含map_ref、resource/hash/revision、尺寸、C35 expected pair及合法spawn政策；教學圖身份未知可先用明示的測試圖，不把試驗map6宣稱原服新手圖。C10提供owner，C25 billing不是map或憑證。
- **出包與狀態**：依A-031/RI-007驗證首個S2C與UI manager初始化；原型S02→S05→S15→S14(1)是待對照候選，不能在MapPane尚不存在時盲發。真C35通過才commit epoch、定位與S14(2)。原生自動報告／附帶封包要按A-020/A-005解析與階段分類，不把原型「忽略未知」直接搬入。
- **latest location與首次進圖分離**：一次性首次入圖／任務outbox不可充當每步位置。權威命令序列更新map、x/y、facing、revision、accepted_seq；DB／journal策略由實作者選，但明示提交水位與恢復窗口。舊socket清理不能覆寫新世代位置。
- **權威移動**：原型夾邊界或客戶端預測不是Server碰撞規則；採A-005已證predicate與明示動態overlay、速度政策，無效步驟按ADR-009校正／回覆，不僅因正常被擋就斷線。ACK重播不得再走一步。

## 穿戴與染色合約

- 正式背包使用穩定item_instance與owner、版本、數量／裝備槽；可另開Development明示的無限衣櫃fixture，不混入經濟。資源外觀ID、物品定義、庫存slot、裝備slot、instance ID不可共用同一個整數當所有身份。
- C1C/C1E只接受已證profile與玩家持有／可穿slot；一次穿戴交易先變更權威裝備，再投影已證S37與S33，自身／其他觀察者看到同一結果。重送、過期slot、重登／換圖不可複製或丟物品；未解use-kind留A-007。
- 持久Appearance至少區分sex、hair、hair_rgb、clothing_ref、clothing_tint（original/custom）；沿用現有hair狀態，不複製建立第二份互相覆蓋的資料。S05與S33一致，更新外觀不重設位置／facing／HP/MP。
- `ff00ff`無染色與已知S33 `000000→ff00ff`保留語意不可當一般純黑。管理端須如實表達限制；沒有染色層的素材不保證整件變色。
- S04置中只在已驗viewport下算錨點。800×600候選8/9是profile-specific；不能透過改world x/y修飾顯示偏移。參照A-006與CT-073/074。

## 在線傳送合約（管理操作，不新增虛構遊戲C2S）

1. 管理者權限／reason／idempotency與expected角色版本通過，查到目前owner、generation、InWorld狀態；先驗目的map/revision與合法spawn。offline設定與online傳送是不同操作。
2. 單一TeleportIntent綁owner/generation與新的loading epoch；鎖定或序列化移動／穿戴衝突，S15/S14請求合法載入，核對本epoch C35，成功才commit最新位置並發S04/S33/S14(2)。沿用原生相容順序，不要求重新登入。
3. 超時／錯CRC／斷線不得寫成成功：在可恢復的舊圖保持或以明確失敗狀態重登復原，不能混合新圖座標與舊圖資源。舊epoch ACK及相同管理請求重送不再傳一次。
4. 共享世界先處理舊AOI離開再建立新AOI加入，保留別人的NPC／怪物；保留裝備、衣色、任務、面向及帳號身份。尚未有多角色並發驗證時可限制每角色一個有效World session，不能使用原型「整個Server只能一人」當正式架構。

## 時間同步／BGM合約

- S66/C75已有原型及Client靜態證據：S66 u32 challenge，C75兩u32；確認完整codec／bit序與允許phase後才接，有限outstanding、TTL、重送／無匹配回覆分類，不能以Client時鐘授權移動／獎勵。每5秒僅原型測試政策。創角畫面無已證heartbeat，不把InWorld檢查移到FormInput；分階段期限與「視窗有回應」仍分開。
- BGM使用A-019已證S19(kind1,repeat0,u16 track)，0停止；只選可用曲目、保留Client音量／靜音。若自訂map→track，標記`designed`並版本化；原服映射unknown不阻擋明示的自訂測試政策，但不能宣稱官方原配曲。過期load epoch的音樂不得蓋新圖，重登／切圖及在線變更都依當前政策。

## Web／本地測試交付

邏輯能力是CharacterRead、ResourceCatalogRead、TeleportRequest、AppearanceChange、EquipmentChange、MapAudioPolicy、TestReportAppend／Correction；名稱不是已存在HTTP路由。每個新API先對應Server domain、既有Admin認證／權限、版本／冪等／audit與狀態回覆，再設計頁面。列表／搜尋／分頁也不是現有P0自帶能力。

回報保存report_id、revision、case、result(pass/fail/not-run)、操作時間／Client變體／Server build／匿名trace，保留原失敗及更正關係；不把不小心勾pass覆寫原紀錄。缺關鍵資料由整合者讀本地紀錄補齊，使用者不當A與DEV之間的傳話人。公開Git只收去敏結論；帳密、E-MAIL、hash／token、DB、完整runtime原件不入repo。

動畫／tooltip／預覽屬Client測試工具。保留原始素材與Client身份，不為新Server移植patch；未修改Client的原生入口證據先解RI-006與A-028，不以副本工作台取代正式驗收。

## 分析與開發交接

機讀項目列出既有R／A／CT、已知證據、精確剩餘問題及依賴。**有證據可實作的codec／domain可先開發；原版CT未跑不等於A要重做。** 開發者回報component status、Server SHA、profile、合成結果；CT另附原版畫面／去敏trace。依 [批次回歸](../05-conformance/prototype-parity-regression-20261101.md) 逐項勾結果，前段失敗未到達的後段寫not-run。
