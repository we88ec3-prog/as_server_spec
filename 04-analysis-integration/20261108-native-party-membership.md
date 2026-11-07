# 原生組隊邀請、名單與管理界線（2026-11-08）

## 來源與範圍

原件 Asgard.exe SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，Ghidra 12.1.4，唯讀靜態分析。這是 A-014 的增量，補上原來未知的實際 producer、reader 與 GroupMemberDialog receiver。下列均為解密後 packet body，不含 opcode／framing；字串為台灣 profile 的 CP950 string8，長度按編碼 bytes 計。GUI 與多人連線仍需實測。

## 已證收發

|方向／opcode|body|原件依據|
|---|---|---|
|C2S 2E 邀請|`00 + name:string8`|572D30 constructor；572DE0 writer；479A20 的 HumanInfoDialog control 0x13、選中其他玩家分支|
|C2S 2E 回覆|`01 + inviterName:string8 + accept:u8 + alternatePrompt:u8`|4B4E50／4B4EF0；正常組隊框固定 alternatePrompt=0；accept=1 接受、0 拒絕|
|S2C 3A 邀請提示|`04 + commonRef:BEu32 + inviterName:string8`|589130 reader；4B78E0 建立 AgreementPane mode0；commonRef 在此顯框路徑未使用|
|S2C 3A 新增成員|`00 + memberRef:BEu32 + career:u8 + hpPercent:u8 + name:string8`|589130 → 4717B0；空列表先自行插入本機 self，再追加來件成員|
|S2C 3A 移除成員|`01 + memberRef:BEu32`|4717B0；移除 self 清空本機 roster；只剩 self 時亦縮回 solo|
|S2C 3A 隊長投影|`02 + leaderRef:BEu32`|4717B0 設本機隊長旗標、調整隊長所在列|
|S2C 3A 血量投影|`03 + memberRef:BEu32 + hpPercent:u8`|4717B0 更新對應非 self 列的 percentage；self 另有 S08 更新路徑|
|S2C 3A 職業投影|`06 + memberRef:BEu32 + career:u8`|4717B0 更新列 +208；46F810 使用 BasicString[455+career]|

S3A reader **每種 type 都先讀 type:u8 與 commonRef:BEu32**，不能省略 type4 的四 bytes。type5／7 為另一個 FindingGroup 名單：BEu16 count，逐列 string8 name + BEu32 A + BEu32 B，type7 末尾另讀 BEu16；4B78E0 → 4D1010 轉給另一個 controller，不能當成 GroupMemberDialog roster 格式。

C2E 的最後兩個 bool 不是「踢人／離隊」。4B4E50 固定最後一位為0，4B4EF0 為1，區別正常與另一類 AgreementPane；兩者共同的第一個 bool 才是接受／拒絕。正常組隊實作應嚴格使用 alternatePrompt=0，其他模式尚未證完整業務用途。

## 原生入口與接受流程

HumanInfoDialog 479A20 先依已選物件取得姓名，選其他玩家的 group control 0x13 才送 C2E op0；wire 不含 objectRef。Server 必須重新解析姓名與登入角色，不得把 client 顯示姓名當授權。

4B78E0 收 type4、且沒有 pending agreement 時，建立 mode0 確認框。4020E0 的 control2 呼叫 callback(1)，control3 呼叫 callback(0)；4B4E50 使用保存在框內的 inviterName 送 op1。4021E0 設 APct=10000 ms；402140 到期 callback(0) 並關閉，所以 native 具有約十秒自動拒絕。4B7B20 取消 mode0 亦走拒絕 callback。

這證明具備原生邀請與回覆 UI，**不代表目前 Server 已投影其他玩家 avatar**。若沒有可選的遠端玩家，不能假稱原生 HumanInfoDialog 邀請入口已能人工操作；可用受控開發 fixture 驗證 wire，GUI 還需實際 actor 與選取流程。

## 名單不必先有世界 actor

4717B0 把 name／ref／HP／career 寫成 0x20C 的本機列，再由 4704C0 → 46F810 填入 HP bar、姓名與職業文字；46F5C0 畫本機 bar 與文字。上述 render 路徑不查世界物件 registry，因此名單顯示不需要先造 S07 remoteHuman。

