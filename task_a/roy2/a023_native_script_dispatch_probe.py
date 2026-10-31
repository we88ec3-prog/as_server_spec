#!/usr/bin/env python3
"""A-023 original S44 type1 vs type2 GUI dispatch evidence, SHA-locked PE32.

No original game binary is committed. The native Client/UI E2E is not run.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
ANCHORS = {
    "S44 handler obtains Script manager":(0x4E0B79,"8b0d3cd16600"),
    "S44 handler invokes Script manager":(0x4E0B80,"e81bb70400"),
    "S44 type2 branch":(0x4E0B87,"807f2402"),
    "S44 type2 requires Script handler result":(0x4E0B91,"85db"),
    "S44 type2 subtype selector":(0x4E0B99,"8a4725"),
    "S44 type2 subtype0 guard":(0x4E0B9C,"84c0"),
    "type2/0 UI manager global":(0x4E0BA4,"8b0d40d16600"),
    "type2/0 UI slot 0x23":(0x4E0BAA,"6a23"),
    "type2/0 slot lookup":(0x4E0BAC,"e8ef490500"),
    "type2/0 slot activation id":(0x4E0BBD,"6a23"),
    "type2/0 slot activation call":(0x4E0BBF,"e82c4f0500"),
    "type2/0 pane component 4":(0x4E0BC4,"6a04"),
    "type2/0 pane component 3":(0x4E0BD4,"6a03"),
    "type2/2 selector":(0x4E0C3E,"3c02"),
    "type2/2 slot 0x24":(0x4E0C48,"6a24"),
    "type2/2 slot method":(0x4E0C4A,"e841490500"),
    "type2/2 pane handler":(0x4E0C51,"e82a2c0000"),
    "Script manager type selector":(0x52C2CA,"8a4524"),
    "Script manager type1 start test":(0x52C2CD,"3c01"),
    "Script manager type1 subtype switch":(0x52C2E6,"ff24850ccb5200"),
    "S44 parser entry":(0x586410,"515356578bf1"),
    "Script runner Main call":(0x52C014,"e8878fffff"),
}

def audit(original):
    data=Path(original).read_bytes()
    if hashlib.sha256(data).hexdigest()!=SHA:
        raise ValueError("original Asgard.exe SHA mismatch")
    pe,=struct.unpack_from("<I",data,0x3c)
    if data[pe:pe+4]!=b"PE\x00\x00":
        raise ValueError("not PE")
    opt=pe+24
    if struct.unpack_from("<H",data,opt)[0]!=0x10b:
        raise ValueError("not PE32")
    base,=struct.unpack_from("<I",data,opt+28)
    section=opt+struct.unpack_from("<H",data,pe+20)[0]
    n,=struct.unpack_from("<H",data,pe+6)
    def read_va(va, size):
        for i in range(n):
            o=section+40*i
            vs,rva,raw_size,raw_off=struct.unpack_from("<IIII",data,o+8)
            delta=va-base-rva
            if 0<=delta and delta+size<=min(vs,raw_size):
                return data[raw_off+delta:raw_off+delta+size]
        raise ValueError("unmapped native VA "+hex(va))
    for label,(va,hexstr) in ANCHORS.items():
        expected=bytes.fromhex(hexstr)
        if read_va(va,len(expected))!=expected:
            raise ValueError(f"native instruction mismatch {va:#x}: {label}")
    return {
        "result":"PASS",
        "client_sha256":SHA,
        "original_instruction_anchors":len(ANCHORS),
        "type1_start":"0x52C2CA type1 → 0x52C2E6 branch, ScriptRunner Main (existing A023)",
        "type2_0":"0x4E0B87 type2/0 + handler result, UI slot0x23, pane components3/4",
        "type2_2":"0x4E0C3E type2/2 → UI slot0x24 method0x4E3880",
        "ui_slot_semantics":"unknown, not an NPC identity/quest completion or Born startup",
        "original_server_first_Born_push":"unknown",
        "native_client_validation":"not-run",
    }

if __name__=="__main__":
    try:
        print(json.dumps(audit(sys.argv[1] if len(sys.argv)>1 else "Asgard.exe"),indent=2))
    except (OSError, ValueError, struct.error) as e:
        sys.exit("FAIL A-023 native dispatch: "+str(e))
