# A-027 / roy1：C02 身分來源、預建帳號驗證與原生創角入口的 BIN-first 研究

日期：2026-10-31。樣本：原版 Asgard.exe，PE32/x86，ImageBase 0x400000，SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。Profile TW-seed0-local-v0.1。證據 ID ev_a027_20261031_asgard_identity_static；本輪靜態反組譯 observed-static，不冒充原伺服器、完整 UI 或原 Client 雙機實測。依 A-EVIDENCE-HANDOFF-v1 評定：**研究範圍 integrated / handoff partial / implementation_ready=false（原生預建帳號認領路由） / native_client_validation=not-run；已證 codec 與負面安全規則可交 DEV。**

## 一、研究結論：有哪些真憑證證據？

**A-027 的安全問題不能以 Client UI 曾經做輸入檢查來回答「已驗證帳號」。** 原版 C02 writer 只把一批 UI 文字與 region 尾欄送網路；本輪沒有找到 C02 帶既有 C03 身分 token、Server challenge/nonce、已簽名證明或其他可獨立證明預建帳號所有權的 Client 資料流。這不是「證明原服沒有驗證」：是由目前可核對的 Client code **不能證明預建 Account 的認領授權**。原生流程原本可能屬 NewUser/註冊而非管理員預建帳號創角。若 Server 只檢查 C02 第一欄等於某個已存在帳號名稱就回 S02(status0)，**攻擊者可冒用該帳號**，違反 R-025。

## 二、重現位址、欄位與證據強度

| VA | BIN 可證內容 | 對語意的限制 |
|---|---|---|
| 0x574170 | 建構 C02，opcode=0x02 | NewUser 物件不等同已授權的 CharacterCreate |
| 0x5742B0..0x574352 | 先兩個 string8；region=2..4 再兩個 string8 + u8，其他 region 另送第三個 string8 | 固定欄位寬度與 profile 分支是 observed；Server 不能把所有分支視為同一種帳密布局 |
| 0x4B2764..0x4B27B2 | UI 提交按鈕 +0x278，配置新 C02 並持有於 Dialog+0x58 | 由 **NewUser UI** 開始而非必有已登入 C03 session |
| 0x4B27B5..0x4B27F2 | UI 控制 Dialog+0x26C → C02 packet+0x24，UI 控制 +0x270 → C02 packet+0x224；都複製最多 0xff code-unit buffer | 對應 serializer 透過 +0x0C subobject offset 看到 +0x18 / +0x218；來源確實是本地 UI 文字 |
| 0x4B27F7..0x4B2811 | UI 控制 +0x274 的文字讀到 **stack-local** 暫存 | 此確認用文字沒有直接作為固定前兩個 C02 欄位傳送 |
| 0x4B2825..0x4B2856 | region=0 時查 widget ID 0x0A；依狀態可清零或寫 C02 內 +0x424 | 非 region2..4 的第三欄有 UI 條件；不能一概命名成密碼確認 |
| 0x4B2858..0x4B28CD | region=4 讀 widget ID 0x17/0x18 到 packet+0x624/+0x822；其他非0 region 使用 0x0F/0x10 | 對 region2..4 的 C02 field3/4 來源已連到 UI widget；region=1 亦走此 UI 邏輯，但其 writer 是另一 branch，**可能有版本/布局差異，需保守標 unknown** |
| 0x4B28D2..0x4B28E0 | 取全域 0x66D110+0x219 的單 byte 放到 C02+0xA22 | 不是帳號 token 或可信身份簽章的證據 |
| 0x4B1A30..0x4B1A83 | 檢查 C02 第一 UI 欄位文字長度：region0 直接 true；其他 region 經 0x550910 取字串、與全域 0x91FED0 的最低限度比較 | 這是 Client 格式/長度 gate，**不是驗證此帳號已預建且登入者是 owner**；原生長度單位不宜推作 UTF-8 bytes |
| 0x5B4A62..0x5B4A93 | 以 UTF-16 word 逐一比對兩段 NUL-terminated 字串，返回 -1/0/+1 | 明確是字串相等檢查，**不是密碼 hash / Auth Server 驗證** |
| 0x4B28FD..0x4B2916 | 將 C02 packet+0x224 的第二欄與 UI+0x274 stack-local 比較；只有返回0 才走後續確認/送出 | 第二欄與 confirmation control 精確對應，**高度符合密碼+確認密碼 UI**，但沒有原生標籤/原服驗證證據，不宣稱其已用於 admin-provisioned password |
| 0x4B2918..0x4B2953 | 字串相等後仍有額外 UI 條件（0x535590、0x55F680、0x42C8F0），符合才進 0x4B2360；否則顯示提示 | 不能因為第二欄相等便跳過條款/其他控制條件 |
| 0x4B2983..0x4B2A37 | 不相等時保存 UI+0x270 為 focus target、建立提示 widget | Client 本地欄位不符會提示，不等於由 Server 拒絕 |
| 0x4B2A3C..0x4B2ADE | 第一欄長度/規則不符時設焦點至 UI+0x26C 並建提示 | 僅輸入合法性，非憑證 |
| 0x4B2360..0x4B23C7 | 配置含 callback=0x4B21E0 的確認 Dialog，並對不同 region 使用文字/欄位生成確認資訊 | UI 經人工確認才觸發實際發 C02 |
| 0x4B21E0..0x4B22A9 | 事件1且 C02 packet 在 Dialog+0x58 才送 C02（0x5788A0），設 state 0x1D | **未見之前透過 C03 驗證的必需條件** |
| 0x4B2340..0x4B235B | 此對話 callback 只接受 opcode0x02 的 S02 | 不能以其他一般登入成功回覆當作 NewUser 身份確認 |
| 0x4B1D60 / 0x4B1F46..0x4B205F | state0x1D 收 S02(status0) 後送 C04 五 u8，改 state0x1E | **這只是 Client 行為**；原服何時合法發 S02(status0) 未由此證明 |
| 0x4AEF04..0x4AEF0D / 0x4B0B60..0x4B0B6C | 上層各有一條建立 MakeInfoDialog 0x4B1A90 的 call path | 有創角/新使用者 UI 入口，但未證實 C03(已預建無角色) 必會自動轉入 |
| 0x573110 / 0x4A7D10 | 獨立 LoginDialog 送 C03：兩個 string8 + u8 | C03 是可追的身份登入入口；尚缺 C03 成功無角帳號與 MakeInfoDialog 之間的 callback 證據 |

