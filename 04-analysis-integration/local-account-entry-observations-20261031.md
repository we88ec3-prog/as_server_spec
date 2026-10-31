# 本地登入／創角入口補充（2026-10-31）

來源是本地既有 REA 調查 `creation-entry-packets.md` 與 `native-main-menu-preview-plan.md` 的去敏整理，本次整合沒有重新跑 Client／REA。原版 EXE SHA256：`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。供 A-020／021／027／028／030 與 Server 入口規劃對照，不提升其原版實機驗收狀態。

## 靜態 Client I/O

|trigger|Client sends / receives|Client reaction|證據與界線|
|---|---|---|---|
|條款同意、本機模式3|入口先讀本機帳務旗標，並非由某個成功 S02 決定創角|0x5408D0 動作、0x540933 比對第三旗標，呼叫 MainMenu(1,1) 或 (1,0)|命令列解析 0x403300、主選單 0x4B0890；只是本機入口分析|
|主選單本地 New 動作|此處建立 UI 不是已知的 Server「開創角」封包|0x4B0230→本地 UI 建立；CharSelect 0x42C920、UserShape ctor 0x560D80、MakeInfo 0x4B1A90|三個 ctor 的兩組已解析引用是 0x4AEE9A/4B0B01、4AEED0/4B0B32、4AEF08/4B0B67；0x5607C0 是繪製函式|
|普通 LoginDialog 收 S02|結果由已存在的 LoginDialog 處理；S03 是轉服|Login S02 handler 0x4A8D60；S03 handler 0x4A8370|已查分支沒有建立創角三 UI 的呼叫；不能把「沒找到」擴大成整個 EXE 不存在任何其他間接路徑|
|MakeInfo 已開啟時收 S02(0)|state0x1D 接成功送 C04，再等第二 S02|state0x1E 接成功走本地完成／回登入；非零結果會有 C15/state0x1F 路徑|0x4B1D60..0x4B217A；完整 status 語意及 retry 留 A-030，不套用 Login 錯誤碼|

可重查的 Evidence 身份（原件留本地，不保證另一個 REA session 依 ID 即可取得）：

- 三 ctor 引用：`ev_6cd272c922ed94b068e62fd3941433b8d20d0c167949afeacd7d1e890b404c9d`、`ev_7f20d15b84aa558ecff44595c3e75f133272748ac612f99163e877fdd38864b3`、`ev_9093cbc7eda80170a8522cd70d8189c2cb42b03377c0db33ce39aa671563e194`。
- MainMenu：`ev_9d783a1c8a8fce584cd6e6db1583f97f7345d4b5d1c903094331d88ce0895ae0`；參數解析：`ev_6b2e0b9bfdc11d86fd410ee30bdacb870f6bb122607c09ee14597498d99001f8`。
- Login dispatcher：`ev_a279d545b4b0826db1ee9775e880576345eebabbeff69c41e812a55833eef2f7`；MakeInfo result：`ev_c238a648583068de57ecea29258fd05b7bab9889f1b239501bac926016f04ed9`。

## 修改副本的實機觀察

使用者另行授權只為看主選單建立診斷副本。該副本 SHA256 `e834a07d21807748561bafa7e9cca97195234a9b664ea9c20f9e83faafc8cb9d`；相對當時手動登入候選的差異是一處 UI 入口立即值，使既有呼叫走 MainMenu(0,0)。候選沿用此前副本改動，**不是宣稱與原始 EXE 只差一個 byte**。

實際看見原生資源的紅幕、標誌與 New／Connect／Exit。未點選按鈕、未在此次預覽輸入帳密、未完成 C02/C04。這只能證明該修改副本可顯示主選單，不能證明原版有可用命令列入口、原版 New 可完成創角，或任一 Server 已通過驗收。

## 對 Server 規劃的影響

保留獨立 NewUser/C02 設計；不要等待「普通登入收到某包自動開創角」的未證假設。S02 必須按當前連線階段／Client UI 合約回覆。C02/C04 是原生 wire；相容 Server 自行實作回應不等於改過 Client 協定。診斷入口調整不能作為修改正式 Client 或繞過身份驗證的理由。
