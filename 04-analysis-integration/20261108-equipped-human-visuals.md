# 武器、盾牌與頭部裝備的角色外觀

使用者要求完整裝備與角色外觀功能。本輪將十六槽裝備的持久狀態接到原生 Human 外觀封包。**欄位、素材查找及持械分支來自原件靜態分析；訓練商品選用的模型、衣裝相容政策是 Server 重建設計。原生畫面尚待測試。** 原始 EXE／DAT 不變。

## 原件證據與查找路徑

Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，REA／Ghidra12.1.4。

S05 reader `0x5895a0` 依序讀取附件 A／RGB、附件 B／RGB。S33 handler `0x4f31a0` 把對應欄位放進 40-byte HumanInfo 的 +0x13／+0x14，顏色放 +0x15／+0x19。`0x474f60` 使用 A+5000、B+6000 查找圖像庫；同時依性別以 Hair+3000／Hair+4000 查找頭部圖像。由此把 A、B 分別識別為武器、盾牌，不能拿背包 IconId 直接填入。

`0x4042b1..0x40432d` 的精確指令及相鄰迴圈將武器 library5001..5109 綁定 `Human/w001.dat`..`w109.dat`，盾牌 library6001..6013 綁定 `s001.dat`..`s013.dat`。這是本版註冊範圍；磁碟另有 w110..w241／s014..s025 並不能證明這些編號可直接使用。頭部 normal hair 與 101 起帽子分開註冊；本輪只啟用實際檢查的105，不開放任意 byte。

`0x47a030`／`0x47a1d0` 在任一附件非零且 career!=5 時為初始動作加8。`0x475240` 的站立映射亦由 direction 改成 direction+0x20；其他 Motion 依各分支轉為持械動作。**網路 Motion、YPF action index、物理 frame index 是不同編號。** 頭部105取代 Hair 查找，不是額外第三個附件，也不覆寫創角髮型資料。

關鍵 Evidence：

- `ev_ad226bd09a97f90b907aaeb6b0529b6f1af2e8e9fdd8adef03570aae77e75eb4`：S05 reader、S33 handler。
- `ev_346252b94edf0ff508277f25eaaa9d95b0309dc32a114cf3ebf80146bc4faec6`：圖像工廠與更新、持械初始動作分支。
- `ev_d25ea38688e8d2369ac62cb17c00988c78624a6c03d61998f16114709f6517c4`：Human 圖像庫／頭部／附件查找。
- `ev_959dd076866fe1ea2256cd58d3bd2072a5c362887845258600d01cad35b2d906`：Motion 到 action 的依外觀分支。
- `ev_a0ad2006919e87e021914184a4020c43a75702276c0798c6cb10a13ddb6e96c9`、`ev_c5861acf1e863afc600f064f4b0f3fe8377474657b73c43f7237fac262c0eb6e`：註冊迴圈原件 bytes；`ev_82fdff8ea36f6208aef7414bd6d3f23def05ed1ffb518073afed67509fe701f4`／`ev_423ff7eb8f9772404c6a96d67b7c3b9cc004d594c46317d9fcff4156b79f8bc6`：武器 library 起點及傳入參數的精確指令。

有些 Human 方法未被工具建立為 procedure，反編譯失敗；沿精確指令追到可反編譯的圖像庫方法，未修改原件或猜造函式邊界。以上為靜態觀察，沒有聲稱監測到遊戲實際繪製。


選定附件素材的完整檔案SHA256（未散布素材本體）：

|檔案|SHA256|
|---|---|
|w001.dat|`bef5ff1e9a01fe19025947ef06625e7dcdef5a060aedd96c7463ec9d59f84bdd`|
|w024.dat|`4d7c564011af4a871ed8f0988fbed7e09b34b61b32428df453f7ea7b28503e99`|
|s001.dat|`8b3cfe2fd09e9b2b2d16feb5dd4664ff13c9ee203035ce4d8d6664c5b3fceb72`|
|mh105.dat|`494f46fb5ed9d2ae5533362cf331b2f646cf3e6882aed0ad7ee4e7e014fe15bb`|
|wh105.dat|`596654434e3e2e0abe7e582f33b92f7e386f4dbc0a20cca607d4328344195682`|

## 封包契約

沿用 [appearance](appearance.md) 的長度、名字及旗標規則；未列欄位保持既有契約。

|語意|S05 body offset|S33 body offset|型別／目前政策|
|---|---:|---:|---|
|頭髮或頭部圖像|9|14|u8；原髮型或已核頭部105|
|頭部／頭髮 RGB|10..12|15..17|保留創角 RGB；帽子染色效果待原生驗收|
|武器模型|13|18|u8，0無；wire 上限109|
|武器 RGB|14..16|19..21|目前 FFFFFF，未開放個別武器染色|
|盾牌模型|17|22|u8，0無；wire 上限13|
|盾牌 RGB|18..20|23..25|目前 FFFFFF，未開放個別盾牌染色|

