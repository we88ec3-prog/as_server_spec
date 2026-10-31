"""A010 synthetic decoded-body test suite; original native GUI E2E not attempted."""
import unittest
from a010_skill_codec import (
    SkillPacketError, Reader, c4d_start_cast_spell, c56_cast_spell,
    s52_cast_spell, s48_cancel_cast_spell, s2c_add_lasting_spell,
    s2d_remove_lasting_spell, DesignedLastingSpellLedger,
)


def be16(n):
    return n.to_bytes(2, "big")


def be32(n):
    return n.to_bytes(4, "big")


def s2c_fixture(name=b"test", word=0x1234):
    return (
        be32(0x11223344) + b"\x05" + be16(word) + b"\x07"
        + bytes([len(name)]) + name + b"\x09"
        + be32(0x55667788) + be32(0x99aabbcc)
    )


class A010SkillCodecTests(unittest.TestCase):
    def test_c4d_native_be_u16(self):
        self.assertEqual(c4d_start_cast_spell(0x1234), b"\x12\x34")

    def test_c4d_u16_limits(self):
        self.assertEqual(c4d_start_cast_spell(0), b"\0\0")
        self.assertEqual(c4d_start_cast_spell(65535), b"\xff\xff")

    def test_c4d_invalid(self):
        for x in (-1, 65536, "3", True, 1.0):
            with self.subTest(x=x), self.assertRaises(SkillPacketError):
                c4d_start_cast_spell(x)

    def test_c56_native_u8(self):
        self.assertEqual(c56_cast_spell(0), b"\0")
        self.assertEqual(c56_cast_spell(255), b"\xff")

    def test_c56_invalid(self):
        for x in (-1, 256, None, True):
            with self.subTest(x=x), self.assertRaises(SkillPacketError):
                c56_cast_spell(x)

    def test_s52_read_5_bytes(self):
        self.assertEqual(s52_cast_spell(b"\x12\x34\x56\x78\x9a"),
                         dict(opaque_u32=0x12345678, opaque_u8=154))

    def test_s48_read_4_bytes(self):
        self.assertEqual(s48_cancel_cast_spell(be32(0xfedcba98)),
                         dict(opaque_u32=0xfedcba98))

    def test_s2d_read_4_bytes(self):
        self.assertEqual(s2d_remove_lasting_spell(be32(1)),
                         dict(opaque_u32=1))

    def test_s2c_full_wire_order(self):
        r = s2c_add_lasting_spell(s2c_fixture())
        self.assertEqual(
            r,
            dict(opaque_u32_a=0x11223344, opaque_u8_a=5,
                 opaque_u16=0x1234, opaque_u8_b=7, name_bytes=b"test",
                 opaque_u8_c=9, opaque_u32_b=0x55667788,
                 opaque_u32_c=0x99aabbcc),
        )

    def test_s2c_empty_string8(self):
        self.assertEqual(s2c_add_lasting_spell(s2c_fixture(b""))["name_bytes"], b"")

    def test_s2c_max255_string8(self):
        self.assertEqual(len(s2c_add_lasting_spell(s2c_fixture(b"a" * 255))["name_bytes"]), 255)

    def test_s2c_cp950_bytes_preserved(self):
        self.assertEqual(s2c_add_lasting_spell(s2c_fixture(bytes.fromhex("a4a4")))["name_bytes"],
                         bytes.fromhex("a4a4"))

    def test_s2c_string_length_truncated(self):
        raw = s2c_fixture(b"hi")
        # Force name byte count longer than actual named part.
        corrupted = raw[:8] + b"\xff" + raw[9:]
        with self.assertRaises(SkillPacketError):
            s2c_add_lasting_spell(corrupted)

    def test_s2c_truncated_all_offsets(self):
        full = s2c_fixture()
        for k in range(len(full)):
            with self.subTest(k=k), self.assertRaises(SkillPacketError):
                s2c_add_lasting_spell(full[:k])

    def test_fixed_length_extra_and_short_rejected(self):
        for parser, payload in [
            (s52_cast_spell, be32(2)+b"\x03"),
            (s48_cancel_cast_spell, be32(2)),
            (s2d_remove_lasting_spell, be32(3)),
        ]:
            for bad in (payload[:-1], payload + b"\x00"):
                with self.subTest(parser=parser.__name__,bad=bad), self.assertRaises(SkillPacketError):
                    parser(bad)

    def test_s2c_trailing_rejected(self):
        with self.assertRaises(SkillPacketError):
            s2c_add_lasting_spell(s2c_fixture()+b"\x00")

    def test_reader_input_types(self):
        for value in (None, "hi", 42):
            with self.assertRaises(SkillPacketError):
                Reader(value)

    def test_ledger_world_epoch_and_duplicate_add(self):
        led = DesignedLastingSpellLedger()
        led.enter_world(5)
        self.assertTrue(led.add(5, 3, "buff-a"))
        self.assertTrue(led.add(5, 3, "buff-a"))
        self.assertEqual(led.count(), 1)
        self.assertFalse(led.add(4, 7, "late"))
        self.assertEqual(led.count(), 1)

    def test_ledger_remove_and_relogin(self):
        led=DesignedLastingSpellLedger()
        led.enter_world(1)
        led.add(1, 17, b"state")
        led.enter_world(2)
        self.assertFalse(led.remove(1,17))
        self.assertEqual(led.count(),0)
        led.add(2,17,b"new")
        self.assertTrue(led.remove(2,17))
        self.assertTrue(led.remove(2,17))
        self.assertEqual(led.count(),0)


if __name__ == "__main__":
    unittest.main()
