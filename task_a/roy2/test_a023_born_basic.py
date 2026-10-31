"""A-023 synthetic Basic DAT/Script wrapper safety tests; copyrighted assets absent CI."""
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from a023_born_basic_probe import index_dat_bytes,read_script_xml,verify

def make_archive(entries):
    slots=len(entries)+1
    offset=4+36*slots
    out=bytearray(struct.pack("<I",slots))
    content=bytearray()
    for name,data in entries:
        out+=struct.pack("<I",offset)+name.ljust(32,b"\0")
        content+=data
        offset+=len(data)
    out+=struct.pack("<I",offset)+bytes(32)
    return bytes(out+content)

def make_script(xml="<script><function name='Main'>test</function></script>",
                version=1,unit_override=None):
    data=xml.encode("utf-16le")
    units=len(data)//2 if unit_override is None else unit_override
    return zlib.compress(struct.pack(">HI",version,units)+data)

class TestA023BornBasic(unittest.TestCase):
    def test_index_simple_valid(self):
        b=make_archive([(b"AlertFrame.ypf",b"\x11\x00abcdef"),(b"File.txt",b"hello")])
        d=index_dat_bytes(b,validate_release=False)
        self.assertEqual(list(d),["AlertFrame.ypf","File.txt"])
        off,n=d["AlertFrame.ypf"]
        self.assertEqual(b[off:off+n],b"\x11\x00abcdef")
    def test_empty_index_header(self):
        with self.assertRaises(ValueError):index_dat_bytes(b"")
    def test_zero_or_one_slot(self):
        for n in (0,1):
            with self.subTest(n=n),self.assertRaises(ValueError):
                index_dat_bytes(struct.pack("<I",n)+bytes(100))
    def test_huge_slot_count(self):
        with self.assertRaises(ValueError):index_dat_bytes(struct.pack("<I",100001))
    def test_index_beyond_file(self):
        with self.assertRaises(ValueError):index_dat_bytes(struct.pack("<I",39)+b"\0"*10)
    def test_wrong_first_offset(self):
        b=bytearray(make_archive([(b"foo",b"ok")]))
        struct.pack_into("<I",b,4,1)
        with self.assertRaises(ValueError):index_dat_bytes(b,validate_release=False)
    def test_wrong_eof_sentinel(self):
        b=bytearray(make_archive([(b"foo",b"ok")]))
        struct.pack_into("<I",b,4+36,999999)
        with self.assertRaises(ValueError):index_dat_bytes(b,validate_release=False)
    def test_zero_size_member(self):
        with self.assertRaises(ValueError):
            index_dat_bytes(make_archive([(b"foo",b""),(b"bar",b"x")]),validate_release=False)
    def test_duplicate_names(self):
        with self.assertRaises(ValueError):
            index_dat_bytes(make_archive([(b"foo",b"a"),(b"foo",b"b")]),validate_release=False)
    def test_path_traversal_name(self):
        with self.assertRaises(ValueError):
            index_dat_bytes(make_archive([(b"../escape",b"abc")]),validate_release=False)
    def test_backslash_name(self):
        with self.assertRaises(ValueError):
            index_dat_bytes(make_archive([(b"x\\y",b"abc")]),validate_release=False)
    def test_release_must_have_39_slots(self):
        with self.assertRaises(ValueError):
            index_dat_bytes(make_archive([(b"foo",b"ok")]),validate_release=True)
    def test_script_utf16_be_header_valid(self):
        text,root=read_script_xml(make_script())
        self.assertEqual(root.tag,"script")
        self.assertIn("<function",text)
    def test_script_invalid_version(self):
        with self.assertRaises(ValueError):read_script_xml(make_script(version=2))
    def test_script_units_mismatch(self):
        with self.assertRaises(ValueError):read_script_xml(make_script(unit_override=2))
    def test_script_non_xml_root(self):
        with self.assertRaises(ValueError):read_script_xml(make_script("<hello/>"))
    def test_script_reject_trailing_zlib(self):
        with self.assertRaises(ValueError):read_script_xml(make_script()+b"extra")
    def test_script_reject_truncated(self):
        with self.assertRaises(ValueError):read_script_xml(make_script()[:-2])
    def test_script_non_xml_malformed(self):
        with self.assertRaises(ET.ParseError):read_script_xml(make_script("<script>"))
    def test_script_large_synthetic_units(self):
        text="<script>"+"a"*70000+"</script>"
        got,_=read_script_xml(make_script(text))
        self.assertEqual(got,text)
    def test_source_originals_not_present_ci_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                verify(Path(d)/"Born.dat",Path(d)/"Basic.dat")

if __name__=="__main__":
    unittest.main()
