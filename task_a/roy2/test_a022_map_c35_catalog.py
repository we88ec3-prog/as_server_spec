"""A-022 synthetic negative tests; optional real-asset census via ASGARD_ASSETS_DIR."""
import os
from pathlib import Path
import struct
import unittest

from a022_map_c35_catalog import InvalidResource, census, feed, native_c35, read_members


class A022MapC35Test(unittest.TestCase):
    @staticmethod
    def make_map():
        # 2x4 map: one 2B block, eight 10B tiles, one entry per tail type.
        header = struct.pack('<HHHBB', 2, 2, 4, 2, 4)
        block = b'\x12\x34'
        tiles = bytes(range(80))
        r7 = struct.pack('<BHhh', 2, 31, -9, 17)
        r8 = struct.pack('<HHHH', 1, 17, 23, 99)
        r16 = struct.pack('<HHIIHH', 3, 0x0100, 0x0302017F, 0x11223344, 8, 9)
        return (header + block + tiles + struct.pack('<I',1) + r7 +
                struct.pack('<I',1) + r8 + struct.pack('<I',1) + r16)

    def setUp(self):
        self.table = []
        # Independent polynomial-derived fixture; native byte table is
        # SHA/anchor verified by census() when original EXE is provided.
        for i in range(256):
            x = i << 8
            for _ in range(8):
                x = (((x << 1) ^ 0x1021) if x & 0x8000 else (x << 1)) & 65535
            self.table.append(x)

    def test_crc_native_primitive_vectors(self):
        self.assertEqual(feed(0,b'\x01\x02\x03',self.table),0x1222)
        self.assertEqual(feed(0,b'ABC',self.table),0x1AA6)

    def test_full_map_c35_and_canonical_skip(self):
        raw = self.make_map()
        base = native_c35(raw,self.table)
        self.assertEqual(base['tail_counts_7_8_16'],[1,1,1])
        self.assertEqual((base['width'],base['height']),(2,4))
        # 16B record offsets +5..+7 do not enter native checksum.
        changed = bytearray(raw)
        changed[-11:-8] = b'\xff\x00\x7a'
        self.assertEqual(native_c35(changed,self.table)['c35_be_hex'],
                         base['c35_be_hex'])
        changed[-12] ^= 0x40  # 16B record +4 DOES enter checksum.
        self.assertNotEqual(native_c35(changed,self.table)['c35_be_hex'],
                            base['c35_be_hex'])

    def test_bad_map_rejected(self):
        raw = self.make_map()
        damaged = (raw[:3],raw[:-1],raw+b'\x00',raw[:6]+b'\x00'+raw[7:])
        for value in damaged:
            with self.subTest(length=len(value)):
                with self.assertRaises(InvalidResource):
                    native_c35(value,self.table)

    def test_dat_first_offset_and_library(self):
        raw = self.make_map()
        entry = lambda start,name: struct.pack('<I',start)+name.ljust(32,b'\x00')
        dat = struct.pack('<I',2)+entry(76,b'00006.map')+entry(76+len(raw),b'')+raw
        members = list(read_members(dat,0))
        self.assertEqual(len(members),1)
        self.assertEqual(members[0][0],6)
        with self.assertRaises(InvalidResource):
            list(read_members(dat,1))
        with self.assertRaises(InvalidResource):
            list(read_members(dat[:4]+struct.pack('<I',80)+dat[8:],0))

    @unittest.skipUnless(os.getenv('ASGARD_ASSETS_DIR'),
                         'set ASGARD_ASSETS_DIR for original asset census')
    def test_full_original_census(self):
        root=Path(os.environ['ASGARD_ASSETS_DIR'])
        summary,maps=census(root/'Asgard.exe',root)
        self.assertEqual((summary['map_count'],summary['unique_map_payloads'],
                          summary['unique_c35_pairs']),(494,330,330))
        by_ref={r['map_ref']:r['c35_be_hex'] for r in maps}
        self.assertEqual((by_ref[6],by_ref[10000],by_ref[18001]),
                         ('00040F90','00040F90','0012F892'))


if __name__=='__main__':
    unittest.main()
