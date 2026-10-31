#!/usr/bin/env python3
"""A-015 original MAP parser and coordinate evidence; no private assets exported.

Original Asgard.exe 0x4B33A0 MAP loader, 0x4B2C80 tile accessor;
0x4B4BB0 line bit4 test; 0x4D120B bit0; grid 0x4B3250.
Pixel geometry inferred from viewport bound 0x4B4A3B/0x4B4A73;
NEVER call it a proven player walkability/spawn rule.
"""
import argparse, hashlib, json, re, struct
from collections import Counter
from pathlib import Path

EXPECTED={
"Map0.dat":"dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761",
"Map1.dat":"8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b",
"Map2.dat":"5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb"}

class MapError(ValueError):pass

class MapView:
    def __init__(self,raw):
        self.raw=memoryview(raw)
        if len(raw)<8:raise MapError("short MAP")
        self.headers=struct.unpack_from("<HHH",raw)
        self.width,self.height=raw[6],raw[7]
        if not self.width or not self.height:raise MapError("zero dimensions")
        self.block_bytes=((self.width+1)//2)*((self.height+3)//4)*2
        self.tile_offset=8+self.block_bytes
        self.tile_end=self.tile_offset+self.width*self.height*10
        if self.tile_end>len(raw):raise MapError("tile truncation")
        at=self.tile_end;self.tail=[]
        for stride in (7,8,16):
            if at+4>len(raw):raise MapError("tail count truncation")
            n,=struct.unpack_from("<I",raw,at);at+=4
            if n>(len(raw)-at)//stride:raise MapError("tail truncation")
            self.tail.append((at,n,stride));at+=n*stride
        if at!=len(raw):raise MapError("trailing MAP bytes")
    def contains_tile(self,x,y):
        return type(x) is int and type(y) is int and 0<=x<self.width and 0<=y<self.height
    def tile_offset_at(self,x,y):
        if not self.contains_tile(x,y):raise MapError("out of tile bounds")
        return self.tile_offset+10*(x+y*self.width)
    def tile(self,x,y):
        a,b,c,flag=struct.unpack_from("<HHHI",self.raw,self.tile_offset_at(x,y))
        return dict(x=x,y=y,layers_u16=[a,b,c],flags_u32=flag,bit0=bool(flag&1),
                    bit4=bool(flag&16),walkable="unknown-original-player-rule")
    def pixel_to_tile_candidate(self,px,py):
        """48x32 viewport cell geometry, not a confirmed player feet/pivot mapping."""
        if type(px) is not int or type(py) is not int or not(0<=px<48*self.width and 0<=py<32*self.height):
            raise MapError("pixel outside candidate viewport")
        return px//48,py//32
    def tile_for_pixel_candidate(self,px,py):
        return self.tile(*self.pixel_to_tile_candidate(px,py))
    def tail_pixel_candidates(self):
        result=[]
        for pos,n,stride in self.tail[1:]:
            good=aligned_x=aligned_y=0
            for j in range(n):
                x,y=struct.unpack_from("<HH",self.raw,pos+j*stride+(2 if stride==8 else 12))
                good+=x<48*self.width and y<32*self.height
                aligned_x+=x%48==0;aligned_y+=y%32==0
            result.append(dict(count=n,in_pixel_bounds=good,x_multiple_48=aligned_x,y_multiple_32=aligned_y))
        return result

def members(blob):
    b=memoryview(blob)
    if len(b)<76:raise MapError("short DAT")
    count,=struct.unpack_from("<I",b,0)
    if not 2<=count<=200000 or 4+36*count>len(b):raise MapError("slot count")
    offsets=[struct.unpack_from("<I",b,4+i*36)[0] for i in range(count)]
    if offsets[0]!=4+count*36 or offsets[-1]!=len(b) or any(x>y for x,y in zip(offsets,offsets[1:])):
        raise MapError("DAT offset/sentinel")
    seen=set()
    for i in range(count-1):
        raw_name=bytes(b[8+i*36:40+i*36]).split(b"\0",1)[0]
        try:name=raw_name.decode("ascii")
        except UnicodeDecodeError:raise MapError("non-ASCII member")
        if not re.fullmatch(r"[0-9]{5}\.map",name) or name in seen:raise MapError("member name/duplicate")
        seen.add(name)
        if offsets[i]>=offsets[i+1]:raise MapError("empty MAP")
        yield name,MapView(b[offsets[i]:offsets[i+1]])

def audit(path,verify_sha=False):
    raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if verify_sha and sha!=EXPECTED.get(Path(path).name):raise MapError("mismatched original MAP archive")
    map_count=tile_count=bit0=bit4=bounds31=0
    flags=Counter();point31=Counter()
    tails=[dict(count=0,in_pixel_bounds=0,x_multiple_48=0,y_multiple_32=0) for _ in range(2)]
    for name,m in members(raw):
        map_count+=1;tile_count+=m.width*m.height
        if m.contains_tile(31,29):
            bounds31+=1;point31[m.tile(31,29)["flags_u32"]]+=1
        for idx in range(m.width*m.height):
            flag,=struct.unpack_from("<I",m.raw,m.tile_offset+10*idx+6)
            flags[flag]+=1;bit0+=bool(flag&1);bit4+=bool(flag&16)
        for i,info in enumerate(m.tail_pixel_candidates()):
            for k in info:tails[i][k]+=info[k]
    return dict(file=Path(path).name,sha256=sha,maps=map_count,tiles=tile_count,
        bit0_set=bit0,bit4_set=bit4,flag_counts=dict(sorted(flags.items())),
        tile_31_29_in_bounds_maps=bounds31,at_31_29_flags=dict(sorted(point31.items())),
        tail_pixel_candidates=tails,walkability="unknown",native_client_e2e="not-run",
        raw_assets_exported=False)

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("archives",nargs="+")
    ap.add_argument("--verify-original-sha",action="store_true");args=ap.parse_args()
    print(json.dumps([audit(p,args.verify_original_sha) for p in args.archives],
                     ensure_ascii=False,indent=2))
