#!/usr/bin/env python3
"""A026 roy3: original hash-pinned sources optional in CI; synthetic codecs always run."""
import os
import tempfile
import unittest
from pathlib import Path
from a026_roy3_native_probe import (verify_exe,verify_born,verify_basic,c39_fields,
     synthetic_c39_body,dat_members,pe_reader)
class A026Native(unittest.TestCase):
    def test_01_original_exe(self):
        p=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
        if not p.exists():self.skipTest("original EXE unavailable")
        r=verify_exe(p)
        self.assertEqual((r["call_edges"],r["byte_anchors"],r["C39_internal_selectors"],r["S2F_receive_cases"]),(14,17,9,10))
    def test_02_original_born(self):
        p=Path(os.environ.get("ASGARD_BORN","/mnt/data/Born.dat"))
        if not p.exists():self.skipTest("original Born.dat unavailable")
        r=verify_born(p)
        self.assertEqual(r["waypoint"],[31,29])
        self.assertFalse(r["direct_SendReply"] or r["direct_reward_or_finish"])
    def test_03_original_basic(self):
        p=Path(os.environ.get("ASGARD_BASIC","/mnt/data/Basic.dat"))
        if not p.exists():self.skipTest("original Basic.dat unavailable")
        r=verify_basic(p)
        self.assertEqual(r["members"],38)
        self.assertEqual(r["verified_ui_members"]["AlertFrame.ypf"]["size"],177648)
    def test_04_selector_shapes(self):
        self.assertEqual([len(c39_fields(i)) for i in range(1,10)],[1,1,2,1,1,1,1,1,1])
    def test_05_string8(self):
        self.assertEqual(synthetic_c39_body(1,4,0x11223344,0x5566,b"ABC").hex(),"0411223344556603414243")
    def test_06_two_string8(self):
        self.assertEqual(synthetic_c39_body(3,4,0x11223344,0x5566,b"A",b"BC").hex(),"041122334455660141024243")
    def test_07_u8(self):
        self.assertEqual(synthetic_c39_body(8,4,0x11223344,0x5566,126).hex(),"041122334455667e")
    def test_08_internal_selector_not_wire(self):
        self.assertEqual(synthetic_c39_body(1,4,2,3,b"Z"),synthetic_c39_body(2,4,2,3,b"Z"))
    def test_09_reject_invalid(self):
        for n in (0,10):
            with self.assertRaises(ValueError):c39_fields(n)
        with self.assertRaises(ValueError):synthetic_c39_body(3,0,0,0,b"x")
        with self.assertRaises(ValueError):synthetic_c39_body(1,0,0,0,b"x"*256)
        with self.assertRaises(ValueError):synthetic_c39_body(9,0,0,0,b"x")
        with self.assertRaises(ValueError):pe_reader(b"bad")
    def test_10_archive_sentinel(self):
        import struct
        d=struct.pack("<I",2)+struct.pack("<I",76)+b"AlertFrame.ypf".ljust(32,b"\x00")+struct.pack("<I",79)+bytes(32)+b"abc"
        self.assertEqual(dat_members(d),{"AlertFrame.ypf":(76,3)})
        with self.assertRaises(ValueError):dat_members(d[:-1])
if __name__=="__main__":unittest.main()
