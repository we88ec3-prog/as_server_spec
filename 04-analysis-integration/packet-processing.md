# Client / Server雙向處理矩陣

C2S：Client serializer → wire → Server解碼／狀態驗證 → Domain命令 → 必要回覆。S2C：Server投影 → wire → Client parser → handler → UI／世界狀態。表中client_entry不是Server函式，不要求各Server具有同名方法。

|ID|方向/opcode|名稱|系統|body或分支|Client入口|前置狀態|相關封包|完整度|
|---|---|---|---|---|---|---|---|---|
|PKT-C00|C2S 0x00|Version|SYS-AUTH|u16,u8,u8,u16,u16；欄位語意仍有未知|0x577e80|首次簽章之後|PKT-S00|partial|
|PKT-C02|C2S 0x02|NewUser|SYS-CHAR|台灣profile為4個string8及flag；其他語系分支不可套用|0x5742b0|公告／條款階段|PKT-S02|partial|
|PKT-C03|C2S 0x03|Login|SYS-AUTH|string8 name,string8 password,u8 flag|0x573110|版本／公告完成|PKT-S02,PKT-S03|profile-documented|
|PKT-C04|C2S 0x04|NewUserInfo|SYS-CHAR|u8 sex,u8 hair,RGB3|0x574420|創角草稿成功之後||profile-documented|
|PKT-C10|C2S 0x10|TransferToken|SYS-AUTH|raw opaque token，非string8|runtime-transfer|轉服新連線首包||profile-documented|
|PKT-C11|C2S 0x11|ChangeDir|SYS-MOVE|u8 direction(0..7)|0x571960|已進世界||profile-documented|
|PKT-C1C|C2S 0x1c|UseInventory|SYS-ITEM|u8 kind,u8 slot,u8 flag,u8 use_kind；本profile use_kind5無尾部|0x577800|已進世界且格位有效|PKT-S37,PKT-S33|profile-documented|
|PKT-C1E|C2S 0x1e|Wear|SYS-ITEM|u8 slot；遊戲實測換裝主要走C1C|0x578010|已進世界|PKT-S37,PKT-S33|profile-documented|
|PKT-C25|C2S 0x25|WorldEntryMetadata|SYS-WORLD|原型接受但未完整解讀billing metadata|0x4a8370|token交接完成|PKT-S02,PKT-S05,PKT-S15,PKT-S14|partial|
|PKT-C33|C2S 0x33|Move|SYS-MOVE|u8 direction,u8 sequence7,u8 gait_flags|0x573bf0|已進世界|PKT-S0B|profile-documented|
|PKT-C35|C2S 0x35|MapCRC|SYS-WORLD|BE u16,BE u16；CRC算法／比較策略待補|0x573490|收到S14(1)後|PKT-S04,PKT-S33,PKT-S14|partial|
|PKT-C62|C2S 0x62|FramedSignature|SYS-AUTH|decoded body=aram，ordinal0|0x53c846|binary greeting之後||profile-documented|
|PKT-C75|C2S 0x75|CheckTimeReply|SYS-AUTH|BE u32 challenge,BE u32 client_time|0x571e80|已進世界||profile-documented|
|PKT-S00|S2C 0x00|VersionCheck|SYS-AUTH|result u8後分支；result0: u32,seed u8,key string8,message_count u8|0x589b60|C00後||profile-documented|
|PKT-S02|S2C 0x02|LoginOrCreateResult|SYS-AUTH|u8 status,string8 message；依會話狀態解讀|0x57dbc0|登入／創角／進世界初始化||profile-documented|
|PKT-S03|S2C 0x03|TransferServer|SYS-AUTH|u32 address,u16 port,u8 token_size,raw token；位元序見情境|0x5886c0|登入成功|PKT-C10|partial|
|PKT-S04|S2C 0x04|UserPosition|SYS-WORLD|BE u16 x,y,viewport_x,viewport_y；本profile鏡頭8,9|0x589990|世界／地圖已建立||profile-documented|
|PKT-S05|S2C 0x05|SelfAppearance|SYS-LOOK|外觀與flags；詳細欄位見appearance.md|0x5895a0|登入成功建立世界UI後||profile-documented|
|PKT-S0B|S2C 0x0b|MoveAck|SYS-MOVE|BE u16 x,BE u16 y,u8 sequence；bit7成功、低7bit回送|0x583150|C33之後||profile-documented|
|PKT-S0F|S2C 0x0f|AddInventory|SYS-ITEM|變長物品欄；詳細已知分支見items.md|0x57a3f0|進圖初始化／背包變更||profile-documented|
|PKT-S14|S2C 0x14|MapLoadingControl|SYS-WORLD|u8 control：1請求CRC、2關閉載入；3錯誤分支未納入profile|0x4f2300|地圖載入中|PKT-C35|partial|
|PKT-S15|S2C 0x15|Map|SYS-WORLD|BE u16 map,width,height,u8 flags,u8 field,string8 title|0x57ff30|已有MapPane與自身玩家||profile-documented|
|PKT-S19|S2C 0x19|PlaySound|SYS-AUDIO|kind1:u8 kind=1,u8 repeat,BE u16 track；repeat0循環、track0停止|0x584ae0|可播放音訊時||profile-documented|
|PKT-S33|S2C 0x33|PutHuman|SYS-LOOK|玩家座標、面向、外觀及名稱；見appearance.md|0x585570|玩家與地圖已建立||profile-documented|
|PKT-S37|S2C 0x37|AddEquipment|SYS-ITEM|變長裝備欄；見items.md|0x579830|穿戴成功／裝備恢復||profile-documented|
|PKT-S60|S2C 0x60|Stipulation|SYS-AUTH|u8 type,u16 compressed_size,zlib CP950 NUL文字|0x587190|公告請求後；請求分支尚待逐項納入registry||partial|
|PKT-S66|S2C 0x66|CheckTime|SYS-AUTH|BE u32 challenge|0x57dd30|已進世界；5秒為本機政策|PKT-C75|profile-documented|
|PKT-C0F|C2S 0x0f|MetadataRequest|SYS-AUTH|body03；其他request種類待分析|documented profile; exact per-branch entry pending A-020|see profile-login.md|PKT-S18|profile-documented|
|PKT-C4B|C2S 0x4b|StipulationRequest|SYS-AUTH|空body；已取得server list後|documented profile; exact per-branch entry pending A-020|see profile-login.md|PKT-S60|profile-documented|
|PKT-C57|C2S 0x57|ServerListOrSelection|SYS-AUTH|body01請求清單；body0000選本機第一項|documented profile; exact per-branch entry pending A-020|see profile-login.md|PKT-S56,PKT-S60|profile-documented|
|PKT-C6C|C2S 0x6c|ScriptRequest|SYS-AUTH|本profile觀察body03，原型不回覆；正式Script更新策略待分析|documented profile; exact per-branch entry pending A-020|see profile-login.md||partial|
|PKT-S18|S2C 0x18|Metadata|SYS-AUTH|本profile最小body00030000；未還原其他metadata種類|documented profile; exact per-branch entry pending A-020|see profile-login.md||partial|
|PKT-S56|S2C 0x56|ServerList|SYS-AUTH|u16 BE compressed_size + zlib entry bytes；本profile只定義單項|documented profile; exact per-branch entry pending A-020|see profile-login.md||profile-documented|
|PKT-S0A|S2C 0x0a|Message|SYS-AUTH|u8 status,string16 CP950 message；不能用來替代登入S02|documented profile; exact per-branch entry pending A-020|see profile-login.md||profile-documented|