物件 ref 在 row 中保留供點列選取／指定技能等用途。470520 的點列操作另經目前技能 targeting／MapPane，**不能推論不存在世界 actor 的隊友可被選取、施法或跨圖互動**。不應為了 roster 顯示捏造遠端人形封包。

Server 必須在各接收者 view 中一致映射 memberRef：本機 self 的原生參照為1，其餘成員使用穩定且不碰撞的 ref；type2 leaderRef 也用相同 view。不要將持久 characterId 當 raw uint32 wire ref。

## 安全投影限制

- type0 是 **append，不去重**。不要每 tick 重送全部新增列，也不要把 self 當來件成員再加一次。
- 同一 Client 若要重建完整 roster，可先 type1(self=1) 清，再對每位其他成員各送一次 type0，最後 type2 指定隊長。這是依 receiver 推導的重建序列，GUI 待測。
- 移除其他成員應僅送本機已知 ref。type1 的 solo／縮排分支先依當時名單長度運作，未知 ref 不宜拿來試探。
- 4717B0 的新增 guard 超過13列會拒絕；這是本機程式界線，不能當原服隊伍上限／公平政策證據。Server 自訂較小上限須明示為重建規則。
- HP percentage 限0..100；career 使用已核對原件範圍。self 初建會用 currentHP/maxHP 做除法，Server 的 maxHP 必須大於0。

## 不可借用的封包與仍未知事項

C12／S58 仍是 shared member-list 系列，不能僅見 class 名稱便當 party。已核 C12 producer：
MailListDialog 4ABD90、GuildListDialog 472380、UserListDialog 552790／552850／553580／554210，另有 FriendListDialog 區域；它們不能用來證明 party leave／kick。

HumanInfoDialog 選 self 的 group control 會送 CToggleStatus（constructor575BB0、opcode1B），toggle項目2並更動本地控制；**未證此動作等於離隊**，不可直接把它轉為解散。其他選項也共用該類。

尚未證明原生 UI 的：
1. 主動離隊、踢人、解散的 C2S producer 與 wire。
2. 隊長移交的 C2S intent（S3A type2 只證 Server 可投影結果）。
3. 找隊伍 type5／7 的完整互動與 alternatePrompt=1 的業務。
4. 原服隊伍人數、邀請期限、XP／loot分配、隊長繼任規則。

Server 可獨立制定安全的 party domain 與受控管理 API，但必須把以上未接原生入口及重建政策列出；不能冒稱已還原 GUI 管理全部功能。

## 可交付的最小閉環

用真登入角色解析姓名 → 以 C2E op0 建單一有期限邀請 → S3A type4 → C2E op1 接受或拒絕 → 接受時原子更新 membership → 各 view 用 type0／2 投影 → HP／career變動用 type3／6 → Server domain 成員離開或解散時用 type1投影。拒絕、過期與重播不得產生隊伍或再次加列。

此閉環的 Server 授權、邀請 nonce／期限、單一隊伍限制、離線策略、XP／loot及持久化都是重建設計；原件只證上述收發與 UI。

## 精選證據

- `ev_0844b01932963eaf327c9e6d819b3e6067c99b12b1bbfee51a18fc0997cc7822`：C2E constructor／writer。
- `ev_ffd1f13bb03fdbecdc2103f9b2d48dc1b7847adf67c48c82e5230307c545c62b`：邀請及兩類回答 producer。
- `ev_5e5d4b0bf75c069a2f07ba8a702a6340de2f9881faf44a8f05c8e2c7b570a95b`：589130 reader、邀請顯框。
- `ev_765249e8f75009e4ef65952222ed2cec9ced8bb78fc394d05755c5d60eb6c1a0`：4717B0 roster新增／移除／隊長／更新。
- `ev_824811e3e4aab48dbef84b3aa57fab0f0873b3ee159cf65d0ab94eb591995d1f`：46F810填列、46F5C0附近 render、清除列。
- `ev_d8fdb8fc56613ae540f55d0d58f12182d5049b4d4368a4303c28c605695bd257`：C12非party producer對照。

原始完整 Evidence 與逐指令資料留在分析暫存；本頁與配套 JSON 可攜，不要求公開 EXE／偽碼／私有 Server。

## 原生普通聊天可承載明示的新 Server 指令

