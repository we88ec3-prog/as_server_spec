#!/usr/bin/env python3
"""A-015 MAP field audit: private asset input, aggregate metadata output only."""
import argparse
import json
import struct
from collections import Counter
from pathlib import Path

def inspect_archive(path):
    data=path.read_bytes()
    if len(data)<40: raise ValueError("short archive")
    n=struct.unpack_from("<I",data,0)[0]
    if not 1<n<=200000 or 4+36*n>len(data): raise ValueError("invalid slots")
    offsets=[struct.unpack_from("<I",data,4+36*i)[0] for i in range(n)]
    if offsets[0]!=4+36*n or offsets[-1]!=len(data) or offsets!=sorted(offsets):
        raise ValueError("invalid archive offsets")
    h01=diff=maps=bounds=0; counts=[0,0,0]; with_records=[0,0,0]
    flag7=Counter(); tuples=Counter(); p8ok=p8total=p16ok=p16total=x8=y8=0
    for i in range(n-1):
        name=data[8+36*i:40+36*i].split(b"\0",1)[0]
        if len(name)!=9 or name[-4:].lower()!=b".map" or not name[:5].isdigit():
            raise ValueError("unexpected member name")
        b=memoryview(data)[offsets[i]:offsets[i+1]]
        if len(b)<8: raise ValueError("truncated MAP header")
        h0,h1,h2,w,h=struct.unpack_from("<HHHBB",b,0)
        if not w or not h: raise ValueError("invalid dimensions")
        maps+=1;h01+=h0==h1;diff+=h1!=h2
        if h1!=h2:tuples[f"{h0},{h1},{h2}"]+=1
        bounds+=w>31 and h>29
        pos=8+((w+1)//2)*((h+3)//4)*2+w*h*10
        for index,stride in enumerate((7,8,16)):
            if pos+4>len(b): raise ValueError("truncated tail count")
            amount=struct.unpack_from("<I",b,pos)[0];pos+=4
            if amount>(len(b)-pos)//stride:raise ValueError("tail out of bounds")
            counts[index]+=amount;with_records[index]+=amount>0
            for k in range(amount):
                p=pos+k*stride
                if stride==7: flag7[b[p]]+=1
                elif stride==8:
                    _,x,y,_=struct.unpack_from("<HHHH",b,p)
                    p8total+=1;p8ok+=x<w*48 and y<h*32
                else:
                    _,_,_,_,x,y=struct.unpack_from("<HHIIHH",b,p)
                    p16total+=1;p16ok+=x<w*48 and y<h*32
                    x8+=x%8==0;y8+=y%8==0
            pos+=amount*stride
        if pos!=len(b):raise ValueError("MAP trailing bytes")
    return dict(file=path.name,maps=maps,header_first_two_equal=h01,
                header_third_differs=diff,header_mismatch_tuples=dict(tuples),
                candidate_31_29_in_bounds=bounds,tail_count_7_8_16=counts,
                maps_with_tail_7_8_16=with_records,
                seven_byte_first_flag={str(k):v for k,v in sorted(flag7.items())},
                tail8_pixel_bounds_pass=p8ok,tail8_records=p8total,
                tail16_pixel_bounds_pass=p16ok,tail16_records=p16total,
                tail16_x_multiple_8=x8,tail16_y_multiple_8=y8)

def audit(files):
    reports=[inspect_archive(Path(x)) for x in files]
    keys=("maps","header_first_two_equal","header_third_differs",
          "candidate_31_29_in_bounds","tail8_pixel_bounds_pass",
          "tail8_records","tail16_pixel_bounds_pass","tail16_records",
          "tail16_x_multiple_8","tail16_y_multiple_8")
    totals={k:sum(r[k] for r in reports) for k in keys}
    for field in ("tail_count_7_8_16","maps_with_tail_7_8_16"):
        totals[field]=[sum(r[field][i] for r in reports) for i in range(3)]
    flags=Counter();tuples=Counter()
    for report in reports:
        flags.update(report["seven_byte_first_flag"])
        tuples.update(report["header_mismatch_tuples"])
    totals["seven_byte_first_flag"]=dict(flags)
    totals["header_mismatch_tuples"]=dict(tuples)
    return dict(schema_version=1,files=reports,totals=totals,
                exe_accessors={"tail7":"0x4B2D70","tail8":"0x4B2DE0","tail16":"0x4B2E40"},
                field_types={"tail7":"bool(normalized u8), LE u16, LE i16, LE i16",
                             "tail8":"4 LE u16",
                             "tail16":"LE u16,u16,u32,u32,u16,u16"},
                pixel_bounds_hypothesis="x < width*48 and y < height*32 at tail8(+2,+4) / tail16(+12,+14)",
                confidence="byte layout observed-static; pixel-coordinate interpretation inferred",
                not_proven=["NPC spawn or identity","native tutorial map","collision or walkability",
                            "original release/version match","native Client E2E"],
                raw_game_assets_exported=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives",nargs=3,type=Path)
    parser.add_argument("--json",type=Path)
    args=parser.parse_args()
    result=json.dumps(audit(args.archives),ensure_ascii=False,indent=2)+"\n"
    print(result,end="")
    if args.json:args.json.write_text(result,encoding="utf-8")

if __name__=="__main__":
    main()
