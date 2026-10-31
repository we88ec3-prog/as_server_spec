# A-009／roy2 — 攻擊、傷害、死亡：原版 Client BIN-first 收發契約

- **日期**：2026-10-31。工作分支：既有 `task_a/roy2`；系統 `SYS-COMBAT`／R-010。
- **原件**：`Asgard.exe` PE32、ImageBase `0x400000`；SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。本報告所列為該版本原始 PE 靜態證據，**不是原版 Server 封包錄影、戰鬥公式、Native Client 實機**。
- **依賴**：A-008 的 S08 Status、A-024 的 C13/S5F 與 S07 物件、A-004 的可見玩家與 object ID、A-025 的教學攻擊。所有 decoded body **不含 framing / XOR / opcode**。
- **證據等級**：observed-static＝實際 PE opcode ctor、writer/reader、呼叫點；synthetic-test＝可重跑的構造/負向測試；designed＝新 Server 自訂的安全政策；unknown＝原版行為無足夠證據。

## 一、RTTI → vtable → opcode → 原始 parser/writer

本輪直接將 MSVC RTTI `CAttackPacket`、`CBattlePacket`、`SBattlePacket`、`SDamageEffectPacket`、`SDieObjectsPacket` 與 COL、vtable 和 native ctor 核對，避免只看類別名稱配錯 opcode。

|封包|原始 Native 定位|本版 decoded wire body|可信界線|
|---|---|---|---|
|**C13 Attack**|ctor `0x570A10`，`0x570A29: push 13h`；writer `0x570AC0`→`0x45AC40`（BE u32）；producer `0x55709E`、`0x557A5F`|**BE u32** 單欄，packet local +0x18|該 u32 由兩條不同遊戲路徑填入 local +0x24，尚未證為任何 map/actor ID 的完整語意。|
|**C3D Battle**|ctor `0x5711C0`、`0x5711CB: push 3Dh`；writer `0x570DE0`|**u8 subtype (0..15)**，其後依 subtype 不同：不應套固定四位元組|非 C13 的別名；用途/各 UI emitter 不全是基本攻擊。|
|**S3D Battle**|ctor `0x57C6E0`、`0x57C6EC: push 3Dh`；reader `0x57C890`、`0x57CD98` jump table|**u8 subtype (0..15)**，不同分支差異很大；詳下|不是 S13 傷害數值本體；部分 subtype 使用 string8 與 variable-count。|
|**S13 DamageEffect**|ctor `0x57DDE0`、`0x57DDF9: push 13h`；reader `0x57DE90`|**2×BE u32、u8、2×BE u16、u8 flags，後面按 bit0 選配**|至少提供效果封包資料；不能把第一個 u32 或 u16 擅自命名為 actual HP delta。|
|**S5F DieObjects**|ctor `0x57E1B0`、`0x57E1C9: push 5Fh`；reader `0x57E260`|**BE u32** 一欄|死亡事件 packet 與移除物件 S0E 分離；u32 對應 native registry 的 key 尚需 handler XREF。|
|**S08 Status**|A-008：ctor `0x586CD0`；reader `0x586D40`；Status receiver `0x53F8A0`；UI callback `0x540660`|flags 0x20＝四組 BE u32 現值（其他 flags 見 A-008）|證明獨立 Client 狀態投影，不代表 S13/S5F 一定由 S08 觸發或同包扣血。|

**注意**：C13 和 S13 方向不同但 opcode 數字同為 `0x13`；C3D 和 S3D 同為 `0x3D` 但使用不同 writer/reader。S5F 是 DieObjects，而 S0E 是 RemoveObjects。不要把 `C05` 的其他 ctor 誤標成 C3D Battle，C3D ctor 真正 push 的是 `0x3D`。

## 二、S13 DamageEffect 逐欄 Native Reader

`0x57DE93/0x57DE9D` 依次 `0x45AEB0`（BE u32），`0x57DEA7` 讀 u8、`0x57DEB1/0x57DEBC` 讀 BE u16、`0x57DEC7` 讀 flags u8。**基礎 decoded body 長度 14 bytes**：

|wire offset|type|Packet 本地欄位／證據|
|---:|---|---|
|0..3|BE u32|local +0x18|
|4..7|BE u32|local +0x1C|
|8|u8|local +0x33|
|9..10|BE u16|local +0x34|
|11..12|BE u16|local +0x30|
|13|u8 flags|local +0x32|

