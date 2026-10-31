# Roy1/2/3 合併後 P0 分析／原版動態驗收缺口（2026-11-01）

## 已有原件，不應再重複要求
`Asgard.exe`、`Basic.dat`、`Locale.dat`、`Map0.dat`、`Map1.dat`、`Map2.dat`、`Born.dat` 均已提供且 SHA256 已核對。創角 NAME/EMAIL 原版資源 label 映射 **Region2..4 已解**；真 MAP 靜態 C35 pair **已解**；Region3 一般轉服 C25 是 `CBillingInfoPacket 3×string8` **已解**。不要再把它們列「完全未知」或要求重分析。

## P0 仍需分析／取得的具體證據（先後可並行）
|順序|任務|真正剩餘問題／觸發→C2S→S2C→Client 行為|可交付 DEV 的出口|
|---|---|---|---|
|1|**A-028 + A-031，首次創角成功的自動 World 轉場**|原版 `state0x1e+final S02(0)→0x4b206b` 之後何者在**沒有可見 LoginDialog 人工再登入**的情況下發起 World？是否背景 C03/S03/新 TCP C10？Region3 `LoginDialogPane` 是否只建構隱藏 UI／觸發 callback0x4A8890？先後的 C2S/S2C、TCP ID、body shape 必須從原版動態 trace 或更多 EXE dataflow 定案|依 region/狀態證成最小 PostCreateEntryContext → 正確 Client 原生 grant/transition；不能憑 user-visible flow 自造封包|
|2|**A-030／CT-104/105，原生 S02 非零 UI 與 C15**|Region2..4 NAME/F3 EMAIL/F4 已證，但 E-MAIL 是否空白仍會送 C02？S02 status=1 + text 是靜態候選，不是官方錯密碼狀態；原版 GUI 會提示/發 C15/留 socket 可重試嗎？所選 runtime region/seed 與帳號 Client ID 長度 gate 是否相容？|只啟用匹配 verified region/label/profile；驗 owner + credential version；合法 S02 stage1/2；失敗可見且不冒充 TCP 業務斷線|
|3|**A-031 + CT-108，一般登入的 World entry 回覆**|已證 Region3 S03→C10→C25 三個 opaque string8、non3 某路徑只 C10；**C10/C25 後原版到底何時接受 S05/S15/S14，是否另需 S02/S2C、transport phase？**|World routing 不再硬等 C25=01；C10 token 是唯一權威，依 profile 接 C25 optional；原版收到真正地圖資料|
|4|**A-032 + CT-108，真 MAP/S04/S33/出生可視**|初始 `map_ref=6` 的理論 C35 `00040F90`，但尚未觀察原版真正 C35；選定地圖的原生 S15/title/flags 與 S04 viewport/facing 是否讓 Client 顯示？**合法出生位置未知**，map6 不代表教學圖|版本/原件 SHA 鎖定 MapCatalog，capture true C35，原版可見人物與地圖；能在已驗出生座標停留|
|5|**A-005 + CT-109，原生玩家移動碰撞/校正**|C33 seq 回覆與 S0B bit7 分支已證，但 Client 的真正移動 step/方向、collision `0x4BE470→0x4C1850`、flags/動態 block、撞牆 rollback 與實際速度/回包時間仍不明|最小有界 Server-authoritative C11/C33+S0B，經原版 UI 實測可走5步與一次阻擋，禁止單靠 tile flags=0 判定可走|
|6|**A-015/023（首次真正教學圖，非 interim 走路的先決）**|目前無原版教學 map_ref/出生點/招募員實際 spawn，Born (31,29) 是文字引導；若最終必須進原版教學圖，需其證據，不能把 map6 擅當官方|先讓原版 Client 在原件已確認的安全地圖可操作，標 `native-interim-playable`；再把教學圖/首次腳本接入後才宣告 ONB-03 原教學圖通過|

## 要求的現場資料（沒有真帳密／信箱）
一段 **未修改原始 Asgard.exe SHA、選定 region/seed/Client version** 的本機 UI + TCP 去敏 trace：
1. 新建帳號：C02 收發 ordinal/field count/各欄編碼長度 → S02 status/message length → C04 body length → final S02 → **接下來 10 秒**所有 C2S/S2C opcode、frame length、時間、TCP connection ID、畫面是否出現 LoginDialog。
2. 一般既有角色登入：C03→S03（**遮蔽 token**）→新 TCP C10→Region3 C25（只記 body shape/長度）→第一個 World S2C。
3. 原版 World：S15(map_ref)/S14(1)→C35 二組 u16、S04 四欄、S33 角色、S14(2) → C11/C33(seq/mode)→S0B(status_seq,x/y)，包含合法 5 步和一次阻擋畫面。
4. 可另做錯密/停權／重名/空 E-MAIL：只記 S02(status/message length)、C15、socket timeout/FIN/RST，**不記原始明文/解密 C02 body**。異常斷線與正常 S03 transfer close 分開。

動態實測是 Server/CT 出場門檻，A 靜態子集已可交 DEV；不要因無法同時做原版 Client E2E 而將已證 A 分析全重開。若提供額外**教學互動**資源可再指定 `PaperDialog.dat`，但**首次成功創角→可移動的 P0 沒有新必缺原件檔名**。
