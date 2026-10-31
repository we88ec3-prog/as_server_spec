#!/usr/bin/env python3
"""A-012 original-client Quest UI resource and Born Script lifecycle witnesses.

No unprovided Script/Server claims: x86/resource tests are OFFLINE only.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET
import zlib

EXE_SHA = 'db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
BORN_SHA = '992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98'
BASIC_SHA = '0da379bf6dcc58be8ff3e4865fe8fe4859ae531f4aaef386196be56123082b96'
BORN_CRC = 0x1D87B0C0
ASSET_SHA = {
    'AlertFrame.ypf': 'b641441d1f0378de04b6f7929c333d95e6ad7df451f3927432e5c4d0305602ce',
    'QuestImage.ypf': '1f49352d77e79dcc8c535e03458e0f98d6532f1a01d38cedb164b29fd8ffec8e',
    'BasicString.txt': 'fa92f7a3cf544ff9e141d98620943b362e2d3dcc6e327878a818ebaa6ac3123b',
    'SkinString.txt': '7ba039919300dccf595fc5f5f4e6d79156b8b96c23a56fa3118d1e55847f199c',
}
# Original EXE VA -> exact machine code window. RVA file offset = VA-0x400000.
ANCHORS = {
    'native S44 opcode': (0x5862f9,'6a44'),
    'native S44 type1 subtype dispatch': (0x52c2ca,'8a45243c01'),
    'native C6C opcode': (0x575159,'6a6c'),
    'native C6C subtype bound': (0x575221,'83f804'),
    'native C6C type1': (0x51aa5c,'c6462401'),
    'native C6C replied flag': (0x51ab33,'c7873c02000001000000'),
    'native C6C send reply': (0x51ab3d,'e85edd0500'),
    'native client.Dispose dispatch': (0x526873,'68a8325f00'),
    'native client.Dispose C6C(4)': (0x5268c6,'c6462404'),
    'native C6C(4) send': (0x5268f4,'e8a71f0500'),
    'native no-reply flag check': (0x519479,'8b873c02000085c0'),
    'native no-reply C6C(2)': (0x5194ce,'c6462402'),
    'native C6C(2) send': (0x5194f1,'e8aaf30500'),
    'native C6C script name string8': (0x5752d6,'6aff8d561a'),
    'native S44 script cache scan': (0x52951d,'6874e56000'),
}

def digest(buf: bytes) -> str:
    return hashlib.sha256(buf).hexdigest()

def archive_members(data: bytes) -> dict[str, bytes]:
    if len(data)<8:
        raise ValueError('archive header truncated')
    n=struct.unpack_from('<I',data)[0]
    if n!=39 or len(data)<8+36*n:
        raise ValueError('archive index count/length invalid')
    pos=8+36*n
    out={}
    for i in range(n):
        off=8+36*i
        name=data[off:off+32].split(b'\0')[0].decode('ascii',errors='strict')
        end=struct.unpack_from('<I',data,off+32)[0]
        if not name:
            break  # original archive has an unused terminal index record
        if name in out or not pos<=end<=len(data):
            raise ValueError('invalid archive end offset')
        out[name]=data[pos:end]
        pos=end
    return out

def string_table(raw: bytes)->dict[int,str]:
    if not raw.startswith(b'\xff\xfe'):
        raise ValueError('missing UTF16LE BOM')
    out={}
    for line in raw.decode('utf-16').splitlines():
        x,sep,text=line.partition(' ')
        if sep and x.isdecimal():
            out[int(x)]=text
    return out

def born_entry(raw:bytes)->tuple[str,str]:
    buf=zlib.decompress(raw)
    if len(buf)<6:raise ValueError('short Born resource')
    version,n=struct.unpack_from('>HI',buf)
    if version!=1 or len(buf)!=6+2*n:raise ValueError('Born wrapper mismatch')
    xml=buf[6:].decode('utf-16le')
    if zlib.crc32(xml.encode('cp950'))!=BORN_CRC:raise ValueError('Born text checksum mismatch')
    funcs=ET.fromstring(xml).findall('function')
    if len(funcs)!=1 or funcs[0].get('name')!='Main':raise ValueError('Born entry mismatch')
    return funcs[0].get('name'),funcs[0].text or ''

def original_validation(exe:bytes,born:bytes,basic:bytes)->dict:
    for label,buf,hash_ in (('Asgard.exe',exe,EXE_SHA),('Born.dat',born,BORN_SHA),('Basic.dat',basic,BASIC_SHA)):
        if digest(buf)!=hash_:raise ValueError(label+' SHA mismatch')
    for name,(va,hex_) in ANCHORS.items():
        b=bytes.fromhex(hex_)
        if exe[va-0x400000:va-0x400000+len(b)]!=b:raise ValueError('Native signature mismatch: '+name)
    members=archive_members(basic)
    for name,hash_ in ASSET_SHA.items():
        if digest(members[name])!=hash_:raise ValueError('Resource SHA mismatch: '+name)
    labels=string_table(members['BasicString.txt'])
    skin=string_table(members['SkinString.txt'])
    if labels.get(101)!='這裡是對話視窗，請按Enter後進行對話。':raise ValueError('dialogue tutorial locale mismatch')
    if labels.get(198)!='與NPC對話的視窗':raise ValueError('npc dialogue locale mismatch')
    if skin.get(2263)!='任務日誌' or skin.get(2264)!='任務欄':raise ValueError('quest UI locale mismatch')
    entry,code=born_entry(born)
    if not ('client.CreateArray' in code and 'page.Insert' in code and 'PaperDialog_Create' in code):
        raise ValueError('Born UI API mismatch')
    for forbidden in ('SendReply','SetQuest','GiveReward','SetFlag','Teleport'):
        if forbidden in code:raise ValueError('Unexpected Born action: '+forbidden)
    if '(31,29)' not in code:raise ValueError('Born text coordinate mismatch')
    return dict(native_anchors=len(ANCHORS),assets=list(ASSET_SHA),born_entry=entry,
                paper_dialog_dependency='PaperDialog_Create',quest_authority='unknown')

def script_close_event(name:str,context:int,replied:bool)->list[bytes]:
    """STATIC-derived native lifecycle; not a GUI capture or authority decision."""
    if not name or not 0<=context<=0xffffffff:raise ValueError('invalid script/context')
    data=name.encode('cp950')
    if len(data)>255:raise ValueError('name length')
    base=bytes((len(data),))+data+struct.pack('>I',context)
    return [b'\x04'+base]+([] if replied else [b'\x02'+base])

class TestA012ResourceBridge(unittest.TestCase):
    def test_01_original_sha_x86_and_resources(self):
        exe=Path(os.getenv('ASGARD_EXE','/mnt/data/Asgard.exe'))
        born=Path(os.getenv('ASGARD_BORN_DAT','/mnt/data/Born.dat'))
        basic=Path(os.getenv('ASGARD_BASIC_DAT','/mnt/data/Basic.dat'))
        if not all(p.exists() for p in (exe,born,basic)):
            self.skipTest('Original game assets are absent; SHA/x86 tests require EXE, Born.dat, Basic.dat')
        self.assertEqual(original_validation(exe.read_bytes(),born.read_bytes(),basic.read_bytes())['native_anchors'],len(ANCHORS))
    def test_02_born_unchanged(self):
        born=Path(os.getenv('ASGARD_BORN_DAT','/mnt/data/Born.dat'))
        if not born.exists():self.skipTest('Original Born.dat absent')
        self.assertEqual(born_entry(born.read_bytes())[0],'Main')
    def test_03_born_crc_reject(self):
        born=Path(os.getenv('ASGARD_BORN_DAT','/mnt/data/Born.dat'))
        if not born.exists():self.skipTest('Original Born.dat absent')
        with self.assertRaises((ValueError,zlib.error)):born_entry(born.read_bytes()[:-1])
    def test_04_dialog_does_not_equal_quest(self):
        self.assertEqual(script_close_event('Born',0x11223344,False),
            [bytes.fromhex('0404426f726e11223344'),bytes.fromhex('0204426f726e11223344')])
    def test_05_reply_suppresses_no_reply_cleanup(self):
        self.assertEqual(script_close_event('Born',0x11223344,True),[bytes.fromhex('0404426f726e11223344')])
    def test_06_context_boundaries(self):
        with self.assertRaises(ValueError):script_close_event('Born',0x100000000,False)
    def test_07_bad_empty_name(self):
        with self.assertRaises(ValueError):script_close_event('',0,False)
    def test_08_bad_name_length(self):
        with self.assertRaises(ValueError):script_close_event('A'*256,0,False)
    def test_09_archive_truncated(self):
        with self.assertRaises(ValueError):archive_members(b'\0'*6)
    def test_10_archive_bogus_length(self):
        with self.assertRaises(ValueError):archive_members(b'\0'*8)
    def test_11_string_table_requires_bom(self):
        with self.assertRaises(ValueError):string_table(b'101 Hello')
    def test_12_no_reward_assumed(self):
        self.assertEqual(script_close_event('Born',0,False)[0][0],4)
        self.assertNotIn('RewardGrant',repr(script_close_event('Born',0,False)))

if __name__=='__main__':unittest.main(verbosity=2)
