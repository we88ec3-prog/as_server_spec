#!/usr/bin/env python3
"""A032 original EXE SHA locked S14(1)->C35 producer and mapdata getter proof.

Original x86 PE static evidence only. This probe cannot substitute for network capture.
"""
import argparse,hashlib,json,struct
from pathlib import Path
EXE_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
EDGES={
 0x4f23f5:(0xe8,0x5733e0),  # construct C35
 0x4f240e:(0xe8,0x4b4850),  # header cached map object +4
 0x4f241d:(0xe8,0x4b4890),  # mapdata cached CRC
 0x4f2428:(0xe8,0x5788a0),  # enqueue C2S
 0x573498:(0xe8,0x45ab40),  # writer BE u16 first
 0x5734a4:(0xe8,0x45ab40),  # writer BE u16 second
 0x4b4896:(0xe9,0x4b3650),  # cached mapdata crc getter tail jump
}
ANCHORS={
 0x4f2319:"0fb640244856",
 0x4f231f:"0f84a6000000",
 0x4f23f3:"8bc8",
 0x4f2408:"8b0dd8d06600",
 0x4f2413:"66894624",
 0x4f2422:"8bce",
 0x4f2424:"66894626",
 0x5733f9:"6a35",
 0x573493:"0fb74618",
 0x57349d:"0fb74e1a",
 0x4b4850:"8b81b4000000",
 0x4b4856:"668b4004",
 0x4b4890:"8b89b4000000",
 0x4b3650:"568bf1",
 0x43e0a0:"0fb74c2408",
}
class NativeMismatch(ValueError):pass
def reader(data):
 if data[:2]!=b"MZ":raise NativeMismatch("invalid DOS header")
 p=struct.unpack_from("<I",data,0x3c)[0]
 if data[p:p+4]!=b"PE\x00\x00":raise NativeMismatch("invalid PE header")
 o=p+24
 if struct.unpack_from("<H",data,o)[0]!=0x10b:raise NativeMismatch("not PE32")
 base=struct.unpack_from("<I",data,o+28)[0]
 ns=struct.unpack_from("<H",data,p+6)[0]
 s=o+struct.unpack_from("<H",data,p+20)[0]
 areas=[]
 for i in range(ns):
  vs,rva,rawsize,raw=struct.unpack_from("<IIII",data,s+40*i+8)
  areas.append((base+rva,min(vs,rawsize),raw))
 def read(va,n):
  for start,sz,raw in areas:
   if start<=va and va+n<=start+sz:
    return data[raw+va-start:raw+va-start+n]
  raise NativeMismatch(f"unmapped VA {va:x}")
 return read
def verify(path):
 exe=Path(path).read_bytes()
 if hashlib.sha256(exe).hexdigest()!=EXE_SHA:raise NativeMismatch("wrong original Client SHA")
 rd=reader(exe)
 for at,(op,dest) in EDGES.items():
  ins=rd(at,5)
  if ins[0]!=op or at+5+struct.unpack_from("<i",ins,1)[0]!=dest:
   raise NativeMismatch(f"unexpected S14/C35 call or jmp at {at:x}")
 for at,signature in ANCHORS.items():
  b=bytes.fromhex(signature)
  if rd(at,len(b))!=b:raise NativeMismatch(f"unexpected x86 bytes at {at:x}")
 return {
  "original_sha256":EXE_SHA, "native_edges":len(EDGES),
  "native_anchors":len(ANCHORS),"incoming_packet":"S14 subtype1 (read packet+0x24)",
  "client_outgoing_opcode":"C35","send_queue":"0x5788a0",
  "client_C35_body":"two BEu16: current MapData header word + cached structured CRC",
  "map_ref_encoded_inside_C35":False,
  "native_windows_gui_and_tcp_capture":"not-run",
 }
def decode_c35(body):
 if type(body) is not bytes or len(body)!=4:raise ValueError("C35 must have exact 4 decoded bytes")
 return struct.unpack(">HH",body)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("exe");a=p.parse_args()
 print(json.dumps(verify(a.exe),indent=2))
