# A-019 — MapMusic 與 S19 曲目選擇的 Server 交接契約

[原生分析](../03-analysis-requests/A-019-roy1-map-music.md)； [機讀原件統計與空官方對照表](../02-server-planning/map-music-evidence.json)； [測試工具](../tools/a019_music_map_probe.py)。Client Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。**Client S19 音訊解析已證、Server 地圖→音樂政策未證**。

### 原生已確認

- `PKT-S19`（S2C opcode0x19）：`kind==1: u8=1,u8 repeat,u16_be track` (4-byte body)；`kind!=1: u8 kind,u16_be sound_id` (3-byte body)。Reader 0x584AE0, music handler 0x4F25D0→0x53CDC0，其他 sound handler 0x4F25F8→0x53D250。未知 kind 不當作可用合法音效枚舉。
- 音樂檔名按 `%05d.mp3` 格式組裝；對應 `Music` 路徑，數值 `track=0` 進停止/清除音樂路徑；本機 `01000012`／`01000000` 是合成 fixtures，**非 map1/map18 官方曲目**。
- 三份 Map*.dat 原件 SHA 固定、archive index 正式名稱 **288+184+22=494 個 *.map**；各索引未列音樂檔或證實對照。沒有完整原始 map→track 資料表。

### Designed 配置（不假裝原服）

`MapMusicCatalog(profile,content_revision,map_ref,track,repeat,source_evidence,origin_verified)`、`MusicCue(session_generation,loading_epoch,map_ref,revision,cue_kind,track)`。正式 verified `map_track_bindings=[]` 時不得預設 test track1，也不能用 `map_ref` 當 `track`；`origin=local-fixture` 必須與原版內容區分。

World 選定合法 map/ref/revision → S15/S14/C35 的內部 epoch 驗證 → 設計上在 InWorld 後依 verified catalog 發 S19；若缺 verified row，**不自動送曲目**，可按產品選擇顯式 stop policy `S19(1,0,0)`（designed），並保留目前音樂政策未知的狀態。舊 generation/reconnect/重複 map pending 需拒絕 stale audio cue。同一 map epoch/cue nonce 只處理一次。Client 是否啟用音樂/音量及 MP3 實際存在與否不影響 World transition commit。

### 交付/門檻

**A-019 status integrated / handoff partial / implementation_ready=true（限 S19 codec、來源驗證型 catalog、轉圖安全 cue）**。正式 Native map→track ready **false**；原原服完整切圖→音樂政策、music asset 是否存在及實機驗收未證。SCN-006 保持 manual-pass-subset；CT-005/006 合成不變、新增 CT-060/061/062 planned。需要原版 map+S19 trace、原服 map music table 或證實內容來源才可加入真正官方 track row。缺少的合成播放示例檔名 `Music/00018.mp3`，其存在與否不能證明地圖關聯。
