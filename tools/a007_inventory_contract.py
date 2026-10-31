#!/usr/bin/env python3
"""A-007: BIN-derived C1C/C1E/S10/S38 fixtures, DESIGNED persistent item ledger.
No original Server business semantics or native GUI testing claimed.
"""
import hashlib,sqlite3,struct,tempfile,unittest
from pathlib import Path
SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
SIG={
"C1C opcode":(0x577769,"6a1c"),"C1C writer 4u8":(0x577800,"568bf10fb6461850"),
"C1C dispatch":(0x577831,"0fb6461b4883f808"),
"C1E opcode":(0x577f79,"6a1e"),"C1E writer":(0x578010,"0fb6411850"),
"C08 opcode":(0x571f59,"6a08"),"C08 writer":(0x571ff0,"568bf10fb6461850"),
"C0C writer":(0x574af0,"8b411850"),
"S10 opcode":(0x585b99,"6a10"),"S10 parser":(0x585c30,"568bf1e87851edff"),
"S38 opcode":(0x585a29,"6a38"),"S38 parser":(0x585ac0,"568bf1e8e852edff"),
"S0F parser":(0x57a440,"e86b09eeff"),"S0F mode":(0x57a4f8,"e8b308eeff84c0"),
"S37 flags":(0x5798c8,"e8e314eeff"),
}
def bin_check(path):
 b=Path(path).read_bytes()
 if hashlib.sha256(b).hexdigest()!=SHA:raise ValueError("Asgard.exe release mismatch")
 for name,(va,h) in SIG.items():
  v=bytes.fromhex(h)
  if b[va-0x400000:va-0x400000+len(v)]!=v:raise ValueError(name)
 return len(SIG)
LENGTH={2:4,3:8,4:6,5:0,6:4,7:2,8:2,9:4}
def c1c(kind,slot,flag,use_kind,tail=b""):
 if not all(type(v)==int and 0<=v<=255 for v in (kind,slot,flag,use_kind)):raise ValueError("u8")
 if use_kind==1:
  if not tail or len(tail)!=tail[0]+1:raise ValueError("string8")
 elif use_kind in LENGTH:
  if len(tail)!=LENGTH[use_kind]:raise ValueError("tail length")
 else:raise ValueError("unknown use_kind")
 return bytes([kind,slot,flag,use_kind])+tail
def s10(b):
 if len(b)!=3:raise ValueError("S10 length")
 return tuple(b)
def s38(b):
 if len(b)!=2:raise ValueError("S38 length")
 return (b[0],b[1]==1)
