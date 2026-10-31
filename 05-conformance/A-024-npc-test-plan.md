# A-024｜NPC／怪物物件 Client I/O 與後續原生驗收

**Scope**：原版 Asgard.exe S07/S0C/S64/S5F/S0E parser，A-022 MAP loading、A-023 Born/S44；原服 NPC spawn/AI/respawn 規則仍 unknown，Server 的暫定 epoch/授權規則列 **designed**。同 SHA/profile 的原 Client native 驗收未執行。

- **CT-021 — 真新手 spawn**：只在 S15/S14/C35/S04 同 epoch 已完成載圖後接受 S07；必須找到官方 tutorial map_id、S07 非空 row subtype、NPC/monster asset+entity/map binding，兩次登入/相同生成不重複；未提供這些時不能標 validated。
- **CT-022 — 動作／死亡／移除**：S0C/S64 表演移動、S5F/S0E 分離死亡/清除；舊 epoch、消息錯序、截斷/超長、斷線重登、重複移除和怪物重生 generation。S64 native local 11 path bytes 風險以保守校驗處理；不是原版 wire limit 的證明。
- **CT-034 — 互動教學 NPC**：A-023 S44 啟動 Born.Main 是已證 Client 收包行為；女招募員實體與 C2S click/互動 opcode **未證實**，C43 object-info 類僅候選。要先確立 map、NPC entity id 和 UI producer，再跑真假互動、超界、重送與 UI/任務結果。

6 項**合成**檢查：\`python -m unittest discover -s task_a/roy2 -p 'test_a024_npc_codec.py'\`，包括 S5F/S0E、S0C、S64、S07 空列、錯包及 entity epoch 模型（本機 PASS）。非空 S07 仍故意 fail closed。下游權威 Server AI 由 DEV 負責，不因 native CT 尚未執行而阻止已證 Client 研究交接。
