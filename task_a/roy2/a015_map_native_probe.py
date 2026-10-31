#!/usr/bin/env python3
"""A-015 original Asgard.exe SHA-locked MAP/collision/coordinate native byte probe."""
import hashlib,struct,sys
from pathlib import Path
SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
ANCHORS={
"block 2B":(0x4b2c60,"8b 81 48 02 00 00 0f af 44 24 08"),
"tile width*row+column":(0x4b2c80,"8b 91 40 02 00 00 0f af 54 24 08"),
"client tile stride17":(0x4b2c91,"c1 e0 04 03 c2"),
"bit0 setter":(0x4b2cc7,"83 c8 01 89 42 06"),
"bit0 clearer":(0x4b2cd0,"83 e0 fe 89 42 06"),
"auxiliary u32 grid":(0x4b2ce0,"8b 81 40 02 00 00"),
"auxiliary neighbor grid":(0x4b2d1e,"8b 1c b9 85 db 8d 3c b9"),
"auxiliary adjacent zero":(0x4b2d38,"83 38 00 75 19 8b 48 04"),
"aux grid header guard":(0x4b32c6,"0f b7 46 04 0f bf 4c 24 10"),
"aux grid marking cell1":(0x4b32ea,"03 d0 c7 04 91 01 00 00 00"),
"MAP block ceil dims":(0x4b34a5,"8d 45 ff 99 2b c2 d1 f8"),
"MAP allocated tile stride17":(0x4b34e6,"c1 e1 04 03 cb"),
"MAP LE u32 flags at+6":(0x4b3557,"8b 0f 83 c7 04 89 48 06"),
"tail7":(0x4b3575,"8b 17 8b c2 6b c0 07"),
"tail8":(0x4b35ad,"6a 00 8d 3c d7"),
"tail16":(0x4b35bc,"8b 07 68 aa 00 00 00"),
"derived aux grid loader call":(0x4b35f6,"e8 55 fc ff ff"),
"tile bound negative x":(0x4b4925,"85 db 56 57"),
"tile bound x greater":(0x4b493b,"3b d8 7d 32"),
"tile bound y greater":(0x4b4955,"3b f9 7d 18"),
"pixel height 32":(0x4b4a3b,"c1 e2 05 3b d3"),
"pixel width 48":(0x4b4a73,"8d 14 40 c1 e2 04"),
"line test bit4":(0x4b4beb,"b3 10"),
"line checks tile+6":(0x4b4c03,"84 58 06"),
"other consumer bit0":(0x4d120b,"f6 40 06 01"),
"C35 header read +4":(0x4b4850,"8b 81 b4 00 00 00 66 8b 40 04")
}
def pe_bytes(b,va,count):
    peoff,=struct.unpack_from("<I",b,0x3c)
    if b[peoff:peoff+4]!=b"PE\0\0":raise ValueError("bad PE")
    n,=struct.unpack_from("<H",b,peoff+6)
    opt=peoff+24
    if struct.unpack_from("<H",b,opt)[0]!=0x10b:raise ValueError("not PE32")
    base,=struct.unpack_from("<I",b,opt+28)
    sh=opt+struct.unpack_from("<H",b,peoff+20)[0]
    for i in range(n):
        o=sh+40*i
        virt,rva,rawsize,raw=struct.unpack_from("<IIII",b,o+8)
        if base+rva<=va and va+count<=base+rva+min(virt,rawsize):
            p=raw+va-base-rva
            return b[p:p+count]
    raise ValueError("VA not mapped")
def verify(filename):
    b=Path(filename).read_bytes()
    if hashlib.sha256(b).hexdigest()!=SHA:raise ValueError("original EXE SHA mismatch")
    for name,(va,pattern) in ANCHORS.items():
        expect=bytes.fromhex(pattern)
        if pe_bytes(b,va,len(expect))!=expect:
            raise ValueError("invalid native anchor "+name)
        print("PASS",name,hex(va))
    print("PASS A-015 26 native VA checks; original player collision/GUI E2E not run")
if __name__=="__main__":verify(sys.argv[1] if len(sys.argv)>1 else "Asgard.exe")