class Store:
 """Designed Server reference model, not original game rules."""
 def __init__(self,path,bag_cap=3,equip_cap=8):
  self.db=sqlite3.connect(path,isolation_level=None)
  self.bag_cap,self.equip_cap=bag_cap,equip_cap
  self.db.executescript("""
  CREATE TABLE IF NOT EXISTS item(iid TEXT PRIMARY KEY,owner TEXT,loc TEXT,slot INTEGER,template TEXT,qty INTEGER CHECK(qty>0),rev INTEGER);
  CREATE UNIQUE INDEX IF NOT EXISTS unique_slot ON item(owner,loc,slot);
  CREATE TABLE IF NOT EXISTS ops(id TEXT PRIMARY KEY,owner TEXT,kind TEXT,digest TEXT);
  CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY,result TEXT);
  """)
 def add(self,iid,owner,slot,template="coat",qty=1):
  if type(qty)!=int or not 0<qty<=65535:raise ValueError("qty")
  self.db.execute("INSERT INTO item VALUES(?,?,?,?,?,?,0)",(iid,owner,"bag",slot,template,qty))
 def run(self,op,owner,kind,src,dst=0,qty=0,digest="x",newid=None):
  if not op or not owner or kind not in ("equip","unequip","split","consume"):return False
  self.db.execute("BEGIN IMMEDIATE")
  try:
   prev=self.db.execute("SELECT owner,kind,digest FROM ops WHERE id=?",(op,)).fetchone()
   if prev:
    self.db.execute("ROLLBACK");return prev==(owner,kind,digest)
   loc="equip" if kind=="unequip" else "bag"
   row=self.db.execute("SELECT iid,qty,template FROM item WHERE owner=? AND loc=? AND slot=?",(owner,loc,src)).fetchone()
   if not row:self.db.execute("ROLLBACK");return False
   iid,have,template=row
   if kind in ("equip","unequip"):
    target="equip" if kind=="equip" else "bag"
    limit=self.equip_cap if target=="equip" else self.bag_cap
    if type(dst)!=int or not 0<=dst<limit or self.db.execute("SELECT 1 FROM item WHERE owner=? AND loc=? AND slot=?",(owner,target,dst)).fetchone():
     self.db.execute("ROLLBACK");return False
    self.db.execute("UPDATE item SET loc=?,slot=?,rev=rev+1 WHERE iid=?",(target,dst,iid))
   else:
    if type(qty)!=int or not 0<qty<=have:self.db.execute("ROLLBACK");return False
    if kind=="split":
     if not newid or qty==have or type(dst)!=int or not 0<=dst<self.bag_cap or self.db.execute("SELECT 1 FROM item WHERE owner=? AND loc='bag' AND slot=?",(owner,dst)).fetchone():
      self.db.execute("ROLLBACK");return False
     self.db.execute("UPDATE item SET qty=qty-?,rev=rev+1 WHERE iid=?",(qty,iid))
     self.db.execute("INSERT INTO item VALUES(?,?,?,?,?,?,0)",(newid,owner,"bag",dst,template,qty))
    elif qty==have:self.db.execute("DELETE FROM item WHERE iid=?",(iid,))
    else:self.db.execute("UPDATE item SET qty=qty-?,rev=rev+1 WHERE iid=?",(qty,iid))
   self.db.execute("INSERT INTO ops VALUES(?,?,?,?)",(op,owner,kind,digest))
   self.db.execute("INSERT INTO outbox VALUES(?,?)",(op,kind))
   self.db.execute("COMMIT");return True
  except Exception:
   self.db.execute("ROLLBACK");raise
 def rows(self):return self.db.execute("SELECT iid,owner,loc,slot,template,qty FROM item ORDER BY iid").fetchall()
 def close(self):self.db.close()
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.path=str(Path(self.tmp.name)/"inventory.db");self.m=Store(self.path);self.addCleanup(self.m.close)
  self.m.add("a","player",0)
 def test_01_bin(self):
  p=Path("/mnt/data/Asgard.exe")
  if not p.exists():self.skipTest("Asgard.exe not mounted");return
  self.assertEqual(bin_check(p),15)
 def test_02_c1c_subtypes(self):
  tails={1:b"\x03abc",2:b"\0"*4,3:b"\0"*8,4:b"\0"*6,5:b"",6:b"\0"*4,7:b"\0"*2,8:b"\0"*2,9:b"\0"*4}
  for k,t in tails.items():self.assertEqual(c1c(1,2,0,k,t),bytes((1,2,0,k))+t)
  with self.assertRaises(ValueError):c1c(1,2,0,5,b"\0")
  with self.assertRaises(ValueError):c1c(1,2,0,1,b"\x03ab")
 def test_03_remove(self):
  self.assertEqual(s10(b"\x01\x02\x03"),(1,2,3))
  self.assertEqual(s38(b"\x02\x01"),(2,True))
  self.assertEqual(s38(b"\x02\x00"),(2,False))
  with self.assertRaises(ValueError):s10(b"\x01")
 def test_04_equip_idempotent(self):
  self.assertTrue(self.m.run("e","player","equip",0,2))
  self.assertTrue(self.m.run("e","player","equip",0,2))
  self.assertEqual(self.m.rows()[0][2:4],("equip",2))
 def test_05_full_bag_unequip(self):
  self.m.run("e","player","equip",0,2)
  for s in range(3):self.m.add(str(s),"player",s)
  self.assertFalse(self.m.run("u","player","unequip",2,0))
  self.assertEqual(self.m.rows()[0][2:4],("equip",2))
 def test_06_owner(self):
  self.assertFalse(self.m.run("x","attacker","equip",0,2))
 def test_07_split_consume(self):
  self.m.db.execute("UPDATE item SET qty=10 WHERE iid='a'")
  self.assertTrue(self.m.run("sp","player","split",0,1,3,newid="b"))
  self.assertEqual([r[-1] for r in self.m.rows()],[7,3])
  self.assertTrue(self.m.run("co","player","consume",1,qty=3))
  self.assertEqual(len(self.m.rows()),1)
 def test_08_bad_quantity(self):
  for q in (0,-1,2):self.assertFalse(self.m.run(str(q),"player","consume",0,qty=q))
  self.assertEqual(self.m.rows()[0][-1],1)
 def test_09_digest_collision(self):
  self.assertTrue(self.m.run("id","player","equip",0,1,digest="a"))
  self.assertFalse(self.m.run("id","player","equip",0,1,digest="b"))
 def test_10_restart_replay(self):
  self.m.run("id","player","equip",0,1);self.m.close();self.m=Store(self.path)
  self.assertTrue(self.m.run("id","player","equip",0,1))
  self.assertEqual(self.m.db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0],1)
 def test_11_unique_slot(self):
  with self.assertRaises(sqlite3.IntegrityError):self.m.add("b","player",0)
 def test_12_invalid_destination(self):
  self.assertFalse(self.m.run("u","player","unequip",0,0))
  self.assertFalse(self.m.run("e","player","equip",0,8))
if __name__=="__main__":unittest.main(verbosity=2)
