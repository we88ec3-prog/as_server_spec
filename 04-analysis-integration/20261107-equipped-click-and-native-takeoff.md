# 已穿裝備點選斷線修正與原生卸裝

2026-11-07。使用者回報點已穿裝備斷線、要求可脫裝，並詢問泳裝／禮服缺攻擊動作是否原版設定。斷線時序見[事故紀錄](20261107-equipped-click-incident.md)，動作資源另見[素材分析](20261107-clothing-attack-action-presence.md)。此頁及[精選線索](equipped-click-takeoff-wire-20261107.json)提供可獨立重建的Client／Server合約。

## 點選與卸裝是不同原生請求

原件 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，REA Ghidra12.1.4。原始EXE與素材未修改。

|功能|原件入口|body，不含opcode／ordinal|本輪Server行為|
|---|---|---|---|
|點選已穿裝備的欄位更新|EquipControlPane `0x45c2a0`事件case1 → ctor `0x577490`／CUpdatePartPacket|C3A：1×u8，來自control+0x250格位|驗證當前World、精確長度後保持連線，不改資產；完整原生回覆仍待分析|
|角色裝備卸下|同handler事件case2 → CTakeOffPacket ctor `0x5757d0`|C1F：4×u8；此player分支送`slot,0,0,0`|核對已投影物品、owner／lease／版本／背包容量後原子卸裝|
|守護相關裝備分支|ProtectorEquipDialog `0x510370`事件case2 →同CTakeOff ctor|同C1F四欄，最後欄1|不套用玩家物品卸裝，不改資產，保持連線|
|CWearPacket|既有C1E|仍只有已證u8|本輪不將它改名／重用成卸裝|

事件case編號是Client內部輸入種類；本輪尚未把case2完整回溯至Win32具體按鍵手勢，雙擊／右鍵的原生GUI操作仍待驗。不能為方便測試而將單擊C3A當卸裝。

原件正面證據：

- C3A ctor `0x577490` 的 `0x5774a9` 為 `6a3a`；RTTI為 `CUpdatePartPacket`。handler僅在已穿欄位有內容時，把control格位寫packet+0x24再送出。這與本地兩次C3A len1隨即斷線的metadata相符。
- `0x577540` 完整11-byte writer為 `0fb6411850e8b635eeffc3`，即讀interface-view+0x18的一個byte後呼叫u8 writer。Ghidra Listing未把此位址建成可反編譯程序，因此這項是REA `read_bytes` 加指令解讀，不宣稱有成功decompile此writer。
- CTakeOff ctor `0x5757d0` 呼叫packet opcode0x1f，`0x5757e9` 為 `6a1f`，並初始化packet+0x30為0。角色UI分支寫slot至+0x24、+0x28=0、+0x2c=0。
- `0x575880` writer對interface-view+0x18／+0x1c／+0x20／+0x24皆呼叫 `0x45ab00`，所以是四個byte，**不是u8+u32+u8**。C++欄位曾以int表示，不代表wire寬度。多重繼承interface有12-byte位移，需與producer物件欄位一併核對。
- `0x510370`的守護裝備producer明確把packet+0x30設為1；不能因同opcode／格位就取得玩家裝備權限。

## 卸裝交易與畫面投影

1. 只處理已登入、載圖提交、當前有效World lease的角色。載圖中的舊圖C3A／C1F只驗形狀後捨棄，不執行換裝。
2. C1F只開放已證的`field1=0,field2=0,last=0`玩家分支；其他欄位仍保留原值供結構解析，不能以未知旗標更換其他裝備組。空格位或未投影格位不生造物品，也不斷線。
3. 由已發給此連線的equipment slot找Server持久instance ID與item revision，再以inventory revision做CAS。Client沒有提供或取得任意持久ID的權限。
4. Store在同交易驗owner／目前generation與connection／已提交load、物品位置與版本、未死亡、可用背包格。成功只把原instance移回空背包格並前進版本；不新增資產、不改髮色、面向、職業或染色。
5. 背包滿或死亡等業務拒絕保持原裝備及連線，刷新既有S0F/S37子集；不臆造原版錯誤封包。當前owner的CAS衝突讀回權威快照，過時World authority則仍拒絕。
6. 成功提交後，沿已審原生子集送S38 `[slot,0]`清除玩家equipment容器，再投影S0F背包及S33服裝0／目前外觀。重登由持久狀態重建，不以歷史成功receipt覆寫新狀態。
7. C3A本輪是已知請求的安全不變更處理：保留已投影S37的名稱／說明，**尚未實作完整欄位更新回覆或額外裝備資訊頁**。不能宣稱C3A已具完整原服功能。

Server內部operation ID／receipt不是C1F wire nonce。立即重送到已空裝備槽不二次轉移；若中間已有其他穿戴操作，單靠原生四個byte不能保證辨識所有歷史重送，仍需維持原子版本檢查與已投影物品身份。

## 泳裝與禮服的攻擊動作

兩性外觀1／2在目前YPF第一object的映射攻擊動作24..31及56..63均為空；基礎外觀0則有序列。這能解釋目前缺揮拳的現象，但其餘object／DOI及原服穿戴戰鬥政策未全部釐清，**不能據此斷言原版禁止穿著攻擊**。

本輪不改素材、不將站立／走路假扮攻擊、不自動換外觀或新增禁攻規則。卸裝恢復基礎外觀後可另實測原有普攻；缺動畫與Server是否命中／扣資源分開記錄。

## 驗證狀態

### 使用者實機回覆（修正後）

使用者對集中測試清單回覆「全部正常，卸裝及重登保存成功」。據此記錄點選已穿裝備不斷線、卸裝回背包／恢復基礎外觀、重新穿戴及重登保存通過。這是目前診斷Client與開發Server環境的使用者實測，不擴張為未修改原件驗收。回覆未提供確切卸裝滑鼠手勢，也未另確認特殊衣服攻擊動畫、滿包拒絕或所有裝備槽；這些仍依既有證據界線處理。

完整.NET／SQLite回歸 **479項通過**；新增C3A／C1F形狀、原生Host點選不斷線、卸裝回背包、重送空槽、滿包／未支援裝備組保持連線、髮色／面向／重登保存，以及卸裝Store owner／lease／CAS／死亡／receipt測例。Store該類11項通過包含在完整總數，不能相加成另一個總數。

獨立戰士開發場景的實際HTTP／TCP通過C3A→C1F→S38／S0F／S33、重新穿戴、空槽重送、守護組拒絕及重登保存；這是模擬peer，**原生Client的點擊手勢、卸裝畫面及攻擊呈現仍待使用者實測**。無需重建帳號／角色／金鑰，下一次啟動新版測試Server載入修正即可。
