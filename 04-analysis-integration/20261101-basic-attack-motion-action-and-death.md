# 普攻動作、初始技能項目與原生死亡投影

接續[數字／摩斯追查](20261101-damage-number-mos-and-action-list.md)。本輪只改Server、
測試與規格，不修改原始或診斷Client EXE。尚待diagnostic-copy集中GUI驗證。

## 正面原件證據：Motion1不是本套角色的攻擊

原件SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。
[REA靜態證據](native-basic-attack-motion-and-corpse-20261101.json) 與
[實際資源action子集](base-human-and-mos-actions-20261101.json) 必須一起閱讀。

`0x475240` 將Human motion依HumanInfo／方向映射到YPF action：在本套無武器
基礎衣服，Motion1→direction+8、Motion2→direction+16、Motion4→direction+24。
武器等條件存在時另走+40／+48／+56。它們是action ID，不是physical frame ID。

沿原件YPF17 reader `0x56ea20` 補讀第一object的frame及action表；
`0x567fb0／0x568000` 證實action內存的是frame序列與時間值。兩性基礎衣服
`Human/mb000.dat`、`Human/wb000.dat` 都有730個action slot：

|Human action範圍|各方向內容|意義與證據界線|
|---|---|---|
|8..15|空|舊Server Motion1實際選不到影格，正面解釋不出拳|
|16..23|4影格，raw時間合計400|本地影格目視為移動；不能改成Motion2假裝攻擊|
|24..31|8影格，raw時間合計850|本地影格目視為出拳，Server改用Motion4|
|56..63|6影格，raw時間合計670|另一姿態的動作；不外推所有武器／服裝|

本輪解碼工具只讀第一object的frame/action，未完整解state／transition及後續object；
Ghidra decompiler的假no-return使loop顯示不完整，不能把偽碼中第一筆當成只有一筆。
工具保留欄位raw值，圖像contact sheet只在本地；表中的目視分類是分析者判讀，
不是從原服封包取得的動作enum標籤。目前Server自身外觀固定基礎衣服，後續更衣
要重新核對其action，不可把本次延遲常數當所有裝備的通用規則。

## S5F確實建立CorpseObject

本輪追完 `MapPane 0x4ba310→0x43df20`：前者複製Monster descriptor與方向，
後者帶原件 `corpseobject.cpp` 來源，建立獨立屍體物件並以direction+0x40、
100%參數啟動動畫，之後原living object被移除。摩斯action64..71的8影格，
raw時間合計10820，與本地死亡影格吻合。這補足此前「只證移除」的限制：
**S5F不是單純把目標刪掉，也不應再疊加猜測的S1A死亡動作。**

S13的數字效果可能等待來源動作事件；立即S5F會先移除承接效果的living target。
Server因此先送S11、Motion4的S13及已提交傷害值，再由每連線投影輪詢延後S5F。
延遲1100ms是**重建呈現政策**，參考本套基礎衣服850的序列與輪詢餘裕，
不是原服網路時序或所有技能的命中時間證據。HP與里程碑在命中時已提交，
延遲期間再攻擊仍被權威HP／冷卻拒絕。

待發死亡以舊wire ref綁定，只投影一次。若先離開視野、切圖、回登入或新life
已重生，取消舊死亡；不可對新ref補送舊S5F。新登入者不重新生成已死living
object或補播不曾看見的屍體。正常重生仍按既有規則發舊S0E、新S07及S1A。
屍體自己的視覺存活由Client處理，不把它算活怪或新生命週期。

## 初始「普攻」：使用者需求與Server重建值

使用者明確提出初始普攻技能、滑鼠與空白鍵可觸發；原版nNewWar01也有兩種
輸入說明。S62 reader／ActionInventory及非cast C0E路徑沿上一輪已證原件。
本輪再由 `0x444b70` 證明技能／法術cell讀ActionEntry+4當physical icon frame，
並繪製+0x20a文字。cell mode1使用library2/member5，對應實際 `Icon.dat/skill.ypf`；
其第18影格目視為拳頭。S62的第二段文字存入+0x20a，也正是非cast入口複製到
C0E kind2的文字。`0x575070` writer是u8 kind加CP950 string8。

當前重建項目（**不是找回的原服技能ID／數值**）：

|欄位|值／政策|
|---|---|
|S62 kind／slot／icon|1／1／18|
|三個前置byte|5／0／0；首byte為原生非指定目標使用模式，後續回報修正|
|四段string8|普攻、普攻、基礎近身攻擊、空字串|
|末尾u8／u16／u8|0／0／0，CastValue0，走已證非C4D入口|
|授予|有權威角色且C35載入成功、啟用教學戰鬥的Development profile|
|重登／切圖|重新投影同一固定項目，不依賴一次性創角socket|

啟動時核對Icon.dat長度8589627及已知SHA
`b80cfdd28b4331bf4012210756bf46196c37d43de1240d70df3cb6480e920dee`。
這是本階段固有能力規則，不是已完成全部技能表、升級／熟練度或學習持久化。

技能項目使用C0E kind2、文字「普攻」；Server只匹配自己已發項目，沒有命令
解譯器。選取目標必須是本連線已知、存活、同訓練圖且在視野內的怪；C44選取
超過3秒的目標不當新操作權限。C0E與原生C13都交給同一套距離／冷卻／HP交易，
不能用換入口重複扣血。其他聊天／action文字在本試驗無遊戲副作用；壞封包拒絕。
載圖期間的舊C0E按既有64次budget解析丟棄，不能攜帶舊目標到新地圖。

後續[預設空白鍵補證](20261101-default-space-attack.md)已查到原件Attack鍵表與
action2面前一格選取。上段3秒期限僅是重建技能項目C0E政策，不是原生空白鍵
C13的期限；原生空白鍵也不以滑鼠游標位置或已發S62清單選取目標。

## 驗證與驗收邊界

358項.NET測試通過：含S62獨立byte vector、CP950 encoded-byte長度、截斷／尾隨
拒絕、無選取／未知action／過期選取不扣血、C0E與C13共用冷卻、2／1傷害、
1100ms前不送S5F、只投影一次、快速重生取消舊死亡，以及五職業目的圖再發技能。
4項新YPF索引測試、8項設定升級測試通過。真素材五職業TCP路線亦通過，
包含C02/C04創角、初始S62、C44→C0E及C13命中、Motion4、延後S5F、死亡重生、
學校與目的城鎮重登、職業／位置與逐socket ordinal。

上述是Server／靜態資源／TCP證據，**GUI出拳、數字、技能視窗及死亡動作尚待
使用者集中確認**。診斷副本成功不外推未修改原件CT；候選地圖／城鎮身份與
歷史HELP的版本差異仍按既有地理工作追查。

後續[快捷列／空揮／音效實機回報](20261102-client-feedback-guardian-shortcut-audio.md)
修正原首byte0造成快捷列無執行分支的缺口，並接入已核對的命中／死亡聲音。
上述358項屬本篇原輪基線，後續368項與待GUI項目分開記錄。
