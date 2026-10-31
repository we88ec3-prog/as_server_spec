#!/usr/bin/env python3
"""A-010 original PE32 validation: 25 native VA + 6 MSVC packet RTTI.

No original executable bytes are committed. Checks only the user-provided
Asgard.exe SHA and short discriminative byte patterns. CI runs synthetic codec
without redistributing original EXE.
"""
import argparse
import hashlib
import struct
from pathlib import Path

SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
ANCHORS = {
    "C4D native opcode": (0x575529, "6a 4d 89 74 24 08"),
    "C4D BE u16 writer": (0x5755C0, "0f b7 41 18 50"),
    "C4D real producer ctor call": (0x402034, "e8 d7 34 17 00"),
    "C4D producer selected word": (0x402045, "66 8b 93 0e 08 00 00"),
    "C4D producer writes packet": (0x40204E, "66 89 50 24"),
    "C4D producer transmit": (0x402052, "e8 49 68 17 00"),
    "C56 native opcode": (0x571769, "6a 56 89 74 24 08"),
    "C56 u8 writer": (0x571800, "0f b6 41 18 50"),
    "S52 native opcode": (0x57D569, "6a 52 89 74 24 08"),
    "S52 BE u32 reader": (0x57D600, "56 8b f1 e8 a8 d8 ed ff"),
    "S52 u8 reader": (0x57D60D, "e8 9e d7 ed ff"),
    "S48 native opcode": (0x57D409, "6a 48 89 74 24 08"),
    "S48 BE u32 reader": (0x57D4A0, "56 8b f1 e8 08 da ed ff"),
    "S2C native opcode": (0x57A8E9, "6a 2c 89 74 24 08"),
    "S2C leading BE u32": (0x57A980, "56 8b f1 e8 28 05 ee ff"),
    "S2C first u8": (0x57A98D, "e8 1e 04 ee ff"),
    "S2C BE u16": (0x57A997, "e8 44 04 ee ff"),
    "S2C second u8": (0x57A9A2, "e8 09 04 ee ff"),
    "S2C string8 reader": (0x57A9B7, "e8 e4 0d ee ff"),
    "S2C third u8": (0x57A9BC, "8b ce e8 ed 03 ee ff"),
    "S2C second u32": (0x57A9CB, "e8 e0 04 ee ff"),
    "S2C third u32": (0x57A9D8, "e8 d3 04 ee ff"),
    "S2D native opcode": (0x585D19, "6a 2d 89 74 24 08"),
    "S2D BE u32 reader": (0x585DB0, "56 8b f1 e8 f8 50 ed ff"),
    "native string8 length byte": (0x45B7ED, "0f b6 04 06"),
}
PACKET_RTTI = (
    "CStartCastSpellPacket", "CCastSpellPacket", "SCastSpellPacket",
    "SCancelCastSpellPacket", "SAddLastingSpellPacket",
    "SRemoveLastingSpellPacket",
)


def check(original):
    blob = Path(original).read_bytes()
    if hashlib.sha256(blob).hexdigest() != SHA:
        raise ValueError("unknown Client Asgard.exe SHA256")
    peoff = struct.unpack_from("<I", blob, 0x3c)[0]
    if blob[peoff:peoff+4] != b"PE\x00\x00":
        raise ValueError("not PE")
    opt = peoff + 24
    if struct.unpack_from("<H", blob, opt)[0] != 0x10b:
        raise ValueError("not PE32")
    base = struct.unpack_from("<I", blob, opt+28)[0]
    sec = opt + struct.unpack_from("<H", blob, peoff+20)[0]
    n = struct.unpack_from("<H", blob, peoff+6)[0]

    def read_va(va, length):
        for i in range(n):
            o = sec + 40*i
            virtual_size, rva, raw_size, raw_off = struct.unpack_from("<IIII", blob, o+8)
            start = base + rva
            if start <= va and va+length <= start+min(virtual_size, raw_size):
                p = raw_off + va-start
                return blob[p:p+length]
        raise ValueError("missing PE VA %08x" % va)

    for name,(va,hexdump) in ANCHORS.items():
        expected = bytes.fromhex(hexdump)
        if read_va(va, len(expected)) != expected:
            raise ValueError("native instruction mismatch at %08X: %s" % (va,name))
        print("PASS 0x%X %s" % (va,name))

    for name in PACKET_RTTI:
        if blob.count((".?AV"+name+"@@\x00").encode("ascii")) != 1:
            raise ValueError("missing or ambiguous RTTI: "+name)
        print("PASS RTTI",name)

    print("A-010 PASS: %d instruction VA, %d RTTI; native GUI not-run"
          % (len(ANCHORS), len(PACKET_RTTI)))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client",nargs="?",default="Asgard.exe")
    check(parser.parse_args().client)
