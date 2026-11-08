# 指定治療與獨立Skill／Spell位置

## 來源與本輪內容

使用者要求各職業提供實際有效的重建技能，魔法放Spell、操作清單位置不能斷線；程式私有，可獨立開發的規格公開。原件[Human／自身目標入口](20261108-native-player-targeting.md)已補證：既有S62 mode2、CastValue0、Field2=0能選Human，C0E文字前導後送六byte C65。本輪未改Client或素材，原生GUI仍待測。

新增聖職者 **重建治癒**：一級解鎖、目前一個rank，指定自身或六格內已投影的存活同隊玩家，恢復30HP，MP6／SP0、冷卻1500ms。溢補停在最大HP；目標滿血、非法、無MP、冷卻或死亡均不結算，不復活。名稱、數值、同隊限制、範圍、視線與投遞方式是**Server重建設計**，不是原服治療表。

## 原生入口與前導分流

新增技能在Spell（kind0），使用S62 Field0=2、UseFlags=0、Field2=0、CastValue0。Field0是body offset4的模式；Field2是offset6，只有值1才進額外傷害型玩家／ALT限制。本版治療不用開PvP或設定未知flag。

Client先送C0E kind2／技能文字，再送C65 `kind:u8, issuedSlot:u8, targetRef:BEu32`。前導沒有目標，不扣MP、不治療、不加熟練、不開始冷卻；收到匹配已發S62 row的C65才處理。模式不另外放在C65 body，不能把兩byte mode5與六byte mode2混用。已授權row的正常拒絕回診斷並保持連線，錯長度／未授權slot仍沿原嚴格邊界拒絕。

原件mode2 mouse hit-test包含Human及Monster；能點選不等於有權施放。Monster不能被治療，其他玩家不會因Client可選而自動取得治療權限。原件沒有替Server檢查同隊／HP，所有死亡形態的可點選狀態仍未知。

## 已投影的玩家能力憑證

Host只從自己的已發Human投影表解析targetRef，綁定角色、精確World租約（account、character、generation、connection）、生命代次及當時投影位置／版本；自身ref1使用自己的當前權威狀態。這些不是額外C65欄位，也不是由Client提供的可信角色ID。

Server在施法交易中重新檢查來源租約、已提交載圖、來源位置、職業／等級／學習。再取同隊、同mapRef／contentRevision、當前已提交且沒有pending載圖的存活候選，距離採兩軸各≤6，並確認目標租約、生命、完整位置及持久Human ref與Host憑證一致。自身可無隊伍施放；他人必須同隊。只有數字ref、錯人物ref、已重連／復活、移動後的舊投影、跨圖、離線、pending載圖或退出隊伍者均不能扣費或取得治療。

位置變更使憑證過期時，等待下一次玩家投影更新再選取。C65本身沒有生命代次或操作nonce；保護的是Host目前已發視圖與Server當下狀態，不宣稱能還原Client每個歷史滑鼠事件的生命代次。

Host以可信地圖檢查視線。已核MAP的tile+6原始flags保留bit0x10施法阻擋；該格可走不代表可施法穿透。靜態地圖的施法檢查包含原生0x10及既有保守步行阻擋，斜角亦不穿過阻擋的兩側格；起點、自身格、途經及目標格都需通過。這是Server保守線段政策，不宣稱光柵化與動態overlay已完整還原；自訂地圖provider若無專用skill-line政策，沿既有可占據格檢查，不冒稱已取得其原件flag資訊。

## 結算、投遞與重播

目標完整通過且有HP缺口才檢查／扣MP6。同一交易提交成本、冷卻、熟練、自己的治療或唯一選中隊友的投遞、動作呈現與收據。群療不會因新增指定治療而變成兩次結算，未選中的其他隊友不回血，也不扣收件人的MP。

沿[隊伍支援投遞](20261108-party-support-skills.md)機制，由收件人持自己的租約在角色狀態交易套用並刪投遞，避免反向鎖另一玩家或用舊快照覆寫其狀態。保存失敗保留投遞可重試；來源入列失敗則成本／熟練／冷卻全部回滾。同一內部操作ID不得改目標，重送收據不重扣、不重治；每個新的正常C65意圖由Host另產生操作ID，不以文字hash合併不同次治療。

施法時已接受的隊友效果可在原截止前投遞，後續移動／離隊／切圖不撤銷；只在相同生命且存活時套用，不復活舊生命。未套用投遞最多保留30秒／每人128份，滿額不接受新目標效果。這些與群療相同的重建政策沿用，不代表原服即時治療的原始存檔方式。

