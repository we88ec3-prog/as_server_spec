#!/usr/bin/env python3
"""A-004 native BIN signatures + synthetic visibility wire/domain; NOT native Client E2E."""
import hashlib, struct, unittest
from dataclasses import dataclass
from pathlib import Path
EXE_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
SIG={
 "S07 ctor":(0x57e329,"6a07"),"S07 count":(0x57e3e5,"e8f6c9edff"),
 "S07 stride":(0x57e3f1,"69c028020000"),"S07 object ID":(0x57e447,"e864caedff"),
 "S07 kind dispatch":(0x57e45a,"0fb646044883f80d"),
 "S0E ctor":(0x585e79,"6a0e"),"S0E ID":(0x585f13,"e8984fedff"),
 "S5F ctor":(0x57e1c9,"6a5f"),"S5F ID":(0x57e263,"e848ccedff"),
 "S33 ctor":(0x5854d9,"6a33"),"S0C ctor":(0x5833b9,"6a0c"),
 "S0C ID":(0x583453,"e8587aedff"),"S64 ctor":(0x583549,"6a64"),
 "S64 ID":(0x5835e4,"e8c778edff"),"S11 ctor":(0x57d6d9,"6a11"),
 "S11 ID":(0x57d773,"e838d7edff"),"S1A ctor":(0x582f39,"6a1a"),
 "registry lookup":(0x4eac30,"51568bf1"),
 "draw handler count":(0x4f17e2,"66395824"),"draw handler ID":(0x4f1818,"8b560852")
}
def audit(path):
 b=Path(path).read_bytes()
 if hashlib.sha256(b).hexdigest()!=EXE_SHA:raise ValueError("Asgard.exe revision mismatch")
 for name,(va,h) in SIG.items():
  raw=bytes.fromhex(h)
  if b[va-0x400000:va-0x400000+len(raw)]!=raw:raise ValueError(name)
 return len(SIG)
def pack_ref(ref):
 if type(ref)!=int or not 0<=ref<=0xffffffff:raise ValueError("u32")
 return struct.pack(">I",ref)
def unpack_ref(body):
 if len(body)!=4:raise ValueError("u32 length")
 return struct.unpack(">I",body)[0]
def move_object(body):
 if len(body)!=10:raise ValueError("S0C length")
 return struct.unpack(">IHHBB",body)
def change_direction(body):
 if len(body)!=5:raise ValueError("S11 length")
 return struct.unpack(">IB",body)
def move_path(body):
 if len(body)<15:raise ValueError("S64 short")
 ref,x,y,flag,n=struct.unpack_from(">IHHBB",body)
 if len(body)!=15+n:raise ValueError("S64 path length")
 return ref,x,y,flag,tuple(body[10:10+n]),struct.unpack_from(">HHB",body,10+n)
def draw_simple(body,max_objects=100):
 # Types 5..12 have no tail in original S07 switch. Others fail closed until typed codec.
 if len(body)<2:raise ValueError("S07 short")
 n=struct.unpack_from(">H",body)[0]
 if n>max_objects:raise ValueError("DESIGNED count bound")
 out=[];o=2
 for _ in range(n):
  if o+11>len(body):raise ValueError("truncated")
  x,y,typ,ref,attr=struct.unpack_from(">HHBIH",body,o);o+=11
  if not 5<=typ<=12:raise ValueError("variant-specific type not supported")
  out.append((x,y,typ,ref,attr))
 if o!=len(body):raise ValueError("extra")
 return out
@dataclass(frozen=True)
class Entity:
 world:str
 gen:int
 map_id:int
 epoch:int
 entity_id:int
 wire_ref:int
 x:int
 y:int
 kind:str
class Interest:
 """DESIGNED per observer projections, not original game's interest algorithm."""
 def __init__(self,self_ref,world="w",gen=1,map_id=100,epoch=1):
  self.self_ref,self.world,self.gen,self.map_id,self.epoch=self_ref,world,gen,map_id,epoch
  self.visible={};self.tombstones=set()
 def scope(self,e):
  return (e.world,e.gen,e.map_id,e.epoch)==(self.world,self.gen,self.map_id,self.epoch)
 def add(self,e):
  if not self.scope(e) or e.wire_ref==self.self_ref:return False
  old=self.visible.get(e.wire_ref)
  if old and old.entity_id!=e.entity_id:return False
  self.visible[e.wire_ref]=e;self.tombstones.discard(e.wire_ref);return True
 def update(self,e):
  old=self.visible.get(e.wire_ref)
  if not self.scope(e) or old is None or old.entity_id!=e.entity_id:return False
  self.visible[e.wire_ref]=e;return True
 def remove(self,ref,world,gen,map_id,epoch):
  if (world,gen,map_id,epoch)!=(self.world,self.gen,self.map_id,self.epoch):return False
  if ref==self.self_ref or ref not in self.visible:return False
  del self.visible[ref];self.tombstones.add(ref);return True
 def death(self,ref,world,gen,map_id,epoch):
  if (world,gen,map_id,epoch)!=(self.world,self.gen,self.map_id,self.epoch):return False
  return ref in self.visible  # do NOT equate death event to AOI removal
 def map_reset(self,map_id,epoch,gen=None):
  self.map_id,self.epoch=map_id,epoch
  if gen is not None:self.gen=gen
  self.visible.clear();self.tombstones.clear()
