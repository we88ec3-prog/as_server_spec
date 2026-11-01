# 普攻傷害數字、摩斯投影與技能清單入口

接續[使用者回報與待修項](20261101-tutorial-visibility-and-basic-attack-followup.md)。
原件SHA仍為 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
[本輪原件靜態證據](native-damage-number-and-action-list-20261101.json)
只含經挑選的Client分析，不含Server實作、執行日誌或素材。

## S13傷害數字的正面證據

S13固定欄位14B後必須讀tail u8，未擴充總長15B；flags bit0追加16B，擴充總長31B
（2026-11-02依0x57de90未擴充分支更正）。不能把傷害量塞入基礎effect selector。
原件 `0x4a4b00` 依flags bit0，將完整packet+0x4c傳給 `0x4b6850`；
後者選擇數字樣式並建立 `0x474390` 的HitNumber候選物件。逐指令確認
`0x474435..0x474444` 讀取第三個stack參數、保存於物件+0x2c，送入
`0x473790` 計算十進位位數；`0x4736d0` 拆個位／十位等，`0x4739c0`
逐位繪製。這比只依SDamageEffect類名猜傷害量更強。

|含義|wire offset|完整packet欄|限制|
|---|---|---|---|
|數字值|22..25，BE u32|+0x4c|只證Client顯示值，不是Client權威HP|
|接收者動作候選|14，u8|+0x42|本輪仍設0，不猜受擊／死亡列舉|
|接收者效果候選|15..16，BE u16|+0x44|本輪設0|
|接收者動畫參數|17..18，BE u16|+0x46|本輪設0|
|額外數字／效果候選|19..20，BE u16|+0x48|本輪設0，語意未全部解開|
|其餘欄位|21、26..30|+0x4a、+0x50及尾欄|仍保留中性欄名，本輪設0|

Server先提交命中交易，再按**實際扣除HP**投影31B S13：例如HP3、傷害2，
兩擊顯示值依序為2、1；拒絕／冷卻不產生數字包。設計支援正整數1..999999，
對應已確認的六位十進位繪製子集；不是宣稱原服數值上限。
其餘擴充欄位保持0，不偽造暴擊／命中率／目前HP。

S13仍會走來源／接收者的動畫及效果佇列。現用來源Motion=1及立即S5F死亡
尚未完成動畫對照，因此**本輪只證明下發正確數字值，尚未證明GUI已看見數字**。
不要把此項當成使用者回報已全面修復，也不將S5F移除誤稱為完整死亡動畫。

## 摩斯素材與獨立外觀設定

前一輪已列 `Monster00.dat` 與 `M_00_0_모스.ypf` 的hash／offset。
本輪以既有有界YPF解碼器解出第一group的多個physical frames，目視有翅膀與
長口器的昆蟲外型，符合使用者線索；「摩斯」中文名稱沿用使用者提供的名稱。
物理frame16不是native Motion16，不能混用索引空間。圖像及接觸表只保留本地。

既有A-011的MonsterImageLib映射為：image0x4000→library8000→Monster00、slot0。
Server新增可選的 `TrainingCombat.PresentationImageId=16384`，只接受此項已核對
素材；載入前核對archive長度4431969、整檔SHA及offset220/length556599的member SHA。
未指定時保持舊投影，未知image／素材不符拒絕啟動；不修改DAT或EXE。

**設計分離**：這個設定只改S07 appearance與顯示名稱，不能改共享HP、life ref、
戰鬥policy revision、練習里程碑或NPC位置。原有持久戰鬥契約維持，否則僅換圖像
就會觸發shared-content衝突並使既有角色無法繼續教學。此處不是用新政策覆蓋舊DB。

generated完整路線profile升級v2→v3只加上述外觀設定及profile版本；先備份，
只處理完整符合舊generated模板的檔案，自訂內容不覆寫。DB／金鑰／帳號不寫入。
既有v1先做原來的camera-only升級，再獨立做外觀升級；每步都有自己的備份。
候選地圖與出生座標不因這次升級改變。原版摩斯出現在哪個教學地圖仍unknown。

## 技能清單與滑鼠／空白鍵的分界

原版 `nNewWar01.WarMessage02Proc` 的基本攻擊說明明列滑鼠左鍵及空白鍵，
並將Ctrl+D的魔法／技能視窗與數字快捷鍵另列。這是資源證據，補強使用者回憶；
不能因此推論兩種入口必須先有S62技能項目才會發C13。

原件 `0x497230` 的已解析key-binding action2會找角色面前物件並呼叫
`0x5578d0`；滑鼠路徑也指向此入口。`0x5578d0／0x556f80` 檢查本地狀態及
timer後產生C13，只有target ref，沒有Client傷害量。具體預設按鍵仍需key map
或runtime對照；腳本已證空白鍵說明，不拿action數字2直接當VK_SPACE。

**技能清單不是S08或S0F**：已定位S62 AddAction ctor0x578f70／reader0x579020，
native dispatcher0x4f49db→0x4f2cd0，建立ActionEntry0x4017d0後，kind<2透過
`0x4019b0` 的 `kind*80+slot` 放入ActionInventory。精確decoded body為：

`u8 kind, u8 slot, BEu16 icon, u8×3, string8×4, u8, BEu16, u8`。

所有string8以encoded CP950 byte長度計，不是固定UTF16。entry+0x80e的word
會在0x401ed0被檢查：非0走C4D開始施法；0走另一條action／命令路徑。
因此不能任選一個spell value送「普攻」來宣稱已恢復原生初始技能。
四段文字、flags、圖示ID及普攻entry的具體初值仍待補證；**本次未臆造下發S62**。

## 驗證與尚缺事項

355項.NET回歸通過；8項Python設定升級測試通過。Host整合測試包含2／1傷害
數字、切換摩斯外觀後原死亡狀態／同一policy仍可恢復，以及重生／可視返回。
完整五職業TCP另檢查S13長度、flags、擴充中性欄位、實際數字與逐socket ordinal。
這些皆為Server／TCP驗證，原生GUI仍待集中測試。

後續優先：正確的Human普攻動作與事件佇列→受擊／死亡／移除時序→初始S62
項目及快捷列→集中測滑鼠、空白鍵、NPC出入視野、摩斯與完整畢業路線。
本輪沒有要求使用者重測半完成的攻擊鏈。
