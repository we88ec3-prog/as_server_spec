# Updated DEV plan from Roy1/Roy2 (2026-10-31)

Spec baseline before sync: c45353827c114d793e1a4c81dd6cf44bc1fe93e7; private Server read-only: f2a4a388013b11b5472c3b1022dea5c8176e503b. This is NOT authorization to alter Server code or database.

## Current state (avoid reimplementing completed work)

- DEV-CREATE backend **already implemented**: ICreationCredentialVerifier + IndependentCharacterCreation with independent pre-C03 credential verification, creation-only proof, expiry/generation/account version, C04 atomic commit and C15 pending-only cancel. Old CharacterCreationAccountGuard loggedIn helper remains, but not the new backend.
- GameTcpProbeService has phase-aware timeout and redacted close diagnostics: FormInput idle 600s and absolute 1800s; native Client original >60s validation still not-run.
- LoginWireSession native C02/C04/C15 wiring **not implemented and explicitly fail-closed**. Cannot release original creation because NAME/E-MAIL actual mapping and native S02 nonzero error semantics remain unknown.
- A-029 has proven original C26 (0x26) with three string8 account/old/new and a generic S02 handler. Native C26 response status meanings are unknown; no live adapter.
- Shared world / team damage reward / admission REFUSE domain synthetic progress exists; original NPC/party/reward wire still not validated.

## Ordered development and validation

**P0-0 / runtime issue partition (RI-005 vs RI-001).** On a new original Client session, separately test remaining in MakeInfoDialog >60 seconds and submitting promptly. Read only anonymized local journal at data/diagnostics/game-tcp-YYYYMMDD.jsonl; correlate Server build SHA, accepted C00/FormInput phase, packet opcodes/body lengths, last reply and explicit/timeout/peer close reason, Client FIN/GUI. Do not upload secrets or raw logs. A late C02 send=-1 to a previously closed socket cannot be labeled a C02-triggered close. Synthetic timeout tests do not constitute native success.

**P0-1 / A-030 remaining native UI evidence.** Using region-specific native widget IDs already proven, correlate visible ID, PASSWORD, CONFIRM, NAME, E-MAIL labels to C02 F1-F4 with masked synthetic values. Test whether empty EMAIL blocks local submission, region1 F3 writer mismatch, first-field minimum length for chosen region and S02(nonzero,text) native modal/C15/retry/socket response. Never treat status1 + Request rejected synthetic example as an original-Server code. DoD: verified NAME and EMAIL mapping, selected region/profile, actionable native error response, or explicit fail-closed unknowns. CT-103/104/105 native not-run until actual test.

**P0-2 / DEV-CREATE native adapter (requires separate user authorization).** Reuse implemented IndependentCharacterCreation; do NOT replace it with old loggedIn Guard or allow name-only C02. In LoginWireSession.HandleAsync route evidenced, valid C02 fields to existing Account/password/auth-proof/verified Character NAME; only then send first S02(status0), Client C04 five u8, transaction commit, second S02(status0), Client returns to separate Login C03. C15(empty) only cancels uncommitted same owner+generation draft; idempotent replays and disconnect after commit may not duplicate/drop Character. Nonexistent/wrong/banned/duplicate use proven native S02 failure only; unknown response remains fail-closed, not invented. CT-100/103/104/105 synthetic plus separate original-client GUI acceptance.

**P1-0 / DEV-C26 native password change (requires separate user authorization).** Native opcode C26 and three string8 account/old/new are now known; confirmation is never sent. Add strict decoder/old password verifier and new 4..8 ASCII-alnum policy; atomic hash+credential version change, revoke older session/grant and creation proof, preserve existing Character; both C03 and independent C02 use new password. Do not guess C26-specific S02 success/error status; CT-098 native and CT-099 domain + GUI remain planned.

**P1-1 / shared tutorial and party.** R-033 highest total effective-damage party owns all rewards, all qualifying members get full EXP and independent loot resolution; tie/roster/remote eligibility still need product decisions before implementation. R-034 refusing admission has no quest/asset/map effect and NPC can be asked again. Native A-014/007/009/025 for party/loot/death and A-012/023/026 for Script/quest interactions remain required; original Client CT-101/102 not-run.

## Evidence hierarchy and scope

Observed original EXE static, static inference, Server policy, Server synthetic tests and original Client GUI E2E must be separately labeled. No fabricated game opcode, S02 code, NAME/E-MAIL mapping or resources. No change to as_server_roy, original Asgard.exe, DB schema or Admin UI in this integration. Ask user for specific Server implementation approval before code work.

## 23:51 new main integration evidence: C02 received and explicitly closed (modified Client only)

Another agent updated main after the start of this merge. The latest 2026-10-31 23:51 correlated local test found **modified main-menu-preview diagnostic Client** successfully sent C02, and the running private Server f2a4a38 logged C02(body length 15, ordinal5) then close reason `native-c02-fields-unknown-a030`, without S02. This is now runtime-confirmed for that test and is NOT a 60-second idle timeout; original unmodified Asgard.exe CT-103/104/105 remains not-run. Earlier stale-socket send=-1 is a separate event. The P0 task can shift from diagnosing that particular disconnect to NAME/EMAIL authoritative field map, C02 adapter and Client-supported error S02, without claiming full native acceptance.
