# A-022/A-023 合併後獨立核對與限制（2026-10-31）

## Git ancestry

- 本次主線起始 `c640c4c0434d5def5577236585172ea3f7ed214d`。
- `task_a/roy1` head `c5e551f20d9efda7017ef13edf92e6fb100aefaf` 以兩 parent merge commit `d239bff30a8c0b71eebd2c3a3c7f923a2ca1005b` 併回主線。
- 目前 GitHub **沒有** `task_a/roy2` 這個分支 ref；原 roy2 研究位於 `analysis/A-023-roy2` head `af72c88cae538492558da8d8ed1c1163683b22b5`。研究文檔由 stage commit `f4cd4bbc23c5f26effceccf7e0174a9ecbaa9290` 加入，最後以兩 parent merge commit `7dd8d8639005fe37c2d4695ce226aa7760bd0f47` 納入完整 A-023 structured evidence。
- CT 編號衝突：main 已佔 CT-029～032（A-021），roy2 使用 CT-029～031（教學 Script），合併時將後者改為 CT-033～035，未抹掉既有 CT。

## 原版 EXE 實體重核

本回合本地實際存在 `Asgard.exe`，檔案大小 **3,235,840 bytes**，SHA256 **`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`**。以 `objdump -d -M intel` 重新檢查：

|VA|核對到的 machine instructions|裁定|
|---|---|---|
|0x573490|讀兩個 WORD offset +0x18/+0x1A，各呼叫 0x45ab40|C35 的兩欄 u16 writer 規格支持；實際每欄語意依 0x4B4850/0x4B2EC0 downstream|
|0x57ff30|0x45ade0 連三次，0x45adb0 連兩次，0x45b7a0 讀字串；flags 拆 bit0/1/5/6|S15 3×u16/2×u8/string8 獲實體核對，詳細 map refs 仍 partial|
|0x575210|先讀 +0x18 subtype、cmp 0x4、jump table 0x5752fc|C6C 有 subtype 0..4 分支；各 branch payload 不能直接套同個 schema|
|0x52c8df|由 `[0x66d13c]` 取得物件，`0x52c8e5: call 0x5294e0`|S44 特定分支進 Script 資源/快取管理；**風險隔離**，未執行實際刪檔|
|0x529570|本地路徑處理迴圈呼叫間接函數|Script 本地資源有檔案操作，不等於所有 S44 皆刪除；要追 IAT/branch 才能判定個別操作|

**驗證層級**：EXE identity 與上述 VA 的 static check；沒有原服 Runtime packet capture，沒有宣稱所有 bytes/parser 分支都完整驗證。A-022 其餘 MAP loader/CRC 解釋請回到原報告查 binary 交叉引用，完整 structural CRC fixture 仍缺官方 map bytes。

## Born 資源驗證的可重現性

Roy2 報告與 `task_a/roy2/verify_born.py` 記錄原始 Born.dat 589 bytes SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`；解壓 1154 bytes，唯一 Main，PaperDialog，引導 (31,29) 的女性招募員。**本回合本地沒有 Born.dat 原始 bytes，無法獨立再執行 validator**，因此本次裁定為「roy2 已記錄的 offline evidence + 程式可檢閱」，而非獨立原件 replay PASS；Raw 資源未加入 repo，客戶端與資源是否同版本未證。取得來源原件後用：

```sh
python task_a/roy2/verify_born.py /path/to/Born.dat
```

凡未能證實的首次出生 map、spawn、Born 自動觸發、NPC id、C04 後回覆／登入帳號證明都保持 `unknown`，交 A-015、A-027、A-028、A-012/A-024。Native Client CT 全是 `not-run`。
