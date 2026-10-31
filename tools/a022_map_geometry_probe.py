#!/usr/bin/env python3
"""A022 offline probe, corrected via validated Roy2 offset-first DAT reader."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"task_a"/"roy2"))
from a015_map_coordinate import audit
def main(paths):
    out=[audit(p,verify_sha=True) for p in paths]
    if sum(x["maps"] for x in out)!=494 or sum(x["tiles"] for x in out)!=7701805:
        raise ValueError("Unexpected MAP release or bad indexed container")
    print(json.dumps({"valid_maps":494,"tiles":7701805,"archives":{r["file"]:r["maps"] for r in out},"roy1_old_plus_four_offset":"rejected","walkability":"unknown","native_e2e":"not-run"},ensure_ascii=False))
if __name__=="__main__":
    main(sys.argv[1:] or [str(Path("/mnt/data")/x) for x in ("Map0.dat","Map1.dat","Map2.dat")])
