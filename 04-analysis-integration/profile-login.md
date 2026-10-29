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