**更正比既有 A-021 更細緻的欄位結論：** C02 field1/field2 來自兩個不同 UI 控制；UI+0x274 的比較字串不直接作為這兩個 wire 欄位。第一欄受長度 gate（非 region0），第二欄受與第三個臨時確認控制精確相等的 gate。依表單慣例可**推測** field1 為名稱/帳號候選、field2 為密碼候選、UI+0x274 為「再次輸入密碼」，但只能標 inferred；它們**不能直接被實作成確定的預建帳號憑證契約**，更不能以 UI 的檢查替代 Server 驗證。

## 三、C02 每欄對照（區分 BIN confirmed / inferred / unknown）

| C02 wire field | 原 packet +offset（serializer this） | UI 來源（Dialog/packet owner） | 已證與限制 |
|---|---|---|---|
| field1 string8 | +0x18 | Dialog+0x26C → packet+0x24 | 本地格式/長度 gate；帳號名只是 inferred |
| field2 string8 | +0x218 | Dialog+0x270 → packet+0x224 | 與 Dialog+0x274 文字做 UTF-16 相等比較；password/secret 只是 inferred |
| local comparison (not a C02 field) | 不直接序列化 | Dialog+0x274 → stack-local | 跟 field2 比較，是 UI 確認欄；不等於密碼已通過 Server |
| region 2..4 field3 string8 | +0x618 | region4 UI ID 0x17、其他非0 ID 0x0F → packet+0x624 | 用途 unknown（可能個人資訊/保護問答） |
| region 2..4 field4 string8 | +0x816 | region4 UI ID 0x18、其他非0 ID 0x10 → packet+0x822 | 用途 unknown |
| region 2..4 flag u8 | +0xA16 | global 0x66D110+0x219 → packet+0xA22 | native 值來源確定，旗標授權語意 unknown |
| 其他 region field3 string8 | +0x418 | region0 UI ID 0x0A 條件 → packet+0x424；region1 UI 分支與 serializer 不一致 | 不得假設 region1 與 region0 同義；仍須追更深版本路徑 |

以上 body 仍按 string8（編碼後 byte 數）處理；TW profile 是 CP950，但實際跨區 codepage/最大文字校驗及所有錯誤狀態待 A-001/A-020 的證據。

## 四、空角色預建帳號的最小安全論證

已知規格要求 R-025：**Account 只能由授權後台建立，Client 只可登入既有 Account**。因此凡是從原生 NewUser UI 未認證送出的 C02，均不得在 Server 授權 Account.Create、ClaimAccount、Character.Create、TransferGrant 或「S02(status0) 繼續 C04」；因為回 S02(status0) 會觸發後續 C04，而不是 harmless ack。

原版前置狀態本輪未找到能把**C03 已通過的 Account 身份**帶進 MakeInfoDialog/C02 的證據，C02 封包本身亦未找到可證的既有登入 token/nonce。即便 field1=已預建 account name、field2=密碼，仍需在 **正式確認 field2 的原始用途、驗證方法、帳號繫結與 native UI 可達性** 之後才能開放原生 C02 認領。切勿僅依名字、角色不存在、UI 編碼合法或某個尚未證實的 flag 開放權限。

Server 提供的**設計級 fail-closed policy**：

