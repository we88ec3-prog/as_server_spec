#!/usr/bin/env python3
"""A30 original Basic.dat resource labels + Asgard.exe C02/S02/C15 witness.
Original assets are NOT bundled; tests involving them skip when absent.
"""
import hashlib, os, struct, unittest
from pathlib import Path

EXE_SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
BASIC_SHA = "0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96"
LOCALE_SHA = "813f2800696555f16ec6c4bfc5975b649332340b5a6975d7aeba4c4e77380161"
ANCHORS = {
    "confirmation_name_packet": (0x4b24e7, "0524060000"),
    "confirmation_name_key73": (0x4b24ed, "6a49"),
    "confirmation_email_packet": (0x4b250f, "81c222080000"),
    "confirmation_email_key75": (0x4b2516, "6a4b"),
    "region4_name_widget23": (0x4b2877, "6a17"),
    "region4_email_widget24": (0x4b2896, "6a18"),
    "region2_3_name_widget15": (0x4b28a3, "6a0f"),
    "region2_3_email_widget16": (0x4b28c2, "6a10"),
    "region2_3_name_packet": (0x4b289d, "0524060000"),
    "region2_3_email_packet": (0x4b28bb, "81c122080000"),
    "C02_F3_writer": (0x5742f6, "8dbe18060000"),
    "C02_F4_writer": (0x57430e, "8dbe16080000"),
    "C02_F4_string8_call": (0x574321, "e88a6eeeff"),
    "C02_region2_min": (0x5742ec, "83f802"),
    "C02_region4_max": (0x5742f1, "83f804"),
    "C02_confirm_send": (0x4b229f, "e8fc650c00"),
    "S02_status": (0x4b1da9, "0fb64724"),
    "S02_message_nonempty": (0x4b1dff, "66837f2600"),
    "S02_stage1e_region3_suppress": (0x4b1e1e, "83f803"),
    "S02_message_dialog": (0x4b1ebe, "e8ad06f9ff"),
    "S02_nonzero_branch": (0x4b1eec, "84c0"),
    "C15_opcode15": (0x571609, "6a15"),
    "C15_empty_serializer": (0x5716a0, "c3"),
    "S02_nonzero_C15_create": (0x4b1f1d, "e8cef60b00"),
    "S02_nonzero_C15_send": (0x4b1f2f, "e86c690c00"),
    "S02_nonzero_state1f": (0x4b1f34, "c7464c1f000000"),
}

def directory(data):
    if len(data) < 8:
        raise ValueError("truncated")
    count = struct.unpack_from("<I", data)[0]
    if not 1 <= count <= 4096 or len(data) < 8 + 36 * count:
        raise ValueError("invalid directory")
    out = []
    for i in range(count):
        start = 8 + 36 * i
        name = data[start:start+32].split(b"\0")[0].decode("ascii", errors="replace")
        end = struct.unpack_from("<I", data, start+32)[0]
        out.append((name, end))
    return out

def read_member(data, name):
    d = directory(data)
    ids = [i for i,(n,_) in enumerate(d) if n == name]
    if len(ids) != 1:
        raise ValueError("member missing/ambiguous: "+name)
    i = ids[0]
    start = d[i-1][1] if i else 8+36*len(d)
    end = d[i][1]
    if not 0 <= start < end <= len(data):
        raise ValueError("invalid resource boundaries")
    return data[start:end], (start,end)

def labels(data, member):
    raw, span = read_member(data, member)
    if raw[:2] != b"\xff\xfe":
        raise ValueError("expected UTF16LE BOM")
    result = {}
    for line in raw.decode("utf-16").splitlines():
        key, sep, value = line.partition(" ")
        if sep and key.isdecimal():
            # Some unrelated IDs repeat in the shipped file; the required keys do not.
            result.setdefault(int(key),value)
    return result,span

