#!/usr/bin/env python3
"""A-011: original Client Monster asset bank/S07/S1A/C39 bounded fixtures.
No NPC spawn/template->monster sprite ID or original Server click policy inferred.
"""
from pathlib import Path
import hashlib,struct,unittest
EXE_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
SIG={
"monster template pointer":(0x40438B,"683c1d5f00"),
"bank range start":(0x404371,"bf401f0000"),
"bank range end":(0x4043A9,"81ff6a1f0000"),
"asset registry":(0x4043A3,"e878c30300"),
"S07 object-ref reader":(0x57E447,"e864caedff"),
"S07 type dispatch":(0x57E45A,"0fb646044883f80d"),
"S07 object 16bit candidate":(0x57E451,"e88ac9edff"),
"S07 generic handler":(0x4F17C0,"6aff"),
"C39 writer u8":(0x573863,"0fb64619"),
"C39 writer ref":(0x57386D,"8b4e1c"),
"C39 writer u16":(0x573878,"0fb75620"),
"S1A ref reader":(0x582FD3,"e8d87eedff"),
}
def original_client_audit(path):
 data=Path(path).read_bytes()
 if hashlib.sha256(data).hexdigest()!=EXE_SHA:raise ValueError("Asgard.exe SHA mismatch")
 filename="Monster%02d.dat".encode("utf-16le")
 if data[0x5f1d3c-0x400000:][:len(filename)]!=filename:raise ValueError("resource pattern mismatch")
 for name,(addr,hex_data) in SIG.items():
  pattern=bytes.fromhex(hex_data)
  if data[addr-0x400000:addr-0x400000+len(pattern)]!=pattern:raise ValueError("native byte signature "+name)
 return len(SIG)
def monster_filenames():
 return [(0x1f40+i,"Monster%02d.dat"%i) for i in range(43)]
def draw_simple(body):
 if len(body)<2:raise ValueError("truncated S07")
 count=struct.unpack_from(">H",body)[0];offset=2;rows=[]
 if count>100:raise ValueError("designed bound")
 for _ in range(count):
  if len(body)-offset<11:raise ValueError("short record")
  x,y,kind,object_ref,asset_candidate=struct.unpack_from(">HHBIH",body,offset);offset+=11
  if kind not in range(5,13):raise ValueError("unverified type-tail")
  rows.append((x,y,kind,object_ref,asset_candidate))
 if offset!=len(body):raise ValueError("trailing")
 return rows
def s1a_motion(body):
 if len(body)!=8:raise ValueError("motion length")
 return struct.unpack(">IBHB",body)
def c39_core(kind,object_ref,resource_field):
 if not all(type(x)==int for x in (kind,object_ref,resource_field)):raise ValueError("type")
 if not 0<=kind<=255 or not 0<=object_ref<=0xffffffff or not 0<=resource_field<=65535:raise ValueError("range")
 return struct.pack(">BIH",kind,object_ref,resource_field)
class Tests(unittest.TestCase):
 def test_01_original_exe(self):
  p=Path("/mnt/data/Asgard.exe")
  if not p.exists():self.skipTest("Asgard.exe missing")
  self.assertEqual(original_client_audit(p),12)
 def test_02_monster_filename_range(self):
  v=monster_filenames();self.assertEqual(len(v),43)
  self.assertEqual(v[0],(0x1f40,"Monster00.dat"))
  self.assertEqual(v[-1],(0x1f6a,"Monster42.dat"))
 def test_03_s07_separate_ref_and_candidate(self):
  row=struct.pack(">HHBIH",31,29,5,0x11223344,0x1f40)
  self.assertEqual(draw_simple(b"\0\x01"+row)[0][3:],(0x11223344,0x1f40))
 def test_04_s07_reject_unsupported_tails(self):
  row=struct.pack(">HHBIH",1,2,1,3,4)
  with self.assertRaises(ValueError):draw_simple(b"\0\x01"+row)
 def test_05_s07_reject_short(self):
  with self.assertRaises(ValueError):draw_simple(b"\0\x01"+b"\0"*10)
 def test_06_motion_fields(self):
  self.assertEqual(s1a_motion(struct.pack(">IBHB",0x11223344,2,0x1234,3)),(0x11223344,2,0x1234,3))
  with self.assertRaises(ValueError):s1a_motion(b"\0"*7)
 def test_07_c39_common_wire(self):
  self.assertEqual(c39_core(1,0x11223344,0x1234).hex(),"01112233441234")
 def test_08_no_unverified_resource_identity(self):
  self.assertNotEqual(monster_filenames()[0][0],0x8000)
  self.assertNotEqual(monster_filenames()[0][0],0x11223344)
 def test_09_bad_c39(self):
  for args in [(-1,0,0),(1,-1,0),(1,0,65536)]:
   with self.assertRaises(ValueError):c39_core(*args)
if __name__=="__main__":unittest.main(verbosity=2)
