#!/usr/bin/env python3
"""A013: Asgard economy native packet anchors, synthetic codecs, designed ledger."""
import hashlib,struct,sqlite3,unittest
from pathlib import Path
SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
SIG={
"C4A-ctor":(0x572559,"6a4a"),"C4A-writer":(0x5725f3,"0fb64618"),"C4A-range":(0x572601,"83f805"),"C4A-u32":(0x572611,"8b4e1c"),
"C39-ctor":(0x5737c9,"6a39"),"C39-u8":(0x573863,"0fb64619"),"C39-u32":(0x57386d,"8b4e1c"),"C39-u16":(0x573878,"0fb75620"),
"C17-ctor":(0x577109,"6a17"),"C17-writer":(0x5763a3,"0fb64618"),"C17-range":(0x5763b1,"3d82000000"),"C17-count":(0x5763e7,"0fb6d0"),
"S42-ctor":(0x57e939,"6a42"),"S42-range":(0x57ea10,"83f805"),"S2F-ctor":(0x581ba9,"6a2f"),"S2F-range":(0x581d10,"83f809"),
"S6E-ctor":(0x588169,"6a6e"),"S6E-range":(0x588365,"83f803")}
RTTI=("CExchangePacket","CMerchantPacket","CTradePacket","SExchangePacket","SMerchantPacket","STradePacket")
def native(path):
 b=Path(path).read_bytes()
 if hashlib.sha256(b).hexdigest()!=SHA:raise ValueError("original exe sha")
 for name,(va,h) in SIG.items():
  expected=bytes.fromhex(h)
  if b[va-0x400000:va-0x400000+len(expected)]!=expected:raise ValueError(name)
 for name in RTTI:
  if b.count((".?AV"+name+"@@").encode())!=1:raise ValueError("RTTI "+name)
 return len(SIG)
def bounded(value,n):
 if type(value)!=int or not 0<=value<1<<(8*n):raise ValueError("u%d"%(n*8))
 return value
def exchange(subtype,number,extra=()):
 bounded(subtype,1);bounded(number,4)
 modes={0:0,1:2,2:3,3:1,4:0,5:0}
 if subtype not in modes or len(extra)!=modes[subtype]:raise ValueError("C4A variant")
 if subtype==3:return struct.pack(">BII",subtype,number,bounded(extra[0],4))
 return struct.pack(">BI",subtype,number)+bytes(bounded(n,1) for n in extra)
def merchant(f0,ref,f2):
 return struct.pack(">BIH",bounded(f0,1),bounded(ref,4),bounded(f2,2))
def trade(kind,entries=(),value=None):
 bounded(kind,1)
 if kind==128:
  if value is None or entries:raise ValueError("C17 type128")
  return struct.pack(">BI",kind,bounded(value,4))
 if value is not None:raise ValueError("unexpected field")
 if kind==0:
  if len(entries)>255:raise ValueError("count")
  return bytes((kind,len(entries)))+b"".join(struct.pack(">BBIH",bounded(a,1),bounded(b,1),bounded(c,4),bounded(d,2)) for a,b,c,d in entries)
 if kind in (3,130):
  if len(entries)>255:raise ValueError("count")
  return bytes((kind,len(entries)))+b"".join(struct.pack(">BH",bounded(a,1),bounded(b,2)) for a,b in entries)
 if entries:raise ValueError("unverified variant")
 return bytes((kind,))
