#!/usr/bin/env python3
"""Synthetic decoded-body Social codec and conservative Server membership policy.

Known native serializer: C0E = type:u8 + string8, C19 = type:u8 +
target:string8 + text:string8, C2E op0/1 as studied in Asgard.exe.
The opcode payload here is already decoded; not the AA transport frame.
"""
def _u8(n):
    if not isinstance(n, int) or not 0 <= n <= 255:
        raise ValueError("u8 outside 0..255")
    return bytes((n,))

def _text(s, limit=255):
    if not isinstance(s, str):
        raise ValueError("text must be str")
    raw = s.encode("cp950", "strict")
    if not 0 < len(raw) <= limit:
        raise ValueError("invalid CP950 byte length")
    return _u8(len(raw)) + raw

def c0e_say(type_id, message):
    return _u8(type_id) + _text(message)

def c19_whisper(type_id, recipient, message):
    return _u8(type_id) + _text(recipient) + _text(message)

def c2e_group(op, name=None, flag1=0, flag2=0):
    _u8(op)
    if op == 0:
        return b"\x00" + _text(name)
    if op == 1:
        return b"\x01" + _text(name) + _u8(bool(flag1)) + _u8(bool(flag2))
    raise ValueError("other native ops unconfirmed for this subset")

def decode_string8(raw, cursor):
    if cursor >= len(raw):
        raise ValueError("truncated length")
    n = raw[cursor]
    end = cursor + 1 + n
    if n == 0 or end > len(raw):
        raise ValueError("missing or truncated string")
    try:
        text = raw[cursor+1:end].decode("cp950", "strict")
    except UnicodeError as e:
        raise ValueError("invalid CP950") from e
    return text, end

def decode_c19(raw):
    if not raw: raise ValueError("missing type")
    target, pos = decode_string8(raw, 1)
    text, pos = decode_string8(raw, pos)
    if pos != len(raw): raise ValueError("trailing bytes")
    return dict(type_id=raw[0], recipient=target, text=text)

class MembershipModel:
    """Designed fail-closed policy for an in-memory group example, NOT native semantics."""
    def __init__(self, members, leader):
        self.members = set(members)
        if leader not in self.members:
            raise ValueError("leader missing")
        self.leader = leader
        self.revision = 0

    def kick(self, caller, target, expected_revision, valid_generation=True):
        if (not valid_generation or expected_revision != self.revision
                or caller != self.leader or target not in self.members
                or target == caller):
            return False
        self.members.remove(target)
        self.revision += 1
        return True

    def route_group(self, caller, active_sessions):
        if caller not in self.members: return set()
        return self.members & set(active_sessions)
