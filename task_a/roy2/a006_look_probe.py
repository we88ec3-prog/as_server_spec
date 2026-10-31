#!/usr/bin/env python3
"""A-006 conservative body codec and PE32 original SHA/VA probe; no GUI claims."""
import hashlib
import struct
from pathlib import Path

CLIENT_SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"

class AppearanceError(ValueError):
    pass

def native_probe(path):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=CLIENT_SHA:
        raise AppearanceError("wrong original Client SHA256")
    pe=struct.unpack_from('<I',data,0x3c)[0]
    if data[pe:pe+4]!=b'PE\0\0' or struct.unpack_from('<H',data,pe+24)[0]!=0x10b:
        raise AppearanceError("not PE32")
    base=struct.unpack_from('<I',data,pe+52)[0]
    sections=pe+24+struct.unpack_from('<H',data,pe+20)[0]
    count=struct.unpack_from('<H',data,pe+6)[0]
    def read(va,size):
        for i in range(count):
            off=sections+40*i
            virtual_size,rva,raw_size,raw_ptr=struct.unpack_from('<IIII',data,off+8)
            if base+rva<=va and va+size<=base+rva+min(virtual_size,raw_size):
                p=raw_ptr+va-base-rva
                return data[p:p+size]
        raise AppearanceError("unmapped VA "+hex(va))
    checks={
        'S05 BE object read':(0x5895a3,'e80819edff'),
        'S05 flag bit0 optional RGB':(0x589674,'f6462c01741e'),
        'S05 flag bit4 optional u16':(0x589698,'f6462c10740b'),
        'S05 flag bit1 optional byte':(0x5896a9,'f6462c02740a'),
        'S33 coordinate BE u16':(0x585573,'e86858edff'),
        'S33 flag bit0 RGB':(0x585667,'f6462c01741e'),
        'S33 flag bit4 u16':(0x58568b,'f6462c10740d'),
        'S33 flag bit1 byte':(0x5856a4,'f6462c02740a'),
        'S33 name string8':(0x5856dc,'e8bf60edff'),
        'S33 high-flag bit13 string8':(0x585719,'f6c4207424'),
        'S33 zero-RGB sentinel group1':(0x585795,'c64633ffc64635ff'),
        'S33 zero-RGB sentinel group2':(0x5857b2,'c64636ffc64638ff'),
        'S04 coordinate BE u16':(0x589993,'e84814edff')
    }
    for label,(va,hex_pattern) in checks.items():
        wanted=bytes.fromhex(hex_pattern)
        if read(va,len(wanted))!=wanted:
            raise AssertionError(label)
    return {'status':'PASS','sha256':CLIENT_SHA,
            'original_static_checks':len(checks),'native_client_E2E':'not-run'}

def parse_s05_profile(body):
    """29-byte profile with flags=0 or 0x1000 only. Other flags are variable."""
    if len(body)!=29:
        raise AppearanceError("S05 body length")
    flags,=struct.unpack_from('>I',body,21)
    if flags not in (0,0x1000):
        raise AppearanceError("S05 optional flags need full native parser")
    clothing=bytes(body[25:28])
    if flags==0 and clothing!=b'\xff\x00\xff':
        raise AppearanceError("S05 default sentinel mismatch")
    return dict(object_id=struct.unpack_from('>I',body,0)[0],
                sex=body[4],clothing_id=struct.unpack_from('>H',body,7)[0],
                hair_id=body[9],hair_rgb=bytes(body[10:13]),
                clothing_rgb=clothing,flags=flags,tail=body[28])

def parse_s33_profile(body):
    """Only flags=0 S33 CP950 profile with 42 + name byte count length."""
    if len(body)<43:
        raise AppearanceError("short S33")
    flags,=struct.unpack_from('>I',body,26)
    if flags!=0:
        raise AppearanceError("unsupported S33 optional flags")
    n=body[34]
    if n==0 or len(body)!=42+n:
        raise AppearanceError("S33 length/string8 mismatch")
    try:
        name=bytes(body[35:35+n]).decode('cp950','strict')
    except UnicodeError as exc:
        raise AppearanceError('invalid CP950 name') from exc
    return dict(x=struct.unpack_from('>H',body,0)[0],
                y=struct.unpack_from('>H',body,2)[0],direction=body[4],
                object_id=struct.unpack_from('>I',body,5)[0],sex=body[9],
                clothing_id=struct.unpack_from('>H',body,12)[0],hair_id=body[14],
                hair_rgb=bytes(body[15:18]),clothing_rgb=bytes(body[30:33]),
                name=name,flags=flags)

def encode_s04(x,y,vx,vy):
    if not all(isinstance(z,int) and 0<=z<=0xffff for z in (x,y,vx,vy)):
        raise AppearanceError('S04 coordinate range')
    return struct.pack('>HHHH',x,y,vx,vy)

def anchor(x,y,vx,vy):
    """Profile 48x32 tiles, pane (-56,-36); projection, NOT native GUI proof."""
    world=(x*48+24,y*32+16)
    origin=((x-vx-1)*48,(y-vy-1)*32)
    return (world[0]-origin[0]-56,world[1]-origin[1]-36)

def changed_fields(a,b):
    return {k for k in ('hair_id','hair_rgb','clothing_id','clothing_rgb')
            if a[k]!=b[k]}

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser()
    p.add_argument('exe')
    args=p.parse_args()
    print(json.dumps(native_probe(args.exe),indent=2))
