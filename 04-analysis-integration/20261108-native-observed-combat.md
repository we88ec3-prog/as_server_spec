# 原生戰鬥旁觀者：數字、動作與有限特效（2026-11-08）

## 範圍與入口更正

原件 Asgard.exe SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，Ghidra12.1.4，原件唯讀，未啟動或附掛使用者程式。本頁補多人投影限制，不重定義既有S13 15／31byte body。原生GUI驗收仍待測。

**S13正確入口是4F2620**（4F4994 JMP），沿既有[combat target報告](20261101-native-combat-target-and-effect.md)。前輪remote-player報告一處將同樣讀兩個ref的4F1DC0誤標為S13，本輪已更正。4F1DC0內的Graphics.Effect檢查不能直接當成S13 gate。歷史raw保留，不把錯誤入口的條件接進Server。

## 投遞前必須有合法物件

普通非packed、flags bit0傷害子集的真S13流程：
1. 4F2647先對ReferenceB查4EA240；若命中已退場／延後清理集合，直接結束。
2. 4F266C／4F2692查ReferenceB與ReferenceA，轉LivingObject；不存在的非零目標可呼叫46D230，產生C0C缺物件重同步。
3. 4F288F..4F28B0對來源呼叫virtual+8。Human為47BC20、Monster為4D6C60，處理來源motion／effect。
4. 4F29FF對目標呼叫4A4B00，再到4B6850投影受擊、數字與聲音。

因此Server對每個接收者須使用該view已投影且仍有效的source／target ref。不能拿self1假裝別的玩家；不能靠廣播未知ref讓Client補齊，也不能因C0C讓已死亡或離開視野物件復生。來源／目標不完整時雖存在其他特效與packed座標分支，本輪沒有將它們擴成旁觀fallback。

已知事件與AOI可見性、舊lease拒絕、死亡狀態及每位觀察者的去重，都是Server政策，不是Client替Server做的授權。

## 命中數字：旁觀者並非一律被擋

4A4B00在S13 flags bit0存在時，交4B6850：
- sourceRef（packet+24）
- damage-present=1
- extension Field0／Field1／Field2的受擊動作／特效參數
- Field5顯示amount
- Field3 positional sound

4B6850取得UI20的50D290控制對象ref，並依下列順序決定數字style。該UI經50D310／50D3C0／50D460來源字串確認是ProtectorDialog，RTTI為TargetControlPane；它不是普通滑鼠選取。沒有守護控制時getter回0。

|條件|damage-present=1|非damage／MISS路徑|
|---|---:|---:|
|來源是本機self|0|3|
|目標物件是本機self|1|4|
|UI20守護控制ref等於來源|0|3|
|UI20守護控制ref等於本機self|1|4|
|以上皆否，目標屬Monster type-key|2|5|
|以上皆否，目標屬Human|不建立數字|不建立數字|

fallback的9200E8確為Monster type-key：Monster getter4D6040 bytes `B8 E8 00 92 00 C3`，Human getter479E90 bytes `B8 F0 E3 66 00 C3`回66E3F0。兩者同父91FBD8；5130C0只沿type-key父鏈比較。因此Human不會因為「也是LivingObject」而通過Monster fallback。

具體含義：
- 玩家A攻擊怪物M，旁觀者C即使沒有守護控制對象，也有Monster fallback的style2數字路徑。
- 怪物M攻擊遠端玩家B，C既非來源／目標，若無對應守護控制對象，就不建立該Human受擊數字。
- B自己則走style1。不能把同一31byte包在三個Client都出現數字列為原件保證。

在已查路徑沒有找到一個S13 flags值可強迫所有第三方Human數字顯示。篡改來源1或偽造守護控制資料會改變身分語意，不作解法。樣式、數字像素與守護控制UI實際狀態仍需原生畫面驗收。

## 聲音不等於數字

4B6850的數字fallback失敗會跳到尾段4B6C45，而不是直接return。Field3非零時仍經53D420建立定位聲音，再53D250進SoundManager；使用者Sound.Sound設定、SoundManager啟用與sample是否載入仍可使它無聲。

所以旁觀Human沒有數字，不代表該S13不能有命中聲。也不能反過來憑31byte包或非零soundId宣稱耳朵已驗收。只使用已核同版SoundId；不憑技能／怪物名稱推造音效。4006資源本身沒有type7聲音節點，extension命中聲是另一條明確來源。

