#!/usr/bin/env python3
"""A-015 local metadata-only DAT/MAP/Script probe. No asset extraction or export."""
import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

MAX_FILE = 512 * 1024 * 1024
MAX_MEMBER = 64 * 1024 * 1024
MAX_COUNT = 200000

def sha(b):
    return hashlib.sha256(b).hexdigest()

def parse_map(b):
    if len(b) < 8: raise ValueError("truncated MAP header")
    h0, h1, h2 = struct.unpack_from("<HHH", b, 0)
    w, h = b[6], b[7]
    if w == 0 or h == 0: raise ValueError("zero width/height")
    block = ((w + 1) // 2) * ((h + 3) // 4) * 2
    pos = 8 + block + 10 * w * h
    counts = []
    for stride in (7, 8, 16):
        if pos + 4 > len(b): raise ValueError("MAP count truncated")
        n = struct.unpack_from("<I", b, pos)[0]
        if n > MAX_COUNT or n * stride > len(b) - pos - 4:
            raise ValueError("MAP tail exceeds EOF/limit")
        counts.append(n)
        pos += 4 + n * stride
    if pos != len(b): raise ValueError("MAP trailing bytes")
    return dict(width=w, height=h, header_u16_raw=[h0,h1,h2],
                block_bytes=block, tiles=w*h, tail_counts_7_8_16=counts,
                collision_semantics="unknown", npc_spawn="unknown", eof_ok=True)

def parse_archive(b):
    if len(b) < 40: raise ValueError("truncated DAT archive")
    n = struct.unpack_from("<I", b)[0]
    if n < 1 or n > MAX_COUNT or 4 + n * 36 > len(b):
        raise ValueError("DAT slot count invalid")
    offsets = [struct.unpack_from("<I", b, 4 + i*36)[0] for i in range(n)]
    if offsets[0] != 4 + n*36 or offsets[-1] != len(b):
        raise ValueError("DAT sentinel / first offset mismatch")
    if any(x > y for x,y in zip(offsets, offsets[1:])):
        raise ValueError("DAT non-monotonic offsets")
    extensions, maps = {}, []
    for i in range(n - 1):
        st, en = offsets[i], offsets[i+1]
        if en - st > MAX_MEMBER: raise ValueError("oversize member")
        rawname = b[4+i*36+4:4+(i+1)*36].split(b"\x00",1)[0]
        name = rawname.decode("ascii","backslashreplace")
        ext = name.rsplit(".",1)[-1].lower() if "." in name else "(none)"
        extensions[ext] = extensions.get(ext,0) + 1
        if re.fullmatch(r"[0-9]{5}\.map",name,re.I):
            try: maps.append(dict(name=name, status="valid", **parse_map(b[st:en])))
            except ValueError as e:
                raise ValueError("embedded MAP " + name + " invalid: " + str(e)) from e
    return dict(kind="indexed-dat",slots_including_sentinel=n,members=n-1,
                extension_counts=extensions,map_members=maps,
                name_codec="byte-oriented; non-ASCII uncertain")

def parse_script(raw):
    try: b=zlib.decompress(raw)
    except zlib.error as e: raise ValueError("invalid zlib") from e
    if not (6<=len(b)<=MAX_MEMBER) or b[:4]!=b"\x00\x01\x00\x00":
        raise ValueError("invalid Script wrapper")
    n=int.from_bytes(b[4:6],"big")
    if len(b)!=6+2*n: raise ValueError("Script UTF16 size mismatch")
    t=b[6:].decode("utf-16le","strict")
    obj=dict(kind="zlib-script",inflated_bytes=len(b),inflated_sha256=sha(b),
             prefix_hex=b[:4].hex(),utf16_code_units=n)
    try: root=ET.fromstring(t)
    except ET.ParseError: obj["xml"]="not-xml"
    else:
        obj["xml"]="valid";obj["root"]=root.tag
        obj["function_names"]=[f.get("name") for f in root.findall("function")]
    return obj

def inspect(path, base):
    size=path.stat().st_size
    item=dict(path=path.relative_to(base).as_posix(),size=size)
    if size>MAX_FILE:
        item["kind"]="too-large-to-read";return item
    b=path.read_bytes();item["sha256"]=sha(b)
    if path.suffix.lower()==".map":
        item.update(dict(kind="standalone-map",**parse_map(b)))
    elif path.suffix.lower()==".dat":
        if ("script" in [x.lower() for x in path.parts[:-1]]
                or b[:2] in (b"\x78\x01",b"\x78\x9c",b"\x78\xda")):
            item.update(parse_script(b))
        else: item.update(parse_archive(b))
    else: item["kind"]="hash-only"
    return item

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("root",type=Path)
    p.add_argument("--json",type=Path,help="Optional metadata-only report destination")
    a=p.parse_args()
    root=a.root.resolve()
    if not root.exists(): p.error("no such resource path")
    paths=sorted(x for x in (root.rglob("*") if root.is_dir() else [root]) if x.is_file())
    base=root if root.is_dir() else root.parent
    result=[]
    for item in paths:
        try: result.append(inspect(item,base))
        except (OSError,ValueError,UnicodeError) as e:
            result.append(dict(path=item.relative_to(base).as_posix(),kind="invalid",error=str(e)))
    output=dict(schema_version=1,tool="A-015 metadata-only",files=result,
                original_asset_bytes_included=False,
                warning="Format validation is not proof of game semantics or redistribution rights.")
    encoded=json.dumps(output,ensure_ascii=False,indent=2)+"\n"
    print(encoded,end="")
    if a.json: a.json.write_text(encoded,encoding="utf-8")
    return 1 if any("error" in x for x in result) else 0

if __name__=="__main__": sys.exit(main())
