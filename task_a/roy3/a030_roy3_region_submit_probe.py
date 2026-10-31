#!/usr/bin/env python3
"""A030 roy3: original EXE region1 F3 source mismatch, scoped EMAIL submit check.
Static-only evidence. No original Client GUI, TCP session or Server status capture.
"""
import argparse,hashlib,json,struct
from pathlib import Path
EXE_SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
BASIC_SHA="0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96"
LOCALE_SHA="813f2800696555f16ec6c4bfc5975b649332340b5a6975d7aeba4c4e77380161"
ANCHORS={
 "region0 F3 UI+424":(0x4b2839,"8b565868ff00000081c224040000"),
 "region4 F3 UI+624":(0x4b2870,"81c124060000"),
 "region4 F4 UI+822":(0x4b288f,"81c222080000"),
 "region1/2/3 widget15 F3 UI+624":(0x4b289d,"0524060000506a0f"),
 "region1/2/3 widget16 F4 UI+822":(0x4b28bb,"81c122080000516a10"),
 "region0 submit branch":(0x4b281c,"e8df57feff85c07533"),
 "region4 submit branch":(0x4b2863,"83f804"),
 "submit validator uses F1":(0x4b28e6,"8b56585583c22452"),
 "submit F1 checker":(0x4b28f0,"e83bf1ffff"),
 "submit F2 vs CONFIRM":(0x4b2900,"8d4424145081c124020000"),
 "submit F2 comparer":(0x4b290c,"e851211000"),
 "submit compare decision":(0x4b2914,"85c0756b"),
 "region0 confirmation F3+424":(0x4b2407,"8b47580524040000"),
 "region1/2/3/4 confirmation F3+624":(0x4b24e1,"8b475883c4100524060000"),
 "region1/2/3/4 confirmation F4+822":(0x4b2509,"8b575883c41081c222080000"),
 "confirmation NAME key73":(0x4b24ed,"6a49"),
 "confirmation EMAIL key75":(0x4b2516,"6a4b"),
 "confirm C02 enqueue":(0x4b229f,"e8fc650c00"),
 "C02 extended region min2":(0x5742ec,"83f802"),
 "C02 extended region max4":(0x5742f1,"83f804"),
 "C02 extended F3 writer+618":(0x5742f6,"8dbe18060000"),
 "C02 extended F4 writer+816":(0x57430e,"8dbe16080000"),
 "C02 region0/1 F3 writer+418":(0x574338,"8dbe18040000"),
 "C02 extended flag":(0x574326,"0fb686160a0000"),
 "S02 status reader":(0x57dbc3,"e8e8d1edff"),
 "S02 message reader":(0x57dbd8,"e8c3dbedff"),
 "S02 text nonempty":(0x4b1dff,"66837f2600"),
 "S02 message dialog":(0x4b1ebe,"e8ad06f9ff"),
 "S02 region3 state1E suppress":(0x4b1e1e,"83f803"),
 "S02 nonzero branch":(0x4b1eec,"84c0"),
 "S02 failure sends C15":(0x4b1f2f,"e86c690c00"),
 "S02 failure enters 1F":(0x4b1f34,"c7464c1f000000"),
 "C15 opcode":(0x571609,"6a15"),
 "C15 empty writer":(0x5716a0,"c3"),
}
def read_va(raw):
 if raw[:2]!=b"MZ":raise ValueError("not MZ")
 pe=struct.unpack_from("<I",raw,0x3c)[0]
 if raw[pe:pe+4]!=b"PE\0\0":raise ValueError("not PE")
 n=struct.unpack_from("<H",raw,pe+6)[0];opt=pe+24
 if struct.unpack_from("<H",raw,opt)[0]!=0x10b:raise ValueError("not PE32")
 base=struct.unpack_from("<I",raw,opt+28)[0]
 sec=opt+struct.unpack_from("<H",raw,pe+20)[0]
 areas=[]
 for i in range(n):
  vs,rva,rs,fo=struct.unpack_from("<IIII",raw,sec+40*i+8)
  areas.append((base+rva,min(vs,rs),fo))
 def read(va,nbytes):
  for start,n,fo in areas:
   if start<=va and va+nbytes<=start+n:
    return raw[fo+va-start:fo+va-start+nbytes]
  raise ValueError("unmapped VA "+hex(va))
 return read
