# 海灘服／禮服的攻擊動作素材差異

2026-11-07。使用者回報穿著泳裝／禮服時沒有攻擊動作，並詢問是否原版設定。本輪只讀原始資源與既有 REA 證據，不修改 Client、圖片、腳本或 Server 呈現政策。

**可確認：兩性外觀1／2的第一個 YPF object，在目前普攻所選的方向動作範圍沒有任何影格序列。尚不能確認原版規則就是禁止穿著這些服裝攻擊。**

## 原生映射與命名界線

沿用 [普攻動作分析](20261101-basic-attack-motion-action-and-death.md) 的 `0x475240`／`ev_92fead1e1f0da9d37b95390d49402a4db5abf7f6f5f033f66277e1965e592b6b`：wire Motion4 在一般無武器分支映射到 `direction+24`，其他 Motion4 分支返回 `direction+56`。當 HumanInfo 的 bit0x800 未設，且 `(+0x13=0 且 +0x14=0) 或 +5=5` 時採前者；其餘 Motion4 情形採後者。這些是不同姿態選擇條件，不應簡化成所有情況都固定 action24。

歷史原型 `catalog.json` 將 sex0／1、clothing0／1／2 分別連到 mb／wb000／001／002。既有原件 `0x474f60`、`ev_9465200bc126c0c00fadba69055945408262bb3d343b94990bde6315dd1cd029` 也證明：普通 shape（bit0x800 未設）取 shape+4 的性別、shape+8 的衣服值，性別零選 `cloth+1000`，非零選 `cloth+2000`，資源成員索引1。DAT 成員原名另保留在 JSON；「海灘服／禮服」是既有開發衣櫃名稱，不代表已找到原版物品ID或穿戴規則。

**wire Motion4、YPF action index4、physical frame4 是不同命名空間。** 本次六個素材的 action index4 都非空，因此不能寫成「沒有 action4」；缺的是映射後的24..31／56..63序列。

## 實際讀取結果

使用私有工具 `tools/inspect_ypf_actions.py`，沿原件 YPF17 reader `0x56ea20` 解析第一個 object 的 frame/action metadata。每個 archive 通過索引界線檢查，slot0 是 DOI，slot1 是 YPF；source SHA、member SHA、原名 bytes、offset及精選 action 在 [機讀結果](20261107-clothing-attack-action-presence.json)。

| 性別／衣服 | 原件 archive | 第一object frames | action slots／非空 | action24..31各方向 | action56..63各方向 |
| --- | --- | --- | --- | --- | --- |
| 0／0 | Human/mb000.dat | 1792 | 730／304 | 8影格，raw合計850 | 6影格，raw合計670 |
| 0／1 | Human/mb001.dat | 168 | 730／32 | 0影格，raw合計0 | 0影格，raw合計0 |
| 0／2 | Human/mb002.dat | 168 | 730／32 | 0影格，raw合計0 | 0影格，raw合計0 |
| 1／0 | Human/wb000.dat | 1786 | 730／304 | 8影格，raw合計850 | 6影格，raw合計670 |
| 1／1 | Human/wb001.dat | 168 | 730／32 | 0影格，raw合計0 | 0影格，raw合計0 |
| 1／2 | Human/wb002.dat | 169 | 730／32 | 0影格，raw合計0 | 0影格，raw合計0 |

四個特殊服裝的非空 action 集合完全相同：`0..7、16..23、648..655、714..721`。共32個非空、698個空 action slot。攻擊範圍不是工具找不到索引，而是已讀取的 action element count 為零；也不是八個方向中只缺某個方向。

raw時間保留原數值，沒有把它當作完整 GUI 播放時間或網路延遲保證。所有六個 YPF 均宣告3個 object；本工具只分析第一個，不能假裝已完成其他 object、state、transition 或 DOI 的還原。

## 對開發的意義與待釐清處

目前 S13／自身動作若確實選到這些服裝的上述第一object action，資源缺序列足以解釋看不到揮拳。這是素材層的正面證據；原 Server 是否曾禁止戰鬥、臨時改外觀、選用另一動作／資源、或依其他裝備條件 fallback，仍沒有足夠證據。單憑檔名、只有少數動作或本次 GUI 回報，都不能把其中一種補法說成原版設定。

因此本輪沒有加入自動換成基礎衣服、替代站立／走路作攻擊、禁止傷害等政策。後續若需要重建相容行為，應另列為明確的 Server 設計選擇，並獨立驗證傷害、資源消耗、命中時間與他人視野，不掩蓋素材分析仍有的未知。

## 可重現檢查

對每個列出的 archive 執行 `python tools/inspect_ypf_actions.py <原件archive絕對路徑> 1 <暫存JSON絕對路徑>`，核對 archive/member SHA，再逐一比較 actions[24:32] 與 actions[56:64] 的 elements及duration_sum_raw。工具限制／來源雜湊也記錄在機讀結果中。完整索引僅保留於本地 `workspace/anal-roy-temp/equipment-unequip-20261107`，公開資料不包含美術影格或整份資源。

驗證界線：六素材靜態索引皆讀取成功；沒有啟動或操作使用者的遊戲，也沒有因此宣稱原生 Client／診斷副本 GUI 驗收成功。