def verify_files(exe, basic, locale):
    for name,raw,expected in (
        ("Asgard.exe",exe,EXE_SHA),
        ("Basic.dat",basic,BASIC_SHA),
        ("Locale.dat",locale,LOCALE_SHA),
    ):
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("SHA256 mismatch "+name)
    base,base_span = labels(basic,"BasicString.txt")
    skin,skin_span = labels(basic,"SkinString.txt")
    for key,val in {72:"ID",73:"NAME",75:"E-MAIL"}.items():
        if base.get(key)!=val:
            raise ValueError("BasicString key %d" % key)
    for key,val in {2150:"角色名稱",2151:"密碼",2152:"確認密碼",2153:"名字",2154:"E-Mail"}.items():
        if skin.get(key)!=val:
            raise ValueError("SkinString key %d" % key)
    if b"Servers.txt" not in locale:
        raise ValueError("Locale server list not found")
    for name,(va,h) in ANCHORS.items():
        value=bytes.fromhex(h)
        if exe[va-0x400000:va-0x400000+len(value)]!=value:
            raise ValueError("original x86 changed: "+name)
    return base_span,skin_span,len(ANCHORS)

def synthetic_failure(status=1,message="Request rejected"):
    if type(status) != int or not 1 <= status <= 255:
        raise ValueError("S02 failure status required")
    data=message.encode("cp950")
    if len(data)>255:
        raise ValueError("string8 overflow")
    return bytes([status,len(data)])+data

class TestA30(unittest.TestCase):
    def test_01_archive_synthetic_labels(self):
        one=b"\xff\xfe"+"73 NAME\r\n75 E-MAIL\r\n".encode("utf-16le")
        two=b"\xff\xfe"+"2153 名字\r\n2154 E-Mail\r\n".encode("utf-16le")
        raw=(struct.pack("<II",2,0)
            +b"BasicString.txt".ljust(32,b"\0")+struct.pack("<I",80+len(one))
            +b"SkinString.txt".ljust(32,b"\0")+struct.pack("<I",80+len(one)+len(two))
            +one+two)
        self.assertEqual(labels(raw,"BasicString.txt")[0][73],"NAME")
        self.assertEqual(labels(raw,"SkinString.txt")[0][2154],"E-Mail")
    def test_02_reject_bad_archive(self):
        with self.assertRaises(ValueError): directory(b"\0"*8)
    def test_03_s02_synthetic_message(self):
        self.assertEqual(synthetic_failure().hex(),"0110526571756573742072656a6563746564")
    def test_04_s02_reject_success_status(self):
        with self.assertRaises(ValueError): synthetic_failure(0,"error")
    def test_05_s02_reject_long_message(self):
        with self.assertRaises(ValueError): synthetic_failure(1,"a"*256)
    def test_06_locale_is_not_resource_string_table(self):
        path=Path(os.environ.get("ASGARD_LOCALE_DAT","/mnt/data/Locale.dat"))
        if not path.exists(): self.skipTest("Original Locale.dat absent")
        raw=path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),LOCALE_SHA)
        self.assertIn(b"Servers.txt",raw)
        self.assertNotIn(b"BasicString.txt",raw)
    def test_07_original_3_file_cross_reference(self):
        e=Path(os.environ.get("ASGARD_EXE","/mnt/data/Asgard.exe"))
        b=Path(os.environ.get("ASGARD_BASIC_DAT","/mnt/data/Basic.dat"))
        l=Path(os.environ.get("ASGARD_LOCALE_DAT","/mnt/data/Locale.dat"))
        if not (e.exists() and b.exists() and l.exists()):
            self.skipTest("Original EXE and DAT files are absent from clean checkout")
        self.assertEqual(verify_files(e.read_bytes(),b.read_bytes(),l.read_bytes()),
                         ((0x2e97c,0x32356),(0x3ccbc9,0x3cf08d),26))

if __name__=="__main__":
    unittest.main(verbosity=2)
