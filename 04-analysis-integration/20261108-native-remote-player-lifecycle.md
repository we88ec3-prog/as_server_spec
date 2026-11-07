# 原生遠端玩家：生成、移動、外觀與移除（2026-11-08）

## 來源與範圍

原件 Asgard.exe SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；Ghidra 12.1.4，唯讀分析。這是 A-004／A-011 的增量，重點修正「S06可直接啟動遠端玩家走路」的舊推測。沒有修改原件，也沒有啟動或附掛使用者遊戲。**本頁為靜態可實作契約，完整多人GUI仍待測。**

封包body不含opcode／framing。AOI大小、座標串流頻率、角色lease、穩定ref配置與反作弊，均為Server重建政策，不由Client推得。

## S33可建立真正的遠端Human

S33 reader585570沿用[appearance profile](appearance.md)：BEu16 x/y、u8 facing、BEu32 ref，後接sex、career、clothing、hair、各RGB與flags及name。flags0子集長度為42+CP950名稱byte數。衣色RGB在body30..32始終存在，不需另設HumanFlags。

4F31A0實際以packet.ref對比本地self ref：
- 非self先4BA090(ref)移除舊物件，再47C1D0建立HumanObject，最後4B6450加入MapPane。
- self分支更新既有UserObject：47AB70換profile、設定facing／位置、刷新StatusDialog。
- 因而合法非self ref可以生成遠端角色，並非僅可更新自身外觀。性別、職業、衣髮與染色走同HumanInfo／HumanImage路徑。
- 重送同一remote ref會**刪除後重建**，不是原地更新；可能重置動畫、路徑與附屬呈現。Server應只在首次出現、外觀變動或需重同步時使用，不以每個tick重送S33代替移動。

每個接收者的self view保留ref1，遠端ref不得碰撞self／NPC／怪物／地面物件。原件S05透過UserObject constructor556E30設DAT_0066D0D4等本地自身全域狀態，不能拿S05生成遠端玩家。

### 服裝與flags限制

flags0下沿用已審衣色sentinel／RGB規則。S05的控制旗標不能原封不動視為S33 HumanFlags：47ACE0若見HumanFlags0x1000，僅允許motion0／1／2／0x52，會拒絕attack4及death3等。0x800另有變身服裝範圍檢查，不在本輪普通Human子集。未知非零旗標不得隨意填入。

## 遠端移動必須建立路徑

### S06是既有路徑的確認，不是起步包

S06 body精確為 `ref:BEu32, x:BEu16, y:BEu16`，reader5832D0。dispatch4F16E0找物件、排除本地self後呼叫47A2F0。後者掃已存在的Human路徑節點，找packet XY、標記已確認節點，再處理等候狀態；**不建立路徑、不在空path時直接步行或teleport**。舊A-004由類別名推得的「遠端移動事件」需以此補證限定。

### S64的可實作格式

`ref:BEu32, startX:BEu16, startY:BEu16, headerHeading:u8, count:u8, path[count]:u8, endX:BEu16, endY:BEu16, endHeading:u8`

5835E0 reader →4F1750 registry／排除self →47C9C0 Human path builder →Human virtual+40的47C2D0起步。此virtual明確從下一個路徑節點計算direction、啟動動畫與位移插值。

每個path byte為 `direction<<4 | runCount`：
- 高nibble傳給4430C0 direction-to-delta；使用已審0..7。
- 低nibble代表1..15格；builder先做runCount-1次，再無條件走一步。低nibble0不是空段，Server應拒絕。
- 每run最終節點帶confirmed標記，中間節點為未確認；整段最後節點另有終端標記。不需先發S06才能建立路徑。
- reader的本地path區域為serializer+23..2D，後面+2E／+30是固定終點欄位。本輪**Server安全子集最多11個壓縮run byte**；這是避免覆蓋固定欄位的界線，不宣稱原服最大總步數是11。
- 最小一格count1、path=(direction<<4)|1，end必須等於start+該direction delta。body為16bytes。

