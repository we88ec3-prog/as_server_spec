# C35 第一欄語意勘誤：地圖編號與 MAP 檔頭分開

2026-11-01。此勘誤優先於 A-022、A-032 及舊規劃中「第一欄為 MAP
file offset+4」的解釋。不是使用者提出的遊戲規則，而是本次追查黑畫面／
斷線所得的程式證據修正。

## 原始程式靜態證據

樣本 Asgard.exe SHA256
`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`；
本次使用 Ghidra 12.1.4 經 REA 核對：

- `0x4B33A0(ushort map_ref, ...)` 將第一參數寫入 **MapData 物件+4**，
  亦用它格式化 `%05d.map`，以 `map_ref/10000+9` 選資源庫。
  MAP 檔案資料指標另外保存在物件 `+0x230`，檔頭三個 u16 分別讀入
  `+0x234/+0x238/+0x23C`。證據
  `ev_1ce701c694a9511f23343cdf343041fd6186040798538a2903084c83cc6be74d`。
- `0x4B4850` 回傳 `word[[MapPane+0xB4]+4]`，即上述物件地圖編號；
  不是檔案指標再加 4。證據
  `ev_b6714755ba8c37baca9d9a28f65cc50b0f4e28585ad81ccffe034089df40ca28`。
- `0x4F240E` 是呼叫 `0x4B4850` 的 CALL。Ghidra 此處沒有辨識出
  所屬 procedure，故不宣稱此次取得完整 S14 handler 偽碼。證據
  `ev_2a12713a6fdce38c06de8739176f6df71fb7be9d6375eab8a7f5efe3dee70cdd`。
- `0x573490` 依序序列化 C35 物件+0x18/+0x1A 兩個 BEu16。證據
  `ev_17ab566f7ddbfe36aae7758f1bf8e1bc4583709ad5352be08b6ccba26046d598`。

## 診斷副本實測與修正

使用者操作的區域 3 診斷副本，載入 map_ref=6 後，Server 型別化紀錄
收到 C35 第一欄 **6**、第二欄 **3984 (0F90)**；舊實作預期 4/3984，
因而主動斷線。原生 MAP 檔頭+4 確實為 4，但不能用作網路第一欄。
這是診斷副本的網路觀察，不等於原始未修改 Client 的畫面驗收。

| map_ref | 原始 MAP 檔頭+4 | structured checksum | 修正 C35 body |
|---:|---:|---:|---|
| 0 | 0 | 63A9 | 000063A9 |
| 6 | 4 | 0F90 | 00060F90 |
| 10000 | 4 | 0F90 | 27100F90 |
| 18001 | 18 | F892 | 4651F892 |
| 20001 | 22 | E9B9 | 4E21E9B9 |

地圖 6 與 10000 即使資源 payload 相同，C35 第一欄也不同。
C35 沒有 epoch/request ID；單一 pending loading、版本綁定與 session
隔離仍必要，同地圖晚到回覆的歧義仍存在。

Server 必須比對 pending map_ref 及完整 structured checksum。
保留獨立的原始資源 SHA／檔頭驗證，不能把檔頭 4 改成 6；不能放寬為
接受任意第一欄或任意 CRC。既有程式／診斷欄位 `HeaderWord` 暫保留相容
名稱，其 C35 語意是 map_ref；公開 fixture 的 `header_word` 則僅指原始
檔頭，另列 `c35_map_ref`，避免混用。

## 驗證與剩餘工作

修正後 248 項 Server 測試通過，另以隔離 DB 進行本機 HTTP/TCP smoke：
正確 00060F90 完成載入流程，錯誤 checksum 拒絕；回歸測試確認舊
00040F90 即使 checksum 正確也拒絕，而且不寫入進場 checkpoint。
這些不證明畫面已顯示，也不證明新手地圖、出生點或可走路徑。
下一步由使用者實測進圖，接著處理新角色銜接與權威移動。

實作追溯：私有 roy commit `5494a9b`（C35／ID預填）；後續 `367f442` 補上 C54。私有程式碼不隨 spec 公開。
