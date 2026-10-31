#!/usr/bin/env python3
"""A005: aggregate private DAT/MAP full u32 flags, never export game content."""
import argparse,hashlib,json,struct
from collections import Counter
from pathlib import Path
EXPECTED={
"Map0.dat":"dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761",
"Map1.dat":"8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b",
"Map2.dat":"5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb"}
def audit_archive_bytes(raw):
    if len(raw)<76:raise ValueError("short DAT")
    n,=struct.unpack_from("<I",raw)
    if not 2<=n<=200000 or 4+36*n>len(raw):raise ValueError("invalid slots")
    offsets=[struct.unpack_from("<I",raw,4+i*36)[0] for i in range(n)]
    if offsets[0]!=4+36*n or offsets[-1]!=len(raw) or any(a>b for a,b in zip(offsets,offsets[1:])):
        raise ValueError("offset or sentinel invalid")
    counts=Counter();total=0
    for i,(a,b) in enumerate(zip(offsets,offsets[1:])):
        d=memoryview(raw)[a:b]
        if len(d)<8:raise ValueError("short map header")
        w,h=d[6],d[7]
        if not w or not h:raise ValueError("zero width/height")
        tile_start=8+((w+1)//2)*((h+3)//4)*2
        cursor=tile_start+w*h*10
        if cursor>len(d):raise ValueError("truncated tiles")
        for j in range(w*h):
            f,=struct.unpack_from("<I",d,tile_start+j*10+6)
            counts[f]+=1
        total+=w*h
        for stride in (7,8,16):
            if cursor+4>len(d):raise ValueError("truncated record count")
            k,=struct.unpack_from("<I",d,cursor)
            cursor+=4+k*stride
            if cursor>len(d):raise ValueError("truncated tail")
        if cursor!=len(d):raise ValueError("invalid map EOF")
    return {"maps":n-1,"tiles":total,"flags_u32":{str(x):counts[x] for x in sorted(counts)},
            "bit0_tiles":sum(v for k,v in counts.items() if k&1),
            "bit4_tiles":sum(v for k,v in counts.items() if k&16),
            "bit9_tiles":sum(v for k,v in counts.items() if k&512)}
def audit_file(path,require_sha=False):
    p=Path(path);b=p.read_bytes();digest=hashlib.sha256(b).hexdigest()
    if require_sha and digest!=EXPECTED.get(p.name):
        raise ValueError("original release/version mismatch: "+p.name)
    return {"filename":p.name,"sha256":digest,**audit_archive_bytes(b)}
if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("archives",nargs="+",type=Path)
    cli.add_argument("--verify-original-sha",action="store_true")
    a=cli.parse_args()
    results=[audit_file(p,a.verify_original_sha) for p in a.archives]
    counts=Counter()
    for r in results:counts.update({int(k):v for k,v in r["flags_u32"].items()})
    print(json.dumps({"files":results,"total_maps":sum(x["maps"] for x in results),
      "total_tiles":sum(x["tiles"] for x in results),
      "combined_flags":{str(x):counts[x] for x in sorted(counts)},
      "tile_flags_meaning":"bit4 observed in line test; exact walking collision mask unverified",
      "assets_shared":False,"native_client_E2E":"not-run"},indent=2))
