# 「魔法師／預言者」顯示的具體來源

接續[角色能力初始化](20261102-native-status-initialization.md)。使用者截圖上方職業是魔法師，下方藍色字樣是預言者，同時 FAME=-52、若干數值=-858993460。本輪已找到能精確重現該**錯誤徽章選擇**的原件分支與素材，不能再把預言者僅當作獨立 Title 文字的猜測。滑過當機仍是另一個未驗收問題。

## 三個可見欄位要分開

|StatusDialog child|來源|作用|
|---|---|---|
|0x19|HumanInfo+5職業碼，加BasicString ID455|職業名稱，Mage=3為魔法師|
|0x1a|Status+0x210，由S08 text區塊更新|獨立稱號文字|
|0x1b|職業碼及Status+0x452的signed FAME，經0x47d090選圖|occupation.ypf階級徽章，截圖藍色預言者的來源|

原件 `0x540050` 同時處理這三項；不能把錯徽章當成持久選職 enum 被改掉，也不能以修改Title文字取代修正未初始化數值。

## 原件如何選到「預言者」

EXE SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，REA/Ghidra12.1.4。精選地址與Evidence ID見[機讀證據](native-occupation-rank-evidence-20261102.json)。

`0x47d090` 的 FAME<0 分支：

1. `0x47d110` 設 object=7。
2. `0x47d117` 將門檻放成32-bit整數195（0xc3）。
3. `0x47d11c` 將signed FAME sign-extend，`0x47d120/122` 進行有號比較並在小於等於時跳到第一個結果。
4. 截圖 FAME=-52 符合 -52≤195，讀 `0x60710a` 的LE u16值2，得到 **object7/frame2**。

這裡有必要核對指令的MOVZX/MOVSX及JLE，不能只憑反編譯型別或把0xc3誤當-61自行改寫門檻。實際指令如此，不等於已知原服負聲望的設計意圖。

Basic.dat bank0/slot23 `occupation.ypf`，offset3623935、150286B、member SHA256 `5a75469e3390595bbda63bac235e7bca03e2ba90306c43c11337fc86c796be2b`。原資源為YPF17、63×17、flags0，未使用先前圖塊的調色盤分支。metadata至3340B恰結束；10個object的frame數依序為 **10/8/9/10/10/8/8/17/17/3**，各object action/state/transition皆0。

以有界direct RGB565＋alpha-run解碼作本地離線預覽，object7/frame2的文字正是「預言者」，外觀與截圖藍色字樣一致。完整圖像與派生預覽只留本地，不上Git。這是**原件指令＋資源圖像＋使用者截圖數值的相符證據**，不是該次凍結process的live memory或stack capture。

BasicString448也有同名文字，但不是這條徽章選圖路徑的字串來源；先前只找同名文字不足以判斷，本輪已補證。

## 與S08初始化的關係

既有Server未送S08時，FAME保留0xcc，按signed byte顯示-52；完整32-bit欄位可能顯示0xcccccccc即-858993460。`0x53f510`只初始化部分狀態，不能期待缺封包時其餘欄位自動有效。

前一輪已實作持久S08的重建出生基線 FAME=0，按原件 `0x47d135` 給object/frame=-1，StatusDialog將徽章控制項隱藏；上方職業仍由Mage碼3顯示魔法師。**這不代表正常剛出生一定要有「魔法師」階級徽章**，也不宣稱FAME=0是原服出生規則。實機仍須確認收到S08後預言者圖像消失、數值正常、滑過仍可操作。

正聲望另從職業碼-1選object並查cutoff表。Mage表有20/30/40/50/60/70/80/98/99/255對應frame0..9，但該object實際只有9個frame（0..8）；因此100..127會算出超出已觀察frame範圍的索引。這是後續聲望系統的版本相容性檢查項，不能據此直接宣稱本次hover凍結由越界造成，或擅自改寫合法玩家聲望。原服聲望成長、負值政策與上限仍未知，當前Server沒有新增聲望獎勵玩法。

## 下次實機可讀的診斷值

私有只讀探針新增 `--status` 的職業碼與徽章預測。職業 byte 使用經指令核對的 **User+0x28d**：`0x5400e6` 先將User pointer加4，`0x479ea0` 再讀HumanInfo+0x284，其中職業是+5。**不能漏掉+4而讀成User+0x289。**

只在明示PID及支援EXE SHA相符後以query/VM_READ讀取已證scalar與少量固定常數表，沒有hook、遠端執行、寫入或帳密字串讀取。報告預測是依native分支推算，不冒稱已讀到當前畫面像素；`frame_within_reviewed_asset`只對上述SHA的原件素材frame數比較，不能冒稱已驗證執行中Client使用的素材版本。

離線向量通過：FAME=-52→object7/frame2、FAME=0→隱藏、Mage FAME1/99→frame0/8、FAME100→超出該asset frame範圍，正FAME配未審職業不讀任意表。未對其他路徑的Asgard程式讀記憶體，也沒有替使用者重新啟動測試環境。

hover卡死仍需保留當下Client診斷，舊tooltip延遲相容修正與metadata假說未被本輪證實或推翻。既有集中實機測試要求保持有效，無須因這次純分析再跑一次。
