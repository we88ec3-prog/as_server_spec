#!/usr/bin/env python3
"""A-023 original four Script dependency audit (read-only; no game assets committed).

Original metadata and native Script rules are kept separate from any inference
about first login, NPC binding, original Server policy or GUI E2E.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
import xml.etree.ElementTree as ET
import zlib

FILES = {
    "PaperDialog": ("5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054", 0xF870C574, 3),
    "PaperDialog02": ("49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a", 0x42683546, 3),
    "nNewJoin01": ("8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae", 0xD9390353, 23),
    "Merchant": ("6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350", 0xE9B389CF, 1),
}
BORN_SHA = "992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98"
BORN_CRC = 0x1D87B0C0

class ResourceError(ValueError):
    pass

def decode_script(blob):
    """Strict native BE u16 version + BE u32 UTF16 code units after zlib."""
    d=zlib.decompressobj()
    decoded=d.decompress(blob, 4*1024*1024)
    decoded+=d.flush()
    if not d.eof or d.unconsumed_tail or d.unused_data:
        raise ResourceError("compressed Script truncated/trailing/oversized")
    if len(decoded)<6:
        raise ResourceError("Script header too short")
    version,units=struct.unpack_from(">HI",decoded)
    if version!=1 or len(decoded)!=6+2*units:
        raise ResourceError("invalid native version or UTF16 code-unit length")
    xml=decoded[6:].decode("utf-16le",errors="strict")
    root=ET.fromstring(xml)
    if root.tag!="script":
        raise ResourceError("wrong XML Script root")
    functions={}
    for f in root.findall("function"):
        name=f.get("name")
        if not name or name in functions:
            raise ResourceError("missing/duplicate Script function name")
        functions[name]=f.text or ""
    return {
        "unpacked_size":len(decoded),
        "utf16_code_units":units,
        "text_crc32_cp950":zlib.crc32(xml.encode("cp950",errors="strict")),
        "functions":functions,
        "xml_sha256":hashlib.sha256(decoded).hexdigest(),
    }

def check_exact_resource(directory,name):
    raw=Path(directory,name+".dat").read_bytes()
    expected,crc,count=FILES[name]
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ResourceError(name+": SHA256 not matching original release sample")
    doc=decode_script(raw)
    if doc["text_crc32_cp950"]!=crc or len(doc["functions"])!=count:
        raise ResourceError(name+": text CRC/function count mismatch")
    return doc,{"filename":name+".dat","raw_size":len(raw),
                "raw_sha256":expected,"text_crc32_cp950":f"{crc:08x}",
                "function_count":count,"utf16_code_units":doc["utf16_code_units"],
                "unpacked_size":doc["unpacked_size"],
                "unpacked_sha256":doc["xml_sha256"]}

def assert_has(text,*needles):
    for needle in needles:
        if needle not in text:
            raise ResourceError("required executable Script statement missing: "+needle[:36])

def callback_body(text,control):
    m=re.search(r'\bcase\s+"'+re.escape(control)+r'"\s*\{([^{}]*)\}',text,re.S)
    if not m:
        raise ResourceError("missing callback branch: "+control)
    return m.group(1)

def assert_order(text,*needles):
    offsets=[text.find(x) for x in needles]
    if -1 in offsets or offsets!=sorted(offsets) or len(set(offsets))!=len(offsets):
        raise ResourceError("required Script callback order missing")

def inspect_functions(docs):
    """Evidence limited to actual XML function definitions and references."""
    a=docs["PaperDialog"]["functions"]
    b=docs["PaperDialog02"]["functions"]
    n=docs["nNewJoin01"]["functions"]
    m=docs["Merchant"]["functions"]
    if set(a)!={"PaperDialog_Create","ShowIndexedHelp","PaperDialogProc"}:
        raise ResourceError("PaperDialog function set")
    if set(b)!={"PaperDialog02_Create","ShowIndexedHelp","PaperDialogProc"}:
        raise ResourceError("PaperDialog02 function set")
    if set(m)!={"Main"}:
        raise ResourceError("Merchant root Main missing")
    if "Main" in n or "Main" in b or "Main" in a:
        raise ResourceError("unexpected standalone Main in dependency")
    assert_has(a["PaperDialog_Create"],'dialog.onControlClick = "PaperDialogProc"',
               'pane.SetImage("Basic.dat", "AlertFrame.ypf", 0)',
               'dialog.cancelControl', 'dialog.defaultControl', 'ShowIndexedHelp(dialog, 0)')
    assert_has(callback_body(a["PaperDialogProc"],"OK"),"dialog.Dispose()","client.Dispose()")
    if "SendReply" in a["PaperDialogProc"]:
        raise ResourceError("original PaperDialog unexpectedly sends reply")
    assert_has(b["PaperDialog02_Create"],'dialog.onControlClick = "PaperDialogProc"',
               'pane.SetImage("Basic.dat", "AlertFrame.ypf", 0)',
               'dialog.cancelControl', 'dialog.defaultControl',
               'CancelObject= 14', 'ShowIndexedHelp(dialog, 0)')
    if not re.search(r'dialog\.cancelControl\s*=\s*"OK"',b["PaperDialog02_Create"]):
        raise ResourceError("PaperDialog02 original keyboard cancel target changed")
    for control,value in (("OK","START"),("CANCEL","NOT")):
        segment=callback_body(b["PaperDialogProc"],control)
        assert_has(segment,f'ClientReply.Add("PAPER02", "{value}")')
        assert_order(segment,"ClientReply.Add","client.SendReply","dialog.Dispose","client.Dispose")
    if n.get("DoesTalk","").strip()!="return true;":
        raise ResourceError("nNewJoin DoesTalk is not true")
    for f in ("DoesBuy","DoesSell","DoesRepair","DoesBank","DoesIdentify"):
        if n.get(f,"").strip()!="return false;":
            raise ResourceError("nNewJoin non-talk function unexpected")
    assert_has(n["MerchantTalk"],"JoinMessage01()")
    for i in (1,2,3):
        assert_has(n[f"JoinMessage0{i}"],"QuestDialog_Create(",
                   f'"JoinMessage0{i}Proc"')
    assert_has(callback_body(n["JoinMessage01Proc"],"NEXT"),"JoinMessage02()")
    assert_has(callback_body(n["JoinMessage02Proc"],"NEXT"),"JoinMessage03()")
    assert_has(callback_body(n["JoinMessage02Proc"],"PREV"),"JoinMessage01()")
    assert_has(callback_body(n["JoinMessage03Proc"],"PREV"),"JoinMessage02()")
    for control,value in (("OK","ACCEPT"),("CANCEL","REFUSE")):
        segment=callback_body(n["JoinMessage03Proc"],control)
        assert_has(segment,f'ClientReply.Add("STATE", "{value}")')
        assert_order(segment,"ClientReply.Add","client.SendReply","dialog.Dispose","client.Dispose")
    assert_has(m["Main"],'client.AddGlobal("ServerParam", args)',
               'client.CreateParams()', 'client.AddGlobal("ClientReply", reply)',
               'args.Get("TILE")','args.Get("MNAME")',
               'args.Get("UGOLD")','args.Get("UBAL")',
               'args.Get("UAGOLD")','args.Get("UABAL")',
               'args.Get("UCOLOR")',
               'args.Has("GREETING")','args.Has("TYPE")',
               'DoesTalk()', 'MerchantDialog_Create(', 'MerchantDirectTalk()')
    collision=sorted(set(a)&set(b))
    if collision!=["PaperDialogProc","ShowIndexedHelp"]:
        raise ResourceError("common callback function collision changed")
    # Do not claim that a missing external function is a proven filename.
    defined=set().union(*(set(v["functions"]) for v in docs.values()))
    missing=[x for x in ("QuestDialog_Create","MerchantDialog_Create",
                        "MerchantDirectTalk") if x not in defined]
    if len(missing)!=3:
        raise ResourceError("unexpectedly defined previously external helper")
    return {
        "standalone_script_roots":["Merchant"],
        "helper_only":["PaperDialog","PaperDialog02","nNewJoin01"],
        "paper_ok":"Dispose; native C6C(4) then C6C(2) when no reply",
        "paper02_decisions":{"OK":"PAPER02=START","CANCEL":"PAPER02=NOT"},
        "paper02_cancel_control":"OK (ESC/cancel-key may follow OK; runtime not tested)",
        "newjoin_path":"MerchantTalk → JoinMessage01 → 02 → 03; STATE=ACCEPT or REFUSE",
        "merchant_globals":["ServerParam","ClientReply"],
        "merchant_main_parameters":["TILE","MNAME","UGOLD","UBAL","UAGOLD","UABAL","UCOLOR",
                                    "GREETING (optional)","TYPE (optional)"],
        "unresolved_external_function_names":missing,
        "unverified_external_source_filenames":True,
        "conflicting_imported_function_names":collision,
        "shared_import_conflict_policy":"Do NOT include PaperDialog and PaperDialog02 unconditionally in same runner",
        "c6c_name_source":"Root ScriptRunner issued by S44, NOT inferred from dependency file name",
        "reply_vs_close":"SendReply implies native C6C(1) then Dispose C6C(4), not unreplied C6C(2)",
        "original_recruiter_entity_binding":"unknown",
        "original_first_script_issue_policy":"unknown",
        "quest_completion_or_reward":"not proven",
        "original_gui_runtime":"not-run",
    }

def make_reply_fixture(root_name,context,key,value):
    """Synthetic decoded C6C(1), not original Server packet. ASCII only."""
    if type(context) is not int or not 0<=context<=0xffffffff:
        raise ResourceError("context u32")
    def s8(s):
        if not isinstance(s,str):
            raise ResourceError("expected string")
        b=s.encode("cp950")
        if len(b)>255:
            raise ResourceError("encoded string8 >255")
        return bytes([len(b)])+b
    return (b"\x01"+s8(root_name)+context.to_bytes(4,"big")+
            b"\x00\x01"+s8(key)+s8(value))

def audit(directory, born_path=None):
    docs={}; metas=[]
    for name in FILES:
        doc,meta=check_exact_resource(directory,name)
        docs[name]=doc;metas.append(meta)
    findings=inspect_functions(docs)
    if born_path is not None:
        data=Path(born_path).read_bytes()
        if hashlib.sha256(data).hexdigest()!=BORN_SHA:
            raise ResourceError("Born SHA changed")
        born=decode_script(data)
        if born["text_crc32_cp950"]!=BORN_CRC:
            raise ResourceError("Born CP950 text CRC mismatch")
        assert_has(born["functions"].get("Main",""),'PaperDialog_Create("", page)')
        findings["born_main_to_paper_verified"]=True
    return {
        "result":"PASS","kind":"original-four-Script-files-plus-synthetic-replies",
        "script_resources":metas,"findings":findings,
        "synthetic_context":"0x11223344; NO original Server capture",
        "synthetic_c6c1_root_merchant_accept":make_reply_fixture(
            "Merchant",0x11223344,"STATE","ACCEPT").hex(),
        "synthetic_c6c1_root_merchant_refuse":make_reply_fixture(
            "Merchant",0x11223344,"STATE","REFUSE").hex(),
        "synthetic_c6c1_root_example_paper02":make_reply_fixture(
            "Merchant",0x11223344,"PAPER02","START").hex(),
        "native_client_validation":"not-run"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--script-dir",type=Path,required=True)
    p.add_argument("--born",type=Path)
    a=p.parse_args()
    try:
        print(json.dumps(audit(a.script_dir,a.born),ensure_ascii=False,indent=2))
    except (OSError,ValueError,zlib.error,ET.ParseError,UnicodeError,struct.error) as e:
        p.exit(1,"FAIL A-023 Script bundle: "+str(e)+"\n")
