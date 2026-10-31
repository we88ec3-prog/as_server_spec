#!/usr/bin/env python3
"""A25 C3D/S3D native-static + synthetic fixtures; no GUI success claims."""
import os,unittest
from pathlib import Path
from a025_battle_variant_probe import C_FORMATS,DecodeError,c3d_encode,s3d_parse,verify_original
class TestBattleVariants(unittest.TestCase):
 def test_original_pe(self):
  path=Path(os.environ.get('ASGARD_EXE','/mnt/data/Asgard.exe'))
  if not path.is_file():self.skipTest('original private EXE missing')
  result=verify_original(path)
  self.assertEqual(result['jump_table_entries_verified'],32)
  self.assertGreaterEqual(result['native_byte_windows'],20)
 def test_all_c3d_subtype_branches(self):self.assertEqual(set(C_FORMATS),set(range(16)))
 def test_c3d_empty_extra(self):
  for t in (3,8,11,12,13,14):self.assertEqual(c3d_encode(t),bytes((t,)))
 def test_c3d_single_byte(self):
  for t in (0,4,5,6,10):self.assertEqual(c3d_encode(t,255),bytes((t,255)))
 def test_c3d_two_bytes(self):
  for t in (7,9):self.assertEqual(c3d_encode(t,1,2),bytes((t,1,2)))
 def test_c3d_strings_and_u32(self):
  self.assertEqual(c3d_encode(1,b'A',b'BC',9,0x11223344),bytes.fromhex('0101410242430911223344'))
  self.assertEqual(c3d_encode(2,b'Hi'),bytes.fromhex('02024869'))
  self.assertEqual(c3d_encode(15,0x01020304),bytes.fromhex('0f01020304'))
 def test_c3d_wrong_fields_and_values(self):
  for f in (lambda:c3d_encode(16),lambda:c3d_encode(0),lambda:c3d_encode(0,256),
    lambda:c3d_encode(15,-1),lambda:c3d_encode(2,'text'),
    lambda:c3d_encode(2,b'X'*256),lambda:c3d_encode(1,b'A')):
   with self.assertRaises(DecodeError):f()
 def test_s3d_no_fields(self):
  for t in (1,8,12):self.assertEqual(s3d_parse(bytes([t]))['opaque_fields'],())
 def test_s3d_one_byte(self):
  for t in (4,5,6,10,11):self.assertEqual(s3d_parse(bytes([t,255]))['opaque_fields'],(255,))
 def test_s3d_two_bytes(self):
  self.assertEqual(s3d_parse(bytes([7,0,11]))['opaque_fields'],(0,11))
 def test_s3d_two_u32(self):
  self.assertEqual(s3d_parse(bytes.fromhex('0f1122334455667788'))['opaque_fields'],(0x11223344,0x55667788))
 def test_s3d_string_fixed26(self):
  body=bytes([3,2])+b'AB'+bytes.fromhex('01020304')+bytes([8])+bytes(range(26))
  f=s3d_parse(body)['opaque_fields']
  self.assertEqual((f[0],f[1],f[2],len(f[3])),(b'AB',0x01020304,8,26))
 def test_s3d_invalid_truncated_or_unsupported(self):
  for p in (b'',b'\x10',b'\x00',b'\x02',b'\x09',b'\x0d',b'\x0e',
    b'\x04',b'\x04\x01\x02',b'\x0f\x00\x01',
    b'\x03\x02A',b'\x03\x00'+bytes(30)):
   with self.assertRaises(DecodeError):s3d_parse(p)
 def test_s3d_nonbytes(self):
  with self.assertRaises(DecodeError):s3d_parse('invalid')
if __name__=='__main__':unittest.main(verbosity=2)
