#!/usr/bin/env python3
"""A-030 SHA-locked original Client static witness and synthetic codec; no GUI/server or secrets."""
from pathlib import Path
import hashlib, struct, unittest, os

SHA="db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
# Exact native Asgard.exe VA, x86 instruction bytes, not user data.
A={
"UI region0 id":(0x4b1b00,"c7866c02000001000000"),
"UI region4 id":(0x4b1b51,"c7866c02000014000000"),
"UI region1/2/3 id":(0x4b1b8f,"c7866c0200000c000000"),
"UI first copy":(0x4b27be,"8b866c020000"),
"UI second copy":(0x4b27d6,"8b9670020000"),
"UI confirmation copy":(0x4b27f7,"8b8e74020000"),
"UI region0 extra3":(0x4b2825,"6a0a"),
"UI region4 extra3":(0x4b2877,"6a17"),
"UI region4 extra4":(0x4b2896,"6a18"),
"UI region1/2/3 extra3":(0x4b28a3,"6a0f"),
"UI region1/2/3 extra4":(0x4b28c2,"6a10"),
"UI confirm compare":(0x4b290c,"e851211000"),
"UI first format gate":(0x4b28f0,"e83bf1ffff"),
"UI C02 send":(0x4b229f,"e8fc650c00"),
"C02 first writer":(0x5742b4,"8d7e18"),
"C02 second writer":(0x5742c9,"8dbe18020000"),
"C02 region branch":(0x5742ec,"83f802"),
"C02 extended third":(0x5742f6,"8dbe18060000"),
"C02 extended fourth":(0x57430e,"8dbe16080000"),
"C02 other third":(0x574338,"8dbe18040000"),
"S02 status switch":(0x4b1da9,"0fb64724"),
"S02 nonzero":(0x4b1eec,"84c0"),
"S02 alloc C15":(0x4b1f1d,"e8cef60b00"),
"S02 send C15":(0x4b1f2f,"e86c690c00"),
"S02 state1f":(0x4b1f34,"c7464c1f000000"),
"S02 state1d check":(0x4b1f46,"837e4c1d"),
"S02 alloc C04":(0x4b2021,"e84a230c00"),
"S02 state1e":(0x4b205f,"c7464c1e000000"),
"S02 message nonempty":(0x4b1dff,"66837f2600"),
"S02 visible dialog builder":(0x4b1ebe,"e8ad06f9ff"),
}
# A-030 follow-up: extra chain verified from original x86; labels are NOT established by signatures.
EMAIL_C02_CHAIN={
 "extended region lower":(0x5742ec,"83f802"),
 "extended region upper":(0x5742f1,"83f804"),
 "field4 writer +0x816":(0x57430e,"8dbe16080000"),
 "field4 string8 write call":(0x574321,"e88a6eeeff"),
 "region4 extra fourth UI widget24":(0x4b2896,"6a18"),
 "region2/3 extra fourth UI widget16":(0x4b28c2,"6a10"),
 "packet +0x822 destination":(0x4b28bb,"81c122080000"),
 "confirmation popup fourth value":(0x4b250f,"81c222080000"),
 "confirmation popup fourth locale label ID":(0x4b2516,"6a4b"),
 "region4 extra third UI widget23":(0x4b2877,"6a17"),
 "region2/3 extra third UI widget15":(0x4b28a3,"6a0f"),
 "field3 writer +0x618":(0x5742f6,"8dbe18060000"),
 "extended tail flag u8":(0x574326,"0fb686160a0000"),
 "nonextended third writer":(0x574338,"8dbe18040000"),
 "confirmation C02 enqueue":(0x4b229f,"e8fc650c00"),
}
def verify_email_c02_chain(path=None):
 d=Path(path or client_path()).read_bytes()
 if hashlib.sha256(d).hexdigest()!=SHA:raise ValueError("Client SHA mismatch")
 for description,(va,h) in EMAIL_C02_CHAIN.items():
  literal=bytes.fromhex(h)
  if d[va-0x400000:va-0x400000+len(literal)]!=literal:
   raise ValueError("C02 field4 chain mismatch: "+description)
 return len(EMAIL_C02_CHAIN)


