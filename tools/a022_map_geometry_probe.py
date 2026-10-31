#!/usr/bin/env python3
"""A-022 MAP byte layout/geometry: original Map*.dat resource validation.
No official gameplay walkability/monster spawn/initial tutorial map inferred.
"""
from pathlib import Path
import hashlib,struct,unittest
ARCHIVE_SHA={
"Map0.dat":"dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761",
"Map1.dat":"8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b",
"Map2.dat":"5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb"}
def entries(data):
 if len(data)<8:raise ValueError("short archive")
 n,sz=struct.unpack_from("<II",data)
 if n<2 or n>10000 or sz!=4+36*n or 8+36*n>len(data):raise ValueError("bad directory")
 start=8+36*n
 out=[]
 for i in range(n-1):  # final slot is trailing non-map sentinel
  o=8+36*i;record=data[o:o+36];name=record[:10].split(b"\0")[0].decode("ascii","replace")
  end=struct.unpack_from("<I",record,32)[0]
  if not name.endswith(".map") or end<start or end>len(data):raise ValueError("bad map entry bounds")
  out.append((name,data[start:end]));start=end
 return out
def parse_tile_map(raw):
 if len(raw)<20:raise ValueError("short map")
 a,b,c,w,h=struct.unpack_from("<HHHBB",raw)
 if not (0<w<=255 and 0<h<=255):raise ValueError("zero size")
 block=2*((w+1)//2)*((h+3)//4);tile_off=8+block;after=tile_off+10*w*h
 if after+12>len(raw):raise ValueError("short tiles")
 pos=after;counts=[]
 for width in (7,8,16):
  if pos+4>len(raw):raise ValueError("short section count")
  n=struct.unpack_from("<I",raw,pos)[0];pos+=4
  if n>(len(raw)-pos)//width:raise ValueError("section overrun")
  counts.append(n);pos+=n*width
 if pos!=len(raw):raise ValueError("trailing bytes")
 return {"h0":a,"h1":b,"header2":c,"w":w,"h":h,"tile_offset":tile_off,"counts":counts}
def tile10(raw,meta,x,y):
 if not(type(x)==int and type(y)==int and 0<=x<meta["w"] and 0<=y<meta["h"]):raise ValueError("geometry out of range")
 p=meta["tile_offset"]+10*(y*meta["w"]+x)
 return raw[p:p+10]
def audit():
 result={}
 for filename,expect in ARCHIVE_SHA.items():
  raw=Path("/mnt/data",filename).read_bytes()
  if hashlib.sha256(raw).hexdigest()!=expect:raise ValueError("archive release mismatch")
  named=entries(raw);valid={};special=[]
  for name,payload in named:
   try:valid[name]=parse_tile_map(payload)
   except ValueError:special.append(name)
  result[filename]=(len(named),len(valid),special,valid)
 return result
class Tests(unittest.TestCase):
 def test_01_real_archives(self):
  if not all(Path("/mnt/data",f).exists() for f in ARCHIVE_SHA):self.skipTest("Map*.dat missing")
  res=audit()
  self.assertEqual([(len(res[n][3]),res[n][0]) for n in ARCHIVE_SHA],[(287,288),(183,184),(21,22)])
  self.assertEqual([res[n][2] for n in ARCHIVE_SHA],[["00000.map"],["10000.map"],["20000.map"]])
 def test_02_real_known_headers(self):
  if not Path("/mnt/data/Map0.dat").exists():self.skipTest("missing Map0.dat")
  d=Path("/mnt/data/Map0.dat").read_bytes();e=dict(entries(d))
  self.assertEqual((parse_tile_map(e["00006.map"])["w"],parse_tile_map(e["00006.map"])["h"],parse_tile_map(e["00006.map"])["header2"]),(60,60,4))
  self.assertEqual(parse_tile_map(e["00006.map"])["counts"],[7,0,0])
 def test_03_record_counts(self):
  if not Path("/mnt/data/Map2.dat").exists():self.skipTest("missing Map2.dat")
  e=dict(entries(Path("/mnt/data/Map2.dat").read_bytes()))
  self.assertEqual(parse_tile_map(e["21001.map"])["counts"],[303,3,31])
 def test_04_tile_geometry(self):
  if not Path("/mnt/data/Map0.dat").exists():self.skipTest("missing Map0.dat")
  e=dict(entries(Path("/mnt/data/Map0.dat").read_bytes()));r=e["00006.map"];m=parse_tile_map(r)
  self.assertEqual(len(tile10(r,m,31,29)),10)
  for x,y in [(-1,0),(0,-1),(60,0),(0,60),(999,999)]:
   with self.assertRaises(ValueError):tile10(r,m,x,y)
 def test_05_synthetic_exact_sections(self):
  header=struct.pack("<HHHBB",1,1,4,4,4)
  raw=header+b"\0"*4+b"\0"*160+struct.pack("<III",0,0,0)
  m=parse_tile_map(raw);self.assertEqual(m["tile_offset"],12)
  self.assertEqual(len(tile10(raw,m,1,3)),10)
 def test_06_reject_extra_and_truncate(self):
  raw=struct.pack("<HHHBB",1,1,4,4,4)+b"\0"*4+b"\0"*160+struct.pack("<III",0,0,0)
  for b in (raw[:-1],raw+b"\0"):
   with self.assertRaises(ValueError):parse_tile_map(b)
 def test_07_reject_zero_size(self):
  with self.assertRaises(ValueError):parse_tile_map(struct.pack("<HHHBB",1,2,3,0,2)+b"\0"*100)
 def test_08_reject_bad_directory(self):
  with self.assertRaises(ValueError):entries(struct.pack("<II",10,10)+b"\0"*500)
if __name__=="__main__":unittest.main(verbosity=2)
