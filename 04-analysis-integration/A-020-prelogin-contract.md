# A-020 — Metadata／選服／Script 的安全 Profile 與 Native 分支交接

來源：[A-020 BIN-first 研究](../03-analysis-requests/A-020-roy1-prelogin-branches.md)／`ev_a020_20261031_asgard_prelogin_branch_static`。指定 Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；本文件不是完整原服登入政策還原。

## 已證 Reader/Writer

- **C0F CMetaData**：`0x573a70`，type3 只有 u8；其他 type= u8 + u8 option + string8。Server 的 default accepted mode 仍僅已測 type3，不能把其他 type 全開。
- **S18 SMetaData**：`0x582dc0`，`u8 kind,u8 subtype`；kind0 讀 BE u16 count + `count*(string8,u32_be)`，本機 body `00030000` 是 subtype3 的零筆清單；kind1 是 string8+u32+compressed helper，尚無原服內容/成功測試。
- **C57 CMultiServer**：`0x573f40`，type1 request list 只需 u8，type0 再 u8 selected_id；invalid type 不成功。
- **S56 SMultiServer**：`0x584190`，壓縮 block 後的 u8 count、每筆 `u8 id,u32_be IPv4,u16_be port,u8 flag,3*string8`；local single-list profile is a tested fixture only.
- **C4B CStipulation**：`0x575670` + `0x575720: ret`，空 body。
- **S60 SStipulation**：`0x587190`，type0 讀 u32_be，type1 讀壓縮文字（local profile: `u16_be size,zlib CP950 NUL`）。其他 type 不得發 fake success。
- **C6C/S44**：沿用 A-023 原生 subtypes，S44(1,3) 清 Script cache，絕不發作無副作用 ACK；C6C3 本機 login no-op 不等於任務啟動。

## Server State / Security (designed)

`greeting → C62/C00/S00 → metadata(C0F3/S18 kind0) → C57(1)/S56 → C57(0,id) → optional C4B/S60 → credential-verified C03 → S03/C10` 是本機允許的 profile，不是唯一本地/原服可能時序。明確管理每階段可用 opcode、C57 id 是否在已發 list、S18/S56/S60 壓縮大小與展開上限、string8 byte length 和 CP950 有效性、連線 generation。未知 response type、順序與 CRC 異常要拒絕或隔離，不自行猜原版 status。**Metadata/Script/ServerList 不能授予帳號 owner 權限**；C03 要獨立驗證，C02 pre-auth 仍受 A-027 禁止 claim。

## CT 與未知

`tools/a020_prelogin_contract.py` 離線合成 fixture 測已證 C0F/C57、S18 kind0、S56 zlib list、S60 0/1、C4B empty/狀態拒絕；只證 schema/model，不是原 Client native E2E。新 CT-049/050 planned。S18 kind1 的真實壓縮資料/錯誤、region seed/key 與 S00 非零 UI、官方列表/公告及 first-login script scheduling 仍 unknown；需要**原服含正常/異常分支的登入封包或原 Server 設定**，不能用額外 DAT 檔盲猜。
