# Born 原生引導增量：具名啟動與獨立確認

## 目的與證據界線

承接使用者「新角色能進入新手教學移動」目標與 A-023 已證 Client 契約，
將本地既有 Born/Main 與 PaperDialog 接入已完成 C35 的世界入口。
這是復原 Server 的明確啟動政策；原服首次登入的精確發送政策仍未知。
Born 不包含 map_ref，接上 Born **不能證明目前 map6 是原版教學場景**。
它也不會生成 (31,29) 的女性招募員，NPC／招募任務仍需另接。

## 啟動前的原件檢查

Development／Region3／native-map profile 額外開啟 Born，引導設定必須
指定實際測試 Client 資料夾並明示採 CP950。嚴格核對該資料夾內：

| 資源 | raw SHA256 | CP950 原文字 CRC32 |
|---|---|---|
| Script/Born.dat | 992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98 | 1D87B0C0 |
| Script/PaperDialog.dat | 5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054 | F870C574 |
| Basic.dat | 0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96 | 不用作 script CRC |

解壓 Script：zlib→BEu16 version1＋BEu32 UTF-16 code-unit count＋原始
UTF-16LE XML。不得重排 XML；依 CP950 嚴格編碼後算 reflected CRC32
（poly EDB88320、初值／結尾 complement）。解壓上限 1MiB，檔頭長度、
文字編碼與 raw SHA／CRC 不符皆停止啟動，不以故意錯 CRC 探測 Client。
來源：A-023，原始 getter／runner 的 CRC mismatch 存在潛在懸空指標分支。

## Server 收發與 Client 反應

| 條件／事件 | Server 行為 | Client 反應／界線 |
|---|---|---|
| 同 owner/lease 的 C35 通過、進場已持久提交，尚未確認此版本引導，tutorial_completed=false | S04→S33→S14(2) 後送 S44(type1,subtype0) | 本地 Born＋PaperDialog 齊備後執行 Main，預期顯示引導紙張；GUI待驗 |
| S44 start | name=Born、非零隨機u32 context、CRC1D87B0C0、依賴1筆 PaperDialog/F870C574、參數0 | 不送任何刪除快取／資源更新 selector，不傳腳本原文 |
| C6C subtype4 | 驗同世界lease、腳本名Born及本次context；記已Dispose | 不變更角色／任務進度 |
| 接著 C6C subtype2 | 同樣驗證且需先有4；持久記錄此版本「引導已關閉」 | 不是入學、獎勵或教學完成 |
| 同context重複4/2 | 冪等接受，不重複產生事件 | 不額外發ACK或獎勵 |
| 錯context/name、2先於4、錯階段、舊lease | 拒絕，不保存確認 | 不讓偽造的紙張關閉完成教學 |
| 關閉連線前尚未有完整4→2 | 不保存確認，重登重新顯示 | 提供中斷後重送能力 |
| 已確認且版本相同，重新登入／Server重開 | 不再發此版Born | 目前座標照正常位置保存恢復 |

S44／C6C 完整 body 格式、原始 VA、證據 ID與固定向量沿用
[A-023契約](../task_a/roy2/A-023-script-entry-contract.md)。context 只存在
此 socket 的 Server 執行狀態，不是認證 token，不能取代 Account/Character
或 world generation。C6C(0) 缺檔請求、其他 SendReply／資源更新尚未接入
此最小 Born subset；正常相符資源預期不需下載。

## 確認儲存與版本

使用獨立事件 `tutorial.intro.born.ack:<sha256(intro_revision)>`，
以 Character＋event_kind 唯一寫入既有 World outbox，無新增 schema 遷移。
intro_revision 綁定 map content revision、Born／PaperDialog hashes 與 CP950
profile。事件保留完整 revision，與 world.entry.first 分開。
讀寫都以現行 world lease 鎖定並要求已有 committed map load；舊連線不可
替新連線確認。首次進場 checkpoint、onboarding step、tutorial_completed
完全不因此事件變更。後續真正招募／教學進度須走自己的權威判定。

## 驗證狀態

260項Server回歸通過。另以原始 Client byte signatures／真本地 Script
做離線契約核對；隔離本機 HTTP/TCP 測試涵蓋錯密碼重試→創角→自動
交接→C35→S44→C6C4/2重複→移動→重登保存位置及不重開已確認引導。
已測錯context、2先於4、失效連線不寫確認、引導關閉不完成教學。
這些不是 Client 真實紙張顯示／按鈕操作／行走驗收，仍待使用者實測。

測試入口新建角色模式會啟用本引導；一般既有角色試驗需明示啟用。
原始 EXE/DAT 與 Client Script 不修改，也不隨公開 spec 提交。

私有實作追溯：roy `5da03dd`，程式碼不隨公開規格提供。
