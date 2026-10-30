# 已有資源及地圖分析整合

本頁是既有研究的整理，沒有在本輪重新反編譯。以下為指定Client版本的靜態／結構驗證；資源存在不等於遊戲功能已完成。

## DAT封裝

已盤點945個.dat，其中628個符合相同索引，合計3407成員；其餘為316個壓縮Script及獨立Server.dat，不得套此格式。

|位置|格式／檢查|
|---|---|
|0|LE u32 slot_count n，包含結尾sentinel|
|4起|n個36-byte slot：LE u32 data_offset + 32-byte名稱buffer|
|第一筆data_offset|必須等於4+n*36|
|每成員大小|下一slot offset減本slot offset|
|最後slot|EOF offset；名稱區可能為殘留資料，不是有效名稱|

628個檔已檢查首offset、單調offset及EOF等於檔案長度。名稱在首NUL截止；韓文名稱解碼為CP949屬推斷，應保留raw name bytes。這是容器索引，不是物品屬性表。

## Script

316個Script/*.dat均可zlib解壓：bytes0..3=00010000（語意未知），bytes4..5為BE u16 UTF-16 code-unit數n，offset6後為UTF-16LE，總長必須6+2*n。315個為可解析XML，NDW為純文字。CDATA含Client腳本與介面API，不能視為完整Server任務／獎勵／AI邏輯。

BarberShopDialog的Gender、HairShape、HairColor與CreateHairShape/SetHairObject提供外觀預覽入口；Born為新手對話／座標導引，不能當登入或創角處理器。

## MAP結構

原生loader 0x4b33a0，檔名%05d.map，資源庫選擇map_id/10000+9。Map0/1/2分別有288/184/22個map，共494個；已全量驗證布局，0個結構錯誤。

|offset或順序|格式|目前語意|
|---|---|---|
|0..5|3個LE u16|讀取寬度已知，欄位語意未知|
|6、7|u8 width、u8 height|寬高已由native確認|
|8起|ceil(width/2)*ceil(height/4)*2 bytes|區塊大小已知，位元語意未知|
|區塊後|width*height筆，每筆10bytes：3個u16+1個u32|圖層／碰撞語意未完成|
|tile後|u32 count + count*7bytes|結構已知，語意未知|
|之後|u32 count + count*8bytes|結構已知，語意未知|
|之後|u32 count + 剩餘資料|最後記錄大小尚未證實|

00000.map為20×20、tile offset108、共400格；00001.map為124×185、tile offset5836。不能用這些結構驗證宣稱已完成碰撞或出生點可通行判斷；A-005/A-015負責補完。

## Human / YPF / DOI

Human有男女衣服mb/wb各102檔，髮型mh/wh各36檔；管理目錄在可用資源範圍內篩選，並非所有原始編號都已實測。w/s系列用途尚不能只靠檔名認定。

原生YPF loader 0x56ea20。已解出第一組frame，12個衣服／髮型樣本通過RLE行寬、非零alpha pixel數與palette stream消耗檢查；首幀預覽不是完整行走／動作還原。格式已知：u16版本17、兩u16 header尺寸、u32欄、u32 flags；flags bit0有512byte RGB565 palette。palette後u32為圖片資料absolute offset；metadata含group/frame數與額外區域。frame含4個signed u16 bounds、u32 frame flags及條件區塊。

alpha區有height個u32 rowoffset及u16 RLE run（高byte count，低byte alpha）；非零alpha pixel依序取palette index。樣本alpha為0..248，預覽工具縮放到255，但原引擎rounding仍未完整追查。DOI動作／方向、其餘frame group與替代通道仍未知，不能據首幀自行補動畫映射。

Evidence：MAP ev_e166a44f01c9de3b7eff7457a30e6279b8571b5a76afc7354812c14bf1331e27；YPF ev_118f7890a0a4321dda8b83065142403499e707a3620831c41800a1b4164b4be1。原始資產及抽取工具不隨規格分享；本頁描述格式以利各實作者自行驗證其持有的相符資料。

## Born.dat 本輪原件驗證（A-023）

zlib 589 bytes，SHA256 `992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98`，解壓 1154 bytes；`00010000` + BE u16 574 UTF-16LE units；XML 唯一 Main 建立 PaperDialog，提示往 **(31,29)** 找女性「招募員」並用滑鼠點選。它是導航目標而**非**已證出生座標/NPC ID。本檔無顯式 SendReply/quest/spawn。原始檔未放進共用 repo；資源是否與指定 EXE 同版尚未確認。見 [分析全文](../task_a/roy2/A-023-analysis.md)。
