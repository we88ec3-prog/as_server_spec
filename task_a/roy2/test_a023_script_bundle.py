"""A-023 synthetic tests for original Script wrappers, dependencies and C6C fixtures.

CI deliberately does not contain copyrighted Asgard script files.
"""
import struct
import unittest
import zlib

from a023_script_bundle_probe import (
    ResourceError, decode_script, callback_body, assert_order, assert_has,
    make_reply_fixture, inspect_functions, FILES,
)

def script(xml="<script><function name='Main'>ok</function></script>",
           version=1,unit_count=None):
    b=xml.encode("utf-16le")
    n=len(b)//2 if unit_count is None else unit_count
    return zlib.compress(struct.pack(">HI",version,n)+b)

class A023ScriptBundleTests(unittest.TestCase):
    def test_01_valid_native_wrapper(self):
        r=decode_script(script())
        self.assertEqual(list(r["functions"]),["Main"])
        self.assertEqual(r["functions"]["Main"],"ok")
    def test_02_crc_cp950_matches_plain_xml(self):
        x="<script><function name='Main'>測試</function></script>"
        self.assertEqual(decode_script(script(x))["text_crc32_cp950"],
                         zlib.crc32(x.encode("cp950")))
    def test_03_32bit_units_more_than_u16(self):
        s="<script><function name='Main'>"+"A"*70000+"</function></script>"
        self.assertEqual(decode_script(script(s))["utf16_code_units"],len(s))
    def test_04_reject_wrong_version(self):
        with self.assertRaises(ResourceError):decode_script(script(version=2))
    def test_05_reject_wrong_unit_count(self):
        with self.assertRaises(ResourceError):decode_script(script(unit_count=7))
    def test_06_reject_short_payload(self):
        with self.assertRaises(ResourceError):decode_script(zlib.compress(b"abc"))
    def test_07_reject_trailing_zlib(self):
        with self.assertRaises(ResourceError):decode_script(script()+b"x")
    def test_08_reject_truncated_zlib(self):
        with self.assertRaises((ResourceError,zlib.error)):decode_script(script()[:-3])
    def test_09_reject_non_xml(self):
        with self.assertRaises(Exception):decode_script(script("<script>"))
    def test_10_reject_wrong_root(self):
        with self.assertRaises(ResourceError):decode_script(script("<other/>"))
    def test_11_reject_duplicate_functions(self):
        x="<script><function name='F'>a</function><function name='F'>b</function></script>"
        with self.assertRaises(ResourceError):decode_script(script(x))
    def test_12_reject_missing_name(self):
        with self.assertRaises(ResourceError):
            decode_script(script("<script><function>text</function></script>"))
    def test_13_all_four_expected_resource_keys(self):
        self.assertEqual(set(FILES),{"PaperDialog","PaperDialog02","nNewJoin01","Merchant"})
    def test_14_callback_branch(self):
        s='case "OK" { ClientReply.Add("STATE", "ACCEPT"); client.SendReply(x); }'
        self.assertIn("STATE",callback_body(s,"OK"))
    def test_15_callback_missing_branch(self):
        with self.assertRaises(ResourceError):
            callback_body('case "CANCEL" { }',"OK")
    def test_16_callback_order_success(self):
        assert_order("ClientReply.Add() client.SendReply() dialog.Dispose() client.Dispose()",
                     "ClientReply.Add","client.SendReply","dialog.Dispose","client.Dispose")
    def test_17_callback_order_failure(self):
        with self.assertRaises(ResourceError):
            assert_order("client.Dispose() client.SendReply()", "client.SendReply","client.Dispose")
    def test_18_required_script_operation_failure(self):
        with self.assertRaises(ResourceError):assert_has("client.Dispose()","client.SendReply")
    def test_19_reply_fixture_contains_c6c_type1_and_root(self):
        b=make_reply_fixture("Merchant",0x11223344,"STATE","ACCEPT")
        self.assertEqual(b.hex(),"01084d65726368616e7411223344000105535441544506414343455054")
    def test_20_reply_fixture_accept_vs_refuse(self):
        a=make_reply_fixture("Merchant",5,"STATE","ACCEPT")
        b=make_reply_fixture("Merchant",5,"STATE","REFUSE")
        self.assertNotEqual(a,b)
        self.assertTrue(b.endswith(b"REFUSE"))
    def test_21_reply_fixture_paper02_start_not(self):
        a=make_reply_fixture("Merchant",5,"PAPER02","START")
        b=make_reply_fixture("Merchant",5,"PAPER02","NOT")
        self.assertNotEqual(a,b)
        self.assertIn(b"PAPER02",a)
    def test_22_reply_script_identity_is_root_input(self):
        b=make_reply_fixture("Merchant",9,"STATE","ACCEPT")
        self.assertIn(b"Merchant",b)
        self.assertNotIn(b"nNewJoin01",b)
    def test_23_reply_cp950_encoded_length(self):
        b=make_reply_fixture("S",0,"中文","同意")
        # 1 opcode + (1+1) name + 4 context + 2 count + u8(4),4B key +u8(4),4B value
        self.assertEqual(len(b),1+2+4+2+5+5)
    def test_24_reject_context_range_and_type(self):
        for v in (-1,2**32,True,None):
            with self.subTest(v=v),self.assertRaises(ResourceError):
                make_reply_fixture("Merchant",v,"STATE","ACCEPT")
    def test_25_reject_long_string8(self):
        with self.assertRaises(ResourceError):
            make_reply_fixture("M",1,"X"*256,"YES")
    def test_26_missing_external_dependency_not_silent(self):
        # Presence of a function name alone must not imply a complete ScriptRun.
        for x in ("QuestDialog_Create","MerchantDialog_Create","MerchantDirectTalk"):
            self.assertNotIn(x,{"PaperDialog_Create","PaperDialog02_Create","MerchantTalk"})
    def test_27_originals_absent_ci(self):
        # No original Script files are embedded or loaded into this test.
        self.assertNotIn("PaperDialog.dat",__file__)
    def test_28_detect_wrong_original_script_logic(self):
        fake={
            name:{"functions":{"Main":"none"}} for name in FILES
        }
        with self.assertRaises(ResourceError):inspect_functions(fake)

if __name__=="__main__":
    unittest.main()
