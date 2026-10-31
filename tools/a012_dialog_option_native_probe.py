#!/usr/bin/env python3
"""A012 original Script option/lifecycle resource proof; no native GUI or Server claim."""
import hashlib, os, re, struct, unittest, xml.etree.ElementTree as ET, zlib
from pathlib import Path

HASH={
"Asgard.exe":"db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145",
"Born.dat":"992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98",
"PaperDialog.dat":"5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054",
"PaperDialog02.dat":"49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a",
"nNewJoin01.dat":"8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae",
}
CRC={"Born.dat":0x1d87b0c0,"PaperDialog.dat":0xf870c574,
"PaperDialog02.dat":0x42683546,"nNewJoin01.dat":0xd9390353}
FUNCS={
"Born.dat":["Main"],
"PaperDialog.dat":["PaperDialog_Create","ShowIndexedHelp","PaperDialogProc"],
"PaperDialog02.dat":["PaperDialog02_Create","ShowIndexedHelp","PaperDialogProc"],
"nNewJoin01.dat":["DoesBuy","DoesSell","DoesRepair","DoesBank","DoesIdentify","DoesTalk",
"BuildMuttering","LoadBuyMessage","LoadSellMessage","LoadRepairMessage","LoadDGMessage",
"LoadWGMessage","LoadDIMessage","LoadWIMessage","LoadIdentifyMessage","LoadTalkMessage",
"MerchantTalk","JoinMessage01","JoinMessage01Proc","JoinMessage02","JoinMessage02Proc",
"JoinMessage03","JoinMessage03Proc"]}
X86={
"C6C ctor":(0x575159,"6a6c"),"C6C reply subtype1":(0x51aa5c,"c6462401"),
"SendReply dispatch":(0x526626,"6870df6000"),"replied flag":(0x51ab33,"c7873c02000001000000"),
"Dispose subtype4":(0x5268c6,"c6462404"),"unreplied subtype2":(0x5194ce,"c6462402"),
"reply paircount":(0x57525c,"0fb78e20020000"),"reply pair array":(0x575280,"8bbe24020000"),
"S44 ctor":(0x5862f9,"6a44")}

def path(name):
    return Path(os.environ.get("ASGARD_"+name.replace(".","_").upper(),"/mnt/data/"+name))
def load(name):
    file=path(name)
    if not file.is_file():raise FileNotFoundError(file)
    data=file.read_bytes()
    if hashlib.sha256(data).hexdigest()!=HASH[name]:raise ValueError(name+" SHA")
    return data
def parse(name):
    raw=zlib.decompress(load(name))
    if len(raw)<6:raise ValueError("header")
    version,n=struct.unpack_from(">HI",raw)
    if version!=1 or len(raw)!=6+2*n:raise ValueError("wrapper")
    xml=raw[6:].decode("utf-16le")
    if zlib.crc32(xml.encode("cp950"))!=CRC[name]:raise ValueError("text CRC")
    root=ET.fromstring(xml)
    if root.tag!="script":raise ValueError("XML root")
    funcs={f.get("name"):f.text or "" for f in root.findall("function")}
    if list(funcs)!=FUNCS[name]:raise ValueError("function inventory")
    return funcs
def block(src,name):
    match=re.search(r'case\s+"'+re.escape(name)+r'"\s*\{',src)
    if not match:raise ValueError("control missing "+name)
    depth=1;pos=match.end();start=pos
    while pos<len(src) and depth:
        if src[pos]=="{":depth+=1
        elif src[pos]=="}":depth-=1
        pos+=1
    if depth:raise ValueError("unbalanced case")
    return src[start:pos-1]
def option(src,key):
    body=block(src,key)
    match=re.search(r'ClientReply\.Add\("([^"]+)",\s*"([^"]+)"\)',body)
    if not match or "client.SendReply(ClientReply)" not in body:raise ValueError("not SendReply")
    if not body.index("client.SendReply(ClientReply)")<body.index("dialog.Dispose()")<body.index("client.Dispose()"):
        raise ValueError("wrong lifecycle order")
    return match.groups()
def string8(value):
    data=value.encode("cp950")
    if not data or len(data)>255:raise ValueError("string8")
    return bytes([len(data)])+data
def reply(name,context,key,val):
    if type(context)!=int or not 0<=context<=0xffffffff:raise ValueError("context")
    return b"\x01"+string8(name)+struct.pack(">IH",context,1)+string8(key)+string8(val)
