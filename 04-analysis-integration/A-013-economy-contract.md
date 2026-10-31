# A-013 — Economy Client packet ↔ Server domain boundary (roy1)

[分析原件／完整表](../03-analysis-requests/A-013-roy1-economy-wire.md) ｜ 原 EXE SHA256 \`db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145\` ｜ evidence \`ev_a013_20261031_client_economy_wire_static\`。

**OBSERVED-STATIC**：\`C4A/S42\` = ExchangePacket，\`C39/S2F\` = MerchantPacket，\`C17/S6E\` = TradePacket；各有不同 type/subtype 和多態 payload。C4A subtype0..5、C39 7B common、C17 type0/3/128/130（還有僅 type 的 127 個 selector）已有 Native serializer；S42 subtype0..5、S2F subtype0..9、S6E type0..3 Native reader 也存在。這三對類別的名稱不能單獨證明倉庫、購買成功／拒絕、交易確定／取消的真正意義。原版 Server 經濟政策與金額上限 unknown。

**DESIGNED Server interface (not original Server protocol)**：
- EconomyIntent(observer, family_opcode, verified_subtype, raw_request, visible_target?, world_epoch, session_generation) → 驗證 state/identity/object_ref/距離，未驗證的子命令 fail closed。
- MerchantQuote(CatalogId, CatalogRevision, ItemTemplateId, UnitPrice, Currency, MaxQuantity, Expiry) 僅 Server catalog 可信，不能信 Client 表單價格；Buy/Sell 原子驗證背包空間、物品堆疊、錢額與庫存。
- VaultAccount(owner_id, container_id, slot, item_instance_id, quantity, revision) **只是一種 Server-only 倉庫設計選項**；在原生 C4A/S42 與 UI 操作映射驗證之前 **不啟用「原版倉庫」功能**。
- TradeSession(trade_id, account_a/b, offer_a/b, offer_revision, ready_epoch, confirm_a/b, state) 只有雙方權威確認同一 offer_revision 才以 durable DB transaction 同步轉移兩邊 item_instance IDs、stack、currency；每次修改 offer 使 ready/confirm 失效，斷線/逾期取消未成交保留、退還 reservation。
- 實際 commit 使用單一 ledger tx + token uniqueness + 可重送 receipt/outbox（Server-only），拒絕溢位/負數/同一物品兩筆交易/跨帳號持有/非本地近距離/已解除視野的 object_ref。Client 所見成功 S2F/S42/S6E 必須匹配目前已驗證的原生子命令與 UI，不能自行發明 outcome type。
- 不以 wire u32 width 推定原服金額上限；上限與價格為明示 designed profile，待原版 UI/資源確認後再調整。背包 S0F/S10/S37 通知屬相依 A-007，不能在 DB commit 前先回傳肯定成功。

**CT**：CT-087 native byte-signature + synthetic PASS；CT-088 商店/Exchange 原 Client 實機/錯誤碼 planned；CT-089 雙人交易/取消/斷線/重送 planned。研究 A013 integrated/partial，native Client not-run。實測偏差回開 A/DEV，不把 unknown 填 0。
