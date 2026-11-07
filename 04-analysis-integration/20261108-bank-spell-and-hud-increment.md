# 可見NPC、Spell分類、資源HUD與銀行增量

2026-11-08。此頁整合本輪可開發與可測內容；不包含私有Server實作、帳號資料或原始素材。

## 使用者需求與問題來源

- 使用者要求目前NPC只要畫面點得到即可對話，不再要求走近兩格。這是使用者政策，見[可見NPC契約](20261108-visible-npc-dialogue-policy.md)，不是分析出的原服距離。
- 使用者要求法師魔法放入Spell分類。本輪S62改為kind0，以kind／slot共同追蹤已發技能；普攻和其他已接職業技能保留kind1。快捷列舊分類的過時意圖不施放、不斷線，需從Spell重新拖曳覆蓋。
- 使用者截圖顯示上方MP／SP110/110但施放被拒絕。權威MP2、SP100，真正顯示錯誤來自S08色彩欄多寫一個byte，見[原件更正](20261108-native-status-u24-and-hud-correction.md)。不可再沿用full61B／u32色彩舊基線；正確為full60B／u24色彩，當前值起點62、錢包90。
- 使用者要求測試期間持續開發其他項目，因此本輪另實作既有規劃中的銀行貨幣服務。銀行原生操作來自[同版Script與UI契約](20261108-native-bank-currency-ui-contract.md)，持久規則來自[Server重建設計](20261108-wallet-bank-authority.md)。

## 銀行可獨立實作子集

五城role=Bank角色使用原版Merchant主程式、MerchantDialog、nSuBanker01、MerchantBankDialog、MerchantBankDGDialog、MerchantBankWGDialog、ItemsDialog閉包，啟動先核對原件SHA及strict CP950 CRC。跨城重用此銀行腳本為明示重建綁定，不宣稱五城原版服務對話完全相同；NPC位置與外觀仍按各城既有來源標示。

1. 初次點擊只對同圖revision、C35已提交、有效World lease、Server已投影且目前可見的銀行開S44。Params包含TILE／MNAME／GREETING／UCOLOR，以及真UGOLD／UBAL與各自剩餘可加入容量UAGOLD／UABAL。
2. Client先以TYPE=BANK表示本地選單；選存款／提款送STATE=DEPOSITGOLD／WITHDRAWGOLD。Server用新context回S44 TYPE=BANK及該STATE，建立金額輸入；舊context加入有界已關集合，晚到Dispose／重送不執行交易。
3. 金額確認C6C可只有STATE與U，不得強制要求TYPE；若有TYPE必須為BANK。以Server發出的當前context與存提款階段驗證，不信Client自稱銀行、帳號、餘額、價格或手續費。只接受正整數1..1,000,000,000，拒絕負數、零、非數字與溢位。
4. 每個金額prompt保存economy revision及Server operation ID，交易在同一durable transaction驗owner／lease／已提交載圖與CAS，再原子移動錢包／銀行餘額及寫audit receipt。資金不足或上限拒絕不得扣款；CAS改變重讀權威快照，不自動重試扣款。
5. 成功、業務拒絕或不支援的物品操作均以新S44回當前權威餘額，必要S08投影口袋錢；不回放舊receipt快照。Client銀行Script會樂觀修改本地數字，故失敗也必須恢復真值。沒有使用臆造S2F／S42成功碼。
6. STATE=ABORT或TYPE=ABORT結束操作，Dispose／cleanup沿可見NPC對話的授權及冪等政策。已關context延遲回覆不再次扣款。原生C6C沒有可靠交易nonce，不能宣稱可辨識任意跨新prompt歷史重送。

物品存入／取出尚未實作，收到相應STATE只恢復銀行選單並保持餘額，不建立假倉庫或吞物品。商店買賣、旅館、原版費率、全物品資產流程亦未完成。

## 持久化及測試環境

正常角色首次資金讀取建立0／0，不發錢。只有明示隔離Playground環境會以固定可信event一次發1000測試金；重登或重啟不重發，原有資金與其他進度保留。零手續費、錢包與銀行各10億上限為目前重建規則。

新增錢包／銀行狀態與操作收據兩表。既有SQLite缺表升級沿既有一致性備份流程，保留帳號、角色、技能、資源、位置與管理金鑰。沒有直接修改使用者執行中的資料庫或重啟其遊戲。

Web新增查詢Server資源，明確顯示HP／MP／SP／BP目前值與上限；補滿成功後也顯示真值。這個讀取與既有補滿入口均需管理金鑰、Development及loopback，不把HUD假滿當作實際資源。

## 驗證與下一輪

完整.NET／SQLite回歸 **561項通過**，包含40種新增NPC可見性情境、貨幣Domain／Store、銀行Host流程與獨立原生資源offset測試。已加入截圖數值120／2／100的舊錯位重現：原編碼得到0／110／110，修正後得到120／2／100，沒有免費補滿掩蓋。

獨立真TCP已核對法師Spell分類、四格遠程、原生u24資源游標及Web補滿；銀行核對七份原件Script身份、存250／提100後850／150、錯誤金額／不足餘額／物品拒絕、取消、舊context、重登位置與一次測試金。以上均為模擬peer，**HUD實際畫面、Spell快捷列、遠距點NPC及銀行GUI尚待使用者驗證**。

下一開發批次優先商店商品清單／可信價格／原子買賣及正式資源恢復來源；沿A-013、A-007既有分析補原生UI語意，不用Web或後端測試冒充原版服務已完成。技能原版清單、BUFF／歌曲／詠唱與其他職業特色仍保留待辦。
