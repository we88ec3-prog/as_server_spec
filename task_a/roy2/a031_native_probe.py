#!/usr/bin/env python3
"""A-031 original Asgard.exe 0x25 CBillingInfo and post-C10 region3 evidence.

No original binary is included. Native static verification only, not World E2E.
"""
import hashlib
import struct
import sys
from pathlib import Path
SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
ANCHORS={
"C25 ctor entry":(0x5712e0,"6a ff 68 f8 4d 5e 00"),
"C25 constructor opcode 0x25":(0x5712f9,"6a 25"),
"C25 packet vtable":(0x57130c,"c7 06 0c 36 61 00"),
"C25 packet writer dispatch vtable":(0x571312,"c7 46 0c 00 36 61 00"),
"C25 writer entry":(0x571420,"56 8b f1"),
"C25 region selected":(0x571429,"e8 d2 6b f2 ff"),
"C25 region3 guard":(0x57142e,"83 f8 03 75 47"),
"C25 first local string":(0x571433,"57 8d 7e 18"),
"C25 first string8 write":(0x571444,"e8 67 9d ee ff"),
"C25 second string8 write":(0x57145c,"e8 4f 9d ee ff"),
"C25 third string8 write":(0x571474,"e8 37 9d ee ff"),
"native string8 encoder":(0x45b1b0,"81 ec 04 01 00 00"),
"native WideCharToMultiByte":(0x45b218,"ff 15 b0 12 5f 00"),
"native string8 byte prefix":(0x45b25f,"88 04 11"),
"S03 handler region3 guard":(0x4a8391,"e8 6a fc fe ff 83 f8 03"),
"S03 handler C10 constructed":(0x4a8415,"e8 16 ef 0c 00"),
"S03 handler C10 sent":(0x4a8446,"e8 55 04 0d 00"),
"S03 handler C25 constructed":(0x4a8478,"e8 63 8e 0c 00"),
"S03 handler billing global":(0x4a8491,"68 ff 00 00 00 8d 47 0c"),
"S03 handler second global field":(0x4a84a8,"8d 97 0c 02 00 00"),
"S03 handler third global field":(0x4a84c9,"81 c7 0e 04 00 00"),
"S03 handler C25 sent":(0x4a84f3,"e8 a8 03 0d 00"),
"alternate C10 constructed":(0x52fb5b,"e8 d0 77 04 00"),
"alternate C10 sent":(0x52fb8c,"e8 0f 8d 04 00"),
"alternate region3 C25 guard":(0x52fba1,"83 f8 03 0f 85"),
"alternate C25 constructed":(0x52fbd6,"e8 05 17 04 00"),
"alternate C25 sent":(0x52fc4b,"e8 50 8c 04 00"),
"other producer region3 guard":(0x4a92b1,"83 f8 03 0f 85"),
"other producer C25 constructed":(0x4a92e2,"e8 f9 7f 0c 00"),
"other producer C25 sent":(0x4a9357,"e8 44 f5 0c 00"),
"fourth producer region3 guard":(0x432221,"83 f8 03 0f 85"),
"fourth producer C25 constructed":(0x432259,"e8 82 f0 13 00"),
"fourth producer C25 sent":(0x4322d1,"e8 ca 65 14 00"),
"C10 constructor":(0x577330,"6a ff 68 48 63 5e 00"),
"C10 raw bytes writer":(0x5773e0,"0f b6 41 18 50"),
}
def verify(path):
    b=Path(path).read_bytes()
    digest=hashlib.sha256(b).hexdigest()
    if digest!=SHA:
        raise ValueError("unexpected Asgard.exe SHA "+digest)
    pe,=struct.unpack_from("<I",b,0x3c)
    if b[pe:pe+4]!=b"PE\0\0":raise ValueError("invalid PE")
    opt=pe+24
    if struct.unpack_from("<H",b,opt)[0]!=0x10b:raise ValueError("not PE32")
    base,=struct.unpack_from("<I",b,opt+28)
    sections=opt+struct.unpack_from("<H",b,pe+20)[0]
    n,=struct.unpack_from("<H",b,pe+6)
    def read(va,nbytes):
        for i in range(n):
            o=sections+40*i
            vs,rva,rawsize,rawoff=struct.unpack_from("<IIII",b,o+8)
            off=va-(base+rva)
            if 0<=off and off+nbytes<=min(vs,rawsize):
                return b[rawoff+off:rawoff+off+nbytes]
        raise ValueError("VA not mapped "+hex(va))
    for name,(va,hexbytes) in ANCHORS.items():
        expect=bytes.fromhex(hexbytes)
        if read(va,len(expect))!=expect:
            raise AssertionError("native mismatch %s at %x"%(name,va))
        print("PASS",hex(va),name)
    # RTTI: native vtable COL 0x62bb84 +0x0c -> 0x6692a4
    col=read(0x62bb84,20)
    typeva,=struct.unpack_from("<I",col,12)
    if typeva!=0x6692a4 or b".?AVCBillingInfoPacket@@\x00" not in read(typeva,80):
        raise AssertionError("opcode0x25 constructor vtable RTTI not CBillingInfoPacket")
    if b.count(b".?AVCBillingInfoPacket@@\x00")!=1:
        raise AssertionError("ambiguous CBillingInfoPacket RTTI")
    print("PASS C25 vtable COL -> CBillingInfoPacket, not WorldEntryMetadata")
    print("A-031 PASS %d native VA anchors + RTTI; native TCP and GUI not-run"%len(ANCHORS))
if __name__=="__main__":
    verify(sys.argv[1] if len(sys.argv)>1 else "Asgard.exe")