ChatInputDialog 的送出路徑 42DFD1 比對 Enter key 0x0D，42DFF9 讀 chatMode（+288）。42E420 的 jump table 對 mode=-1 選 42E012；建立 CSayPacket 574FC0，42E04B 寫 type=0，再由 42E16F／42E177 讀目前輸入文字，42E17E send。因此可證普通聊天是 **C0E `00 + text:string8`**。這與 ActionInventory 401DF0 固定 type=2 的技能文字完全不同。

可在此既有通道實作 `/party leave`、`/party kick <name>` 等 **Server 新增命令**，但名稱、語法、權限與結果都是重建設計，不是本次找到的原服指令。原件目前未證保留哪些斜線命令；應明確限定解析前綴，不應將一般聊天交給 shell／任意執行器。

mode1／2 並非 C0E group type：它們轉用 CWhisperPacket 578220，指定目的文字 `!!` 或 `!%d`。此處只確認分流，不因此宣稱已還原群聊／公會完整路由。

### 有界入口排除

- 對 CGroupPacket constructor572D30 的完整靜態 incoming references，外部 UI caller 為479A20、4B4E50、4B4EF0，另有 factory；已見只有邀請與回答，未見 leave／kick／transfer 專用 caller。
- GroupMemberDialog constructor4715A0 只建立13個列控制、初始化狀態，沒有 packet send；control callback470520 走選物／指定技能互動，未見管理按鈕的 C2S producer。
- `Game.ShowGroup` 在55B820與55E3C0 是使用者 profile 的保存／讀取 key；不等於一個網路請求。不能因打開組隊窗便推定要送 C12 或 C2E 其他 subtype。

這是針對已恢復函式與 direct reference 的有界結論，不是全程式「絕無原生管理入口」的證明。



## 命令執行結果的原生文字回饋

兩種已證格式可選，不能拿 S02 重建介面來充當訊息：

|用途|解密後 body|原件鏈|限制|
|---|---|---|---|
|角色聊天泡泡|S0D `00 + sourceRef:BEu32 + text:string8`|5861D0 reader；4F48A0 dispatch 的0D →4F4951→4F2140→SayObject514000→MapPane4B6450|sourceRef 必須已有 actor，本機用1；未知 actor 會進 C0C resync。未證此路徑保留聊天紀錄。|
|暫時 Server 提示|S0A `11 + text:string16`（11為hex，即type17）|582200 reader；4F497E→4F24F0；4C9190查60A7BC+17*12值1；type17→4B7FF0|不需 actor；設MPah=3000ms關閉，下一則替換前一則；GUI樣式待測。|

S0D type0不需type4的第二字串／number。4F2140只查來源 actor、建立顯文字的 SayObject，不重新建立遊戲UI；來源 actor 的0x2000狀態旗標可抑制此顯示，所以不能保證任何actor狀態都會看到泡泡。

S0A type17的4B7FF0建立短暫MessagePane並排三秒計時，既有短訊息會先關閉；另可能暫時隱藏已有訊息Pane。它沒有S02、地圖載入或角色重建。其他S0A type可能走modal MessagePane，不能任意換type。文字採CP950，S0D按string8上限；S0A雖是string16，也宜以可讀短訊息回報真實交易結果，不填過長錯誤堆疊。

這裡只證原生顯示能力；`/party`命令名稱、成功／拒絕文案仍是Server重建政策，不能標原服回覆。

### S0A 的 string16 長度補證

已保留的原件 Evidence `ev_7831105879b610b5bca559b7584b0b628e667adb9d4102d6b75e20fa628861fd`，45B890 直接讀兩個長度byte；在既有TW network stream模式（stream+10非零）用 `CONCAT11(first,second)` 組成BEu16。helper也保留非network模式的little-endian分支，因此不能把「任何使用此helper」都說成無條件BE。

該u16值直接作 `cbMultiByte`：複製恰好此長度bytes、reader cursor前進同長度，再呼叫 `MultiByteToWideChar(DAT_0066E47C,0,bytes,cbMultiByte,...)`。所以台灣profile為 **CP950編碼後byte數**，不是Unicode字數，也不是UTF16位元組數；本地轉碼後另補NUL，wire無尾NUL。

本輪選用的結果提示形狀為 `11 | byteLength:BEu16 | CP950bytes`（11是hex/type17）。S0D角色泡泡列為備選。純訊息顯示契約已靜態確認，實際GUI顯示仍待集中測試。
