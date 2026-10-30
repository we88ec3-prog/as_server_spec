# A-003：創角欄位合法值／帳號角色關係的證據交接

來源：[A-003 roy1 BIN-first](../03-analysis-requests/A-003-roy1-create-legal-values.md)，樣本 Asgard.exe SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，證據 `ev_a003_20261031_asgard_create_palette_ui_static`；A-021/A-027/A-028 為配套。

## 原版已證事實

- C02 writer `0x5742b0`：region2..4 為 4×string8 + u8，其他為 3×string8；field1/field2 源自原 MakeInfoDialog 的兩個 edit，第三 edit 是第二欄的本地確認，不直接附加到 C02 兩欄。
- `0x4985dc/0x4985e8` 設 `0x91fed0` 為 region0→6、region1..4→12；`0x4b1a30` 在 region0 skip、其他 region 用 narrow NUL string length>=12 的本地 gate。**不是 Server 角色名最小長度/username 授權證據。**
- C04 `0x574420` 五 u8，原 UI sender `0x4b2031` 取預覽 state 兩個 byte + 以 `0x66422c` 十筆色表 index 轉 3-byte RGB；**C04 沒有單獨 character_name 欄位**。十色的完整原版 raw bytes/映射請看報告。
- Client `0x1d` 收 S02(0) 發 C04、`0x1e` 再收 S02(0) 走 UI `0x4b206b`，不直接 S03；S02(nonzero) 發 C15 CancelNewUser（empty）並進 0x1f；具體原服重名/性別非法的 status **unknown**。

## Server 開發可用子集（designed）

Wire：string8 byte-length 0..255、TW CP950 profile；C04 sex,hair,r,g,b each u8。色盤 0..9 是**原 Client UI 可選的十色**，不等於原 Server 獨立拒絕其他任意 RGB 的證據。sex/hair 僅 byte 格式已證，未取得原生 allowed-values 列表；獨立 Domain 按有證資源提供合法選項，不填猜測的 `0..N`。

安全：Admin 只在 Admin API 建 Account（R-025）；原 Client NewUser/C02 不能建立 Account 或靠名稱認領預建帳號。必須經原版兼容、Server 已驗證的 owner+session+generation 才能開始角色 pending；**A-027 的 native owner 路由仍 blocked**。C04 不含 name/request ID，須用 Server-side pending intent 綁定；建角 transaction 唯一/冪等；C15 不可刪已提交角色。若選擇一帳一角，必須明註為保守 designed profile，**不能宣稱原版原本就是一帳一角**。

重名、字元合法性、UTF-8/CP950 跨區、帳號與角色名稱是否相同、原服 S02 非零錯誤碼、單帳角色數：全部 unknown，Server 自訂策略與原服行為分開版本管理，發現原服確證再修改。

測試：`tools/a003_create_contract.py`（已用 stdlib unittest 合成通過）；`CT-052` 針對 color table、region、CP950、wire；`CT-053` 針對 pending owner、重名、CAS、C15、斷線/重送。都 `planned/native_client_validation=not-run`。SCN-008 保持 analysis-required（完整 native 身份+轉場未證）。A-003 `integrated/handoff_status=partial` 只表示已證靜態子集整合、不是原服角色完整創建兼容已完成。
