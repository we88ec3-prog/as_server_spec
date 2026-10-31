#!/usr/bin/env python3
"""A028: original Client conditional Region3 automatic C03, static-only."""
import hashlib,json,struct
from pathlib import Path
SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
CALL_EDGES={
 0x4b20c0:0x498000,0x4b2109:0x4a9380,
 0x4a95e9:0x4a87b0,0x4a9617:0x4a8950,
 0x4a8a30:0x4a7d10,0x4a7d6e:0x573060,
 0x4a7dde:0x5788a0,
}
ANCHORS={
 0x4b1f46:"837e4c1d",0x4b205a:"e841680c00",0x4b205f:"c7464c1e000000",
 0x4b206b:"8b866c020000",0x4b20c5:"83f803",0x4b2109:"e87272ffff",
 0x4a9380:"6aff68935e5d00",0x4a93b5:"c706bc9b6000",
 0x4a9485:"83ff04",0x4a948e:"ff24bd54964a00",
 0x4a9495:"a10cd16600",0x4a9508:"8b442438",0x4a9510:"8b0d00d16600",
 0x4a95ee:"a10cd16600",0x4a95f3:"6683780400",
 0x4a95fa:"6683b80402000000",0x4a9604:"6a11",0x4a9606:"ff154c145f00",
 0x4a960c:"6685c0",0x4a960f:"7c0b",0x4a9611:"6a00",0x4a9613:"6a04",
 0x4a9617:"e834f3ffff",0x4a8977:"8b842418020000",0x4a897e:"83c0fc",
 0x4a8981:"83f809",0x4a898f:"ff2485348d4a00",
 0x4a8996:"6acc",0x4a8a29:"6a00",0x4a8a30:"e8dbf2ffff",
 0x4a7d7d:"6a0c",0x4a7da2:"0f95c1",0x4a7dde:"e8bd0a0d00",
 0x4a7d85:"e836cff8ff",0x573110:"568bf1578d7e18",
 0x573129:"8dbe18020000",0x573141:"0fb6862a020000",
 0x573149:"8bce",0x4a889b:"6a01",
 0x573079:"6a03",0x4a8890:"8b44240485c0",0x4a889d:"e86ef4ffff",
}
REGION_CTOR_TARGETS=(0x4a9495,0x4a9549,0x4a9495,0x4a9508,0x4a9495)
PANE_EVENT_TARGETS=(0x4a8996,0x4a8a3a,0x4a8a75,0x4a8bcc,
 0x4a8bcc,0x4a8bcc,0x4a8bcc,0x4a8bcc,0x4a8a81,0x4a8d27)
class NativeMismatch(ValueError):pass
def reader(data):
 if data[:2]!=b"MZ":raise NativeMismatch("not MZ")
 p=struct.unpack_from("<I",data,0x3c)[0]
 if data[p:p+4]!=b"PE\0\0":raise NativeMismatch("not PE")
 opt=p+24
 if struct.unpack_from("<H",data,opt)[0]!=0x10b:raise NativeMismatch("not PE32")
 base=struct.unpack_from("<I",data,opt+28)[0]
 count=struct.unpack_from("<H",data,p+6)[0]
 sec=opt+struct.unpack_from("<H",data,p+20)[0];ranges=[]
 for i in range(count):
  vs,rva,rs,off=struct.unpack_from("<IIII",data,sec+i*40+8)
  ranges.append((base+rva,min(vs,rs),off))
 def read(va,length):
  for start,size,off in ranges:
   if start<=va and va+length<=start+size:
    return data[off+va-start:off+va-start+length]
  raise NativeMismatch("unmapped VA "+hex(va))
 return read
def verify(path):
 data=Path(path).read_bytes()
 if hashlib.sha256(data).hexdigest()!=SHA:raise NativeMismatch("different EXE SHA")
 rd=reader(data)
 for va,target in CALL_EDGES.items():
  b=rd(va,5)
  if b[0]!=0xe8 or va+5+struct.unpack_from("<i",b,1)[0]!=target:
   raise NativeMismatch("wrong native call "+hex(va))
 for va,h in ANCHORS.items():
  x=bytes.fromhex(h)
  if rd(va,len(x))!=x:raise NativeMismatch("wrong instruction "+hex(va))
 a=struct.unpack("<5I",rd(0x4a9654,20))
 b=struct.unpack("<10I",rd(0x4a8d34,40))
 if a!=REGION_CTOR_TARGETS or b!=PANE_EVENT_TARGETS:raise NativeMismatch("jump table changed")
 col=struct.unpack("<I",rd(0x609bbc-4,4))[0]
 desc=struct.unpack("<I",rd(col+12,4))[0]
 if (col,desc)!=(0x625970,0x6665d8) or not rd(desc+8,40).startswith(b".?AVLoginDialogPane@@\0"):
  raise NativeMismatch("not LoginDialogPane")
 # 0x5f144c USER32 GetAsyncKeyState according to original PE import table.
 return {"sha256":SHA,"call_edges":len(CALL_EDGES),"byte_anchors":len(ANCHORS),
  "region_ctor_cases":len(a),"event_cases":len(b),
  "region3_constructor_va":hex(a[3]),"event_argument_4_target":hex(b[0]),
  "conditional_C03_sender":"0x4a7d10","auto_C03_decoded_body":"string8, string8, u8(0)",
  "auto_send_trigger":"two cached wide chars nonzero and GetAsyncKeyState(VK_CONTROL) nonnegative",
  "native_gui":"not-run","S03_C10_World_after_auto_C03":"unverified"}
def conditional_constructor_auto_c03(region,cached_first,cached_second,control_async_state):
 """Synthetic decision, not proof of valid login credentials or a live World."""
 if type(region)!=int or not 0<=region<=4:raise ValueError("region")
 if type(control_async_state)!=int or not -32768<=control_async_state<=32767:
  raise ValueError("signed SHORT GetAsyncKeyState expected")
 return bool(cached_first and cached_second) and control_async_state>=0 and region==3
def arg4_event_path(arg):
 """0x4a8950 dispatches (arg-4) through 0x4a8d34; case4 sends C03."""
 if type(arg)!=int:raise ValueError("native event argument must int")
 return PANE_EVENT_TARGETS[arg-4] if 4<=arg<=13 else None
if __name__=="__main__":
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument("exe");ns=ap.parse_args()
 print(json.dumps(verify(ns.exe),indent=2))
