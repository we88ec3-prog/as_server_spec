#!/usr/bin/env python3
"""A-012 original dialog resource fixtures; OFFLINE ONLY, never native GUI."""
from __future__ import annotations
import hashlib, os, re, struct, unittest, xml.etree.ElementTree as ET, zlib
from pathlib import Path
SOURCES={
 'MerchantDialog.dat':('ed194a77a669cbd8f83fbbd01bb08ed0f800b122695cc204a3a12f002f945095',9388,0x9267d99d,('MerchantDialog_Create','MerchantDialogProc')),
 'QuestDialog.dat':('13f068d8053ea7e7b0231357c318bc6effae867888b94305820fe483a17a02dc',4649,0xd4844b07,('QuestDialog_Create','QuestDialogAdjust')),
 'QuestDialog2.dat':('acb097c05f440e560394199622bb2e971d2ef9d1a33fff1a1c150ba633e63195',4702,0x893c64eb,('QuestDialog2_Create','QuestDialogAdjust2')),
}
def path_for(name):
 return Path(os.environ.get('ASGARD_'+name.upper().replace('.','_'),str(Path(os.environ.get('ASGARD_RESOURCE_DIR','/mnt/data'))/name)))
def parse(name,data):
 sha,units,crc,names=SOURCES[name]
 if hashlib.sha256(data).hexdigest()!=sha:raise ValueError('SHA mismatch')
 raw=zlib.decompress(data)
 if len(raw)<6:raise ValueError('short wrapper')
 v,n=struct.unpack_from('>HI',raw)
 if v!=1 or n!=units or len(raw)!=6+2*n:raise ValueError('BE wrapper')
 xml=raw[6:].decode('utf-16le')
 if zlib.crc32(xml.encode('cp950'))!=crc:raise ValueError('XML CP950 CRC')
 root=ET.fromstring(xml);f=root.findall('function')
 if root.tag!='script' or tuple(x.get('name') for x in f)!=names:raise ValueError('function inventory')
 return {x.get('name'):(x.get('params',''),x.text or '') for x in f}
def case(body,key):
 m=re.search(r'case\s+"'+re.escape(key)+r'"\s*\{(.*?)\n\s*\}',body,re.S)
 if not m:raise AssertionError('missing control '+key)
 return m.group(1)
class TestOriginalDialogs(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if any(not path_for(n).is_file() for n in SOURCES):raise unittest.SkipTest('private DAT missing (NOT a PASS)')
  cls.raw={n:path_for(n).read_bytes() for n in SOURCES}
  cls.fn={n:parse(n,cls.raw[n]) for n in SOURCES}
 def get(self,n,f):return self.fn[n][f][1]
 def test_sha_wrapper_crc(self):
  for n in SOURCES:
   self.assertEqual(hashlib.sha256(self.raw[n]).hexdigest(),SOURCES[n][0])
   self.assertEqual(len(zlib.decompress(self.raw[n])),6+2*SOURCES[n][1])
 def test_function_signatures(self):
  for n in SOURCES:self.assertEqual(tuple(self.fn[n]),SOURCES[n][3])
  x=self.fn['QuestDialog.dat']['QuestDialog_Create'][0]
  y=self.fn['QuestDialog2.dat']['QuestDialog2_Create'][0]
  self.assertEqual(y,x.replace('tile, name','tile, color, name'))
 def test_merchant_menu(self):
  s=self.get('MerchantDialog.dat','MerchantDialog_Create')
  for x in ('MerchantDialogProc','MerchantFrame.ypf','Portrait.dat','MerchantName','bBuy','bSell','bRepair','bBank','bIdentify','bTalk','dialog.cancelControl = "CANCEL"'):self.assertIn(x,s)
 def test_merchant_choices(self):
  s=self.get('MerchantDialog.dat','MerchantDialogProc')
  for k in ('BUY','SELL','REPAIR','BANK','IDENTIFY','TALK','CANCEL'):
   body=case(s,k); val='ABORT' if k=='CANCEL' else k
   self.assertIn('ClientReply.Add("TYPE", "'+val+'")',body)
   self.assertEqual('client.SendReply(ClientReply)' in body,k!='BANK')
 def test_merchant_order(self):
  s=self.get('MerchantDialog.dat','MerchantDialogProc')
  b=case(s,'BANK'); self.assertIn('MerchantBank()',b)
  self.assertLess(b.index('dialog.Dispose()'),b.index('ClientReply.Add('))
  t=case(s,'TALK')
  self.assertLess(t.index('client.SendReply(ClientReply)'),t.index('MerchantTalk()'))
  self.assertIn('client.Dispose()',case(s,'CANCEL'))
  for k in ('BUY','SELL','REPAIR','IDENTIFY'):self.assertIn('dialog.isActive = false',case(s,k))
 def test_quest_factories(self):
  for n,f in (('QuestDialog.dat','QuestDialog_Create'),('QuestDialog2.dat','QuestDialog2_Create')):
   s=self.get(n,f)
   for x in ('dialog.onControlClick = proc','QuestFrame.ypf','dialog.cancelControl = "CANCEL"','dialog.defaultControl = "NEXT"','"EDIT"','"OK"','"PREV"','"NEXT"'):self.assertIn(x,s)
   self.assertNotIn('client.SendReply(',s)
 def test_quest2_portrait(self):
  a=self.get('QuestDialog.dat','QuestDialog_Create')
  b=self.get('QuestDialog2.dat','QuestDialog2_Create')
  self.assertRegex(a,r'\btile\s*=\s*tile - 16384;')
  self.assertIn('portrait.SetFrame(datName, ypfName, objNum, 0)',a)
  self.assertIn('portrait.SetPortrait(tile, color)',b)
  self.assertNotRegex(b,r'(?m)^\s*tile\s*=\s*tile - 16384;')
 def test_adjust_and_tamper(self):
  for n,f in (('QuestDialog.dat','QuestDialogAdjust'),('QuestDialog2.dat','QuestDialogAdjust2')):
   s=self.get(n,f)
   for x in ('dialog.GetControl("EDIT")','dialog.GetControl("OK")','length(edit.text) > 0','ok.isActive = true','ok.isActive = false'):self.assertIn(x,s)
  b=bytearray(self.raw['QuestDialog.dat']);b[-1]^=1
  with self.assertRaises(ValueError):parse('QuestDialog.dat',bytes(b))
if __name__=='__main__':unittest.main(verbosity=2)
