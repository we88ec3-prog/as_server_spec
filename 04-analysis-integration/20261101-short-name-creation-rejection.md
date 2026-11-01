# 短角色名使創角停在連線中：Server 政策修正

## 使用者畫面與本地觀察

2026-11-01 16:22／16:23（UTC+8），使用者改用正確帳號後，仍回報創角
停在連線中；畫面 NAME 是兩個 ASCII 字元（例如w0）。診斷副本 SHA
沿用 `e5f7b1ac742afdda9c6ec30a8934267dfac10221e115f74c2acd6449a4832dba`。

Server build5da03dd 收到 C02(body25)，已通過帳密驗證，隨後以
`native-creation-denied-no-verified-s02-error` 關閉；validation domain=CHAR、
reason=CHAR_CREATION_DENIED，沒有 C04。唯讀查詢該試驗DB：Account1、
draft0、Character0。因此這輪不是已建立角色後的轉場失敗，也未提交外觀。

## 原因與來源分類

私有 Server 的名稱正規化設定 **3～24 CP950 encoded bytes**，短名在
建立草稿前即被拒絕。這是之前自行選定的保守政策，沒有原生3-byte最小
角色名證據。Client能送出本次兩字NAME，不應以該自行限制阻擋本階段。
此外，這類預期輸入錯誤當時只斷線、不送名稱錯誤提示，畫面便長時間
停在等待狀態。不要將此歸因於Windows更新或原始Client崩潰。

## 新 Server 規則（設計決策）

- 名稱改為 **1～24 CP950 bytes**，保留非空、無空白／控制字元與編碼
  驗證、既有正規化唯一性檢查。1-byte下限仍是本Server設計，不冒稱原服。
- 名稱政策拒絕具型別原因，去敏診斷使用 `CHAR_INVALID_NAME`，不記錄
  使用者實際名字、帳密或E-mail。
- 既有Development實驗S02模式下，名稱錯誤回 S02(status1,明確政策文字)，
  等待C15後允許重試。status1沿用既有實驗映射，原生畫面可見性尚待驗。
- 驗證失敗前已有的credential proof必須丟棄；沒有draft時才能這樣重置，
  不取消別人的草稿、不回滾已提交角色。重試C02重新驗證帳密，不沿用
  失敗嘗試的proof。錯誤期間不得發C04成功／World grant。
- 非實驗模式保留拒絕與精確原因，不把status1推廣成所有原版錯誤的定義。

## 驗證與下一步

261項Server測試通過，新增同一連線：非法名稱→S02錯誤→C15→合法w0→
C04保存；另以w0測C04後單次grant綁定及真本機TCP完整創角／進場／Born
關閉／移動／重登入位置。先前「單字A必須拒絕」的測試改為拒絕空白，
不再把舊政策當成不可修改的Client相容要求。

請使用者以新試驗Server保留同一短名重測，觀察是否收到C04、是否自動
交接，以及引導／行走。此處只有合成與Server/TCP測試通過，不宣稱原始
Client或目前診斷副本的完整創角進場已驗收。原始EXE／資源未修改。

私有實作追溯：roy `067d129`。