S05 用於登入初始身份。在線變更只能使用既有 S33 更新路徑，保留 world XY、面向、職業、衣裝、衣色、名稱；不能用 S05 重建自身物件。非法模型在序列化前拒絕。附件為0的舊呼叫仍輸出相同 bytes。

## 可獨立實作的 Server 政策

顯示綁定 revision `development-equipped-visuals-v1` 與 durable item 定義分離。只有 **ID、definition revision、實際 Equipped 槽位** 全部匹配才套用；不能依名稱、IconId 或 Client 自報值綁定。保留現行 v4 catalog、所有 item revision、instance、背包、銀行及收據，不以增加外觀為由改寫既有物品 JSON 或重發裝備。

|物品 ID（均以 development. 開頭）|definition revision|槽|選定模型|
|---|---|---:|---|
|training-sword|development-gear-item-v1|1|武器1，w001|
|training-staff|development-gear-item-v1|1|武器24，w024|
|training-shield|development-gear-item-v1|3|盾牌1，s001|
|training-helmet|development-gear-item-v1|4|Hair105，男 mh105、女 wh105|

這些為測試商品的重建配圖，未證明原服 template 關係。檔內 CP949 名稱將 w001 標為木劍、w024 標為木杖、s001 標為圓盾；對應名稱只能輔助挑選，不能當成原服數值／裝備需求證據。頭部105為本輪男女各自素材候選，完整畫面待測。

原件檔案 SHA256 與各檔首個 YPF object 的 action 表需核對；本輪檢查 w001、w024、s001、mh105、wh105 及男女 body000..002，共11個檔。body 使用 archive member1，附件使用 member0。泳裝／禮服 body1、2 的持械站立32..39等動作為空；因此這兩種衣裝下投影武器=盾牌=0，頭部仍保留。career5 沿用無武器／盾牌顯示的重建相容政策。**這只抑制顯示，不卸裝、不丟道具、不移除加成、不改永久能力。** 原版泳裝能否攻擊、職業武器限制及全部 action 相容性仍未恢復。

投影以交易後的權威裝備讀取。衣裝或有效武器／盾牌／頭部改變才發自身 S33，耳環等無模型變化不重建角色；衣裝切回 body0 時自動恢復仍穿戴的武器／盾牌。卸頭盔取原始創角 Hair，不能把105保存回角色髮型。

其他玩家與自身用同一綁定／相容政策。觀察者在讀取對方位置、World租約、load provenance、衣裝的**同一 SQL statement 快照**讀槽1、3、4的已穿定義，避免把新位置與舊裝備拼接。無 inventory 時只能沿原 wardrobe fallback；有裝備但缺 inventory／定義或槽位不符必須拒絕不一致快照，不偷偷生成裝備。變更同一 remote Human 的 S33 保持穩定 wire reference。

## 驗證與待測

新增13項測例（Domain5、Protocol7、Host1），完整.NET回歸 **1102通過、0失敗／0跳過**。涵蓋封包offset向量與非法編號、精確定義／槽位、衣裝／職業抑制，以及自己與觀察者外觀一致、雙手替換、脫裝恢復原髮型與重登。

隔離真TCP四組通過：原生Merchant購買劍／盾／戒／杖／頭盔共900；C1C／S37／S33驗武器1、盾1、頭部105及雙手杖24，並核能力與原instance；C1F卸裝及銀行存取；出售法杖後餘額250，重登及自有Server重啟後S05／S33仍投影頭部105、位置與資產保存。此TCP為單一合成Client，遠端外觀由Host原格式整合測例覆蓋，沒有冒稱原生雙Client已驗收。

Host SHA256 `5d4bffe2347a6dab41f79a7d0c2604910fd1be94e4b2c7808a90e35aee3b2bb9`，八組件bundle `3339cb4321131ade1b11292564138d11b3a6a831381b2eb56029063ab1bfc7eb`，TCP前後及測試專案重建後一致。三份工作簿僅更新相關進度，無關儲存格變更0；未把舊裝備成功回報改成新外觀已驗收。

原生集中待測：原角色到鐵匠買劍／盾／雙手杖／頭盔→穿劍盾→走動／轉向／普攻→換杖→穿泳裝與脫衣→卸頭盔→重登；用第二個 Client 觀察同樣外觀。特別檢查持械走動各方向、帽子染色／層序、技能與攻擊動作。自訂模板綁定、全部武器／帽子範圍、持械攻擊音效及原服 template 仍待後續分析。
