#!/usr/bin/env python3
"""A-008 SHA-locked original Asgard.exe instruction-pattern checks, no game assets exported."""
import hashlib
import sys
from pathlib import Path

SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
# PE has .text raw file offset 0x1000, VMA 0x401000 -> fileoffset = VA - 0x400000.
CHECKS = {
    "S08 ctor opcode": (0x586ceb, "6a 08"),
    "S08 read entry": (0x586d40, "83 ec 08 53 55 56 57"),
    "S08 flags read u16": (0x586d49, "e8 92 40 ed ff"),
    "S08 full mask 0x40": (0x586d7b, "f6 c3 40"),
    "S08 full skip 1": (0x586d97, "6a 01"),
    "S08 current mask 0x20": (0x586eeb, "f6 c3 20"),
    "S08 secondary mask 0x10": (0x586f22, "f6 c3 10"),
    "S08 text mask 0x08": (0x586f75, "f6 c3 08"),
    "S08 array mask 0x200": (0x586fd9, "f6 c7 02"),
    "S08 GUI handler checks opcode": (0x54066a, "83 78 08 08"),
    "C47 ctor opcode": (0x5708c9, "6a 47"),
    "C47 one-byte writer": (0x570960, "0f b6 41 18 50 e8 96 a1 ee ff"),
    "C47 StatusDialog button IDs 19..23": (0x53fd7a, "83 fe 13 7c 72"),
    "C47 one-hot 0x01": (0x53fdce, "c6 40 24 01"),
    "C47 one-hot 0x10": (0x53fde6, "c6 40 24 10"),
}
RTTI = ("SStatusPacket", "StatusDialog", "ExpBarDialog", "CAddAbilityPacket")

def verify(path):
    raw = Path(path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != SHA:
        raise ValueError(f"wrong client SHA256 {sha}")
    for name, (va, pattern) in CHECKS.items():
        expected = bytes.fromhex(pattern)
        off = va - 0x400000
        if raw[off:off+len(expected)] != expected:
            raise ValueError(f"instruction mismatch at 0x{va:X} ({name})")
        print(f"PASS 0x{va:X} {name}")
    for name in RTTI:
        if raw.count((".?AV"+name+"@@\0").encode()) != 1:
            raise ValueError(f"missing or duplicated RTTI {name}")
        print(f"PASS RTTI {name}")
    print("A-008 PASS: 15 native instruction patterns, 4 RTTI classes; native GUI E2E not run.")

if __name__ == "__main__":
    verify(sys.argv[1] if len(sys.argv) > 1 else "Asgard.exe")
