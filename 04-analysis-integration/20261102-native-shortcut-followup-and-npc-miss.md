# 原生快捷技能後續封包與 NPC MISS

延續 A-004／A-016／技能分析。需求來源為使用者回報，原件證據來自 REA；
重建政策與 GUI 驗收分開記錄。對應機讀證據見
[native-miss-c65-20261102.json](native-miss-c65-20261102.json)。

## 本輪實機回報及斷線因果

使用者確認由南往北返回時 NPC 已正常顯示。這只驗證此次方向性案例，
不外推所有方向、鏡頭速度與所有怪物的可見性。
另回報空白鍵不能對空氣普攻，快捷列1對空氣普攻後斷線。

診斷副本／Server build `0fa2c0b` 的遮蔽日誌顯示：
UTC 2026-11-01 16:35:33.372 收到 C0E，body6；16:35:33.432 回送 S1A，body8；
16:35:33.437 收到 C65，body2，被列 unknown-opcode 並關線。
這證明此次關線發生於 C65，而非 C0E 未到達或 Server 未回動作。
日誌僅保留 opcode／長度等中繼資料，不含本次 C65 的實際兩個 byte。
其值與用途由原件 producer／writer 另行建立，不能宣稱已讀到當次 payload。
之後另一個連線直接送 C00 而 out-of-phase 的自動重連分支仍未修復。

## C65 原生格式與非 cast 普攻分工

`0x5779f0` 建構 CUseActionPacket 並設定 opcode0x65。stream vtable
`0x614454` 的 writer 是 `0x577aa0`，先各寫一個 u8：物件+0x18、+0x19
（完整 packet 的+0x24、+0x25）。第三個本地 mode byte 不直接寫到 wire。
writer 依 mode1..9 選附加參數；jump table `0x577ba8` 的 mode5
指向 `0x577ba6`，直接返回。因此本階段 mode5 的 wire 是兩個 byte，
不能把所有 C65 都當固定長度，也不能把它當一般兩個 byte 的任意命令。

`0x401ed0` 的 CastValue0 分支先呼叫 `0x401df0` 發 C0E kind2／動作文字，
再於 `0x401fe5` 發原先建立的 C65。本階段已發普攻 row 為 Kind1／Slot1／
Mode5／CastValue0，因此重建 subset 接受 C65 `[01,01]`。

Server 契約：

- 必須是加密、WorldReady、已完成載圖、有效 owner，以及已發普攻清單的連線。
- C65 必須恰好2 bytes，Kind1、Slot1；其他 mode／row 尚未實作，不能擴張接受。
- 攻擊由先到的 C0E 執行。C65 不再攻擊、不扣資源、不推進教學、不回猜測成功包。
- 單獨或重複 C65 不產生攻擊，避免一次按鍵被算兩次傷害。

這是目前 issued-row subset 的重建政策；不是全部 CUseAction 語意或原服回應的還原。

## MISS 素材與 renderer 的正面連結

Basic.dat SHA256：`0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96`。
slot13 `HitNumber.ypf`，offset1365116，155600 bytes，member SHA256：
`fe490176519bf79096eeb8c4fe82f4b2d0a5d31d8d7a0258d64f329abeb84502`。
YPF17／非調色盤 RGB565／36 objects；有界解析 metadata 恰好結束於資料起點6788。
object0..17 各10 frames，18..35各1 frame，actions／states／links均0。
離線檢視首 frame：0..5紅色數字，6..11藍色，12..17灰色；18..23紅色 MISS，
24..29藍色 MISS，30..35灰色 MISS。每六個object呈現不同角度／淡出階段。
素材預覽僅本地保存，不放公共 Git，也不當作正在執行 Client 的截圖。

`0x4a4b00` 在 S13 Flags bit0為0時呼叫 `0x4b6850(...,param3=0,...,amount=0)`。
`0x4b6850` 因此選 HitNumber type3／4／5；有擴充時使用0／1／2。
`0x474390` 原始指令的 `RET 0xc` 證明三個參數，不能採偽碼誤判的兩參數簽名；
第三參數是 amount，第二參數 type 存本體+0x44。
繪製介面 this 具有+8調整；`0x4738e0` 以 type*6 +動畫階段選 library0/member13
的 object。因此未帶擴充的 type3／4／5與已檢視的 MISS組相符。
amount0經 `0x473790` 得1位，`0x4736d0` 取0，對應這些單 frame 組的frame0。
**MISS 使用未擴充 S13，並非附帶 amount0 的數字傷害擴充。**

## 教學 NPC 攻擊重建政策

對已發普攻、當前 map/revision、確實已投影的設定 NPC，且距離 Chebyshev<=1，
回 S13 `ReferenceA=1,ReferenceB=NPC,Motion4,Effect0,Animation100,Flags0,Tail0`，body15。
範例 ref0x1001：`00000001 00001001 04 0000 0064 00 00`。
2026-11-02更正：先前錯記body14，漏掉reader在未擴充分支仍必讀的尾碼，
使用者實測NPC完全不揮拳；舊版synthetic/TCP通過不足以證明native可解析。
目前涵蓋設定的招募員／講師／選職與出發 NPC，不泛化玩家或任意 object ref。
最近3秒 C44 選取政策可供 C0E 普攻選取 NPC；這仍是重建政策，非空白鍵目標規則。
此為本頁初版政策，後續[首次命中修正](20261102-first-shortcut-npc-tail-school-music-and-reconnect.md)
已撤除最近選取依賴，改依當下權威位置／面向一格找目標，不需先C44或C13。
開啟對話時不攻擊；NPC miss、空揮與真命中共用普攻呈現冷卻。
MISS 不進扣血交易，不寫 MP／SP／HP，不建立 training hit或practice里程碑。
NPC 攻擊必定 MISS 的規則來自使用者回憶及本階段教學無敵政策，並非找回原服命中率。

## 空白鍵仍未解決與下一步

原件 `0x497230` 的 action2 在面前格無物件時確會呼叫 `0x5578d0(0)`，
但後者仍檢查自身狀態資料+0x0d bitmask0x1e、物件+0x288 bit0x1000、
移動階段+0x514、狀態資料是否存在，以及+0x15攻擊間隔與+0x528上次時間。
查到 target0 producer 不等於當下能發 C13；未取得執行中欄位值，不能猜是哪個阻擋。
另 `0x55a250→0x559350` 使用當下 key map 與 modifier，比對預設表也不能證明使用者當下設定。
本輪查詢先前 PID48220及同名診斷 Client 已無執行個體，沒有取得被動記憶體快照。
下一次集中測試若空白鍵仍無效，需保留 Client，在相同連線對照 C13 是否送出，
再讀上述有限狀態；不要先修改 EXE、按鍵設定或任意猜一個 Server 狀態位。

## 驗證與範圍

376項 .NET測試通過，含 C65合法／長度錯誤／未發 row／未發技能／載圖／失效 owner，
C0E後C65不重複傷害、NPC距離及不給打怪進度。五職業實際內容 TCP 均通過，
包含NPC MISS→空揮→C0E/C65→真命中／死亡→畢業及重登。這仍不是原生 GUI 驗收。
本輪未修改 EXE或使用者角色、金鑰、資料庫；城鎮仍是候選綁定，未證明原版身份。