### 收發必要行為

- C03：Server驗證帳密及登入狀態；失敗S02，成功S03。Client轉連線再送C10，不是直接進圖。
- C33：Server裁定步伐後送S0B；成功bit7及低7bit回送使Client解除等待。不能以S06/S64自己的排除分支替代自身確認。其他玩家同步另待A-004。
- C35：Server僅在載入狀態處理；本profile回S04/S33及載入完成，再送S19。CRC真正驗證及失敗回復尚待補。
- C1C use_kind5：驗證格位與使用權，更新裝備並送S37/S33；正式物品數量與脫裝待A-007，不可把測試衣櫃當完整背包。
- S05：Client建立自身UserObject，MapPane必須已可用；S33將可見角色加入地圖或更新外觀。
- S15：Client清理舊圖其他物件、保留本地玩家並載新地圖；S04定位及S14關閉loading。
- S19 kind1：Client依音樂設定播放Music/%05d.mp3；不代表Server已知道官方map曲目。
- S66/C75：Server檢查challenge的對應及期限；client_time語意更深用途待分析，不因單一時差直接認定作弊。

## A-021 原生創角靜態路徑（非實機驗收）

來源：[`A-021 roy1 靜態報告`](../03-analysis-requests/A-021-roy1-static-analysis.md)；Evidence `ev_a021_20261031_asgard_static`；Client SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

