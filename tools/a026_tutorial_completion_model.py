#!/usr/bin/env python3
"""A-026: static original BIN/resource signatures + DESIGNED SQLite completion fixtures.
Original Server completion/award/exit rules are UNKNOWN; no native Client E2E here.
"""
import hashlib,sqlite3,struct,tempfile,unittest,zlib
from pathlib import Path
CLIENT="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
BORN="992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98"
SIG={
 "C39 ctor":(0x5737c9,"6a39"),
 "C39 u8":(0x573863,"0fb64619"),
 "C39 u32":(0x57386d,"8b4e1c"),
 "C39 u16":(0x573878,"0fb75620"),
 "C39 1..9 branch":(0x573884,"0fb646184883f808"),
 "S15 ctor":(0x57fe99,"6a15"),
 "S15 u16 parser":(0x57ff34,"e8a7aeedff"),
 "S04 pos parser":(0x589993,"e84814edff"),
 "C6C writer":(0x575210,"56"),
 "C0B Quit ctor":(0x574bb9,"6a0b"),
 "C0B Quit empty writer":(0x574c50,"c3"),
}
def verify_native(path):
 b=Path(path).read_bytes()
 if hashlib.sha256(b).hexdigest()!=CLIENT:raise ValueError("Asgard.exe release mismatch")
 for name,(va,h) in SIG.items():
  v=bytes.fromhex(h)
  if b[va-0x400000:va-0x400000+len(v)]!=v:raise ValueError(name)
 return len(SIG)
def verify_born(path):
 b=Path(path).read_bytes()
 if hashlib.sha256(b).hexdigest()!=BORN:raise ValueError("Born.dat mismatch")
 data=zlib.decompress(b)
 if len(data)!=1154 or struct.unpack(">HI",data[:6])!=(1,574):raise ValueError("bad wrapper")
 return data[6:].decode("utf-16le")
def close_body(sub,ctx=0x11223344):
 if sub not in (2,4):raise ValueError("invalid subtype")
 return bytes([sub,4])+b"Born"+struct.pack(">I",ctx)
def parse_close(b):
 if len(b)<6 or b[0] not in (2,4) or len(b)!=b[1]+6:raise ValueError("invalid C6C close")
 return (b[0],b[2:-4],struct.unpack(">I",b[-4:])[0])

