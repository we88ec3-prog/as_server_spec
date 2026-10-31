# ADR-008：創角成功直接進遊戲，不回登入畫面（2026-11-01）

## 已確認的產品要求
原版 `Asgard.exe` 在玩家從獨立 NewUser 畫面完成創角後，**直接銜接遊戲世界載圖，畫面不返回 LoginDialog，玩家不需要再次手動輸入帳號／密碼**。這取代本專案此前「第二段 S02(0) 後回登入再人工 C03」的規劃。

**第一次創角**與**日後已有角色的一般登入**是兩個不同入口：首次 NewUser C02→S02(0)→C04→S02(0)→Client **自動**轉場入 World；日後登入仍由 LoginDialog C03/S03/新 TCP C10（已知常規路徑）進 World。

## 證據與未證
- A-028 原始 EXE 已靜態證明 state 0x1d 收第一 S02(0) 自動發 C04；state 0x1e 收第二 S02(0) 進 `0x4b206b` 本地 callback；**該 callback 切片中沒有立即 C03 或 S03**。這不能推出最終 UI 應回 LoginDialog，亦不能證明背景絕不會再有 C03/S03/C10／新 TCP。
- **「創角直入世界」是使用者確認的需求與 Client 可見行為，非本次已取得的封包動態證據。** Client 的 callback 後續、背景認證/轉服與第一個 World C2S（C25 或其他）尚不明，需 A-028/A-031 分兩條流程查清。
- 禁止任意憑空發 S03、虛構 C03、假設 C25 body=01、無條件接受 C35 或以測試地圖冒充真原版入圖。

## Server 安全設計
1. 管理員預建 Account；創角前由本次 C02 的既有帳密認證建立 connection/generation/credential_version 綁定且會過期的 **creation-only** proof，未提交 C04 不可取得 World 權限。
2. 同一 proof 的合法 C04 才能原子保存 Character／Appearance／OnboardingProgress／既有 Account.creation_email；提交成功後發第二段 S02(0)，並為該**已提交角色**建立限權的內部 PostCreateEntryContext，保留原生 Client state/socket 的轉場機會。PostCreateEntryContext 不是原版封包或免驗證 World grant。
3. A-028/A-031 查得 Client 後續真正會發／收的 opcode、session/連線時序後，Server 才以**同一 account_id/character_id、有效 generation/credential_version、未停權**合法核發/消耗一次性 World 授權。若原版使用背景 C03/S03/C10，按實際已證順序接線；若是另一條直入通道，另按其真實格式接線。**不要求玩家返回登入頁、不讓 C02 草稿直接進世界**。
4. 成功 C04 後 S02 回覆遺失或斷線，不得回滾已提交角色；無法安全續接時才可重新開啟原生普通登入流程作**異常恢復**，不可當成正常創角結局。C15 只取消未提交草稿，重送不能建第二個角色或改寫 E-MAIL。
5. 真地圖 Map0/1/2、C35 header/structured checksum、S04/S33/S14(2)、C11/C33 移動仍須 A-031/A-032/A-005 才能稱「直接進入可操作遊戲」。

## 需修改的 DEV／CT
- DEV-ENTRY-02：C04 成功後不可將連線結束導向登入畫面；建立安全的 committed post-create context。
- DEV-ENTRY-03：補**post-create seamless entry**，與**normal returning-character login** 分開驗證；不可把原本正常 C03/S03/C10 的位置硬套到 C04 成功 callback。
- A-028：從 `0x4b206b` 追後續 UI/socket/封包，不再找「回登入按鈕」。A-031：先追創角後自動 World 鏈，再對照普通 C03/S03/C10 入圖首包。A-030：仍需 NAME/E-MAIL 真欄位與 S02/C15 失敗。
- CT-105/CT-107：**回 LoginDialog 或要求玩家重新輸入帳密即不通過**；CT-108/109：原生真 MAP/C35／移動必須連續成立。日後普通 C03 登入另測。

