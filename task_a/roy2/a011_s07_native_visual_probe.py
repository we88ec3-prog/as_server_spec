#!/usr/bin/env python3
"""A-011 native S07 row resource->MonsterImageLib proof; original PE only.

43 SHA-locked VA patterns. These signatures are static control-flow
anchors, not execution of the original Client, or original monster assets.
"""
import hashlib
import struct
import sys
from pathlib import Path

SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
ANCHORS = {
    "S07 parser read BE u16": (0x57E451, "e88ac9edff"),
    "S07 parser visual row+0C": (0x57E456, "6689460c"),
    "S07 native row stride 0x228": (0x57E3F1, "69c028020000"),
    "S07 separate variant u16 row+222": (0x57E4B8, "66898622020000"),
    "S07 handler read visual +0C": (0x4F1A7F, "668b460c"),
    "S07 handler copy visual to descriptor": (0x4F1A83, "6689442424"),
    "kind1 branch": (0x4F1A8B, "3c01"),
    "kind1 separate variant push": (0x4F1AC3, "668b8e22020000"),
    "kind1 descriptor ptr": (0x4F1ADD, "8d4c243c"),
    "kind1 MonsterObject ctor": (0x4F1AEB, "e8b054feff"),
    "kind2 branch": (0x4F1B68, "3c02"),
    "kind2 separate variant push": (0x4F1BA0, "668b9622020000"),
    "kind2 descriptor ptr": (0x4F1BBA, "8d54243c"),
    "kind2 MonsterObject ctor": (0x4F1BC7, "e8d453feff"),
    "kind4 branch": (0x4F1BD1, "3c04"),
    "kind4 separate variant push": (0x4F1C09, "668b8e22020000"),
    "kind4 descriptor ptr": (0x4F1C23, "8d4c243c"),
    "kind4 MonsterObject ctor": (0x4F1C31, "e86a53feff"),
    "MonsterObject ctor receives visual descriptor ptr": (0x4D7020, "8bcb8b11"),
    "MonsterObject ctor copies descriptor": (0x4D7024, "8d868c0200008910"),
    "MonsterObject ctor separate variant to float": (0x4D7056, "db442434"),
    "MonsterObject ctor stores variant float": (0x4D7061, "d99e7c020000"),
    "MonsterObject invokes image object factory": (0x4D70A6, "e895b2ffff"),
    "image factory receives visual descriptor": (0x4D2356, "8b742414"),
    "image factory deref descriptor first u16": (0x4D235C, "668b06"),
    "image factory calls bank quotient": (0x4D2361, "e8ca510000"),
    "image factory calls slot remainder": (0x4D236E, "e8ed510000"),
    "bank quotient subtract0x4000": (0x4D7535, "81e900400000"),
    "slot remainder subtract0x4000": (0x4D7565, "81e900400000"),
    "bank offset +0x1F40": (0x4D754A, "8d8402401f0000"),
    "slot modulo10": (0x4D757C, "8d0480"),
    "motion selector bound0..5": (0x4D6BC4, "83f805"),
    "local motion base+0x20": (0x4D6BDA, "66052000"),
    "local motion base+0x30": (0x4D6BE7, "66053000"),
    "local motion base+0x40": (0x4D6BF4, "66054000"),
    "C43 info panel state switch": (0x4A2376, "8a464884c0"),
    "C43 panel subtype04 type1": (0x4A2409, "c6402401"),
    "C43 panel subtype04": (0x4A2410, "c6402c04"),
    "C43 panel subtype10": (0x4A24B3, "c6402c10"),
    "C43 panel subtype40": (0x4A254F, "c6402c40"),
    "C43 panel all modes use object ref": (0x4A2553, "894828"),
    "C43 panel enqueues packet": (0x4A2558, "e843630d00"),
    "C43 other type1/subtype04 UI producer": (0x479DEB, "e8b0ea0f00"),
}


def probe(file):
    data = Path(file).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != SHA:
        raise ValueError("original Asgard.exe SHA mismatch: " + sha)
    pe, = struct.unpack_from("<I", data, 0x3C)
    if data[pe:pe+4] != b"PE\x00\x00" or struct.unpack_from("<H", data, pe+24)[0] != 0x10B:
        raise ValueError("not original PE32")
    base, = struct.unpack_from("<I", data, pe+52)
    count, = struct.unpack_from("<H", data, pe+6)
    sections = pe+24+struct.unpack_from("<H", data, pe+20)[0]

    def read_va(va, length):
        for index in range(count):
            offset = sections+40*index
            size,rva,raw_size,raw_at = struct.unpack_from("<IIII", data, offset+8)
            delta = va-base-rva
            if delta >= 0 and delta+length <= min(size,raw_size):
                return data[raw_at+delta:raw_at+delta+length]
        raise ValueError("unmapped native VA: " + hex(va))

    for label, (va, pattern) in ANCHORS.items():
        expected = bytes.fromhex(pattern)
        if read_va(va, len(expected)) != expected:
            raise AssertionError("native VA evidence changed: " + label + " " + hex(va))
    print(f"A-011 original PE PASS: {len(ANCHORS)} S07->MonsterObject->MonsterImageLib instruction anchors")
    print("S07 field_c BEu16 -> bank/slot, variant_u16 is separate; original GUI and original Monster/World assets NOT-RUN")
    return len(ANCHORS)


if __name__ == "__main__":
    probe(sys.argv[1] if len(sys.argv) > 1 else "Asgard.exe")
