# A-021 原 Client 創角收發：靜態可證子集

來源：[`A-021 roy1 靜態報告`](../03-analysis-requests/A-021-roy1-static-analysis.md)；Evidence `ev_a021_20261031_asgard_static`；Client SHA-256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。

| 原生路徑 | Body（已驗證） | 對 Server 的規格影響 | 不得聲稱 |
|---|---|---|---|
| C02 serializer `0x5742b0`，UI 發送 `0x4b229f` | region 2..4：4×string8 + u8；其他：3×string8 | 必須按 region/profile 辨識欄位及嚴格限定合法前置狀態 | field1..4 語意或 Client 一定在無角帳號時進入 UI |
| S02 parser `0x57dbc0`，UI callback `0x4b1d60` | u8 status + string8 message | status=0 且 UI state 0x1d 的分支將發 C04；登入/創角不同狀態不能混用 status code 表 | 所有錯誤碼含義與取消行為已知 |
| C04 serializer `0x574420`，UI 發送 `0x4b205a` | u8 sex + u8 hair + RGB 3 bytes | 僅經前置成功路徑處理，應為每次 Session/角色操作關聯，並行/重送由 Server 保護 | 收到 C04 就表示已建立持久角色、必須立即發 S03 |

靜態 UI 路徑：事件 1→C02→state=0x1d→S02(status0)→C04→state=0x1e。帳號是否由 C02 建立、C03 無角帳號如何到此 UI、C04 後轉服與實際建角回覆仍 `unknown`。**R-025 是 Server 設計要求：Client 永遠不得建立 Account**；不可假借原生 C02 的名稱解除此限制。SCN-008、CT-011..014/018/019 維持待實機驗收。

合成 body 向量（非抓包）：C02/四字串 `016101620163016401`；C02/三字串 `016101620163`；C04 `0102112233`；S02 status0 + 空訊息 `0000`。未知字串語意不得在實作中命名為帳密或角色名。