class SafeModel:
 """Only a designed proof/transaction/recovery reference, not game Server code."""
 def __init__(self,path):
  self.db=sqlite3.connect(path,isolation_level=None)
  self.db.executescript("""
   CREATE TABLE IF NOT EXISTS character(id TEXT PRIMARY KEY, generation INTEGER, map INTEGER, x INTEGER, y INTEGER, state TEXT);
   CREATE TABLE IF NOT EXISTS script(run TEXT PRIMARY KEY,char TEXT,gen INTEGER,ctx INTEGER,c4 INTEGER DEFAULT 0,c2 INTEGER DEFAULT 0);
   CREATE TABLE IF NOT EXISTS event(id TEXT PRIMARY KEY,char TEXT,gen INTEGER,rule TEXT);
   CREATE TABLE IF NOT EXISTS completion(char TEXT PRIMARY KEY,rule TEXT,event TEXT UNIQUE,reward INTEGER);
   CREATE TABLE IF NOT EXISTS reward(char TEXT PRIMARY KEY,item INTEGER);
   CREATE TABLE IF NOT EXISTS exit_pending(char TEXT PRIMARY KEY,gen INTEGER,epoch TEXT,map INTEGER,x INTEGER,y INTEGER,revision TEXT);
   CREATE TABLE IF NOT EXISTS outbox(char TEXT,kind TEXT,PRIMARY KEY(char,kind));
  """)
 def init(self):
  self.db.execute("INSERT INTO character VALUES('hero',7,111,10,10,'entered')")
 def state(self):
  return self.db.execute("SELECT state,map,x,y FROM character WHERE id='hero'").fetchone()
 def count(self,table):
  if table not in ("completion","reward","outbox"):raise ValueError("bad table")
  return self.db.execute("SELECT COUNT(*) FROM "+table).fetchone()[0]
 def born(self,run,gen,ctx):
  if not self.db.execute("SELECT 1 FROM character WHERE id='hero' AND generation=?",(gen,)).fetchone():return False
  self.db.execute("INSERT OR IGNORE INTO script(run,char,gen,ctx) VALUES(?,?,?,?)",(run,"hero",gen,ctx));return True
 def close_born(self,run,gen,ctx,sub):
  if sub not in (2,4):return False
  if self.db.execute("SELECT char,gen,ctx FROM script WHERE run=?",(run,)).fetchone()!=("hero",gen,ctx):return False
  self.db.execute("UPDATE script SET c"+str(sub)+"=1 WHERE run=?",(run,));return True
 def event(self,id,gen,rule,verified):
  if not verified or self.db.execute("SELECT generation FROM character WHERE id='hero'").fetchone()!=(gen,):return False
  self.db.execute("INSERT OR IGNORE INTO event VALUES(?,?,?,?)",(id,"hero",gen,rule));return True
 def complete(self,gen,rule,event,verified_rule,reward=None,verified_reward=False):
  if not verified_rule or not rule or not event:return False
  if reward is not None and (not verified_reward or type(reward)!=int or not 0<=reward<=65535):return False
  prior=self.db.execute("SELECT rule,event,reward FROM completion WHERE char='hero'").fetchone()
  if prior:return prior==(rule,event,reward)
  self.db.execute("BEGIN IMMEDIATE")
  try:
   r=self.db.execute("""SELECT c.generation,c.state,e.gen FROM character c
       JOIN event e ON e.char=c.id WHERE c.id='hero' AND e.id=? AND e.rule=?""",(event,rule)).fetchone()
   if r!=(gen,"entered",gen):self.db.execute("ROLLBACK");return False
   self.db.execute("INSERT INTO completion VALUES(?,?,?,?)",("hero",rule,event,reward))
   if reward is not None:self.db.execute("INSERT INTO reward VALUES('hero',?)",(reward,))
   self.db.execute("UPDATE character SET state='completed' WHERE id='hero'")
   self.db.execute("INSERT OR IGNORE INTO outbox VALUES('hero','completed')")
   self.db.execute("COMMIT");return True
  except Exception:self.db.execute("ROLLBACK");raise
 def exit_request(self,gen,epoch,mapid,x,y,revision,verified_destination):
  if not verified_destination or not epoch or not revision or not all(type(n)==int and 0<=n<=65535 for n in (mapid,x,y)):return False
  if self.db.execute("SELECT generation,state FROM character WHERE id='hero'").fetchone()!=(gen,"completed"):return False
  old=self.db.execute("SELECT gen,epoch,map,x,y,revision FROM exit_pending WHERE char='hero'").fetchone()
  new=(gen,epoch,mapid,x,y,revision)
  if old:return old==new
  self.db.execute("INSERT INTO exit_pending VALUES('hero',?,?,?,?,?,?)",new);return True
 def exit_commit(self,gen,epoch,crc_matches,load_barrier):
  # epoch is INTERNAL; native C35 wire contains NO epoch!
  if not crc_matches or not load_barrier:return False
  self.db.execute("BEGIN IMMEDIATE")
  try:
   row=self.db.execute("SELECT gen,epoch,map,x,y FROM exit_pending WHERE char='hero'").fetchone()
   if not row or row[:2]!=(gen,epoch):self.db.execute("ROLLBACK");return False
   self.db.execute("UPDATE character SET map=?,x=?,y=?,state='exited' WHERE id='hero'",row[2:])
   self.db.execute("DELETE FROM exit_pending WHERE char='hero'")
   self.db.execute("INSERT OR IGNORE INTO outbox VALUES('hero','exited')")
   self.db.execute("COMMIT");return True
  except Exception:self.db.execute("ROLLBACK");raise
 def close(self):self.db.close()

