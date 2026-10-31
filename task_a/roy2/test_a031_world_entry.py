"""A-031 synthetic C10/C25 decoded-body tests; NOT native GUI replay."""
import unittest
from a031_world_entry_codec import (
    PacketError,c10_raw_token,c25_region3_encoded,parse_c25_region3,
    c25_native_codec_for_region,native_world_send_profile,
)

class A031WorldEntryTests(unittest.TestCase):
    def test_c10_is_raw_token(self):
        self.assertEqual(c10_raw_token(bytes.fromhex("123400ff")),bytes.fromhex("123400ff"))
    def test_c10_does_not_prefix_length(self):
        self.assertEqual(len(c10_raw_token(b"token")),5)
    def test_c10_rejects_bad_token(self):
        for data in (None, "abc", b"", b"x"*256):
            with self.subTest(data=type(data)),self.assertRaises(PacketError):
                c10_raw_token(data)
    def test_c25_three_string8_byte_layout(self):
        self.assertEqual(c25_region3_encoded([b"ab",b"c",b"de"]),b"\x02ab\x01c\x02de")
    def test_c25_zero_length_is_three_zero_prefixes(self):
        self.assertEqual(c25_region3_encoded([b"",b"",b""]),bytes.fromhex("000000"))
    def test_c25_exact_roundtrip_raw_cp950(self):
        fields=(bytes.fromhex("a4a4"),b"credit",b"")
        self.assertEqual(parse_c25_region3(c25_region3_encoded(fields)),fields)
    def test_c25_max255_each_and_total(self):
        f=[b"x"*255,b"y"*255,b"z"*255]
        payload=c25_region3_encoded(f)
        self.assertEqual(len(payload),768)
        self.assertEqual(parse_c25_region3(payload),tuple(f))
    def test_c25_rejects_oversized_or_nonbytes(self):
        for fields in ([b"abc",b"a",b"x"*256],[b"x",b"y","z"],[b"x",b"y",None]):
            with self.subTest(fields=fields),self.assertRaises(PacketError):
                c25_region3_encoded(fields)
    def test_c25_requires_exact_three_fields(self):
        for fields in ([],[b"x"],[b"x"]*4,{},None):
            with self.subTest(fields=fields),self.assertRaises(PacketError):
                c25_region3_encoded(fields)
    def test_c25_truncation_all_offsets(self):
        full=c25_region3_encoded([b"abc",b"d",b"ef"])
        for i in range(len(full)):
            with self.subTest(i=i),self.assertRaises(PacketError):
                parse_c25_region3(full[:i])
    def test_c25_trailing_rejected(self):
        with self.assertRaises(PacketError):
            parse_c25_region3(b"\0\0\0\0")
    def test_c25_invalid_input_type(self):
        for x in ("abc",42,None):
            with self.assertRaises(PacketError):parse_c25_region3(x)
    def test_region3_writer_profile(self):
        self.assertEqual(c25_native_codec_for_region(3),"three-string8")
    def test_non_region3_empty_if_called_not_required_to_send(self):
        for i in (0,1,2,4,5,255):
            self.assertEqual(c25_native_codec_for_region(i),
                             "empty-body-if-called-no-known-producer")
    def test_region_invalid(self):
        for i in (-1,256,3.0,True,None):
            with self.assertRaises(PacketError):c25_native_codec_for_region(i)
    def test_native_region3_sequential_c10_then_c25(self):
        packets=native_world_send_profile(3,b"T0",(b"one",b"two",b"three"))
        self.assertEqual([p[0] for p in packets],[0x10,0x25])
        self.assertEqual(packets[0][1],b"T0")
        self.assertEqual(parse_c25_region3(packets[1][1]),(b"one",b"two",b"three"))
    def test_native_other_region_only_c10_proven(self):
        self.assertEqual(native_world_send_profile(0,b"T0"),[(0x10,b"T0")])
        self.assertEqual(native_world_send_profile(4,b"T0"),[(0x10,b"T0")])
    def test_non_region3_billing_data_is_not_native_producer(self):
        with self.assertRaises(PacketError):
            native_world_send_profile(0,b"T0",(b"a",b"b",b"c"))
    def test_region3_missing_fields_not_invented(self):
        with self.assertRaises(PacketError):
            native_world_send_profile(3,b"T0")
    def test_empty_string8_not_empty_c25_body(self):
        self.assertNotEqual(c25_region3_encoded([b"",b"",b""]),b"")
if __name__=="__main__":unittest.main()
