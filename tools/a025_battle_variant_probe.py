#!/usr/bin/env python3
"""A-025 original C3D/S3D jump-table probe and bounded decoded-body codec.
Native static + synthetic only, NOT original GUI / Server battle validation.
"""
from __future__ import annotations
import hashlib, struct, json
from pathlib import Path
SHA='db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
C_JUMPS=(0x570DFF,0x570E0D,0x570E5F,0x570F2A,0x570EB2,0x570F0E,
 0x570EC0,0x570ECE,0x570F2A,0x570EEE,0x570F0E,0x570F2A,
 0x570F2A,0x570F2A,0x570F2A,0x570F1C)
S_JUMPS=(0x57C8D8,0x57CD73,0x57C95C,0x57CA00,0x57CA4C,0x57CA4C,
 0x57CA4C,0x57CA5B,0x57CD73,0x57CA74,0x57CA4C,0x57CB93,
 0x57CD73,0x57CBA2,0x57CC88,0x57CD59)
WINDOWS={
 0x5711CB:'6a3d',0x570DE3:'8b461850e8149deeff',
 0x570DEC:'8b461883f80f',0x570DF8:'ff24852c0f5700',
 0x570DFF:'0fb64e1d',0x570E40:'0fb69690000000',
 0x570F1C:'8b869c000000',
 0x57C6EC:'6a3d',0x57C8BA:'e8f1e4edff',
 0x57C8C2:'0fb6c083f80f',0x57C8D1:'ff248598cd5700',
 0x57C8D8:'8bcee801e5edff',0x57CA00:'6a0068ff000000',
 0x57CA47:'e927030000',0x57CD59:'8bcee850e1edff',
 0x57CD68:'e843e1edff',0x571769:'6a56',
 0x571800:'0fb64118',0x57185C:'e8effeffff',
 0x570A29:'6a13',0x575529:'6a4d',0x57E1C9:'6a5f'
}
# C3D after subtype; all 16 writer destinations now individually classified.
# No business meaning or Server acceptance is inferred from these shapes.
C_FORMATS={0:'B',1:'string8,string8,B,I',2:'string8',3:'',4:'B',5:'B',
 6:'B',7:'BB',8:'',9:'BB',10:'B',11:'',12:'',13:'',14:'',15:'I'}
# S3D complex, vector-bearing subtypes 0/2/9/13/14 are NOT safe codec here.
S_FORMATS={1:'',3:'string8,I,B,26B',4:'B',5:'B',6:'B',
 7:'BB',8:'',10:'B',11:'B',12:'',15:'II'}
class DecodeError(ValueError):pass

def pe_read(data,va,n):
 if data[:2]!=b'MZ':raise DecodeError('not MZ')
 pe,=struct.unpack_from('<I',data,0x3c)
 if data[pe:pe+4]!=b'PE\0\0':raise DecodeError('not PE')
 count,=struct.unpack_from('<H',data,pe+6)
 opt=pe+24
 if struct.unpack_from('<H',data,opt)[0]!=0x10b:raise DecodeError('not PE32')
 base,=struct.unpack_from('<I',data,opt+28)
 sh=opt+struct.unpack_from('<H',data,pe+20)[0]
 for i in range(count):
  at=sh+40*i
  vs,rva,rs,offset=struct.unpack_from('<IIII',data,at+8)
  if base+rva<=va and va+n<=base+rva+min(vs,rs):
   return data[offset+va-base-rva:offset+va-base-rva+n]
 raise DecodeError('unmapped VA')

def verify_original(exe):
 raw=Path(exe).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SHA:raise DecodeError('EXE version mismatch')
 for va,hx in WINDOWS.items():
  if pe_read(raw,va,len(hx)//2)!=bytes.fromhex(hx):
   raise DecodeError('native VA mismatch '+hex(va))
 for va,want in ((0x570F2C,C_JUMPS),(0x57CD98,S_JUMPS)):
  if struct.unpack('<16I',pe_read(raw,va,64))!=want:
   raise DecodeError('jump table mismatch '+hex(va))
 return {'original_sha256':SHA,'native_byte_windows':len(WINDOWS),
  'jump_table_entries_verified':32,'c3d_writer_subtypes':16,
  's3d_bounded_reader_subtypes':sorted(S_FORMATS),
  'original_gui_tcp':'not-run','original_tutorial_combat_required':'unknown'}

def one(v):
 if type(v) is not int or not 0<=v<=255:raise DecodeError('u8')
 return bytes((v,))
def word32(v):
 if type(v) is not int or not 0<=v<=0xffffffff:raise DecodeError('BEu32')
 return struct.pack('>I',v)
def string8(b):
 if type(b) is not bytes or len(b)>255:raise DecodeError('encoded string8')
 return bytes((len(b),))+b

def c3d_encode(sub,*args):
 if type(sub) is not int or sub not in C_FORMATS:raise DecodeError('subtype')
 fmt=C_FORMATS[sub]
 fields=[]
 if fmt:
  for k in fmt.split(','):
   fields += ['B','B'] if k=='BB' else [k]
 if len(args)!=len(fields):raise DecodeError('wrong fields')
 out=one(sub)
 for k,v in zip(fields,args):
  out+=string8(v) if k=='string8' else one(v) if k=='B' else word32(v)
 return out

def s3d_parse(data):
 if type(data) is not bytes or not data:raise DecodeError('missing subtype')
 sub=data[0]
 if sub not in S_FORMATS:raise DecodeError('unsafe complex/unverified subtype')
 fmt=S_FORMATS[sub]
 kinds=[]
 if fmt:
  for k in fmt.split(','):
   kinds+=['B','B'] if k=='BB' else ['I','I'] if k=='II' else [k]
 pos=1;fields=[]
 for k in kinds:
  if k=='string8':
   if pos>=len(data):raise DecodeError('short len')
   n=data[pos];pos+=1
   if pos+n>len(data):raise DecodeError('short string')
   fields.append(data[pos:pos+n]);pos+=n
  elif k=='B':
   if pos>=len(data):raise DecodeError('short u8')
   fields.append(data[pos]);pos+=1
  elif k=='I':
   if pos+4>len(data):raise DecodeError('short u32')
   fields.append(struct.unpack_from('>I',data,pos)[0]);pos+=4
  elif k=='26B':
   if pos+26>len(data):raise DecodeError('short fixed bytes')
   fields.append(data[pos:pos+26]);pos+=26
 if pos!=len(data):raise DecodeError('trailing bytes')
 return {'subtype':sub,'opaque_fields':tuple(fields),
  'native_result_meaning':'unverified'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('exe',type=Path)
 a=p.parse_args();print(json.dumps(verify_original(a.exe),indent=2))
