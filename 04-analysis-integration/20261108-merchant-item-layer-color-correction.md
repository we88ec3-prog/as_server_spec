# 商店／銀行圖示染黑：LAYER與文字COLOR更正

2026-11-08。使用者實機回報同件禮服在商店／銀行為黑色，背包為白色。原始EXE SHA沿本版既有契約，本輪以REA核對Script列表繪圖，不從截圖猜RGB格式。

## 正確欄位

Merchant Script把R列參數寫入cell.COLOR、O寫入cell.LAYER、E寫入cell.EFFECT。原生列表繪製 `0x51e670` 在category0讀這三個字串：

- **R／COLOR是名稱文字顏色索引**。以 `%u` 讀取後呼叫 `0x430590(5,index)`，從原件 `0x5f3908 + index*4` 查packed顏色；index0是0xffffffff白字。不能把R設成0xffffff當作圖示白色，那會把byte索引當作RGB。
- **O／LAYER是圖示染色RGB**。讀無號十進位後，透過 `0x4fdb10` 寫入 R=(O>>16)&255、G=(O>>8)&255、B=O&255、alpha=255。它不是RGB565，也不接受由十六進位字串推測的格式。
- E仍是原生effect欄，不能因色差擅自增加效果值。

因此之前所有O="0"會產生opaque黑色染層。若要與目前背包投影RGB255／255／255一致，應用 **R="0", O="16777215", E="0"**；O十進位16777215即0xffffff，記憶體packed顏色為0xffffffff。原件無染層sentinel為packed0xffff00ff（`0x5f38a4`），Script可用O十進位16711935產生；那代表跳過染層，與明確指定白色不是同一政策。

## 表格路徑與另一個ScriptItemCell的區別

ItemsDialog表格cell經 **51e670→5193b0→4919e0→490f20**。5193b0將文字顏色交名稱繪製，將LAYER交ItemImageLib；4919e0用490f20建立物品圖示。此路徑使用Icon library2/member1 `item.tw.ypf`，不是先前獨立ScriptItemCell繪圖45cb00→491ba0→491330使用的member3 `pitem.tw.ypf`。

先前商店／銀行契約列出member3的ScriptItemCell原生呼叫雖然存在，**不能把它直接等同本次ItemsDialog列表**。本輪修正該適用範圍：兩種原生UI元件都存在，但ItemsDialog的本次色差已有明確LAYER=0證據，不需要因猜測member差異而換圖示。兩路瓶形圖示候選仍有各自原件預覽，這不更改原服物品用途的未知。

Server投影應取物品權威RGB產生O的十進位字串，名稱R只使用已核對的有限索引；不讓Client或商品資料任意越界索引文字palette。這是重建投影安全政策，不是找回原服顏色目錄。

已完成原件靜態核對；商店／銀行白色顯示、列表選中／重開及背包一致性仍待GUI驗收。沒有改Client、素材或原件palette。
