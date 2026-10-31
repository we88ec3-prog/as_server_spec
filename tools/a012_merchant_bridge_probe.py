#!/usr/bin/env python3
"""A012 Script evidence probe: original Merchant common entry and school-dialogue hooks.

Original EXE/DAT bytes are private inputs, never bundled with the repository.
A PASS confirms resource/statical-code paths, NOT original Client GUI or Server quest policy.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import struct
import unittest
import xml.etree.ElementTree as ET
import zlib

EXPECTED = {
    'Asgard.exe': ('db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145', None, None),
    'Merchant.dat': ('6888021cc8d12d9ae25d64bffd8316f7a87802f924091c2d06527f10ab08f350', 0xe9b389cf, ['Main']),
    'nNewJoin01.dat': ('8410064a564e381bfe941c71af3fc70598ea2325df69c3d216d7fbba1c7f79ae', 0xd9390353, None),
    'Born.dat': ('992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98', 0x1d87b0c0, ['Main']),
    'PaperDialog.dat': ('5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054', 0xf870c574, ['PaperDialog_Create', 'ShowIndexedHelp', 'PaperDialogProc']),
    'PaperDialog02.dat': ('49a618b9a59bda1294df6cbd8fa57e07c6e42c7647602dd988decf4a147bf22a', 0x42683546, ['PaperDialog02_Create','ShowIndexedHelp','PaperDialogProc']),
}
EXE_ANCHORS={
    'C6C packet constructor opcode': (0x575159, '6a6c'),
    'C6C reply subtype 1': (0x51aa5c, 'c6462401'),
    'C6C replied state': (0x51ab33, 'c7873c02000001000000'),
    'C6C dispose subtype 4': (0x5268c6, 'c6462404'),
    'C6C no-reply cleanup subtype 2': (0x5194ce, 'c6462402'),
    'C6C serializer pair count': (0x57525c, '0fb78e20020000'),
    'S44 opcode': (0x5862f9, '6a44'),
}

def file_path(name: str) -> Path:
    """Allow either a common resource folder or named overrides."""
    env_name='ASGARD_'+name.upper().replace('.','_')
    return Path(os.environ.get(env_name, str(Path(os.environ.get('ASGARD_RESOURCE_DIR','/mnt/data'))/name)))

def verified_bytes(name: str, raw: bytes) -> bytes:
    if hashlib.sha256(raw).hexdigest()!=EXPECTED[name][0]:
        raise ValueError(f'original file SHA mismatch: {name}')
    return raw

def original_file(name: str) -> bytes:
    return verified_bytes(name, file_path(name).read_bytes())

def parse_script(name: str) -> dict[str,str]:
    if name not in EXPECTED or not name.endswith('.dat'):
        raise ValueError('unknown original resource name')
    packed=original_file(name)
    unpack=zlib.decompress(packed)
    if len(unpack)<6:
        raise ValueError('short Script wrapper')
    ver,units=struct.unpack_from('>HI',unpack)
    if ver!=1 or len(unpack)!=6+2*units:
        raise ValueError('Script wrapper length/version mismatch')
    xml=unpack[6:].decode('utf-16le')
    if zlib.crc32(xml.encode('cp950'))!=EXPECTED[name][1]:
        raise ValueError('Script CP950 CRC mismatch')
    root=ET.fromstring(xml)
    if root.tag!='script':
        raise ValueError('Script XML root mismatch')
    funcs={f.get('name'):f.text or '' for f in root.findall('function')}
    expected_names=EXPECTED[name][2]
    if expected_names is not None and list(funcs)!=expected_names:
        raise ValueError('original function inventory mismatch')
    return funcs

def native_probe() -> int:
    exe=original_file('Asgard.exe')
    for name,(va,code) in EXE_ANCHORS.items():
        signature=bytes.fromhex(code)
        if exe[va-0x400000:va-0x400000+len(signature)]!=signature:
            raise ValueError('original x86 signature changed: '+name)
    return len(EXE_ANCHORS)

def parse_option_callback(source: str, control: str) -> tuple[str,str]:
    m=re.search(r'case\s+"'+re.escape(control)+r'"\s*\{(?P<body>.*?)\}', source, re.S)
    if not m:
        raise ValueError('control case absent')
    body=m.group('body')
    choice=re.search(r'ClientReply\.Add\("([^\"]+)",\s*"([^\"]+)"\)',body)
    if not choice or 'client.SendReply(ClientReply)' not in body:
        raise ValueError('no reply producer')
    if not body.index('ClientReply.Add') < body.index('client.SendReply') < body.index('dialog.Dispose()') < body.index('client.Dispose()'):
        raise ValueError('reply/close ordering invalid')
    return choice.groups()

def describe_bridge(merchant: dict[str,str], school: dict[str,str]) -> dict:
    main=merchant.get('Main','')
    if not main or 'Main' in school:
        raise ValueError('missing Merchant.Main / school must not claim Main')
    for symbol in ['client.AddGlobal("ServerParam", args)', 'reply = client.CreateParams()',
                   'client.AddGlobal("ClientReply", reply)', 'client.AddGlobal("MerchantTile", tile)',
                   'client.AddGlobal("MerchantName", name)', 'BuildMuttering()', 'DoesTalk()',
                   'MerchantDialog_Create(']:
        if symbol not in main:
            raise ValueError('merchant common entry missing '+symbol)
    for symbol in ['tile\t= client.Str2Int(args.Get("TILE"))',
                   'name\t= args.Get("MNAME")', 'gold\t= client.Str2Int(args.Get("UGOLD"))',
                   'balance\t= client.Str2Int(args.Get("UBAL"))',
                   'agold\t= client.Str2Int(args.Get("UAGOLD"))',
                   'abal\t= client.Str2Int(args.Get("UABAL"))',
                   'color   = args.Get("UCOLOR")']:
        if symbol not in main:
            raise ValueError('server parameter getter changed '+symbol)
    if not main.index('client.AddGlobal("ClientReply", reply)') < main.index('BuildMuttering()') < main.index('DoesTalk()') < main.index('MerchantDialog_Create('):
        raise ValueError('merchant initialization order mismatch')
    if 'QuestDialog_Create' in main:
        raise ValueError('Do not conflate Merchant.Main with QuestDialog_Create provider')
    for cmd in ['BUY','SELL','REPAIR','BANK','IDENTIFY','DIRECT']:
        if f'type = "{cmd}"' not in main:
            raise ValueError('Merchant.TYPE branch missing '+cmd)
    if school.get('DoesTalk','').strip()!='return true;':
        raise ValueError('school DoesTalk flag missing')
    for name in ['DoesBuy','DoesSell','DoesRepair','DoesBank','DoesIdentify']:
        if school.get(name,'').strip()!='return false;':
            raise ValueError('school unexpected merchant feature '+name)
    if 'JoinMessage01();' not in school.get('MerchantTalk',''):
        raise ValueError('school MerchantTalk not linked')
    for symbol in ['MerchantTile','MerchantName','QuestDialog_Create']:
        if symbol not in school.get('JoinMessage01',''):
            raise ValueError('school missing external symbol '+symbol)
    choices=school['JoinMessage03Proc']
    if parse_option_callback(choices,'OK')!=('STATE','ACCEPT') or parse_option_callback(choices,'CANCEL')!=('STATE','REFUSE'):
        raise ValueError('school option mapping changed')
    return {'merchant_main':True, 'school_merchant_talk':True,
            'source_getters':['TILE','MNAME','UGOLD','UBAL','UAGOLD','UABAL','UCOLOR','GREETING','TYPE'],
            'reply_globals':['ServerParam','ClientReply','MerchantTile','MerchantName'],
            'school_option_pairs':[('STATE','ACCEPT'),('STATE','REFUSE')],
            'quest_dialog_provider_found':False,
            'merchant_dialog_provider_found':False,
            'npc_script_binding_known':False,
            'original_gui_executed':False}

class TestA012MerchantBridge(unittest.TestCase):
    def setUp(self):
        required=['Merchant.dat','nNewJoin01.dat']
        if not all(file_path(n).is_file() for n in required):
            self.skipTest('Original Script resources absent; source tests not run')
        self.merchant=parse_script('Merchant.dat')
        self.school=parse_script('nNewJoin01.dat')
    def test_01_merchant_main_single(self): self.assertEqual(list(self.merchant),['Main'])
    def test_02_school_no_main(self): self.assertNotIn('Main',self.school)
    def test_03_original_merchant_bridge(self): self.assertTrue(describe_bridge(self.merchant,self.school)['merchant_main'])
    def test_04_server_params_global(self): self.assertIn('client.AddGlobal("ServerParam", args)',self.merchant['Main'])
    def test_05_client_reply_alloc(self): self.assertIn('client.AddGlobal("ClientReply", reply)',self.merchant['Main'])
    def test_06_merchant_tile_global(self): self.assertIn('client.AddGlobal("MerchantTile", tile)',self.merchant['Main'])
    def test_07_merchant_name_global(self): self.assertIn('client.AddGlobal("MerchantName", name)',self.merchant['Main'])
    def test_08_currency_server_params(self): self.assertEqual(describe_bridge(self.merchant,self.school)['source_getters'][:7],['TILE','MNAME','UGOLD','UBAL','UAGOLD','UABAL','UCOLOR'])
    def test_09_merchant_type_branches(self): self.assertIn('MerchantDirectTalk()',self.merchant['Main'])
    def test_10_initial_menu(self): self.assertIn('MerchantDialog_Create(MerchantGreeting, bBuy, bSell, bRepair, bBank, bIden, bTalk, color)',self.merchant['Main'])
    def test_11_talk_only(self): self.assertEqual(self.school['DoesTalk'].strip(),'return true;')
    def test_12_buy_disabled(self): self.assertEqual(self.school['DoesBuy'].strip(),'return false;')
    def test_13_no_school_main(self): self.assertEqual(self.school['MerchantTalk'].strip(),'JoinMessage01();')
    def test_14_school_first_page_symbols(self): self.assertIn('QuestDialog_Create(',self.school['JoinMessage01'])
    def test_15_school_yes_reply(self): self.assertEqual(parse_option_callback(self.school['JoinMessage03Proc'],'OK'),('STATE','ACCEPT'))
    def test_16_school_no_reply(self): self.assertEqual(parse_option_callback(self.school['JoinMessage03Proc'],'CANCEL'),('STATE','REFUSE'))
    def test_17_merchant_not_quest_dialog_provider(self): self.assertNotIn('QuestDialog_Create',self.merchant['Main'])
    def test_18_unknown_npc_binding(self): self.assertFalse(describe_bridge(self.merchant,self.school)['npc_script_binding_known'])
    def test_19_no_auto_quest_grant(self): self.assertNotIn('QuestCompleted',self.merchant['Main'])
    def test_20_no_fake_persistent_storage(self): self.assertNotIn('SaveQuest',self.school['JoinMessage03Proc'])
    def test_21_full_original_script_crc(self):
        for filename in ['Merchant.dat','nNewJoin01.dat','Born.dat','PaperDialog.dat','PaperDialog02.dat']:
            if file_path(filename).is_file(): self.assertTrue(parse_script(filename))
    def test_22_native_exe_sender(self):
        if not file_path('Asgard.exe').is_file():self.skipTest('Original EXE absent')
        self.assertEqual(native_probe(),len(EXE_ANCHORS))
    def test_23_invalid_option(self):
        with self.assertRaises(ValueError):parse_option_callback(self.school['JoinMessage03Proc'],'BOGUS')
    def test_24_callback_unreplied(self):
        with self.assertRaises(ValueError):parse_option_callback('case "OK" { dialog.Dispose(); }','OK')
    def test_25_tampered_resource_rejected(self):
        data=original_file('Merchant.dat')
        changed=data[:-1]+bytes([data[-1]^1])
        with self.assertRaises(ValueError): verified_bytes('Merchant.dat',changed)

if __name__=='__main__':unittest.main(verbosity=2)
