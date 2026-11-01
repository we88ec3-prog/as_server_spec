# 實機回報：北向NPC、守護鈴、快捷鍵、空揮與音效

## 來源與尚未完成的範圍

使用者於2026-11-02（台灣時間）提供學校畫面並回報：從南往北走時NPC未正常
出現；普攻已拖到下方快捷列，按數字鍵仍無反應；命中及摩斯死亡缺音效。
另點「守護鈴」後斷線，並說只是誤點、不記得原功能。

使用者提供的原版行為線索另包括：空白鍵／快捷鍵可對空氣普攻，非指定目標
技能可對空氣施放且不消耗MP／SP；攻擊NPC可能顯示miss。這些需求／回憶
**不是全部已由原件證明**。本輪只實作固有普攻空揮；一般技能成本、所有
非指定目標技能、NPC miss字樣仍待深入分析，不發明技能ID或用0傷害冒充miss。

REA原件身份與精選Evidence見[機讀視圖](feedback-native-20261102.json)。
原始日誌、完整REA與失敗的被動記憶體讀取留本地anal-roy-temp，不公開封包body。

## 守護鈴：原生C27被當未知封包

本地Server於UTC 2026-11-01 16:04:24記錄：InWorld／WorldReady收到C27、body長0，
分類unknown-opcode並closed，close reason為invalid-native-protocol-or-state。
這是Server主動拒絕原生請求，不能解讀成使用者破壞協議或Client自己崩潰。

原件`CMyGuardianPacket` RTTI連到constructor`0x574010`，呼叫`0x578600(0x27)`；
writer vtable指向`0x5740c0`，原件byte為RET。`0x534d42`有呼叫constructor。
這與實測空body吻合。`0x574000`是另一個getter，不是此constructor。
名稱支持守護相關請求，但沒有據此還原守護召喚、狀態、裝備或SProtector成功回覆。

本輪Development native profile只接受已授權InWorld角色、加密、精確空body的
C27並維持連線，不發成功回覆、不建立守護物件／物品。格式非空、載圖中、
失效owner與非支援profile仍拒絕。其他未知opcode政策不放寬。
此相容處理只解決誤斷線，**守護鈴完整功能未完成**。

同輪UTC16:04:28另見重連socket在Connected直接收到C00而關閉；這是另一條
尚未還原的重連握手分支，不假裝本輪已修復所有自動重連情境。

## 快捷列：S62使用模式0不會執行

原件`0x46d2c0`按快捷列資料找ActionEntry，讀`entry+7`決定使用方式。
值5立即建立CUseAction再走`0x401ed0`；值0不進任何可執行分支便返回。
S62 handler`0x4f2cd0`及entry constructor`0x4017d0`支持以下對應：

|wire／模型欄位|entry欄位|本輪含義|
|---|---|---|
|kind|+6|技能／法術分類；本輪仍kind1|
|三個byte中第一個Field0|+7|使用模式selector，改5，非bitmask|
|第二個UseFlags|+8|bit0可阻止非cast action送出；仍0|
|CastValue|+0x80e|仍0，走C0E，沒有猜測C4D技能ID|

初始普攻row前7 bytes改為`01 01 00 12 05 00 00`。S62第二段文字仍為普攻；
`0x401df0`檢查+8 bit0後複製該文字到C0E kind2。這是修正原件正面顯示的
本地使用入口；不是找回官方普攻資料表。快捷列GUI仍須實測，TCP只驗row與C0E。

## 空揮的Server呈現與資源界線

原生預設空白鍵的面前格選取可能送target0的C13；非cast普攻快捷列送C0E。
本輪對自己已發初始普攻的已授權角色，target0回S1A self_ref1、Motion4、100%。
`0x4f1c60`原件處理本身有self ref分支並呼叫LivingObject motion；Motion4沿
既有基礎衣服出拳證據。不是憑空指定一個不存在的目標發傷害封包。

空揮不進入扣血交易、不產生training hit或practice里程碑、不寫HP／MP／SP；
這是本階段固有普攻0成本政策，不外推所有技能。空揮與成功命中共用每連線
呈現節流，真命中仍須通過持久距離／冷卻／HP校驗。沒有開放NPC／玩家扣血。
既有C0E近期選取政策保留；選取過期可空揮，不再假裝命中舊目標。

## 命中及死亡音效

`0x4a4b00→0x4b6850`的S13擴充欄位經`0x53d420→0x53d250`播放音效。
已確認wire offset19的BEu16（模型Field3、完整packet+0x48）是音效ID；之前送0，
所以沒有此路徑的命中音效。與顯示傷害的wire22..25／Field5分開。

`0x53d250`用sound_id/1000+12選庫、sound_id%1000選slot，播放archive WAV。
本地Sound0.dat鎖定長度19291196、SHA
`dbe1edd0dce6765b2ec21d1cfda8de95901df24e2fd16f92873c8591c154cd6d`。

|候選用途|slot／ID|來源member|offset／bytes|member SHA256|
|---|---|---|---|---|
|一般命中|1|00001_타격음.wav|38732／2968|83db6471676661aa52fb45b3f21b69f48c3a62e8df237ad0c860268c6ce2bfb4|
|摩斯死亡|38|00038_모스죽기.wav|1502066／35148|2cf07463cf24c06e95e837e5c6411680faa3261da24e90aca0f1c9bbc2a90e17|

檔名CP949、WAV格式均驗證；檔名支持素材用途，**沒有原服封包證明官方事件配對**。
本輪明示重建綁定：命中S13 Field3=1；延後S5F同批再發S19 kind0/id38單次音效。
kind0為採用的非音樂subset，不宣稱已還原全部sound kind枚舉。原BGM不改。
音效綁定只在核對摩斯與Sound0素材後啟用；不改持久戰鬥契約／生命週期。
舊death ref取消／快速重生時不補播；活物死亡投影一旦送出不重複播放。

被動讀取Client音效設定因Frida VirtualAllocEx存取拒絕而未成功；沒有得到當下
音效開關值，不把工具失敗當作Client設定關閉，也未改其設定或EXE。

## 南往北NPC生成時序

先前完整pane邊界仍用來保留／移除已有NPC。但S0B後立刻生成剛進新邊界的
NPC時，Client鏡頭可能尚在上一格，物件會被舊pane立即裁掉，Server卻已記為
可見。這是與使用者方向性回報吻合的**待GUI驗證時序解釋**，未取得成功runtime hook。

Server將新進NPC的S07限制在「前一格pane與新pane皆包含」時送出；已存在NPC
仍保留完整新pane，不退回先前過小視野。初次C35載圖不套移動交集。六組
四方向／不同偏移測試包含南離開→向北返回：第一格邊界不過早S07，下一格
交集成立後發一次S07+S1A，區內與重播不重送。此修正目前限教學NPC投影；
怪物其餘原生裁切時序仍需持續觀察，不藉此宣稱通用多人AOI完成。

## 驗證與待辦

368項.NET測試已通過，含C27合法／非空／載圖／失效owner、六組NPC返回、
初始row模式5、空揮無hit／里程碑、節流、S13音效欄位及單次死亡音效。
完整新版五職業TCP含守護鈴後仍可空揮、不產生傷害、正常命中／死亡音效及
畢業重登，五職業全部通過。Client畫面／實際聽覺驗收仍待集中測試。

仍開放：NPC攻擊miss的確切renderer／封包語意、其他非指定目標技能與資源成本、
完整守護系統，以及守護誤斷線後出現的C00重連分支。這些待辦延續A-004、
A-016、A-019／相關封包研究；不把使用者回憶當成已完成實作或原生事實。
