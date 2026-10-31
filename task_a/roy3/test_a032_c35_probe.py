#!/usr/bin/env python3
"""Synthetic and optional original-asset test: no copyrighted bytes in repo."""
import hashlib
import struct
import unittest
from pathlib import Path
from a032_c35_probe import crc_table, feed, checksum, report, FormatError

class CheckC35(unittest.TestCase):
    def setUp(self):
        self.table=tuple(self.make_table())
    @staticmethod
    def make_table():
        # independent generation of the 0x1021 table: used only for synthetic tests
        for i in range(256):
            x=i<<8
            for _ in range(8):
                x=((x<<1)^0x1021 if x&0x8000 else x<<1)&0xffff
            yield x
    @staticmethod
    def make_map(tail7=b"",tail8=b"",tail16=b""):
        if len(tail7)%7 or len(tail8)%8 or len(tail16)%16:raise ValueError
        return (struct.pack("<HHHBB",1,2,4,2,4)+b"\0"*4+b"\0"*80+
                struct.pack("<I",len(tail7)//7)+tail7+
                struct.pack("<I",len(tail8)//8)+tail8+
                struct.pack("<I",len(tail16)//16)+tail16)
    def test_crc_native_primitive(self):
        self.assertEqual(self.table[:3],(0,0x1021,0x2042))
        self.assertEqual(feed(0,b"\x01\x02\x03",self.table),0x1222)
        self.assertEqual(feed(0,b"ABC",self.table),0x1aa6)
    def test_strict_bounds(self):
        with self.assertRaises(FormatError):checksum(self.make_map()[:-1],self.table)
        with self.assertRaises(FormatError):checksum(self.make_map()+b"x",self.table)
    def test_structural_normalization(self):
        tail7_a=struct.pack("<BHhh",1,65535,-5,6)
        tail7_b=struct.pack("<BHhh",99,65535,-5,6)
        # Non-zero first byte is a BOOLEAN, so two raw files have same checksum.
        a=self.make_map(tail7=tail7_a)
        b=self.make_map(tail7=tail7_b)
        self.assertEqual(checksum(a,self.table)["checksum"],checksum(b,self.table)["checksum"])
        # +5..+7 of 16B tail do NOT participate in the 13-call canonical stream.
        c=bytearray(range(16));d=c.copy()
        d[5:8]=b"\x12\x34\x56"
        self.assertEqual(checksum(self.make_map(tail16=c),self.table)["checksum"],
                         checksum(self.make_map(tail16=d),self.table)["checksum"])
        d[8]^=1
        self.assertNotEqual(checksum(self.make_map(tail16=c),self.table)["checksum"],
                            checksum(self.make_map(tail16=d),self.table)["checksum"])
    def test_all_three_tail_types(self):
        rec7=struct.pack("<BHhh",2,17,-1,-2)
        rec8=struct.pack("<4H",1,2,3,4)
        rec16=bytes(range(16))
        value=checksum(self.make_map(rec7,rec8,rec16),self.table)
        self.assertEqual(value["tail_record_counts"],{"7":1,"8":1,"16":1})
        self.assertEqual(len(value["c35_be_u16_pair_hex"]),8)

if __name__=="__main__":
    unittest.main()
