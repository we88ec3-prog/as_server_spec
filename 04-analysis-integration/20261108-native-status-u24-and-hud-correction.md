# S08三位元組色彩欄、HUD假滿與錢包投影更正

2026-11-08。使用者回報上方藍色MP、黃色SP條顯示110/110，卻無法施放技能。Server當時權威MP為2、SP為100，並未完成補滿操作。本輪找到原生讀取寬度與Server編碼不一致的直接原因，不能用免費補滿或取消資源驗證掩蓋。

**S08 flag0x40區塊是60 bytes，色彩群組是BE u24／3 bytes。舊規格的61 bytes／BE u32錯誤，以下取代該結論。** 原件SHA、每個read call的VA／寬度／wire cursor及來源Evidence見 [機讀表](20261108-native-status-u24-and-hud-correction.json)。

## 根因與精確讀取

`0x586e8d` 呼叫 `0x45ae30`。此reader檢查剩餘至少3 bytes、依序讀三個byte，將cursor前進3；BE模式回傳24-bit整數。它與四位元組reader `0x45aeb0` 不同。回傳值存入32-bit本地欄位，不代表wire也是32-bit。

舊Server在body50..52的色彩群組多寫一個零byte，使之後所有欄位向後多一格。以HP120、MP2、SP100、BP0作合成重現：Client讀到的目前值變成0、0x78000000、0x02000000、0x64000000；HUD再向最大值截頂，因此出現HP0/120、MP110/110、SP110/110。這與使用者截圖相符；上述數字推算屬合成解碼解釋，不冒稱當次已錄到完整wire。

full block尾端已逐call重算，並非只沿用原先長度表：

|call VA|讀取|0x78 body offset|
|---|---|---|
|0x586e8d|u24色彩群組|50..52|
|0x586e97|u8能力點，擴成native u16|53|
|0x586ea6／0x586eb0|各u8|54／55|
|0x586eba|BEu16|56..57|
|0x586ec5／0x586ecf／0x586ed9／0x586ee3|各u8|58／59／60／61|

rowCount／按鍵配置相關byte仍是固定尾欄，沒有因其值而追加額外wire；另flag0x200才讀count/vector，不得混入full block。

## 正確0x78配置

所有offset均排除opcode、ordinal、加密與framing，自flags首byte算起。

|body offset|內容|
|---|---|
|0..1|flags0x0078|
|2..61|flag0x40完整資料，60 bytes|
|62／66／70／74|flag0x20的HP／MP／SP／BP目前值，各BEu32|
|78|flag0x10的EXP，BEu32|
|82／84／86／88|四個BEu16進度值|
|90..93|口袋金錢，BEu32|
|94..98|flag0x08的五個byte|
|99起|title string8，含編碼後byte長度|

單獨flags0x40的body長62；單獨0x20或0x10仍各18。完整0x78為`99+encodedString8Bytes(title)`；空title string8也占1byte。舊初始化fixture與測試若沿61-byte假設均須更正，不能用相同錯誤offset的往返測試證明原生正確。

## 上方HUD與能力窗是不同接收者

上方元件是 `HitManaStaminaDialog`，GUI resource7；`0x474c30` 從事件+0x14取得完整packet，檢查packet+8 opcode0x08，再轉入 `0x474590`。

此HUD直接讀完整packet：+0x30為fullflag，+0x38／3c／40／44為最大值；+0x7c為currentflag，+0x80／84／88／8c為目前值。bar controls0..3與數字controls4..7分別更新。`0x433f20`讀bar maximum，`0x433ed0`設定maximum時只會向下裁切過大的current，不會自動補滿。0x10的EXP／錢包沒有覆寫這段HUD資源。

能力窗由 `0x53f8a0→0x540050`更新Status欄位，是另一條路徑；本輪沒有拿能力窗證據代替HUD。parser使用子物件視圖，本地offset與完整packet相差+0x0c，兩條接收者均已對照。Ghidra此函式的stack／unaff暫存變數有不完整推導，因此關鍵欄位同時用精確指令核對。

## 錢包欄位與銀行的分界

flag0x10最後u32由reader存packet-local+0x9c，完整packet+0xa8經Status接收器存至Status+0x48c。Inventory UI `0x48aead／0x48aec3` 以它更新金額control0x20、控制錢幣拖曳control0x21；`0x464bb5`亦用它限制金額輸入。因此它可投影真實口袋餘額。銀行餘額另由S44參數UBAL顯示，不把口袋餘額當銀行存款。

更新錢包若使用單獨0x10，需同時填入目前EXP與四個進度值，避免為更新金錢而清掉其他欄位。修正後全量0x78的錢包是body90，而非舊body91。

本輪只有原件靜態／有界metadata與合成偏移重現；Client原件保持不變。開發仍須在修正後由使用者集中確認HUD與權威資料一致，不能把這份分析本身當成GUI已通過。
