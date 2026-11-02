# A010-D01 / roy1 — 已學技能清單、ID、快捷列與 Server 登入資料

2026-11-02；沿用 task_a/roy1，沒有創立新 branch，沒有改 Client。工作來源：[main 的 A010-D01 工作卡](https://github.com/we88ec3-prog/as_server_spec/blob/main/03-analysis-requests/web-skill-review/jobs/A010-D01.md)、A010/A007/A008 基線、main 2026-11-02 快捷鍵增量分析、原始 Asgard.exe。原件 SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145；本次有 33/33 PE 原生 byte anchors、3/3 shortcut 設定名稱與 15/15 單元測試通過。沒有實機 Windows GUI / 原服登入抓包。

**限定判定 partial：S62→ActionEntry→shortcut→C4D 的欄位與靜態路徑已證，官方技能 ID/圖示、學習封包、完整首次登入下發時機仍未知。**

## 1. 四個不能混淆的欄位

|欄位|原生證據|真正用途和界線|
|---|---|---|
|Action kind + action slot|S62 wire offset0/1 為兩個 u8；0x4019B0 的索引 key = kind*80+slot；0x538970 查 ActionEntry|清單鍵，例如 kind1+slot1=81；**81 不是技能 ID，也不是快捷欄位置**|
|presentation_word|S62 wire offset2..3 BEu16，0x4017D0 存 ActionEntry+4，0x4019A0 取值，0x444AFB 再組合額外 byte*10000|顯示/圖示識別候選，但完整 Icon.dat member/frame 消費鏈未證；**不能直接稱官方 skill_id/icon_id**|
|cast_value|S62 四段 string8 後另讀 BEu16；packet local+0x20→0x4F2E37→ActionEntry+0x80E（寫入點0x4018B6）→0x401FB8/0x402045→C4D BEu16|**值確實送到 C4D**；但是否為永久官方 learned_skill_id、等級或 variant 尚未證明|
|shortcut(row,cell)|0x559470 索引 (row*10+cell)*12，每格 valid DWORD/type DWORD/slot u8|Client 快捷列位置；**與 S62 action_slot 不同**，Shortcut.Type 還經 0x489E60 轉換才查 ActionInventory|

原件顯示 0x401ED0 對 ActionEntry+0x80E 先檢查：等於 0 走非施法 action（0x401DF0 的 C0E 與 mode-dependent C65）；非零走 0x575510 C4D，0x402052 enqueue，0x4FD1D0 本地 action。C56 user-UI sender 仍未知，不能說每次 C4D 後必送 C56。

## 2. S62/S63 解密後 wire 欄位

原生 SAddAction ctor 0x578F70，在 0x578F89 push 0x62。reader 0x579020..0x5790DC 依序：

|wire 相對 offset|型別|packet local offset|Client Entry / 注意|
|---|---|---|---|
|0|u8 kind|+0x18|entry+6|
|1|u8 slot|+0x19|action row key|
|2..3|BEu16 presentation_word|+0x1A|entry+4|
|4|u8 use_mode|+0x1C|entry+7，mode selector|
|5|u8 use_flags|+0x1D|entry+8|
|6|u8 opaque|+0x1E|entry+9|
|7起|4 × string8（各 u8 encoded byte count+N bytes）|+0x22,+0x222,+0x422,+0x624|四個 native Unicode 緩衝區，確切名稱/tooltip 對應未全證|
|四字串之後|u8 opaque|+0x824|unknown|
|再後|BEu16 cast_value|+0x20|entry+0x80E→C4D|
|最後|u8 opaque|+0x825|unknown|

**因四段文字變長，cast_value 並沒有固定 wire offset**。保留原 encoded bytes，不能把本地寬字串 buffer 當成固定 512-byte wire，也不能假設所有 Client 版本都用同一 codepage。

SRemoveAction ctor 0x5858A0 / opcode0x63（0x5858B9），reader 0x585950 僅 **kind:u8,slot:u8** 兩位元組；0x4F2F10 消費並以 0x538F20 刪 ActionInventory、0x559500 清除對應 shortcut 參照。原版 UI 學技能/升級時從 Client 送哪個 opcode，**沒有證據，不補造**。

## 3. 快捷列保存：本地設定是已證，跨設備同步是未知

0x559470 每列 10 格，每格 12 byte 結構。原始字串確實位於 Asgard.exe：

- Shortcut.%d.%d.IsValid（0x612974）：0x55BC48 寫入／0x55EBD9 讀取。
- Shortcut.%d.%d.Type（0x61294C）：0x55BC74 寫入／0x55EC2F 讀取。
- Shortcut.%d.%d.Slot（0x612924）：0x55BC9E 寫入／0x55EC8F 讀取。

0x55EC69..0x55EC6C 對 Type 限制 0..3。0x46D338 讀 shortcut row，0x46D365→0x489E60 翻譯 type 再查 action，**Shortcut.Type 不應等同 S62 kind**。這證明 Client 本地設定 API 的讀寫，但本次無證據可定義實際設定檔名、儲存位置、帳號/角色隔離，以及原服是否另外提供跨電腦同步。尚未找到具確證的獨立 Server→Client 快捷 layout packet，不得捏造。

## 4. 登入後 Server 必須準備的資料（設計與原版介面分列）

|資料|提供方式|已知與未證界線|
|---|---|---|
|角色已擁有的 action/skill snapshot|登入、選角與 World owner 驗證後，**在可使用快捷鍵前**逐筆下發 S62 row；保持各角色 action_kind/action_slot 穩定|已證 Client 讀取 S62 建清單；首次 snapshot 與 S15/C35/S04 的精確時序、原服筆數仍 unknown|
|一筆可顯示/操作的 ActionEntry|S62 kind、slot、presentation_word、mode、flags、四段 encoded strings、cast_value、opaque bytes|有欄位格式，但官方名稱、icon、ID、非零 cast_value 與 enum 不能臆造|
|學會/升級/移除|Server 在**授權並持久提交**後利用 S62 更新或 S63 移除，重登 snapshot 可重建|原版學技能 Client C2S producer/回覆尚未證，設計不能被冒稱官方規則|
|快捷列綁定|Client 已有本地 Shortcut.row.cell.IsValid/Type/Slot 機制；Server 要保證 action key 不亂重排|沒有已證的原生快捷 layout S2C；若需跨設備 Server 同步，另規劃 Server 自有儲存/API，先別偽造 opcode|
|施法授權|收到 C4D 的 BEu16 必須查當前角色已學 catalog、World generation、目標與消耗/冷卻|原服技能數值公式、範圍、冷卻與等級映射 unknown；不得把 C4D 當成功擊中|
|其他回覆|S08 更新資源；S52/S48 回施法狀態/取消；S2C opcode0x2C 與 S2D opcode0x2D 更新持續效果|這些包不等於已學清單 S62，且效果 enum 未解|

**資料模型（designed）**：CharacterLearnedAction(character_id,action_kind,action_slot,cast_value,presentation_ref,revision)；若自行提供跨設備快捷布局則另表 ShortcutLayout(character_id,row,cell,type,slot,valid)。Session/snapshot generation 必須防止舊角色資料、舊快捷鍵指到另一個角色的新技能。不可把 display word、action slot、hotbar cell 或 C4D cast value 放進同一種 skill_id 欄。

main 2026-11-02 的新手普攻 row 前七 bytes 為 01 01 00 12 05 00 00（kind1/slot1/presentation18/mode5/use_flags0），CastValue0→C0E/C65 kind1/slot1。這是**現有 Server 重建的 issued-row subset**，不是官方普攻技能 ID18；C65 不可讓單一攻擊雙重扣血，其他 mode 不能一律當 C65 2bytes。

## 5. 未解問題、具名缺件及驗收

目前可引用 main 的 resource-index：Icon.dat 包含 skill.ypf（SHA b320a8b61258a464216a75b0e5fa58560a5abff0f17c2d7227cf66d8991ddc58）和 spell.ypf（SHA 20fbe76bfe39fb1070dee22bb5994227767aeab71a4b420839e75a4b6be83dac），但本輪未提供原始 **Icon.dat**，無法確認圖示 atlas/frame 與 presentation_word 對應。Basic.dat 的 ProtectorSkill.ypf 僅能當資源候選。官方技能定義 Skill*.dat/Spell*.dat 確切 filename 未獲 Client selector 證明，禁止捏造。

下一批精確 evidence_requests：① 0x444AFB / SkillSpellDialog / ActionListPane 的 render、tooltip、拖曳 callback，配 Icon.dat；② 0x489E60→0x489A30 的 Type/kind轉換、0x55BC40/0x55EBD7 config namespace 與持久化；③ 真正 learn/upgrade/delete UI producer 與 opcode；④ 原版進入 World 時的 S62/S63 packet trace、技能 icon/名字與 CastValue、跨角色/跨PC快捷列；⑤ C56 sender/施法階段。

**本次缺少的具名原件：Icon.dat**（目的：核對 skill.ypf、spell.ypf 的圖示，不需全部 Human）。Asgard.exe、Basic.dat 已有。原版 GUI/TCP/Server e2e not-run；A010-D01 **partial**、A-010 仍 integrated/handoff partial；CT-095/096 仍 planned/not-run。

驗證指令：

    python tools/a010d01_shortcut_probe.py Asgard.exe
    python -m unittest discover -s tools -p 'test_a010d01_shortcut_probe.py' -v

原件靜態 33 native windows + 3 config strings、15/15 Python tests PASS；這些不等於原版 Client GUI PASS。
