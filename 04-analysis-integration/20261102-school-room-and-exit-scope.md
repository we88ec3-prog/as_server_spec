# 教學地圖數、室內資源與出口的實作範圍

**後續補正**：[原生傳送入口表已找到](20261102-native-portals-and-route-authority.md)，為Basic.dat slot24 Portals.tbl；Map7有10個入口格與兩個native小地圖anchor。下方保留先前查找歷程，hover/grid來源已補證，目的MAP／落點仍未恢復。

使用者詢問目前是否只有一張教學圖，以及畫面上的門／出口是否可換圖。
目前Server候選流程為Map6招募區→Map7學校→所選職業候選城鎮；學校只接Map7一張，
Life／War／Career／Departure NPC與摩斯練習都同圖。這是重建安排，不是原版圖數結論。

核對原Map0 SHA後，實際存在00007..00038.map等多張室內候選；
Map8／9／10／11與Map7不同，離線預覽有不同家具、空間及地毯式門口。
Map12..29完整member相同；Map30..38完整member相同；Map39..43及45..54完整member相同。
這些相同檔案可支持存在複本資源，**不單憑相同就認定是教學分流或私有房間**。
具體SHA、尺寸、52件Map6..58（缺55）資料與8張新預覽覆蓋見
[school-room-candidates-20261102.json](school-room-candidates-20261102.json)。
圖片只留本地；Map8..15的非零flag共14件省略，static unsupported為0。
靜態預覽沒有NPC、動畫、碰撞驗收或已驗證傳送點，不可從地毯方向猜目的MAP／座標。

待解析：

- 原教學每位NPC與哪個MAP綁定、是否依腳本階段逐間移動。
- 門口的觸發格／範圍、目的MAP及出生點，是否需要任務條件。
- 是同圖鏡頭移動、換房間還是換map，須以實際map ref與C35屏障辨識。
- Client資源是否含足夠出口關係，或精確目的地原本完全由Server配置。

現有Script未給出足以覆原上述全部連線的原服表。若需重建出口，應以明確
來源map/revision、Server已提交位置、任務進度及唯一目的地授權，沿既有S15/S14/C35
切圖屏障提交；不直接接受Client指定目的地，也不只靠走近門就算畢業。
這些是Server規劃，未在本輪接上門口，不改使用者位置，也未宣稱原版只有一張學校。

## 使用者補充的左側地圖與出口游標線索

使用者明確補充：左側地圖資訊可見點位，游標移到可切圖點位會換圖案。
這是待定位的native UI觀察，不只是對門的外觀推測；不能因純MAP尾段未見目標
就斷言Client不含出口資訊或所有出口只在Server。

本輪Map6..12逐byte範圍核對：前段u16 block全0，tile flags僅0/1/16/17的子集，
7B物件段後的8B／16B記錄數均0，解析恰到EOF。見
[school-map-exit-check-20261102.json](school-map-exit-check-20261102.json)。
這只表示這些段沒有額外可直接讀取的目的MAP／XY記錄，不排除其他本地表或Server metadata。

REA已追到MiniMap `0x4d1080→0x4d0ea0` 使用 `MinimapLocation` 類別資料，
`0x4d0370` 從文字記錄取三個整數，存為u16/u16/i32；繪圖依第三欄1/2/3選顏色。
前兩個數值作標記位置。這支持**座標／顯示類型**，尚未支持第三欄是目的MAP。
另有從MapData輔助grid標記位置的路徑，不能與MinimapLocation混為同一來源。
`MinimapLocation`會經Metainfo查詢；精確cache／Server資料來源與出口hover判斷仍待追。
可攜視圖：[native-minimap-exit-leads-20261102.json](native-minimap-exit-leads-20261102.json)。

本輪稍後確認診斷Client已不存在，未取得該點位的畫面／游標快照；沒有另開遊戲。
下一次Client保留時應定位實際點位、記當前map與tileXY、觀察hover而不先點擊，
接著連到native cursor分支及其資料讀取。取得目的地的正面證據前不猜接房間。
