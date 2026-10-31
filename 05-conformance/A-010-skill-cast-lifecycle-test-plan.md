# 重要：以下 CT-095/096 是 main 新編號；原版技能 GUI not-run

# A-010 技能施放／持續效果 Client 原生驗收（CT-095／CT-096）

原件 `Asgard.exe` PE32 SHA256 `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。證據 [A-010 詳細報告](../task_a/roy2/A-010-analysis.md)。不可把解碼成功或 Server 合成模擬冒稱 Native Client E2E。

## CT-095：原件靜態與離線 decoded-body 確認

```sh
python task_a/roy2/a010_native_probe.py Asgard.exe
python -m unittest discover -s task_a/roy2 -p 'test_a010_skill_codec.py' -v
```

- SHA 鎖定原件：25 條特定位址 opcode/field/native reader/writer pattern + MSVC RTTI `CStartCastSpellPacket`、`CCastSpellPacket`、`SCastSpellPacket`、`SCancelCastSpellPacket`、`SAddLastingSpellPacket`、`SRemoveLastingSpellPacket`。
- C4D `BE u16` 由 `0x402034..0x402052` 真實 producer 取 `[ebx+0x80E]`；C56 `u8` sender 仍待 UI trace。
- S52 5B / S48 4B / S2D 4B 定長 strict length and trailing guard。
- S2C dynamic `BE u32,u8,u16,u8,string8,u8,u32,u32`，字串以 encoded byte length（max 255）讀，不允許固定當 UTF16 wire 或忽略檔外 byte。
- 合成測試：0、u16/u8/u32 極限、CP950 raw bytes、截斷每一 byte boundary、字串長度錯誤、額外尾 byte、重複 add/remove、map epoch stale。
- 此 gate 的本地「LastingSpellLedger」僅是 **Server designed synthetic sample**，不是原版 stacking/duration/recast policy；native Client GUI `not-run`。

## CT-096：原生 Client 技能施放、取消、BUFF/過期與效果視覺（planned / not-run）

1. 在官方同版 Client 的 World 介面選取一項明確技能，錄製 mouse/shortcut UI callback→是否產 C4D `BE u16`，以及此值與選取技能清單的 ID 對應。記錄 context / caster / target / spell 名稱，但不輸出帳密。
2. 分別記錄 C56 的真實 producer、在哪個選取/持續/結束狀態送出、是否必須跟 C4D 先後；不可只依兩個 packet 名稱推斷二階段 protocol。
3. 控制 Server 回覆 S52 每個實際可見的 u8 狀態和 S48 取消；截斷值/超時/地圖中斷/移動中斷/斷線，確認 local animation／UI 回滾。
4. 對真正 BUFF 類技能以原版 trace 確認 S2C 8 field body、圖示/描述/剩餘時間顯示、相同 ID 重送/刷新/疊加，再對照 S2D 移除。核對尾兩 u32 的時基或身份含義，不假設其中一個是 duration。
5. 對單體、AOE、治療、BUFF、召喚**逐類使用原版已證 skill ID**，追 C4D/C56/S13/S08/S07/S5F/S2C/S2D 的必要/條件分支；沒有相應原始技能資料則標 unknown，不生造數值/公式。
6. Server 冷卻/資源與權威 target legality 必須有自訂一致性測試；此 **Server designed** 不視為 original native Client evidence。
7. 交付原始輸入畫面、去識別 decoded packet + time order、資源檔 SHA（若取得）、相關 EXE VA，驗證成功/失敗/取消/逾時/重連每類情境。不能把僅合成範例標 native PASS。

**結案界線**：CT-095 native-static/offline subset 可用，CT-096 **planned/not-run**。原版 skill taxonomy/cooldown/MP/stack/expire 仍 unknown，A-010 靜態研究交付 `integrated/partial`。
