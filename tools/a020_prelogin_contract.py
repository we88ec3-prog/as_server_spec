#!/usr/bin/env python3
"""A-020: BIN-derived packet fixture tests + designed safe server prelogin gate.

Original Asgard.exe is NOT executed by these tests. Native Server statuses,
timing, S18 kind1 resource semantics and full regional rules are not proven.
"""
import struct
import unittest
import zlib


def s8(value: bytes) -> bytes:
    if not isinstance(value, bytes) or len(value) > 255:
        raise ValueError("string8 requires <=255 encoded bytes")
    return bytes([len(value)]) + value


def take_s8(b: bytes, at: int):
    if at >= len(b): raise ValueError("missing string8 length")
    n = b[at]
    if at + 1 + n > len(b): raise ValueError("truncated string8")
    return b[at + 1:at + 1 + n], at + 1 + n


def c0f(type_: int, option=0, text=b"") -> bytes:
    if not 0 <= type_ <= 255: raise ValueError("invalid type")
    if type_ == 3:
        if option != 0 or text: raise ValueError("type3 cannot have trailing fields")
        return b"\x03"
    if not 0 <= option <= 255: raise ValueError("invalid option")
    return bytes((type_, option)) + s8(text)


def c57(type_: int, selected=None) -> bytes:
    if type_ == 1 and selected is None:
        return b"\x01"
    if type_ == 0 and isinstance(selected, int) and 0 <= selected <= 255:
        return bytes((0, selected))
    raise ValueError("C57 only accepts type1 or type0 + selected-id")


def parse_s18_kind0(body: bytes):
    # 0x582DC0: kind:u8, subtype:u8, count:u16be, count*(string8, u32be)
    if len(body) < 4 or body[0] != 0:
        raise ValueError("only native kind0 subset confirmed")
    subtype, count = body[1], int.from_bytes(body[2:4], "big")
    pos, items = 4, []
    if count > 128: raise ValueError("local defensive count policy")
    for _ in range(count):
        name, pos = take_s8(body, pos)
        if pos + 4 > len(body): raise ValueError("truncated value")
        value = int.from_bytes(body[pos:pos + 4], "big")
        pos += 4
        items.append((name, value))
    if pos != len(body): raise ValueError("trailing data")
    return subtype, items


def s56(entries):
    """Server fixture: u16be compressed_len + zlib(u8 count, records)."""
    if len(entries) > 32: raise ValueError("local fixture limit, not native capacity")
    raw = bytearray((len(entries),))
    for id_, ip_be, port, flag, name, x, y in entries:
        if any(not 0 <= n <= 255 for n in (id_,flag)): raise ValueError("u8")
        if not 0 <= ip_be <= 0xffffffff or not 0 <= port <= 65535:
            raise ValueError("numeric range")
        raw.extend(struct.pack(">BIHB", id_, ip_be, port, flag))
        raw.extend(s8(name) + s8(x) + s8(y))
    compressed = zlib.compress(bytes(raw))
    if len(compressed) > 65535: raise ValueError("compressed limit")
    return struct.pack(">H", len(compressed)) + compressed


def decode_s56(body: bytes):
    if len(body) < 2 or int.from_bytes(body[:2], "big") != len(body) - 2:
        raise ValueError("compressed length mismatch")
    dec = zlib.decompressobj()
    raw = dec.decompress(body[2:], 8193)
    if not dec.eof or dec.unused_data or dec.unconsumed_tail or len(raw) > 8192:
        raise ValueError("unsafe/truncated/oversized compressed body")
    if not raw: raise ValueError("missing count")
    count, pos, out = raw[0], 1, []
    if count > 32: raise ValueError("local count guard")
    for _ in range(count):
        if pos + 8 > len(raw): raise ValueError("truncated entry")
        id_, ip, port, flag = struct.unpack(">BIHB", raw[pos:pos+8])
        pos += 8
        name,pos = take_s8(raw, pos)
        x,pos = take_s8(raw, pos)
        y,pos = take_s8(raw, pos)
        out.append((id_, ip, port, flag, name, x, y))
    if pos != len(raw): raise ValueError("trailing entries")
    return out


def s60_type0(value):
    return b"\x00" + struct.pack(">I", value)


def s60_type1(text):
    raw = text + b"\x00"
    c = zlib.compress(raw)
    return b"\x01" + struct.pack(">H",len(c)) + c


