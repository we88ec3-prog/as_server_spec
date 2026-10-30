# A-014／roy2 — 聊天、群組、密語、公會：原版 Client BIN-first 研究

- **範圍**：R-015 / SYS-SOCIAL，Client UI → C2S 封包序列化 → S2C parser → 本機成員顯示；非法操作、斷線與多連線交接由 Server 另有 **designed** 策略。不是原服 Server 原始碼，也不是原生 E2E。
- **版本證據**：原始 `Asgard.exe` PE32 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，profile `TW-seed0-local-v0.1`；RTTI 類別描述子及 class vtable → 實際 constructor 中 `push opcode` → native field writer / reader。原件無改寫，只有可以分享的位址/欄位。
- **證據層級**：`observed-static`=原 EXE 指令，`inferred`=根據 class 名稱猜測功能，`designed`=Server 暫定安全策略，`unknown`=未看到原服協定/回覆；原生 Client E2E=`not-run`。

## 1. 功能存在性與 BIN 連結，不靠字串空猜

EXE UTF-16LE 來源符號 `ChatInputDialog.cpp`、`FriendListDialog.cpp`、`GroupMemberDialog.cpp`、`GuildListDialog.cpp`、`WhisperTargetDialog.cpp`、`InputChat`、`InputWhisper`、`InputShoutToGroup`、`InputShoutToGuild` 及 `Game.ShowGroup`、`Game.ShowWhisper` 證明 **Client 有這些 UI／輸入入口**。這些名稱本身不證明原服允許創建公會、踢人、邀請或有獨立 guild wire opcode。

RTTI class descriptor 在原 EXE `.data`：`CGroupPacket@0x6694C4`、`CMemberListPacket@0x669558`、`CSayPacket@0x669760`、`CWhisperPacket@0x669994`、`SMemberListPacket@0x669DB0`、`SMessagePacket@0x669DF0`、`SSayPacket@0x66A07C`、`SUpdateGroupMembersPacket@0x66A194`。透過 RTTI `CompleteObjectLocator` 追 vtable，再核對各建構函式傳入的實際 opcode，區分「真有類別／進入 parser」和「假設該類別所做的業務動作」。

|方向/代碼|native class、constructor/opcode|已證 decoded body 格式／分支|限制|
|---|---|---|---|
|C2S `0x0E`|CSayPacket `0x574FC0`，`0x575070` serializer|`type:u8, text:string8` (`0x45AB00` / `0x45B1B0`)|type → local/group/guild/shout 的對照仍需追 UI call site，不得填造|
|C2S `0x19`|CWhisperPacket `0x578220`，`0x5782D0` serializer|`type:u8, target:string8, text:string8`|type 具體值、不可送達/封鎖/密語回覆尚未完整驗證|
|C2S `0x2E`|CGroupPacket `0x572D30`，`0x572DE0` serializer|`op:u8`; op=0 `+name:string8`; op=1 `+name:string8 +flag1:u8(bool) +flag2:u8(bool)`; other op 僅寫 op|未知 op 可能有其它資料由其他方法寫入；type0/1 **不是**已證邀請/踢人/解散語意|
|C2S `0x12`|CMemberListPacket `0x573550`，`0x573600` serializer|`op:u8`; op0 `+sub:u8`; op1 `+sub:u8`, 再分 1..5，部分為 1/2 個 `string8`（各上限 30 bytes）、部分 `u8`；op2 `+sub:u8`，sub1 `+u32`，sub2 `+string8`; op3 `+sub:u8`，sub1/2 `+string8`|不可把不同 op/sub 誤解為同一種公會／好友操作；需逐 UI 呼叫點補語意|
|S2C `0x0A`|SMessagePacket `0x582150`，`0x582200` reader|`type:u8 + text:string16` 的讀取入口；`0x45B890` 以長度限制 `0x752F` 呼叫|既有 AUTH/SYS 中 S0A 用於狀態訊息；不應全部轉作聊天訊息|
|S2C `0x0D`|SSayPacket `0x586120`，`0x5861D0` reader|`type:u8, source_id:u32, text:string16`；type4 另外讀 `text2:string16, number:u32`|source_id 身分/可見範圍、type↔頻道名稱、type4 顯示語意待證|
|S2C `0x58`|SMemberListPacket `0x580040`，`0x5800F0` reader|`type:u8, subtype:u8`；後續資料由分支/別的函式進一步處理|成員清單原始逐列格式與成員上限仍 partial|
|S2C `0x3A`|SUpdateGroupMembersPacket `0x5887A0`，於 `0x5887CA` 檢查 subtype=5|`SUpdateGroupMembers` 類別存在，某 subtype5 建構階段額外初始化；內含 0x208B 步長之成員結構處理（`0x588800..0x588F20`）|內部 `0x208` 是本機結構不是 wire stride！不可把它當成封包長度或固定成員上限|

