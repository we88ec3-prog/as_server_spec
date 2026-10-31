# A-031：C10 後的原版 C25 協定與 World 入口驗收（CT-110，承接 CT-108）

Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。BIN-first 證據：[A-031 原件研究](../task_a/roy2/A-031-analysis.md)。**原始 C25 是 CBillingInfoPacket 不是 WorldEntryMetadata。**

## CT-110：離線原生靜態＋合成 C10/C25 decoded body

```sh
python task_a/roy2/a031_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a031_world_entry.py' -v
```

驗證 native 35 instruction anchors + vtable RTTI：`0x5712E0` ctor opcode0x25、`0x571420` writer region3 guard、`0x45B1B0` string8 encoder、`0x4A8446→0x4A84F3`、`0x52FB8C→0x52FC4B` 兩條 C10→C25 流、另兩條 region3 C25 producer。合成 20 個測試：C10 raw token無額外長度、Region3 C25=3×(u8 byte length + raw encoded bytes)、empty body時 **`000000`**、max255×3、CP950 bytes保存、trailing及truncated fail-closed、非3已知直接 producer不期待 C25。

此 gate 只能確認原始 Client 靜態實作與 synthetic codec，不代表 socket 實際送出、選用 seed、區域政策或真 World 連線已成功。不得自動把 native CT-108 標 Passed。

## CT-108：需要原生 Client／真實 World 進入擷包（仍 planned / not-run）

1. **Region 3**：記錄無改版原版 Client C03→S03→新 TCP 首個 C10；核對 C10 raw token 不二次套長度；接著觀察真正的 **C25 三個 string8**，比對 `global+0x0C/+0x20C/+0x40E` UI/資料來源。遮蔽所有欄位原值、token及帳密，只保留 lengths、hash、codepage/region/seed、payload shape。
2. **非 Region 3**：各至少一筆有效持久角色的原版 Client trace，檢查是否 C10 後無 C25，以及 World 下一個 Client→Server／Server→Client 真 opcode；**不可**強制假 C25=01 或無 body C25，亦不可武斷主張完全不會送 C25。
3. 記錄 C10 與 C25 的真實 AA framing、seed/ordinal/密碼機制和 TCP 寫入順序；本次靜態 `0x5788A0` 是 enqueue，原生 wire byte order 需實際擷包核對。
4. 追本版 World 首個 S2C 是否 S02、S05、S15 或其他（**不得猜必有第二個 S02**），以及 S14(1)→C35 真 MAP checksum、S04/S33 與 MapPane/可操作入圖；要有原生 GUI 截圖及否定分支。
5. 錯 C10 token、C25 超長、region不合、非同期、斷線後重連、未存在持久角色、未匹配 map/CRC fail-closed；這些是 Server designed security acceptance。
6. 原版 Client runtime + SQLite/Postgres durable state 要與 DEV-ENTRY-03/04 分層驗收；synthetic fixture通過絕不能替代原生 CT-108。

**A-031 完成界線**：原版 static C25 body/兩條連續 sender 已證，`integrated/ready` 只限所述 Client wire 子集。真正原版 World GUI/實際 first S2C／失敗碼，CT-108 `not-run`。不需額外具名遊戲資源檔，缺的是同 SHA original Client 的遮敏 transfer/World wire capture。
