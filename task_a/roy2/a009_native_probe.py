#!/usr/bin/env python3
"""A-009 SHA-locked original Asgard.exe native PE evidence; no assets exported."""
from pathlib import Path
import hashlib
import sys
SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
# ImageBase=0x400000, .text raw file offset matches RVA for this exact PE.
CHECKS={
 "C13 Attack ctor opcode":(0x570a29,"6a 13"),
 "C13 Attack BE-u32 writer":(0x570ac0,"8b 41 18 50 e8 77 a1 ee ff"),
 "C13 producer 1":(0x55709e,"e8 6d 99 01 00"),
 "C13 producer 2":(0x557a5f,"e8 ac 8f 01 00"),
 "C3D Battle ctor opcode":(0x5711cb,"6a 3d"),
 "C3D subtype writer":(0x570de0,"56 8b f1 8b 46 18 50"),
 "S3D Battle ctor opcode":(0x57c6ec,"6a 3d"),
 "S3D subtype parser 0..15":(0x57c8ba,"e8 f1 e4 ed ff"),
 "S13 DamageEffect ctor opcode":(0x57ddf9,"6a 13"),
 "S13 DamageEffect first BE-u32":(0x57de93,"e8 18 d0 ed ff"),
 "S13 packed-opaque bit 3":(0x57decc,"a8 08"),
 "S13 packed-opaque bit 4":(0x57def6,"a8 10"),
 "S13 optional bit 0":(0x57df1b,"a8 01"),
 "S5F DieObjects ctor opcode":(0x57e1c9,"6a 5f"),
 "S5F DieObjects BE-u32":(0x57e263,"e8 48 cc ed ff"),
 "S08 status callback (A008)":(0x54066a,"83 78 08 08"),
}
RTTI=("CAttackPacket","CBattlePacket","SBattlePacket",
      "SDamageEffectPacket","SDieObjectsPacket")
def verify(path):
    data=Path(path).read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    if digest != SHA: raise ValueError(f"wrong client profile sha256 {digest}")
    for label,(va,hexdump) in CHECKS.items():
        expected=bytes.fromhex(hexdump)
        ofs=va-0x400000
        if data[ofs:ofs+len(expected)] != expected:
            raise ValueError(f"{label} mismatch at VA 0x{va:x}")
        print(f"PASS native {label} 0x{va:x}")
    for name in RTTI:
        token=(".?AV"+name+"@@\0").encode()
        if data.count(token)!=1: raise ValueError("missing or ambiguous RTTI "+name)
        print("PASS RTTI",name)
    print(f"A009 PASS: {len(CHECKS)} native byte patterns and {len(RTTI)} RTTI; native Client E2E not run")
if __name__=="__main__":
    verify(sys.argv[1] if len(sys.argv)>1 else "Asgard.exe")
