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
