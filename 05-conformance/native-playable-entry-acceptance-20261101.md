# 原版創角→登入→進圖→可操作：CT-107/108/109

**全部 `planned`、`native_client_validation=not-run`。** 原 Client SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；測試需記本次 Server/main commit、DB provider、selected region/seed、MAP SHA/版本及去敏 trace。不得修改 EXE，不接受合成 C25=01/任意 C35/測試 World fixture 當 native PASS。

## CT-107：第一次建立角色並成功拿到登入 grant
建立無角色 Account（Admin，不經 Client 註冊）→ 原版 NewUser C02 → stage1 S02(0) → C04 → stage2 S02(0) → **原生 UI 不回登入、不需再次人工輸入帳密，直接開始 World 轉場**（實際 Client C2S/S2C 待 A-028/A-031）。SQLite/Pg 均檢查 Character+Appearance+onboarding+`creation_email` 原子提交及持久化、帳戶 owner 不變；不存在／錯密／停權／重名／NAME/EMAIL 失效／C15/重播/中斷不多寫一筆、錯誤 UI 可見。記 S02 非零正確 native message/retry/C15，不把已證的正常轉服關線誤判成失敗。**創角後顯示登入頁或要求人工重送 C03 即驗收失敗**。預建帳號測試值必須符合選定原 Client UI region 欄位限制。

## CT-108：真 Client World entry 與地圖載入
由 CT-107 **同一原版 Client 的首次創角成功自動入世界**開始；另以合成預置角色**僅單獨驗一般 C03/S03/C10 route**，不是 CT-107 PASS。依 A-028/A-031 驗證的真實轉場／World 首包/C25（不猜）→ S05/S15/S14(1) → 真 Client 回 C35 正確 header + structured checksum → Server 原子 world-entry checkpoint → S04/S33/S14(2) → 地圖顯示、人物定位、loading 結束。MAP 綁定真 `Map0.dat`／`Map1.dat`／`Map2.dat` revision；錯 C35/非法 epoch/錯碼/斷線不能偷寫 tutorial_completed，重登恢復。若只在其他合法圖測得，標 interim，非正式教程圖通過。

## CT-109：世界可操作與位置安全
原版 Client 地圖載入後使用真正按鍵/滑鼠操作 C11 轉向、C33 3u8 移動，Server 提供 client 支援的 S0B（其他觀察者依已證 S06/S11）並更新權威座標。以 A-032 明確測得的合法路徑往返、測一個阻擋/邊界與錯序/重送、斷線重登位置、兩玩家同圖互不竄改。未證 collision bit 先保持安全拒絕，不得全圖放行；玩家只有載入地圖但無法行走不算通過。

## 最終驗收
只有 `CT-107 + CT-108 + CT-109` **同一個原版 Client flow** 均 native passed 且持久資料重啟不變，才宣稱「原版 Client 可創角、登入、進遊戲且可操作」。Domain/unit/CI/agent analysis 的 PASS 只能分別記錄；未知服務端狀態不能讓拒絕退化成已成功。依賴 A-030、A-031、A-032、A-005 與 [DEV 路線](../02-server-planning/native-playable-entry-roadmap-20261101.md)。

## ADR-008 最終驗收更正

創角成功後**直接進世界**，不能把「回 LoginDialog → 玩家手動 C03 → World」當作 CT-105/107 通過；正常已存角色日後登入則獨立以 C03/S03/C10 驗證。原 Client 後續封包尚未知，實測前保持 `planned/not-run`。詳 [ADR-008](../02-server-planning/post-create-direct-world-decision-20261101.md)。

## 2026-11-01 靜態證據新增與原版 UI 出場限制

- Region2～4 C02 F3=NAME、F4=E-MAIL 已原件驗證；CT-105/107 的選定 region、原生表單及失敗 S02/C15、成功直入 World 尚 not-run。
- CT-110（Region3 C10 後 C25 `CBillingInfoPacket` 三 string8）與 CT-111（Region3 最終創角回呼建構 LoginDialogPane）是離線／合成測試，不可取代原版 CT-108。Region!=3 不可強制存在 C25。
- A-032 MAP 靜態重算確認 map_ref=6 C35=`00040F90`，map_ref=0/10000/18001/20001 請見 [整合報告](../04-analysis-integration/roy123-verified-evidence-review-20261101.md)；**未抓到原版 Client 真 C35**、spawn/view/facing、教學圖 id 仍 unknown，CT-108 不可提早通過。
- A-005 native S0B bit7/low7 分支已證，**回當次 C33 sequence**；合法移動/阻擋 rollback GUI 未執行，CT-109 不可提早通過。
- [完整新驗收操作/次序](../02-server-planning/roy123-playable-world-implementation-20261101.md)，錯誤／待取證由 [A 精準清單](../03-analysis-requests/roy123-remaining-playable-blockers-20261101.md) 跟蹤。
