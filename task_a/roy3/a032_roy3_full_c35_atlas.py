#!/usr/bin/env python3
"""A032 roy3: full 494 native MAP C35 atlas, content identity and guarded pending-map comparison.

Loads SHA-pinned Asgard.exe/Map0,1,2.dat without embedding copyright asset bytes.
Imports predecessor's observed original C35 normalization from a032_c35_probe.
No original Windows Client socket/GUI, spawn, or walkability assertion.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from a032_c35_probe import MAP_SHAS, FormatError, checksum, crc_table, members

ARCHIVE_COUNTS={"Map0.dat":288,"Map1.dat":184,"Map2.dat":22}
EXPECTED_MAP_COUNT=494
EXPECTED_UNIQUE_CONTENT=330
EXPECTED_UNIQUE_C35=330
EXPECTED_DUPLICATE_CLUSTERS=33
EXPECTED_PAIR_ATLAS_SHA256="8a0ba7ebe767385db7296de1ca0c3b999aa620e05e6ab1793db0e640f30c375a"

def build_atlas(exe_path, map_dir, *, strict=True):
    """Original archive bytes -> one row per member, sorted by numerical map_ref."""
    table=crc_table(Path(exe_path).read_bytes())
    seen=set()
    entries=[]
    for archive,expected_count in ARCHIVE_COUNTS.items():
        raw=Path(map_dir,archive).read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=MAP_SHAS[archive]:
            raise FormatError("original archive hash mismatch: "+archive)
        found=0
        for name,member in members(raw):
            ref=int(name[:5])
            if ref in seen or ref//10000!=int(archive[3]):
                raise FormatError("duplicate or wrong archive map_ref "+name)
            seen.add(ref)
            data=checksum(member,table)
            entries.append(dict(map_ref=ref,archive=archive,map_name=name,
                payload_sha256=hashlib.sha256(member).hexdigest(),
                width=data["width_tiles"],height=data["height_tiles"],
                header=data["header_word"],checksum=data["checksum"],
                c35_body_hex=data["c35_be_u16_pair_hex"],
                tail_record_counts=data["tail_record_counts"]))
            found+=1
        if strict and found!=expected_count:
            raise FormatError(f"wrong number of {archive} maps: {found} vs {expected_count}")
    entries.sort(key=lambda v:v["map_ref"])
    if strict and len(entries)!=EXPECTED_MAP_COUNT:
        raise FormatError("missing MAP members")
    pair_groups=defaultdict(list);payload_groups=defaultdict(list)
    for row in entries:
        pair_groups[row["c35_body_hex"]].append(row["map_ref"])
        payload_groups[row["payload_sha256"]].append(row["map_ref"])
    pair_digest=hashlib.sha256("".join(
        f'{row["map_ref"]:05d}:{row["c35_body_hex"]}\n' for row in entries
        ).encode("ascii")).hexdigest()
    pair_collisions={}
    for pair,ids in pair_groups.items():
        hashes={row["payload_sha256"] for row in entries if row["map_ref"] in ids}
        if len(hashes)>1:
            pair_collisions[pair]=ids
    clusters=[ids for ids in pair_groups.values() if len(ids)>1]
    summary={
      "original_exe_and_archives_sha_pinned":True,
      "map_count":len(entries),
      "map_count_by_archive":dict(Counter(x["archive"] for x in entries)),
      "distinct_payload_sha256":len(payload_groups),
      "distinct_c35_pair":len(pair_groups),
      "duplicate_c35_clusters":len(clusters),
      "excess_repeated_refs":len(entries)-len(pair_groups),
      "largest_pair_cluster":max((len(x) for x in clusters),default=1),
      "distinct_content_sharing_same_c35":len(pair_collisions),
      "map_ref_to_c35_digest_sha256":pair_digest,
      "native_c35_capture":"not-run","native_GUI_spawn_walk":"not-run",
      "c35_pair_identifies_map_ref":False
    }
    if strict and (len(entries),len(payload_groups),len(pair_groups),len(clusters),pair_digest)!=(494,330,330,33,EXPECTED_PAIR_ATLAS_SHA256):
        raise FormatError("original 494 MAP atlas differs from pinned fixture")
    return {"summary":summary,"entries":entries}

@dataclass(frozen=True)
class PendingMap:
    """Server-designed pending-map binding; none of these fields are in C35 body."""
    map_ref:int
    map_sha256:str
    c35_body_hex:str
    generation:int

def accept_c35_for_pending(pending,*,active_map_ref,active_generation,active_payload_sha256,received_body):
    """Fail-closed Server-designed guard against duplicate-C35 map identity confusion.

    The map_ref and generation are Server-tracked session context, NOT client C35 fields.
    """
    if not isinstance(pending,PendingMap):return False
    if not isinstance(received_body,(bytes,bytearray)) or len(received_body)!=4:return False
    return (
        active_map_ref==pending.map_ref
        and active_generation==pending.generation
        and active_payload_sha256==pending.map_sha256
        and bytes(received_body).hex().upper()==pending.c35_body_hex
    )

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--exe",type=Path,required=True)
    ap.add_argument("--map-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,help="optional metadata JSON manifest, no map bytes")
    args=ap.parse_args()
    atlas=build_atlas(args.exe,args.map_dir)
    if args.output:
        args.output.write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(atlas["summary"],ensure_ascii=False,indent=2))
if __name__=="__main__":main()
