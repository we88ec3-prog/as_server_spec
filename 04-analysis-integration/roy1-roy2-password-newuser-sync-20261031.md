# 2026-10-31 Roy1/Roy2 analysis sync and validation

Scope: analysis/spec only. No modifications to as_server_roy, Asgard.exe or databases, and no new branches.

## Git baseline

- main before merge: c45353827c114d793e1a4c81dd6cf44bc1fe93e7
- task_a/roy1: c3e531e3e7d7f97127f2e732f4498f6becf3135b (8 commits ahead and 3 behind main, diverged at 6b935906).
- task_a/roy2: ab2525bbe7f36d5cec89f35189e2d776ea5a8942 (already ancestor of main, 0 outstanding commits).
- private Server main (read-only): f2a4a388013b11b5472c3b1022dea5c8176e503b.

Merge decision: bring Roy1's A-029/A-030 original reports, contract documents, and offline probes into the main tree, merge shared JSON at field granularity, preserve newer main RI-001/RI-005 evidence, CI governance and test identifiers. Create two-parent commit to retain Roy1 ancestry. Roy2 has no unapplied commits. After successful CI, fast-forward both existing analysis branch refs to main without force.

## Client evidence validated

The uploaded original Asgard.exe SHA256 is db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145, byte size 3235840. Local independent check confirms at file-offset RVA 0x171a29 the instruction bytes 6a26 (push 0x26), as documented by Roy1 A-029. C02 writer VA 0x5742b0 is also present. These are original binary static findings, NOT a network trace or original Client GUI acceptance.

- **A-029**: Client C26 (0x26) for changing password is proven at constructor 0x571a10 and writer 0x571ac0. Three string8 fields correspond to account candidate (control8), old password (control9) and new password (control10); confirmation (control11) is only locally checked; event12 submits, event13 cancels. Shared S02 handler is located, but C26-specific success/failure codes and native GUI response are unknown. Roy1's report documents 19 signatures and 14 synthetic tests. A-029 integrated / partial; native CT-098/099 not-run.
- **A-030**: C02 native region widgets mapped in original binary: region0 IDs 1/2/3 and extra widget10, region1 IDs 12/13/14 and extra widgets15/16 but writer/extra mismatch, region2-3 IDs 12/13/14/15/16, region4 IDs 20/21/22/23/24. S02 nonzero with nonempty message has native text dialog and C15(empty) dispatch, except region3 state0x1e message suppression. Roy1 reports 30 native anchors/29 status selectors/15 synthetic tests. Label NAME vs EMAIL semantics, EMAIL required gate, actual native status meanings and GUI E2E remain unknown. A-030 integrated / partial, native CT-103/104/105 not-run.
- ID/PASSWORD/CONFIRM have strongly inferred semantics from UI controls and local comparison, not originally extracted localized label strings. In region2-4 F3 NAME and F4 EMAIL are plausible candidates, **NOT** confirmed. Region0 sends only F3, region1 mismatch exists; no assumptions about E-MAIL persistence or required format.

## Current Server main baseline reconciliation

- Backend implemented: ICreationCredentialVerifier + IndependentCharacterCreation create-only credential proof, account-status/version fence, pending draft, C04 transaction/idempotency, C15 owner-aware cancel. Legacy CharacterCreationAccountGuard still depends on loggedIn but is not the independent flow's authority.
- Live LoginWireSession C02/C04/C15 still fail-closed due to missing NAME/EMAIL native wire semantic and safe S02 error response. Existing backend does NOT mean original Client can now finish native creation.
- RI-005 pre-submit waiting and RI-001 actual submitted C02 are different. Recent runtime sample: Server FIN_WAIT_2 versus Client CLOSE_WAIT while Client UI responds, and subsequent C02 send=-1 on an already closed socket; that send does not prove C02 triggered closure.
- Current Server FormInput idle timeout 600 seconds / absolute 1800 seconds and redacted JSONL GameTcpDiagnosticJournal were implemented; 60-second earlier behavior is historical, original Client >60-second test not-run.
- R-033 party maximum aggregate damage and R-034 tutorial refusal no-op have Server domain synthetic tests, but original native party/loot/NPC packets and E2E remain open.

## Conflict resolutions and acceptance gates

- Keep main runtime-issues.json, idle-disconnect-observability.md, RI-001 and RI-005 revisions, not Roy1 stale copies.
- Mark A-029 and A-030 integrated/partial; retain original static evidence and genuine native-client-validation=not-run. Add packet PKT-C26 and all original report+evidence references. Keep CT-098/099/103/104/105 planned, no test-ID renumber.
- Original native C02 adapter remains blocked until verified NAME/E-MAIL labels and region and UI error statuses; C26 live password change needs its own S02 change-status acceptance.
- No confirmed additional missing file. If UI labels require an external asset, inspect EXE loader and report exact filename before requesting it.
- No new product decisions now: separate direct C02 credential verification, Admin-only provisioning, no client changes, successful create returns login are settled. Possible email storage and legacy length policy decisions require actual A-030 observations.

## 23:51 new main integration evidence: C02 received and explicitly closed (modified Client only)

Another agent updated main after the start of this merge. The latest 2026-10-31 23:51 correlated local test found **modified main-menu-preview diagnostic Client** successfully sent C02, and the running private Server f2a4a38 logged C02(body length 15, ordinal5) then close reason `native-c02-fields-unknown-a030`, without S02. This is now runtime-confirmed for that test and is NOT a 60-second idle timeout; original unmodified Asgard.exe CT-103/104/105 remains not-run. Earlier stale-socket send=-1 is a separate event. The P0 task can shift from diagnosing that particular disconnect to NAME/EMAIL authoritative field map, C02 adapter and Client-supported error S02, without claiming full native acceptance.
