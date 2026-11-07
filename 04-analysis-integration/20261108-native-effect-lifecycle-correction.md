# 原生特效4000循環與4006有限替代

2026-11-08。使用者實測確認：指定目標法術已能命中、資源耗盡會拒絕，但效果掛在怪物身上不消失，多次施放重複堆疊。這是原生畫面回報；下列生命週期為同版不可變 EXE／Effect4.dat 的靜態補證。此前將4000當作最小一次性候選的判斷不成立。

## 循環來自原件runner，不是影格數

Effect04000.eff（slot1，1979 bytes）有兩節點：node0 CreateEffectsAction 引用 image node1；node1 imageKey4000、duration1920，帶權重100%的回指 node0。因此即使其 YPF object0只有12個 physical frames，整個 runner 仍會重排下一輪效果。不能用影格數、有限資源長度或合成TCP成功推論一次性播放。

`0x459bd0` 處理原生 ERra 事件，CreateEffectsAction 經 `+0x60` 取得 image node，再呼叫 `0x459680` 建圖。後者依 image references 的百分比時點排 ERra，回指會再次執行 action。最後的通用 reference 選擇按累積權重決定下一節點；4000的100%回指沒有隨機退出機會。

## 已追通的原生刪除鏈

Human 的 S13 投影入口 `0x47bc20` 在 `0x47bc9a` 清 EBX；`0x47bcf5`／`0x47bd2a` 把零作為 `0x458bc0` 第四參數，存入 runner+0x80。這不是 S13 damage flags1 的原樣傳入；本次一般S13路徑沒有抑制自動刪圖。

`0x459680` 在 runner+0x80為零時，依原件 image node+8 的 duration，在 duration+1 排程原生 **ERke** 事件。`0x459bd0` 的 ERke 分支經 `0x459b60` 移除 runner 圖物件索引，再呼叫 `0x4b9ce0`，執行圖物件移除、圖庫註銷與生命週期釋放。活動圖物件及 queued actions 均為零後，它解綁來源／目標、撤銷排程，經 `0x41b890` 結束 runner；destructor `0x459420` 清剩餘圖物件及資源引用。

所以4000的單次圖片可以刪除，卻又被循環重新產生；Server猜測一個timeout或把S13 flags改零，不能修正資源圖中的回邊。本輪沒有證明一個可單獨取消某次S13 runner的Server封包，不能把S2D lasting移除或物件S0E冒充該功能。舊場景已建立的循環也不會因後續改送另一selector而自動消失，驗收應用新的Client場景；不為清特效刪除怪物權威實體。

## 4006替代候選與可實作範圍

EffectSelector **4006** 經既有原生索引取 Effect4.dat slot7 `Effect04006.eff`，offset11711203、1976 bytes，SHA256 `2729bf0f3b4a5399c4bf7831329bf8126167960ab3824c088d47fce7ed842107`。同樣只有 CreateEffectsAction＋image兩節點，但 imageKey為4002、duration1600、references空。唯一圖路徑0→1，沒有回邊、沒有type7音效節點。原生duration+1刪除條件已滿足，不需要Server另造消失計時器。

對應 `effect04.ypf` object2有10個physical frames、1action、1state、0links；完整52objects metadata掃描恰好到data base35618且所有channel span在member範圍。它是有界原件驗證的**Development通用有限候選**，不能命名為原版火球或證明與任一原版魔法對應。

archive仍使用 Effect4.dat SHA256 `5cac55442e8504786bf9e8b7be73eed2a1cd05a65970739e1fdf24df0f7e58dc`；YPF SHA256 `e5c9d3990b9b40012812eb466ee630da58473db9ff44700d754fd1ed9aa4c867`。Server可保持同一S13形狀及原件hash gate，只替換重建技能的selector為4006，保留明示停用開關；不修改Client或素材。

待集中GUI驗證：新場景連續施法、停止後特效自行消失、再次施法沒有永久堆疊、目標死亡／移除時沒有殘留或當機。1600是原件duration欄，不是保證牆鐘精確到毫秒；低幀率及事件排程可延遲。此輪仍不能將靜態終止路徑當作新候選GUI已通過。
