# 怪物單步、玩家受擊與死亡／復活投影

2026-11-08。使用者要求繼續完成Server功能。本輪補不可變本版EXE的可交付原生子集；AI索敵、傷害、仇恨、復活時間與恢復比例是Server重建政策，不由封包名推導。原件SHA256沿本版 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。本輪沒有執行Client，GUI驗收另記。

## 怪物→本地玩家受擊

現有31B S13可用來源怪物ref、目標本地玩家ref、Motion4、Effect0、AnimationParameter100、flags bit0及已提交的實際傷害值。`0x4a4b00` 依bit0把數字交 `0x4b6850`，後者明確對 `target==DAT_0066d0d4+0x0c` 建立HitNumber style1；沒有要求來源必為玩家。因此不需捏造另一個怪物傷害opcode。S13只播放效果，權威HP另以S08投影；傷害與死亡必須先由Server提交。

怪物Motion setter `0x4d63e0` 經 `0x4d2520` 映射：Motion0→direction+32、Motion1→direction+40、Motion2→direction+48、Motion3→direction+64、Motion4→direction+56。已審摩斯第一object的40..47為6frame／raw600，56..63為6frame／raw900。因此Motion4可到本套摩斯攻擊序列；不是把Human Motion4的action24套在怪物身上。

## S0C是從起點前進一格，不是終點teleport

S0C body精確為 `BEu32 ref, BEu16 x, BEu16 y, u8 heading, u8 fieldB`，10B。`0x4f1610` handler忽略本地自身，對其他物件先校正到x/y，再設heading，最後呼叫該物件virtual+0x40。

Monster vtable `0x60ac9c+0x40` 指向 `0x4d7390`：保留舊像素位置、播放direction+40移動動作，並將物件格位設為 `(x+dx[heading], y+dy[heading])`。圖像隨動畫從舊像素到新格。**因此Server單步必填舊起點x/y；填新的終點會再多走一格。** direction表仍0北、1東、2南、3西、4東北、5東南、6西南、7西北。

fieldB傳給動畫結束callback `0x4d7330`；其額外分支仍不命名為官方枚舉，本次採0作保守子集。單步完成前不應用零間隔多送起點相同的S0C；步頻、碰撞、斜角與擁擠由Server權威判定。S11只轉向，S04是自身定位，不能代替怪物單步動畫。

S64仍可讀為ref、起點XY、u8 heading候選、u8 pathCount、path bytes、終點XY及尾heading。`0x4f1750→0x47c9c0` 會建立路徑節點，path byte高4bit為direction、低4bit為步數，並處理目前路徑修正；它也不對本地自身套用。本輪最小AI採S0C單步，不宣稱已完整驗S64所有回正／尾欄情境。

## 玩家墓碑：S1A，不發S5F自刪

S1A body為 `BEu32 ref,u8 motion,BEu16 animationParameter,u8 tail`。`0x4f1c60` 明確允許self，當self且motion非0時取消本地pending movement，再呼叫virtual+0x44(motion,animationParameter)。Human mapping `0x475240` 的Motion3為direction+64。

已審兩性base衣服mb000／wb000的action64..71各只有1frame、raw100；本輪離線解碼實看：男性frame240為RIP墓碑，女性frame248為十字架墓碑。因此可用 **S08 HP0＋S1A(selfRef,3,100,0)** 作本輪死亡呈現候選，保留同一玩家實體，Server拒絕移動、技能、攻擊及一般恢復。其他衣服／朝向的墓碑呈現與持續時序仍待GUI；不能因這個候選就宣稱原版幽靈／復活系統完成。

S5F handler `0x4f2bb0→0x4ba310` 的CorpseObject分支針對Monster類型；後續 `0x4b9ce0` 對本地玩家還有特殊保護。這不是玩家死亡／復活的證據，不應把怪物S5F套到self造成清理副作用。

## 重建5秒後同圖復活與自身投影

本輪Server政策是死亡5秒後，在**單一交易原子提交復活HP與同圖spawn pose**，再直接投影S05／S04／S33／S08／S1A Motion0。這個同圖復活不走S15／C35、不改load epoch。5秒不是原服復活時間；普通每分鐘恢復、藥水與技能恢復不能繞過明示復活。

初登入既有已驗順序是S05→S15→S14(1)→C35→S04/S33/S08/S14(2)。曾考慮把同圖復活套進online transfer，再於C35後送S05；**此提案未採用**：同圖相同checksum的C35在wire上無法區分新舊確認，既有WorldLoadingSession契約禁止因此重用載圖流程。不得將該提案描述為已實作復活。

本輪採直接重建self：S05 `0x4f3830` 不檢C35／phase，且明確處理既有self：發解綁事件、移除registry、解構舊self，再建新self。因此不重載地圖而重新下發S05是靜態可行子集；後接S04位置、S33外觀、S08權威資源及S1A Motion0恢復站立，仍須GUI驗收，不借用先前登入／切圖通過紀錄冒稱已驗。

S05會重建自身，不能只用作無副作用的名稱／HP更新；需完整回送當前職業、外觀、朝向／位置、S08、已學技能、背包／裝備及場景投影。死亡期間舊命令與復活交易以角色狀態版本、lease及Server生命週期規則隔離；不因同圖復活創造假載圖epoch。是否保留本地快捷列也須實測，不以原生raw ref作持久生命世代。

## 有界復活Script盤點與未知

原件存在ClericReviv、ClericResurrection、ClericGreatResurrection、SuperUltraResurrection。四者Main建立ServerParam／ClientReply後呼叫YesNoDialog_Create，文字含0／40／50／100%但混有不能strict CP950編碼的字。它們只能證明Client有相關確認介面資源，不能把文字比例當原服權威公式、或當本輪安全可直接啟動的完整閉包。nSuPriest01本版是買魔法類入口且DoesTalk=false，不等於找回復活神官服務。

本輪沒有證明玩家原生自主復活專用C2S opcode、完整同版Script安全依賴及原服復活地點；不存在特定英文RTTI名稱也不證明Client沒有該功能。最小可玩閉環先採明示Server自動復活政策，不造復活按鈕命令。

待集中原生驗收：摩斯走一格而非兩格、步頻與停住、怪物首擊／連擊的玩家傷害數字及HP、致死墓碑、死亡不能操作／恢復、5秒後同圖直接重建self與站立、spawn位置、沒有額外S15／C35載圖交互、復活後技能／藥水／背包及重登。原件靜態與合成TCP測試分列。
