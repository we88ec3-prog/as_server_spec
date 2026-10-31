# Roy1/Roy2 合併後需再分析的工作（2026-10-31）

## 2026-10-31 五件新資源已到位（不要再索取）

`nNewJoin01.dat`、`PaperDialog.dat`、`PaperDialog02.dat`、`Monster00.dat`、`World00.dat` 已讀取與離線驗證，詳 [原件證據](../04-analysis-integration/new-asset-samples-20261031.md)。nNewJoin01 的初級學校三頁與 `STATE=ACCEPT/REFUSE` 是**資源靜態已證**，PaperDialog02 另有 `PAPER02=START/NOT`；兩包 5+5 個 YPF member 已建立檔名指紋。**取消舊表「本地缺這五件原件」的描述**；仍需 Client NPC→script、`QuestDialog_Create` 真依賴、imageID→YPF member/motion、學校入圖目的地與原生 E2E，不可把腳本對話當 NPC 綁定或任務完成。Script 缺件請先找原生 dependency 明確檔名，不能直接要求猜測的 `QuestDialog.dat`。


**不修改原始 `Asgard.exe`，不需要還原原服 Server-only 的管理政策／固定 AI／發獎策略**。狀態：11 個 A 本次已回寫 integrated（9? Roy2 六項、Roy1 五項），但「已回寫靜態證據」不等於 Native Client E2E。不要重做已證已交付部分。

|先後|A 任務|要追的剩餘 Client 行為與可交付憑據|影響開發|
|---|---|---|---|
|**P0**|**A-027 / A-021**|在原版 C03 成功無角色帳號後，是否**真的可進 NewUser/MakeInfoDialog**？UI callback、C02 首欄標籤/帳號來源與當前 Auth/Session 的聯結。沒有途徑要給出查過的入口及否證，不可用匿名 C02 冒充登入。|DEV-040 Native 創角；CT-054|
|**P0**|**A-024 + A-011**|S07 **已知 1..14 row schema**，現在追各 kind → ObjectRegistry/render/sprite/EntityId/NPC vs Monster 的**實際分類**；點擊 NPC 是否送 C43、C39 或其他？對應 S34/S62/S63 UI 回應。提供 EXE ctor→handler→畫面、缺件檔名。|DEV-070-M 真 Client NPC/Monster 顯示；CT-080/081|
|**P0**|**A-004**|A/B 同圖收 S33、S06/S11、S0E 的 ObjectRegistry **同 key**、出生/移除 callback、ID 重用、可見性 update/離圖／斷線 Client 反應；不要只證 parser。|DEV-070-M 玩家互見；CT-055/070/075|
|**P0**|**A-022 + A-005**|真實 `C25` 原版 Client 送包與 `S15/S14/C35` 可接受 map_ref/checksum、S04/S33 顯示；移動碰撞 flag4 vs flag0 的不同算法/Client blocked move、S0B 校正 UI；`Map0/1/2.dat` 已有。|DEV-050/060 Native World；DEV-070-M 權威移動；CT-071/072|
|P1|**A-009 + A-025 + A-010**|C13 Client 實際點擊/目標取得、S13 傷害UI、S5F 死亡與 S0E 移除的畫面回調；C3D/S3D 剩餘複雜 subtype；**Roy1 `S1E DieObjects` 與 Roy2 `S5F` 指向同 parser 0x57E260 的衝突**，追真 S1E vtable/reader。技能 C4D/C56 與效果，教學是否強制戰鬥需內容證據。|DEV-080；CT-058～060/078/079|
|P1|**A-026 + A-023 + A-012**|原版 Born 只引導 (31,29)，S44/C6C close 不等於 QuestComplete。追原生招募員 NPC 與 `nNewJoin01.dat` 候選對應、C39/S2F 互動/Script reply 後**Client 實際何時更新任務 UI 或切圖**。有條件就請原服封包 trace 或官方內容/設定，無則保留 unknown。|DEV-090；CT-061～063/026～028|
|P1|**A-020**|C0F type≠3、S18 kind1、S60(type0/1) region/Client UI 及錯誤/重試畫面；`C4B` 是否真的必然請公告不可從空 writer 推出。|DEV-020；CT-056/057|
|P2|**A-008/A-006**|S08 conditional Stats native 面板、S05/S33 其他 flags/裝備及 UI；Human 8方向 YPF/DOI 動畫圖層對應（要實際檔名或 renderer）。|DEV-080/外觀；CT-073/074/076/077|
|P2|**A-007/A-019**|C1C/C08/C0C/S0F/S37 物品實際 Client UI，S19 音樂 map→track 真來源與不同圖時行為。|物品／音訊；CT-064～069|

