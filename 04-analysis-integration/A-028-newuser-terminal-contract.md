# A-028：C04 終局回覆、C15 取消與角色持久提交邊界

證據：[A-028 BIN-first 原始研究](../03-analysis-requests/A-028-roy1-c04-terminal-analysis.md)，`ev_a028_20261031_asgard_c04_response_static`；同 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。原版 Client 觀察屬 **observed-static**，Server commit/rollback 設計屬 **designed**，原始 Client E2E 尚未執行。

## 原生 Client 回覆分流（已證）

| 前置 Local state | S02 result | 原生 Client 反應 | 證據 |
|---|---|---|---|
| `0x1d`（已發 C02） | `status=0` | 發 C04 五個 u8，轉 `0x1e` | `0x4b1f46→0x4b205f` |
| `0x1e`（已發 C04） | `status=0` | `0x4b206b` 本地 UI 操作，region3 另建視窗；**此回調無直接 C03/S03/C10** | `0x4b206b→0x4b217a` |
| `0x1d` / `0x1e` | `status != 0` | 依碼對 UI focus/display，發 **C15**，設 `0x1f` | `0x4b1da9,0x4b1ee9,0x4b1f1b..0x4b1f34` |
| 任意其他 state | `status=0` | 同一 `0x4b206b` local UI 分支（可能無關 C04） | `0x4b1f46` 的 `jne` |

S02 parser `0x57dbc0` 是 `u8 status,string8 message`；C15 constructor `0x5715f0` opcode`0x15`，serializer `0x5716a0` 為空 `ret`；rdata `0x6136a4` 含 `ccancelnewuser.cpp`。C15 **body 零 byte**，但仍需套用正常 C2S binary 連線封包包裝（非 C00/C10 plaintext exception）。已知 special focus status 3/4/18/26/31 → first UI edit；17 → second edit，**這不是正式的錯誤文字含義表**。

## Server 安全交接（designed）

**A-027 仍未找到安全的 native C02 owner claim 路由；因此不得僅憑 C02 或 C04 回覆成功來建立帳號／角色。** 可獨立開發並驗證：

1. Admin 先建立 Account，且已有可信 CredentialVerifier/AuthContext(owner, account, connection_generation, expiry)。C02 只負責已證的欄位 decoder；不認證、不得 CREATE Account。
2. 只有合法 owner 與 PendingCharacterIntent 且 profile/版本、合法名字與外觀全通過，才允許接受 C04；未認證或跨世代一律拒絕。
3. **建議設計**：以 DB transaction + unique account/character constraints 保存角色與外觀，再發對應狀態的 S02 成功。若回覆遺失，重試同 intent idempotent；不同 body 不覆蓋角色。
4. C15 只能取消同 owner/session/generation **尚未提交的 pending create**。已提交資料、已消耗的 reward ledger、另一世代的角色都不能因舊 C15 刪除。
5. C04 後 success 的 UI 已被證明不是立即 S03；只有走合法 C03、S03 World grant、C10 的已證登入路徑才可以進入 World。**原版 UI 後續回登入入口的操作仍 unknown，不得假裝由 S02 success 自動完成**。

測試：既有 CT-031/032 + 新 CT-043/044。合成 Python fixture `tools/a028_newuser_response.py` 可單獨跑（S02 parse、C04 五 u8、C15/error state、角色單次提交），但不代表實機 CT 過關。A-028 `integrated/handoff_status=partial/native_creation_commit_ready=false`；原生完整建角仍受 A-027、A-003 與實際 Server/Client 回覆證據限制。

## 2026-11-01 ADR-008（覆蓋上文所有回登入假設）

**原版 Client 成功 C04／第二段 S02(0) 後直接進遊戲、不返回 LoginDialog，玩家不需手動第二次 C03。** 上方舊有「成功後回登入」「手動重新登入」是過時 Server 規劃，不再做開發或 CT 出場條件；A-028 的 0x4b206b callback 無立即 S03 仍是有效靜態觀察，但後續背景授權/轉服/首 World opcode 必須由 A-028/A-031 補證，不能猜。已存在角色日後的一般 C03/S03/C10 登入不變。新正式需求見 [ADR-008](../02-server-planning/post-create-direct-world-decision-20261101.md)。原版 Client E2E 未執行。


## A-028／roy2 後續原生追查：Region3 真正的 LoginDialogPane（2026-11-01）

[詳細 BIN-first 報告](../task_a/roy2/A-028-postcreate-ui-native-followup.md) 確認：C04 後 `state=0x1e` 收第二段 S02(0) 會進 `0x4B206B`。此 callback 先操作 MakeInfoDialog `+0x26C` widget，經 `0x535510` 清掉 manager UI slots `0x0C/0x0B/0x0D`，經 `0x5354B0` release slot `0x07`；**這是本地 UI object lifetime，不是 World transfer 或角色刪除**。

- **Region3**：`0x4B20C0..0x4B20C8` 檢查 region=3；`0x4B2109` 呼叫 `0x4A9380`。其 vtable `0x609BBC`、COL `0x625970`、TypeDescriptor `0x6665D8` 對應 **`LoginDialogPane`**，所以不能再稱未知 popup 類型。
- 這不代表使用者必然看到登入畫面。Ctor `0x4A9380..0x4A9651` 包含本地 UI setup/event，但沒有直接發 `C03`。另一獨立 callback `0x4A8890` 在參數非零時才於 `0x4A889D` 呼叫 `0x4A7D10` 的 C03 sender；**本次無證據可將 final S02 成功自動接到這個 callback**。
- **Region !=3**：在此函式釋放 UI 後直接離開，不呼叫 `0x4A9380`；其實際背景 World 入口仍需 native runtime/其他回呼。
- **S02 非零**：仍產 `C15` 空 body + `state=0x1f`；Region3+state1e 的非空 message 可能略過一般 modal，不能解讀為無錯或 Server rollback。S02 code 的官方業務語意未知。
- **ADR-008 優先**：使用者確認創角成功直接進遊戲、無手動二次登入。過時「成功後只能要求玩家回 LoginDialog 手動 C03」不可實作。本次確定「建立 LoginDialogPane object」不等於「手動登入」也不等於「背景 C03 已證」。只有原版 Client UI＋C2S/S2C 擷包能證實 final S02→first World transfer。

可重現 `task_a/roy2/a028_native_postcreate_probe.py` **31 native VA＋LoginDialogPane RTTI**、`task_a/roy2/test_a028_postcreate.py` 合成回歸；獨立 **CT-111** 靜態驗收，**CT-105/107/108 原版 E2E not-run**。Server 仍需 owner/generation 綁定 C04 durable commit，再依真正 Client 下一包做 postcreate grant，不能因 `LoginDialogPane` 存在猜 grant 或改用 A031 returning-character C10/C25。

**此輪未缺新的具名資源檔。** 原版的下一步缺去敏 `C02→S02→C04→S02→first World S2C/C2S` GUI/packet timeline；禁止將帳密、角色名、信箱、token 原值寫入 Git。
