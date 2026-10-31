# Asgard Web 管理介面：分階段規劃與實作快照

2026-11-01 更新：唯讀查核 `as_server_roy@e93c9a17`，**WEB-P0 已實作／人工E2E獨立**；P1/P2角色／地圖／衣色／音樂／測試工作台仍待後端能力與頁面交付。本次只更新規格，不變更Server、HTML/JS、API、DB或Client。依 [使用者實作前確認規則](../00-governance/explicit-implementation-confirmation.md) 由DEV負責實作，分析者不得代改。

## 管理API與P0範圍（原始查核 be3d2444；最新補充 e93c9a17）

目前有受保護 HTTP JSON 管理 API，**`/admin-ui/` P0瀏覽器頁面亦已存在**，具建帳、查ID、停權／解封／救援重設與audit，不能再派工重建P0。ASP.NET Core Host 預設 `http://127.0.0.1:18080`，拒絕非 loopback；管理路由使用 `X-Admin-Key`（獨立密鑰長度至少32字，無密鑰則503），遊戲帳號密碼 **4～8 ASCII 英數、大小寫敏感**。

|實際已存在 API|P0 Web 介面用途|
|---|---|
|`GET /health/live`、`GET /health/ready`|服務與「玩家 Ready」分開顯示（ready 503 是設計上可能的未開放狀態）|
|`POST /admin/accounts`|管理員建帳（遊戲密碼4～8字；自動建議 CSPRNG 8字）|
|`GET /admin/accounts/{id}`|依 **Account ID** 查詢帳號／狀態|
|`PUT /admin/accounts/{id}/suspension`|停權1～3650日或永久|
|`DELETE /admin/accounts/{id}/suspension`|解除停權|
|`POST /admin/accounts/{id}/credential-reset`|重設玩家登入密碼（舊授權撤銷）|
|`GET /admin/audit?limit=50`|近期稽核紀錄只讀|
|`POST /admin/dev/characters`、`GET /admin/dev/world-scenes/{characterId}`|**只有 Development**，不得當正式玩家編輯工具|

注意：本規格 `admin-operations.json` 的 `/admin/v1`、`character.teleport/adjust`、`item.grant`、多角色 RBAC 是**未來設計**，不是上表實際 API。**目前也沒有帳號清單／名稱搜尋 API**，P0 不能假裝能搜尋。

## 預定 Web 資訊架構

- **P0 登入/連線區**：提供 Admin Key 暫時輸入及「解除鎖定／忘記本次 Key」；不是玩家登入，也不宣稱多位管理員身分已實作。
- **P0 總覽**：`live`、`ready`、環境/API 可用性，準確區分 Server 存活與是否可讓原版玩家進圖。
- **P0 帳號管理**：新建帳號、按 ID 讀取、指定天數/永久停權、解封、重設4～8字遊戲密碼；每次變更顯示 API 回覆與重新查詢結果。停權、重設必須確認帳號 ID 及操作後果。
- **P0 稽核**：近期操作列、UTC 時間／類型／目標／結果，絕不顯示明文密碼、token、原始封包或雜湊。
- **P1**：帳號名稱搜尋/列表/分頁、角色與 Session 查詢、稽核分頁與篩選，**需先新增對應 Server API 並再次確認實作範圍**。
- **P2**：角色傳送、角色狀態/道具管理、跨節點管理、真實 GM 權限、多人管理員 RBAC/MFA、外網 HTTPS；目前不提供可按的假按鈕，需另有後端權限、原版相容證據與安全方案。

## 技術提案（僅規劃）

**P0現已採用的方案**：同一 ASP.NET Core Host 在 loopback 提供 `/admin-ui/` 靜態頁面；前端以 same-origin `fetch('/admin/...')` 加 `X-Admin-Key` 呼叫現有 API。後續沿用此入口，先接真Server domain／API，不新增只會顯示成功的假按鈕。

- Key 僅儲存在頁面記憶體，刷新／關頁即清除；不得放 `localStorage`、`sessionStorage`、cookie、網址、console 或 log。建議 CSP、`Cache-Control:no-store`、nosniff、禁止第三方腳本，資料僅以安全純文字渲染；不啟用跨來源 CORS。
- 金鑰驗證/操作授權永遠由 Server 決定；現有單把共享 Key 的 API 沒有每人角色區分，不能用前端選單偽裝 RBAC。高風險動作二次確認、Server 稽核/冪等、限速與錯誤可讀性要明確。
- 錯誤分流：400 格式、401 Key 錯、404 ID 無效、409 衝突、503 未配置 Key/未就緒；新增資料 201、變更 204 後重新讀取。舊密碼不能截斷；不讓 UI 自己宣稱寫入成功。
- 現有只限本機 loopback；若未來開放遠端，需另行明確確認 TLS、管理身份/MFA、CSRF/CORS/Host 安全與防暴力使用，不可直接把 18080 對公網開放。

## 分段交付及阻塞

|階段|設計範圍|阻塞|本次狀態|
|---|---|---|---|
|WEB-P0|首頁＋金鑰欄＋建帳/查ID/停權/解封/重設/稽核|新版source已有頁面／API，人工E2E另記|source-implemented；不重做|
|WEB-P1|帳號清單/搜尋、角色與 Session 列表、稽核分頁|缺 Server list/search/role API、授權確認|規劃完成、不得實作|
|WEB-P2|正式 GM 操作、多使用者 RBAC/MFA、遠端管理|安全／權限／正式 Client 行為與業務決策|僅方向規劃|

驗收規劃 [WEBUI-P01..P10](../05-conformance/admin-web-management-acceptance-plan.md) 全是 `planned/not-run`。**下一次即使收到「實作」指示，先請使用者確認範圍，不得直接開始寫碼**。

## 原型能力恢復的本機角色工作台

[增量合約](prototype-parity-delivery-plan-20261101.md) 規劃角色查詢、衣櫃／獨立衣色、在線切圖、曲目與回報更正；這些尚無對應正式API，不是P0頁面已完成的功能。以現有localhost Admin Key安全邊界先規劃可用增量，不把外網RBAC/MFA當本機功能的必須前置；外網與多人管理仍另案。原型的Client啟動／EXE變體不併入遊戲Server domain。

## 最新決策：正常玩家不得靠 Admin Web 修改密碼（2026-10-31）

原版 Client 本身具有**更改密碼 UI**；玩家正常改密碼時必須從該遊戲 UI 進行，不能把管理端 `POST /admin/accounts/{id}/credential-reset` 當作玩家自助頁。管理端保留授權管理員 **救援/忘記密碼/初始化密碼** 的功能與審計，任何遊戲中改密碼只由查證後的原生封包路徑進後端同一 CredentialStore。更改密碼 UI 的欄位/opcode/回覆需 [A-029](../03-analysis-requests/requests.json)；本次只規劃，**即使後續要求實作 Web UI，也須先再確認範圍**。