正常start!=end路徑中，方向由實際節點推導，不靠兩個heading欄位。headerHeading僅在start==end的校正分支用來設定面向；endHeading在終點等於本機目前座標的校正分支用。Server可一致填首段／末段direction，但這是可審子集選擇，不把尚未完整還原的兩欄硬命名為原服首／末步語意。

### 必須處理的路徑界線

- start!=end卻count0，builder仍會取最後節點，不能發送。
- start==end直接走校正／清path分支，非空閉環也不按runs播放。完整繞一圈回原點不能壓成一包；須分成終點不同的合法路段，或明示採重同步呈現。
- end必須與每個run展開結果一致；不能任意把起終點連成直線，冒稱還原已走的權威路線。
- Server若暫存多筆權威步伐，可從接收者已知pose尋找連續原始steps後壓縮同方向run；缺段、過量或不可安全分段才S33 rebase。這是重建串流政策。
- S0C雖也會對Human呼叫virtual+40，但Human的47C2D0讀既有path。Monster的一格起步語意不能直接移植成「空path Human的S0C一步」。本輪遠端Human使用S64。

## 轉向、移除與離開視野

S11 body為 `ref:BEu32, direction:u8`。4F15E0→4B7F70找物件、對遠端呼叫virtual+3C設定方向；self另受本地移動狀態保護。未知ref可走C0C缺物件重同步。

S0E body為 `ref:BEu32`。既有handler4F1DA0→4BA0C0→4B9CE0執行移除；4B9CE0不銷毀本地自身UserObject，遠端則解綁／移除registry並釋放。可用於離開視野、離線或換圖，但Server應只移除接收者已知物件。再次可見重新S33，不依賴舊動畫／path。

## 攻擊、特效、死亡與復活投影

- S13既有combat body可引用remote Human作來源／目標。4F1DC0先分別查兩端registry，Human實際執行與數字／特效亦引用物件；先投影所需actor再發戰鬥事件。不可用self1假冒其他玩家。
- 命中數字的觀察者分支與Client顯示option有額外條件；不能僅以wire相同宣告每個旁觀者都會顯示同一數字。權威HP仍由Server維護。
- S1A body為 `ref:BEu32, motion:u8, animationParameter:BEu16, tail:u8`。4F1C60對找到的Human走virtual+44→47ACE0→475240；motion3在普通Human flags0子集映射direction+64（墓碑素材），不是只有self可用。
- 旁觀者可在remote S33之後再S1A motion3呈現已死亡者；活著者可S1A motion0。HP0、復活時機／位置與權限是Server政策；動畫包不替代資料交易。
- S05只能建立本地self。遠端復活／外觀重建可用S33＋S1A0，保持該接收者的remote ref映射；原版完整復活業務仍未還原。
- 不把只證Monster用途的S5F當刪除／復活Human指令。

## 精選原件證據

- `ev_ccd4f1da50bfc3836d862897d296206d2af984c788e000813c41db6ccd93939c`：4F31A0 self／remote分支與585570 reader。
- `ev_fa057509d446517238e1b2a40ba8d6bb5670712820674b02868c9d1e5e85d291`：47C1D0 Human constructor、5832D0 S06 reader。
- `ev_53132371d1c6d10c6955a94ee6f9a51de314ee26835bc63916e25f4609eab0bc`：47A2F0既有節點確認、4B7F70轉向。
- `ev_f8ebc969e8af720ced6f87c73dbacd2f4feb4be5f77a83dec7597acc1e1e491d`：47C9C0路徑builder與各校正分支。
- `ev_ee44bb22353e646e180c6e2d2d7304189b3f4345347adb80281b92040e780a39`：5835E0 reader、47C2D0 Human步行executor。
- `ev_fd32db4da92dc8f1ad95d1cadad69c0eadef030828cc3eea248358aaa0beb347`：47ACE0動作gate、556E30自身全域建立。
- `ev_84984a1a327bb910b4469af4d68655f61a2fd5ec8018164a2c45febef2d4c317`：移除與戰鬥數字分支。

完整Evidence與快照留在分析暫存。公開契約不包含私有Server實作、原EXE或完整偽碼。