def verify_original():
    exe=load("Asgard.exe")
    for name,(va,hex_) in X86.items():
        b=bytes.fromhex(hex_)
        if exe[va-0x400000:va-0x400000+len(b)]!=b:raise ValueError("x86: "+name)
    born,plain,choice,join=(parse(n) for n in CRC)
    if "PaperDialog_Create" not in born["Main"] or "PaperDialog02_Create" in born["Main"]:raise ValueError("Born dependency")
    if "SendReply" in plain["PaperDialogProc"]:raise ValueError("Plain PaperDialog unexpected reply")
    if not block(plain["PaperDialogProc"],"OK").index("dialog.Dispose()")<block(plain["PaperDialogProc"],"OK").index("client.Dispose()"):
        raise ValueError("plain close order")
    if "dialog.AppendControl(button, \"CANCEL\")" not in choice["PaperDialog02_Create"]:raise ValueError("missing CANCEL")
    if 'dialog.cancelControl\t= "OK"' not in choice["PaperDialog02_Create"]:raise ValueError("cancelControl is not OK")
    if option(choice["PaperDialogProc"],"OK")!=("PAPER02","START"):raise ValueError("PAPER02 START")
    if option(choice["PaperDialogProc"],"CANCEL")!=("PAPER02","NOT"):raise ValueError("PAPER02 NOT")
    if "Main" in join or "JoinMessage01()" not in join["MerchantTalk"]:raise ValueError("not Merchant hook")
    if option(join["JoinMessage03Proc"],"OK")!=("STATE","ACCEPT"):raise ValueError("STATE ACCEPT")
    if option(join["JoinMessage03Proc"],"CANCEL")!=("STATE","REFUSE"):raise ValueError("STATE REFUSE")
    for name in ("DoesBuy","DoesSell","DoesRepair","DoesBank","DoesIdentify"):
        if "return false;" not in join[name]:raise ValueError("merchant feature flag")
    if "return true;" not in join["DoesTalk"]:raise ValueError("no MerchantTalk")
    return len(X86)

class TestA012(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not all(path(n).is_file() for n in HASH):raise unittest.SkipTest("Original assets absent; do not misreport as PASS")
    def test_01_sha_and_native(self):self.assertEqual(verify_original(),9)
    def test_02_four_crc_and_xml(self):
        for name in CRC:self.assertEqual(list(parse(name)),FUNCS[name])
    def test_03_born_paper_one_page(self):
        self.assertIn("page.Insert(msg)",parse("Born.dat")["Main"])
        self.assertIn("(31,29)",parse("Born.dat")["Main"])
    def test_04_plain_close_no_reply(self):
        self.assertNotIn("client.SendReply",parse("PaperDialog.dat")["PaperDialogProc"])
    def test_05_paper02_yes(self):self.assertEqual(option(parse("PaperDialog02.dat")["PaperDialogProc"],"OK"),("PAPER02","START"))
    def test_06_paper02_no(self):self.assertEqual(option(parse("PaperDialog02.dat")["PaperDialogProc"],"CANCEL"),("PAPER02","NOT"))
    def test_07_join_yes(self):self.assertEqual(option(parse("nNewJoin01.dat")["JoinMessage03Proc"],"OK"),("STATE","ACCEPT"))
    def test_08_join_no(self):self.assertEqual(option(parse("nNewJoin01.dat")["JoinMessage03Proc"],"CANCEL"),("STATE","REFUSE"))
    def test_09_join_no_main(self):self.assertNotIn("Main",parse("nNewJoin01.dat"))
    def test_10_c6c1_accept_fixture(self):
        self.assertEqual(reply("nNewJoin01",0x11223344,"STATE","ACCEPT").hex(),
          "010a6e4e65774a6f696e303111223344000105535441544506414343455054")
    def test_11_c6c1_refuse_fixture(self):self.assertTrue(reply("nNewJoin01",0x11223344,"STATE","REFUSE").endswith(b"\x06REFUSE"))
    def test_12_paper02_bodies(self):
        for val in ("START","NOT"):self.assertIn(b"PAPER02",reply("PaperDialog02",0,"PAPER02",val))
    def test_13_reject_context(self):
        with self.assertRaises(ValueError):reply("Born",-1,"STATE","ACCEPT")
    def test_14_reject_overflow(self):
        with self.assertRaises(ValueError):string8("A"*256)
    def test_15_reject_no_case(self):
        with self.assertRaises(ValueError):block('case "OK" {}',"CANCEL")
    def test_16_reject_no_reply(self):
        with self.assertRaises(ValueError):option('case "OK" {dialog.Dispose();}',"OK")
    def test_17_Born_not_join(self):self.assertNotIn("nNewJoin01",parse("Born.dat")["Main"])
    def test_18_paper02_not_plain(self):self.assertNotIn("client.SendReply",parse("PaperDialog.dat")["PaperDialogProc"])
    def test_19_literal_npc_binding_unproven(self):self.assertNotIn("Born",parse("nNewJoin01.dat")["MerchantTalk"])
    def test_20_quest_rule_not_inferred(self):self.assertNotIn("QuestCompleted",repr(parse("nNewJoin01.dat")["JoinMessage03Proc"]))
if __name__=="__main__":unittest.main(verbosity=2)