| 原生路徑 | Body（已驗證） | 對 Server 的規格影響 | 不得聲稱 |
|---|---|---|---|

詳見 [原生創角靜態矩陣](A-021-native-flow.md)。C02 不能直接等同於已登入後的 CreateCharacter，R-025 禁止 Client 建立 Account。

## roy1 A-021 協定回顧與不信任前認證資料（2026-10-31）

已核對 Asgard.exe 靜態證據：C02 writer 依 region 分支，region 2～4 為四個 length-prefixed string8 + flag，其他為三個 string8；C04 writer 五個 u8；S02 status u8 + string8；CreateInfo UI state 0x1d 收到 status0 時送 C04/轉 0x1e。**C02 有可能在 C03 之前出現**。這並不證明字串欄位包含有效密碼，也不證明某預建帳號已被授權認領。R-025 僅管理員創建 Account 的規範不變；PreAuth C02 只可解析與安全拒絕／等待能被證實的 identity proof（A-027）。C04 的 S02 終局與 World 轉服待 A-028。來源與信任標記詳見 [A-021 review](A-021-roy1-review.md)。

## A-023 Script 通道：解析安全與首次導引的未知

Roy2 BIN-first 確認 Client C6C opcode 0x6C（ctor `0x575140`、serializer `0x575210`，subtype 0..4 分支）；S44 opcode 0x44（ctor `0x5862e0`、type1/subtype3 handler `0x52c8e5→0x5294e0`），其中本機 Script cache 作業**不是無副作用 ACK**，不得送未知合成 S44。另 Born.Main 顯示 PaperDialog 引導玩家去 (31,29) 找女性招募員，但不證首觸發、NPC ID 或 map/spawn。詳見 [A-023 分析](../task_a/roy2/A-023-analysis.md)。CT-033..035 為此分支的教學 Script CT；A-021 原 CT-029..032 不變。

## A-001/A-023 更新後原生協定裁定（2026-10-31）

- A-001：binary AA frame `payload_length:u16_be`，body seed0..9 mask + key/ordinal XOR（例外 opcode 不加 ordinal 依具體 profile）；C00 8-byte，S00 result0/1/2 parser 形態；只有 seed0/local 登入基線，seed1..9 synthetic fixtures 非 runtime。詳見 [A-001](../03-analysis-requests/A-001-roy1-seed-and-version.md)。
- A-023：`S44(1,0)` Script named start，檢查 `name,context,text_crc32,deps,params`，Client 資源足夠則執行 Main；缺檔的 C6C0 → S44(1,1) 更新；Born/PaperDialog 無 SendReply 的 OK Dispose 送 C6C4 再 C6C2。**不代表 quest completion、原服 start 時間或 NPC binding 已確認**。詳細 schema、CRC/CP950 前提及清快取風險見 [A-023 Client 契約](../task_a/roy2/A-023-script-entry-contract.md)。

