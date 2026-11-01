# 既有分析盤點與本輪深挖界線

本輪直接查閱requests.json、A-009/A-010完整報告、A-008狀態報告、
A-024物件交付、A-025合約、Quest/Skill交叉審查與nNewWar01實際資源。
正式A編號保持32項，不以另開同題A來替代已存在的partial工作。

|A|主表狀態|已證的可交付範圍|不能據此宣稱|
|---|---|---|---|
|A-008|integrated/ready|S08 flags與C47最小請求|原服HP/MP數學公式與技能耗用時序|
|A-009|integrated/partial|C13、S13、S5F與部分Battle變體|可實際連續打怪、傷害數字、死亡／復活都完成|
|A-010|integrated/partial|六種技能／持續效果wire與C4D producer|已學清單、施法完整時序、技能類型、成本／CD、BUFF UI已完成|
|A-024|integrated/ready|非Human物件packet layouts|原服怪物spawn／AI／傷害／死亡動畫全都還原|
|A-025|integrated/partial|教學戰鬥intent與邊界|原版要求殺哪隻怪、殺幾隻及何時畢業|
|A-026|integrated/partial|Born／Script生命週期、完成／出口設計邊界|原服任務規則、獎勵與城鎮出口已找回|

正式Native Client驗收均保持各自not-run／未驗，不以招募員的診斷副本成功
取代技能／戰鬥實測。Server自己的開發與本輪Web分析可並行。

## 發現的文件風險

1. A-009報告保留來源分支CT-063/064，而main主表已是CT-078/079；
   A-010使用main CT-095/096。Web結果不得沿用來源舊號新增同號測試。
2. A-025主表implementation_ready_scope仍有歷史`S1E`死亡敘述，本輪依
   既有原件constructor0x57E1B0／opcode0x5F更正為S5F；不是新發現另一死亡包。
3. 部分主表title/method存在既有亂碼，審查以A ID、具名報告和原件SHA為準；
   不猜亂碼內容，也不藉本次任務重寫無關需求。
4. 先前S07曾發生wire第4／第5byte對照錯誤，已在原件重新定位修正。
   技能深挖同樣必須把wire offset、本地packet欄及actor欄分開，不只codec自我往返。

## 深挖交付的優先級

先普通攻擊與怪物受擊／死亡閉環，讓新手場景真正能操作；技能先確認
「Server如何讓已學技能出現在UI／快捷列」與選取值，再接施法／取消。
目前只有技能開始／效果packet而沒有完整清單入場鏈，無法證明玩家能選到技能。
BUFF identity與計時、各類效果、技能切圖及內容表再依tasks.json追補。

nNewWar01包含基本攻擊與技能操作說明，但沒有在本次所讀函式中送kill完成回覆。
這只能限定這些函式，不足以證明整個教學無擊殺需求。A025-D01必須取得正面
objective/event來源；否則保留unknown，將使用者希望可打怪的玩法需求另列。

## 本地後續補證（不變更既有Web輸入包身份）

S62技能清單／ActionInventory、C0E非cast入口、Human普攻Motion4、S13數字與
S5F原生CorpseObject已有[新增分析](../../04-analysis-integration/20261101-basic-attack-motion-action-and-death.md)。
初始普攻項目已用原生wire的重建值接入；不是找回原服技能ID或完整學習表。
Web任務請先讀此增量，避免重派已完成的入口定位；舊jobs仍保留其baseline／
manifest身份，不能把後續新檔假稱為舊包已reviewed。GUI與原版數值仍待驗證。
