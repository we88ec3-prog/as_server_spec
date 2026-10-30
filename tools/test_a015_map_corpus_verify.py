#!/usr/bin/env python3
"""Synthetic tests for A-015 MAP corpus verifier: no game assets required."""
import struct
import unittest

from a015_map_corpus_verify import parse_map, scan_archive


def map4():
    return struct.pack("<HHHBB", 0, 0, 0, 4, 4) + bytes(4 + 16 * 10) + struct.pack("<III", 0, 0, 0)


class MapCorpusTest(unittest.TestCase):
    def test_map(self):
        self.assertEqual(parse_map(map4())["tile_records"], 16)

    def test_truncated_and_extra_bytes(self):
        for bad in (map4()[:-1], map4()[:15], map4() + b"\x00"):
            with self.assertRaises(ValueError):
                parse_map(bad)

    def test_archive(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        body = map4()
        first = 4 + 2 * 36
        data = (struct.pack("<I", 2) +
                struct.pack("<I32s", first, b"00000.map") +
                struct.pack("<I32s", first + len(body), b"") + body)
        with TemporaryDirectory() as folder:
            path = Path(folder) / "Map0.dat"
            path.write_bytes(data)
            self.assertEqual(scan_archive(path)["map_member_count"], 1)
            path.write_bytes(data[:-1])
            with self.assertRaises(ValueError):
                scan_archive(path)


if __name__ == "__main__":
    unittest.main()
