#!/usr/bin/env python3
"""A-015 synthetic MAP field audit tests; no original game assets bundled."""
import struct
import tempfile
import unittest
from pathlib import Path
from a015_field_audit import inspect_archive

def mkmap(rec7=(),rec8=(),rec16=()):
    b=struct.pack("<HHHBB",1,1,4,4,4)+bytes(4+4*4*10)
    for stride,recs in zip((7,8,16),(rec7,rec8,rec16)):
        assert all(len(r)==stride for r in recs)
        b+=struct.pack("<I",len(recs))+b"".join(recs)
    return b

def archive(m):
    start=4+2*36
    return (struct.pack("<I",2)+struct.pack("<I32s",start,b"00000.map")+
            struct.pack("<I32s",start+len(m),b"")+m)

class Tests(unittest.TestCase):
    def read(self,contents):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"Map0.dat";p.write_bytes(contents)
            return inspect_archive(p)
    def test_valid_records(self):
        r7=struct.pack("<BHhh",1,65000,-20,5)
        r8=struct.pack("<HHHH",12,191,127,3)
        r16=struct.pack("<HHIIHH",1002,0,0,128,191,127)
        result=self.read(archive(mkmap([r7],[r8],[r16])))
        self.assertEqual(result["tail_count_7_8_16"],[1,1,1])
        self.assertEqual(result["tail8_pixel_bounds_pass"],1)
        self.assertEqual(result["tail16_pixel_bounds_pass"],1)
        self.assertEqual(result["header_third_differs"],1)
    def test_out_of_bounds_is_counted_not_assumed(self):
        r8=struct.pack("<HHHH",12,192,0,3)
        r16=struct.pack("<HHIIHH",1002,0,0,128,0,128)
        result=self.read(archive(mkmap(rec8=[r8],rec16=[r16])))
        self.assertEqual(result["tail8_pixel_bounds_pass"],0)
        self.assertEqual(result["tail16_pixel_bounds_pass"],0)
    def test_truncated_map(self):
        with self.assertRaises(ValueError): self.read(archive(mkmap()[:-1]))
    def test_truncated_archive(self):
        with self.assertRaises(ValueError): self.read(archive(mkmap())[:-1])

if __name__=="__main__":unittest.main()
