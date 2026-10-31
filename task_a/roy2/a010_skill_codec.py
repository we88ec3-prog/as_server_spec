"""A-010: original Asgard.exe skill/spell decoded bodies.

PE32 SHA256 db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145
All values deliberately opaque: original Client's spell category, duration, stack
and Server damage/resource/cooldown policy are not established by packet decoding.
Wire body only; excludes transport framing / seed XOR.
"""
import struct


class SkillPacketError(ValueError):
    pass


class Reader:
    def __init__(self, raw):
        if not isinstance(raw, (bytes, bytearray, memoryview)):
            raise SkillPacketError("decoded body must be bytes")
        self.raw = bytes(raw)
        self.pos = 0

    def take(self, n):
        if n < 0 or self.pos + n > len(self.raw):
            raise SkillPacketError("truncated skill packet")
        b = self.raw[self.pos:self.pos + n]
        self.pos += n
        return b

    def u8(self):
        return self.take(1)[0]

    def u16(self):
        return struct.unpack(">H", self.take(2))[0]

    def u32(self):
        return struct.unpack(">I", self.take(4))[0]

    def string8_raw(self):
        return self.take(self.u8())

    def done(self):
        if self.pos != len(self.raw):
            raise SkillPacketError("unexpected trailing skill bytes")


def _uint(n, bits):
    if type(n) is not int or not 0 <= n < (1 << bits):
        raise SkillPacketError("value outside u%d" % bits)
    return n


def c4d_start_cast_spell(spell_word):
    """0x575510 constructor opcode 0x4D / 0x5755C0 writer: BE u16."""
    return struct.pack(">H", _uint(spell_word, 16))


def c56_cast_spell(value):
    """0x571750 constructor opcode 0x56 / 0x571800 writer: u8."""
    return bytes([_uint(value, 8)])


def s52_cast_spell(raw):
    """0x57D550 ctor opcode0x52 / 0x57D600 reader: BE u32,u8."""
    r = Reader(raw)
    obj = {"opaque_u32": r.u32(), "opaque_u8": r.u8()}
    r.done()
    return obj


def s48_cancel_cast_spell(raw):
    """0x57D3F0 ctor opcode0x48 / 0x57D4A0 reader: BE u32."""
    r = Reader(raw)
    obj = {"opaque_u32": r.u32()}
    r.done()
    return obj


def s2d_remove_lasting_spell(raw):
    """0x585D00 ctor opcode0x2D / 0x585DB0 reader: BE u32."""
    r = Reader(raw)
    obj = {"opaque_u32": r.u32()}
    r.done()
    return obj


def s2c_add_lasting_spell(raw):
    """0x57A8D0 ctor opcode0x2C / 0x57A980 native field-reading order.

    Original 0x45B7A0 performs string8 byte length + local codepage conversion
    into a wide buffer (max 255 source bytes), not a fixed on-wire 0x200B name.
    Preserve raw bytes; CP950 as profile hypothesis, not forced decoding.
    """
    r = Reader(raw)
    obj = {
        "opaque_u32_a": r.u32(),
        "opaque_u8_a": r.u8(),
        "opaque_u16": r.u16(),
        "opaque_u8_b": r.u8(),
        "name_bytes": r.string8_raw(),
        "opaque_u8_c": r.u8(),
        "opaque_u32_b": r.u32(),
        "opaque_u32_c": r.u32(),
    }
    r.done()
    return obj


class DesignedLastingSpellLedger:
    """Designed Server-only event ledger; NOT original Client/server behavior.

    Models generation-scoped add/remove idempotence; does not guess duration,
    stacking, caster identity, expiration clock or server authoritative damage.
    """

    def __init__(self):
        self._epoch = None
        self._effects = {}

    def enter_world(self, epoch):
        self._epoch = epoch
        self._effects.clear()

    def add(self, epoch, effect_key, payload):
        if epoch != self._epoch:
            return False
        key = _uint(effect_key, 32)
        self._effects[key] = payload
        return True

    def remove(self, epoch, effect_key):
        if epoch != self._epoch:
            return False
        key = _uint(effect_key, 32)
        self._effects.pop(key, None)
        return True

    def count(self):
        return len(self._effects)
