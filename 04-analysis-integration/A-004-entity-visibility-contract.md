# A-004 — World entity visibility / object-ref / disappearance Server contract

[原始 Client 證據](../03-analysis-requests/A-004-roy1-world-visibility.md)｜[合成驗收](../tools/a004_visibility_model.py)。Evidence `ev_a004_20261031_world_entity_visibility_bin_static`；Client SHA `db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145`。**原始 Client wire/lookup 已證；AOI/EntityId/epoch/revision 設計不等於原 Server 的固定政策。**

### Native packet codec (S2C)

- `S07 DrawObjects`: u16BE count + variable records, each begins u16BE(x),u16BE(y),u8(type),u32BE(object_ref),u16BE(attr). Reader 0x57e3e0, handlers 0x4f17c0; type1/2/4 optional flags/RGB/string8, type3 5×u8+string8, type5..12 none, type13 string8, type14 u8+u8+u16BE. All other meanings unknown. Bound count and frame on Server; same (type,ref) does not automatically imply durable persistent entity.
- `S33 PutHumanObject`: see appearance.md for u16 x/y, facing, u32BE object_ref and CP950 name/flags; not a generic monster spawn.
- `S0E RemoveObjects` u32BE ref only (0x585f10); `S5F DieObjects` u32BE ref only (0x57e260). **Not synonymous**; former is removal candidate, latter death/visual state candidate, native handler visual semantics not fully verified. Correction: the constructor opcode for DieObjects is **0x5F** at 0x57e1c9, not 0x1E at factory allocation 0x57e298.
- `S0C MoveObject`: u32BE ref +2×u16BE +2×u8 (0x583450).
- `S64 MovePath`: u32BE ref+2×u16BE+u8+path_len:u8+path_len×u8+2×u16BE+u8 (0x5835e0).
- `S11 ChangeDirection`: u32BE ref+u8 (0x57d770).
- `S1A Motion`: u32BE ref + u8 + u16BE + u8 (0x582fd0).
- `S05` own appearance, `S0B` own movement ack, `S15` clear old map others; do not substitute them for observer visibility events.

### DESIGNED lifetime and interest tracking

```text
WorldEntity(entity_id[server stable], kind, world_instance, map_id, state, revision)
ClientRef(viewer_connection,generation,map_epoch,wire_ref[u32],entity_id,visible)
  on verified map entry: begin snapshot scoped to world/map/generation
  if newly visible: S33 human or type-valid S07 other, once per binding
  if already visible: S0C/S64 motion or S11 heading/appearance as supported
  if AOI leave/disconnect: S0E on each observing connection
  if authoritative dead: S5F only when verified native visual semantics
  on map exit/reset: clear stale projections; S15 client local cleanup != DB delete
  if unknown ref/update, mismatched identity/revision, stale generation: reject/resync
```

Original wire lacks world_generation/map_epoch. Out-of-order old S0E after reused ref can kill a new drawing; **Server-side epoch alone does not repair ambiguous packets on one TCP**. Enforce serialized visibility projection/ref retirement and transport fences, or reconnect on ambiguity. Move/Die before Add must never spawn unknown object. Repeated Add same binding may refresh, duplicate S0E no extra change. **Do not assume original 32-bit wire_ref equals SQL PK, 64-bit EntityId, or globally unique NPC ID.** Observer interest distances, model content, full S07 type-resource semantics and original Server ID retirement all pending A-024/Client trace.

Gate: A-004 `integrated/handoff partial`; original 2-Client E2E `not-run`, SCN-005/011 `analysis-required`. CT-063/064/065 planned, old CT-018/022 not magically passed. Correct S5F reference in A-025/S012 packet docs. No newly created branch.
