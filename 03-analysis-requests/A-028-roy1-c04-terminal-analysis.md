# A-028 — C04 後的 S02 結果、取消訊號與重登/轉服（BIN-first）

- 日期：2026-10-31；分析者 roy1；工作分支 `task_a/roy1`
- 原件：使用者提供的 `Asgard.exe`，PE32 x86、ImageBase `0x400000`，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`
- 分析方法：對原始 EXE 執行 `objdump -D -M intel`、用 PE section mapping 驗證 vtable/字串與 3..31 status 跳表；對照 A-021/A-027 先前研究。**未使用原 Server，亦未跑原 Client E2E。**
- 證據 `ev_a028_20261031_asgard_c04_response_static`。結果：`integrated`（已查得原生 Client C04 後的 S02 已知分支），`handoff_status=partial`，`native_client_validation=not-run`，`native_creation_commit_ready=false`；**分析研究已交付，原版 Account/Character 完整可用路徑仍受 A-027 原生驗證缺口阻擋**。遵守 A-EVIDENCE-HANDOFF-v1，不以新 Server/CT 未完成作為逆向失敗。

## 1. 新的關鍵結果

**C04 後並非直接 S03：Client 在 C04 發出後把 MakeInfoDialog `state` 設為 `0x1e`；再收到 S02(status0) 時會走 `0x4b206b` 的本地 UI 完成分支，而不是第二次發送 C04，也未在這個 callback 中直接建立 S03/C10/world connection。** 因而不能把 A-021 第一個 `S02(status0)` 當作 Character 已成功提交，更不能把收到 C04 當作 Server 已保存 Character。

另一項新原生證據：**S02(status≠0) 分支會建立並發送 opcode `0x15`（C15 / CancelNewUser），然後 `state=0x1f`**。C15 constructor `0x5715f0` 的 `push 0x15 → 0x578600`；rdata at `0x6136a4` 是 `./packet/ccancelnewuser.cpp` 的 UTF-16 debug path，vtable `0x613690` 第二 method `0x5716a0: ret`，因此 C15 目前可證的 body **0 bytes**（仍須走 C2S 既有 binary transport 的 ordinal/codec，勿誤認為 raw plaintext 例外）。這是 Client 對 S02 非零回覆的行為，不代表 Server 原本對每個錯誤一定「已撤銷資料庫草稿」或對 C15 有什麼 reply。

## 2. 可稽核原生位址

| VA / 範圍 | BIN observed-static | 規格意義 |
|---|---|---|
| `0x574370` → `0x574420` | C04 NewUserInfo，serializer 五個 u8 | `sex,hair,color_r,color_g,color_b`（原 profile）；角色合法集合仍待 A-003 |
| `0x4b1f46` | S02 status0 分支檢查 `[Dialog+0x4c] == 0x1d`，不相符轉 `0x4b206b` | 分辨 **C02 中途成功** 與 **C04 後 success**，不能用同一個 ACK 解釋 |
| `0x4b2031..0x4b205a` | 把 UI 性別/髮型及 `0x66422c` RGB 投影五 byte 寫入 C04，`0x5788a0` 送出 | 這是 client-generated C04，無 DB commit 訊息 |
| `0x4b205f` | `mov dword ptr [esi+0x4c],0x1e` | C04 已送出的 local state |
| `0x57dbc0..0x57dbde` | S02 parser：`u8 status` + `string8 message` | 請保留原始 status，不把登入錯密 status3 套用為建角錯誤 |
| `0x4b1da9..0x4b1ded` | status3..31 查 `0x4b21bc` byte index，再跳 `0x4b21a8` target table | 只是 focus/control 與 UI 錯誤分派；不是官方錯誤碼文字表 |
| `0x4b1e0d..0x4b1e27` | 若 local state=0x1e 且 region=3，分支略過一般 message display 建立 | 特定地區/階段的提示處理不同，不等於沒有失敗或無需 C15 |
| `0x4b1ee9..0x4b1f34` | `status !=0` 時構造 `0x5715f0` 的 C15，`0x5788a0` 發包，local state=0x1f | 有證 **S02 非零 → C15 + state1f**；原因/字面錯誤描述仍 unknown |
| `0x5715f0..0x571642` | 封包 constructor `opcode=0x15` | C15 類別 |
| `0x613690`, `0x61369c`, `0x5716a0` | vtable method 綁定到 `0x5716a0: ret`，rdata path `ccancelnewuser.cpp` | C15 serializer 為空 body，wire frame 長度由 transport 加 opcode/ordinal |
| `0x4b206b..0x4b20b5` | S02 success 且非 state0x1d 時從 UI `+0x26c` 取文字，call `0x434cc0`（widget 虛擬操作）、操作控制 0x0b/0x0c/0x0d/0x07 | 可證 UI local transition，**此段沒有立即發出 C03 或 S03** |
| `0x4b20ba..0x4b217a` | 成功的 UI 分支 region=3 還會建立與填充另一個視窗/提示組件 | 完整畫面語意、是否手動轉登入 unknown；非 World transfer 證據 |
| `0x4b14b0..0x4b1553` | Dialog 的另一路 UI popup handler，清 `+0x54`，設 state=0x1f | state1f 含 UI/彈窗清理行為；不能說是已保存角色 |
| `0x4b2340..0x4b235b` | MakeInfoDialog callback 僅將 opcode0x02 派至 `0x4b1d60` | 不應把所有通用通知/登入 packet 轉成建角成功 |

### S02 非零 status 對輸入焦點的靜態對照

`0x4b1da9` 先取 `status-3`；在 3..31 範圍使用 29-byte `0x4b21bc` index 表。對有專門 focus 的值，以 section bytes 和跳表核對：

| status | target | local focus |
|---|---|---|
| 3 | `0x4b1dc3` | `Dialog+0x26c` |
| 4 | `0x4b1dd9` | `Dialog+0x26c` |
| 17 | `0x4b1dce` | `Dialog+0x270` |
| 18 | `0x4b1de4` | `Dialog+0x26c` |
| 26 | `0x4b1dd9` | `Dialog+0x26c` |
| 31 | `0x4b1de4` | `Dialog+0x26c` |

其餘 3..31 對應 default `0x4b1ded`；status1/2 或超出表範圍也略過這個 focus 分流。**只有焦點有證據，具體「帳號已存在／密碼錯誤／名稱太短」的文義未證**。status!=0 仍會走 C15 + state1f 的後續邏輯。

## 3. 從 C02 至 C04 後的已知狀態機（Client observed-static）

```text
NewUser / MakeInfoDialog (state 0x1c；是否 C03 後可達 UNKNOWN)
    C02 發送 -> state 0x1d
    收 S02(status=0) in 0x1d
      -> C04(5 u8) 發送 -> state 0x1e
    收 S02(status=0) in 0x1e
      -> 0x4b206b local UI transition; region3 additional UI
      -> NO immediate S03/C10 in this callback, final navigation UNKNOWN
    收 S02(status!=0) in 0x1d 或 0x1e
      -> status-specific focus/message (except guarded presentation branch)
      -> C15 (opcode0x15, empty body) -> state 0x1f
    已在 state 0x1f/其他 state 的後續 UI/cancel、再次 C02
      -> 需在後續 UI 操作/原版實測確認；不可假造自動重登
