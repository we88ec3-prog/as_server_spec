# 斯歐米 NPC 原生腳本與安全介紹契約

2026-11-07。使用者目前優先希望配置斯歐米 NPC；本次依原始 Client 的 `Script/nSu*.dat`、`Merchant.dat`、`MerchantDialog.dat` 靜態分析。這份規格提供可獨立重建的行為契約，並未提供原始腳本全文。機器可讀的來源雜湊、CRC、各 NPC 功能與依賴在 [JSON](20261107-suomi-script-npc-contract.json)。NPC 站位另外參照 [配置分析](20261107-suomi-placement-review.md)。

## 來源與證據界線

解碼限制為 zlib 最多 1 MiB、完整 EOF、無尾隨資料；內部是 big-endian 版本 `u16=1`、UTF-16 code-unit 長度 `u32`，後接 UTF-16LE XML。JSON 的 CRC32 對原始 XML 文字以 strict CP950 編碼計算，保留原始換行，並不是對壓縮檔計算。不能編碼的檔案記錄 `null` 與字元位置，不以替代字元冒充已驗證的原生 CRC。

這是出貨腳本的靜態證據。未由此證明原服的 NPC 地圖座標、販售品項、價格、餘額、任務狀態或完整職業服務；檔名尾碼 `01` 也不是座標。原生 GUI 是否正常載入、頭像是否正確及文字是否裁切，仍需實機確認。

## 可辨識的姓名與服務

| 腳本 | 原件可辨識內容 | 菜單能力與交談條件 |
| --- | --- | --- |
| nSuBanker01 | 斯歐米城銀行掌櫃「席茲」 | BANK；有 Quest01 時 TALK，呼叫 Quest01 |
| nSuInn01 | 湖濱小屋、莉坦的旅館 | 無交易；Quest01／Quest04 時 TALK |
| nSuAllMarket01 | 露天商人「蘇西亞」 | BUY、SELL，無 TALK |
| nSuPotion01 | 老年人口吻，未辨出姓名 | BUY、SELL；Quest02／Quest16 時 TALK |
| nSuPriest01 | 魔法師之神「里亞」的神官 | BUY；DoesTalk=false，雖保留 MerchantTalk→Quest17 |
| nSuSmith01 | 可辨功能，部分文字混雜／CP950 失敗 | BUY、SELL、REPAIR；Quest02 或 STEP 時 TALK |
| nSuMarket01 | 問候使用動態 MerchantName，部分混雜文字 | BUY、SELL；DoesTalk=false，保留額外交談函式 |
| nSuProMarket01 | 文字混雜，未辨出姓名 | BUY；DoesTalk=false，保留 ChangeName01 呼叫 |
| nSuQuest01 | 未辨出可靠姓名 | 無交易；Quest15 時 TALK→Quest15 |

「里亞」是該句中的神名，不能直接用作神官姓名。藥水商、武器商、聊天 NPC 等無可靠原件姓名時，配置使用明確的角色名稱；不從現代版本補翻譯姓名。武器商／藥水商等角色解讀也應保留檔名與功能線索的證據層級。

## 本輪採用：原生唯讀介紹

這是 **Server 重建設計**，使用既有原件腳本，不是把所有城鎮 NPC 都認定為旅館老闆，也不是宣稱已完成原版銀行或商店。

以 `Merchant.Main(args)` 為入口，依賴僅載入 `nSuInn01` 與 `MerchantDialog`。不傳 `TYPE`、`Quest01`、`Quest04`，也不透傳任意 Client 參數。傳入各 NPC 的 `MNAME`、已校驗的 `TILE`、簡短 `GREETING`，覆蓋旅館原問候。這條路徑得到六項功能全為 false，因此只有頭像、姓名、介紹及 Cancel，不會建立 BUY／SELL／BANK／REPAIR／IDENTIFY／TALK 按鈕。

`Main` 無條件建立數個 native 參數物件、global、顏色字串，並將 `UGOLD`／`UBAL`／`UAGOLD`／`UABAL` 經 `Str2Int` 初始化。這些金額 global 在此唯讀對話路徑沒有顯示或使用；若初始化為零，僅為未使用 ABI 佔位，不能視為真實帳戶餘額，也不得據此開啟銀行功能。`UCOLOR` 沿用原件介面；原件 Main 傳第八個 color 參數，而 Create 宣告七參數，本輪不修改原件。

可達腳本呼叫閉包如下，其餘均為 native client／control／dialog 方法或 builtin `length`：

1. `Main → BuildMuttering`：插入旅館問候，稍後由 GREETING 覆蓋。
2. `Main → DoesBuy/DoesSell/DoesRepair/DoesBank/DoesIdentify/DoesTalk`：前五 false；未有 Quest01／Quest04，最後一項也 false。
3. `Main → MerchantDialog_Create`：建立視窗與 Cancel，所有服務分支均跳過。
4. `CANCEL → MerchantDialogProc`：`dialog.Dispose`，加入 `TYPE=ABORT`，`client.SendReply`，最後 `client.Dispose`。

因此不需為這條路徑提供 Quest01／Quest04、MerchantBank 或交易 dialog。這是特定參數路徑的封閉集合，不是聲稱 Merchant 的所有分支都無外部依賴。`TYPE=DIRECT` 不能替代此方案：它會呼叫此 bundle 未提供的 MerchantDirectTalk。

Cancel 是原件的關閉按鈕，不是 OK。這條路徑不產生 STATE。C6C 子類型與 native Dispose 封包順序應依既有 script bridge 分析及實測處理；XML 本身只證明 SendReply／Dispose 呼叫順序。

## 素材與 Server 邊界

背景為 `Script.dat/MerchantFrame.ypf`，按鈕使用 native `CreateImageButton` object 14。介紹的原生矩形只有 `(130,32)-(310,56)`，需限制為簡短可信文字，實機確認換行與裁切。

若使用頭像，原件公式是 `TILE-16384`，除以 10 選 `Portrait.dat/informationNN.ypf`，餘數選 object，frame 0。原件僅檢查 `0<TILE<32768`；Server 應加嚴為 `16384<=TILE<32768`，且實際驗證 archive member/object 存在。不能單憑範圍保證頭像存在。

Server 必須把對話綁定目前 owner/session、地圖、NPC 與互動距離，只接受預期的 ABORT／關閉生命週期；重播關閉應冪等。偽造 BUY／BANK／TALK 不應突入服務分支或改動資產，也不應因此讓 Client 斷線。完整交易功能仍需權威帳戶／物品資料、交易契約與獨立測試後才解鎖。

## 未採用的通用對話候選

Dialog、QuestDialog、PaperDialog、HelpDialog 是函式包，沒有獨立 Main。useLetter／useLetter2 是固定任務信件入口；PaperExample 是固定示範文字。TextInput 雖接受 Narration／TellerTile，卻呼叫 legacy MerchantDialog_Prepare、Point_GetX/Y，建立預設 hello 的輸入框並提交 Text，並非這次需要的唯讀介紹。沒有藉用新手 Life 腳本作城鎮對話。

後續驗收應集中確認六個 NPC 的可見性／站位／姓名／頭像／短介紹、Cancel 與再次交談、移出視野再回來，以及關閉後仍可移動／重登。銀行、購買、修理、改名與原版任務進度均不列入本輪完成項。