## 有限4006與重複投遞

[4006生命週期補證](20261108-native-effect-lifecycle-correction.md)仍適用：
Effect4.dat SHA `5cac55442e8504786bf9e8b7be73eed2a1cd05a65970739e1fdf24df0f7e58dc`；slot7 Effect04006.eff，offset11711203、1976bytes，SHA `2729bf0f3b4a5399c4bf7831329bf8126167960ab3824c088d47fce7ed842107`。節點0→1、imageKey4002、duration1600，沒有回邊與聲音節點。它是重建通用有限候選，不是原版法術對應。

Human47BC20每次符合條件均可呼叫458BC0配置新的runner，沒有原生eventId去重；runner+80=0時，459680依duration+1排ERke，459BD0→459B60→4B9CE0刪圖，活動與排程清空後釋放runner。這是原生完成鏈，不能用Server猜timeout代替。

因此：
- 一個已提交hit對每個合法觀察者投遞一次S13，才是Server「每hit一次」政策。
- 範圍技能三個合法hit，各一個S13，可能建立三個獨立有限runner／來源動作；不會因同selector自動合併。
- 重播同一S13會再播放，不能把有限資產誤當重播去重。快速多hit可能同時疊加，但應各自結束；實際消失仍待GUI。
- 不為了修視覺疊加重算傷害、重扣資源或刪除權威目標；observer投影與交易receipt分開。
- 不額外發一輪相同S1A／S13當作「補數字」，避免重複動作和音效。

## S1A空揮、恢復姿勢與死亡

S1A對已知remote Human可直接送motion4空揮、motion0站立，不需要target。它沒有傷害或資源恢復語意：真正HP／MP／SP由Server提交，S08只給正確owner，旁觀顯示不能靠改self數值。

47ACE0仍有動作gate：47A440→476880→474F00辨識步行／跑動動作（8..23、40..55及特殊714..729），忙碌時可拒播；HumanFlags bit4也會擋，0x1000只允許0／1／2／0x52。因此不能保證在進行S64插值時插入的空揮或墓碑一定顯示。

Monster→remoteHuman命中可沿同一S13來源／目標鏈，權威死亡提交後再S1A(remote,3,100,0)；普通Human motion3映direction+64，實際服裝素材是否含該動作另受資產限制。不要拿S5F的Monster生命週期代替Human。

為避免旁觀者仍在走路而拒播死亡，Server可選擇明示的重建策略：必要時先S33於已提交死亡pose重建remote／清path，再S13該次命中，最後S1A3；保留墓碑期間不提早S0E。先重建再特效也避免剛掛到舊actor的runner被外觀重建移除。這是依native gate推得的可測順序，不是原服死亡時序或延遲的還原證據。復活投影同樣由權威狀態決定，remote S33＋S1A0不得變成本地S05。

## 本輪證據與待測

原始資料在combat-observers-native-20261108；公開僅精選契約：
- `ev_6ce9df8ff8aa84f01e3ef667016faa175bd633a08ce9ccc1e7ac42b3de4c841d`：4B6850完整數字分支、50D290守護控制ref。
- `ev_86770bc3a4d75c53bda0aeabf85486f01391fec2f5f29b3e37334b5f39b089f8`：5130C0 type-key父鏈、HitNumber建立。
- `ev_b47e644d438bcff3e901b90f36283fe379c0f3936f0d1ede450ed39fc66a363a`：4A4B00 extension欄位與定位聲音。
- `ev_5a98c7ee53d01ebcb9204fbe4d37bc4c389d77f9b4b16c3687bf6035d7adfa12`：458BC0每次runner配置、47ACE0動作gate、SoundManager。
- `ev_2ae26713d8609f17f5b0736a4aca0206c3759155893146ac018ad15bb18147e1`：既有有限生命週期原件鏈。

GUI集中待測：三人旁觀A打M、M打B，C無守護控制時的差別；已提交amount／HP與視覺分開比對；單次／範圍／連續4006停止後消失；空揮與行走交錯；移動中受致命擊的remote墓碑；視野退出與舊ref不再播。


補證：UI20 class COL／type descriptor指向TargetControlPane，50D310、50D3C0、50D460均標ProtectorDialog.cpp且發守護控制包。此處的額外身分分支不可當成普通鎖定目標或滑鼠hover設定。
