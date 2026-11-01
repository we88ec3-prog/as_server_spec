# 原生測試Server背景音樂增量

## 來源與本輪範圍

使用者先前提出沒有BGM，舊原型已於2026-10-25得到「有聲音了」回饋。
新版Server原先沒有S19出包；本輪依使用者「繼續後續規劃／開發／待測」
指示接入，不把原型驗收當成新版驗收。

音樂封包與檔名依[A-019原生契約](A-019-map-music-contract.md)：
S2C19恰4bytes `kind1,repeat0,track:u16BE`，track0停止，其餘查找
Music/%05d.mp3。原件SHA與REA證據沿用該契約；本輪無修改原始素材。
目前只實作音樂分支，不宣稱其他kind音效或完整音訊系統已完成。

## 可獨立實作的Server政策

- 正式／一般Host預設不發cue。只有明示Development native-map trial
  才可配置local-policy cue；不得因缺少官方對照表默認把map_ref當track。
- 配置含map_ref、content revision、track及local-policy來源註記；啟用
  需操作者承認這是本地選曲。曲目為0..65535，repeat固定0。
- 非零track啟動前檢查絕對Music目錄下的固定五位數.mp3檔存在且非空；
  不接受檔名或路徑作為Client提供的曲目。0停止不要求音樂檔。
- 已驗owner／現行授權、C35內容及epoch持久提交後，S04/S33/S14(2)
  之後發一次S19，若有Born則排在Born之前。不在C25、載圖未完成或
  拒絕C35時播放。設定錯map／revision拒絕，不把舊cue套到其他地圖。
- 重新登入完成新epoch時再發同一配置。離開角色回LoginDialog不額外
  發S19，避免對登入UI猜測音樂處理；主選單本身的音樂由Client決定。
- 停止cue與「不發cue」不同，後者保留Client現況。音量／靜音不修改，
  音效裝置或解碼失敗不能回滾已提交的世界狀態。啟動選曲檔案檢查
  是配置驗證，與進場後的實際可聽見結果分開。

目前僅一張已配置測試圖的啟動政策，不含DB音樂管理、在線曲目變更、
Web播放器或官方map→track表，也不代表在線切圖已完成。沒有schema遷移。

## 實作與驗證

私有roy `fdb4d81`。270項Server測試通過；三輪真loopback HTTP/TCP
分別測本地曲目1、停止0、不發cue，同時回歸短名創角、Born、C35、
移動、重登位置與同TCP C0B→C03。另測S19固定向量01000012、01000000、
BE上界，配置未承認／非Development／缺圖／缺檔／空檔拒絕，錯CRC
不出音樂、map/revision不符拒絕。MP3 fixture測試僅證檔案存在與長度，
不是音樂解碼器測試。

隔離試驗入口明示選曲1，可選18或0，亦可停用cue；這是操作者設定，
不是正式Host自動fallback。metadata保留local origin與選曲，便於重現。
新版可聽見BGM與原始未修改Client音訊CT仍待驗。當前合併後CT音樂
編號為CT-067/068/069；舊分支CT-060/061/062是legacy來源ID，不能用來
標記主線教學／獎勵CT。
