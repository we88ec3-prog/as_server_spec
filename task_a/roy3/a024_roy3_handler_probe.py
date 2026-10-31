#!/usr/bin/env python3
"""A024 roy3: hash-pinned native dispatch, object registry callbacks and C43 producer."""
import argparse,hashlib,json,struct
from pathlib import Path

SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
# opcode -> native dispatcher trampoline, target, packet label
HANDLERS={
 0x07:(0x4f492d,0x4f17c0,"DrawObjects"),
 0x0c:(0x4f4912,0x4f1610,"MoveObject"),
 0x0e:(0x4f493f,0x4f1da0,"RemoveObjects"),
 0x29:(0x4f4948,0x4f1dc0,"Effect"),
 0x5f:(0x4f49b3,0x4f2bb0,"DieObjects"),
 0x62:(0x4f49d7,0x4f2cd0,"AddAction"),
 0x63:(0x4f49e0,0x4f2f10,"RemoveAction"),
 0x64:(0x4f4924,0x4f1750,"MovePath")
}
CALLS={
 0x4f181c:0x4eac70,0x4f183f:0x4eac30,0x4f1896:0x4b80d0,
 0x4f1914:0x4dc030,0x4f1946:0x4ba090,0x4f196b:0x4c0640,
 0x4f19f4:0x496540,0x4f1aeb:0x4d6fa0,0x4f1bc7:0x4d6fa0,
 0x4f1c31:0x4d6fa0,0x4f1b12:0x4b6450,
 0x4f1623:0x4eac30,0x4f167c:0x46e3f0,
 0x4f175f:0x4eac30,0x4f17ac:0x47c9c0,
 0x4f2bc0:0x4eac30,0x4f2c01:0x4ba310,
 0x479dc7:0x574500,0x479deb:0x5788a0,
 0x4a23f8:0x574500,0x4a2558:0x5788a0
}
ANCHORS={
 0x4f48a4:"8b5008",0x4f48a7:"83c2fd",0x4f48aa:"83fa6e",
 0x4f48b3:"0fb692304b4f00",0x4f48ba:"ff2495784a4f00",
 0x4f17e2:"66395824",0x4f1810:"69f628020000",0x4f1821:"807e040e",
 0x4f182b:"807e1101",0x4f194b:"8a4604",0x4f194e:"3c0d",
 0x4f1975:"3c01",0x4f197d:"3c02",0x4f1985:"3c04",
 0x4f1991:"663d0080",0x4f199b:"663dffbf",
 0x4f1a25:"a801",0x4f1a5a:"a810",0x4f1a71:"a802",
 0x4f1a8b:"3c01",0x4f1b68:"3c02",0x4f1bd1:"3c04",
 0x4f1661:"a1d4d06600",0x4f169f:"8bce",0x4f16a1:"ff5234",
 0x4f16b9:"ff523c",0x4f16c6:"ff5040",
 0x4f1da0:"8b442404",0x4f1da4:"8b4824",0x4f1dab:"8b0dd8d06600",
 0x4f1db1:"e90a83fcff",
 0x4f2bbb:"8b4324",0x4f2bcb:"68d8fb9100",
 0x479ddb:"c6402401",0x479de2:"894828",0x479de7:"c6402c04",
 0x4a2409:"c6402401",0x4a2410:"c6402c04",0x4a2553:"894828"
}
class NativeError(ValueError):pass

def pe_reader(data):
    if data[:2]!=b"MZ":raise NativeError("not MZ")
    p=struct.unpack_from("<I",data,0x3c)[0]
    if data[p:p+4]!=b"PE\x00\x00":raise NativeError("not PE")
    n=struct.unpack_from("<H",data,p+6)[0];o=p+24
    if struct.unpack_from("<H",data,o)[0]!=0x10b:raise NativeError("not PE32")
    base=struct.unpack_from("<I",data,o+28)[0]
    s=o+struct.unpack_from("<H",data,p+20)[0];sections=[]
    for i in range(n):
        vsize,rva,rsize,raw=struct.unpack_from("<IIII",data,s+40*i+8)
        sections.append((base+rva,min(vsize,rsize),raw))
    def read(va,size):
        for start,length,raw in sections:
            if start<=va and va+size<=start+length:
                return data[raw+va-start:raw+va-start+size]
        raise NativeError("VA not file-backed: "+hex(va))
    return read

def decode_handler_slot(read,opcode):
    if not 3<=opcode<=0x71:raise NativeError("outside dispatch range")
    ix=read(0x4f4b30+opcode-3,1)[0]
    t=struct.unpack("<I",read(0x4f4a78+ix*4,4))[0]
    b=read(t,9)
    if b[:5]!=bytes.fromhex("89442404e9"):return (t,None,ix)
    return (t,t+9+struct.unpack_from("<i",b,5)[0],ix)

def verify_exe(path):
    data=Path(path).read_bytes();sha=hashlib.sha256(data).hexdigest()
    if sha!=SHA:raise NativeError("original executable SHA differs")
    read=pe_reader(data)
    for va,dest in CALLS.items():
        b=read(va,5)
        if b[0]!=0xe8 or va+5+struct.unpack_from("<i",b,1)[0]!=dest:
            raise NativeError("native call mismatch "+hex(va))
    for va,hx in ANCHORS.items():
        if read(va,len(hx)//2)!=bytes.fromhex(hx):
            raise NativeError("instruction mismatch "+hex(va))
    result={}
    for op,(trampoline,handler,name) in HANDLERS.items():
        if decode_handler_slot(read,op)[:2]!=(trampoline,handler):
            raise NativeError("handler mismatch "+hex(op))
        result["%02X"%op]={"trampoline_va":hex(trampoline),
                           "handler_va":hex(handler),"name":name}
    return {"exe_sha256":SHA,"result":"PASS","native_calls":len(CALLS),
            "native_instruction_anchors":len(ANCHORS),
            "dispatch_handlers":result,"native_gui":"not-run",
            "original_server_npc_ai":"unknown"}

def c43_body(first,object_key,last):
    if any(type(x) is not int for x in (first,object_key,last)):
        raise ValueError("integer fields required")
    if not(0<=first<=255 and 0<=object_key<=0xffffffff and 0<=last<=255):
        raise ValueError("C43 value out of range")
    return struct.pack(">BIB",first,object_key,last)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("exe")
    print(json.dumps(verify_exe(p.parse_args().exe),indent=2))