`string8` 是**編碼後 byte** 長度，該台灣 profile 使用 CP950 且上限 255 bytes（`CGroup/CMemberList` 部分呼叫限 30）。`string16` 是另一套兩位元組長度 reader，不要用 string8 拼接。raw TCP framing／XOR ordinal 依 `04-analysis-integration/transport.md`，這裡只列 **解碼後 body**，不假造原服成功回覆 fixture。

## 2. 逐頻道與群組／公會功能判定（證據層級）

|操作|Client 可確認項|Server 交接所需|狀態|
|---|---|---|---|
|一般附近發話|ChatInput UI + C0E type+text、S0D type+source+text|Server 以 sender session 決定 origin，投影同地圖/視野內合法接收者；受限制 type 拒絕|**observed-static wire**, route policy **designed**|
|密語|InputWhisper、C19 target+text，WhisperTargetDialog、S0D/S0A|Server 對 target 真實在線狀態、封鎖政策、名字正規化，錯誤回覆需另查原生 byte|**observed-static sender**，失敗結果 **unknown**|
|群組通話|InputShoutToGroup，C0E type 值的具體對照待查|Server 以該成員當下 group_id 分發，不能憑 client 宣稱群組|UI 存在 **observed-static**；type mapping **unknown**|
|公會通話|InputShoutToGuild、GuildListDialog、C0E type 對照待查|Server 按 guild_id/member 權威；不假設與 group 等同|UI 存在 **observed-static**；native guild protocol **unknown**|
|群組/名單操作|C2E、C12 與 S58/S3A，有操作型別和多分支|Server 驗證邀請者與被邀請者、在同一 group、當下權限、epoch 和原子成員更新|packet 架構 **observed-static**；每個 op 對應語意 **unknown**|
|好友/封鎖密語|FriendListDialog、`Friend%02d`、`BlockWhisper%02d` 設定名稱|本機設定≠已確認原服資料庫；不可直接改成 Server-backed 好友名單|UI/設定字串 **observed-static**，跨裝置同步 **unknown**|

**重要**：目前未從 EXE 取得有獨立 `CGuildPacket/SGuildPacket` 類名；這只是掃描範圍內的負面證據，**不是原版沒有公會功能**。Guild 很可能經共用 member/group 類或另一封包；未可證明前不執行原生 guild command。

## 3. Server 可直接採用的安全狀態／路由規格（全部 designed，非原服證明）

- `SocialSession(account_id, character_id, world_generation, connection_id, map_instance, group_id?, guild_id?)`。Client 不得指定發話者 ID；從已認證、仍有效的 world generation 取得。
- `say(neighborhood)` 只發送至同地圖/同 instance 的合法鄰域、保證不穿越 map epoch；`whisper` 使用標準化目標名定址已登入角色；`group/guild` 廣播只從伺服器權威會員關係決定收件者。
- `invite/accept/leave/kick/leader-change`：`expected_membership_revision` + 原子 member update / generation CAS；禁止踢非本群、低權限踢高權限、自己邀自己、重複加入、已過期邀請、跨 group/guild 冒領；不把 client op/sub 當權限。
- **離線**：定址收件者不在線要分離 `unknown/offline/blocked` 政策；若防帳號枚舉，可統一錯誤，這是本 Server **designed** 選擇。離線訊息持久化是獨立需求，不能自動假定。
- **重送/切服/斷線**：透過 session generation 使舊連線不可重複發話、不可二次接受邀請；重登入先從 DB/持久狀態重建 group projection，再發 S58/S3A（原生 subtype 尚須確認）。發話不可藉任意 C2S retry 產生複數訊息；如無 request ID，Server 僅以連線一次 delivery policy 控制，不能自稱原服 exactly-once。
- **文字安全**：string8 CP950 byte 長度、空字串、不能編碼字元、壞包、資料長度、控制碼、限速，先於廣播檢核；UTF-16LE 文字保留原始顯示語意，應依台灣 codepage 重建 Client 可表示的 bytes。
- **拒絕**：未知 type/op/sub、未認證、權限不足、好友封鎖、舊 generation、無 guild/group 之操作均不能改變其他玩家狀態。原版拒絕 S0A/S0D 的 *精確 status/type 文案* 仍 unknown；絕不可自創為已驗證的 native reply。

## 4. 正常與失敗測試、A/DEV/CT 分界

可執行 synthetic decoded-body fixture / membership model：
```sh
python -m unittest discover -s task_a/roy2 -p 'test_a014_social.py'
```

契約與負向測試詳見 [A-014-social-test-plan.md](../../05-conformance/A-014-social-test-plan.md)。**不要求先有新 Server 才研究**：A 逆向已證欄位可移交 DEV；原生 A-014 group/guild type/subtype 對照、收件路由與原服拒絕 status 需要後續 BIN UI crossrefs / 合法 Native traces。A-014 結論 `status=integrated, handoff_status=partial, native_client_validation=not-run`；可先實作純聊天/密語的已知 codec + 權威安全模型，群組/公會仍不可宣稱 native-compatible ready。
