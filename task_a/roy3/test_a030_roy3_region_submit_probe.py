#!/usr/bin/env python3
"""Offline fixtures with optional SHA-pinned original resource checks, no GUI."""
import os,unittest
from pathlib import Path
from a030_roy3_region_submit_probe import verify_exe,verify_labels,region_fields,basic_member,read_va,ANCHORS
class A030Roy3Tests(unittest.TestCase):
 def test_original_exe(self):
  p=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
  if not p.exists():self.skipTest("original EXE unavailable")
  x=verify_exe(p)
  self.assertEqual(x["original_anchor_count"],34)
  self.assertTrue(x["region1_F3_mismatch"])
 def test_original_labels(self):
  b=Path(os.environ.get("ASGARD_BASIC_DAT","/mnt/data/Basic.dat"))
  l=Path(os.environ.get("ASGARD_LOCALE_DAT","/mnt/data/Locale.dat"))
  if not(b.exists() and l.exists()):self.skipTest("original resources absent")
  self.assertIn("75",verify_labels(b,l)["EMAIL"])
 def test_region0(self):self.assertEqual(region_fields(0)["F3_wire"],"+0x424")
 def test_region1_mismatch(self):self.assertNotEqual(region_fields(1)["F3_UI"],region_fields(1)["F3_wire"])
 def test_region2_3(self):
  for i in (2,3):
   self.assertEqual(region_fields(i)["F4_wire"],"+0x822")
   self.assertEqual(region_fields(i)["F3_wire"],"+0x624")
 def test_region4(self):self.assertEqual(region_fields(4)["tail"],"u8")
 def test_region1_no_email(self):self.assertIsNone(region_fields(1)["F4_wire"])
 def test_invalid_region(self):
  for x in (-1,5,"2",None):
   with self.assertRaises(ValueError):region_fields(x)
 def test_wrong_pe(self):
  with self.assertRaises(ValueError):read_va(b"bad")
 def test_bad_archive(self):
  with self.assertRaises(ValueError):basic_member(b"bad","x")
 def test_static_not_native_GUI(self):
  p=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
  if not p.exists():self.skipTest("original EXE absent")
  self.assertEqual(verify_exe(p)["native_GUI"],"not-run")
if __name__=="__main__":unittest.main(verbosity=2)
