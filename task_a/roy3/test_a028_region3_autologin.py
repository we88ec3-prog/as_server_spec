"""A028 Native Region3 automatic C03 path, original-EXE optional in CI."""
import os,unittest
from pathlib import Path
from a028_region3_autologin_probe import (verify,NativeMismatch,conditional_constructor_auto_c03,
 arg4_event_path,REGION_CTOR_TARGETS,reader)
class NativeAutoLoginChainTests(unittest.TestCase):
 def test_01_hash_locked_original(self):
  exe=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
  if not exe.exists():self.skipTest("original EXE not available")
  p=verify(exe)
  self.assertEqual((p["call_edges"],p["byte_anchors"]),(7,36))
  self.assertEqual((p["region_ctor_cases"],p["event_cases"]),(5,10))
  self.assertEqual(p["native_gui"],"not-run")
 def test_02_success_requires_region3(self):
  for region in (0,1,2,4):
   self.assertFalse(conditional_constructor_auto_c03(region,True,True,0))
 def test_03_both_cached_fields_nonempty(self):
  for x,y in ((False,False),(True,False),(False,True)):
   self.assertFalse(conditional_constructor_auto_c03(3,x,y,0))
 def test_04_ctrl_held_suppresses(self):
  self.assertFalse(conditional_constructor_auto_c03(3,True,True,-32768))
  self.assertFalse(conditional_constructor_auto_c03(3,True,True,-1))
 def test_05_ctrl_not_held_can_auto_send(self):
  self.assertTrue(conditional_constructor_auto_c03(3,True,True,0))
  self.assertTrue(conditional_constructor_auto_c03(3,True,True,1))
 def test_06_case4_reaches_login_packet_sender(self):
  self.assertEqual(arg4_event_path(4),0x4a8996)
  self.assertEqual(REGION_CTOR_TARGETS[3],0x4a9508)
 def test_07_other_event_cases_different(self):
  self.assertEqual(arg4_event_path(5),0x4a8a3a)
  self.assertEqual(arg4_event_path(6),0x4a8a75)
  self.assertIsNone(arg4_event_path(3))
  self.assertIsNone(arg4_event_path(14))
 def test_08_unsupported_region_guard(self):
  for r in (-1,5,3.0,"3"):
   with self.assertRaises(ValueError):conditional_constructor_auto_c03(r,True,True,0)
 def test_09_control_must_be_signed_short(self):
  for v in (-32769,32768,"0",False):
   with self.assertRaises(ValueError):conditional_constructor_auto_c03(3,True,True,v)
 def test_10_not_PE(self):
  with self.assertRaises(NativeMismatch):reader(b"bad")
 def test_11_explicit_no_world_proof(self):
  exe=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
  if not exe.exists():self.skipTest("original EXE not available")
  self.assertEqual(verify(exe)["S03_C10_World_after_auto_C03"],"unverified")
if __name__=="__main__":unittest.main(verbosity=2)