Flags 分支：
- `flags & 0x08`（`0x57DECC`）：**不另消耗 wire bytes**；把第一個 u32 拆成高16與低16（local +0x20/+0x24），清空本地 +0x18。此處可證「混合/packed ID representation」，**不能**由此宣告它一定是 attacker/target。
- `flags & 0x10`（`0x57DEF6`）：同理把第二個 u32 拆成高16與低16（local +0x28/+0x2C）、清 +0x1C，**不新增 wire bytes**。
- `flags & 0x01`（`0x57DF1B`）：額外 **17 bytes**，依序 u8(+0x36)、BE u16×3(+0x38,+0x3A,+0x3C)、u8(+0x3E)、BE u32×2(+0x40,+0x44)、u8（reader tail-call）。**最小/此分支總 decoded body 14/31 bytes**。其他 flags 的完整業務語意未知，不可當作命中/暴擊/治療 enum。

高風險實作錯誤：把 bit3/bit4 的拆分當成額外 4 bytes，會使後續欄位全部錯位；把可選 bit0 永遠當固定 17 bytes，會使不帶附加效果的普通 S13 裁切錯誤。

## 三、C3D / S3D subtype 多態

**C3D**（writer `0x570DE0`）：先寫 subtype u8（從 local +0x18），再用 `0x570F2C` 跳表。示例：
- subtype0：額外 u8，`0x570DFF`。
- subtype1：兩個 length-prefixed string（`0x45B1B0` writer）、u8、BE u32，`0x570E0D`。
- subtype2：一個 string8 writer，`0x570E5F`（有空值替代分支）。
- subtype4/5/6/10：額外 u8（共用/相鄰分支），部分 subtype 7/9 依不同 local byte 對寫兩 u8。
- subtype15：額外 BE u32，`0x570F1C`。
- subtype3/8/11/12/13/14：跳 default 分支、僅 subtype u8 或 native 未見額外 writer；**不能解釋為 Server 一定接受**。

**S3D**（reader `0x57C890`）：先讀 subtype u8，`0x57CD98` 16-way jump table。已核對的**安全最小解碼子集**：
- subtype1/8/12：本 reader 無額外 payload。
- subtype4/5/6/10：再讀 u8 一個。
- subtype7：再讀 u8 兩個。
- subtype15：再讀 **BE u32 兩個**（`0x57CD59`）。
- subtype3：**string8、BE u32、u8、26×u8**（`0x57CA00..0x57CA47`）。
- subtype0：先 BE u16 count，然後每列 string8 + u8；subtype2：u8 count + 變長列；subtype9/11/13/14：具多欄、字串及/或 vector 的版本分支。這些**尚未**納入安全 codec；此輪只記原件 VA，不把所有複雜變體假裝成固定封包。S3D `0x57C8C5` 只對 subtype>15 落到 default；不能將合法 0..15 直接等同於所有分支已完整驗證。

## 四、Client 觸發→送出→接收→狀態/動畫的實際分界

|步驟／觸發|C→S / native origin|S→C / Client 讀取|客戶端效應與未知|
|---|---|---|---|
|已在 World 中發動攻擊，兩條 native producer `0x55709E`、`0x557A5F`|分配 C13 並寫 local +0x24 目標候選 u32，呼叫 `0x5788A0` 發送；前置可見本地狀態/冷卻 gate，但精確 input keyboard/mouse callback 未逐層定名|Server 可能回 S13、S3D、S08、S5F；**哪些是同一擊的必要回包與順序未從單一 Client 原件證實**|不能把點擊動畫、C13 發送、命中成功與 HP 減少視為同一事件。|
|Server 通知效果|沒有由此 reader 自動發出的 C13|S13 → parser 把效果資料、flags、選配欄位放入 packet object|效果分類與受擊人資料的 UI／模型 callback 尚未獨立 end-to-end 證實；精確 miss/crit 顯示未知。|
|Server 通知戰鬥活動／提示|C3D 是另一多態 Client 命令入口，其 UI 觸發依 subtype|S3D subtype0..15 多態分支|UI dialogs/動作、雙人戰鬥同步、取消和原生成功/失敗結果不應靠 packet 名稱推測。|
|Server 更新玩家數值|此步驟無自動 C13|S08 flags 0x20 等既有 A-008 條件資料|可確定原生 Status/StatusDialog 接收/刷新，不能宣稱每次 S13 都會有相應 S08。|
|Server 通知物件死亡|Client 接收到 S5F 不代表發 C13|S5F BE u32；**並非 S0E RemoveObjects**|原生物件死亡模型/動畫/屍體留存/掉落/復活是否存在另一個 ack 尚待 handler trace。|
|不合法目標、射程超限、冷卻、已死亡、斷線／切圖|C13 只有 BE u32，**沒有 Client 宣告傷害/命中/距離/時間戳**|這些拒絕分支的專用原生 S2C error code 未證|Server 實作時得明確設計拒絕／不變更狀態／只向合法視野投影；這是 **designed**，不可宣稱原服如此裁決。|

