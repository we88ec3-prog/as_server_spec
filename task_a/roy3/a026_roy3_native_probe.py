#!/usr/bin/env python3
"""A-026 roy3 native C39/S2F, Born and Basic provenance. Offline static only."""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from xml.etree import ElementTree as ET

EXE_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
BORN_SHA="992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98"
BASIC_SHA="0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96"
C39_TABLE=(0x573896,0x573896,0x5738ae,0x573896,0x5738cb,0x573896,0x573896,0x5738da,0x5738e9)
S2F_TABLE=(0x581d22,0x581db2,0x58206f,0x581e52,0x581e79,0x58206f,0x581f4e,0x581fe0,0x58206f,0x58206f)
EDGES={0x573868:0x45ab00,0x573873:0x45ac40,0x57387f:0x45ab40,0x5738a6:0x45b1b0,0x5738be:0x45b1b0,
       0x5738d2:0x45ab00,0x5738e1:0x45ab00,0x5738f0:0x45ab00,0x581ca3:0x45adb0,0x581cc0:0x45adb0,
       0x581cca:0x45aeb0,0x581cd4:0x45adb0,0x581cde:0x45ade0,0x581ce9:0x45adb0}
ANCHORS={0x5737c9:"6a39",0x573863:"0fb64619",0x57386d:"8b4e1c",0x573878:"0fb75620",
         0x573884:"0fb646184883f808",0x57388f:"ff2485f8385700",0x573896:"8d7e22",
         0x5738ae:"8d7e22",0x5738c3:"8dbe22020000",0x5738cb:"0fb64622",
         0x5738da:"0fb64e22",0x5738e9:"0fb65622",0x581ba9:"6a2f",
         0x581ca3:"e80891edff",0x581cab:"0fb6c0",0x581d10:"83f809",
         0x581d1b:"ff248584205800"}

def hash_checked(path, expected):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=expected:raise ValueError("different original resource: "+str(path))
    return data

def pe_reader(exe):
    if exe[:2]!=b"MZ":raise ValueError("not MZ")
    pe=struct.unpack_from("<I",exe,0x3c)[0]
    if exe[pe:pe+4]!=b"PE\x00\x00":raise ValueError("not PE")
    n=struct.unpack_from("<H",exe,pe+6)[0]
    opt=pe+24
    if struct.unpack_from("<H",exe,opt)[0]!=0x10b:raise ValueError("not PE32")
    base=struct.unpack_from("<I",exe,opt+28)[0]
    sec=opt+struct.unpack_from("<H",exe,pe+20)[0]
    regions=[]
    for i in range(n):
        at=sec+40*i
        vs,rva,rs,raw=struct.unpack_from("<IIII",exe,at+8)
        regions.append((base+rva,min(vs,rs),raw))
    def read(va,length):
        for start,size,raw in regions:
            if start<=va and va+length<=start+size:
                return exe[raw+va-start:raw+va-start+length]
        raise ValueError("unmapped PE VA "+hex(va))
    return read

def verify_exe(path):
    read=pe_reader(hash_checked(path,EXE_SHA))
    for va,target in EDGES.items():
        op,disp=struct.unpack("<Bi",read(va,5))
        if op!=0xe8 or va+5+disp!=target:raise ValueError("native call mismatch "+hex(va))
    for va,hex_pattern in ANCHORS.items():
        b=bytes.fromhex(hex_pattern)
        if read(va,len(b))!=b:raise ValueError("native code mismatch "+hex(va))
    for va,table in ((0x5738f8,C39_TABLE),(0x582084,S2F_TABLE)):
        got=struct.unpack("<"+"I"*len(table),read(va,len(table)*4))
        if got!=table:raise ValueError("native switch table mismatch "+hex(va))
    return {"exe_sha256":EXE_SHA,"C39_opcode":0x39,"S2F_opcode":0x2f,
            "call_edges":len(EDGES),"byte_anchors":len(ANCHORS),
            "C39_internal_selectors":len(C39_TABLE),"S2F_receive_cases":len(S2F_TABLE),
            "native_client_e2e":"not-run"}

