# A-009／SYS-COMBAT 驗收計畫：Client 靜態合約與原生實機分離

原始檔：`Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。研究：[A-009](../task_a/roy2/A-009-analysis.md)。只有 `task_a/roy2` 分支，原始 EXE 不進 Git。

## CT-063：原版 EXE 離線驗證（本輪已 PASS）

```sh
python task_a/roy2/a009_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a009_combat.py' -v
```

- 原件 16 VA instruction patterns / 5 RTTI PASS。
- 15 組 synthetic tests PASS：C13 target BE u32、S5F 僅 u32、S13 14B 基底／31B 可選段／packed flags bit3/4、截斷與超量拒絕、S3D 已證簡單 subtype 的正負測試。
- 複雜 S3D subtype 與 C3D subtype 的所有 UI/原生回覆**未納入端對端測試**；不得把離線編解碼測試說成遊戲已可戰鬥。

## CT-064：原生 Client 戰鬥 E2E（planned，not-run）

1. 同版原 Client 完成登入／轉服／地圖與 NPC 生成。記錄本機角色／目標實際 object key、map epoch 與 packet decoded body。
2. 針對單擊與連擊分別確認 C13 writer 單一 BE u32、兩個 producer 的 Client 操作來源及非法 target 的 Client 本地反應。
3. Server 回放最小 S13（14B）及選配 S13（31B）；驗證旗標 0x01/0x08/0x10 混合、特效/命中/暴擊文字與 target/actor registry 對應。不要把 S13 的任意 32 位元欄位誤定為扣血值。
4. 完整追 S3D subtype0..15、C3D subtype0..15 的每個有效 variant。收集每個變長 string8/count、UI handler、負向拒絕；現有 safe codec 對未解變體刻意拒絕。
5. 觀察合法命中、miss、減血後 S08 通知、血量歸零與死亡 S5F、殘留屍體及最終 S0E 移除次序；確認是否有獨立復活/返回介面的 Server packet。
6. Server（**designed**）：超射程、不同圖/epoch、無效 ID、怪物已死亡、冷卻、角色死亡、非法負值、u32 溢位、重送/雙擊、斷線後延遲消息、同 tick 兩者死亡；測試權威 commit、去重與可見性廣播。
7. 產出遮蔽敏感資訊的 packet trace、原生畫面、Server event ID/epoch、每個結果對應的 opcode/欄位與 Client callback VA。錯誤歸屬分為 A（原生 wire/UI 解析缺陷）與 DEV（Server 政策/運算/排序）。

**狀態**：CT-063 offline subset 已獲本輪獨立證據，CT-064 native Client **not-run**。這兩者不得混同 A-009 靜態研究結案。
