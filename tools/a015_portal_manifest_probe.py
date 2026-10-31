#!/usr/bin/env python3
"""A-015: Basic Portals.tbl / FileSizeInfo.txt vs original MAPs (offline only).
Never export raw game assets or per-map portal coordinate lists.
"""
from __future__ import annotations
import argparse, hashlib, json, re, struct
from collections import Counter
from pathlib import Path

EXPECTED={
 'Basic.dat':'0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96',
 'Map0.dat':'dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761',
 'Map1.dat':'8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b',
 'Map2.dat':'5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb',
}
class FormatError(ValueError):pass

def indexed_members(blob):
 data=memoryview(blob)
 if len(data)<76:raise FormatError('short DAT')
 n,=struct.unpack_from('<I',data)
 if not 2<=n<=100000 or 4+36*n>len(data):raise FormatError('bad DAT count')
 starts=[struct.unpack_from('<I',data,4+36*i)[0] for i in range(n)]
 if starts[0]!=4+36*n or starts[-1]!=len(data) or any(a>=b for a,b in zip(starts,starts[1:])):
  raise FormatError('bad DAT index or sentinel')
 members={}
 for i in range(n-1):
  name_bytes=bytes(data[8+36*i:40+36*i]).split(b'\0',1)[0]
  try:name=name_bytes.decode('ascii')
  except UnicodeDecodeError as e:raise FormatError('invalid member name') from e
  if not name or name in members:raise FormatError('empty/duplicate member')
  members[name]=data[starts[i]:starts[i+1]]
 return members

def portal_records(raw):
 raw=memoryview(raw)
 if len(raw)<6:raise FormatError('short portal header')
 version,n=struct.unpack_from('<HI',raw)
 if version!=1 or n>100000 or len(raw)!=6+6*n:raise FormatError('bad portal version/count/size')
 rows=list(struct.iter_unpack('<HHH',raw[6:]))
 if len(rows)!=len(set(rows)):raise FormatError('duplicate portal record')
 return version,rows

def manifest_records(raw):
 rows={}
 for line in bytes(raw).decode('utf-16').splitlines():
  if not line:continue
  fields=line.split('\t')
  if len(fields)!=3 or not re.fullmatch(r'\d+',fields[1]) or not re.fullmatch(r'\d+',fields[2]):
   raise FormatError('invalid FileSizeInfo row')
  if fields[0] in rows:raise FormatError('duplicate FileSizeInfo file')
  rows[fields[0]]=(int(fields[1]),int(fields[2]))
 return rows

def map_metadata(blob):
 raw=memoryview(blob)
 if len(raw)<20:raise FormatError('short MAP')
 w,h=raw[6],raw[7]
 if not w or not h:raise FormatError('zero MAP dimensions')
 off=8+((w+1)//2)*((h+3)//4)*2
 pos=off+w*h*10
 if pos>len(raw):raise FormatError('short MAP tile region')
 for stride in (7,8,16):
  if pos+4>len(raw):raise FormatError('short MAP tail count')
  n,=struct.unpack_from('<I',raw,pos);pos+=4
  if n>(len(raw)-pos)//stride:raise FormatError('short MAP tail')
  pos+=n*stride
 if pos!=len(raw):raise FormatError('MAP trailing bytes')
 return w,h,off

def audit_basic_and_maps(basic,archives):
 members=indexed_members(basic)
 if 'Portals.tbl' not in members or 'FileSizeInfo.txt' not in members:
  raise FormatError('required Basic member missing')
 version,portals=portal_records(members['Portals.tbl'])
 manifest=manifest_records(members['FileSizeInfo.txt'])
 expected_archives={'Map0.dat','Map1.dat','Map2.dat'}
 if set(archives)!=expected_archives:raise FormatError('three MAP archives required')
 maps={};counts={};size_matches={}
 for arch,data in archives.items():
  if arch not in manifest or manifest[arch][0]!=len(data):
   raise FormatError('MAP length missing/mismatched FileSizeInfo')
  size_matches[arch]=True
  inner=indexed_members(data);counts[arch]=len(inner)
  for name,payload in inner.items():
   if not re.fullmatch(r'[0-9]{5}\.map',name):raise FormatError('bad MAP name')
   ref=int(name[:5])
   if ref//10000!=int(arch[3]) or ref in maps:raise FormatError('MAP ID archive/duplicate')
   w,h,offset=map_metadata(payload)
   maps[ref]=(w,h,offset,payload)
 if not portals:raise FormatError('empty Portals.tbl')
 flags=Counter();by_archive=Counter();used=set()
 for ref,x,y in portals:
  if ref not in maps:raise FormatError('portal references absent MAP')
  w,h,offset,data=maps[ref]
  if x>=w or y>=h:raise FormatError('portal coordinate out of bounds')
  rawflags,=struct.unpack_from('<I',data,offset+10*(x+y*w)+6)
  flags[rawflags]+=1;by_archive[f'Map{ref//10000}.dat']+=1;used.add(ref)
 return {
  'evidence_grade':'original-static-resource-crosscheck',
  'basic_index_members':len(members),'file_size_info_rows':len(manifest),
  'map_archive_member_counts':counts,'file_size_info_map_sizes_match':size_matches,
  'file_size_info_third_column':'unknown',
  'portal_table':{
   'version':version,'rows':len(portals),'distinct_map_refs':len(used),
   'map_archive_rows':dict(sorted(by_archive.items())),
   'missing_refs':0,'out_of_bounds':0,'duplicate_tuples':0,
   'raw_tile_flags_at_rows':dict(sorted(flags.items()))},
  'native_client_gui':'not-run','player_walkable':'unknown',
  'teleport_semantics':'not-proven','original_assets_exported':False,
 }

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--basic',type=Path,required=True)
 ap.add_argument('--map-dir',type=Path,required=True)
 ap.add_argument('--verify-original-sha',action='store_true')
 args=ap.parse_args()
 names=['Map0.dat','Map1.dat','Map2.dat']
 try:
  files={args.basic.name:args.basic.read_bytes()}
  files.update({n:(args.map_dir/n).read_bytes() for n in names})
  if args.basic.name!='Basic.dat':raise FormatError('expected Basic.dat')
  if args.verify_original_sha:
   for name,data in files.items():
    if hashlib.sha256(data).hexdigest()!=EXPECTED[name]:
     raise FormatError('wrong original SHA: '+name)
  result=audit_basic_and_maps(files['Basic.dat'],{n:files[n] for n in names})
 except (OSError,FormatError,UnicodeError,struct.error) as e:ap.error(str(e))
 result['sha256']={n:hashlib.sha256(b).hexdigest() for n,b in files.items()}
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