def c39_fields(selector):
    """Selector lives in Client packet+0x18; it is NOT serialized as a leading u8."""
    if not 1<=selector<=9:raise ValueError("selector not in 1..9")
    if selector==3:return ("string8@+0x22","string8@+0x222")
    if selector in (1,2,4,6,7):return ("string8@+0x22",)
    return ("u8@+0x22",)

def synthetic_c39_body(selector,first_u8,target_be_u32,aux_be_u16,extra,extra2=None):
    """Decoded-body fixture ONLY: u8/u32BE/u16BE; string8 uses caller-provided bytes."""
    c39_fields(selector)
    if not 0<=first_u8<=255 or not 0<=target_be_u32<=0xffffffff or not 0<=aux_be_u16<=65535:
        raise ValueError("invalid fixed width")
    data=struct.pack(">BIH",first_u8,target_be_u32,aux_be_u16)
    def put_string(value):
        if type(value) is not bytes or len(value)>255:raise ValueError("invalid string8")
        return bytes((len(value),))+value
    if selector==3:
        if extra2 is None:raise ValueError("missing second string")
        return data+put_string(extra)+put_string(extra2)
    if extra2 is not None:raise ValueError("extra field invalid")
    if selector in (1,2,4,6,7):return data+put_string(extra)
    if type(extra) is not int or not 0<=extra<=255:raise ValueError("invalid extra u8")
    return data+bytes((extra,))

def dat_members(raw):
    if len(raw)<76:raise ValueError("short archive")
    n=struct.unpack_from("<I",raw)[0]
    if n<2 or n>100000 or 4+n*36>len(raw):raise ValueError("bad DAT count")
    offsets=[struct.unpack_from("<I",raw,4+i*36)[0] for i in range(n)]
    if offsets[0]!=4+n*36 or offsets[-1]!=len(raw) or any(a>=b for a,b in zip(offsets,offsets[1:])):
        raise ValueError("invalid DAT offsets")
    result={}
    for i in range(n-1):
        name=raw[8+36*i:40+36*i].split(b"\x00")[0].decode("ascii")
        if name in result:raise ValueError("duplicate member")
        result[name]=(offsets[i],offsets[i+1]-offsets[i])
    return result

def verify_basic(path):
    members=dat_members(hash_checked(path,BASIC_SHA))
    expected=("AlertButton.ypf","AlertFrame.ypf","QuestImage.ypf")
    if any(n not in members for n in expected):raise ValueError("missing Basic UI resource")
    return {"basic_sha256":BASIC_SHA,"members":len(members),
            "verified_ui_members":{n:{"offset":members[n][0],"size":members[n][1]} for n in expected}}

def verify_born(path):
    raw=zlib.decompress(hash_checked(path,BORN_SHA))
    version,units=struct.unpack_from(">HI",raw)
    if version!=1 or len(raw)!=6+2*units:raise ValueError("invalid Born wrapper")
    root=ET.fromstring(raw[6:].decode("utf-16le"))
    funcs=root.findall("function")
    if len(funcs)!=1 or funcs[0].attrib.get("name")!="Main":raise ValueError("not Born.Main")
    body=funcs[0].text or ""
    if not all(x in body for x in ("(31,29)","PaperDialog_Create","client.CreateArray","page.Insert")):
        raise ValueError("Born does not match observed guide")
    return {"born_sha256":BORN_SHA,"entry":"Main","waypoint":[31,29],
            "direct_SendReply":("SendReply" in body),
            "direct_reward_or_finish":any(x in body for x in ("GiveItem","RewardGrant","quest.Complete")),
            "original_exit_map":"unknown"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--exe",required=True);p.add_argument("--born",required=True);p.add_argument("--basic",required=True)
    a=p.parse_args()
    print(json.dumps({"exe":verify_exe(a.exe),"born":verify_born(a.born),
                      "basic":verify_basic(a.basic),
                      "C39_shapes":{i:c39_fields(i) for i in range(1,10)}},
                     ensure_ascii=False,indent=2))
