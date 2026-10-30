#!/usr/bin/env python3
"""Synthetic A-015 validation. No original game data is bundled."""
import io
import json
import struct
import tempfile
import unittest
import zlib
from contextlib import redirect_stdout
from pathlib import Path
from a015_content_probe import parse_map, parse_archive, parse_script, main

def map4():
    # 4x4 grid -> 4 bytes of block data + 16*10B tiles + 3 empty tails.
    return (struct.pack("<HHHBB", 1, 2, 3, 4, 4) +
            b"\x00" * 4 + b"\x00" * 160 + struct.pack("<III", 0, 0, 0))

def archive(member):
    start = 4 + 36 * 2
    return (struct.pack("<I", 2) +
            struct.pack("<I32s", start, b"00000.map") +
            struct.pack("<I32s", start + len(member), b"") + member)

class ContentProbeTests(unittest.TestCase):
    def test_map_and_archive(self):
        self.assertEqual(parse_map(map4())["tiles"], 16)
        doc = parse_archive(archive(map4()))
        self.assertEqual(doc["slots_including_sentinel"], 2)
        self.assertEqual(doc["map_members"][0]["width"], 4)

    def test_reject_short_and_invalid_member(self):
        for thunk in (lambda: parse_map(map4()[:-1]),
                      lambda: parse_archive(archive(map4())[:-1]),
                      lambda: parse_archive(archive(map4()[:-1]))):
            with self.assertRaises(ValueError):
                thunk()

    def test_script(self):
        xml = '<script><function name="Main">test</function></script>'
        s = xml.encode("utf-16le")
        blob = zlib.compress(b"\x00\x01\x00\x00" +
                             struct.pack(">H", len(s) // 2) + s)
        self.assertEqual(parse_script(blob)["function_names"], ["Main"])
        with self.assertRaises(ValueError):
            parse_script(b"bad")

if __name__ == "__main__":
    unittest.main()
