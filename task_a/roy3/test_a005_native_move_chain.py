#!/usr/bin/env python3
"""Synthetic branch tests, and optional original EXE via ASGARD_EXE."""
import os
import unittest
from pathlib import Path
from a005_native_move_chain import classify_s0b, check_original, AuditError

class A005NativeChainTests(unittest.TestCase):
    def test_original_if_provided(self):
        exe=os.environ.get("ASGARD_EXE")
        if exe: self.assertEqual(check_original(Path(exe))["offline_native_static"],"PASS")
    def test_seq_wrap_and_high_bit_branch(self):
        self.assertEqual(classify_s0b(0xff,0,predicted_xy=(12,13),authoritative_xy=(12,13)),"set-high-bit-prediction-matched")
        self.assertEqual(classify_s0b(0x7f,0),"clear-high-bit-authoritative-reposition-stop-path")
        self.assertEqual(classify_s0b(0xfe,0),"stale-or-out-of-order")
    def test_clear_high_bit_vs_set_high_bit(self):
        self.assertEqual(classify_s0b(0x05,6),"clear-high-bit-authoritative-reposition-stop-path")
        self.assertEqual(classify_s0b(0x85,6,predicted_xy=(3,4),authoritative_xy=(2,4)),"set-high-bit-authoritative-rebase")
        self.assertEqual(classify_s0b(0x85,6),"set-high-bit-needs-prediction-check")
    def test_bad_sequence(self):
        for a,b in ((256,0),(-1,0),(0,128),(0,-1)):
            with self.assertRaises(ValueError):classify_s0b(a,b)
    def test_reject_nonoriginal_exe(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            bad=Path(t)/"Asgard.exe"
            bad.write_bytes(b"MZ"+bytes(512))
            with self.assertRaises(AuditError):check_original(bad)

if __name__=='__main__':unittest.main()
