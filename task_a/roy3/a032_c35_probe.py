#!/usr/bin/env python3
"""A-032 offline native-asset C35 reconstruction; does not verify GUI or walking."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

EXE_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
MAP_SHAS={
    "Map0.dat":"dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761",
    "Map1.dat":"8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b",
    "Map2.dat":"5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb",
}
class FormatError(ValueError):
    pass

def crc_table(exe):
    # .data VA 0x663000, file offset 0x263000; table VA 0x664720.
    if hashlib.sha256(exe).hexdigest()!=EXE_SHA:
        raise FormatError("unrecognized Asgard.exe SHA")
    t=struct.unpack_from("<256H",exe,0x264720)
    if t[:3]!=(0,0x1021,0x2042):
        raise FormatError("invalid CRC table anchor")
    return t

def feed(crc,data,table):
    # 0x43E0A0: byte is FIRST arg, accumulator is SECOND arg.
    for b in data:
        crc=(table[(crc>>8)&255]^(crc<<8)^b)&0xffff
    return crc

def members(dat):
    if len(dat)<76: raise FormatError("short DAT")
    count,=struct.unpack_from("<I",dat)
    if count<2 or 4+36*count>len(dat): raise FormatError("bad DAT slot count")
    offsets=[struct.unpack_from("<I",dat,4+36*i)[0] for i in range(count)]
    if (offsets[0]!=4+36*count or offsets[-1]!=len(dat) or
        any(a>=b for a,b in zip(offsets,offsets[1:]))):
        raise FormatError("bad DAT index/EOF sentinel")
    seen=set()
    for i in range(count-1):
        try: name=dat[8+36*i:40+36*i].split(b"\0",1)[0].decode("ascii")
        except UnicodeDecodeError as e: raise FormatError("nonascii MAP member") from e
        if not re.fullmatch(r"[0-9]{5}\.map",name) or name in seen:
            raise FormatError("invalid or duplicate member")
        seen.add(name)
        yield name,memoryview(dat)[offsets[i]:offsets[i+1]]

def checksum(raw,table):
    m=memoryview(raw)
    if len(m)<20: raise FormatError("short MAP")
    h0,h1,h2=struct.unpack_from("<HHH",m)
    w,ht=m[6],m[7]
    if not w or not ht: raise FormatError("zero MAP dimensions")
    block_len=((w+1)//2)*((ht+3)//4)*2
    tile_start=8+block_len
    tile_end=tile_start+w*ht*10
    if tile_end>len(m):raise FormatError("truncated block/tile")
    crc=feed(0,m[8:tile_start],table)
    crc=feed(crc,m[tile_start:tile_end],table)
    at=tile_end
    counts={}
    for stride in (7,8,16):
        if at+4>len(m):raise FormatError("truncated tail count")
        n,=struct.unpack_from("<I",m,at);at+=4
        if n>(len(m)-at)//stride:raise FormatError("truncated tail records")
        counts[str(stride)]=n
        if stride==7:
            # 0x4B2FE0: bool(u8), LEu16, sign-extend two LEi16 to LEi32.
            for i in range(n):
                flag,u,x,y=struct.unpack_from("<BHhh",m,at+7*i)
                crc=feed(crc,bytes([int(flag!=0)])+struct.pack("<Hii",u,x,y),table)
        elif stride==8:
            # 0x4B30B0: four LEu16, byte order unchanged.
            crc=feed(crc,m[at:at+8*n],table)
        else:
            # 0x4B3150: thirteen calls to 0x43E0A0 per 16B entry.
            # +0 LEu16; bool(+2 LEu16); bool(+3 byte); +4 byte;
            # +8..+11 bytes; +12 LEu16; +14 LEu16; skip +5..+7.
            for i in range(n):
                p=at+16*i
                a,b=struct.unpack_from("<HH",m,p)
                canon=(struct.pack("<H",a)+bytes([int(b!=0),int(m[p+3]!=0),m[p+4]])+
                       m[p+8:p+16].tobytes())
                assert len(canon)==13
                crc=feed(crc,canon,table)
        at+=n*stride
    if at!=len(m):raise FormatError("trailing MAP bytes")
    return {"header_le_u16":[h0,h1,h2],"width_tiles":w,"height_tiles":ht,
            "header_word":h2,"checksum":crc,
            "c35_be_u16_pair_hex":struct.pack(">HH",h2,crc).hex().upper(),
            "tile_start_offset":tile_start,"tail_record_counts":counts}

def report(exe_path,archive_path,map_ref,candidate_path=()):
    if not isinstance(map_ref,int) or not 0<=map_ref<=65535:
        raise FormatError("map_ref must be a network u16")
    lib=map_ref//10000
    archive_name=f"Map{lib}.dat"
    if Path(archive_path).name!=archive_name:raise FormatError("incorrect archive for map_ref")
    data=Path(archive_path).read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    if sha!=MAP_SHAS[archive_name]:raise FormatError("archive version/hash mismatch")
    table=crc_table(Path(exe_path).read_bytes())
    name=f"{map_ref:05d}.map"
    payload=next((m for n,m in members(data) if n==name),None)
    if payload is None:raise FormatError("map_ref does not exist")
    result=checksum(payload,table)
    result.update(map_ref=map_ref,archive=archive_name,archive_sha256=sha,
                  map_name=name,map_payload_sha256=hashlib.sha256(payload).hexdigest(),
                  source_grade="original-static-resource-reconstruction",
                  native_c35_captured=False,native_walkability_verified=False)
    if candidate_path:
        points=[]
        w,h=result["width_tiles"],result["height_tiles"]
        for x,y in candidate_path:
            if not 0<=x<w or not 0<=y<h:raise FormatError("candidate tile out of bounds")
            flag,=struct.unpack_from("<I",payload,result["tile_start_offset"]+10*(x+y*w)+6)
            points.append({"x":x,"y":y,"tile_flags_u32":flag,"player_walkable":"unknown"})
        result["candidate_path"]=points
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--map-dir",type=Path,required=True)
    p.add_argument("--map-ref",type=int,required=True)
    p.add_argument("--candidate-path",default="",help="semicolon-separated x,y tile coordinates")
    a=p.parse_args()
    coords=[]
    if a.candidate_path:
        try:coords=[tuple(map(int,part.split(","))) for part in a.candidate_path.split(";")]
        except ValueError:p.error("invalid candidate-path")
        if any(len(pair)!=2 for pair in coords):p.error("expected x,y;x,y")
    if not 0<=a.map_ref<=65535:p.error("map_ref outside u16 range")
    try:
        result=report(a.exe,a.map_dir/f"Map{a.map_ref//10000}.dat",a.map_ref,coords)
    except (FormatError,OSError,struct.error) as e:p.error(str(e))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
