#!/usr/bin/env python3
"""A-028: BIN-derived S02/C04/C15 fixtures + *designed* safe commit model.

No native Client E2E is claimed. For original Client UI branches, this is a
simple deterministic model; no real original Server's persistence is known.
"""
from dataclasses import dataclass


def parse_s02(body: bytes):
    if len(body) < 2:
        raise ValueError("S02 missing status or string8 length")
    size = body[1]
    if len(body) != size + 2:
        raise ValueError("S02 string8 length mismatch")
    return body[0], body[2:]


def encode_c04(sex, hair, r, g, b):
    parts = (sex, hair, r, g, b)
    if any(not isinstance(x, int) or not 0 <= x <= 255 for x in parts):
        raise ValueError("C04 requires five u8")
    return bytes(parts)


@dataclass
class NewUserUI:
    state: int = 0x1C
    c04_count: int = 0
    c15_count: int = 0
    has_successful_ui_transition: bool = False

    def c02_submitted(self):
        if self.state != 0x1C:
            raise ValueError("C02 must be submitted from new-user UI")
        self.state = 0x1D

    def receive_s02(self, body: bytes):
        status, message = parse_s02(body)
        if status != 0:
            # 0x4B1EE9 -> 0x4B1F34 and constructor 0x5715F0 (C15)
            self.c15_count += 1
            self.state = 0x1F
            return "C15_NO_BODY"
        if self.state == 0x1D:
            # 0x4B1F46 -> 0x4B205F
            self.c04_count += 1
            self.state = 0x1E
            return "C04_FIVE_BYTES"
        # 0x4B206B, other states including 0x1E; UI activity, no direct S03.
        self.has_successful_ui_transition = True
        return "UI_LOCAL_SUCCESS_NO_IMMEDIATE_S03"


class SafeCharacterCommit:
    """Design-only: one character per admin-provisioned authenticated owner."""
    def __init__(self):
        self.account_owner = {"acct": "owner"}
        self.characters = {}
        self.commits = 0

    def finish_c04(self, account, authenticated_owner, pending_owner, body):
        if len(body) != 5:
            return False
        if (self.account_owner.get(account) != authenticated_owner
                or pending_owner != authenticated_owner):
            return False
        if account in self.characters:
            return self.characters[account] == body  # idempotent duplicate
        self.characters[account] = body
        self.commits += 1
        return True


def test():
    assert encode_c04(1, 2, 0x11, 0x22, 0x33).hex() == "0102112233"
    assert parse_s02(bytes.fromhex("0000")) == (0, b"")
    assert parse_s02(bytes.fromhex("0303657272")) == (3, b"err")
    for invalid in (b"", b"\x00", b"\x00\x01", b"\x00\x00\x01"):
        try:
            parse_s02(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid S02 was accepted")
    good = NewUserUI()
    good.c02_submitted()
    assert good.receive_s02(bytes.fromhex("0000")) == "C04_FIVE_BYTES"
    assert good.state == 0x1E and good.c04_count == 1
    assert good.receive_s02(bytes.fromhex("0000")) == "UI_LOCAL_SUCCESS_NO_IMMEDIATE_S03"
    assert good.c04_count == 1 and good.state == 0x1E
    bad = NewUserUI()
    bad.c02_submitted()
    assert bad.receive_s02(bytes.fromhex("0303657272")) == "C15_NO_BODY"
    assert bad.c15_count == 1 and bad.state == 0x1F
    bad_after_c04 = NewUserUI()
    bad_after_c04.c02_submitted()
    bad_after_c04.receive_s02(bytes.fromhex("0000"))
    assert bad_after_c04.receive_s02(bytes.fromhex("0100")) == "C15_NO_BODY"
    assert bad_after_c04.state == 0x1F
    db = SafeCharacterCommit()
    appearance = encode_c04(1, 2, 0x11, 0x22, 0x33)
    assert not db.finish_c04("acct", "intruder", "intruder", appearance)
    assert not db.finish_c04("acct", "owner", "intruder", appearance)
    assert db.commits == 0
    assert db.finish_c04("acct", "owner", "owner", appearance)
    assert db.finish_c04("acct", "owner", "owner", appearance)
    assert db.commits == 1
    assert not db.finish_c04("acct", "owner", "owner", b"\x01\x03\x11\x22\x33")
    print("PASS A-028: S02 parser, C04 u8 layout, C15 failure path, UI state, fail-closed idempotency")

if __name__ == "__main__":
    test()
