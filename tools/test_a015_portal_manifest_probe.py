#!/usr/bin/env python3
"""A-015 original and synthetic positive/negative regression tests."""
import os, struct, unittest, hashlib
from pathlib import Path
from a015_portal_manifest_probe import (FormatError,indexed_members,portal_records,
  manifest_records,map_metadata,audit_basic_and_maps,EXPECTED)

def archive(rows):
 count=len(rows)+1;pos=4+36*count;index=struct.pack('<I',count);payload=b''
 for name,body in rows:
  index+=struct.pack('<I',pos)+name.encode('ascii').ljust(32,b'\0')
  pos+=len(body);payload+=body
 index+=struct.pack('<I',pos)+bytes(32)
 return index+payload
def map5():
 block=((5+1)//2)*((5+3)//4)*2
 return struct.pack('<HHHBB',0,0,0,5,5)+bytes(block)+bytes(250)+bytes(12)
def fixture(rows=None):
 if rows is None:rows=[(1,1,1),(10001,2,2),(20001,3,3)]
 archives={f'Map{i}.dat':archive([(f'{i*10000+1:05d}.map',map5())]) for i in range(3)}
 text=''.join(f'{k}\t{len(v)}\t12345\r\n' for k,v in archives.items()).encode('utf-16')
 portals=struct.pack('<HI',1,len(rows))+b''.join(struct.pack('<HHH',*row) for row in rows)
 return archive([('Portals.tbl',portals),('FileSizeInfo.txt',text)]),archives

class TestPortalManifest(unittest.TestCase):
 def test_synthetic_success(self):
  b,m=fixture();result=audit_basic_and_maps(b,m)
  self.assertEqual(result['portal_table']['rows'],3)
  self.assertEqual(result['portal_table']['raw_tile_flags_at_rows'],{0:3})
  self.assertEqual(result['file_size_info_rows'],3)
 def test_original_resources_if_mounted(self):
  root=Path(os.environ.get('ASGARD_RESOURCE_DIR','/mnt/data'))
  if not all((root/n).is_file() for n in EXPECTED):self.skipTest('private original assets absent')
  data={n:(root/n).read_bytes() for n in EXPECTED}
  for n,raw in data.items():self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED[n])
  result=audit_basic_and_maps(data['Basic.dat'],{n:d for n,d in data.items() if n.startswith('Map')})
  self.assertEqual(result['basic_index_members'],38)
  self.assertEqual(result['file_size_info_rows'],416)
  self.assertEqual(result['map_archive_member_counts'],{'Map0.dat':288,'Map1.dat':184,'Map2.dat':22})
  self.assertEqual(result['portal_table']['rows'],2840)
  self.assertEqual(result['portal_table']['distinct_map_refs'],312)
  self.assertEqual(result['portal_table']['raw_tile_flags_at_rows'],{0:2837,1:1,17:2})
 def test_truncated_portal(self):
  with self.assertRaises(FormatError):portal_records(struct.pack('<HI',1,2)+bytes(6))
 def test_bad_portal_version(self):
  with self.assertRaises(FormatError):portal_records(struct.pack('<HI',2,0))
 def test_duplicate_portal(self):
  with self.assertRaises(FormatError):portal_records(struct.pack('<HI',1,2)+struct.pack('<HHH',1,1,1)*2)
 def test_absent_mapref(self):
  b,m=fixture([(2,1,1)])
  with self.assertRaises(FormatError):audit_basic_and_maps(b,m)
 def test_outside_bounds(self):
  b,m=fixture([(1,5,1)])
  with self.assertRaises(FormatError):audit_basic_and_maps(b,m)
 def test_duplicate_manifest(self):
  with self.assertRaises(FormatError):manifest_records('Map0.dat\t4\t1\nMap0.dat\t4\t2'.encode('utf-16'))
 def test_invalid_manifest(self):
  with self.assertRaises(FormatError):manifest_records('Map0.dat\twrong\t1'.encode('utf-16'))
 def test_size_mismatch(self):
  b,m=fixture();members=indexed_members(b)
  bad=members['FileSizeInfo.txt'].tobytes().decode('utf-16').replace(str(len(m['Map0.dat'])),'99999',1).encode('utf-16')
  b=archive([('Portals.tbl',members['Portals.tbl'].tobytes()),('FileSizeInfo.txt',bad)])
  with self.assertRaises(FormatError):audit_basic_and_maps(b,m)
 def test_index_offset(self):
  b=bytearray(archive([('one',b'A')]));struct.pack_into('<I',b,4,111)
  with self.assertRaises(FormatError):indexed_members(b)
 def test_truncated_map(self):
  with self.assertRaises(FormatError):map_metadata(map5()[:-1])
 def test_extra_map_byte(self):
  with self.assertRaises(FormatError):map_metadata(map5()+b'A')
if __name__=='__main__':unittest.main(verbosity=2)
