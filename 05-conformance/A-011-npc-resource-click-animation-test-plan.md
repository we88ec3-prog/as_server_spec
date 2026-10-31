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
