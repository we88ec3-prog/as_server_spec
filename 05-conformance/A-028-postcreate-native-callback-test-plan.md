# A-028 增量回歸：CT-111 原生 C04／S02 後 UI 與直接入圖邊界

[原件靜態詳細證據](../task_a/roy2/A-028-postcreate-ui-native-followup.md)，SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。此檔只補**離線原生靜態與 synthetic 子集**；保留原本 CT-105/107/108 的實機直接 World 驗收需求。

## CT-111：原始 Client 證據及合成 S02/C04/C15 狀態回歸

```bash
python task_a/roy2/a028_native_postcreate_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a028_postcreate.py' -v
```

- **原始二進位**：31 native VA patterns，含 state0x1d→C04/state0x1e；state0x1e status0→UI cleanup；status!=0→C15(empty) +state1f；Region3 first modal skip；4 UI slots `0x0C/0x0B/0x0D/0x07` 釋放。
- **新證據**：Region3 final S02-success callback 建立 `0x4A9380` UI class；vtable0x609BBC→COL0x625970→TD0x6665D8 明確 `LoginDialogPane`。這是建構，不代表玩家必須手動二次登入。其初始化與 separate C03 producer 必須分辨。
- **區域限制**：Region0/1/2/4 這個 success callback 中不建立上述 LoginDialogPane；不能從沒有該 class 建構推導為一定不走轉服。
- **合成測試**：S02 精確 string8 bytes parser（截斷/尾部/255B、原始 CP950 bytes）、五個 C04 u8 邊界、S02 status0 final UI 清理、Region3 pane 建構、status1..255 C15 empty、focus special 3/4/17/18/26/31、modal special suppression。所有狀態模型僅表示 original native branch 的**有限可證子集**。
- **必須維持 unknown**：原版 Client final callback → background C03/S03/C10/World socket 的完整因果 xref 未證；`LoginDialogPane` ctor 本身沒有直接 C03 send；`0x4A8890` 回呼的 nonzero branch 可呼叫 `0x4A7D10` 不等於已證會自動觸發。
- 原始 Client E2E／Server 持久角色建立／官方 S02 錯誤狀態碼 **一律 not-run/unknown**，不可把 CT-111 PASS 當創角入 World 成功。

## 原版 CT-105/107/108 真實出場條件（維持 not-run）

1. Admin 預建空帳號，原版 GUI NewUser C02（不同 region 需核對 Native LABEL）、第一 S02(0)→C04、第二 S02(0)，且**畫面不要求使用者手動返回登入與再次輸入帳密**（ADR-008）。
2. 本地時間/連線 session/region/seed + 去敏每一個 C2S/S2C opcode，重點是 final S02(0) 後直至第一次 World 進圖；若背景有 C03、S03、C10，必須從**實際**封包記錄證明，不得由 LoginDialogPane ctor 推理。
3. Region3 若實際有 C25（A031）、S05/S15/S14/C35/S04/S33，記錄 codepage 與 hashed bytes 長度；non3 不強制 C25。
4. 失敗 S02、C15 及 UI/連線、回覆遺失/重送；Server 的 create transaction 與 postcreate owner/generation 不得因晚到 C15 回滾。
5. 原版 Client 無修改，只有 native GUI+實際 TCP trace 與重登資料持久測試通過，才可將直接入世界標 passed。

**需要的不是新的遊戲檔**。如實記錄原生 Client packet metadata，遮罩 ID/PASSWORD/NAME/E-MAIL/transfer token；**CT-111 synthetic static 不取代 CT-105/107/108**。