class Tests(unittest.TestCase):
 def setUp(self):
  self.a=Interest(1);self.e=Entity("w",1,100,1,15,42,10,20,"human")
 def test_01_bin(self):
  p=Path("/mnt/data/Asgard.exe")
  if not p.exists():self.skipTest("Asgard.exe not mounted")
  self.assertEqual(audit(p),20)
 def test_02_ref_endian(self):
  self.assertEqual(pack_ref(0x11223344).hex(),"11223344")
  self.assertEqual(unpack_ref(bytes.fromhex("11223344")),0x11223344)
  with self.assertRaises(ValueError):unpack_ref(b"\x01")
 def test_03_draw_simple(self):
  b=b"\x00\x01"+struct.pack(">HHBIH",12,13,5,0x11223344,22)
  self.assertEqual(draw_simple(b),[(12,13,5,0x11223344,22)])
 def test_04_draw_invalid(self):
  for body in (b"\xff\xff",b"\x00\x01",b"\x00\x01"+struct.pack(">HHBIH",1,1,1,42,1)):
   with self.assertRaises(ValueError):draw_simple(body)
 def test_05_move_object(self):
  self.assertEqual(move_object(bytes.fromhex("11223344001a002b0304")),(0x11223344,26,43,3,4))
  with self.assertRaises(ValueError):move_object(b"\x00"*9)
 def test_06_move_path(self):
  b=struct.pack(">IHHBB",42,10,20,1,2)+b"\x06\x07"+struct.pack(">HHB",11,21,3)
  self.assertEqual(move_path(b),(42,10,20,1,(6,7),(11,21,3)))
  with self.assertRaises(ValueError):move_path(b[:-1])
 def test_07_change_direction(self):
  self.assertEqual(change_direction(pack_ref(42)+b"\x07"),(42,7))
  with self.assertRaises(ValueError):change_direction(b"\x00"*6)
 def test_08_self_not_other(self):
  self.assertFalse(self.a.add(Entity("w",1,100,1,99,1,10,20,"human")))
 def test_09_spawn_update(self):
  self.assertTrue(self.a.add(self.e))
  self.assertTrue(self.a.update(Entity("w",1,100,1,15,42,11,20,"human")))
  self.assertEqual(self.a.visible[42].x,11)
 def test_10_repeat_spawn(self):
  self.assertTrue(self.a.add(self.e));self.assertTrue(self.a.add(self.e))
  self.assertEqual(len(self.a.visible),1)
 def test_11_leave_not_death(self):
  self.a.add(self.e)
  self.assertTrue(self.a.remove(42,"w",1,100,1))
  self.assertFalse(self.a.death(42,"w",1,100,1))
  self.assertFalse(self.a.remove(42,"w",1,100,1))
 def test_12_death_not_leave(self):
  self.a.add(self.e)
  self.assertTrue(self.a.death(42,"w",1,100,1))
  self.assertIn(42,self.a.visible)
 def test_13_map_epoch_fence(self):
  self.a.add(self.e);self.a.map_reset(200,2)
  self.assertFalse(self.a.remove(42,"w",1,100,1))
  self.assertEqual(len(self.a.visible),0)
 def test_14_ref_conflict(self):
  self.a.add(self.e)
  self.assertFalse(self.a.add(Entity("w",1,100,1,16,42,12,25,"monster")))
  self.assertEqual(self.a.visible[42].entity_id,15)
 def test_15_wrong_map(self):
  self.assertFalse(self.a.add(Entity("w",1,101,1,15,42,11,20,"human")))
 def test_16_stale_generation(self):
  self.assertFalse(self.a.add(Entity("w",0,100,1,15,42,11,20,"human")))
  self.assertFalse(self.a.update(self.e))
 def test_17_reappear_after_leave(self):
  self.a.add(self.e);self.assertTrue(self.a.remove(42,"w",1,100,1))
  self.assertTrue(self.a.add(self.e));self.assertNotIn(42,self.a.tombstones)
 def test_18_ref_update_identity_mismatch(self):
  self.a.add(self.e)
  self.assertFalse(self.a.update(Entity("w",1,100,1,99,42,10,10,"human")))
if __name__=="__main__":unittest.main(verbosity=2)
