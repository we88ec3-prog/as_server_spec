#!/usr/bin/env python3
"""Verify Map0/Map1/Map2 indexed archives and embedded MAP layouts, without asset export.

Usage: python tools/a015_map_corpus_verify.py Map0.dat Map1.dat Map2.dat --json private-metadata.json
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_map(data):
    if len(data) < 8:
        raise ValueError("MAP header truncated")
    h0, h1, h2, w, h = struct.unpack_from("<HHHBB", data, 0)
    if not w or not h:
        raise ValueError("invalid MAP dimensions")
    blocks = ((w + 1) // 2) * ((h + 3) // 4) * 2
    pos = 8 + blocks + 10 * w * h
    if pos + 12 > len(data):
        raise ValueError("MAP grid/trailing counters truncated")
    counts = []
    for stride in (7, 8, 16):
        if pos + 4 > len(data):
            raise ValueError("MAP counter truncated")
        n = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        if n > (len(data) - pos) // stride:
            raise ValueError("MAP tail out of bounds")
        counts.append(n)
        pos += stride * n
    if pos != len(data):
        raise ValueError("MAP leftover bytes")
    return {
        "sha256": sha256(data),
        "size": len(data),
        "header_u16_raw": [h0, h1, h2],
        "width": w,
        "height": h,
        "block_bytes": blocks,
        "tile_records": w * h,
        "tail_records_7_8_16": counts,
        "includes_31_29": w > 31 and h > 29,
    }


def scan_archive(path):
    blob = path.read_bytes()
    if len(blob) < 40:
        raise ValueError("archive too short")
    n = struct.unpack_from("<I", blob, 0)[0]
    if n <= 1 or n > 200000 or 4 + 36 * n > len(blob):
        raise ValueError("archive slot count invalid")
    offsets = [struct.unpack_from("<I", blob, 4 + 36 * i)[0]
               for i in range(n)]
    if offsets[0] != 4 + n * 36 or offsets[-1] != len(blob):
        raise ValueError("archive index/EOF sentinel mismatch")
    if any(a > b for a, b in zip(offsets, offsets[1:])):
        raise ValueError("nonmonotonic archive offsets")
    maps = []
    seen = set()
    for i in range(n - 1):
        raw = blob[8 + 36 * i:40 + 36 * i].split(b"\x00", 1)[0]
        try:
            name = raw.decode("ascii")
        except UnicodeError as e:
            raise ValueError("non-ASCII MAP filename") from e
        if not re.fullmatch(r"[0-9]{5}\.map", name, re.IGNORECASE):
            raise ValueError("invalid member name: " + repr(name))
        if name in seen:
            raise ValueError("duplicate MAP filename: " + name)
        seen.add(name)
        parsed = parse_map(memoryview(blob)[offsets[i]:offsets[i + 1]])
        parsed["name"] = name
        maps.append(parsed)
    return {
        "file": path.name,
        "file_size": len(blob),
        "sha256": sha256(blob),
        "slots_including_eof_sentinel": n,
        "map_member_count": len(maps),
        "total_tail_records_7_8_16": [
            sum(m["tail_records_7_8_16"][j] for m in maps)
            for j in range(3)
        ],
        "coordinate_31_29_in_bounds": sum(m["includes_31_29"] for m in maps),
        "maps": maps,
    }


def summarize(paths):
    archives = [scan_archive(Path(p)) for p in paths]
    hashes = defaultdict(list)
    for archive in archives:
        for m in archive["maps"]:
            hashes[m["sha256"]].append(archive["file"] + ":" + m["name"])
    duplicate_groups = [sorted(x) for x in hashes.values() if len(x) > 1]
    duplicate_groups.sort(key=lambda x: (-len(x), x))
    return {
        "schema_version": 1,
        "archives": [{k: v for k, v in a.items() if k != "maps"}
                     for a in archives],
        "map_members": sum(a["map_member_count"] for a in archives),
        "unique_payloads": len(hashes),
        "alias_entries_same_bytes": sum(len(x) - 1 for x in duplicate_groups),
        "duplicate_groups": len(duplicate_groups),
        "cross_archive_duplicate_groups": sum(
            len({x.split(":")[0] for x in g}) > 1 for g in duplicate_groups),
        "coordinate_31_29_in_bounds": sum(
            a["coordinate_31_29_in_bounds"] for a in archives),
        "duplicate_group_examples": duplicate_groups[:4],
        "raw_assets_exported": False,
        "client_resource_same_release": "unverified",
        "c35_structured_checksum": "unknown",
        "tutorial_map_id": "unknown",
        "recruiter_npc_id": "unknown",
        "note": "Map dimensions and identical bytes do not prove spawn, NPC identity or gameplay semantics.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map_archives", nargs=3)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    try:
        report = summarize(args.map_archives)
        serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        print(serialized, end="")
        if args.json:
            args.json.write_text(serialized, encoding="utf-8")
    except (OSError, ValueError, struct.error) as exc:
        print("MAP validation FAILED: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
