#!/usr/bin/env python3
"""A010-D01 PE-gated original and synthetic action/shortcut tests."""
import os, struct, unittest
from pathlib import Path
from a010d01_shortcut_probe import (
 ContractError,verify_exe,parse_s62,parse_s63,action_key,shortcut_offset,shortcut_ref)
def fixture(kind=1,slot=1,cast=0,mode=5):
 return bytes([kind,slot])+struct.pack('>H',18)+bytes([mode,0,0])+b'\x06Attack'+bytes([0])+b'\x04desc\x00'+bytes([0])+struct.pack('>H',cast)+b'\x00'
class TestActionShortcut(unittest.TestCase):
 def test_original_exe(self):
  path=Path(os.environ.get('ASGARD_EXE','/mnt/data/Asgard.exe'))
  if not path.exists():self.skipTest('original EXE not available')
  r=verify_exe(path)
  self.assertEqual(r['native_windows'],33)
  self.assertEqual(r['shortcut_config_strings'],3)
 def test_s62_fields(self):
  r=parse_s62(fixture())
  self.assertEqual((r['kind'],r['slot'],r['presentation_word'],r['use_mode'],r['cast_value']),(1,1,18,5,0))
  self.assertEqual(r['texts_encoded'][0],b'Attack')
  self.assertEqual(len(r['texts_encoded']),4)
 def test_cast_value_not_action_slot(self):
  self.assertEqual(parse_s62(fixture(1,1,0x1234))['cast_value'],0x1234)
  self.assertEqual(parse_s62(fixture(1,1,0x1234))['action_lookup_key'],81)
 def test_string8_and_empty(self):
  p=bytes([2,8])+struct.pack('>H',0)+b'\x05\x00\x00'+bytes([255])+b'B'*255+b'\0\0\0'+b'\0'+b'\0\0'+b'\0'
  self.assertEqual(len(parse_s62(p)['texts_encoded'][0]),255)
 def test_s62_reject_truncated(self):
  b=fixture()
  for cut in range(len(b)):
   with self.assertRaises(ContractError):parse_s62(b[:cut])
 def test_s62_reject_trailing(self):
  with self.assertRaises(ContractError):parse_s62(fixture()+b'\x00')
 def test_s62_reject_type(self):
  with self.assertRaises(ContractError):parse_s62('not bytes')
 def test_s63_exact(self):
  self.assertEqual(parse_s63(b'\x01\x01'),{'kind':1,'slot':1,'action_lookup_key':81})
 def test_s63_reject_length(self):
  for bad in (b'',b'\x01',b'\x01\x01\x01'):
   with self.assertRaises(ContractError):parse_s63(bad)
 def test_action_index(self):
  self.assertEqual([action_key(x,y) for x,y in ((0,1),(1,1),(2,80))],[1,81,240])
 def test_shortcut_stride(self):
  self.assertEqual([shortcut_offset(*p) for p in ((0,0),(0,9),(1,0),(1,9))],[0,108,120,228])
 def test_shortcut_invalid(self):
  for row,col in ((-1,0),(0,-1),(0,10),(256,0)):
   with self.assertRaises(ContractError):shortcut_offset(row,col)
 def test_shortcut_resolution(self):
  r=parse_s62(fixture(kind=1,slot=1,cast=0x77))
  res=shortcut_ref(0,0,True,1,1,{(1,1):r})
  self.assertEqual((res['resolved'],res['action_lookup_key'],res['cast_value']),(True,81,0x77))
 def test_unresolved_shortcut_does_not_create_skill(self):
  res=shortcut_ref(0,0,True,1,1,{})
  self.assertFalse(res['resolved']);self.assertIsNone(res['cast_value'])
 def test_empty_shortcut(self):
  self.assertIsNone(shortcut_ref(0,0,False,1,1,{}))
if __name__=='__main__':unittest.main(verbosity=2)
