# A-014：社交聊天／密語／隊伍／公會 Server 契約（2026-10-31）

**來源**：[A-014 Client 原始碼位置與測試](../task_a/roy2/A-014-analysis.md)、[封包索引](../task_a/roy2/A-014-packet-index.json)。Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，目前 `integrated/handoff=partial/native_client_validation=not-run`。功能名稱與 UI 存在，不代表 Server 原版回覆與權限已知。

## 已驗 native decoded body（不含 framing/ordinal/XOR）

|封包|方向|已知部分|重要限制|
|---|---|---|---|
|C0E Say|C2S|`type:u8,text:string8`|type 對附近／群／公會／喊話尚未對上 UI 值|
|C19 Whisper|C2S|`type:u8,target:string8,text:string8`|離線／封鎖／未送達原版回覆未知|
|C2E Group|C2S|`op:u8`，op0 +name:string8，op1 +name:string8+2×u8|不能擅自將 op0/1 當確定邀請/踢人|
|C12 MemberList|C2S|op/subtype 分支；部分 +string8 或 +u8/u32|不同 op/sub 不可套固定 row schema|
|S0A Message|S2C|`type:u8,text:string16`|與 AUTH/其他提示共用，不都是聊天|
|S0D Say|S2C|`type:u8,source_id:u32_be,text:string8`；type4 另 `text2:string8,number:u32_be`|**修正 A-014 原報告誤標的 string16**：實際 `0x5861F2/0x58620D` 呼叫 `0x45B7A0`|
|S58 / S3A|S2C|type/subtype/分支已定位|S3A 的 `0x208` 是 Client 內存 stride，**不是 wire 成員 row**|

## 服務端授權與狀態（designed）

1. **來源身份**：所有 C0E/C19/C2E/C12 都從已綁定 World Session 的 Account/Character/generation 推導 sender；不信任 Client 字串或自行指定發話者。舊世代封包拒絕。
2. **路由**：附近聊天僅投送同 instance 且在 Server 定義的可見範圍；密語由 Server 正規化名字查受權角色；group/guild 只根據 Server 持久化 membership 投送。type 未核實前禁止錯誤映射為原版 native channel。
3. **群組操作**：`membership_revision` + 原子 CAS，重送/跨世代/非本群/無權操作 fail closed；未知 C2E/C12 op/sub 不變更成員或社交資料。
4. **字元與限速**：依已驗的 string8/string16 **分開** codec，CP950 以編碼後 byte 長度限制；非法文字、超限、失效 Session、惡意重複訊息/邀請拒絕。原 Client 沒有穩定全域 idempotency ID；不把 socket ordinal 當永續交易 ID。
5. **回覆/離線政策**：錯誤碼、好友封鎖、離線訊息持久化皆 unknown 或需產品設計決策；不能填造原服 opcode/type/value。Server designed 與 Client observed-static 在日誌與測試中分開標註。

## DEV／CT 範圍

- 可先開發：C0E/C19 decoded-body parser/encoder、S0D/S0A 型別差異、Session/群組權威邊界、未知 subtype 拒絕、限速/惡意字元/跨帳號測試；在未證原版 type/op 的情況不對真 Client 任意發明群／公會回覆。
- `CT-047`：聊天／密語格式與 sender spoof、禁言／跨世代拒絕；`CT-048`：群組／成員分支、原子 membership/security；均 `planned/native-client not-run`。專案最優先仍為 A-027 的預建帳號 owner 和 A-015/A-022 真正教程出生，不因社交子集可用而改變入門關鍵路徑。


**CT-049** 專門追原版群組／公會頻道 Client E2E、S0D 真實類型及成員清單回覆。CT-047/048 的合成 codec/security 成功不能代替 CT-049；Native Client 驗收仍 `not-run`。
