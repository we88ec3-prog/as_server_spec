#!/usr/bin/env python3
"""A-024: SHA-locked native PE evidence, S07 two-level switch, and object packet ctor/readers.

PE file offset=VA-0x400000 in this exact original image. Does not export game assets.
"""
from pathlib import Path
import hashlib
import struct
import sys

EXPECTED_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
IMAGE_BASE=0x400000
ANCHORS={
    "S07 count BE u16":(0x57e3e5,"e8 f6 c9 ed ff"),
    "S07 local row stride 0x228":(0x57e3f1,"69 c0 28 02 00 00"),
    "S07 type 1..14 gate":(0x57e45a,"0f b6 46 04 48 83 f8 0d"),
    "S07 two-level jump":(0x57e46f,"ff 24 8d d4 e5 57 00"),
    "S07 optional bit0":(0x57e4c4,"a8 01"),
    "S07 optional bit1":(0x57e4f2,"f6 46 10 02"),
    "S07 optional bit4":(0x57e505,"f6 46 10 10"),
    "S07 first kind text":(0x57e531,"e8 6a d2 ed ff"),
    "S07 type13 string branch":(0x57e57e,"6a 00 68 ff 00 00 00"),
    "S07 type14 two u8/u16 branch":(0x57e592,"8b cf e8 17 c8 ed ff"),
    "S3C info reader BE u32":(0x586ad3,"e8 d8 43 ed ff"),
    "S34 object info common header":(0x584555,"e8 56 68 ed ff"),
    "S34 dynamic subtype11 gate":(0x584569,"e8 42 68 ed ff"),
    "S34 subtype6 gate":(0x58492a,"80 f9 06"),
    "S62 add action ctor":(0x578f89,"6a 62"),
    "S62 add action reader":(0x579023,"e8 88 1d ee ff"),
    "S63 remove action ctor":(0x5858b9,"6a 63"),
    "S63 remove action reader":(0x585953,"e8 58 54 ed ff"),
    "S29 effect ctor":(0x57e6b9,"6a 29"),
    "S29 effect reader":(0x57e762,"e8 49 c7 ed ff"),
}
# kind 1..14 -> jump group by native index
EXPECTED_GROUPS=[0,0,1,0,4,4,4,4,4,4,4,4,2,3]
EXPECTED_ADDRS=[0x57e476,0x57e538,0x57e57e,0x57e592,0x57e5b1]
RTTI=("SDrawObjectsPacket","SObjectInfoReplyPacket","SShowObjectInfoPacket",
      "SAddActionPacket","SRemoveActionPacket","SEffectPacket")

def scan(path):
    image=Path(path).read_bytes()
    digest=hashlib.sha256(image).hexdigest()
    if digest!=EXPECTED_SHA:
        raise ValueError("client SHA mismatch: "+digest)
    def raw(va,n):
        off=va-IMAGE_BASE
        if off<0 or off+n>len(image):raise ValueError("VA out of file")
        return image[off:off+n]
    for label,(va,signature) in ANCHORS.items():
        expected=bytes.fromhex(signature)
        if raw(va,len(expected))!=expected:
            raise ValueError(f"native byte mismatch: {label} VA 0x{va:X}")
        print(f"PASS 0x{va:X} {label}")
    groups=list(raw(0x57e5e8,14))
    addrs=list(struct.unpack("<5I",raw(0x57e5d4,20)))
    if groups!=EXPECTED_GROUPS or addrs!=EXPECTED_ADDRS:
        raise ValueError("S07 type jump dispatch mismatch")
    print("PASS S07 14 type entries / five exact jump destinations")
    for classname in RTTI:
        token=(".?AV"+classname+"@@\0").encode("ascii")
        if image.count(token)!=1:
            raise ValueError("RTTI class missing/ambiguous: "+classname)
        print("PASS RTTI "+classname)
    print("A-024 native probe PASS: 20 anchors, 14 type switches, six RTTI; original GUI not-run")

if __name__=="__main__":
    scan(sys.argv[1] if len(sys.argv)>1 else "Asgard.exe")
