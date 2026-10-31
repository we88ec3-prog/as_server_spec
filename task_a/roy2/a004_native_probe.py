#!/usr/bin/env python3
"""A-004 original PE32 reader/constructor locator audit; exports metadata only."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
CONSTRUCTORS = {
    "S33.PutHuman": (0x5854D0, 0x33),
    "S06.MoveHumanAck": (0x583220, 0x06),
    "S11.ChangeDirection": (0x57D6C0, 0x11),
    "S0B.Move": (0x5830A0, 0x0B),
    "S0E.RemoveObjects": (0x585E60, 0x0E),
}
READERS = {
    "S06": (0x5832D0, [0x45AEB0, 0x45ADE0, 0x45ADE0], 0x30),
    "S11": (0x57D770, [0x45AEB0, 0x45ADB0], 0x20),
    "S0B": (0x583150, [0x45ADE0, 0x45ADE0, 0x45ADB0], 0x30),
    "S0E": (0x585F10, [0x45AEB0], 0x15),
    "S33Prefix": (0x585570, [0x45ADE0, 0x45ADE0, 0x45ADB0, 0x45AEB0], 0x30),
}

def audit(path):
    data = Path(path).read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA:
        raise ValueError("Client SHA256 does not match the audited original")
    peoff = struct.unpack_from("<I", data, 0x3c)[0]
    if data[peoff:peoff+4] != b"PE\x00\x00":
        raise ValueError("not PE")
    n = struct.unpack_from("<H", data, peoff+6)[0]
    optional = peoff+24
    if struct.unpack_from("<H", data, optional)[0] != 0x10b:
        raise ValueError("not PE32")
    base = struct.unpack_from("<I", data, optional+28)[0]
    sec = optional + struct.unpack_from("<H", data, peoff+20)[0]
    regions = []
    for i in range(n):
        off = sec + i*40
        vsize, rva, rsize, raw = struct.unpack_from("<IIII", data, off+8)
        regions.append((base+rva, raw, min(vsize,rsize)))
    def position(va):
        for start, raw, size in regions:
            if start <= va < start+size:
                return raw+va-start
        raise ValueError("unmapped VA " + hex(va))
    def relative_calls(va, size):
        pos = position(va)
        result = []
        for i in range(size-4):
            if data[pos+i] == 0xe8:
                disp = struct.unpack_from("<i", data, pos+i+1)[0]
                result.append(va+i+5+disp)
        return result
    for name,(va,opcode) in CONSTRUCTORS.items():
        pos = position(va)
        if bytes((0x6a,opcode)) not in data[pos:pos+0x32]:
            raise AssertionError("constructor push " + name)
        if 0x578730 not in relative_calls(va,0x36):
            raise AssertionError("constructor base call " + name)
    for name,(va,expected,size) in READERS.items():
        found=iter(relative_calls(va,size))
        if not all(any(addr==want for addr in found) for want in expected):
            raise AssertionError("native reader order " + name)
    return {
        "status":"PASS", "client_sha256":sha, "image_base":hex(base),
        "constructors":{k:{"va":hex(v[0]),"opcode":hex(v[1])}
                        for k,v in CONSTRUCTORS.items()},
        "readers":{k:{"va":hex(v[0]),"targets":[hex(x) for x in v[1]]}
                   for k,v in READERS.items()},
        "native_client_E2E":"not-run", "original_assets_exported":False
    }

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("client",type=Path)
    args=p.parse_args()
    print(json.dumps(audit(args.client),indent=2))
