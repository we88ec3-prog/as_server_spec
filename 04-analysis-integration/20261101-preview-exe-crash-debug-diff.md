# RI-008：修改版 Preview 的記憶體存取違規排錯分析

日期：2026-11-01。**modified-preview-debug-only；絕非原始 Asgard.exe 的運行驗收證據**。全程讀取上傳 EXE 的 Bytes、PE headers 及 i386 指令；沒有執行或修改 Client/Server。

## 身份與二進位比較

| 類別 | 原始 Asgard.exe | 修改版 Asgard-main-menu-preview.exe |
|---|---|---|
| SHA256 | db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145 | e834a07d21807748561bafa7e9cca97195234a9b664ea9c20f9e83faafc8cb9d |
| 大小 | 3,235,840 | 3,239,936 bytes |
| PE | PE32/i386, ImageBase 0x400000 | PE32/i386, ImageBase 0x400000 |

修改版多出 .tipfix 區段，兩檔共同位址範圍有 41 個不同 byte / 18 個連續差異區塊，其中 8 個差異區塊位於 .text。修改版並非原始 Client，但兩檔的創角最終 S02 callback 0x4B206B..0x4B2180 和 Windows WER 錯誤指令 0x541264 前後的 Bytes 相同。

## 崩潰位置

Windows Application Error ID 1000 / WER 1001：Asgard-main-menu-preview.exe version 2.1.2.0，APPCRASH，ExceptionCode=0xC0000005，FaultOffset=0x00141264。按 PE 靜態映像基址，對應 VA 0x00541264。實際讀取修改版後的該指令為 mov dword ptr [eax+4],edx；函式 0x541250 先從 [esp+4] 取得 eax，並在第三參數為零時寫入該指標。如果 EAX 為 null、已釋放或不可寫就可能造成此存取違規。

已知創角 final S02(0) Region3 callback 在 0x4B212A 呼叫 0x541250；傳入的參數來自 [esi+0x64]，在此特定 caller 的情況可能是 UI 關聯物件指標失效。但 0x541250 存在多處其他 CALL 候選：不能只靠 fault RVA 判定該次必從 final S02 callback 進入，必須查 WER dump 的返回位址、EAX 與 call stack，才可定實際 caller。

## 修改版相關 Patch 候選（不能當成已證根因）

- VA 0x4A880D：原本 Region3 的 jne 0x4A882D 改為無條件 jmp 0x4A882D，會略過原版 Region3 特定 UI 操作。與 LoginDialogPane 子系統相近，值得優先檢查。
- VA 0x4A9660：UI 函式指標由 0x4A9508 改到 0x4A9495。
- VA 0x4A9913、0x489606：原本呼叫 0x560F00，改為 xor eax,eax 與 NOP，改變條件分支。
- VA 0x5409A3：push 1 改為 push 0，改變 UI 建立函式的參數。
- VA 0x4FC380：加入 jmp 至新 .tipfix RVA0x5D5000 的 trampoline；本次還沒有它與 crash 的直接證據。

這些修改都只描述修改版，**不得拿來反推原版游戲必有相同錯誤**。目前沒有 EAX 值、ExceptionInformation、實際 call stack、已存活的 dump，因此根因仍是強候選、非結案。

## 交接與下一步

先在本機確認 WER ReportArchive/ReportQueue 內的 dump 是否存在，優先取 WinDbg .ecxr、r eax ecx edx eip esp、kv；若不能取得 dump，再在測試版用原版未更動的 RVA 0x141264 位置作唯讀斷點抓暫存器/返回位址。若返回地址為 0x4B212F，再追 MakeInfoDialog [esi+0x64]；否則改追真正的 callsite。只需分享去敏化的暫存器/stack，不發布整份含秘密的記憶體 dump。

**分開處理 Server 問題：** Native Region3 C25 收到後停留 WorldGranted 且沒有 S05/S15/S14 的問題，已由 Server 原始碼 _worldFixture=null -> Continue() 確認，是獨立實作缺口。此次 UI 崩潰不得被誤寫成 C25 停頓的因果證據。
