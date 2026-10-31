# A-019 / CT-060～062：原版音樂封包與地圖曲目證據驗收

2026-10-31。適用 Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。驗證依據：[A-019 原始 EXE/Map archive](../03-analysis-requests/A-019-roy1-map-music.md) / [音樂契約](../04-analysis-integration/A-019-map-music-contract.md) / [資源 SHA 與官方對照空表](../02-server-planning/map-music-evidence.json) / [離線工具](../tools/a019_music_map_probe.py)。下列均 planned；離線 signature/unit tests pass 不能算 native Client E2E passed。

## CT-060：Server→Client 音訊封包
1. 以相同 Client hash isolated sandbox 連線，測 S19 `01 00 00 12`：music track18 依本機 fixture 播放（如已有 `Music/00018.mp3`），含 `repeat0`。此 track18 是合成值，**不是某張官方地圖的歌**。
2. 送 S19 `01 00 00 00`，核對停止；音訊不存在/靜音時只記 audio failure，不改 World load success。
3. 分支 kind!=1：body `02 00 12` 為三 byte 其他音效 path，**沒有 repeat**。不要求其 exact kind2 原服 business semantics 或可播放的音效檔已證實；未知 kind 實際效果須錄到原版 UI 才可升級。
4. 調整/truncate body（缺 track 一 byte／多一 byte），用 Server parser 純合成測試負例，**不要故意向原版 Client 發惡意/長度錯誤封包做崩潰測試**。

## CT-061：地圖原曲目來源
1. 記 Map0.dat、Map1.dat、Map2.dat 的原始 SHA，解析 u32LE index count、36-byte entries；核對 `288+184+22=494` 個可辨識 `NNNNN.map`；其他 slot 保留原 bytes/hash，不將未知 entry 填歌。
2. 用**原版伺服器**或其確實可配對的 map-music 原始 table，在同 release 用 2 張以上地圖逐次 capture `S15.map_ref + S19(kind1,track)`（含原始時間、重登/返圖/音量/手動音效情境），才逐行填 official `MapMusicCatalog`；需區分任務/事件音樂與 map background，不能把同時發生誤判為固有地圖曲。
3. 若沒有原服 trace/table，**預期結果就是 official rows=0 / unknown**，不把 local track1、track18 自動填入；驗收「成功確認官方配表」維持 pending。

## CT-062：新 Server 的安全轉圖音樂
1. 在純 mock profile 對已驗證地圖/自訂 local-fixture 構造 `MusicCue`，S15/S14(1)→C35→S04/S14(2) 同 World generation/epoch 才推 S19；原版原服封包時序不從此推定。
2. 同 epoch/同 cue 重送不二播；不同 generation、載圖中斷、舊 pair C35 混淆時拒絕 stale cue。Client C35 不含 epoch，曖昧時 fail closed 並重新連線。
3. 無 source-proven song row 不發猜測曲目；若設計需切圖清音，明示 optional `S19(1,0,0)` 停止政策，不稱之為原版官方。
4. Player 音量0、Music/00018.mp3 缺檔、MP3 無法解碼、Client 停用音效時，音訊失敗不應使已完成的 World/Map state 回滾。
5. 真 Client multi-map E2E 應附版本、原曲來源、S15/S19 correlation、聽感/停止、斷線與 CT 結果；尚未執行不可 claim passed。

**具名缺檔**：本次無 `Music/00018.mp3`；其他正式曲目檔名需從原服對應曲號推得 `Music/NNNNN.mp3`，無法預先保證有哪些。原服 map→track 設定檔的**確切檔名未知**，不可憑空稱 `MapMusic.dat`。