本人／收件人以S08同步實際HP／MP，沿共同事件呈現施法者動作；不偽造S13傷害、永久地圖特效或持續圖示。特定原版治療動畫／音效仍未核對。

## Skill與Spell各自的位置空間

清單版本`reconstructed-career-skills-v5-targeted-recovery`共31項。只把完整匹配已交付v1..v4的內建清單升級，自訂清單不默默改寫。新治療指定NativeKind0；舊聖職者Skill保持kind1，魔法師舊Spell保持kind0，不把舊快捷列所指物件搬庫。

位置身份必須是`(kind,slot)`，不能只用slot。每個角色可有Spell80格與Skill80格，其中Skill一格為基本攻擊，故可學上限80 Spell＋79 Skill。清單驗證依職業及kind分別計數；七職業的資料層總定義界線1113。這是容器界線，不宣稱已還原159個具名技能；Host外部ContentPath仍有既有128KiB界線，不宣稱任意大型JSON皆可直接載入。

定義的可選NativeKind及舊資料缺省須相容：未覆寫仍按既有職業規則；null欄位不寫進舊catalog canonical JSON，避免在同一v1..v4 revision下改變contract內容。已學狀態第一次對照已核catalog補存kind、只增加技能狀態revision，保留原Key／slot／rank／熟練／冷卻。已存非空kind與catalog不符須明確遷移，不默默換庫。

本輪新增一個技能庫schema標記，World輔助資料集67→68。既有有帳號的SQLite庫在第一次建立標記前做一致性備份，保留尚未補kind的原JSON；標記與schema同交易建立，離線角色未轉換也不會讓每次啟動重複備份。單獨升級此項的備份使用pre-skill-inventories-v1標籤；其他同步升級沿合併遷移備份。這是SQLite備份與狀態遷移範圍，未宣稱已做舊版Server完整回退或PostgreSQL備份還原演練。

新學技能只查同kind的空格；不同kind可同號。C30排序的來源與目的期待亦帶kind，僅同庫換位；Spell移到與普攻同號的slot不能移動普攻，Skill排序也不能碰同號Spell。S63清除只針對該庫，S62重新投影保留其他庫物件。新技能自己的Spell／快捷列仍待原生GUI集中驗收。

## 驗證界線

最終完整.NET回歸 **891項全數通過、0跳過**，本增量新增25項：分類／施法線領域8項、資料層13項及Host原格式4項。原始EXE保持原SHA；原生GUI未測。

資料層覆蓋唯一選中隊友、自身無隊伍、數字ref不足以授權、錯ref、距離6／7格、退隊、移動、重連、死亡／復活、pending及跨圖、成本／冷卻、滿血、溢補、目標綁定收據及入列回滾。分類測試涵蓋舊JSON、兩庫同號、普攻隔離、CAS／重登保存及真正學滿80＋79的界線。

Host原格式測試覆蓋Spell row、C0E前導不執行、C65第一次即治療、未投影／過期／非隊友拒絕、自身、只更新被選中的HP、Spell換位不動普攻，以及步行阻擋和原生0x10施法阻擋。原生GUI、指定治療動畫音效及復活不因此視為通過。

## 真實TCP九組

隔離Host、三個聖職者合成peer，沿真TCP及原生組隊入口，九組全部通過：非隊友／錯ref不扣費；C0E前導無效果、第一個C65令唯一指定隊友20→50HP及施法者MP−6；冷卻無重扣；滿血NoChange無成本；自身ref1；無MP拒絕；同號Skill／Spell分離及無假S13；Spell明示移到普攻同號後仍可自療且不移動普攻；後續走動／收件人重連不重套用。期望事件維持5秒界線，沒有把未收到事件改成通過。

受傷、耗MP與補滿使用有一次性目錄標記及精確租約限制的測試fixture，呼叫真Store API；不是Client打怪受傷證據，也不是公開管理功能。其餘角色未獲治療，canonical物品、錢包與銀行不變，投遞最後清空。精確位置／連線／生命同時競態由資料層測試覆蓋，未宣稱這輪TCP強迫重現所有競態。

測試啟動前複製不可變runtime，八個Server DLL的manifest前後相同。最終bundle SHA256 `5a34a4122f8174f1cb066841cbfbefae549bbe3a530e8f52e644fcd2ace86e12`；Host `07b53458becfca3b6d3e987bf1febbb9408e6a36c12611700022a926e09dd791`，Infrastructure `ce29cedc8234508de9e057e50703aad68f0584366cae0583bd02d4888208c607`。沒有發布DLL、DB或原始流量；測試Host已清理。fresh DB的TCP結果與舊庫備份遷移分別驗證，不把兩者混作同一情境。
