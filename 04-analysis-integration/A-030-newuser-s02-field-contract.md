# A-030 Client C02 NAME/E-MAIL and S02 Failure Contract (scope-limited)

Source: [BIN-first report](../03-analysis-requests/A-030-native-newuser-disconnect-fields.md), [reproducible probes](../tools/a030_native_newuser_contract.py), A-021/A-027/A-028, A-020; original Asgard.exe SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145. Evidence ev_a030_20261031_newuser_regions_s02_failure_bin_static. All Client observations observed-static; no native GUI/packet capture, no original Server error semantics.

## Exact, observable C02 field contract
- Common F1: MakeInfoDialog +0x26c, packet owner +0x24, writer subobject+0x18; **likely ID** based on first-field length gate, UI display label not independently extracted.
- Common F2: dialog+0x270, packet+0x224, writer+0x218; **likely PASSWORD**; independent dialog+0x274 confirmation compared with F2 at 0x4b290c. CONFIRM is **local-only, never an extra C02 string**.
- Region0: F3 from widget10 (0x0a), packet+0x424, writer+0x418; UI branch at 0x4b2835 conditionally empties value. Exactly 3 wire string8.
- Region1: writer sends only F1/F2/F3 at +0x418, but UI's non-region0 branch fills packet+0x624/+0x822 from widgets15/16, not +0x424: **inconsistent in observed submit slice**; exclude from native-ready claims.
- Region2/3: F3 from widget15→packet+0x624→writer+0x618, F4 from widget16→packet+0x822→writer+0x816; tail flag from global 0x66d110+0x219; exactly 4 string8 + u8.
- Region4: F3 from widget23, F4 from widget24; same writer offsets/tail shape as region2/3.
- Native layout evidence 0x4b1afa..0x4b1bc1, 0x4b27b5..0x4b28e0, 0x5742b0..0x574352. Message/codepage region-specific; synthetic examples CP950 TW index4.
- NAME=F3 and EMAIL=F4 are **conditional hypotheses for region2..4**, not confirmed label associations; there is no uniquely proven NAME or E-MAIL mapping from current EXE + available assets. Do NOT map F4 to Account table or use F3 for CharacterName until original UI/label and anonymized C02 field-length comparison confirm actual region. No NAME/EMAIL labels located in raw EXE static ASCII/UTF16 search. Missing concrete UI asset filename is unverified; do not invent one.
- E-MAIL optional: explicit submit block only checks F1 format, F2=confirmation, and UI terms; **extra-field mandatory/valid format still unknown**, e.g. widget resource property can enforce it.

## S02 nonzero C15, no fabricated status semantic
Original S02 parser 0x57dbc0: status:u8, string8 encoded text. For MakeInfoDialog:
- callback 0x4b1d60 from active NewUser state, status value at S02 object+0x24, UTF16 text+0x26.
- status3/4/18/26/31 focus first UI field; status17 second; status1/2 have no special focus; the other status codes are default category. **This does not map any code to wrong password, existing account, banned or duplicate NAME**.
- Non-empty message triggers dialog build 0x4b1e2e..0x4b1ec3 except state0x1e + region3 suppresses it. Nonzero status then 0x4b1f1b constructs native C15(empty), 0x4b1f2f sends, 0x4b1f34 changes local state 0x1f. **C15 handling on real Server after close/retry still unknown**.
- **Synthetic, not an observed original Server error:** S02 body hex `01 10 526571756573742072656a6563746564` = nonzero status1, ASCII text 'Request rejected'. On state0x1d (with UI callback active and normal text path), static code is capable of displaying text and emitting C15, but **no native GUI run**. Candidate for isolated native E2E only; DO NOT claim status1 has verified official business meaning.
- S02(status0) in state0x1d calls native C04 five bytes, state0x1e; in state0x1e status0 uses local success path 0x4b206b (does not auto-login). No S02(0) for failed auth.

## Server design guardrails (DESIGNED, not Client or original Server observations)
1. Do not enable independent C02 Account ownership based on guessed NAME/EMAIL; require verifiable existing ID/password and first-stage auth proof attached to connection/generation and credential_version.
2. Avoid TCP Close for ordinary credential rejection where a native S02 error is supported. But official status/UI and post-C15 socket behavior are **not yet native-validated**; fail closed rather than claim compatibility.
3. Never log raw decrypted C02 frame, ACCOUNT/PASSWORD/EMAIL/NAME test values or S02 sensitive text. Record only region, opcode, field count/encoded lengths, masked IDs, event order, client state, status, socket close origin and redacted popup.
4. Correct first-stage success S02(0) → C04; only after server-side atomic character commit, final S02(0). C15 cancels only same uncommitted intent. Session/replay/failure/ban remains Server-owned.

## CT closure
Offline 30 EXE instruction signatures and full 29-entry focus selector, 15 synthetic unittest: PASS. CT-103/104/105 unchanged as **planned/native-client not-run**. Native completion requires documented visible NAME/E-MAIL widget IDs or user-verified UI resource mapping, region/seed/profile, two anonymized form submissions (EMAIL empty vs filled, NAME changed vs constant), S02 nonzero dialog observation and C15 trace plus no-disconnect proof. Source file is a *test of native static code and designed codec*, not a runtime client or server run. Full original Server auth/status logic remains unknown.

## 2026-11-01 ADR-008（覆蓋上文所有回登入假設）

**原版 Client 成功 C04／第二段 S02(0) 後直接進遊戲、不返回 LoginDialog，玩家不需手動第二次 C03。** 上方舊有「成功後回登入」「手動重新登入」是過時 Server 規劃，不再做開發或 CT 出場條件；A-028 的 0x4b206b callback 無立即 S03 仍是有效靜態觀察，但後續背景授權/轉服/首 World opcode 必須由 A-028/A-031 補證，不能猜。已存在角色日後的一般 C03/S03/C10 登入不變。新正式需求見 [ADR-008](../02-server-planning/post-create-direct-world-decision-20261101.md)。原版 Client E2E 未執行。