# Additional original x86 anchors; this is code-flow evidence, NOT a real GUI/session test.
STRICT_S02_C15_AND_NAME_EMAIL={
 "C02 opcode 0x02":(0x574189,"6a02"),
 "C02 F3 relative +0x618":(0x5742f6,"8dbe18060000"),
 "C02 F4 relative +0x816":(0x57430e,"8dbe16080000"),
 "UI region4 first extra +0x624":(0x4b2870,"81c124060000"),
 "UI region4 second extra +0x822":(0x4b288f,"81c222080000"),
 "UI region2-3 second extra +0x822":(0x4b28bb,"81c122080000"),
 "confirm dialog F3 packet+0x624":(0x4b24e7,"0524060000"),
 "confirm dialog F3 locale key0x49":(0x4b24ed,"6a49"),
 "confirm dialog F4 packet+0x822":(0x4b250f,"81c222080000"),
 "confirm dialog F4 locale key0x4b":(0x4b2516,"6a4b"),
 "S02 status parser":(0x57dbc3,"e8e8d1edff"),
 "S02 message parser":(0x57dbd8,"e8c3dbedff"),
 "MakeInfo S02 dispatcher":(0x4b235b,"e900faffff"),
 "S02 focus dispatch index":(0x4b1db5,"0fb688bc214b00"),
 "S02 message text gate":(0x4b1dff,"66837f2600"),
 "S02 region3 suppression":(0x4b1e1e,"83f803"),
 "S02 text dialog builder":(0x4b1ebe,"e8ad06f9ff"),
 "S02 zero/nonzero branch":(0x4b1eec,"84c0"),
 "native C15 opcode0x15":(0x571609,"6a15"),
 "native C15 empty serializer":(0x5716a0,"c3"),
 "S02 nonzero C15 ctor":(0x4b1f1d,"e8cef60b00"),
 "S02 nonzero C15 send":(0x4b1f2f,"e86c690c00"),
 "S02 nonzero state1f":(0x4b1f34,"c7464c1f000000"),
 "S02 success state1d branch":(0x4b1f46,"837e4c1d"),
 "S02 success C04 ctor":(0x4b2021,"e84a230c00"),
 "S02 success state1e":(0x4b205f,"c7464c1e000000"),
}
def verify_strict_original_branches(path=None):
 d=Path(path or client_path()).read_bytes()
 if hashlib.sha256(d).hexdigest()!=SHA:raise ValueError("Client SHA mismatch")
 for name,(va,h) in STRICT_S02_C15_AND_NAME_EMAIL.items():
  expected=bytes.fromhex(h)
  if d[va-0x400000:va-0x400000+len(expected)]!=expected:
   raise ValueError("S02/C15/original NAME-EMAIL source: "+name)
 return len(STRICT_S02_C15_AND_NAME_EMAIL)

def newuser_reply_effect(state,region,status,text):
 """Derived from 0x4b1d60; returns code-path flags, NOT a native GUI result."""
 if state not in (0x1d,0x1e) or region not in range(5) or not 0<=status<=255:
  raise ValueError("outside traced Native NewUser state/region/status")
 if status:
  return {"display_attempt":bool(text) and not (region==3 and state==0x1e),
          "send_c15":True,"next_state":0x1f,"send_c04":False,"local_success":False}
 return {"display_attempt":bool(text) and not (region==3 and state==0x1e),
         "send_c15":False,"next_state":0x1e if state==0x1d else state,
         "send_c04":state==0x1d,"local_success":state==0x1e}

FOCUS_SELECTOR=bytes([0,1]+[4]*12+[2,3]+[4]*7+[1]+[4]*4+[3])
WIDGETS={
 0:(1,2,3,10,None),
 1:(12,13,14,15,16),
 2:(12,13,14,15,16),
 3:(12,13,14,15,16),
 4:(20,21,22,23,24),
}
def client_path():
 return Path(os.environ.get("ASGARD_EXE") or ("Asgard.exe" if Path("Asgard.exe").is_file() else "/mnt/data/Asgard.exe"))
def verify_client(path=None):
 d=Path(path or client_path()).read_bytes()
 if hashlib.sha256(d).hexdigest()!=SHA:raise ValueError("SHA mismatch")
 for name,(va,h) in A.items():
  b=bytes.fromhex(h)
  if d[va-0x400000:va-0x400000+len(b)]!=b:raise ValueError("x86 mismatch: "+name)
 if d[0x4b21bc-0x400000:0x4b21bc-0x400000+29]!=FOCUS_SELECTOR:
  raise ValueError("S02 status focus selector mismatch")
 return len(A)
def string8(value):
 if not isinstance(value,str) or "\0" in value:raise ValueError("invalid string8")
 raw=value.encode("cp950")
 if len(raw)>255:raise ValueError("too long")
 return bytes([len(raw)])+raw
def encode_C02(region,fields,flag=0):
 if type(region)!=int or region not in range(5):raise ValueError("region")
 count=4 if region in (2,3,4) else 3
 if len(fields)!=count:raise ValueError("field count")
 if type(flag)!=int or not 0<=flag<=255:raise ValueError("flag")
 return b"".join(string8(x) for x in fields)+(bytes([flag]) if count==4 else b"")
def encode_S02_nonzero(status,message):
 if type(status)!=int or not 1<=status<=255:raise ValueError("failure status")
 return bytes([status])+string8(message)