```

重要：原版 `S02(status0)` 對話框 local state !=0x1d 的路徑不僅可能含 0x1e，**不應把此成功分支當成全域「C04 已建角」證明**；它是 UI 分流。S02 status0 in 0x1d 已足以發 C04，但若原服預建帳號驗證尚未證實，Server 不能向任意 pre-auth C02 發送它（A-027 security decision）。

## 4. Server 開發交接：角色提交時機與錯誤恢復（designed）

本次 Client code **沒有**原始 Server DB commit call，也沒有原版角色「已持久化」可驗證旗標。對具可信 owner/AuthContext 的**日後可驗證創角流程**，可先交付以下不依賴猜測狀態碼的 Domain 合約：

- **前置授權**：Account 必須由管理員預建，且已核對 owner 與 credential / session generation；在 A-027 原生路由未解前，對外 C02/C04 仍 fail closed，任何 C02 字串或 S02 status 都不能直接建立 Account/Character。
- **建角意圖**：只有可信 pending account+generation+expiry+request_id 並通過合法名稱/外觀/唯一性，才能接受 C04；沒有 C02 綁定的 C04、另一條連線/舊世代的 C04、停權帳號都拒絕且無持久副作用。
- **提交順序**：**設計選擇**：於一個 DB transaction 中以 unique(account_id)（本 profile 一角色的保守策略）與 unique(character_name) 等約束寫入 Character+Appearance；完成 durable commit 後才回此 UI 可接受的 S02(status0)。這個選擇不是原伺服器 commit 時點的靜態證明。
- **重試/重送**：若回覆遺失，重試同 owner+same intent 必須返回已存在結果而不新增第二角色；改變 body、cross-owner、timeout 一律拒絕／走明確已授權重新嘗試，不覆蓋既有 Character。
- **錯誤與 C15**：收到原生 C15 可標記/取消當前 generation 的未提交 pending 草稿，已提交 Character **不可因晚到 C15 撤銷**。不要將 Client 收到非零 S02 時回送的 C15 當作原服 DB rollback 的證據。
- **成功後**：原版 S02(success) 的 UI 分支不等於 S03 transfer，避免 Server 在新帳號 UI 成功時盲送 S03 造成畫面/連線錯序。何時走回 LoginDialog C03、角色恢復與 World Grant 仍需 UI 入口／可重現端對端測試；SCN-009/010 保持分析所需門檻。

不支援的原生 status message/提示不應亂填。登入錯密的 S02 status3 是**別的 LoginDialog profile**，不是 C04 的可用錯誤碼。

## 5. 新增可驗證測試與剩餘未知

1. `CT-032` 修改分析依據：對 state0x1e 收 `S02(0,empty)`，預期進 `0x4b206b` UI 本地完成路徑，**不期待 C03/S03 由同個 callback 直接發出**；原 Client end-to-end not-run。
2. `CT-043`：`S02(status!=0)` 在 `state0x1d/0x1e` 產生 C15、body 空、state0x1f；focus status 3/4/17/18/26/31；本次 static/synthetic，不是原服 status 意義證明。
3. `CT-044`：原子角色提交/重送/回覆遺失/C15 延遲/跨帳號/冒用/重啟，designed Domain 測試，需等可信 Account owner 的原生入場證據才放行正式 Client 驗收。
4. `tools/a028_newuser_response.py`：純 Python 合成 S02 parser、C04 u8、C15 行為 UI state 與 designed fail-closed commit/idempotency，沒有執行原 Client。
5. 仍未解：**A-027** pre-C03 C02 如何安全認領預建 Account、C03 no-character→MakeInfoDialog；**A-003** 原版角色名稱、合法值與角色數；**A-028 native gap** status0 成功的原始 Server DB 時點、status1..31 文字語意、0x1e UI 後是否重登/轉服及具體操作、C15 Server 處理。必須有原生資源/Server 證據或 UI CT 才能宣告全流程 ready。

## 6. 重現

```sh
sha256sum Asgard.exe
objdump -D -M intel --start-address=0x4b1d60 --stop-address=0x4b21dc Asgard.exe
objdump -D -M intel --start-address=0x5715f0 --stop-address=0x5716b0 Asgard.exe
objdump -D -M intel --start-address=0x4b14b0 --stop-address=0x4b1562 Asgard.exe
objdump -D -M intel --start-address=0x574370 --stop-address=0x57444a Asgard.exe
python3 tools/a028_newuser_response.py
```

讀 PE file section：`.text` RVA0x1000/raw0x1000、`.rdata` RVA0x1f1000/raw0x1f1000；在 `0x613690` 的原生 vtable 中 `0x5716a0` 對應空 serializer，`0x6136a4` 為 UTF-16 `./packet/ccancelnewuser.cpp`。僅附 VA/合成向量，不上傳遊戲 EXE 或使用者資料。
