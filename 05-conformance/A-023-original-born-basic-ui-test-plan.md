# CT-112／A-023：原始 Born／Basic 素材與 S44 Type2 UI 分派（靜態）驗收

**不含原版 Client GUI/Server runtime**；原始 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。對應證據 [A023-E19～E24](../task_a/roy2/A-023-born-basic-native-dispatch-20261101.md)。

## Original-source local gate（original asset required）

```bash
python task_a/roy2/a023_native_script_dispatch_probe.py Asgard.exe
python task_a/roy2/a023_born_basic_probe.py --born Born.dat --basic Basic.dat
# 若拿到 exact PaperDialog.dat 原件，再跑完整 dependency
python task_a/roy2/a023_born_basic_probe.py --born Born.dat --basic Basic.dat --paper PaperDialog.dat
```

- 校驗 Client SHA and 22 original native VA bytes，包括 `0x4E0B87` type2、`0x4E0BAA` slot0x23、`0x4E0C3E` subtype2、`0x4E0C48` slot0x24、`0x52C2CA` type1 dispatch 和 `0x52C014` Main。
- 校驗 Born SHA、zlib、BE u16 version/BE u32 UTF16 units、CP950 text CRC `1D87B0C0`、唯一 Main 及 `PaperDialog_Create` reference。
- 校驗 Basic.dat indexed 39-slot archive 首 offset與 EOF、38 member 連續範圍／名稱、`AlertFrame.ypf` SHA、member offset 13196、size177648、version17、width348/height85 header。
- **沒有 `PaperDialog.dat` 時只能標「歷史依賴證據」，不標此輪全資源 GUI 完成**。即使有，也不代表原本 Server 會在哪個時點發送 Born 或 UI 實機已成功。
- 這些驗證器 read-only；不可把原版 EXE、Script 文字、Graphic 原件放進 GitHub/CI。

## GitHub CI 的 synthetic fixture

```bash
python3 -m unittest discover -s task_a/roy2 -p 'test_a023_born_basic.py' -v
```

21 個正負向案例，覆蓋 DAT 36B slot + EOF sentinel、空／錯位 member、非法或重複名稱、script BEu16+BEu32 codeunit、zlib 短包或尾綴、多於 65535 code units、欠缺原始檔明確拒絕等。合成 fixture 的 PASS 不得冒稱 native Client GUI 或原版 Server first-login PASS。

## 原版 Client 後續 Native CT-033/034/035（本輪維持 not-run）

- **CT-033**：需以隔離/可恢復資源環境驗 S44 1/0 start、缺檔 1/1 更新、C6C 0/4/2；S44 type1/subtype3 **會刪 Script cache**，禁止把它當 generic ACK。
- **CT-034**：在真實首次 World 進入（不是 Dev synthetic map）驗 Script 是否自動下發、何時顯示 Born/PaperDialog、S44 1/0、載入序列、女性招募員實際 NPC ID/map/position/點擊/相應對話。沒有原版 Server 事件／封包或 NPC 設定時必須保持「原服觸發 unknown」，不能自己捏造首次原服旗標。
- **CT-035**：正常關閉 Born 的 Client C6C(4)→C6C(2)，重播/斷線/重入時不會被 Server 當任務完成。對於獨立 C6C(1) 的 `STATE=ACCEPT/REFUSE` 候選入學 Script，要先核對 entity→script binding；拒絕零副作用且可再次點擊屬設計要求，不是原服已證行為。
- **Source boundary**：`PaperDialog.dat`（正確 SHA 版）是 Born.Main 必需的 Script 依賴；若需進一步比對 nNewJoin01/Merchant，具體檔名為 `nNewJoin01.dat`、`Merchant.dat`。本輪未取得這幾份原件，已有既有報告但未重測。P0「角色進 World 可行走」不因這些 P1 教學素材而卡住。

**驗收標記**：CT-112 `original-native-static subset passed locally + CI synthetic passed`；**full native Script GUI / original Server auto trigger CT-033/034/035 not-run**。
