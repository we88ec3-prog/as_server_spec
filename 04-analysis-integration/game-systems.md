# 遊戲系統解析的整合格式

每個SYS建立一份規則頁；目前systems.json是責任索引，不是已完成全部規則。

每頁應有：玩家目標、領域資料（定義／實例／關係／所有者）、觸發輸入、可觀察輸出、狀態機、公式與單位、時間與順序、交易／冪等／權限、資料版本、相關PKT／SCN／CT、證據等級、未知A及自訂規則profile。

優先完整化：AUTH/CHAR/WORLD/MOVE/LOOK/ITEM/PERSIST。STATS/COMBAT/SKILL/NPC/QUEST/ECONOMY/SOCIAL目前保持待分析，不能用其他遊戲慣例補成原服公式。來源可為Client parser、UI或資源，但Server端掉落率、獎勵條件、AI、命中公式未必能從Client還原；找不到證據時應由產品規則明示設計。

音樂與鏡頭屬呈現投影，不應改變Domain world位置；衣色與髮色分開。視野的規則必須包含角色自己、他人、NPC、怪物與掉落物，物件ID重用也屬協定生命週期。
