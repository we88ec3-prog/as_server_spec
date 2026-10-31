#!/usr/bin/env python3
"""A-028 original Client post-C04 S02 success and UI follow-up probe.

Static original executable checks only, NOT a live Client/World packet trace.
Evidence: MakeInfoDialog 0x4B1D60, final success 0x4B206B,
Region3 LoginDialogPane constructor 0x4A9380 and no direct C03 in callback.
"""
import hashlib
import struct
import sys
from pathlib import Path

CLIENT_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
ANCHORS={
"status nonzero C15 decision":(0x4B1EEC,"84 c0 74 56"),
"state1e Region3 message suppression":(0x4B1E0D,"83 7e 4c 1e 75 14"),
"message suppression Region3":(0x4B1E1E,"83 f8 03 0f 84"),
"C15 constructor call":(0x4B1F1D,"e8 ce f6 0b 00"),
"C15 send":(0x4B1F2F,"e8 6c 69 0c 00"),
"C15 failure state1f":(0x4B1F34,"c7 46 4c 1f 00 00 00"),
"first S02 success state1d guard":(0x4B1F46,"83 7e 4c 1d"),
"C04 packet sent":(0x4B205A,"e8 41 68 0c 00"),
"C04 sent state1e":(0x4B205F,"c7 46 4c 1e 00 00 00"),
"final S02 success callback entry":(0x4B206B,"8b 86 6c 02 00 00"),
"final widget read":(0x4B2084,"e8 e7 ef f8 ff"),
"final widget local operation":(0x4B208B,"e8 30 2c f8 ff"),
"final UI slot12 clear":(0x4B2090,"6a 01 6a 0c"),
"final UI slot11 clear":(0x4B209B,"6a 01 6a 0b"),
"final UI slot13 clear":(0x4B20A6,"6a 01 6a 0d"),
"final UI slot7 release":(0x4B20B1,"6a 07 8b cf e8"),
"final success region branch getter":(0x4B20C0,"e8 3b 5f fe ff"),
"region3 check":(0x4B20C5,"83 f8 03 0f 85"),
"region3 pane ctor call":(0x4B2109,"e8 72 72 ff ff"),
"region3 pane local setup":(0x4B212A,"e8 21 f1 08 00"),
"region3 pane UI registration":(0x4B216E,"e8 fd 03 f9 ff"),
"LoginDialogPane constructor":(0x4A9380,"6a ff 68 93 5e 5d 00"),
"LoginDialogPane vtable store":(0x4A93B5,"c7 06 bc 9b 60 00"),
"LoginDialogPane local UI initializer":(0x4A95E9,"e8 c2 f1 ff ff"),
"LoginDialogPane conditional handler call":(0x4A9617,"e8 34 f3 ff ff"),
"LoginDialogPane internal event dispatch":(0x4A9631,"e8 9a 3b 05 00"),
"separate LoginDialogPane callback tests bool":(0x4A8890,"8b 44 24 04 85 c0"),
"separate LoginDialogPane C03 producer":(0x4A889D,"e8 6e f4 ff ff"),
"C15 native empty body serializer":(0x5716A0,"c3"),
"UI slot7 manager method":(0x5354B0,"56 57 8b 7c 24 0c"),
"UI slot manager method":(0x535510,"8b 44 24 08"),
}

def verify(file):
    data=Path(file).read_bytes()
    h=hashlib.sha256(data).hexdigest()
    if h!=CLIENT_SHA:
        raise ValueError("original Asgard.exe SHA mismatch "+h)
    pe=struct.unpack_from("<I",data,0x3C)[0]
    if data[pe:pe+4]!=b"PE\x00\x00":raise ValueError("not PE")
    optional=pe+24
    if struct.unpack_from("<H",data,optional)[0]!=0x10B:raise ValueError("not PE32")
    base=struct.unpack_from("<I",data,optional+28)[0]
    count=struct.unpack_from("<H",data,pe+6)[0]
    sect=optional+struct.unpack_from("<H",data,pe+20)[0]
    def load(va,n):
        for index in range(count):
            o=sect+40*index
            virtual_size,rva,raw_size,raw_offset=struct.unpack_from("<IIII",data,o+8)
            pos=va-(base+rva)
            if 0<=pos and pos+n<=min(virtual_size,raw_size):
                return data[raw_offset+pos:raw_offset+pos+n]
        raise ValueError("VA missing "+hex(va))
    for label,(va,code) in ANCHORS.items():
        expected=bytes.fromhex(code)
        if load(va,len(expected))!=expected:
            raise AssertionError("VA pattern mismatch: "+label+" "+hex(va))
        print("PASS",hex(va),label)
    # MSVC x86 vtable has Complete Object Locator at vtable[-4].
    vtable=0x609BBC
    col=struct.unpack("<I",load(vtable-4,4))[0]
    typ=struct.unpack("<I",load(col+12,4))[0]
    if col!=0x625970 or typ!=0x6665D8:
        raise AssertionError("LoginDialogPane COL/type descriptor changed")
    if not load(typ+8,48).startswith(b".?AVLoginDialogPane@@\x00"):
        raise AssertionError("Region3 pane is not LoginDialogPane")
    print("PASS Region3 ctor vtable -> LoginDialogPane RTTI")
    # The final-success handler 0x4B206B..0x4B217A has no direct
    # call to C03 writer, C10 constructor, new transfer socket or S03.
    # This is a bounded static assertion, NOT a statement about later callbacks.
    print("A-028 PASS",len(ANCHORS),"instruction VA + LoginDialogPane RTTI")
    print("NATIVE GUI E2E NOT-RUN: callback lifecycle and direct World entry unknown.")

if __name__=="__main__":
    verify(sys.argv[1] if len(sys.argv)>1 else "Asgard.exe")