class Ledger:
 """Server-designed atomic money simulation: NOT native Asgard economy semantics."""
 def __init__(self):
  self.c=sqlite3.connect(":memory:")
  self.c.execute("CREATE TABLE wallet(id INTEGER PRIMARY KEY,amount INTEGER CHECK(amount>=0 AND amount<=4294967295))")
  self.c.execute("CREATE TABLE receipt(token TEXT PRIMARY KEY,src INTEGER,dst INTEGER,amount INTEGER,status TEXT)")
 def put(self,i,n):
  bounded(n,4);self.c.execute("INSERT INTO wallet VALUES(?,?)",(i,n));self.c.commit()
 def amount(self,i):return self.c.execute("SELECT amount FROM wallet WHERE id=?",(i,)).fetchone()[0]
 def send(self,t,src,dst,n):
  if not t or src==dst or n<=0:raise ValueError("intent")
  bounded(n,4)
  with self.c:
   old=self.c.execute("SELECT src,dst,amount,status FROM receipt WHERE token=?",(t,)).fetchone()
   if old:
    if old[:3]!=(src,dst,n):raise ValueError("token reuse")
    return old[3]
   a,b=self.amount(src),self.amount(dst)
   result="committed" if a>=n and b+n<=0xffffffff else "rejected"
   if result=="committed":
    self.c.execute("UPDATE wallet SET amount=? WHERE id=?",(a-n,src))
    self.c.execute("UPDATE wallet SET amount=? WHERE id=?",(b+n,dst))
   self.c.execute("INSERT INTO receipt VALUES(?,?,?,?,?)",(t,src,dst,n,result))
   return result
class Tests(unittest.TestCase):
 def test_01_original(self):
  p=Path("/mnt/data/Asgard.exe")
  if not p.exists():self.skipTest("original not mounted")
  self.assertEqual(native(p),18)
 def test_02_c4a(self):
  self.assertEqual(exchange(0,0x11223344).hex(),"0011223344")
  self.assertEqual(exchange(1,0x11223344,(2,3)).hex(),"01112233440203")
  self.assertEqual(exchange(2,0x11223344,(2,3,4)).hex(),"0211223344020304")
  self.assertEqual(exchange(3,0x11223344,(0x55667788,)).hex(),"031122334455667788")
  self.assertEqual(exchange(4,1).hex(),"0400000001")
  self.assertEqual(exchange(5,1).hex(),"0500000001")
 def test_03_c39(self):self.assertEqual(merchant(1,0x11223344,0x5566).hex(),"01112233445566")
 def test_04_c17(self):
  self.assertEqual(trade(0,[(1,2,0x11223344,0x5566)]).hex(),"00010102112233445566")
  self.assertEqual(trade(3,[(2,0x1234)]).hex(),"0301021234")
  self.assertEqual(trade(128,value=0x11223344).hex(),"8011223344")
  self.assertEqual(trade(130,[(2,0x1234)]).hex(),"8201021234")
 def test_05_negative(self):
  for f in (lambda:exchange(6,1),lambda:exchange(1,1,(1,)),lambda:merchant(-1,1,1),lambda:trade(0,[(1,2,3,65536)]),lambda:trade(128),lambda:trade(3,[(1,2)]*256)):
   with self.assertRaises(ValueError):f()
 def test_06_once(self):
  l=Ledger();l.put(1,100);l.put(2,8)
  self.assertEqual(l.send("a",1,2,20),"committed");self.assertEqual(l.send("a",1,2,20),"committed")
  self.assertEqual((l.amount(1),l.amount(2)),(80,28))
 def test_07_insufficient_overflow(self):
  l=Ledger();l.put(1,8);l.put(2,0xffffffff)
  self.assertEqual(l.send("a",1,2,9),"rejected");self.assertEqual(l.send("b",1,2,1),"rejected")
  self.assertEqual((l.amount(1),l.amount(2)),(8,0xffffffff))
 def test_08_token(self):
  l=Ledger();l.put(1,10);l.put(2,0);l.send("a",1,2,2)
  with self.assertRaises(ValueError):l.send("a",1,2,3)
 def test_09_cancel(self):
  l=Ledger();l.put(1,10);l.put(2,0)
  self.assertEqual((l.amount(1),l.amount(2)),(10,0))
 def test_10_range(self):
  with self.assertRaises(ValueError):Ledger().put(1,0x100000000)
if __name__=="__main__":unittest.main(verbosity=2)
