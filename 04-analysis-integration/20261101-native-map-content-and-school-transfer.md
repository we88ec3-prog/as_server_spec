# 多地圖內容與新手學校傳送接線

使用者觀察：招募員可點選並接受，但沒有傳送、重開仍同對話；使用者推測下一步應切到另一個教學場景並與下一位 NPC 互動。原始 nNewJoin01 的接受文案確實詢問進入初級學校，但沒有 map_ref、座標或下一個 NPC ID，不能由文案造出官方地圖綁定。

## 已交付的內容基礎

Server 已有可重用的 MAP reader：驗 archive SHA、36B 索引、唯一五位數名稱、遞增 offsets 與精確 EOF sentinel；驗 MAP 尺寸、block/tile、7/8/16-byte 三類尾段與精確 EOF；產生 member SHA、C35 structural checksum、tile flags 與顯式出生點 fixture。現有 map6 移動試驗亦改用此 reader 並核對其固定 revision/checksum。

讀取既有三庫共494張MAP，C35 checksum及尺寸與[A-032獨立工具](../task_a/roy3/a032_c35_probe.py)全部一致。metadata見[內容目錄](native-map-catalog-20261101.json)；這是資源與離線公式交叉驗證，不是494張圖都通過GUI。各圖角色仍標unknown。

原生CRC feed為 `crc=(table[crc>>8]^(crc<<8)^byte)&0xFFFF`，table polynomial0x1021，不能換成一般直接XOR輸入的CRC16函式。tail7規範化bool並將兩個i16符號擴充為LEi32；tail8保持8B順序；tail16按既有A-032選出13B、略過+5..7。C35第一個u16用map_ref，不能用MAP raw header+4。新測例另核對負座標、bool normalization、忽略padding與非法hash/尾段等。

## 下一步 Server 行為

舊本地原型曾由管理功能實測在線切圖：S15、S14(1)、C35、S04/S33、S14(2)、BGM。它只檢查C35長度，不能照搬為新版權威校驗。新版需共用Npc/Skill/Admin/MapGate的載圖與提交核心，但各來源保有自己的授權。

1. NPC接受保存入學意圖，等該runner關閉後開始切圖；拒絕不切圖，重送不新增事件。已接受角色重登須按已提交階段接續，不重複無進展加入對話。
2. Server從已核對的內容目錄選目的圖、可站立出生點、NPC及對話綁定；官方來源未知的復原版設定須明示，不能讓Client自由指定目的地。
3. 每個角色僅一個pending transfer，綁lease/generation/connection、來源context、舊位置version、目的map/revision、校驗pair與期限。loading時暫停移動／互動。
4. C35正確才交易提交新可變位置及階段；不可覆寫不可變first-entry checkpoint或提早宣稱tutorial_completed。逾時／斷線保留上個已提交位置；新連線依已提交map挑內容。
5. 學校生活／戰鬥說明、職業選擇及傳送員要接到各自真實回覆契約；最後依已保存職業進相應城鎮，再標完整教學完成。生活／戰鬥腳本不送完成回覆的地方，不能偽造Client已回報。

以上是接線規劃。內容reader已實作與測試；在線學校傳送、選職、城鎮提交與完整GUI驗收仍未完成。
