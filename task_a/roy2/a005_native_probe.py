#!/usr/bin/env python3
"""A005: confirm native PE32 call/writer/flag sequences on user-owned original."""
import argparse, hashlib, json, struct
from pathlib import Path
EXPECTED="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
def audit(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=EXPECTED: raise ValueError("unknown Asgard.exe SHA")
    off,=struct.unpack_from("<I",b,0x3c)
    if b[off:off+4]!=b"PE\x00\x00": raise ValueError("not PE32")
    n,=struct.unpack_from("<H",b,off+6)
    opt=off+24
    if struct.unpack_from("<H",b,opt)[0]!=0x10b:raise ValueError("not PE32")
    base,=struct.unpack_from("<I",b,opt+28)
    sec=opt+struct.unpack_from("<H",b,off+20)[0]
    def read(va,size):
        for i in range(n):
            o=sec+i*40
            vs,rva,rs,raw=struct.unpack_from("<IIII",b,o+8)
            limit=min(vs,rs)
            if base+rva<=va and va+size<=base+rva+limit:
                pos=raw+va-base-rva
                return b[pos:pos+size]
        raise ValueError("unmapped VA "+hex(va))
    checks=[
        ("C33 three u8 writers",0x573bf0,0x30,["e8036feeff","e8f76eeeff","e8eb6eeeff"]),
        ("C11 one u8 writer",0x571960,0x10,["e89691eeff"]),
        ("S0B BE16 BE16 u8",0x583150,0x26,["e8887cedff","e87d7cedff","e8427cedff"]),
        ("MAP 17byte tile copies flag+6",0x4b3520,0x42,["c1e004","894806"]),
        ("MAP flag bit0 dynamic set/clear",0x4b2ca0,0x3a,["83c801","83e0fe"]),
        ("MAP line-check bit4",0x4b4be7,0x180,["b310","845806"]),
        ("MAP different consumer tests bit0",0x4d1204,0x12,["f6400601"]),
    ]
    for name,va,check_size,ops in checks:
        raw=read(va,check_size)
        if not all(bytes.fromhex(p) in raw for p in ops):
            raise AssertionError(name+" native bytes mismatch")
    return {"status":"PASS","native_checks":len(checks),"sha256":EXPECTED,
            "check_names":[x[0] for x in checks],"native_client_E2E":"not-run",
            "original_assets_shared":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("client");args=p.parse_args()
    print(json.dumps(audit(args.client),indent=2))
