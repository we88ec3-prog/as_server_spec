#!/usr/bin/env python3
"""A010-D01: original-PE-gated S62/S63 action rows and local shortcut refs.
No raw assets or server internals; GUI persistence remains unverified.
"""
from __future__ import annotations
import hashlib, json, struct
from pathlib import Path

ORIGINAL_EXE_SHA='db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
ORIGINAL_BASIC_SHA='0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96'
WINDOWS={
 0x578f89:'6a62',
 0x579023:'e8881deeff',
 0x57902d:'e87e1deeff',
 0x579037:'e8a41deeff',
 0x579042:'e8691deeff',
 0x57904c:'e85f1deeff',
 0x579056:'e8551deeff',
 0x57906b:'e83027eeff',
 0x579080:'e81b27eeff',
 0x579095:'e80627eeff',
 0x5790b1:'e8ea26eeff',
 0x5790b8:'e8f31ceeff',
 0x5790c5:'e8161deeff',
 0x5790d0:'e8db1ceeff',
 0x5858b9:'6a63',
 0x585953:'e85854edff',
 0x58595d:'e84e54edff',
 0x4f2e83:'e848e9f0ff',
 0x4f2eaf:'e8fceaf0ff',
 0x4f2f28:'e883eaf0ff',
 0x4019b4:'33c98a4c2408',
 0x401f86:'b150f6e902c2',
 0x401fb8:'6683bb0e08000000',
 0x4018b6:'6689860e080000',
 0x4019a0:'668b4104',
 0x55bc48:'6874296100',
 0x55bc74:'684c296100',
 0x55bc9e:'6824296100',
 0x55ebd9:'6874296100',
 0x55ec2f:'684c296100',
 0x55ec8f:'6824296100',
 0x559478:'8d0480',
 0x559481:'8d8481186b0000',
}
SETTING_STRINGS={
 0x612924:'Shortcut.%d.%d.Slot',
 0x61294c:'Shortcut.%d.%d.Type',
 0x612974:'Shortcut.%d.%d.IsValid'
}
class ContractError(ValueError): pass

def _pe_va(raw,va,n):
 if raw[:2]!=b'MZ':raise ContractError('not MZ')
 off,=struct.unpack_from('<I',raw,0x3c)
 if raw[off:off+4]!=b'PE\0\0':raise ContractError('not PE')
 cnt,=struct.unpack_from('<H',raw,off+6)
 opt=off+24
 if struct.unpack_from('<H',raw,opt)[0]!=0x10b:raise ContractError('not x86 PE32')
 base,=struct.unpack_from('<I',raw,opt+28)
 sec=opt+struct.unpack_from('<H',raw,off+20)[0]
 for i in range(cnt):
  p=sec+i*40
  vsize,rva,rawsize,rawptr=struct.unpack_from('<IIII',raw,p+8)
  if base+rva<=va and va+n<=base+rva+min(vsize,rawsize):
   return raw[rawptr+(va-base-rva):rawptr+(va-base-rva)+n]
 raise ContractError('unmapped PE address')

def verify_exe(path):
 raw=Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=ORIGINAL_EXE_SHA:raise ContractError('original EXE SHA mismatch')
 for va,hx in WINDOWS.items():
  if _pe_va(raw,va,len(hx)//2)!=bytes.fromhex(hx):
   raise ContractError(f'PE instruction mismatch {va:#x}')
 for va,text in SETTING_STRINGS.items():
  if _pe_va(raw,va,2*(len(text)+1))!=text.encode('utf-16le')+b'\0\0':
   raise ContractError(f'shortcut config key mismatch {va:#x}')
 return {'client_sha256':ORIGINAL_EXE_SHA,'native_windows':len(WINDOWS),
         'shortcut_config_strings':len(SETTING_STRINGS),'native_client_gui_test':'not-run'}

def u8(data,pos):
 if pos>=len(data):raise ContractError('u8 truncated')
 return data[pos],pos+1

def u16be(data,pos):
 if pos+2>len(data):raise ContractError('u16 truncated')
 return struct.unpack_from('>H',data,pos)[0],pos+2

def read_string8(data,pos):
 n,pos=u8(data,pos)
 if pos+n>len(data):raise ContractError('string8 truncated')
 return data[pos:pos+n],pos+n

def parse_s62(body):
 """Native 0x579020 decoded body, not framing/opcode; four raw string8 fields."""
 if type(body) is not bytes:raise ContractError('body must be bytes')
 pos=0
 kind,pos=u8(body,pos);slot,pos=u8(body,pos)
 presentation_word,pos=u16be(body,pos)
 mode,pos=u8(body,pos);use_flags,pos=u8(body,pos);extra_byte,pos=u8(body,pos)
 texts=[]
 for _ in range(4):
  item,pos=read_string8(body,pos);texts.append(item)
 extra_after_texts,pos=u8(body,pos)
 cast_value,pos=u16be(body,pos)
 final_byte,pos=u8(body,pos)
 if pos!=len(body):raise ContractError('S62 trailing bytes')
 return {'kind':kind,'slot':slot,'presentation_word':presentation_word,
         'use_mode':mode,'use_flags':use_flags,'extra_byte':extra_byte,
         'texts_encoded':texts,'post_text_byte':extra_after_texts,
         'cast_value':cast_value,'final_byte':final_byte,
         'action_lookup_key':action_key(kind,slot),
         'cast_id_semantics':'opaque; not proven official learned_skill_id'}

def parse_s63(body):
 if type(body) is not bytes or len(body)!=2:raise ContractError('S63 is two u8')
 kind,slot=body
 return {'kind':kind,'slot':slot,'action_lookup_key':action_key(kind,slot)}

def action_key(kind,slot):
 if type(kind) is not int or type(slot) is not int or not 0<=kind<=255 or not 0<=slot<=255:
  raise ContractError('invalid kind/slot')
 return kind*80+slot

def shortcut_offset(row,cell):
 """0x559470: local address index=(row*10+cell)*12, not a skill ID."""
 if type(row) is not int or type(cell) is not int or not 0<=row<=255 or not 0<=cell<10:
  raise ContractError('shortcut row/cell invalid')
 return (row*10+cell)*12

def shortcut_ref(row,cell,valid,resolved_action_kind,action_slot,action_rows):
 """DESIGNED projection of native config+list lookup; no server success implied.
 resolved_action_kind is AFTER native type translation (0x489e60), not raw Shortcut.Type.
 """
 shortcut_offset(row,cell)
 if type(valid) is not bool or not valid:return None
 k=action_key(resolved_action_kind,action_slot)
 rowdata=action_rows.get((resolved_action_kind,action_slot))
 return {'shortcut_row':row,'shortcut_cell':cell,'resolved_action_kind':resolved_action_kind,
         'action_slot':action_slot,'action_lookup_key':k,'resolved':rowdata is not None,
         'cast_value':None if rowdata is None else rowdata['cast_value']}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('exe',type=Path)
 a=p.parse_args()
 print(json.dumps(verify_exe(a.exe),indent=2))
