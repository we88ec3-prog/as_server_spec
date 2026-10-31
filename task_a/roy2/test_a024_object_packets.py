"""A-024 synthetic decoded object projection: test native S07 row cases and update/event packet splits."""
import unittest
from a024_object_packets import (
    PacketError, draw_objects_s07, decode_s3c_show_object_info,
    decode_s34_info_reply, decode_s62_add_action,
    decode_s63_remove_action, decode_s29_effect,
)
be16 = lambda n: n.to_bytes(2, "big")
be32 = lambda n: n.to_bytes(4, "big")

def row(kind, tail=b"", obj=0x12345678):
    return be16(31)+be16(29)+bytes([kind])+be32(obj)+be16(0x5678)+tail

def type124_tail(flags=0, text=b"N", opt=b""):
    return bytes([1,2,3,4,5])+be16(0x789a)+be32(flags)+opt+bytes([len(text)])+text

class NativeObjectPackets(unittest.TestCase):
    def test_s07_zero_rows(self):
        self.assertEqual(draw_objects_s07(b"\x00\x00")["rows"], [])

    def test_s07_type_1_2_4_variants(self):
        for kind in (1,2,4):
            packet=be16(1)+row(kind,type124_tail(0,b"AB"))
            obj=draw_objects_s07(packet)["rows"][0]
            self.assertEqual(obj["kind"],kind)
            self.assertEqual(obj["name_raw_cp950"],b"AB")
            self.assertEqual(obj["object_key_candidate"],0x12345678)

    def test_s07_type124_optional_flags_in_native_order(self):
        extra=b"\x11\x22\x33\x44"+be16(0x5566)
        obj=draw_objects_s07(be16(1)+row(4,type124_tail(0x13,b"X",extra)))["rows"][0]
        self.assertEqual(obj["optional_u8x3"],[0x11,0x22,0x33])
        self.assertEqual(obj["optional_u8"],0x44)
        self.assertEqual(obj["optional_u16"],0x5566)

    def test_s07_type3_five_and_string(self):
        obj=draw_objects_s07(be16(1)+row(3,b"\x01\x02\x03\x04\x05\x02Hi"))["rows"][0]
        self.assertEqual(obj["variant5"],[1,2,3,4,5])
        self.assertEqual(obj["name_raw_cp950"],b"Hi")

    def test_s07_5_to_12_no_tail(self):
        data=be16(8)+b"".join(row(k) for k in range(5,13))
        self.assertEqual([r["kind"] for r in draw_objects_s07(data)["rows"]], list(range(5,13)))

    def test_s07_type13_text(self):
        self.assertEqual(draw_objects_s07(be16(1)+row(13,b"\x03NPC"))["rows"][0]["name_raw_cp950"],b"NPC")

    def test_s07_type14_fixed(self):
        obj=draw_objects_s07(be16(1)+row(14,b"\x01\x02"+be16(255)))["rows"][0]
        self.assertEqual(obj["variant_u16"],255)

    def test_s07_multirecord_mixed_exact(self):
        b=be16(4)+row(1,type124_tail(0,b""))+row(5)+row(13,b"\x02AB")+row(14,b"\x04\x05"+be16(6))
        self.assertEqual(draw_objects_s07(b)["count"],4)

    def test_s07_truncated_at_every_offset(self):
        b=be16(1)+row(1,type124_tail(0x13,b"Hi",b"\x01\x02\x03\x04"+be16(10)))
        for n in range(len(b)):
            with self.subTest(n=n), self.assertRaises(PacketError):
                draw_objects_s07(b[:n])

    def test_s07_illegal_type_count_and_trailing(self):
        for b in (be16(1)+row(0),be16(1)+row(15),be16(0)+b"X",be16(2)+row(5)):
            with self.assertRaises(PacketError):draw_objects_s07(b)
        with self.assertRaises(PacketError):
            draw_objects_s07(be16(1025),max_records=1024)

    def test_s07_string_is_raw_cp_bytes(self):
        raw=b"\xa4\x40"
        obj=draw_objects_s07(be16(1)+row(13,b"\x02"+raw))["rows"][0]
        self.assertEqual(obj["name_raw_cp950"],raw)

    def test_s3c_show_info_fixed7(self):
        self.assertEqual(decode_s3c_show_object_info(be32(9)+b"\x01\x02\x03")["options"],[1,2,3])
        with self.assertRaises(PacketError):decode_s3c_show_object_info(be32(9))

    def test_s34_info_subtype6(self):
        b=b"\x06"+be32(10)+b"\x00"+be16(11)+b"\x01"+be32(12)+b"\x02\x03\x04"
        self.assertEqual(decode_s34_info_reply(b)["subtype6"]["field_u32"],12)
        with self.assertRaises(PacketError): decode_s34_info_reply(b[:-1])

    def test_s34_dynamic_subtype11_refused(self):
        with self.assertRaises(PacketError): decode_s34_info_reply(b"\x0b"+be32(7)+b"\x00")
        self.assertEqual(decode_s34_info_reply(b"\x01"+be32(7)+b"\x00")["flags"],0)

    def test_s62_add_action_four_strings(self):
        b=b"\x01\x02"+be16(3)+b"\x04\x05\x06"
        b+=b"\x01A\x02BC\x00\x01D"
        b+=b"\x07"+be16(8)+b"\x09"
        result=decode_s62_add_action(b)
        self.assertEqual(result["texts_raw_cp950"],[b"A",b"BC",b"",b"D"])
        with self.assertRaises(PacketError):decode_s62_add_action(b[:-1])

    def test_s63_remove_action(self):
        self.assertEqual(decode_s63_remove_action(b"\x05\x06"),{"tag_a":5,"tag_b":6})
        with self.assertRaises(PacketError):decode_s63_remove_action(b"\x05\x06\x07")

    def test_s29_effect_fixed13(self):
        b=be32(1)+be32(2)+be16(3)+be16(4)+b"\x05"
        self.assertEqual(decode_s29_effect(b)["kind_or_flags"],5)
        with self.assertRaises(PacketError):decode_s29_effect(b[:-1])

if __name__ == "__main__":
    unittest.main()
