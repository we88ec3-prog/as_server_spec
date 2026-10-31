# 本地測試問題 → Server 修正交接

更新：2026-10-31。規格起點 `6b93590`；唯讀核對 `as_server_roy@b8e212e`。本次沒有執行該 Server、變更其檔案或驗收遊戲。問題機讀入口：[runtime-issues.json](../03-analysis-requests/runtime-issues.json)；工作邊界：[問題收集流程](../00-governance/runtime-feedback-workflow.md)。

後續實測回報 **RI-005**：Client 視窗有回應但使用者看到斷線，之後手動關閉；事前 UI／根因未知。新增 [閒置斷線與監測合約](idle-disconnect-observability.md)，要求程序、TCP 與會話狀態分開，按階段診斷 timeout；不直接歸入 RI-001，也不把手動退出當 crash。

第二輪已觀察 Server FIN_WAIT_2／Client CLOSE_WAIT，使用者畫面為創角「登錄連線中」後「伺服器無回應」。需求拆分為 **RI-005 表單等待排除一般60秒 read timeout** 與 **RI-001 送出後 wire 失敗**，兩者獨立回驗。不能只延長期限就宣稱創角修好；也不能因未記到 C02 就把本次根因定為 C02。詳見同頁第二輪補充。

**最新結論（23:51 新連線，Server f2a4a38）**：已關聯 Client C02 send=20/20、Server 收到 C02、reason=`native-c02-fields-unknown-a030` 後關閉且未回 S02；RI-001 的本次直接原因已確認。新版 FormInput 已實作 idle600／absolute1800秒，此次關閉不是60秒 timeout。詳見 [完整去敏時間線與交付](idle-disconnect-observability.md#新連線回驗c02-已收到後主動關閉ri-001-根因切片已確認)。下方 b8e212e 表為歷史查核；新版期限已有實作，原生 C02 adapter 仍未接通，不應重做已完成的期限工作。

## P0 / RI-001：原生創角斷線

目前的 [斷線修正規劃](native-newuser-disconnect-remediation-20261031.md) 以 `ad84f9` 作歷史根因基線；不能把它的「尚未驗證憑證／沒有草稿處理」直接當成新版全部未實作。

|項目|截至 b8e212e 的唯讀查核|交付／剩餘工作|
|---|---|---|
|管理帳號與創角身份|實作文件已回報共用憑證驗證、停權／version、限流與 creation-only proof|沿用並對照負向驗收；不要求先 C03，不由 C02 自行註冊 Account|
|C04 提交|實作文件已回報 proof、世代／TTL、transaction 與冪等處理|仍須核對實際 wire adapter 是否能到達，不能以後端測試取代原版驗收|
|關閉診斷|已有 pre-C02、frame／timeout 等 close reason 分類改動|保留實際版本、會話時間線；確認 FIN/RST 方向，區分 H0～H4|
|原生 C02/C04/C15 接線|目前 LoginWireSession 的對應分支仍明確關閉，原因指向 A-030 或缺少已驗證創角意圖|先補 NAME/EMAIL/region 與 S02 錯誤路徑，再依已證 wire 契約接通；不猜欄位、不盲送成功|
|原版 Client 成功與錯誤 UI|本次沒有實測結果|CT-103～105 仍 not-run，不標 resolved|

以上實作進度來源為該 commit 的 `docs/planning/DEV-CREATE-spec-20261031.md` 與入口分派唯讀查核，屬實作快照。**Server 必須遵守的行為**仍由公開合約決定：

1. 三入口獨立：Login、NewUser、ChangePassword。一般登入失敗不能虛構「轉創角」封包；C02 可獨立驗證管理端預建帳號，無需先成功 C03。
2. 合法 C02 → 驗證憑證／狀態／限制 → creation-only pending → 第一 S02(0)；沒有授權成功之前不可回成功，也不可發 World grant。
3. C04 五個 u8 只能提交本連線同世代的有效 pending；成功 atomic commit 後回第二 S02(0)。Client 本地完成並返回登入，之後 C03 是另一個登入流程；不可自行在創角成功後強送 S03。
4. 一般錯密／停權／重名等業務失敗使用 **A-030 證實相容的**非零 S02 構型；未知時不能臆造錯誤碼。C15 只取消擁有者未提交意圖，不刪已提交角色。真正 frame／protocol 錯誤另按協定關閉。
5. 觀測僅記 opcode、length、ordinal、階段、時間、匿名 trace、close reason／發起端與去敏 UI。不得輸出 Password／Confirm／Email、C02 解密正文、憑證 hash 或 token。

**交接次序**：A-030 補原生欄位、地區及錯誤／重試切片 → 本規格審核更新合約 → Server 開發者接通原生 adapter → 合成及原版 CT 分別驗證。已有後端或診斷可沿用，不需等所有研究才做可獨立開發部分；本工作不替開發者修改實作。

**驗收**：沿用 [CT-103～105 矩陣](../05-conformance/native-newuser-disconnect-acceptance-plan.md)。錯密、未知帳號、停權、已有角色、合法創角、C04 中斷／重送、C15 取消與成功後再登入逐項記錄。每輪可連續測多項；因前段失敗無法到達者寫 not-run。

## P1 / RI-002、RI-003：置中與獨立衣色

這兩項是舊 Python 原型的已知問題及靜態修正，不是已重現的新 Server bug。先對照現有 [A-006 分析](../task_a/roy2/A-006-analysis.md)；不另開相同研究、不套用舊資料庫 schema 作為新 Server 的必要實作。

|問題|跨實作合約／預期|回驗步驟|
|---|---|---|
|RI-002 人物站立偏右、移動置中|保持 world x/y、路徑與碰撞不變；鏡頭偏移獨立。800×600 已分析 profile 下 S04 offsets(8,9) 對齊 (400,300)，舊(9,9) 橫差48px；其他 viewport 需重算，不能全域硬套。是角色錨點，不以衣服外框判定。|同點站立→八向走停→邊界→切圖→重登；記錄 profile、S04、世界座標與螢幕錨點。不能為置中改目的地或移動確認。|
|RI-003 衣服跟隨髮色|髮色／衣服染色獨立保存、讀取及編碼，S05/S33 一致；ff00ff 是無染色保留值，000000 在已知 S33 轉成該值。外觀 API 若不能忠實表達純黑，必須拒絕或明示限制，不能默默顯示為原色。|紅髮＋藍衣→更換兩套有染色層的衣服→切圖→改綠髮衣色不變→恢復原色→重登。合成 bytes 與實機顯色分開記錄。|

## RI-004 與 Client 診斷的界線

延遲 tooltip 副本曾獲使用者確認；不能由此推定 Windows Update 是原因，也不能推定目前 Server 有相同缺陷。重新發生時先取得版本及重現／程序狀態，禁止把補丁視為原版 Client 必需條件。

2026-10-31 的主選單診斷副本曾實際顯示 **New／Connect／Exit**，但只確認可見畫面，沒有按下後完成創角。相關原生入口的靜態整合見 [本地登入／創角入口補充](../04-analysis-integration/local-account-entry-observations-20261031.md)。這項結果不計入 CT-105。
