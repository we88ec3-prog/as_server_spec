# 候選分析結果契約

每個結果為單一JSON物件，UTF-8，沒有Markdown code fence。task_id必須存在
於tasks.json；export_id與baseline_commit、input_manifest_sha256從PACKAGE_ID.json
複製。已提供整包不等於已讀取，inspected_artifacts只列實際使用的artifact_id。

```json
{
  "schema_version": 1,
  "export_id": "從PACKAGE_ID.json複製",
  "baseline_commit": "從PACKAGE_ID.json複製",
  "input_manifest_sha256": "從PACKAGE_ID.json複製",
  "task_id": "A010-D02",
  "reviewer": "claude",
  "status": "partial",
  "inspected_artifacts": [],
  "unreviewed": [],
  "findings": [],
  "packet_changes": [],
  "evidence_requests": [],
  "unknowns": []
}
```

status僅`completed_scope`、`partial`、`needs_evidence`。completed_scope只代表
這個子任務的交付條件，不代表技能系統、原服復原或Native CT完成。

- `unreviewed[]`：`artifact_id,reason`；截斷／不可存取／未閱讀分開說明。
- `findings[]`：`id,classification,statement,evidence,limitations`。
  id用`task_id/reviewer/F001`避免不同模型F001互撞；classification為
  `observed_static`、`derived`、`server_design`或`needs_evidence`。
  evidence為陣列，每項`artifact_id,native_va,locator`；VA不適用可null，
  locator須指函式、分支、指令或資源函式，不能只有整檔名稱。
- `packet_changes[]`：`direction,opcode,field,type,wire_offset,local_offset,
  meaning,evidence_ids,confidence`。未知offset用null，不把本地欄當wire。
  direction用C2S或S2C；opcode用0xNN。0x2C是opcode，非方向縮寫。
- `evidence_requests[]`：`id,target,kind,why,expected_question`。
  kind例如procedure、callers、incoming_data_refs、handler_dispatch、
  resource_selector、runtime_observation。請求最小範圍，禁止要求全量JSON。
- `unknowns[]`：未解問題字串，說明是缺Client證據、可能Server-only規則，
  還是需要原生實機；三者不能混成「缺檔」。

本地整合時逐項核對export／manifest／原件SHA、檔案引用與結論，衝突保留
原值並另記修正證據，不因模型輸出JSON就直接改Server或正式封包規格。
