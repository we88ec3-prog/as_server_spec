# 最小登入profile：明示的可實作子集

本profile使用binary/table0、台灣CP950及單一local world endpoint。下列最小回覆已讓所測Client正常登入，不宣稱完整metadata／patching服務已還原。A-020負責補足原生其他分支。

|前置狀態|收到C2S body|Server行為／下一狀態|
|---|---|---|
|新登入連線|尚無packet|送raw 1b430a，等待AA frame|
|Connected|C62 ordinal0 body6172616d|SignatureAccepted|
|SignatureAccepted|C00 8-byte body|回plain S00 body 00 00000000 00 09 4e65786f6e496e632e 00；VersionAccepted|
|版本已接受|C6C body03|此最小profile不回；Script分支待分析|
|VersionAccepted|C0F body03|S18 body00030000；MetadataSent|
|MetadataSent|C57 body01|S56單項清單；ServerListSent|
|ServerListSent|C57 body0000|S60本機公告；LoginReady|
|ServerListSent或LoginReady|C4B空body|S60本機公告；LoginReady|
|已通過版本協商|C03帳密|錯誤回S02 status3/string8後可重試；正確回S03交接|

S00上述body：result0、u32值0（未解完整語意）、seed0、string8 key=NexonInc.、message_count0。不支援的版本與其他result不可假設同一格式。

S56 body：BE u16 compressed_size + zlib data。本profile單項解壓資料為：01 00 0100007f 3aa2 00 0a 4c6f63616c2054657374 00 00，代表本機測試fixture；其中第一個01是清單count，後接id00、address、port、flag00、string8名稱與兩個空string8；flag及extra的語意仍未知，不應臆造。3aa2為15010，可按設定改變。

S60 body：01 + BE u16 compressed_size + zlib(CP950公告文字+00)。原型用Local Test。這是本機公告，不是原服條款。

S03 body：BE u32值0x0100007f、BE u16 transfer_port、u8 token_size、opaque token。token內容由Server產生；本機目前24byte／60秒／一次性為設計策略，不是原Client強制固定值。Client轉連線送plain C10，body直接為token；Server驗證後接受C25，再進SCN-001世界初始化。

最低拒絕條件：簽章不符、重複版本握手、非法長度、無效／過期／重用token、無前置狀態的選服與進圖。原型允許部分中間狀態直接C03的相容行為，正式Server應公布接受集合並測試，不能無條件接受任意狀態的登入。

密碼、token及metadata原始body不應進分享紀錄；本頁的key及位址／埠是公開合成profile fixture，不含實際帳密。

## 先前已確認的metadata／Script細節

S18 parser 0x582dc0：type0的清單為u16 count，每項string8 name及u32 CRC；本機subtype3採空清單。handler 0x432f30在空清單時呼叫0x432360繼續清單流程。C57 serializer 0x573f40：subtype1無其他欄，subtype0後接u8 selected_id。S56 parser 0x584190讀count與每項id/address/port/flag/name/extra1/extra2；0x4332a0可更新本地清單cache並選服。

SScript為S44（constructor 0x5862e0，handler 0x52c2a0），**不可當成通用空成功回應**：type1/subtype3會走0x5294e0清理安裝目錄Script快取，具有刪檔副作用；其他subtype還有清單／壓縮文字分支。既有最小profile暫不回C6C，是明示相容策略。此項已知觀察不代表S44全部分支已解析；A-020仍須補完整狀態與作用。

登入失敗必須使用此畫面的S02/status3/string8；LoginDialog對S0A走default，不能用一般SMessage替代。成功路徑及錯誤後重試已人工通過；歷史文件內早期「待驗證」不能蓋過這個較晚驗收。
 
## A-001 更新：S00 資料型別與多 seed 支援邊界

`0x589B60` 對 `S00.result=0` 的 parser 明確讀 `BE u32 opaque`、`u8 seed`、`u8 key_len`、`raw key bytes`、`u8 message_count`、逐項 `string8`。資料位元上相當於 `string8 key`，但 key 必須按 raw bytes 作 XOR，不可額外經文字轉碼。result=1/2 為不同數量欄位與訊息清單，不能把非零結果誤當作正常 seed 切換。原 Client `0x53B630` 有 seed0..9 的原生生成分支；**只有 seed0 屬已知可登入 TW fixture**，seed1..9 本次是可重現 codec 合成單元測試、不是已完成原 Client E2E。詳見 [A-001](../03-analysis-requests/A-001-roy1-seed-and-version.md) / [測試工具](../tools/a001_codec_vectors.py) / [transport](transport.md)。

## A-002：S03/C10 的原生資料流與 Token 使用邊界

S03 parser `0x5886C0` 依序讀 BE u32 address、BE u16 port、u8 token_len、**raw token bytes**；在 region3/4，`0x4A8370` 以 address/port 建立後續連線，再透過 `0x577330/0x5773E0` 將 token 原文放入 C10（body raw bytes，無 string8 前綴）。S03 和 C03 的 opcode 同為 0x03，但方向及解碼不同；C10 為既有 binary profile 的 C2S plain opcode0x10 + token，無 ordinal。登入 TCP 關閉與 World C10 交接期間的 token 有效性由 Server grant lease 控制。原版 duplicate-login error 未確認，**不推測 S02 status 值**。見 [A-002](../03-analysis-requests/A-002-roy1-login-transfer.md)。

## A-020 / roy1：登入前原生封包各分支與 local fixture 分界（2026-10-31）

[完整 BIN-first](../03-analysis-requests/A-020-roy1-prelogin-branches.md)／[Server 安全交接](A-020-prelogin-contract.md)：
`C0F` 原生 CMetaData `0x573a70`，type3 僅 byte03，其他 type 多 u8 option+string8；`S18` 原生 SMetaData `0x582dc0` 先 u8 kind/u8 subtype，kind0 再 u16 BE count+（string8,u32BE）清單，所以本機 `00030000` 是 **kind0,subtype3,count0**；kind1 是不同的 name/u32+compressed helper，非同種 list。
`C57` 原生 CMultiServer `0x573f40`，type1 僅 01 要求清單，type0 為 00+selected_id；`S56` 原生 SMultiServer `0x584190` zlib 後先 u8 count、每筆 id/address/port/flag/3×string8。
`C4B` 原生 CStipulation `0x575720: ret` **空 body**；`S60` 原生 SStipulation `0x587190` type0 BE u32、type1 壓縮 CP950 文字。local C57(0)/C4B→S60 是**本機 Server 的 designed mapping**，非原服固定時序；region key、失敗 UI、S18 kind1 真內容、其他官方清單均 unknown。
`C6C(3)` 在現有 local profile 不回覆，不能假稱 Script start；S44 type1/subtype3 會清理本機 Script 快取，正式不得當安全 ACK。此研究 `integrated/handoff partial`，native E2E not-run；CT-049/050 planned。