class A026Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.path=str(Path(self.tmp.name)/"test.db")
  self.m=SafeModel(self.path);self.m.init();self.addCleanup(self.m.close)
 def event(self):return self.m.event("evt1",7,"verified-test-rule",True)
 def complete(self,reward=None,verified_reward=False,**k):
  d=dict(gen=7,rule="verified-test-rule",event="evt1",verified_rule=True,reward=reward,verified_reward=verified_reward)
  d.update(k);return self.m.complete(**d)
 def test_01_native_signatures(self):
  p=Path("/mnt/data/Asgard.exe")
  if not p.exists():self.skipTest("needs Asgard.exe");return
  self.assertEqual(verify_native(p),11)
 def test_02_born_wrapper_and_absent_reward(self):
  p=Path("/mnt/data/Born.dat")
  if not p.exists():self.skipTest("needs Born.dat");return
  s=verify_born(p)
  self.assertIn("PaperDialog_Create",s);self.assertIn("(31,29)",s)
  for x in ("SendReply","quest.Complete","reward_item","tutorial_completed"):self.assertNotIn(x,s)
 def test_03_c6c_close_not_completion(self):
  self.assertEqual(close_body(4).hex(),"0404426f726e11223344")
  self.assertEqual(close_body(2).hex(),"0204426f726e11223344")
  self.assertTrue(self.m.born("r",7,0x11223344))
  for n in (4,2,4,2):
   subtype,name,ctx=parse_close(close_body(n))
   self.assertEqual(name,b"Born")
   self.assertTrue(self.m.close_born("r",7,ctx,subtype))
  self.assertEqual(self.m.state()[0],"entered")
  self.assertEqual(self.m.count("completion"),0)
 def test_04_old_context_and_truncated_close(self):
  self.m.born("r",7,0x11223344)
  self.assertFalse(self.m.close_born("r",8,0x11223344,4))
  self.assertFalse(self.m.close_born("r",7,55,2))
  with self.assertRaises(ValueError):parse_close(b"\x04\x04Born\x11")
 def test_05_unverified_rule_no_grant(self):
  self.assertFalse(self.complete())
  self.assertFalse(self.m.event("evt1",7,"verified-test-rule",False))
  self.assertTrue(self.event())
  self.assertFalse(self.complete(verified_rule=False))
  self.assertEqual(self.m.count("completion"),0)
 def test_06_optional_reward_once(self):
  self.event()
  self.assertFalse(self.complete(reward=42,verified_reward=False))
  self.assertTrue(self.complete(reward=42,verified_reward=True))
  self.assertTrue(self.complete(reward=42,verified_reward=True))
  self.assertFalse(self.complete(reward=43,verified_reward=True))
  self.assertEqual((self.m.count("completion"),self.m.count("reward")),(1,1))
 def test_07_no_invented_reward(self):
  self.event();self.assertTrue(self.complete())
  self.assertEqual((self.m.count("completion"),self.m.count("reward")),(1,0))
 def test_08_unverified_destination_and_generation(self):
  self.event();self.complete()
  self.assertFalse(self.m.exit_request(7,"e1",222,20,20,"rev",False))
  self.assertFalse(self.m.exit_request(8,"e1",222,20,20,"rev",True))
  self.assertTrue(self.m.exit_request(7,"e1",222,20,20,"rev",True))
  self.assertFalse(self.m.exit_request(7,"e2",222,20,20,"rev",True))
  self.assertFalse(self.m.exit_commit(7,"e2",True,True))
  self.assertFalse(self.m.exit_commit(7,"e1",True,False))
  self.assertTrue(self.m.exit_commit(7,"e1",True,True))
  self.assertEqual(self.m.state(),("exited",222,20,20))
 def test_09_crash_after_completion_before_exit(self):
  self.event();self.complete()
  self.m.exit_request(7,"e1",222,20,20,"rev",True)
  self.m.close();self.m=SafeModel(self.path)
  self.assertEqual(self.m.state(),("completed",111,10,10))
  self.assertFalse(self.m.exit_commit(7,"e1",False,True))
  self.assertTrue(self.m.exit_commit(7,"e1",True,True))
  self.assertEqual((self.m.count("completion"),self.m.count("reward")),(1,0))
 def test_10_completion_duplicate_conflict(self):
  self.event();self.assertTrue(self.complete())
  self.assertFalse(self.complete(event="not-same"))
  self.assertEqual(self.m.count("completion"),1)

if __name__=="__main__":unittest.main(verbosity=2)
