# 除主程式外，Web AI需要哪些檔案？

初輪直接讀本庫的jobs工作頁即可：任務、既有分析、精選原件偽碼／xref及
必要資源索引已附在Git。**不必先上傳Asgard.exe或整套素材**。原始二進位及
完整匯出仍留本地；Web AI若需要進一步資料，應指出精確函式／member，再由
本地補成可審查的分析摘錄。它不能憑GitHub連結存取使用者的E槽。

|研究目的|已確認存在的原件／member|初輪提供／後續補件方式|不能超推|
|---|---|---|---|
|技能清單／圖示／快捷列|Icon.dat內skill.ypf、spell.ypf|本庫resource-index.json有整庫及member SHA／offset／長度；追出UI selector後補指定圖示的結構／預覽與引用|圖示存在不等於技能ID、已學列表、MP/CD表|
|UI文字／共用元件|Basic.dat內BasicString.txt、ProtectorSkill.ypf|僅為實際存在的候選，先追loader／selector再補該member文字或結構|檔名帶Skill不證它是完整技能定義或學習規則|
|新手攻擊／技能講義|Script/nNewWar01.dat，及已盤點nNewLife01/nNewJob01/nNewTeleport01|本庫提供函式名、SHA及整理後流程；需要時只補相關函式摘錄|操作說明不是擊殺objective；Dispose不是畢業|
|怪物生成／攻擊／受擊|Monster00.dat..42及對應World資源|先由S07 image／library／slot定位，再補具體member與動作索引；不要求全部Monster庫|素材與動畫不等於原服HP、AI或掉落表|
|技能畫面效果|Effect0.dat..4|先追實際檔案selector／effect參照，再給指定member索引／結構／預覽|視覺效果不等於權威傷害、BUFF強度或範圍|
|技能聲音|Sound0.dat..2及SOUND資料夾|只在聲音播放路徑研究時補真正引用到的成員|不是施法協定、技能清單或耗魔研究的必需前置|
|技能／NPC觸發切圖|Map0.dat..2及其已核對MAP metadata|沿本庫494張MAP的SHA／尺寸／C35目錄，必要時只補指定圖的欄位／出生點證據|同地圖素材不證職業／教學角色綁定|

本地根目錄盤點沒有看到獨立Skill／Spell命名檔；這只是檔案盤點，不證明
技能定義必定不在Client。不能創造Skill.dat或Spell.dat要求使用者補檔。

## 最有價值的補充，常常不是另一個DAT

如果問題是C56何時送出、S52狀態、BUFF identity或計時，需要的是具體
producer／factory註冊／handler／member讀寫的偽碼、指令和xref。若靜態仍無法
定案，再提供去敏後的操作→opcode→Client callback／UI變化摘要。原始log、
封包錄製、帳密、DB與私有Server不放在公開spec。

MP／SP成本、冷卻、命中／傷害、掉落與任務獎勵若僅在原服，提供更多Client
圖片也無法恢復。此時Web結果應明寫Server-only unknown，另提復原版設計，
不能拿tooltip或圖示索引當正式Server規則。