## 必要來源檔（只要求真正缺的）

- 已有：`Asgard.exe`、`Born.dat`、`Map0.dat`、`Map1.dat`、`Map2.dat`，**不要重複索取**。
- 可明確指出的 Script 依賴：`PaperDialog.dat`；交互 Script 目前僅有候選名 `nNewJoin01.dat`，要由 A-023/026 確認是同版/同 NPC，不可當已證。
- **NPC 資源**：原件中有 selector `World%02d.dat` 與 `Monster%02d.dat`，具體例子 `World00.dat`、`Monster00.dat` 只是模板展開，不保證存在或就是 NPC 定義檔。**請 A-011/A-024 先回報真實被載入的檔名/目錄索引**，不要讓使用者盲傳整包圖像。
- 原服的原生 quest/mob/drop/地圖/死亡時序若僅靠 Client 無法還原，可標「Server policy unknown」不阻擋已知 Client codec 交 DEV。

## 交付驗收

每個 A 的增量要有 `trigger / client_sends / client_receives / client_reaction / evidence(original VA or resource hash) / unknowns`。協定及合成測試可先進整合；Native E2E 必須獨立錄原版 Client SHA、畫面/方向/去敏封包/下一個 UI/Server state，**不可使用合成 fixture 冒充實機**。同一種已知封包的欄位切片不要重做，集中補 registry/UI、地圖資源綁定及錯誤/成功分支。


## Roy2 A-011 / Roy1 A-004 第二輪分析結果

**A-011 已 integrated/partial**，不再要求它從頭找出 NPC／怪物 resource library 或 C43 serializer：S07 kind1/2/4→MonsterObject、Monster 10 sprite slot/檔、C43 兩條 producer 已查。**剩餘的 P0 項目**：哪個實際 SpriteImage ID 對應教學招募員／首隻怪；S07 row+0x222 到最終圖像 ID 的完整 XREF；`C43→S34/S44→NPCChatDialog` native UI chain；Monster motion 六 selector 真實動作/動畫素材；A-004 已有 0x4EAC30 ObjectRegistry lookup，但 death/remove callback、雙原 Client AOI E2E 尚未證。

**需要的具名原件**（若要確認圖像/動畫）：原版同版本、確實存在的 `Monster00.dat`（或任一 `MonsterNN.dat`）和 `World00.dat`（或任一 `WorldNN.dat`）各一份樣本即可。**不需要 `@Monster00.dat`，也不用重新提供 Asgard.exe／Map0～2.dat／Born.dat**。互動 PaperDialog 的 `PaperDialog.dat` 可另提供；`nNewJoin01.dat` 仍只是候選。最新 CT-082/083（Roy2）及 CT-084～086（Roy1）均 planned/not-run。

## P0／A-020 + A-002：原版密碼欄 8 字限制定位（2026-10-31）

使用者實際觀察遊戲登入密碼欄只容納 8 字元。請以相符原件 `Asgard.exe` 追**登入 C03** 的 password control（不是創角 C02 region1 >=12 gate），交付 max-length 初始化 VA、鍵入第 9 字/貼上/大小寫/CP950 轉碼之 UI 效果、C03 `string8` 長度及實際送入 bytes。原生 CT-037 用 8 ASCII 英數確認，這是 Client I/O 精準分析，不要求還原原服密碼政策。Server 先依 [TW-native-8](../02-server-planning/native-game-password-8char-policy.md) 自訂合法遊戲憑證並作 P0 DEV-030 修正；尚未獨立反組譯證實 8 字 UI，標 `reported-client-UI`。