def verify_exe(path):
 raw=Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXE_SHA:raise ValueError("Client SHA mismatch")
 read=read_va(raw)
 for name,(va,hx) in ANCHORS.items():
  if read(va,len(hx)//2)!=bytes.fromhex(hx):raise ValueError("native bytes mismatch "+name)
 # Only assert absence of a direct F4 address in the local final submit guard;
 # no conclusion on other GUI events, empty field or actual TCP frames.
 guard=read(0x4b28d2,0x4b2918-0x4b28d2)
 if bytes.fromhex("22080000") in guard or bytes.fromhex("24060000") in guard:
  raise ValueError("unexpected extra field access in submit guard")
 return {"sha256":EXE_SHA,"original_anchor_count":len(ANCHORS),
         "region1_copied_F3":"packet+0x624","region1_serialized_F3":"packet+0x424",
         "region1_F3_mismatch":True,"final_submit_explicit_F4_nonempty_guard":"not observed",
         "native_GUI":"not-run"}
def region_fields(region):
 if type(region)!=int or region not in range(5):raise ValueError("region0..4")
 if region==0:return {"F3_UI":"+0x424","F3_wire":"+0x424","F4_wire":None}
 if region==1:return {"F3_UI":"+0x624","F3_wire":"+0x424","F4_UI":"+0x822","F4_wire":None}
 return {"F3_UI":"+0x624","F3_wire":"+0x624","F4_UI":"+0x822","F4_wire":"+0x822","tail":"u8"}
def basic_member(raw,name):
 if len(raw)<4:raise ValueError("short DAT")
 count=struct.unpack_from("<I",raw)[0]
 if not 1<=count<=4096 or len(raw)<8+36*count:raise ValueError("invalid DAT directory")
 entries=[]
 for i in range(count):
  off=8+i*36
  label=raw[off:off+32].split(b"\0")[0].decode("ascii")
  end=struct.unpack_from("<I",raw,off+32)[0]
  entries.append((label,end))
 ids=[i for i,(label,_) in enumerate(entries) if label==name]
 if len(ids)!=1:raise ValueError("ambiguous member")
 idx=ids[0];begin=entries[idx-1][1] if idx else 8+36*count;end=entries[idx][1]
 if not begin<end<=len(raw):raise ValueError("out of range")
 return raw[begin:end]
def verify_labels(basic,locale):
 b=Path(basic).read_bytes();l=Path(locale).read_bytes()
 if hashlib.sha256(b).hexdigest()!=BASIC_SHA or hashlib.sha256(l).hexdigest()!=LOCALE_SHA:
  raise ValueError("Basic/Locale SHA mismatch")
 def strings(name):
  raw=basic_member(b,name)
  if not raw.startswith(bytes.fromhex("fffe")):raise ValueError("not UTF16LE")
  items={}
  for line in raw.decode("utf-16").splitlines():
   key,sep,val=line.partition(" ")
   if sep and key.isdecimal():items.setdefault(int(key),val)
  return items
 base,skin=strings("BasicString.txt"),strings("SkinString.txt")
 for rows,key,val in ((base,73,"NAME"),(base,75,"E-MAIL"),(skin,2153,"名字"),(skin,2154,"E-Mail")):
  if rows.get(key)!=val:raise ValueError("label mismatch")
 return {"NAME":"BasicString[73]/SkinString[2153]","EMAIL":"BasicString[75]/SkinString[2154]"}
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--exe",required=True);ap.add_argument("--basic",required=True);ap.add_argument("--locale",required=True)
 a=ap.parse_args()
 print(json.dumps({"native":verify_exe(a.exe),"labels":verify_labels(a.basic,a.locale),
                   "regions":{i:region_fields(i) for i in range(5)}},ensure_ascii=False,indent=2))
