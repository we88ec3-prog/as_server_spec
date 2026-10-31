# Roy1 A-012 / Roy2 A-010 第二輪追補同步（2026-10-31）

**來源 pin**：第一輪整合後 main `0a059f47eb4f5acd3f00009736bc72ed093a4bd0`（第一次已通過 GitHub CI）；Roy1 最新 `eb4dfe1c320de4cdacf11a30fd86b9845c7e5768`（新增 A-012）；Roy2 最新 `094f5028417f81f1413acf7e56c756a109b20561`（新增 A-010）。這次建置新 3-parent merge，保留既有 Roy1/Roy2 歷史，兩個 branch refs 不 force push。原始 `Asgard.exe` / DAT 不修改、不上傳，遊戲密碼 4～8字及共用地圖政策不變。

## Roy1 A-012：任務選項 / Script 回覆

- 使用相同原始 Client SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。A-012 **來源報告**：20 個原生 C6C/S44 指令定位、Born wrapper/CRC 及 14 synthetic tests PASS。這些是分析者證據，仍**沒有**本輪 Windows Client GUI 操作或原服 quest trace。
- S44(1,0) 會指定 Script.Main；Client `SendReply` 送 **C6C(1,name,context,pair_count,key/value string8)**，而 `Dispose` → C6C(4)，未回覆 cleanup → C6C(2)。`STATE=ACCEPT` 是已取得的 `nNewJoin01.dat` 選擇資料，但 NPC entity→script bind 與任務完成/獎勵/出生圖都無法由 C6C 自動推定。
- 可先做 `ScriptRun` 授權/expiry/reply idempotency、許可 key/value 白名單、`QuestIntent` ledger；絕不可因 Client 文字或關閉 UI 發獎。

## Roy2 A-010：技能施放／取消／持續效果

- A-010 **來源報告**：25 個原生 PE VA 指令定位及 6 個 RTTI，原版 C4D、C56、S52、S48、S2C、S2D 的 decoded-body codec/單元測試已交付；Client 原始技能效果 UI/cooldown/MP/stack/duration/producer 時序 **未證**。
- C4D = **BEu16 選擇技能值**，已追到 Client 本地 producer；C56 = u8 (尚未確認實際 UI 送出時機)；S52 = BEu32+u8；S48=BEu32（取消）；**S2C 是 opcode `0x2C` 的 AddLastingSpell，並非「S→C」泛稱**，其中動態 string8；S2D 是 `0x2D` 的 RemoveLastingSpell，不能誤當 S5F death 或 S0E 移除世界物件。
- Server 可先做 `CastIntent`/cooldown/resource reservation 以及 `LastingEffectLedger` 的權威狀態、idempotent add/remove/outbox；**公式、spell-id、時長與官方 UI 語意不推測**。

## CT 編號再次碰撞，已重新安排

第一輪 main 已有 CT-087～089 經濟、CT-090～091 地圖。後來 Roy1 A-012 建 CT-090～092，Roy2 A-010 建 CT-089～090，不能無衝突照搬。

- **A-012 Quest**：來源 Roy1 CT-090、CT-091、CT-092 → main **CT-092、CT-093、CT-094**。
- **A-010 Skill**：來源 Roy2 CT-089、CT-090 → main **CT-095、CT-096**。

在 requests/evidence/packets/vectors/flows/work-items/traceability 與研究文件改號；全部新 Client CT = planned / not-run，不以 synthetic tests 冒充原版 GUI E2E。

## 需要繼續分析／資源

- A-012/A-011/A-024：NPC 點擊 → 真的 `nNewJoin01`/Quest Script 入口、NPC entity/key/原生回覆 UI；Server quest rule/獎勵政策分開規劃。
- A-010/A-025：C56 真正 UI producer、C4D→C56→S52/S48 時序、S2C/S2D 同一 effect identity、spell-id→UI/效果/時長/stack 與 Client 顯示。
- A-022/A-015：C35 structured checksum 與原版可走座標仍待 Client trace。
- **目前無新增必需具名遊戲檔案**。現有已提供 `Asgard.exe`、`Born.dat`、`Map0/1/2.dat`、`Monster00.dat`、`World00.dat`、`nNewJoin01.dat`、`PaperDialog.dat`、`PaperDialog02.dat`。若原生 XREF 指明技能定義素材，才補列正確檔名；`Skill*.dat`/ `Spell*.dat` 目前只是**未證猜測，不能要求**。

[Server 接續規劃](../02-server-planning/new-quest-skill-dev-iteration-20261031.md)。