## A-002 更正 C25 誤標與登入轉服 wire

原版 C03：`string8 account,string8 password,u8 flag`；S02：`u8 status,string8 message`；S03：`u32_be addr,u16_be port,u8 token_len,raw bytes`；C10：**raw token body**、無第二個 u8 length。位址 `0x4A8370` 是 S03 的 transfer handler，不可當 C25 的 region parser。真實 Server 的 duplicate-login status/policy 未知。見 [A-002 靜態核對](A-002-merge-verification.md)。


## A-024 NPC/Monster Client I/O（decoded S2C static subset）

|PKT|原生 ctor → reader|已證 Body|門檻|
|---|---|---|---|
|S07 DrawObjects|0x57E310 → 0x57E3E0|BE u16 count + variant rows；首欄 BE u16,u16,u8,u32,u16；type1..14 分支|0x228 是 **local struct stride**，不是 wire row size；非空變體仍需 BIN 深查|
|S0C MoveObject|0x5833A0 → 0x583450|BE u32,u16,u16,u8,u8|位置/速度語意 unknown|
|S64 MovePath|0x583530 → 0x5835E0|BE u32,u16,u16,u8,u8 count, count*u8, u16,u16,u8|local 路徑 +0x23..+0x2D 只有 11 slots：Server 保守 cap11 是 **designed**, 非原服已證界限|
|S5F DieObjects|0x57E1B0 → 0x57E260|BE u32|原版死亡/HP/掉落分支未知|
|S0E RemoveObjects|0x585E60 → 0x585F10|BE u32|觸發清除時機/範圍未知|

\`C43 CObjectInfoRequest\` 類存在但不能直接認定為 NPC click；A-023 \`Born.dat\` 提及 (31,29) 只是 UI 引導，非出生或 NPC id。原生源頭與原服 AI 規格 unknown，禁止預設 type/category/respawn seconds。Server 應由 authenticated World/instance/epoch 投影、去重、限制未知 type；**這是 designed**。CT-021/022/034 仍 planned。參照 [A-024](../task_a/roy2/A-024-analysis.md)／[synthetic tests](../task_a/roy2/test_a024_npc_codec.py)。

## A-004／roy2：原始 Client 多人視野／移動／移除（2026-10-31）

以原版 `Asgard.exe` SHA256 `db3df616...` 的 RTTI、vtable 與 native reader，確認 **S33 PutHuman** 起首 BE u16 x/y、u8 facing、BE u32 actor 欄，**S06 MoveHumanAck** BE u32,u16,u16，**S11 ChangeDirection** BE u32,u8，**S0E RemoveObjects** BE u32，**S0B MoveAck** BE u16,u16,u8 **不含第三方 actor ID**。C33/C11 是 Client 移動／轉向送出方向；S33（玩家）與 S07（其他圖上物件）的資料路徑不可混淆。

5 種 S2C native opcode constructor + 5 reader sequence 以實際 PE 及 SHA 鎖定 probe 全部 PASS；9 個合成 CP950/欄位長度/選配 flags/epoch/重送測試 PASS，**不是** native 兩 Client E2E。已更新 [A-004 分析報告](../task_a/roy2/A-004-analysis.md)、[機讀 locator](../task_a/roy2/A-004-native-locators.json)、[CT-054/CT-055](../05-conformance/A-004-visibility-test-plan.md)、SCN-005 與 FLOW-VISIBILITY。

目前未追通完整原生 MapPane/ObjectRegistry callback、跨包 u32 ID 的實際 key 查找和 Native UI 的離視野效果。Server 可按 map_instance/epoch/id 做權威可見集合和斷線 fencing（**designed**），但原服 AOI 範圍、重用規則不得聲稱已證。`A-004.status=integrated`, `handoff_status=partial`, `native_client_validation=not-run`。
