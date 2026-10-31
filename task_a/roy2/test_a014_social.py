#!/usr/bin/env python3
"""Only synthetic social codec / permission tests, no native protocol E2E."""
import unittest
from a014_social import (c0e_say, c19_whisper, c2e_group,
                         decode_c19, MembershipModel)

class SocialContractTests(unittest.TestCase):
    def test_say_cp950_bytes(self):
        self.assertEqual(c0e_say(0, "測試"), bytes.fromhex("0004b4fab8d5"))
        self.assertEqual(len(c0e_say(1, "測試")), 6)

    def test_whisper_roundtrip(self):
        raw = c19_whisper(2, "甲", "測試")
        self.assertEqual(decode_c19(raw),
                         {"type_id": 2, "recipient": "甲", "text": "測試"})

    def test_group_known_branch(self):
        self.assertEqual(c2e_group(0, "甲"), b"\x00\x02\xa5\xd2")
        self.assertEqual(c2e_group(1, "A", 2, 0), b"\x01\x01A\x01\x00")
        with self.assertRaises(ValueError): c2e_group(5, "A")

    def test_malformed_text_or_excess_bytes(self):
        for b in (b"", b"\x01", b"\x01\x00", b"\x01\x01A",
                  c19_whisper(1, "A", "B") + b"x"):
            with self.assertRaises(ValueError): decode_c19(b)
        for text in ("", "A" * 256, "😊"):
            with self.assertRaises((ValueError, UnicodeError)):
                c0e_say(0, text)

    def test_stale_generation_and_wrong_permissions(self):
        g = MembershipModel(["a", "b", "c"], "a")
        self.assertFalse(g.kick("b", "c", 0))
        self.assertFalse(g.kick("a", "c", 0, False))
        self.assertFalse(g.kick("a", "c", 1))
        self.assertTrue(g.kick("a", "c", 0))
        self.assertFalse(g.kick("a", "c", 0))
        self.assertEqual(g.members, {"a", "b"})
        self.assertEqual(g.route_group("c", ["a", "b"]), set())
        self.assertEqual(g.route_group("a", ["a"]), {"a"})

if __name__ == "__main__":
    unittest.main()
