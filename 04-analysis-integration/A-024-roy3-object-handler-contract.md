# A-024 roy3 — 原版 NPC object lifecycle Client I/O 規格交接

基礎：task_a/roy2/A-024-analysis.md；本輪：task_a/roy3/A-024-roy3-native-object-handlers.md；Evidence A024-E20..E27。Client SHA db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。

**Trigger**：World/AOI 場景下 Client 收到 S07 建物、S0C/S64 移動、S5F 死亡、S0E 移除；C43 info 與 C13 attack 由 Client 主動送出。
**Client sends**：C43 u8+BEu32+u8；已追兩條 01+object_key BEu32+04 的 producer（VA 0x479DC7/0x4A23F8），不代表女性招募員的唯一點擊方式。C13 BEu32 沿用 Roy2。
**Client receives**：本階段 dispatcher 0x4F48A0 中 S07→0x4F17C0、S0C→0x4F1610、S64→0x4F1750、S0E→0x4F1DA0、S5F→0x4F2BB0、S29→0x4F1DC0、S62→0x4F2CD0、S63→0x4F2F10。S34/S3C 另有 parser，不可從此階段 default 宣告全域無效。
**Client reaction**：S07 0x228 local row stride，kind14 existing/new object，kind13 special 0x4C0640，kind1/2/4 經 0x4D6FA0，其他 kind 視 0x8000..0xBFFF field conditional；依 0x4B6450 加入 scene。S0C 以 object key 查 0x4EAC30，再執行 vtable +0x34/+0x3C/+0x40 位置方向及狀態；S64 0x47C9C0 path；S0E 0x4BA0C0 remove；S5F 0x4F2BB0 獨立死亡，並非立即 S0E。
**Evidence**：原始 EXE 8 native dispatch、21 call、39 native byte anchors、10 個 local tests；Roy2 S07 14 kind/其他 packet codecs；未改原始 EXE。
**Unknowns**：kind→NPC/Monster/静態資源 binding、真招募員 entity map/Script、Server AI/spawn/respawn/speed、實際動畫/UI、S34/S3C 其他 phase handler、Native E2E not-run。

Server designed：對 auth/session/map/generation/object ID/AOI 驗證，防舊 spawn、重送、死亡與移除混淆、玩家攻擊和 NPC 點擊必驗距離與權限。此安全規則不可冒充原服 AI。詳細 Native CT-081 於 05-conformance/A-024-roy3-native-object-lifecycle.md。A024 static handoff ready。
