#!/usr/bin/env python3
"""A032 real original C35 emitter path and safely decoded C35 body."""
import os,unittest
from pathlib import Path
from a032_roy3_native_c35_emit import verify,reader,decode_c35,NativeMismatch
class NativeC35Emit(unittest.TestCase):
 def test_01_original_exe_edges_and_anchors(self):
  p=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
  if not p.is_file():self.skipTest("original Asgard.exe unavailable")
  s=verify(p)
  self.assertEqual((s["native_edges"],s["native_anchors"]),(7,15))
  self.assertFalse(s["map_ref_encoded_inside_C35"])
 def test_02_two_be_u16(self):
  self.assertEqual(decode_c35(bytes.fromhex("00040F90")),(4,3984))
 def test_03_native_fixture_pairs(self):
  for s,a,b in (("000063A9",0,25513),("0012F892",18,63634),("0016E9B9",22,59833)):
   self.assertEqual(decode_c35(bytes.fromhex(s)),(a,b))
 def test_04_strict_length(self):
  for raw in (b"",b"\0",b"\0"*3,b"\0"*5):
   with self.assertRaises(ValueError):decode_c35(raw)
 def test_05_strict_bytes_type(self):
  for raw in ("00040F90",bytearray(b"\0"*4),None):
   with self.assertRaises(ValueError):decode_c35(raw)
 def test_06_wrong_pe_rejected(self):
  with self.assertRaises(NativeMismatch):reader(b"hi")
 def test_07_different_exe_rejected(self):
  import tempfile
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"Asgard.exe";p.write_bytes(b"MZ"+b"\0"*200)
   with self.assertRaises(NativeMismatch):verify(p)
 def test_08_native_tcp_not_falsely_claimed(self):
  p=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
  if not p.is_file():self.skipTest("original Asgard.exe unavailable")
  self.assertEqual(verify(p)["native_windows_gui_and_tcp_capture"],"not-run")
if __name__=="__main__":unittest.main(verbosity=2)
