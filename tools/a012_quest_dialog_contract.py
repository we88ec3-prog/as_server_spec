#!/usr/bin/env python3
"""A-012: SHA-locked Client Script reply, original Born resource and SERVER-DESIGNED session checks.
Original Server quest rules and native GUI E2E are NOT derived from this script.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET
import zlib

CLIENT_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
BORN_SHA="992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98"
BORN_CRC950=0x1d87b0c0
ANCHORS={
 "C6C opcode":(0x575159,"6a6c"),
 "C6C subtype writer":(0x575213,"0fb6461850"),
 "C6C subtype bound":(0x575221,"83f804"),
 "C6C jump table":(0x57522a,"ff2485fc525700"),
 "C6C reply context":(0x57524e,"8b861c020000"),
 "C6C reply pair count":(0x57525c,"0fb78e20020000"),
 "C6C reply array":(0x575280,"8bbe24020000"),
 "C6C reply value offset":(0x575292,"6aff81c700020000"),
 "C6C cleanup2 writer":(0x5752bf,"8bcee8ea5eeeff"),
 "C6C dispose4 writer":(0x5752d6,"6aff8d561a"),
 "SendReply dispatch":(0x526626,"6870df6000"),
 "SendReply call":(0x526652,"e89943ffff"),
 "Dispose dispatch":(0x526873,"68a8325f00"),
 "Dispose creates type4":(0x5268c6,"c6462404"),
 "replied flag check":(0x519479,"8b873c02000085c0"),
 "no-reply creates type2":(0x5194ce,"c6462402"),
 "SendReply creates type1":(0x51aa5c,"c6462401"),
 "SendReply copies context":(0x51aa70,"8b9724020000899628020000"),
 "SendReply sets replied":(0x51ab33,"c7873c02000001000000"),
 "S44 opcode":(0x5862f9,"6a44"),
}
def verify_client(path):
 data=Path(path).read_bytes()
 if hashlib.sha256(data).hexdigest()!=CLIENT_SHA:raise ValueError("Client SHA mismatch")
 for name,(va,h) in ANCHORS.items():
  p=bytes.fromhex(h)
  if data[va-0x400000:va-0x400000+len(p)]!=p:raise ValueError("native signature: "+name)
 return len(ANCHORS)
def verify_born(path):
 raw=Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=BORN_SHA:raise ValueError("Born SHA mismatch")
 buf=zlib.decompress(raw)
 if len(buf)<6:raise ValueError("Born header")
 version,n=struct.unpack_from(">HI",buf)
 if version!=1 or len(buf)!=6+2*n:raise ValueError("Born BE wrapper")
 xml=buf[6:].decode("utf-16le")
 if zlib.crc32(xml.encode("cp950"))!=BORN_CRC950:raise ValueError("Born text CRC950")
 funcs={f.get("name"): f.text or "" for f in ET.fromstring(xml).findall("function")}
 if set(funcs)!={"Main"}:raise ValueError("Born function list")
 return funcs["Main"]
def string8(s):
 if not isinstance(s,str) or "\0" in s:raise ValueError("invalid string8")
 b=s.encode("cp950")
 if len(b)>255:raise ValueError("encoded string8 too long")
 return bytes((len(b),))+b
def reply_body(name,context,pairs):
 if type(context)!=int or not 0<=context<=0xffffffff:raise ValueError("context")
 if not isinstance(pairs,list) or len(pairs)>32:raise ValueError("designed maximum pair count")
 out=bytearray(b"\x01"+string8(name)+struct.pack(">IH",context,len(pairs)))
 for pair in pairs:
  if not isinstance(pair,tuple) or len(pair)!=2:raise ValueError("key/value pair")
  out+=string8(pair[0])+string8(pair[1])
 return bytes(out)
def lifecycle_body(kind,name="",context=None):
 if kind==3:
  if name or context is not None:raise ValueError("type3 no payload")
  return b"\x03"
 if kind not in (0,2,4):raise ValueError("unsupported kind")
 out=bytes((kind,))+string8(name)
 if kind in (2,4):
  if type(context)!=int or not 0<=context<=0xffffffff:raise ValueError("context")
  out+=struct.pack(">I",context)
 elif context is not None:raise ValueError("type0 no context")
 return out
def parse_client_body(body):
 """Strict server-design decoder for native C6C wire fields; CP950 fixture, not all regional clients."""
 if not body:raise ValueError("empty")
 typ=body[0]
 if typ not in range(5):raise ValueError("subtype")
 if typ==3:
  if len(body)!=1:raise ValueError("trailing bytes")
  return {"type":3}
 pos=1
 def getstring():
  nonlocal pos
  if pos>=len(body):raise ValueError("short length")
  n=body[pos];pos+=1
  if pos+n>len(body):raise ValueError("short data")
  try:v=body[pos:pos+n].decode("cp950")
  except UnicodeDecodeError as e:raise ValueError("invalid cp950") from e
  pos+=n
  return v
 name=getstring();result={"type":typ,"name":name}
 if typ==0:
  if pos!=len(body):raise ValueError("trailing")
  return result
 if pos+4>len(body):raise ValueError("short context")
 result["context"]=struct.unpack_from(">I",body,pos)[0];pos+=4
 if typ==1:
  if pos+2>len(body):raise ValueError("short pair count")
  count=struct.unpack_from(">H",body,pos)[0];pos+=2
  if count>32:raise ValueError("designed pair limit")
  result["pairs"]=[(getstring(),getstring()) for _ in range(count)]
 if pos!=len(body):raise ValueError("trailing")
 return result
class DialogLedger:
 """SERVER-DESIGNED no-grant state fence; not original game quest policy."""
 def __init__(self,session,name,context,allowed_keys=frozenset()):
  self.session,self.name,self.context=session,name,context
  self.allowed_keys=frozenset(allowed_keys)
  self.replied=False;self.closed=False;self.events=[]
 def accept(self,session,body):
  e=parse_client_body(body)
  if session!=self.session or e.get("name")!=self.name or e.get("context")!=self.context:
   raise ValueError("stale/mismatched dialog")
  if e["type"] not in (1,2,4):raise ValueError("not a dialog-result subtype")
  if e["type"]==1:
   keys=[p[0] for p in e["pairs"]]
   if self.closed or len(keys)!=len(set(keys)) or any(k not in self.allowed_keys for k in keys):
    raise ValueError("duplicate/unknown key or closed run")
   if self.replied:return "replay"
   self.replied=True
   self.events.append(("client-reply-observed",tuple(e["pairs"])))
   return "reply-observed-not-authoritative"
  if self.closed:return "replay"
  if e["type"]==4:
   self.events.append(("dispose-observed",None))
   return "dispose-observed"
  self.closed=True
  self.events.append(("no-reply-cleanup",None))
  return "closed-no-grant"
class Tests(unittest.TestCase):
 def test_01_native(self):
  p=Path("/mnt/data/Asgard.exe")
  if not p.exists():self.skipTest("Asgard.exe not mounted")
  self.assertEqual(verify_client(p),20)
 def test_02_born(self):
  p=Path("/mnt/data/Born.dat")
  if not p.exists():self.skipTest("Born.dat not mounted")
  main=verify_born(p)
  self.assertIn("PaperDialog_Create",main)
  self.assertIn("(31,29)",main)
  self.assertNotIn("SendReply",main)
 def test_03_reply_fixture(self):
  self.assertEqual(reply_body("nNewJoin01",0x11223344,[("STATE","ACCEPT")]).hex(),
      "010a6e4e65774a6f696e303111223344000105535441544506414343455054")
 def test_04_born_close(self):
  self.assertEqual(lifecycle_body(4,"Born",0x11223344).hex(),"0404426f726e11223344")
  self.assertEqual(lifecycle_body(2,"Born",0x11223344).hex(),"0204426f726e11223344")
 def test_05_type0_type3(self):
  self.assertEqual(parse_client_body(lifecycle_body(0,"Born")),{"type":0,"name":"Born"})
  self.assertEqual(parse_client_body(lifecycle_body(3)),{"type":3})
 def test_06_roundtrip(self):
  for pairs in ([],[("STATE","ACCEPT")],[("選項","拒絕"),("X","2")]):
   self.assertEqual(parse_client_body(reply_body("nNewJoin01",9,pairs))["pairs"],pairs)
 def test_07_truncation(self):
  b=reply_body("Born",0x11223344,[("STATE","ACCEPT")])
  for i in range(len(b)):
   with self.subTest(offset=i),self.assertRaises(ValueError):parse_client_body(b[:i])
 def test_08_invalid_tail_and_type(self):
  for b in (b"",b"\x05",b"\x03\x00",lifecycle_body(2,"Born",3)+b"x"):
   with self.assertRaises(ValueError):parse_client_body(b)
 def test_09_widths(self):
  fns=(lambda:reply_body("Born",-1,[]),lambda:reply_body("Born",0,[("a","b")]*33),
       lambda:reply_body("太"*128,1,[]),lambda:lifecycle_body(2,"Born",None))
  for f in fns:
   with self.assertRaises(ValueError):f()
 def test_10_close_no_reward(self):
  l=DialogLedger("s1","Born",0x11223344)
  self.assertEqual(l.accept("s1",lifecycle_body(4,"Born",0x11223344)),"dispose-observed")
  self.assertEqual(l.accept("s1",lifecycle_body(2,"Born",0x11223344)),"closed-no-grant")
  self.assertEqual(l.accept("s1",lifecycle_body(2,"Born",0x11223344)),"replay")
  self.assertEqual(len(l.events),2)
 def test_11_choice_no_reward(self):
  l=DialogLedger("s1","nNewJoin01",5,{"STATE"})
  b=reply_body("nNewJoin01",5,[("STATE","ACCEPT")])
  self.assertEqual(l.accept("s1",b),"reply-observed-not-authoritative")
  self.assertEqual(l.accept("s1",b),"replay")
  self.assertEqual(l.accept("s1",lifecycle_body(4,"nNewJoin01",5)),"dispose-observed")
  self.assertEqual(len(l.events),2)
 def test_12_stale(self):
  l=DialogLedger("s1","Born",5)
  for session,body in (("s2",lifecycle_body(4,"Born",5)),("s1",lifecycle_body(4,"Born",6)),("s1",lifecycle_body(4,"other",5))):
   with self.assertRaises(ValueError):l.accept(session,body)
 def test_13_duplicate_key(self):
  l=DialogLedger("s1","nNewJoin01",5,{"STATE"})
  with self.assertRaises(ValueError):l.accept("s1",reply_body("nNewJoin01",5,[("STATE","YES"),("STATE","NO")]))
 def test_14_unknown_key(self):
  l=DialogLedger("s1","nNewJoin01",5,{"STATE"})
  with self.assertRaises(ValueError):l.accept("s1",reply_body("nNewJoin01",5,[("REWARD","999")]))
if __name__=="__main__":unittest.main(verbosity=2)
