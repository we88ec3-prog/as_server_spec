# A-028 Roy3 Region3 自動 C03 / post-create Client I/O 交接

來源 task_a/roy3/A-028-roy3-conditional-auto-c03.md；A028-E10..E16。繼承 Roy2 C04/S02/C15 和 A031 C10/C25。原件 SHA db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145。

**Trigger**：MakeInfoDialog state1D S02(0)→C04/1E；final S02(0)→0x4B206B cleanup；Region3 0x4B2109→0x4A9380 LoginDialogPane constructor。
**Conditional automatic login**：ctor 0x4A95EE checks global [0x66D10C]+4/+0x204 two UTF16 chars nonzero and USER32.GetAsyncKeyState(0x11 Ctrl) signed nonnegative → 0x4A9617 calls 0x4A8950(event arg4, second0) → 0x4A8A30 calls C03 producer 0x4A7D10(0) → 0x4A7DDE send.
**Client sends**：C04 5u8；auto C03 opcode03 body two string8+u8(last0) from pane widget2/3；alternate independent nonzero callback 0x4A8890 triggers C03 last1；S02 failure sends empty C15。Do not treat last byte as unauthenticated World grant.
**Client receives**：S02 status/message; S03 may follow successful authenticated C03 (not captured for post-create). General A031 S03 transfer includes new TCP C10 and Region3 C25 3 string8, but native postcreate World sequence NOT observed.
**Client reaction**：UI cleanup; Region3 pane constructor can conditionally invoke auto login without manual input; other regions do not take same branch; cache presence is not proof of widget values/credential validity; Ctrl pressed suppresses only this conditional auto path.
**Evidence**：original EXE seven direct call edges, 42 anchors, 5 Region jump entries, 10 event entries, MSVC LoginDialogPane RTTI, original PE IAT GetAsyncKeyState, 12 offline tests.
**Unknowns**：runtime cache/keyboard/GUI, whether auto branch actually fires after real success, credential contents, actual S03, new TCP World initial S2C/map and Region0/1/2/4 auto mechanism; all native GUI not-run.

DEV / ADR-008：Do NOT require manual re-login; do NOT ban background C03 just because user never sees login UI. Securely bind committed C04 Account/Character/generation, verify C03 credentials and S03/C10 grant, never trust C03 tail0 or C25 as owner proof. CT-105/107/108 still necessary; A028 remains integrated/partial until native seamless World entry is observed.
