#!/usr/bin/env python3
"""Synthetic branch checks and optional original EXE SHA/native probes."""
import os,tempfile,unittest
from pathlib import Path
from a024_roy3_handler_probe import (verify_exe,pe_reader,decode_handler_slot,
    c43_body,NativeError,HANDLERS,CALLS,ANCHORS)
class A024Roy3Tests(unittest.TestCase):
 def test_01_original_exe(self):
    p=Path(os.getenv("ASGARD_EXE","/mnt/data/Asgard.exe"))
    if not p.exists():self.skipTest("original EXE unavailable")
    r=verify_exe(p)
    self.assertEqual((r["native_calls"],r["native_instruction_anchors"],len(r["dispatch_handlers"])),(21,39,8))
 def test_02_distinct_dispatch(self):
    self.assertEqual(len({x[0] for x in HANDLERS.values()}),8)
    self.assertEqual(len({x[1] for x in HANDLERS.values()}),8)
 def test_03_spawn_remove_die_distinct(self):
    self.assertEqual((HANDLERS[7][1],HANDLERS[14][1],HANDLERS[95][1]),(0x4f17c0,0x4f1da0,0x4f2bb0))
 def test_04_move_single_vs_path(self):
    self.assertEqual((HANDLERS[12][1],HANDLERS[100][1]),(0x4f1610,0x4f1750))
 def test_05_c43_producer_body(self):
    self.assertEqual(c43_body(1,0x11223344,4).hex(),"011122334404")
 def test_06_c43_bad_width(self):
    for triple in ((256,0,4),(1,-1,4),(1,0,256),(1,1.5,4)):
      with self.assertRaises(ValueError):c43_body(*triple)
 def test_07_opcode_range(self):
    for opcode in (2,0x72):
      with self.assertRaises(NativeError):decode_handler_slot(lambda x,y:b"\0"*y,opcode)
 def test_08_wrong_exe(self):
    with tempfile.TemporaryDirectory() as d:
      p=Path(d)/"Asgard.exe";p.write_bytes(b"MZ"+bytes(400))
      with self.assertRaises(NativeError):verify_exe(p)
 def test_09_not_pe(self):
    with self.assertRaises(NativeError):pe_reader(b"bad")
 def test_10_producer_and_kind_branches(self):
    self.assertEqual(CALLS[0x479dc7],0x574500)
    self.assertEqual(CALLS[0x4a23f8],0x574500)
    self.assertEqual(ANCHORS[0x4f1da4],"8b4824")
    self.assertEqual([ANCHORS[x] for x in (0x4f1a8b,0x4f1b68,0x4f1bd1)],["3c01","3c02","3c04"])
if __name__=="__main__":unittest.main()
