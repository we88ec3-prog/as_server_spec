# CT-058～060 — A025 原版戰鬥多型與教學目標驗收補充（2026-11-01）

依據 [原始 native 分支表](../03-analysis-requests/A-025-roy1-battle-variant-closure-20261101.md)／[探針](../tools/a025_battle_variant_probe.py)／[測試](../tools/test_a025_battle_variant_probe.py)。本次 22 native windows、C3D 16 + S3D 16 = 32 jump pointers、14 synthetic/original-static tests **離線 PASS**。未操作 Windows 原版 Client GUI/TCP/原 Server。

|現行正式 CT|可離線確認|待原版 GUI/TCP 與 Server 驗證|
|---|---|---|
|CT-058|C13 u32BE、C4D u16BE、C56 u8、S52 u32BE+u8、**S5F** u32BE（修正歷史錯誤 S1E）；writer/reader opcode|攻擊與施法 UI 真 sender、S52 第二欄與 C56 階段實際意義|
|CT-059|原版 C3D subtype0..15 16-way 表；S3D 1/3/4/5/6/7/8/10/11/12/15 安全解碼；complex 0/2/9/13/14 fail closed、壞長度/尾端拒絕|complex five branch 完整 vector schema/上限、原版 result UI/成功/失敗時序、所有 subtype 原服業務定義|
|CT-060|Server designed intent→CombatResolved→已 verified QuestObjective ledger，跨 actor/generation/replay 防重與無授權 objective 不變|官方新手是否需戰鬥、首次 Monster 身份、kill objective/獎勵/出圖與雙人實際 Client 行為|

命令：

    python tools/a025_battle_variant_probe.py Asgard.exe
    python -m unittest discover -s tools -p 'test_a025_battle_variant_probe.py' -v

**正式 CT-058／059／060 原版實機狀態都保持 planned/not-run。** 以前 A25 CT-051/052/053 為分支歷史編號；主線實際 CT-051 屬其他任務，不覆寫。上傳原件及任何真實封包請保持私有/去敏，不提交原遊戲素材。
