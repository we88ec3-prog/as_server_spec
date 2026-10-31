# A-011：NPC／Monster 資源 ID、點擊互動、動畫原生 Client 驗收（CT-067/068）

原始 `Asgard.exe` SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。所有可下載/可共用成果只包括非素材程式碼與邊界，不包含第三方 Monster 圖像或完整 DAT。

## CT-067：Native EXE static + synthetic mapping（離線可重跑）

```sh
python task_a/roy2/a011_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a011_resource.py' -v
```

驗證：
- 原始 SHA 鎖定、**29 native VA instruction patterns + 4 RTTI + 3 wide literals**。
- `WorldXX.dat` 7000..7023（24 筆）；`MonsterXX.dat` 8000..8042（43 筆），**字串前導 @ 並未傳入註冊器**。
- image ID `0x4000..` → lib `0x1F40+floor((id-0x4000)/10)`、slot `(id-0x4000)%10`。可用本 Client 已登錄 library 的 bounded range `0x4000..0x41AD` 只是一個 designed safe guard。
- S07 kind1/2/4 → MonsterObject ctor `0x4D6FA0`；不把「kind1=某怪物」當 native proof。
- C43 已證的兩個 producer 皆 type1/subtype4 + BE u32，未知 UI／所有 NPC 對話不推測。
- Motion selector 0..5 → three offsets +0x20/+0x30/+0x40 twice；16bit wrap explicitly coded，**不把 selector 0 命名 idle / attack**。
- 離線通過不等於 NPC/Monster 外觀或真實點擊動畫已測通。

## CT-068：原生 Client World NPC/Monster 互動、素材與動畫（planned, not-run）

1. 在同版原始 Client 完成 world entry、取得真實 S07 非空 kind1/2/4（objectKey，client image/motion fields，x/y）。用同版 `MonsterNN.dat` 內容與 XREF 核對最終 asset imageId 到庫內資源及畫面上指定角色。
2. 各 kind 先取 id 0x4000、0x4009、0x400A 及中高界圖像作非正式受控素材驗證，記錄實際檔內 member 是否存在及 YPF/DOI animation frames、pivot/group、方向、duration；不能用缺素材的空畫面當 Client 不支援該 type。
3. 對 NPC、怪物、非生命物件各做普通點擊/雙擊/選單/攻擊/互動，抓取 C43 type/body，確認是否等同 native 0x479DC7/0x4A23F8；若不是，逆向實際生產者，不強迫 NPCChatDialog 等於 C43。
4. 若收到 S34/S3C/S44，追到 NPCChatDialog/NPCHistoryDialog 的真實 GUI callback、打開/回覆/關閉/失敗分支。PaperDialog/Born 需另與 A-023 版本匹配。
5. S0C/S64 移動、S13 效果、S5F 死亡、S0E 移除與 local motion selector 的切換分開錄製；要求找到各 motion group 的實際動畫意義及最終 Server packet trigger。
6. 安全：無效 resource id、未載入檔案、重複 spawn、removed entity click、不同 map epoch、C43 偽造/越距及重送 fail closed（Server policy 為 **designed**）；不向 Native Client 發無上限資料。
7. 交付遮蔽敏感資訊的 decoded packet trace + 原生畫面 + objectkey/assetID/row kind/VA 完整對照；無法建立映射即保持 unknown。

**狀態**：A-011 原生 Client I/O 靜態子集可交；真實 NPC 素材、UI 點擊與動畫 runtime **not-run**，不得聲稱原版掉落／怪物 AI 已被驗收。

## 2026-11-01 A-011 新增原生靜態 CT-116 與更新真正 Native CT-083

**編號更正**：本頁既有 Roy2 局部 CT-067/068 是歷史來源 ID；main 統一映射為 **CT-082（離線）/CT-083（原版 Client Native）**，本輪新增 **CT-116（原始 S07 image source + C43 3 mode 離線）**。以 [CT-116 最新細則](A-011-s07-visual-source-c43-test-plan.md) 和 [完整證據](../task_a/roy2/A-011-native-s07-visual-id-c43-20261101.md) 為準。

**新的原生 static 結果**：S07 每筆固定共通欄 x/y、kind、object ref 之後的 **第五欄 BEu16**，native `0x57E456 [row+0x0C]`，被 `0x4F1A7F` 放在 MonsterObject descriptor 第一個 u16，經 `0x4D6FA0→0x4D2340→0x4D7530/0x4D7560` 完整接上 Monster library `8000..8042`、slot 0..9（safe imageID `0x4000..0x41AD`）；`row+0x222` variant_u16 存成另一個 float 欄，不是 image ID。C43 的 pane mode0/1/2 完整送 `type1/subtype0x04,0x10,0x40`，共用 pane+0x4C 的 BEu32 object ref。

```bash
python task_a/roy2/a011_s07_native_visual_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a011_s07_visual_chain.py' -v
```

已從同 SHA 原始 EXE 驗證 43 個 native VA 靜態錨點及 23 synthetic unit tests。**CT-083 不因 CT-116 通過就變成 Native Client GUI pass**：還缺同版 MonsterNN / WorldNN 原始檔 payload→YPF/DOI image/frame/group/direction 實際對照、NPC/怪物模板與地圖綁定、真正 mouse click→C43/C39→S34/S3C/S44/NPCChatDialog、原服 AI/drop/生成規則及 GUI 擷包。即使先前專案已記錄 Monster00/World00 五個 YPF member 索引，本輪並未收到該兩個 binary，不能直接從 10 image slots/庫對照 5 個 YPF member。
