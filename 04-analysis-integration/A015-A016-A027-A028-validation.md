# task_a/roy1 + task_a/roy2 最新主線合併／驗證（2026-10-31）

## 本輪來源及合併邊界

起始 main `ae3f45af5a174f65650ac6f040e9192a0e9e8ee5`；roy2 新 A-015 head `408112044a9afcd4e31fa7d19dd357dfe9951677` 已 fast-forward。roy1 head `b933e254e5339d7800711c9dc0c1808166e24b3a` 的 A-016/A-027/A-028 分析以雙 parent merge `abf66bd14cc520d74a400108e8779cb3532e3e8c` 併入，沿用原本的 task_a 分支，不新增分支。結構化 PKT/SCN/CT 逐項交集整合，不直接覆蓋 roy2 A-015。原 roy1 新測試 CT-039～044 與 roy2 CT-039～040 撞號，因此 roy1 六項依序重編 CT-041～046，原來源中的歷史編號不代表主線最終 ID。

## 獨立做過的核驗

1. 本地 `Asgard.exe` PE32 i386：3,235,840 bytes、SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`，符合分析報告使用的版本。objdump spot-check：C02 writer `0x5742B0` 呼叫 string8 writer；`0x4B205F` 設 state=0x1E、`0x4B206B` 進成功 UI；`0x5715F0` 建 opcode0x15、`0x5716A0` 為 `ret` (empty body)、S02 error `0x4B1F1B` 送出 C15 並設 state0x1F。這是 BIN static 核對，沒有原 Client E2E。
2. 本地原始 `Map0.dat`、`Map1.dat`、`Map2.dat` SHA256 分別為 `dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761`／`8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b`／`5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb`。獨立撰寫解析器逐張核對 DAT 索引/EOF、MAP 尺寸、block、10B tile、三個 count + 7B/8B/16B records，得到 **288+184+22=494/494 PASS**；尾段總數 **74,032/396/2,269**，與 roy2 報告一致。沒有靠 checksum 或檔案名臆測遊戲地圖 ID。
3. `Born.dat` raw 589B SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`，可實際 zlib 解壓為 1154B；解析 `>HI` 得 `version 1, count 574`；XML 有 (31,29) 引導文案。修正 A-015 catalog 對 wrapper 的歷史簡化，不可解讀為 4-byte magic 再 16-bit count。PaperDialog.dat 原件本回合沒有，因此完整 dependency/CP950 CRC 等引用 roy2 報告，沒有冒稱獨立重跑。
4. A-016 的 SQLite crash/reopen、A-027 UI 模型、A-028 S02/C15 模型工具是作者提供的 synthetic/designed fixtures；本次以 EXE static／resource parser 交叉核對，不等於測過原 Client/原服的登入、教學與永久交易政策。

## 仍要保留 unknown

- 原服 Account preprovisioned identity 及 C03 無角色進 MakeInfoDialog 是否原生可達；C02 UI 確認字串不等於帳號授權。
- 原服 C04 實際 DB 提交點與完整成功後回登入畫面流程；S02(status0) 只證 UI，不等於自動 S03。
- 真教程 MAP ID/spawn/NPC entity、地圖內容與 Client 同發行版證據、C35 第二欄 structured checksum。
- C35 沒有 wire epoch；同一 TCP 的同 pair 舊包在資訊上不可判別，Server 必須額外保障 session boundary。
- 原服 Born 發送時機、任務/獎勵政策與 Script close 的遊戲意義；C6C2/4 非任務完成證明。

此頁是 **研究檢驗與 DEV 規劃 gate**，所有 native Client CT 仍 not-run；沒有使用不存在的真 Server 截包編造 PASS。分析子集 integrated/partial 可以交 DEV，不因缺實機而停工。

## 追加 roy2 A-014／A-015 closure 二次核對（2026-10-31）

最新 `task_a/roy2` 增量 `c97bf22c040b6ae1676b772f8b351284d9ee38a4` 透過雙親 `f73da39cf3121d19bf0d9ddf5a4ab021d8be222b` 合併。A-015 format inventory `handoff=ready` **只限格式/來源/可重現工具**，而 `original_tutorial_content_ready=false, implementation_ready=false, asset_release_match=unverified, native_client_validation=not-run` 不變。A-014 報告的 S0D 文字欄位有靜態誤判：本輪用原 Asgard.exe `0x5861D0` 確認先讀 type:u8 + source:u32，`0x5861F2` 與 type4 extra `0x58620D` 均 call `0x45B7A0` (string8)；S0A 的 `0x582218` 呼叫 `0x45B890` (string16)。已修正報告、機讀索引與主線 PKT-S0D，不能將 A014 原文字 string16 直接照抄成 Server codec。群組／公會 op/sub 仍 unknown。A014 源報告試驗 CT-041～043 與 roy1 衝突，主線 CT-047～049 獨立列號；皆 planned、native not-run。
