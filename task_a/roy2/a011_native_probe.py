#!/usr/bin/env python3
"""A-011 SHA-locked native PE evidence; original executable is never committed.

The mapped .text/.rdata offsets in this EXE satisfy file_off = VA - 0x400000.
Check original resource registry, sprite quotient/remainder, S07 MonsterObject,
local animation group switch, C43 producer and RTTI anchors.
"""
import hashlib
from pathlib import Path
import sys

SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
ANCHORS={
 "World 7000 registry start":(0x404331,"bf 58 1b 00 00"),
 "World format pointer":(0x40434b,"68 5c 1d 5f 00"),
 "World 7023 registry end":(0x404369,"81 ff 6f 1b 00 00"),
 "Monster 8000 registry start":(0x404371,"bf 40 1f 00 00"),
 "Monster format pointer skips @":(0x40438b,"68 3c 1d 5f 00"),
 "Monster 8042 registry end":(0x4043a9,"81 ff 6a 1f 00 00"),
 "Monster sprite subtract 0x4000":(0x4d7535,"81 e9 00 40 00 00"),
 "Monster library index +8000":(0x4d754a,"8d 84 02 40 1f 00 00"),
 "Monster intra-file sprite subtract 0x4000":(0x4d7565,"81 e9 00 40 00 00"),
 "Monster modulo10 multiply":(0x4d757c,"8d 04 80"),
 "S07 kind1 MonsterObject branch":(0x4f1a8b,"3c 01"),
 "S07 kind2 MonsterObject branch":(0x4f1b68,"3c 02"),
 "S07 kind4 MonsterObject branch":(0x4f1bd1,"3c 04"),
 "S07 kind1 native ctor call":(0x4f1aeb,"e8 b0 54 fe ff"),
 "S07 kind2 native ctor call":(0x4f1bc7,"e8 d4 53 fe ff"),
 "S07 kind4 native ctor call":(0x4f1c31,"e8 6a 53 fe ff"),
 "MonsterObject constructor local motion field":(0x4d70c1,"66 8b 87 68 02 00 00"),
 "Monster local motion selector 0..5":(0x4d6bc4,"83 f8 05"),
 "Monster local motion +0x20":(0x4d6bda,"66 05 20 00"),
 "Monster local motion +0x30":(0x4d6be7,"66 05 30 00"),
 "Monster local motion +0x40":(0x4d6bf4,"66 05 40 00"),
 "C43 constructor opcode":(0x574519,"6a 43"),
 "C43 first u8 writer":(0x5745b3,"0f b6 46 18"),
 "C43 object-info producer A":(0x479dc7,"e8 34 a7 0f 00"),
 "C43 object-info producer B":(0x4a23f8,"e8 03 21 0d 00"),
 "C43 producer A type1":(0x479ddb,"c6 40 24 01"),
 "C43 producer A subtype4":(0x479de7,"c6 40 2c 04"),
 "C43 producer B type1":(0x4a2409,"c6 40 24 01"),
 "C43 producer B subtype4":(0x4a2410,"c6 40 2c 04"),
}
RTTI=("MonsterObject","MonsterImageLib","NPCChatDialog","NonHumanInfoObject")

def verify(path):
    data=Path(path).read_bytes()
    got=hashlib.sha256(data).hexdigest()
    if got != SHA:
        raise ValueError("unexpected Asgard.exe SHA256: "+got)
    for name,(va,patt) in ANCHORS.items():
        want=bytes.fromhex(patt)
        if data[va-0x400000:va-0x400000+len(want)] != want:
            raise ValueError(f"instruction mismatch {name} at VA 0x{va:X}")
        print("PASS 0x%X %s"%(va,name))
    for name in RTTI:
        if data.count((".?AV"+name+"@@\x00").encode())!=1:
            raise ValueError("ambiguous native RTTI "+name)
        print("PASS RTTI",name)
    def wide(va):
        p=va-0x400000
        chars=[]
        while data[p:p+2]!=b"\x00\x00":
            chars.append(data[p:p+2]);p+=2
        return b"".join(chars).decode("utf-16le")
    if wide(0x5f1d3c)!="Monster%02d.dat" or wide(0x5f1d5c)!="World%02d.dat" or wide(0x5f1d3a)!="@Monster%02d.dat":
        raise ValueError("resource format string pointers not matching")
    print("A-011 PASS: 29 original byte anchors, 4 RTTI, 3 wide literals; native UI E2E not-run")

if __name__=="__main__":
    verify(sys.argv[1] if len(sys.argv)>1 else "Asgard.exe")
