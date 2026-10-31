#!/usr/bin/env python3
"""A005: original-EXE path gate and MAP dynamic-overlay recovery (offline only)."""
import argparse
import hashlib
import json
import struct
from collections import Counter, deque
from pathlib import Path

EXE_SHA='db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
MAP0_SHA='dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761'
EDGES={
 0x4B4966:0x4C1850,0x4C1862:0x4B2C80,0x4C18C8:0x4C3AA0,
 0x4B8B4F:0x4EA900,0x4B8B71:0x4B4920,0x4B8BA0:0x4B4920,
 0x4B8BB1:0x4431E0,0x4BE7B7:0x4B8B20,0x4BE5E8:0x46E740,
 0x4BE60D:0x46E740,0x4BE7DF:0x4B4AB0,0x557B9B:0x4BE470,
 0x557C1F:0x4B4920,
}
WINDOWS={
 0x4C186B:'83c006',0x4C186E:'8b10',0x4C1870:'8911',
 0x4C18C1:'85c9',0x4C18D8:'8b03f7d623c68903',
 0x4B8B31:'85c9',0x4B8B54:'83f801',
 0x4B8B76:'f644241001',0x4B8BA5:'f644241008',
 0x4B8BB8:'8a44241a',0x4B8BC1:'d3e2',0x4B8BC6:'84c2',
 0x4BE642:'c74424148f010000',0x4BE7A7:'a803',
 0x4BE813:'46',0x4BE814:'83fe08',
 0x4BE999:'c744242015000000',0x4BE9BC:'c744246413000000',
}
class ProbeError(ValueError): pass

def reader(exe):
    if exe[:2]!=b'MZ':raise ProbeError('not MZ')
    p,=struct.unpack_from('<I',exe,0x3c)
    if exe[p:p+4]!=b'PE\0\0':raise ProbeError('not PE')
    n,=struct.unpack_from('<H',exe,p+6)
    opt=p+24
    if struct.unpack_from('<H',exe,opt)[0]!=0x10b:raise ProbeError('not PE32')
    base,=struct.unpack_from('<I',exe,opt+28)
    sec=opt+struct.unpack_from('<H',exe,p+20)[0]
    segments=[]
    for i in range(n):
        off=sec+i*40
        vs,rva,rs,raw=struct.unpack_from('<IIII',exe,off+8)
        segments.append((base+rva,min(vs,rs),raw))
    def read(va,size):
        for start,length,off in segments:
            if start<=va and va+size<=start+length:
                return exe[off+va-start:off+va-start+size]
        raise ProbeError(f'unmapped VA {va:#x}')
    return read

def verify_exe(path):
    exe=Path(path).read_bytes()
    if hashlib.sha256(exe).hexdigest()!=EXE_SHA:
        raise ProbeError('wrong EXE SHA')
    read=reader(exe)
    for va,target in EDGES.items():
        op,disp=struct.unpack('<Bi',read(va,5))
        if op not in (0xe8,0xe9) or va+5+disp!=target:
            raise ProbeError(f'bad native call/jump {va:#x}')
    for va,hx in WINDOWS.items():
        if read(va,len(hx)//2)!=bytes.fromhex(hx):
            raise ProbeError(f'bad native opcode {va:#x}')
    return {'original_SHA':EXE_SHA,'native_edges':len(EDGES),
            'native_opcode_anchors':len(WINDOWS),'result':'PASS'}

def compose_tile_flags(raw,added,removed):
    """0x4C1850 overlay only, when tile is in the current dynamic overlay rect."""
    for x in (raw,added,removed):
        if type(x) is not int or not 0<=x<=0xffffffff:
            raise ValueError('expected unsigned 32-bit integer')
    return ((raw | added) & ~removed) & 0xffffffff

def local_candidate_gate(dest_effective_flags,source_effective_flags,
                         source_direction_mask,direction_index,*,
                         object_lookup_is_one=False,global_bypass=False):
    """Exact branch subset of 0x4B8B20; global/actor are inputs, not reconstructed.
    Neither a substitute for 0x4BE470's bounds/heuristic nor native movement E2E.
    """
    if not all(type(v) is int and 0<=v<=0xffffffff for v in
               (dest_effective_flags,source_effective_flags)):
        raise ValueError('bad flags')
    if not 0<=source_direction_mask<=255 or not 0<=direction_index<=7:
        raise ValueError('invalid dir mask/index')
    if global_bypass: return True
    if object_lookup_is_one: return False
    if dest_effective_flags & 1: return False
    if source_effective_flags & 8 and (source_direction_mask & (1<<direction_index)):
        return False
    return True

def map_payload(dat,mapname):
    n,=struct.unpack_from('<I',dat,0)
    if not 2<=n<=100000 or 4+n*36>len(dat):raise ProbeError('bad archive index')
    starts=[struct.unpack_from('<I',dat,4+i*36)[0] for i in range(n)]
    if starts[0]!=4+n*36 or starts[-1]!=len(dat) or any(a>=b for a,b in zip(starts,starts[1:])):
        raise ProbeError('bad sentinel/index')
    for i in range(n-1):
        name=dat[8+36*i:40+36*i].split(b'\0',1)[0]
        if name==mapname.encode('ascii'):
            return memoryview(dat)[starts[i]:starts[i+1]]
    raise ProbeError('map missing')

def audit_map6(path):
    dat=Path(path).read_bytes()
    if hashlib.sha256(dat).hexdigest()!=MAP0_SHA:raise ProbeError('wrong map archive SHA')
    m=map_payload(dat,'00006.map')
    w,h=m[6],m[7]
    start=8+((w+1)//2)*((h+3)//4)*2
    count=w*h
    if not w or not h or start+10*count>len(m):raise ProbeError('bad map tiles')
    flags=[struct.unpack_from('<I',m,start+10*i+6)[0] for i in range(count)]
    path=[(30,30),(30,31),(30,32),(31,32),(32,32)]
    if any(not(0<=x<w and 0<=y<h and not(flags[x+y*w]&1)) for x,y in path):
        raise ProbeError('candidate path outside raw bit0-clear subset')
    q=deque([path[0]]); seen={path[0]}
    while q:
        x,y=q.popleft()
        for dx,dy in ((0,1),(1,0),(0,-1),(-1,0)):
            nx,ny=x+dx,y+dy
            if 0<=nx<w and 0<=ny<h and (nx,ny) not in seen and not flags[nx+ny*w]&1:
                seen.add((nx,ny));q.append((nx,ny))
    return {'map_ref':6,'width':w,'height':h,
            'raw_tile_flags':dict(sorted(Counter(flags).items())),
            'raw_bit0_clear':sum(not(f&1) for f in flags),
            'raw_4neighbor_component_from_30_30':len(seen),
            'candidate_path':path,'native_walkability':'unverified',
            'native_client_gui':'not-run'}

def eight_neighbor_direction(dx,dy):
    """Eight adjacent grid steps' result from native 0x4431E0 (NOT all slopes)."""
    mapping={(0,-1):0,(1,0):1,(0,1):2,(-1,0):3,
             (1,-1):4,(1,1):5,(-1,1):6,(-1,-1):7}
    try:return mapping[(dx,dy)]
    except KeyError as e:raise ValueError('not an adjacent step') from e

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--exe',type=Path,required=True)
    a.add_argument('--map0',type=Path,required=True)
    ns=a.parse_args()
    print(json.dumps({'exe':verify_exe(ns.exe),'map6':audit_map6(ns.map0)},indent=2))
