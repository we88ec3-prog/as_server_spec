# NPC尚在畫面內就消失：改用原生地圖窗格邊界

## 使用者實機回報與根因

使用者回報「感覺還沒離開視線範圍NPC就消失了，出現時也是突然出現」。
這是人工畫面觀察；不是由Server測試推定的需求。

之前Server為避免Client自行裁切後無法重建，採角色X±6、Y±7的保守範圍。
它確實能做離開／返回投影，但範圍落在畫面內。相機錨點400,300時，
X差7的NPC錨點仍可在64或736附近，卻已收到Server的S0E；返回則在相近
畫面位置突然收到S07。此Server設計足以造成使用者描述的提早移除／生成。
不能把先前TCP可見集合測試通過當成視覺正確的證據。

## 原件邊界與修正契約

原件EXE身份及新REA視圖見[機讀證據](native-pane-visibility-20261101.json)。
沿[既有相機profile](appearance.md)的固定800×600 Client：地圖窗格912×672，
pane位移(-56,-36)，tile48×32。此為目前支援的profile，不推廣為任意解析度AOI。

`0x4b49f0`把pixel可視矩形裁到MAP邊界；`0x4c3b00`分別以32／48除成tile矩形。
`0x46e740`的包含判斷是左／上包含、右／下不包含；`0x4b9d80`在不包含時
走`0x4b9ce0`清除Client物件。因此不能只擴大Server範圍卻忽略Client裁切。

Server以當前權威位置、已發S04偏移與已驗MAP尺寸計算：

```text
originX = (playerX - viewportX - 1) * 48
originY = (playerY - viewportY - 1) * 32
left   = max(0, originX) / 48
top    = max(0, originY) / 32
right  = min(mapWidth * 48, originX + 912) / 48
bottom = min(mapHeight * 32, originY + 672) / 32
visible = left <= objectX < right && top <= objectY < bottom
```

除法使用原生整數截斷；mapWidth／Height來自Server已驗素材設定，不能由任意
Client回覆授權。對目前viewport8,9、遠離MAP邊緣的情況，結果是X±9、Y±10。
其他偏移會得到不同範圍，不一律套對稱距離。

所有教學NPC與練習怪共用此判斷；移動提交後做每連線集合差分。仍只在離開
時發S0E、返回發S07+S1A，留在區內不重播動畫；怪物HP、life ref、死亡延遲、
教學進度不變。切圖／回登入頁沿原有清除與重建；未修改Client或地圖profile。

## 驗證界線

新增邊界測試走東西南北、另外兩種S04偏移，確認舊±6/7範圍之外仍不提早
移除，到原生邊界才移除，反向返回只重建一次，seq重播不重建。練習怪測試
亦改走到完整窗格之外，返回保持同一life與命中audit。
測試fixture的S04相機統一改為8,9，重登完整byte向量同步核對，world位置不改。

原生Client中的移動插值、邊緣裁切及返回動畫仍需使用者實機復驗；目前靜態
公式與Server測試不能代替這項。不是新增淡入效果或原服多人視野協議還原。
本輪優先修此回報，暫緩盜賊／武道家目的城鎮候選升級，未改任何傳送目的地。

本輪363項.NET測試全部通過；真素材五職業TCP教學／攻擊／死亡重生／重登
回歸全部通過。TCP仍使用v3候選目的地，1001／3001的城鎮形態反證未解除，
此處成功只判協議與持久化回歸；不判原版城鎮身份或GUI邊緣可見性通過。
