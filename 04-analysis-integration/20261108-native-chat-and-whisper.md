# 原生聊天、密語與隊伍頻道（2026-11-08）

## 來源與界線

這是 A-014 與 [原生組隊增量](20261108-native-party-membership.md) 的補證。原 EXE SHA-256：`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；Ghidra 12.1.4，原件唯讀，沒有啟動／附掛使用者 Client。下列為解密後 body，opcode 不含在 body；台灣 profile 的 string8 是 u8 **CP950編碼後byte數**，string16 是 BEu16 編碼後byte數，均不含尾NUL。

**原生支援靜態確證，不等於本輪GUI已驗收。** Local半徑8、Whisper送單人、Party送所有在線隊員，是本輪 Server 重建政策，不是反編譯出的原服範圍或權限。

## C2S 可用 ABI

|opcode|body|已證 producer／用途|
|---|---|---|
|0E|`kind:u8 + text:string8`|普通聊天 kind=0；ChatInput Enter 分支42E012→574FC0→42E04B固定寫0→42E177複製輸入→5788A0送出|
|0E|`02 + actionText:string8`|401DF0 ActionInventory 技能前導文字；**不是普通聊天或聊天頻道2**|
|19|`kind:u8 + target:string8 + text:string8`|578220 constructor opcode19；5782D0依序寫kind、target、text|
|19|`00 + playerName:string8 + text:string8`|ChatInput密語模式3，由42E103起複製所選姓名，kind=0|
|19|`00 + "!!":string8 + text:string8`|ChatInput組隊模式1；須本地GroupMemberDialog count>0才送|
|19|`00 + "!n":string8 + text:string8`|公會模式2的n=1..3；本輪可先不接guild功能|
|19|`01 + blockedName:string8 + empty:string8`|42FE00收到S0A type0後的訊息黑名單回覆，不是使用者傳話kind|

普通聊天 Enter code42DFD1檢查key0D。模式在來源不同的base／observer view有不同位移，故此處只記語意值：-1普通、1隊伍、2公會、3密語，不以混合this偏移推導wire欄位。

### 隊伍／公會不是猜字面名稱

42E4EC～42E527把模式改為1，讀 BasicString[89]「組隊:」。其送出路徑42E057檢查隊伍名單，再以literal「!!」作C19 target。這把UI標籤、群組存在檢查及writer串起，足以將 **kind0／target!!** 對應隊伍發話。

42E52C～42E5C7把模式改為2，subindex循環0..2，依次讀BasicString[482..484]「和睦公會」「戰爭公會」「一般公會」；送出時格式字串「!%d」，值為subindex+1。因此!1／!2／!3不是隊伍子組。這只證本版Client目的標記，未還原三種公會的Server會員／權限規則。

原件 Basic.dat SHA-256 `0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`；member index2 `BasicString.txt`，offset190844、14810bytes，SHA-256 `fa92f7a3cf544ff9e141d98620943b362e2d3dcc6e327878a818ebaa6ac3123b`。按UTF16文字中的顯式數字key讀89／482／483／484，不能把實體行號當key。

## Actor-free 的原生聊天歷史

**建議可實作的承載：S0A type18（decimal，hex0x12）+ string16 text。**

430480從packet+8判opcode：0A→4304BD→42FE00，0D→4304B1→42FDB0。42FE00是ChatInput history的SMessage receiver，獨立於MapPane短訊息handler。

S0A type18在固定policy表（60A7B8、stride12）為color FFA0A0FE、modalFlag=0、styleFlag=0。42FE00查4C9190(type)為0後，查4C91A0(type)為0，直接42FA90(text,color,0,0)，不查世界actor、不解析訊息內姓名、不進styled-text轉換。42FA90將文字折行，追加至本地history列，總視覺列接近500時移除舊列，並更新捲動。

因此 Server 可以回：
`12 | CP950ByteLength:BEu16 | "[Party] CanonicalName: text" 的CP950bytes`。

**這是選用已證原生plain-history槽來承載Server訊息；[Local]／[Whisper]／[Party]及文字樣式是Server自訂格式，不宣稱type18就是原服隊伍頻道。** 發送者必須由認證session取得，再由Server拼接，不能讓client用text前綴冒名。訊息樣式／保存與使用者option的實際觀感仍須GUI集中測試。

### S0A其他type

|type（decimal）|原件處理|使用界線|
|---|---|---|
|0|42FE00會按option走首個「>」之前的姓名解析、密語歷史／黑名單檢查，再追加；plain color FF9EECEE|若採此格式，`Name>text`不要求空格。不要將channel前綴塞在Name前，會改變姓名辨識。|
|1..7、9..11、13..15|modalFlag0、styleFlag1，經5411A0等styled-text解析後追加|本輪不用未知markup格式來承載使用者原文；不能只見type便命名頻道。|
|8、16|modalFlag1|會走另一個MessagePane分支，不能當一般history。|
|17（hex11）|modalFlag1；MapPane特例4B7FF0建立三秒短訊息|下一則替換前一則，**不進42FE00 history**；適合簡短命令結果，非完整聊天。|
|12、18..20|modalFlag0、styleFlag0|可走plain-history；本輪固定選18，不任意依顏色命名原版用途。|

S0A type0若找到被封鎖的姓名，42FE00送C19(kind1,name,empty)並停止本次追加。這是被動拒收回報，不能當原生聊天傳送。type18不執行該姓名解析分支；若採用它，Server需自行實作訊息拒收／封鎖政策，不能宣稱Client原生黑名單已被完整保留。

## S0D 的顯示與 type4 界線

5861D0讀 `type:u8 + sourceRef:BEu32 + text:string8`；**僅type4**再讀 `text2:string8 + number:BEu32`。其他type不能多塞尾欄位。

MapPane dispatcher4F48A0→4F2140先查sourceRef世界物件，再建立SayObject514000，未知物件可能觸發C0C重同步。因此不能把所有跨玩家訊息用sourceRef=1假裝自己講話。42FDB0另可按type policy把text送42FA90 history，但這不消除MapPane同時查actor的副作用。

type4的SayObject路徑將text2交給「SayLocation」metadata，保存位置／互動相關資料；完整number用途與原服觸發來源尚未確證。它**不是已證「senderName+whisperText」格式，也不是免actor的密語替代**。無原版對照時不要編造type4數字或拿它繞過remote avatar投影。

## 可實作閉環與未知

Server可嚴格解析C0E kind0、C19 kind0。target!!依當下權威party取得接收者；其他有效玩家姓名走Whisper；!1／!2／!3保留為已識別但未實作公會意圖，拒絕時以S0A17回報，不斷線、不冒充普通姓名。C19kind1可識別為Client拒收回報，但Server持久封鎖列表尚需獨立需求／協定，不用此包直接宣告完成。

本輪將Local半徑8、Whisper單人、Party在線隊員、發送速率／內容上限／回音規則標為重建政策。跨地圖、離線密語、封鎖同步、原服所有訊息type／顏色用途、C0E其餘kind、S0D4位置數字與三種公會完整規則仍未知。

## 精選證據

- `ev_a0af909838ada8e380233a919896494c5324dca2d7a32bc2bc5eb5ed7b10563c`：578220／5782D0 constructor與writer。
- `ev_b4d93d6e1f402e709d6c41847a1c437f7956a401eac092a464eb231c1f8d98c5`：42FE00／42FDB0 history receiver與type0拒收回報。
- `ev_5ad0207c5ab1f51587e40300ab4c53fcede722e1db9c42d547f68c254bad9930`：type policy accessors與42FA90追加。
- `ev_e471fe5440d1dd5a559f2ce68ccf4b11deb2f97001e05f9179f900436ef1ee81`：精確訊息policy表。
- `ev_7831105879b610b5bca559b7584b0b628e667adb9d4102d6b75e20fa628861fd`：45B890 string16按encoded-byte count讀取／轉碼，沿用既有TW network模式BE證據。

完整逐指令與可攜快照留在分析暫存；本頁不公開原件、完整偽碼或私有Server。

後續：[Server拒收與原生黑名單邊界](20261108-chat-ignore-and-native-blacklist-boundary.md)補上持久化拒收；本頁未完成項保留當輪歷史，未把原生本機名單同步宣告完成。