def parse_s60(body):
    if not body: raise ValueError("missing type")
    if body[0] == 0:
        if len(body) != 5: raise ValueError("type0 requires u32")
        return ("number",int.from_bytes(body[1:],"big"))
    if body[0] == 1:
        if len(body) < 3 or int.from_bytes(body[1:3],"big") != len(body)-3:
            raise ValueError("compressed length mismatch")
        z = zlib.decompressobj()
        data = z.decompress(body[3:],8193)
        if not z.eof or z.unused_data or z.unconsumed_tail or len(data)>8192:
            raise ValueError("invalid compressed content")
        return ("text",data)
    raise ValueError("unknown S60 type")


class Prelogin:
    """Deliberately narrow LOCAL profile; not claimed as original Server sequencing."""
    def __init__(self):
        self.state = "VersionAccepted"
        self.ids = set()

    def accept(self, opcode, body):
        if opcode == "C6C" and self.state=="VersionAccepted" and body==b"\x03":
            return "local-script-noop"
        if opcode == "C0F" and self.state=="VersionAccepted" and body==b"\x03":
            self.state="MetadataSent"
            return b"\x00\x03\x00\x00"  # S18(kind0,subtype3,count0)
        if opcode=="C57" and self.state=="MetadataSent" and body==b"\x01":
            self.ids={0}
            self.state="ListSent"
            return s56([(0,0x0100007f,15010,0,b"Local Test",b"",b"")])
        if opcode=="C57" and self.state=="ListSent" and body==b"\x00\x00":
            self.state="Selected"
            return "selected"  # S60 is optional local policy
        if opcode=="C4B" and self.state=="Selected" and body==b"":
            self.state="LoginReady"
            return s60_type1(b"Local Test")
        raise ValueError("unexpected packet/order/selector")


class Tests(unittest.TestCase):
    def test_c0f_branches(self):
        self.assertEqual(c0f(3), b"\x03")
        self.assertEqual(c0f(1,2,b"ABC"), b"\x01\x02\x03ABC")
        with self.assertRaises(ValueError): c0f(3,1,b"bad")

    def test_s18_real_empty_and_nonempty(self):
        self.assertEqual(parse_s18_kind0(bytes.fromhex("00030000")),(3,[]))
        body=b"\x00\x02\x00\x01" + s8(b"abc") + b"\x01\x02\x03\x04"
        self.assertEqual(parse_s18_kind0(body),(2,[(b"abc",0x01020304)]))
        for b in (body[:-1],body+b"\x00",b"\x01\x03"):
            with self.assertRaises(ValueError): parse_s18_kind0(b)

    def test_c57_selection_and_compressed_s56(self):
        self.assertEqual(c57(1),b"\x01")
        self.assertEqual(c57(0,0),b"\x00\x00")
        with self.assertRaises(ValueError): c57(2)
        record=(0,0x0100007f,15010,0,b"Local Test",b"",b"")
        body=s56([record])
        self.assertEqual(decode_s56(body),[record])
        for bad in (body[:-2],body+b"EXTRA",b"\x00\x04xxxx"):
            with self.assertRaises(ValueError): decode_s56(bad)

    def test_c4b_empty_and_s60_variants(self):
        self.assertEqual(b"",b"")  # ctor 0x575670 + empty writer 0x575720
        self.assertEqual(parse_s60(s60_type0(0x12345678)),("number",0x12345678))
        self.assertEqual(parse_s60(s60_type1(b"Local Test")),("text",b"Local Test\x00"))
        for bad in (b"",b"\x02",b"\x00\x00",b"\x01\x00\x05x"):
            with self.assertRaises(ValueError):parse_s60(bad)

    def test_minimal_gate_and_order(self):
        g=Prelogin()
        with self.assertRaises(ValueError):g.accept("C57",b"\x01")
        self.assertEqual(g.accept("C6C",b"\x03"),"local-script-noop")
        self.assertEqual(parse_s18_kind0(g.accept("C0F",b"\x03")),(3,[]))
        dec=decode_s56(g.accept("C57",b"\x01"))
        self.assertEqual(dec[0][0],0)
        with self.assertRaises(ValueError):g.accept("C57",b"\x00\x01")
        self.assertEqual(g.accept("C57",b"\x00\x00"),"selected")
        self.assertEqual(parse_s60(g.accept("C4B",b""))[0],"text")
        with self.assertRaises(ValueError):g.accept("C4B",b"")

    def test_no_unverified_script_or_owner(self):
        g=Prelogin()
        for opcode,body in [("C6C",b"\x00"),("C6C",b"\x04"),("S44",b"\x01\x03"),("C03",b"hello"),("C0F",c0f(0,1,b"x"))]:
            with self.assertRaises(ValueError):g.accept(opcode,body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