def decode_S02(body):
 if len(body)<2 or len(body)!=2+body[1]:raise ValueError("truncated/extra S02")
 return body[0],body[2:].decode("cp950")
def focus_for(status):
 if not 3<=status<=31:return None
 category=FOCUS_SELECTOR[status-3]
 return {0:"first",1:"first",2:"second",3:"first"}.get(category)
class TestA030(unittest.TestCase):
 def test_01_orig_sha_and_30_anchors(self):
  if not client_path().is_file():self.skipTest("Original Asgard.exe absent; set ASGARD_EXE for native signature validation")
  self.assertEqual(verify_client(),30)
 def test_02_focus_selector(self):self.assertEqual(len(FOCUS_SELECTOR),29)
 def test_03_region0_widget(self):self.assertEqual(WIDGETS[0],(1,2,3,10,None))
 def test_04_region4_widget(self):self.assertEqual(WIDGETS[4],(20,21,22,23,24))
 def test_05_region1_2_3_widget(self):
  for i in (1,2,3):self.assertEqual(WIDGETS[i],(12,13,14,15,16))
 def test_06_region0_body(self):self.assertEqual(encode_C02(0,["i","p","x"]).hex(),"016901700178")
 def test_07_region4_body(self):self.assertEqual(encode_C02(4,["i","p","n","e"],7).hex(),"01690170016e016507")
 def test_08_region1_discrepancy(self):
  self.assertIsNotNone(WIDGETS[1][4]);self.assertEqual(encode_C02(1,["i","p","x"]).hex(),"016901700178")
 def test_09_bad_region_shape(self):
  for i,x in ((0,["i","p","n","e"]),(4,["i","p","n"])):
   with self.assertRaises(ValueError):encode_C02(i,x)
 def test_10_overflow(self):
  with self.assertRaises(ValueError):string8("a"*256)
 def test_11_s02_failure_ascii(self):
  self.assertEqual(encode_S02_nonzero(1,"Request rejected").hex(),"0110526571756573742072656a6563746564")
 def test_12_s02_read(self):self.assertEqual(decode_S02(encode_S02_nonzero(2,"Denied")),(2,"Denied"))
 def test_13_s02_focus(self):
  self.assertEqual([focus_for(x) for x in (3,4,17,18,26,31,1,2,5)],["first","first","second","first","first","first",None,None,None])
 def test_14_s02_truncation(self):
  b=encode_S02_nonzero(1,"Error")
  for n in range(len(b)):
   with self.assertRaises(ValueError):decode_S02(b[:n])
 def test_15_no_success_as_error(self):
  with self.assertRaises(ValueError):encode_S02_nonzero(0,"Denied")
 def test_16_native_extended_field4_chain(self):
  if not client_path().is_file():self.skipTest("Original Asgard.exe absent; set ASGARD_EXE")
  self.assertEqual(verify_email_c02_chain(),15)
 def test_17_strict_original_name_email_s02_c15(self):
  if not client_path().is_file():self.skipTest("Original Asgard.exe absent; set ASGARD_EXE")
  self.assertEqual(verify_strict_original_branches(),26)
 def test_18_no_embedded_email_label_in_original_exe(self):
  if not client_path().is_file():self.skipTest("Original Asgard.exe absent")
  d=client_path().read_bytes()
  self.assertIn("Locale.dat".encode("utf-16le"),d)
  self.assertNotIn("E-MAIL".encode("utf-16le"),d)
 def test_19_s02_failure_sends_c15_and_enters_1f(self):
  for state in (0x1d,0x1e):
   for region in range(5):
    effect=newuser_reply_effect(state,region,1,"Request rejected")
    self.assertTrue(effect["send_c15"])
    self.assertEqual(effect["next_state"],0x1f)
    self.assertFalse(effect["send_c04"])
    self.assertEqual(effect["display_attempt"],not (state==0x1e and region==3))
 def test_20_s02_empty_text_no_popup_still_c15(self):
  for state in (0x1d,0x1e):
   x=newuser_reply_effect(state,4,2,"")
   self.assertFalse(x["display_attempt"])
   self.assertTrue(x["send_c15"])
 def test_21_s02_success_twostage_no_c15(self):
  first=newuser_reply_effect(0x1d,4,0,"")
  final=newuser_reply_effect(0x1e,4,0,"")
  self.assertEqual(first["next_state"],0x1e)
  self.assertTrue(first["send_c04"])
  self.assertFalse(first["send_c15"])
  self.assertTrue(final["local_success"])
  self.assertFalse(final["send_c04"])
 def test_22_original_gui_not_inferred_from_static_probe(self):
  for bad in ((0x1f,4,1,""),(0x1d,5,1,""),(0x1d,4,-1,"")):
   with self.assertRaises(ValueError):newuser_reply_effect(*bad)
if __name__=="__main__":unittest.main(verbosity=2)
