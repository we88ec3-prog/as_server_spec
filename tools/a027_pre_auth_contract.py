#!/usr/bin/env python3
"""A-027 static C02 body fixtures and DESIGNED deny-by-default ownership gate.

NOT a native-server model; safe synthetic account names/secrets only.
Run: python3 tools/a027_pre_auth_contract.py
"""


def string8(raw: bytes) -> bytes:
    if len(raw) > 255:
        raise ValueError("string8 byte limit exceeded")
    return bytes((len(raw),)) + raw


def encode_c02(region: int, fields: tuple[bytes, ...], flag: int = 0) -> bytes:
    if region in (2, 3, 4):
        if len(fields) != 4 or not 0 <= flag <= 255:
            raise ValueError("region 2..4 expects four strings + u8")
        return b"".join(string8(f) for f in fields) + bytes((flag,))
    if len(fields) != 3:
        raise ValueError("other regions expect three strings")
    return b"".join(string8(f) for f in fields)


def read_c02(region: int, body: bytes):
    count = 4 if region in (2, 3, 4) else 3
    fields, i = [], 0
    for _ in range(count):
        if i >= len(body):
            raise ValueError("truncated string8 length")
        n = body[i]
        i += 1
        if i + n > len(body):
            raise ValueError("truncated string8 value")
        fields.append(body[i:i + n])
        i += n
    flag = None
    if count == 4:
        if i == len(body):
            raise ValueError("missing u8 flag")
        flag = body[i]
        i += 1
    if i != len(body):
        raise ValueError("trailing bytes")
    return tuple(fields), flag


class PreAuthGate:
    """Designed: C02 alone is NEVER authoritative for admin-preprovisioned account."""

    def __init__(self):
        self.accounts = {"alice": {"character": None}}
        self.pending = set()
        self.successes = 0

    def receive_c02(self, region: int, body: bytes):
        fields, flag = read_c02(region, body)
        # Parsing is not authentication; no account/character/lease mutation.
        return {"accepted": False, "reason": "NO_VERIFIED_ACCOUNT_OWNER",
                "wire_fields": len(fields), "has_flag": flag is not None}


def test():
    assert encode_c02(2, (b"a", b"b", b"c", b"d"), 1).hex() == "016101620163016401"
    assert encode_c02(0, (b"a", b"b", b"c")).hex() == "016101620163"
    assert encode_c02(1, (b"a", b"b", b"c")).hex() == "016101620163"
    for region in (0, 1, 2, 3, 4, 5):
        fields = (b"alice", b"secret", b"verify", b"extra") if region in (2, 3, 4) else (
            b"alice", b"secret", b"verify")
        packet = encode_c02(region, fields, 1)
        assert read_c02(region, packet) == (fields, 1 if len(fields) == 4 else None)
        gate = PreAuthGate()
        assert gate.receive_c02(region, packet)["accepted"] is False
        assert gate.accounts == {"alice": {"character": None}}
        assert not gate.pending and gate.successes == 0
        for invalid in (packet[:-1], packet + b"\xff"):
            try:
                read_c02(region, invalid)
            except ValueError:
                pass
            else:
                raise AssertionError("Malformed C02 accepted")
    print("PASS A-027: C02 region codecs, truncation/trailing guards, pre-auth no-claim")


if __name__ == "__main__":
    test()
