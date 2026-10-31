"""A-009 decoded-body synthetic tests; separate from native Client GUI E2E."""
import unittest
from a009_combat_codec import c13_attack,s5f_die,s13_damage_effect,s3d_battle_simple
U16=lambda n:n.to_bytes(2,"big")
U32=lambda n:n.to_bytes(4,"big")
class CombatTest(unittest.TestCase):
    def test_attack_endianness(self):
        self.assertEqual(c13_attack(0x12345678),b"\x12\x34\x56\x78")
    def test_attack_bad(self):
        for n in (-1,2**32,"x"):
            with self.assertRaises(ValueError): c13_attack(n)
    def test_die_be_u32(self):
        self.assertEqual(s5f_die(U32(0xabcdef12))["object_opaque"],0xabcdef12)
    def test_die_rejects_extra(self):
        for b in (b"",b"\0"*3,b"\0"*5):
            with self.assertRaises(ValueError): s5f_die(b)
    def test_damage_base(self):
        b=U32(0x10203040)+U32(0x50607080)+b"\x04"+U16(0x1234)+U16(0x9876)+b"\0"
        x=s13_damage_effect(b)
        self.assertEqual(len(b),14)
        self.assertEqual((x["field34_u16"],x["field30_u16"]),(0x1234,0x9876))
    def test_damage_split_bits_do_not_read_extra(self):
        b=U32(0x12345678)+U32(0x9abcdef0)+b"\x07"+U16(2)+U16(3)+b"\x18"
        x=s13_damage_effect(b)
        self.assertEqual(x["opaque_1_split"],[0x1234,0x5678])
        self.assertEqual(x["opaque_2_split"],[0x9abc,0xdef0])
    def test_damage_optional(self):
        b=U32(1)+U32(2)+b"\0"+U16(3)+U16(4)+b"\x01"
        b+=b"\x05"+U16(6)+U16(7)+U16(8)+b"\x09"+U32(10)+U32(11)+b"\x0c"
        self.assertEqual(len(b),31)
        self.assertEqual(s13_damage_effect(b)["extra"]["opaque_u32"],[10,11])
    def test_damage_cut_each_byte(self):
        b=U32(1)+U32(2)+b"\0"+U16(3)+U16(4)+b"\x01"+b"\x05"+U16(6)+U16(7)+U16(8)+b"\x09"+U32(10)+U32(11)+b"\x0c"
        for n in range(len(b)):
            with self.subTest(n=n),self.assertRaises(ValueError): s13_damage_effect(b[:n])
    def test_damage_extra_rejected(self):
        with self.assertRaises(ValueError): s13_damage_effect(b"\0"*15)
    def test_battle_no_payload(self):
        for subtype in (1,8,12):
            self.assertEqual(s3d_battle_simple(bytes([subtype]))["subtype"],subtype)
    def test_battle_one_u8(self):
        for subtype in (4,5,6,10):
            self.assertEqual(s3d_battle_simple(bytes([subtype,42]))["param_u8"],42)
    def test_battle_two_u8(self):
        self.assertEqual(s3d_battle_simple(bytes([7,9,10]))["params_u8"],[9,10])
    def test_battle_two_u32(self):
        self.assertEqual(s3d_battle_simple(b"\x0f"+U32(5)+U32(6))["params_u32"],[5,6])
    def test_battle_subtype3(self):
        b=b"\x03\x02AB"+U32(10)+b"\x09"+bytes(range(26))
        x=s3d_battle_simple(b)
        self.assertEqual(x["text_raw"],b"AB")
        self.assertEqual(x["array26"][-1],25)
    def test_battle_bad_variants(self):
        for b in (b"",b"\x02",b"\x07\x09",b"\x0f"+U32(1),b"\x01\x00",b"\x03\x02A"):
            with self.assertRaises(ValueError):s3d_battle_simple(b)
if __name__=="__main__": unittest.main()
