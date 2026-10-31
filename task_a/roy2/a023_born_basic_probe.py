#!/usr/bin/env python3
"""A-023 read-only Born.dat+Basic.dat original-resource dependency check.

Verifies release-locked SHA and DAT member metadata, not game UI rendering.
If PaperDialog.dat is not provided, its original bytes are NOT reverified.
"""
import argparse
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

BORN_SHA = "992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98"
BASIC_SHA = "0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96"
FRAME_SHA = "b641441d1f0378de04b6f7929c333d95e6ad7df451f3927432e5c4d0305602ce"
PAPER_SHA = "5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054"

def sha256(blob):
    return hashlib.sha256(blob).hexdigest()

def checked_original(path, sha):
    data = Path(path).read_bytes()
    if sha256(data) != sha:
        raise ValueError(Path(path).name + ": resource SHA256 mismatch")
    return data

def index_dat_bytes(blob, *, validate_release=True):
    if len(blob) < 4:
        raise ValueError("short DAT header")
    slots, = struct.unpack_from("<I", blob)
    if slots < 2 or slots > 100000 or 4 + slots*36 > len(blob):
        raise ValueError("invalid DAT slot count/header length")
    header_end = 4 + slots*36
    entries = []
    for i in range(slots):
        o = 4 + 36*i
        off, = struct.unpack_from("<I",blob,o)
        name = blob[o+4:o+36].split(b"\0",1)[0]
        entries.append((off,name))
    if entries[0][0] != header_end or entries[-1][0] != len(blob):
        raise ValueError("DAT header or EOF sentinel mismatch")
    result = {}
    for i in range(slots-1):
        start,namebytes = entries[i]
        end = entries[i+1][0]
        if not header_end <= start < end <= len(blob):
            raise ValueError("empty/overlapping/invalid DAT member offset")
        if not namebytes or b"/" in namebytes or b"\\" in namebytes:
            raise ValueError("invalid DAT member name")
        name = namebytes.decode("cp949",errors="strict")
        if name in result:
            raise ValueError("duplicate member")
        result[name] = (start,end-start)
    if validate_release and slots != 39:
        raise ValueError("Basic.dat expected 39 index slots")
    return result

def read_script_xml(blob):
    d = zlib.decompressobj()
    payload = d.decompress(blob, 8*1024*1024) + d.flush()
    if not d.eof or d.unused_data or d.unconsumed_tail:
        raise ValueError("Script truncated/trailing/oversized zlib")
    if len(payload) < 6:
        raise ValueError("short Script")
    version,units = struct.unpack_from(">HI",payload)
    if version != 1 or len(payload) != 6 + 2*units:
        raise ValueError("Script native version/UTF16 units invalid")
    text = payload[6:].decode("utf-16le",errors="strict")
    root = ET.fromstring(text)
    if root.tag != "script":
        raise ValueError("invalid Script XML root")
    return text,root

def verify(born, basic, paper=None):
    born_blob = checked_original(born,BORN_SHA)
    born_xml,born_root = read_script_xml(born_blob)
    f = born_root.findall("function")
    if len(f)!=1 or f[0].get("name")!="Main":
        raise ValueError("Born Main changed")
    body = f[0].text or ""
    for literal in ('client.CreateArray()', 'page.Insert(msg)',
                    'PaperDialog_Create("", page)', '(31,29)', '招募員'):
        if literal not in body:
            raise ValueError("Born guidance missing")
    crc = zlib.crc32(born_xml.encode("cp950",errors="strict"))
    if crc != 0x1D87B0C0:
        raise ValueError("Born text CRC changed")
    basic_blob = checked_original(basic,BASIC_SHA)
    members = index_dat_bytes(basic_blob)
    if "AlertFrame.ypf" not in members:
        raise ValueError("Basic.dat lacks AlertFrame.ypf")
    offset,size = members["AlertFrame.ypf"]
    frame = basic_blob[offset:offset+size]
    if sha256(frame)!=FRAME_SHA:
        raise ValueError("AlertFrame.ypf SHA mismatch")
    if len(frame)<16:
        raise ValueError("truncated YPF")
    version,width,height = struct.unpack_from("<HHH",frame)
    if version!=17:
        raise ValueError("unknown YPF version")
    output = {
        "result":"PASS", "scope":"original-resource-offline-no-GUI",
        "born":{"sha256":BORN_SHA,"size":len(born_blob),"entry":"Main",
                "text_crc32_cp950":f"{crc:08x}","waypoint_text_only":[31,29],
                "requires_paper_dialog":True},
        "basic":{"sha256":BASIC_SHA,"size":len(basic_blob),
                 "slots_including_sentinel":len(members)+1,"members":len(members),
                 "AlertFrame.ypf":{"offset":offset,"size":size,"sha256":FRAME_SHA,
                                   "version":version,
                                   "header_dimensions_only":[width,height]}},
        "paper_dependency":"not-provided-in-this-verification",
        "native_original_first_push":"unknown", "native_recruiter_entity":"unknown",
        "native_client_validation":"not-run",
    }
    if paper is not None:
        data = checked_original(paper,PAPER_SHA)
        _,root = read_script_xml(data)
        names = [node.get("name") for node in root.findall("function")]
        if len(names)!=3 or set(names)!={"PaperDialog_Create","ShowIndexedHelp","PaperDialogProc"}:
            raise ValueError("PaperDialog functions changed")
        output["paper_dependency"]="sha-and-functions-verified"
        output["paper_sha256"]=PAPER_SHA
    return output

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--born",type=Path,required=True)
    parser.add_argument("--basic",type=Path,required=True)
    parser.add_argument("--paper",type=Path)
    a=parser.parse_args()
    try:
        print(json.dumps(verify(a.born,a.basic,a.paper),ensure_ascii=False,indent=2))
    except (OSError,ValueError,UnicodeError,zlib.error,ET.ParseError) as e:
        parser.exit(1,"FAIL A-023: "+str(e)+"\n")