### Combat ServerOwner 決策（均 designed；不可冒充原服公式）
1. 只允許 authenticated World session、目前 map epoch、活著且狀態可攻擊的角色提交 C13，不能信任 u32=某角色的 Client 聲稱；查同 map instance、視野、距離、武器、消耗、冷卻、正在施法或取消狀態。
2. 由 Server 將命中、暴擊、傷害、減免、HP/MP 與效果/死亡判定放在同一授權事件中處理；所有公式與數值範圍由 DEV 定義并標 `designed`。負數、overflow、超 max、空目標、移除/舊 generation 的 target 應 fail closed。
3. **同時死亡**：同一權威 combat tick 對雙方先驗證，按 Server 明確選擇的 simultaneous-resolution 契約計算兩次傷害，再提交 HP 及死亡事件；不得因通知封包先後改寫死亡真相。此為可測的**提案**，不是原版戰鬥證據。
4. 將實際命中結果與視覺事件分開：S13 是效果，S08 是 Status 更新，S5F 是死亡事件，S0E 是移除；避免把 UI 特效誤作 durable damage/kill。Server 應決定它們的 atomic outbox ordering，且切圖/斷線 generation fencing。
5. C13/S13/S5F 沒有已證同一 action nonce；不允許假設重送 exactly-once。Server 可設每 session/tick/action window 的去重與事件 ID，需對重送/雙擊/跨圖舊包、同 tick 雙殺提出測試。
6. 復活觸發、復活 S2C opcode、滿血/原地/轉圖 policy **本次沒有原版 wire 證據**，由 DEV 與後續 Native CT 分開交付，不能把再次 S07/S33 等同於已證復活 protocol。

## 五、可重跑驗證與精確追蹤

原版二進位：
```sh
python task_a/roy2/a009_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a009_combat.py' -v
objdump -d -M intel --start-address=0x570a10 --stop-address=0x570ad0 Asgard.exe
objdump -d -M intel --start-address=0x570de0 --stop-address=0x570f2c Asgard.exe
objdump -d -M intel --start-address=0x57c890 --stop-address=0x57cd98 Asgard.exe
objdump -d -M intel --start-address=0x57de90 --stop-address=0x57df90 Asgard.exe
objdump -d -M intel --start-address=0x57e1b0 --stop-address=0x57e270 Asgard.exe
```

本輪本地已執行：**原件 SHA 正確，16 個原生 VA byte pattern PASS，5 RTTI PASS，15 個合成 unittests PASS**。測試包含 C13 endian/overrange、S5F count、S13 base14/opt31/packed flags、所有截斷位置、S3D 小型 subtype 與未知/多餘 bytes fail closed。這**不是** Native Client E2E、不是原服公式或真正擊殺實測。

|證據|原件 VA / 產物|
|---|---|
|A009-E01|C13 constructor `0x570A10`、writer `0x570AC0`|
|A009-E02|攻擊 producer `0x55709E`、`0x557A5F`|
|A009-E03|C3D ctor `0x5711C0`、writer `0x570DE0`、jump table `0x570F2C`|
|A009-E04|S3D ctor `0x57C6E0`、reader `0x57C890`、jump table `0x57CD98`|
|A009-E05|S13 ctor `0x57DDE0`、reader `0x57DE90`、flags `0x57DECC/0x57DEF6/0x57DF1B`|
|A009-E06|S5F ctor `0x57E1B0`、reader `0x57E260`|
|A009-E07|A-008 S08 `0x53F8A0`／`0x540660`，僅確認相鄰狀態機介面|
|A009-E08|16 binary checks + 5 RTTI + 15 synthetic tests，工具 `a009_native_probe.py`、`a009_combat_codec.py`、`test_a009_combat.py`|

## 六、交接與結案界線

- **靜態 Client I/O 可交付**：C13，S13，S5F 的 decoded wire；C3D/S3D 子型別選擇與已證小型分支；攻擊的 native send producer；A-008 S08 狀態投影聯接；相關程式碼、測試與 CT-063/064。
- **未證**：S3D/C3D 全部複雜 subtype、S13/S5F native GUI callback 到 object registry/HP 真正連結、精確 miss/crit/受擊動畫、原版擊殺/屍體/復活/斷線處理與錯誤回覆、數學公式/同時死亡、教學怪物正式 ID 或特定技能觸發。這些不得偽稱成「原服已還原」。Server 可以自行設計安全權威與測試。
- **缺少資源檔名**：本輪沒有新增必需資源檔；`Asgard.exe` 已提供。若進一步分析原版教學怪物及技能資料，可根據 Client 已有模板先調查 `@Monster%02d.dat`、`World%02d.dat`（這是命名模板，**非已證必要的特定實檔**），不要求上傳整包圖片。
- **狀態**：`A-009 status=integrated`、`handoff_status=partial`（基本攻擊/效果/死亡 wire 已有確切靜態證據，但多態 subtype/GUI 並未完整解析）、`native_client_validation=not-run`。不是將原版 Client 上線驗收誤當 A-009 分析的前置要求；CT-063 離線子集有證，CT-064 Native E2E 仍 planned。
