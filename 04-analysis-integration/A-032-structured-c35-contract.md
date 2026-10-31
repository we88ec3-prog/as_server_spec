# A-032：真 MAP 的 C35 靜態雙值整合契約

來源：task_a/roy3/A-032-roy3-native-map-c35.md、task_a/roy3/a032_c35_fixture.json、task_a/roy3/a032_c35_probe.py；原始樣本 SHA256 與算法定位見 A032-E01～E05。這是 Client 靜態證據的**部分整合**，不是原始 Client GUI 驗收。

## 可直接給 DEV 的已證範圍

- S15 第一個 BEu16 為 map_ref；以 map_ref / 10000 + 9 的 library 查找 Map0/1/2.dat 中格式 %05d.map。採用 SHA256 綁定整庫及 member bytes，拒絕其他版本與不存在的 map_ref。
- Client 在 S14(1) 的本地 MAP checksum 由 0x4B2EC0、CRC 單 byte 原語 0x43E0A0 計算；C35 為兩個 BEu16：MAP file header offset+4 LEu16（wire BE）與 structured checksum。不是 .map raw CRC；詳細 7/8/16B normalization 以 A32 報告與離線程式為準。
- 目前候選 map_ref=6 是 Map0.dat 的 00006.map，60×60，header=0x0004，初始靜態 CRC=0x0F90；C35 初始理論 body=00040F90。與 Map1.dat 的 10000.map payload 完全相同，仍是兩個不同 map_ref。
- 離線候選 tile path: (30,30)→(30,31)→(30,32)→(31,32)→(32,32)。每格都 in-bounds、raw flags=0；這**不能**提供原生 walkability、spawn/facing/viewport 成功保證。

## DEV 安全條件

1. 必須檢查 transfer/session、單一 loading epoch、map_ref、archive/member hash 與完整 C35 pair。只比對第一欄或接受任意 CRC 不合規。
2. 不得將 map_ref=6 當「原版新手教學地圖」，不得因 tile flags=0 即標合法出生／可走路，也不得把 Born.dat 的 (31,29) 當 player spawn。
3. 未經原版 Client C35 capture 對照、S04/S33/S14(2) 畫面驗收及 C33/S0B 行走/撞牆 CT-108/109，這個 fixture 只能作 **static-content-match**，不能升格 **native-validated-world-entry**。
4. 當 C35不一致、同 session 重複 loading、不同版本或記錄不到 Native 時，維持 fail-closed。

## 待測實驗

開通原生 World 首包（A-031/DEV-ENTRY-03）後，載入 map_ref=6：記 S15、S14(1)、原 Client C35 十六進位（遮罩帳號令牌）；成功後記 S04 四欄座標／S33 面向、可視地圖及玩家五步路徑的 C33/C11/S0B，再做 blocked tile 回滾。若 C35 與 00040F90 不同，先查是否 MapData 已被動態改動或版本不一致，**不要修改 Server 為任意 CRC 放行**。

### 現況

A-032 = integrated (已審靜態值子集) / handoff partial / native_client_validation not-run / overall implementation_ready=false。最初「合法出生位置、已觀察可走路徑」**尚未驗收**；缺的是可用原生 Client World session/封包與畫面紀錄，不是需要重新提供已上傳的五個原件。責任：A-032 靜態補正、A-005 碰撞追查、DEV-ENTRY-04/05 與 CT-108/109 原生確認。
