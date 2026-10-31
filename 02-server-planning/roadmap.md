# 階段路線及完成門檻

|階段|範圍|出場門檻|主要依賴|
|---|---|---|---|
|M0 規格基線|現有單人原型的可追溯profile、封包／情境／向量|語意無私有程式依賴；未知有A；最後兩項顯示實機驗收|R-023/024、A-006|
|M1 相容核心|認證、狀態機、雙玩家可見性、移動權威、保存、真背包最小模型|兩原客戶端互見、移動、更衣、斷線；非法動作不破壞狀態|A-001..007、A-015..018|
|M2 可玩循環|數值、戰鬥、技能、怪物、死亡／復活／掉落|完整打怪循環；錯誤目標、重送、同時事件可重現|A-008..011、物品實例|
|M3 內容與經濟|對話、任務、商店／倉庫／交易，按確認的範圍擴充|領獎／交易中斷及重啟無重複資產；內容規則有版本|A-012/013/016|
|M4 社交與持續內容|聊天、組隊、公會等已確認系統|權限、離線、多人同步與持久化通過|A-014及核心一致性|
|M5 營運準備|容量量測、備份還原、升級、管理權限、濫用控制|故障演練、回復驗證、可追蹤版本及操作稽核|A-017/018及完整驗收|

不按日曆承諾完整遊戲時間。先把M1兩人互見完成，再擴大戰鬥與經濟，避免只增加單人UI可見功能。每個階段均應交付可運行增量、規格更新和批次驗收，不能只交反編譯摘要。

## M1 內新增 ONB 首次玩家 P0 子里程碑

ONB-01 管理後台建帳和安全登入 → ONB-02 Client 創角（需 A-021）→ ONB-03 首次原生教學進圖（需 A-022）→ ONB-04 故障回復與 CT/原 Client 驗收。ONB-05 怪物、NPC、技能及完成教學為後續階段，**不算本次首次進圖已完成**。見 [first-login-onboarding.md](first-login-onboarding.md)。

## 首次玩家到完整教學的新階段（2026-10-31）

M1/ONB-01～04 定義「管理員建帳→玩家登入→創角→進入原生教學→故障恢復」；M2/M3/ONB-05～06 定義「教學 NPC/怪物→技能/目標→完成與退出」。見 [ONB 進度板](onboarding-delivery-board.md)、[機讀開發批次](work-items.json)、[教學 Server 規劃](tutorial-runtime-plan.md)。規劃完成不等於 Server 已實作或原 Client 驗收。

## Client I/O → Server 實作分段路線（v2）

依 [Client I/O 縱切開發計畫](client-io-delivery-plan.md) 分 DEV-IO-01～06（正式追蹤仍用 ONB-01～06）。與其等待原服帳號驗證、固定出生點或首次任務派送政策，先按已證 C03/S03/C10、C02/S02/C04/C15、S15/S14/C35/S04/S33、S44/C6C 實作對應 Adapter/Domain；由 Server 自行決策 account owner、map/spawn、Script 派送、NPC AI 和 Quest。Client UI 下一步尚未知仍須 A 定點查（尤其 C03 無角進 NewUser），CT 只在原 Client 實測後標 passed。參照 [機讀矩陣](client-io-flow-matrix.json)。

## 下一階段：已知 Client 收發與 Server Authority 併行（2026-10-31）

[Server SAFE/WIRE/WORLD/SCRIPT 分段規劃](native-creation-next-iteration.md) · [機讀就緒關卡](onboarding-readiness-gates.json)。**SAFE-01～04 的帳號身份、創角輸入與已登入帳號一致性、草稿與 C04/C15 原子/冪等設計可立即開工**；A-027 的原生 C03(no-character)→NewUser UI 與 C02 第1欄語意未證前，Host 仍不解鎖 native C02/C04。A-020 登入、A-022 MAP/C35、A-028 C04 後 UI 可同步深入；A-024～026 依 NPC/技能/任務 Client 封包證據擴張。新 CT-054 只作 Native UI 驗收計畫，目前 not-run。
