# 原生持續效果：圖示、倒數與移除

本輪延續A-010-D03，以同版原始Client靜態證據補齊持續效果閉環。原件SHA256：`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；Ghidra12.1.4。本輪未修改原件、未操作遊戲或Server；原生GUI尚待測。

## 已可實作的封包契約

所有欄位是解密後body，不含framing。整數大端，string8前綴是CP950編碼byte數；原生name本地緩衝不是wire UTF16。

|opcode|body|意義|
|---|---|---|
|S2C 0x2C|BEu32 identity, u8 iconFamily, BEu16 iconFrame, u8 opaqueA, string8 name, u8 opaqueB, BEu32 remainingSeconds, BEu32 totalSeconds|新增持續效果；18+N bytes|
|S2D 0x2D|BEu32 identity|移除同identity持續效果；4 bytes|

Reader57A980/585DB0仍是原A010已證格式。新增證據49C050 dispatcher直接比較opcode2C/2D，分別tail-jump49BAE0/49BCD0；不能只用RTTI名稱推接收者。

49BAE0從完整packet+24取identity，+28取iconFamily、+2A取iconFrame、+2C opaqueA、+2E name、+22E opaqueB、+230 remainingSeconds、+234 totalSeconds。這與reader子view起點相差12；這些是本地offset，不是wire offset。

**尾兩u32是剩餘秒數及總秒數，不是stack或UTC timestamp。** Handler各乘1000，存入持續效果本地結構的64bit毫秒欄位；tooltip49A00將剩餘/總時長各除1000，格式化4994A0為時／分／秒。opaqueA、opaqueB本輪僅證拷貝保存，未證buff層數或職業等用途。

## identity、刷新與顯示容量

49D340以第一u32為map鍵，發現相同identity已存在直接return0；49BAE0不更新原有內容。因此重送同identity不會刷新倒數或替換名稱，不能把重送當作refresh。

49BCD0→49D530依相同identity移除inventory，清對應圖示、閃爍集合及當前tooltip。重建Server若要刷新，先S2D再S2C，並由權威效果ledger一次更新數值與expiresAt，不能只動圖示。不同identity可同時顯示，不代表Client會自動計算數值疊加。

49B080掃0..23尋找空顯示格，49BE90建立24個控制項。效果id0在圖示查詢中被當空值處理，Server應分配非0 identity；同時投影最多24個是重建安全界線。超量狀態不能假稱全部可見。

## Client倒數不等同Server到期

49B500是timer callback（缺Ghidra procedure boundary，使用精確指令保存，未修函式或原件）：

- timer1每1000ms遍歷非閃爍圖示，49CB20將剩餘本地毫秒扣1000；49CBB0讀取剩餘時間。
- 剩餘≤10秒便加入閃爍集合。timer0每500ms在圖示frame10與31間切換遮罩呈現。
- 下一次timer1會跳過已在閃爍集合的項目，因此不是持續遞減至0後自動刪除的流程。
- 本輪完整callback指令未見建立／送出C2S，也未見自然到0呼叫49D530。**Server應按權威期限主動S2D**，不能等Client自刪或到期回報。
- 這是相對秒數，無timeGetTime/UTC換算；UI timer受本地執行排程影響，不得作Server權威時計。

Handler以32bit乘法形成秒×1000後再存64bit，避免超大秒值溢位。建議短期測試30秒、0<remaining≤total且total≤4294967；若total≤10即進閃爍分支，不能用進度比例呈現驗證長時效果。這些值域與測試時長是重建安全政策，不是原服公式。

## 合法圖示素材與tooltip

49B3E0/4990A0將iconFamily0映射library2/member5，family1映射library2/member6，並以iconFrame作**單object內的physical frame**。它不是EffectSelector、SpellID或item icon的0x8000編碼。

|family|Icon.dat member|SHA256|合法physical frames|
|---|---|---|---|
|0|slot5 skill.ypf，offset7241725，625904bytes|b320a8b61258a464216a75b0e5fa58560a5abff0f17c2d7227cf66d8991ddc58|0..318|
|1|slot6 spell.ypf，offset7867629，721998bytes|20fbe76bfe39fb1070dee22bb5994227767aeab71a4b420839e75a4b6be83dac|0..370|

Icon.dat SHA256：`b80cfdd28b4331bf4012210756bf46196c37d43de1240d70df3cb6480e920dee`。兩member均YPF v17、31×31、direct RGB565、1object；metadata完整解析分別恰好止於dataBase7936/8936，channel皆做bounds檢查。兩者frame1均非空31×31，可作重建通用圖示候選；**未證它對應哪個原版buff**。frame0在tooltip constructor走不畫icon分支，故最小候選使用1。

49BAE0先按spell庫frame數檢查iconFrame，超界fallback65；family0較小，不能因此認為0..370都安全可送給skill庫。Server應按family獨立驗證，僅接受0/1，不依賴Client fallback。

滑鼠訊息49B2F0查顯示格與identity，49CAA0複製效果內容，再499A00建LastingSpellEstimateDialog。name在4990A0送StaticText，時長由Client生成含換行格式；此閉環沒有呼叫GetStringFromMetaData或HelpString。不要把數字stack硬塞name後再聲稱原生層數功能。tooltip原生實機安全仍須由使用者確認。

## 最小重建buff與待測項

最小可玩實作：施放後Server原子保存buff（角色、技能來源、非0展示identity、開始/期限、實際屬性修正），以S08投影變動能力，再S2C(family1,frame1,opaque0,remaining30,total30)。重新施放同buff時S2D→S2C。到期／死亡清除／登出切換由Server政策決定，移除屬性修正並S08、S2D。該技能數值、30秒與同類不可疊加均須標重建政策，不能稱原服已還原。

重登時以Server期限重算remaining秒數並重新S2C；資料庫中的絕對期限不能原值塞進wire。過期不再投影。原生capacity與移除完整性需測：圖示出現、移入tooltip、倒數、最後10秒閃爍、期限消失、刷新只剩一個圖示、重登剩餘時間、屬性實際生效及移除還原。TCP body解析或Server ledger測試均不能替代這些GUI驗收。

原始raw與snapshot保留workspace/anal-roy-temp/lasting-effects-native-20261108；公開JSON列精選Evidence IDs，不發布原EXE/DAT、完整偽碼或私有Server。