1. Incoming C02，僅解析其有證欄位/region 結構、去識別記錄 failure code。缺確證的 native compatible 身分路徑 → NO_AUTH_CLAIM（不回 success、不寫任何 Account/Character/lease/Grant）。
2. 若後續原生證據支持 C02 中含「真正的預建 Account credential」：由 CredentialVerifier 驗證帳號已存在、密碼/狀態有效（避免 timing/name enumeration），建立 server-side AuthContext(account_id,connection_generation,expiry)。C02 名稱欄位不可自動等於被授權 owner；帳號、憑證與 server-record 結果必須同時符合。
3. 若證明原生 Client 可由 C03 已登入無角帳號進入 MakeInfoDialog：C02 必須與**同個已驗證 session** 的 account_id 對應，禁止跨連線、跨世代或從 pre-auth C02 自行 claim；需保留 Client UI 原生線路證據。
4. 驗證成功才可建立一次性 PendingCharacterIntent（owner/session 綁定）、在合適時機回該 UI 可以接受的 S02(status0)，然後進 C04；C04 最後提交/回覆依 A-028 的獨立結論，不能把 A-027 完成等同 A-028 完成。
5. 無帳號、錯密、停權、帳號已被他人初始化、C02 與有效 session 所有者不同、跨世代、重送/並發均 fail-closed。原服對應 S02 status/messages **unknown**，不得移植 LoginDialog 錯密 status3 充作 C02 錯誤碼。

不論使用者正確填了多少 UI 資料，**Client-side checks 本身不可信**；惡意 Client 可以直接合成封包跳過。權限只能靠 Server 身份驗證與持久紀錄，不得以 Client 提供的名字/flag 為權威。

## 五、已知 vs 未知行為矩陣

| 測試情境 | Client observed-static | 可安全交給 DEV | 原生完整路由 |
|---|---|---|---|
| C02 第1欄輸入、長度 | UI+0x26C → field1；region!=0 受 0x4B1A30 檢查 | decoder / 禁止未授權寫入 | partial |
| C02 第2欄與確認不相等 | 0x5B4A62 返回非0 → 本地提示 | Server 仍需獨立格式驗證 | partial |
| region2..4 C02 字串/flag | serializer 固定結構且 UI extended 控制來源已知 | 合成 codec fixtures | 可解析；用途 unknown |
| 匿名 C02（僅已存在帳號名） | 原 UI 可早於 C03 發包 | **拒絕 claim**、角色/帳號不變 | blocked |
| 真預建帳號、但 C03 尚未驗證身份 | 沒有已證帳號憑證綁定 | **拒絕 claim** | blocked |
| C03 有效、角色為空 | C03 login writer 已知 | Domain 保持 NoCharacter、不得擅自 issue World Grant | 原生 UI 自動轉場 unknown |
| S02(status0) in state0x1D | 發 C04、state0x1E | 只有已認證 owner/pending 才准 success | C04 final A-028 |
| 兩 Client 同名/冒用/跨 Session | Client code 不能提供強制保護 | owner+generation CAS 唯一性、禁止 account overwrite | 原服 UI status unknown |
| 非法/取消/斷線/重送 | UI 有提示及返回動作分支；原服 retry unknown | 不授權、pending expire、無持久半角色 | partial |

## 六、下游 CT 與後續精準工作

- **可立即交付**：region-aware C02 codec；欄位->UI offset 映射；第一欄長度和第二欄確認比較的 Client 靜態觀察；pre-auth 絕不寫 Account/Character，未有 credential verifier 絕不 issue S02(success)/C04/World。對照既有 CT-029..032，新增 CT-039 專門測 pre-auth ownership/fail-closed，CT-040 測 UI 控制與 serializer 對照（都是 planned）。
- **目前仍需原始材料/跟進逆向**：原生控件實際標籤/字串資源、region1/0 欄位完整作用；原服如何驗證 pre-provisioned account/password（若原流程並不存在，需轉為符合 R-025 的安全替代流程）、C03(no character) 可達 UI 的控制路徑。A-028 後續負責 C04 最終回覆、資料庫提交與登入/轉場。
- **真正的阻塞定義**：A-027 對已限定的 BIN 研究成果 status=integrated、handoff=partial，但預建帳號原生認領**實作路由仍 blocked**，不代表要等新 Server 實機才做研究；凡目前無法由 Client/BIN 證明的原服決策不可填猜測值。

## 七、可重現指令

sha256sum Asgard.exe
objdump -D -M intel --start-address=0x574170 --stop-address=0x574353 Asgard.exe
objdump -D -M intel --start-address=0x4b2700 --stop-address=0x4b2b50 Asgard.exe
objdump -D -M intel --start-address=0x4b1a30 --stop-address=0x4b1a84 Asgard.exe
objdump -D -M intel --start-address=0x5b4a62 --stop-address=0x5b4a94 Asgard.exe
objdump -D -M intel --start-address=0x4b2360 --stop-address=0x4b25e9 Asgard.exe
objdump -D -M intel --start-address=0x4b21e0 --stop-address=0x4b2370 Asgard.exe
objdump -D -M intel --start-address=0x4aeef0 --stop-address=0x4aef2e Asgard.exe
objdump -D -M intel --start-address=0x4b0b30 --stop-address=0x4b0b80 Asgard.exe

只提交位址、合成規格與去識別安全測試，不上傳原版 EXE、帳密或遊戲原始資源。
