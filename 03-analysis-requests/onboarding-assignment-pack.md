# A-XX 分工交付包：首次玩家至教學完成

日期：2026-10-31。Client SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，profile `TW-seed0-local-v0.1`。**此處只是委派規劃，不是已派人；requests.json 裡 assignee 仍為 null、status 仍 open。**

|分析|專長／任務|優先|先決條件與可並行性|
|---|---|---|---|
|A-021|Client 登入/創角 UI、C02/C04/S02 及轉場|P0／第一個委派|優先立即開始；參照 A-003/A-020|
|A-022|地圖/資源、首次教學地圖 ID、spawn、C25/C35/CRC|P0／與 A-021 並行|靜態研究可開始；完整進圖實驗需要 A-021|
|A-023|新手教學第一個 Script/NPC/任務 UI 依賴|P1／可並行|可先追靜態；動態驗證依賴 A-022|
|A-024|教學 NPC/怪物 spawn、AI 動作/消失/可見性|P1|可先追 A-011；實際場景需 A-022/023|
|A-025|教學技能/攻擊、目標合法性、效果及任務計數|P1|可先追 A-009/010；實際教學依賴 A-024|
|A-026|教學完成、獎勵（若存在）、出口/重登|P1|先追 A-012，動態需 A-022～025|

## 接手與交付

1. 認領時更新 requests.json 的 `assignee`、`status` 與 `dependencies`，分析人員自行保存原始大型證據；共用 repo 不包含原始 EXE/遊戲資產/真實憑證。
2. 每份成果至少提供 Client SHA/版本、Evidence ID、反編譯與 BIN 位址、封包方向/opcode、逐欄 offset/type/byte order/encoding、Client UI 效果、正常與拒絕/取消/超時/重送/重登路徑。
3. 將「observed-static / observed-runtime / inferred / designed / unknown」逐項標記，未知不能填 0 當作已驗證。
4. 分析完成先進 review；整合後更新 PKT／SCN／CT、tracability、manifest，才能標 integrated；單純提交研究筆記不算。
5. 此任務適合多位研究者並行；同一 Client 版本與原始資源身份必須一致。原生測試與 Server 合成測試分開記錄。

## 可直接貼給受派人員

> 請依 as_server_spec 最新 main 的 A-XXX 執行逆向研究，先閱讀該 A 的 method/deliverable、相關 R/SCN/CT 與版本 SHA。交付原生 Client 端到端流程、封包序列與字段、BIN 位址及資源依據、失敗/中斷/重試分支、Server 需要的語意和至少一個 CT 建議。所有結論標 observed-static/runtime/inferred/designed/unknown，禁止以猜測的 map ID、opcode、技能 ID 或獎勵數值取代證據。把可分享成果整理回 04-analysis-integration，未解阻塞保留在 A。

## 不需要等分析才能做的 Server 工作

管理建帳、憑證與停權核對、角色 DB 唯一性、一次性 grant、Loading/失敗回復骨架、任務 ledger 與場景 instance/generation 的 domain 模型均可以先開發。**原生相容映射**（C02/C04 回應、教學 map/spawn、NPC/技能/完成封包）必須等待相應 A。

## 分析者與驗收者的責任切割（強制）

本交接包中所有 A-021～026 的「Client 實測」若需要尚未開發的 Server，**只要求分析者交出待跑的重現步驟與預期，不要求分析者先做出 Server 或先讓 CT 通過**。有證據的原 Client 靜態觀察、封包欄位、腳本/資源語意可先交付且經審查。若必要字段仍 unknown，將 `handoff_status=partial`，不能自稱整段流程完整可實作；只有原始證據不可取得才真正 blocked。

分析工作審查和原 Client E2E 驗收要各自標記狀態。A-021 的交付清單與 CT-018 分工見 [A-021-acceptance.md](A-021-acceptance.md)，所有接案者必須遵循 [通用關卡](../00-governance/phase-gates.md)。

## A-027/A-028 優先分派：解除原生預建帳號創角阻塞

roy1 的 A-021 static subset 已完成 review，但是 **C02 在 C03 前的帳號擁有者證明未知**。交付 A-027 給 Auth/Client UI 研究者，要求明確驗證 C02 欄位來源、身份校驗方式及如何預防他人帳號被冒用；交付 A-028 給 Client state/packet 研究者，要求完成 C04 後 state0x1e 的回覆、角色提交/失敗與轉服或重登。兩者都**不需要先把 Server 做出來才算分析完成**；缺證據必須保持 partial，不能以安全性不足的 provisional claim 取代。

## 最新指派順序（2026-10-31，以本節覆蓋上方歷史表）

A-021、A-022、A-023 均 `integrated/handoff_status=partial`，不可再當作尚未開始。**P0 第一批**：A-027（pre-C03 C02 owner/credential boundary）＋ A-015（版本化原生 MAP/Born/NPC 出生資料），可由兩位分析者並行；A-003 與 A-020 同時補合法值和 metadata/auth。**P0 第二批**：A-028（C04 最終 status / Character commit / transfer），可在 A-027 身份來源尚未結論時先查 state0x1e 的 BIN，但不能設計無憑證帳號認領。A-016 補 crash/recovery、A-022 針對實際 MAP 的 checksum expected pair 是平行支線。**P1 第三批**：A-012（Born/Script 任務語意）＋ A-011/A-024（女性招募員及首 NPC、怪物 spawn/action）；有了明確場景和 NPC 後才封閉 A-025 技能/目標事件，最後 A-026 完成條件／出圖／獎勵。A-004/A-005 可並行補可見性與移動權威。

A-023 的 CT-ID 經 main merge 改為 CT-033..035，不再佔用 A-021 的 CT-029..032。Born 原件是否與 Client 版本相符尚未證實；本次驗證 EXE SHA 與指定 BIN 分支，Born 原件離線 PASS 僅有 roy2 的研究報告/validator 可供日後重現。

完整排程與出場門檻見 [新優先矩陣](../02-server-planning/analysis-priority-after-A022-A023.md)。

## A-001/A-023 本輪合併後給分析者的最新指令

A-001 與 A-023 的 `integrated` 是可用證據子集；不要求重新做已經重現的 seed mask 或 S44(1,0) 主解析。**A-020** 補實際選 seed/key 的條件與版本/失敗 UI；**A-012** 補原服 first-login Born script 派送及任務/flag，已知 C6C2/4 為 cleanup 而非 quest；**A-015** 補原版 map ID、出生、MapContent revision/CRC 並驗證資源與 Client 發行配對；**A-024** 查招募員 entity/map/spawn、候選 nNewJoin01 真實綁定。最高 P0 保持 A-027、A-015、A-028。詳細限定格式見 [新證據 review](../04-analysis-integration/A-001-A-023-merge-verification.md)。研究不以 Server 實機 CT 為完成門檻。
