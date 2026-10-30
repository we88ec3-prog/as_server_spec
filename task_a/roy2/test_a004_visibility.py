"""A-004 synthetic fixtures only, no original game assets."""
import struct
import unittest
from a004_visibility import (PacketError,parse_s06,parse_s11,parse_s0e,parse_s0b,
                              parse_s33_zero_flags,VisibilityProjection)
def make_s33(name="測試",oid=0x12345678):
    encoded=name.encode("cp950")
    b=bytearray(34)
    struct.pack_into(">HHBI",b,0,10,20,3,oid)
    b[9]=1
    b[12:14]=b"\x00\x03"
    b[14]=2
    b[15:18]=b"\x11\x22\x33"
    b[30:33]=b"\xff\x00\xff"
    return bytes(b)+bytes([len(encoded)])+encoded+b"\x00\x00\x00\x00\x00\x64\x00"
class VisibilityTests(unittest.TestCase):
    def test_s06(self):
        self.assertEqual(parse_s06(bytes.fromhex("12345678000a0014"))["field_u16_b"],20)
    def test_s11(self):
        self.assertEqual(parse_s11(bytes.fromhex("1234567807"))["direction"],7)
    def test_s0e(self):
        self.assertEqual(parse_s0e(bytes.fromhex("12345678"))["opaque_u32"],0x12345678)
    def test_s0b_self_ack_has_no_object_id(self):
        self.assertEqual(parse_s0b(bytes.fromhex("000b000aff")),
                         {"x":11,"y":10,"sequence_low7":127,"status_bit7":True})
    def test_s33_profile_CP950(self):
        b=make_s33()
        self.assertEqual(len(b),46)
        p=parse_s33_zero_flags(b)
        self.assertEqual((p["x"],p["y"],p["facing"],p["object_id"],p["name"]),
                         (10,20,3,0x12345678,"測試"))
    def test_s33_negative(self):
        b=make_s33()
        invalid=[b[:-1],b+b"x",b[:34]+b"\x00"+b[35:],
                 b[:26]+b"\x00\x00\x10\x00"+b[30:]]
        for item in invalid:
            with self.assertRaises(PacketError): parse_s33_zero_flags(item)
    def test_fixed_packet_length_guards(self):
        for fn,good in ((parse_s06,b"\0"*8),(parse_s11,b"\0"*5),
                        (parse_s0e,b"\0"*4),(parse_s0b,b"\0"*5)):
            for item in (good[:-1],good+b"x"):
                with self.assertRaises(PacketError):fn(item)
    def test_projection_epoch_replay(self):
        p=parse_s33_zero_flags(make_s33())
        w=VisibilityProjection("map1",10,99)
        self.assertTrue(w.spawn_or_refresh(10,p))
        self.assertTrue(w.spawn_or_refresh(10,p))
        self.assertEqual(len(w.humans),1)
        self.assertFalse(w.spawn_or_refresh(10,dict(p,object_id=99)))
        self.assertTrue(w.remote_position(10,p["object_id"],11,20))
        self.assertTrue(w.remote_direction(10,p["object_id"],4))
        self.assertFalse(w.remote_position(9,p["object_id"],1,1))
        self.assertTrue(w.remove(10,p["object_id"]))
        self.assertFalse(w.remove(10,p["object_id"]))
        self.assertFalse(w.spawn_or_refresh(10,p))
        w.reenter("map2",11)
        self.assertFalse(w.remote_direction(10,p["object_id"],2))
        self.assertTrue(w.spawn_or_refresh(11,p))
    def test_epoch_must_advance(self):
        w=VisibilityProjection("map1",1,3)
        with self.assertRaises(ValueError):w.reenter("map2",1)
        self.assertFalse(w.spawn_or_refresh(0,{"object_id":5}))
if __name__=="__main__":unittest.main()
