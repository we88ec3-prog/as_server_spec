"""A-008 synthetic decoded-body tests, separate from native Client E2E."""
import unittest
from a008_status_codec import decode_s08, encode_c47
def be16(n): return n.to_bytes(2, "big")
def be32(n): return n.to_bytes(4, "big")
class StatusWireTest(unittest.TestCase):
    def test_no_payload(self):
        self.assertEqual(decode_s08(b"\x00\x00")["flags"], 0)
    def test_mode_bits_no_payload(self):
        self.assertTrue(decode_s08(be16(0x183))["mode_bit8"])
    def test_full_layout_61_bytes(self):
        block=b"\x7f\x09"+b"".join(be32(x) for x in (10,20,30,40))
        block+=be16(0x1234)+be16(0x5678)+b"\x01\x02"
        block+=be16(9)+be16(10)+bytes(range(6))
        block+=be32(100)+b"\x0b"+be32(200)+b"\x0c"+be32(300)
        block+=be32(400)+b"\x0d\x0e\x0f"+be16(0x4444)+b"\x01\x02\x03\x04"
        self.assertEqual(len(block),61)
        p=decode_s08(be16(0x40)+block)["full"]
        self.assertEqual([p["p2c_u32"],p["p30_u32"],p["p34_u32"],p["p38_u32"]],[10,20,30,40])
        self.assertEqual((p["p3e_u16"],p["p3c_u16"]),(0x1234,0x5678))
        self.assertEqual(p["p60_u32"],400)
        self.assertEqual(p["p64_u8"],13)
    def test_partial_u32(self):
        p=decode_s08(be16(0x20)+b"".join(be32(i) for i in (0,1,0xffffffff,100)))
        self.assertEqual(p["current"],[0,1,4294967295,100])
    def test_secondary_u16(self):
        p=decode_s08(be16(0x10)+be32(99)+b"".join(be16(i) for i in (1,2,3,65535))+be32(42))
        self.assertEqual(p["secondary"]["p8c_98_u16"],[1,2,3,65535])
    def test_string8_and_vector(self):
        p=decode_s08(be16(0x208)+bytes([1,2,3,4,5,2])+b"AB"+bytes([3,9,10,11]))
        self.assertEqual(p["text"]["raw_cp_bytes"],b"AB")
        self.assertEqual(p["extra_list"],[9,10,11])
    def test_mixed_flag_group_order(self):
        body=be16(0x238)+b"".join(be32(i) for i in (1,2,3,4))
        body+=be32(5)+b"".join(be16(i) for i in (6,7,8,9))+be32(10)
        body+=bytes([1,2,3,4,5,0])+bytes([0])
        self.assertEqual(decode_s08(body)["extra_list"],[])
    def test_all_truncation_boundaries(self):
        body=be16(0x208)+bytes([1,2,3,4,5,2])+b"AB"+bytes([3,9,10,11])
        for n in range(len(body)):
            with self.subTest(n=n),self.assertRaises(ValueError):decode_s08(body[:n])
    def test_extra_bytes_rejected(self):
        with self.assertRaises(ValueError):decode_s08(b"\x00\x00\x00")
    def test_c47_one_hot(self):
        for n in (1,2,4,8,16):
            self.assertEqual(encode_c47(n),bytes([n]))
        for n in (0,3,17,255,-1):
            with self.subTest(n=n),self.assertRaises(ValueError):encode_c47(n)
    def test_count_and_string_255(self):
        body=be16(0x208)+bytes([1,2,3,4,5,255])+b"A"*255+bytes([255])+b"B"*255
        p=decode_s08(body)
        self.assertEqual(len(p["text"]["raw_cp_bytes"]),255)
        self.assertEqual(len(p["extra_list"]),255)
if __name__ == "__main__": unittest.main()
