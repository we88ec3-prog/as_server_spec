"""A-008: decoded S08/C47 bodies for original SHA-locked Asgard.exe.

Synthetic wire-only codec; no original Server formulas or Native GUI execution.
Field labels use offsets in SStatusPacket object, not wire offsets.
"""
from dataclasses import dataclass

@dataclass
class Cursor:
    data: bytes
    pos: int = 0
    def take(self, n):
        if n < 0 or self.pos + n > len(self.data):
            raise ValueError(f"truncated S08 at byte {self.pos}, need {n}")
        chunk = self.data[self.pos:self.pos + n]
        self.pos += n
        return chunk
    def u8(self): return self.take(1)[0]
    def u16(self): return int.from_bytes(self.take(2), "big")
    def u32(self): return int.from_bytes(self.take(4), "big")

def decode_s08(body: bytes) -> dict:
    """SStatusPacket::Read (VA 0x586D40), decoded body without outer framing."""
    c = Cursor(body)
    flags = c.u16()
    result = {"flags": flags, "mode_bit7": bool(flags & 0x80),
              "mode_bit1": bool(flags & 0x02), "mode_bit0": bool(flags & 0x01),
              "mode_bit8": bool(flags & 0x100)}
    if flags & 0x40:
        f = {"padding_byte": c.u8(), "p28_u8": c.u8()}
        for off in (0x2c, 0x30, 0x34, 0x38):
            f[f"p{off:02x}_u32"] = c.u32()
        for off in (0x3e, 0x3c):
            f[f"p{off:02x}_u16"] = c.u16()
        for off in (0x69, 0x68):
            f[f"p{off:02x}_u8"] = c.u8()
        for off in (0x42, 0x44):
            f[f"p{off:02x}_u16"] = c.u16()
        for off in range(0x46, 0x4c):
            f[f"p{off:02x}_u8"] = c.u8()
        for off, width in ((0x4c,4),(0x50,1),(0x54,4),
                           (0x58,1),(0x5c,4),(0x60,4),
                           (0x64,1),(0x66,1),(0x67,1),(0x6a,2)):
            f[f"p{off:02x}_u{8*width}"] = (
                c.u8() if width == 1 else c.u16() if width == 2 else c.u32())
        for off in range(0x6c, 0x70):
            f[f"p{off:02x}_u8"] = c.u8()
        result["full"] = f
    if flags & 0x20:
        result["current"] = [c.u32() for _ in range(4)]
    if flags & 0x10:
        result["secondary"] = {"p88_u32": c.u32(),
            "p8c_98_u16": [c.u16() for _ in range(4)],
            "p9c_u32": c.u32()}
    if flags & 0x08:
        attrs = [c.u8() for _ in range(5)]
        length = c.u8()
        result["text"] = {"p_a4_a8": attrs, "raw_cp_bytes": c.take(length)}
    if flags & 0x200:
        count = c.u8()
        result["extra_list"] = list(c.take(count))
    if c.pos != len(body):
        raise ValueError(f"trailing S08 bytes after offset {c.pos}")
    return result

def encode_c47(ability_choice: int) -> bytes:
    """StatusDialog button ID 0x13..0x17 emits one of 1,2,4,8,16."""
    if ability_choice not in (1, 2, 4, 8, 16):
        raise ValueError("not a native one-hot choice")
    return bytes([ability_choice])