本決策只更新共同規格，未修改 as_server_roy 或 Asgard.exe；原版 Client E2E 全部 `not-run`。現有 `Asgard.exe`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat` 已提供，不需重傳。


## A-028 原版 Client callback 新實證（2026-11-01）

原始 `Asgard.exe` 與 [A-028 後續 BIN-first 報告](../task_a/roy2/A-028-postcreate-ui-native-followup.md) 已確認 final `S02(0)` 在 `state0x1e` 走 `0x4B206B`，並清除 UI slots `0x0B/0x0C/0x0D/0x07`。**Region3** 除了清除外，`0x4B2109` 會建立 `0x4A9380` 原生 **LoginDialogPane**（vtable `0x609BBC`／MSVC TypeDescriptor `0x6665D8`）。它是記憶體內的 UI 物件，**不等同玩家會看見要求手動登入的畫面，也沒有證明自動送出 C03**。此 success callback 本身沒有直接 C03/C10/new World TCP constructor；其他 Region 在此處不建立這個 pane。

獨立 LoginDialogPane `0x4A8890` 在參數為 nonzero 時可呼叫 C03 送包 `0x4A7D10`，**未證 final S02 success 會自動觸發該 callback**。因此保留 ADR-008：**使用者不需要再次手動登入，創角成功直接進遊戲**；但完整背景封包因果仍需 Native CT-105/107/108 去敏 Client TCP/GUI trace。A-031 的常規已存在角色 C03/S03/C10/C25 證據不能不經驗證就當第一次創角的動態順序。

Server 的 PostCreateEntryContext 需保留相同 Account/Character/generation/credential version 的授權，只有實際 Client 後續合法封包出現才進行 World transition。C15 繼續只能取消尚未提交草稿；不由本地 UI slot 清理或新建 LoginDialogPane 推導 Server Account/Character 撤銷或建立新帳號。

新增 CT-111 原始 PE 靜態＋合成測試，原版 Native E2E 保持 not-run。


## A-028 Roy3 新原件結論：Region3 有條件自動 C03（2026-11-01）

**本節以原始 Asgard.exe SHA db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145 的新 x86 證據，取代上節「尚未證明 LoginDialogPane 能自動 C03」的舊分析限制。** A028 原版 Client 靜態證據確認的「可執行分支」，仍與玩家實際 GUI/網路 E2E 不同。

Region3：final S02(0) → 0x4B206B UI cleanup → 0x4B2109 建 0x4A9380 LoginDialogPane → ctor 在 [0x66D10C]+4 及 +0x204 的兩個 UTF16 開頭字元非0，且 USER32.GetAsyncKeyState(0x11 VK_CONTROL) 回 signed SHORT 非負時，0x4A9617 以 event4 調 0x4A8950，經 event 跳表0x4A8D34[0]=0x4A8996 → 0x4A8A30 直接呼叫 0x4A7D10 C03 發送流程，不經手動登入按鈕。auto C03 是兩個 string8 + u8=0；另一獨立 LoginDialogPane callback 的 nonzero 分支 C03 最後 u8=1。

這說明產品要求「創角完成不用重新手動輸入帳密/按登入」**不等於禁止 Client 在背景再送 C03**。但 constructor 快取非空不證明送出的帳密有效，Region3 以外入口亦未證；若觸發成功仍須 Server 正規驗證 Account/Character/Session，按真正 S03/C10/C25/World 收包進行授權與畫面驗收。不要把「靜態已發現有條件自動 C03 入口」推成「創角成功一定收到 S03、一定可以登入 World」。

研究資料：task_a/roy3/A-028-roy3-conditional-auto-c03.md、04-analysis-integration/A-028-roy3-automatic-c03-contract.md；原件 7 native E8 direct calls、42 opcode anchors、5 Region entries、10 event entries、12 offline tests。CT-105/107/108 原版 GUI/TCP 仍 not-run。原版 Client、DB、Server 程式未因本次補充而修改。
