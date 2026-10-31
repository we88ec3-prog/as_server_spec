#!/usr/bin/env python3
"""A-019: native packet/music cues and Map*.dat index only; no original Server mapping.
Original source assets are NOT committed; designed cue model is not original Server logic.
"""
from __future__ import annotations
import hashlib
import re
import struct
import unittest
from pathlib import Path

EXE_SHA = 'db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
PACK_SHA = {
 'Map0.dat': 'dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761',
 'Map1.dat': '8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b',
 'Map2.dat': '5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb',
}
SIG = {
 'S19 ctor opcode':(0x584A49, '6a19'),
 'S19 read type u8':(0x584AE3, 'e8c862edff'),
 'S19 normalize type1 boolean':(0x584AE8,'fec8f6d81bc040'),
 'S19 read repeat if type1':(0x584AF6,'e8b562edff'),
 'S19 read u16 track':(0x584B00,'e8db62edff'),
 'S19 handler branch':(0x4F25D4,'8b482485c9'),
 'S19 music call':(0x4F25EB,'e8d0a70400'),
 'S19 other sound call':(0x4F260B,'e840ac0400'),
 'music file format arg':(0x53CE4D,'6820ee6000'),
 'music alternate format arg':(0x53CF01,'6820ee6000'),
 'map filename format arg':(0x4B3424,'68fca26000'),
}
def native_audit(exe):
 data = Path(exe).read_bytes()
 if hashlib.sha256(data).hexdigest() != EXE_SHA:
  raise ValueError('Asgard.exe release mismatch')
 for label, (va, signature) in SIG.items():
  expected=bytes.fromhex(signature)
  if data[va-0x400000:va-0x400000+len(expected)] != expected:
   raise ValueError('mismatched original binary at '+label)
 if data[0x60EE20-0x400000:][:18].decode('utf-16le') != '%05d.mp3\0':
  raise ValueError('original music filename format')
 return len(SIG)

def archive_index(dat):
 data=Path(dat).read_bytes()
 filename=Path(dat).name
 if hashlib.sha256(data).hexdigest() != PACK_SHA[filename]:
  raise ValueError('Map pack revision mismatch: '+filename)
 count, size=struct.unpack_from('<II',data)
 if size != 4+36*count or len(data) < 8+36*count:
  raise ValueError('archive directory offset/size')
 directory=data[8:8+36*count]
 names=[]
 for n in range(count):
  record=directory[36*n:36*(n+1)]
  match=re.match(rb'([0-9]{5}\.map)\x00',record)
  if match:names.append(match.group(1).decode('ascii'))
 if b'Music' in directory or b'.mp3' in directory or b'.MP3' in directory:
  raise ValueError('unexpected audio filename in archive DIRECTORY')
 return {'archive':filename,'directory_entries':count,'named_maps':len(names),
         'unclassified_entries':count-len(names),'music_file_names_in_directory':0,
         'first_map':names[0] if names else None,'last_map':names[-1] if names else None}

def encode_music(track,repeat=0):
 if type(track) is not int or not 0<=track<=65535:raise ValueError('track range')
 if type(repeat) is not int or not 0<=repeat<=255:raise ValueError('repeat range')
 return bytes((1,repeat))+track.to_bytes(2,'big')

def decode_s19(body):
 if not body:raise ValueError('missing kind')
 # Original reader normalizes kind==1 to the music branch; other kinds
 # omit repeat and use separate sound playback path.
 if body[0]==1 and len(body)==4:
  return ('music',body[1],int.from_bytes(body[2:],'big'))
 if body[0]!=1 and len(body)==3:
  return ('other-sound',None,int.from_bytes(body[1:],'big'))
 raise ValueError('invalid body length or selector')

class DesignedMusicPolicy:
 def __init__(self, verified_catalog):
  # map_ref -> track only if source verified, no blanket test track 1.
  self.catalog=verified_catalog
  self.generation=None
  self.map_epoch=None
  self.last=None
 def enter(self, generation,map_epoch,map_ref,revision,verified_revision):
  if not verified_revision or generation is None or map_epoch is None:return None
  if (self.generation,self.map_epoch)==(generation,map_epoch):return None
  self.generation,self.map_epoch=generation,map_epoch
  row=self.catalog.get((map_ref,revision))
  if not row or not row.get('native_source_verified'):return None
  track=row['track']
  if type(track)!=int or not 0<=track<=65535:return None
  self.last=(generation,map_epoch,map_ref,revision,track)
  return encode_music(track,row.get('repeat',0))
 def stale(self,generation,map_epoch):
  return (self.generation,self.map_epoch)!=(generation,map_epoch)

class Tests(unittest.TestCase):
 def test_01_original_exe_signatures(self):
  p=Path('/mnt/data/Asgard.exe')
  if not p.exists():self.skipTest('Asgard.exe not mounted')
  self.assertEqual(native_audit(p),11)
 def test_02_original_map_index_counts(self):
  paths=[Path('/mnt/data')/x for x in PACK_SHA]
  if not all(p.exists() for p in paths):self.skipTest('Map archives not mounted')
  rows=[archive_index(p) for p in paths]
  self.assertEqual([r['directory_entries'] for r in rows],[289,185,23])
  self.assertEqual([r['named_maps'] for r in rows],[288,184,22])
  self.assertEqual(sum(r['named_maps'] for r in rows),494)
 def test_03_music_track_18_vector(self):
  self.assertEqual(encode_music(18,0).hex(),'01000012')
  self.assertEqual(decode_s19(bytes.fromhex('01000012')),('music',0,18))
 def test_04_music_stop_vector(self):
  self.assertEqual(encode_music(0).hex(),'01000000')
 def test_05_other_sound_branch_not_music(self):
  self.assertEqual(decode_s19(bytes.fromhex('020012')),('other-sound',None,18))
  with self.assertRaises(ValueError):decode_s19(bytes.fromhex('02000012'))
 def test_06_truncated_or_unbounded(self):
  for b in (b'',b'\x01',b'\x01\x00\x12',b'\x01\x00\x00\x12\x00'):
   with self.assertRaises(ValueError):decode_s19(b)
  for x in (-1,65536,1.1):
   with self.assertRaises(ValueError):encode_music(x)
 def test_07_unknown_map_not_automatically_track1(self):
  p=DesignedMusicPolicy({})
  self.assertIsNone(p.enter(1,10,10001,'rev1',True))
 def test_08_unverified_catalog_row_rejected(self):
  p=DesignedMusicPolicy({(10001,'rev1'):{'track':1,'native_source_verified':False}})
  self.assertIsNone(p.enter(1,10,10001,'rev1',True))
 def test_09_verified_synthetic_cue_only(self):
  p=DesignedMusicPolicy({(10001,'rev1'):{'track':18,'repeat':0,'native_source_verified':True}})
  self.assertEqual(p.enter(1,10,10001,'rev1',True),bytes.fromhex('01000012'))
  self.assertIsNone(p.enter(1,10,10001,'rev1',True))
  self.assertTrue(p.stale(1,9))
 def test_10_new_epoch_and_unverified_revision(self):
  p=DesignedMusicPolicy({(1,'rev1'):{'track':18,'native_source_verified':True}})
  self.assertIsNone(p.enter(1,2,1,'rev1',False))
  self.assertEqual(p.enter(1,2,1,'rev1',True),bytes.fromhex('01000012'))
  self.assertIsNone(p.enter(2,1,1,'rev2',True))

if __name__=='__main__':unittest.main(verbosity=2)
