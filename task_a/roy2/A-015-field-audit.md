# A-015／roy2：原始三庫 MAP 欄位級驗證與語意假說

- 2026-10-31；工作目錄與分支：`task_a/roy2/` / `task_a/roy2`。本輪**沒有建立新分支**。
- 原 Client `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，原始地圖 Map0/1/2 SHA 見 [A-015 主報告](A-015-analysis.md)；遊戲原件不放入共享 Git。
- 證據類別：函式 accessor 為 **observed-static**，494 張 MAP 的值域/數量是 **observed-static-resource**；符合 48×32 影像座標的 interpretation 為 **inferred**；沒有原生 Client E2E。

## BIN-first：三種尾部 record 可明確分型

|record|檔案內 offset／型別|原始 EXE 直接取值位置|已證 / 未證|
|---|---|---|---|
|7-byte|+0 `u8`（由 native bool-normalize），+1 `LE u16`，+3 `LE i16`，+5 `LE i16`|`0x4B2D70`，取 +0、+1、+3、+5；`0x4B2FDC..0x4B3083` 校驗|寬度/符號性已證；物件名稱/地圖邏輯意義未知|
|8-byte|+0 `LE u16`、+2 `LE u16`、+4 `LE u16`、+6 `LE u16`|`0x4B2DE0` 取 +0,+2,+4,+6；`0x4B30B0..0x4B312C`|寬度已證；+2/+4 是疑似像素座標，不得當成 NPC spawn|
|16-byte|+0 `LE u16`、+2 `LE u16`、+4 `LE u32`、+8 `LE u32`、+12 `LE u16`、+14 `LE u16`|`0x4B2E40` 逐欄讀取；`0x4B3150..0x4B3239`|欄位已證；+12/+14 是疑似像素座標，+0 不得直接當 NPC ID|

### 真實 494 張 MAP 的交叉驗證

|檔案|MAP 筆數|7B records|8B records|16B records|header +0 == +2|header +4 不同於 +2|
|---|---:|---:|---:|---:|---:|---:|
|Map0.dat|288|39,481|0|4|288|30|
|Map1.dat|184|30,523|306|523|184|2|
|Map2.dat|22|4,028|90|1,742|22|0|
|**合計**|**494**|**74,032**|**396**|**2,269**|**494**|**32**|

- MAP header `+0,+2,+4` 三個 `LE u16`；本版所有 MAP 的 +0/+2 值相同，**但第三個 +4 在 32 張呈現 1,1,4**，故不可將其簡化為兩個重複值。A-022 的 C35 第一欄來自 MAP header +4，這項差異尤其不能忽略。
- 7-byte record 的第一個 byte 在全部 74,032 筆中，`0=72,577`、`1=1,455`；native 以非零布林化。其後 `u16,i16,i16` 的業務用途未知。
- 8-byte record 的 `(+2,+4)` 共 **396/396** 組，以及 16-byte record 的 `(+12,+14)` 共 **2,269/2,269** 組，均滿足 `0≤x<width×48`、`0≤y<height×32`。已知畫面格尺度為 48×32，此為很強的**像素座標假說**，但位置也可能是視覺物件/裝飾偏移；不是新手出生位置或 NPC 生成證據。
- 16-byte 疑似 x 值 2,265/2,269 筆為 8 的倍數，疑似 y 值 2,253/2,269 筆為 8 的倍數。這支持美術資產/圖層對齊假說，不能直接轉為角色走路單位。
- 7B/8B/16B records 分別出現在 **490/34/58 張**地圖。已有前段索引、block/tile、tail/EOF、494 SHA 驗證，本輪主要是深入欄位型別與版號風險，非重複聲稱整張地圖的所有遊戲語意已解。

## 可重現、負向測試及文件邊界

```sh
python task_a/roy2/a015_field_audit.py Map0.dat Map1.dat Map2.dat --json /private/a015-fields.json
python -m unittest discover -s task_a/roy2 -p 'test_a015_field_audit.py'
```

上傳的三份原始庫跑完整統計 **494/494 PASS**；4 個合成單元測試（正常欄位、座標超界、損壞 MAP、截斷 archive）全部 PASS。公開結果只含總數/欄位型別，不含任何原始遊戲素材。

## A-015 狀態決議（不切換 A-016）

研究規格可交付：DAT/MAP/Script/YPF 已確定的格式、MAP 三尾段的欄位型別、原始全量資源 inventory 與可重現 metadata-only 探針，並區分未知語意與版權/散布許可。

**仍缺** Human/衣服/髮型等原始 YPF 全量樣本、技能與物品定義檔真實位置及原始欄位、資料與 EXE 發行版對應 manifest、真正的 tutorial map/spawn/NPC 與校驗第二欄。原始資源從未推到共享 Git；格式可讀不等於有權散布。

`A-015.status=integrated` 僅已證格式子集，`handoff_status=partial`，`native_client_validation=not-run`。因 A-015 尚未完成其完整內容來源調查，**不啟動 A-016**，等待取得相關資料或進一步 BIN-first 分析；CT-039 的 MAP 離線檢查已通過，CT-040 原生 Client 教學仍未執行。
