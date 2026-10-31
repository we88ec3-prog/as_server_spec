# A-032 roy3 完整 C35 全庫與發送呼叫鏈交接

來源 task_a/roy3/A-032-roy3-full-c35-analysis.md、原先 A032 report、A005 native collision。原件 Asgard.exe、Map0/Map1/Map2 SHA pinned。證據 A032-E06..E12。

Trigger：S15 指定 map_ref 後 S14(1)，原版 handler0x4F23CB 進入 C35 sender。
Client sends：0x4F23F5 ctor C35 0x5733E0、0x4F240E header getter0x4B4850、0x4F241D CRC getter0x4B4890→0x4B3650、0x4F2428 enqueue0x5788A0；writer0x573490 依序2個 BEu16，body4B，不帶 map_ref/epoch。
Client receives：S15 map_ref、S14(1)，後續原 World S04/S33/S14(2) 需 GUI 驗收。
Client reaction：對已 loaded MapData 自本地 header+4 和 structured checksum 組 C35，原件全庫494/494確認，330組不同 pair、33 duplicate clusters，map_ref6/10000 pair均00040F90。完整 atlas canonical SHA256=8a0ba7ebe767385db7296de1ca0c3b999aa620e05e6ab1793db0e640f30c375a。
Evidence：原始 EXE SHA、7 call/jump edges+15 byte anchors、全部 494 MAP 的 CRC 本地核驗、原版檔 SHAs、20 項新回歸（原件測試需檔案存在；clean CI 不得冒充 original pass）。
Unknown：原版 GUI C35 當次真 body、官方 tutorial map_ref、合法出生 S04 viewport/facing、原版 C33/C11/S0B 玩家走路／障礙修正，Server 原服出生政策。

DEV-designed：C35 絕不能拿來識別 map_ref。綁定 Server 自行記錄的 authenticated loading session、pending map_ref、generation、archive/member SHA 與 4B checksum，嚴格比對、錯 map epoch/digest/missing pending fail-closed。CRC 不可取代 World grant。相同 payload的不同 map_ref 仍隔離 instance。

A032 靜態校驗子研究 complete；整體任務因 native GUI/合法 spawn/可走路徑未證保持 partial、CT-108/109 not-run。
