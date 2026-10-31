#!/usr/bin/env python3
"""A-025: original Asgard.exe byte-gated codec fixtures + DESIGNED domain tests.
Not a running original Client/Server; never establishes original tutorial quest policy.
"""
import hashlib
import struct
import tempfile
import sqlite3
import unittest
from pathlib import Path

EXE_SHA256 = 'db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
# .text original VA->raw mapping: raw file offset == VA-0x400000.
SIGNATURES = {
    'CAttack ctor 0x13': (0x570A29, bytes.fromhex('6a13')),
    'CAttack writer BE u32': (0x570AC0, bytes.fromhex('8b411850e877a1eeff')),
    'CStartCastSpell ctor 0x4D': (0x575529, bytes.fromhex('6a4d')),
    'CStartCastSpell writer BE u16': (0x5755C0, bytes.fromhex('0fb7411850e87655eeff')),
    'CCastSpell ctor 0x56': (0x571769, bytes.fromhex('6a56')),
    'CCastSpell writer u8': (0x571800, bytes.fromhex('0fb6411850e8f692eeff')),
    'SCastSpell ctor 0x52': (0x57D569, bytes.fromhex('6a52')),
    'SCastSpell reader u32,u8': (0x57D600, bytes.fromhex('568bf1e8a8d8edff')),
    'SDieObjects ctor 0x1E': (0x57E049, bytes.fromhex('6a1e')),
    'SDieObjects reader u32': (0x57E260, bytes.fromhex('568bf1e848ccedff')),
    'CBattle ctor 0x3D': (0x5711CB, bytes.fromhex('6a3d')),
    'CBattle writer 16 variant branches': (0x570DEC, bytes.fromhex('8b461883f80f')),
    'SBattle ctor 0x3D': (0x57C6EC, bytes.fromhex('6a3d')),
    'SBattle variant dispatch 0..15': (0x57C8C2, bytes.fromhex('0fb6c083f80f')),
}

def native_signatures(exe):
    b = Path(exe).read_bytes()
    if hashlib.sha256(b).hexdigest()!=EXE_SHA256:
        raise ValueError('Client version mismatch')
    for name,(va,raw) in SIGNATURES.items():
        if b[va-0x400000:va-0x400000+len(raw)]!=raw:
            raise ValueError('native signature mismatch '+name)
    return len(SIGNATURES)

def u32be(value):
    if type(value) is not int or not 0<=value<=0xffffffff: raise ValueError('u32')
    return struct.pack('>I',value)

def c13_attack(ref):
    # opaque 32-bit target/ref; Client object/UI gives the context, not quest proof
    return u32be(ref)

def c4d_start_cast(spell):
    if type(spell) is not int or not 0<=spell<=0xffff: raise ValueError('u16')
    return struct.pack('>H',spell)

def c56_cast(value):
    if type(value) is not int or not 0<=value<=255: raise ValueError('u8')
    return bytes([value])

def s52_cast_result(body):
    if len(body)!=5: raise ValueError('requires 5 bytes')
    return struct.unpack('>IB',body)

def s1e_die(body):
    if len(body)!=4: raise ValueError('requires u32')
    return struct.unpack('>I',body)[0]

class Authority:
    """Designed Server policy; NOT original Asgard quest/damage/cooldown values."""
    def __init__(self, path):
        self.db=sqlite3.connect(path,isolation_level=None)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS objective_events(event TEXT PRIMARY KEY, actor TEXT NOT NULL, objective TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS progress(actor TEXT NOT NULL, objective TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(actor,objective));
        ''')
    def apply(self, *, actor, valid_account, world_generation_matches, alive,
              target_exists, target_same_map, in_range, skill_unlocked,
              resource_enough, cooldown_ready, combat_event_id, objective,
              verified_tutorial_objective):
        if not all((actor, valid_account,world_generation_matches,alive,
                    target_exists,target_same_map,in_range,skill_unlocked,
                    resource_enough,cooldown_ready,combat_event_id)):
            return False
        # Original tutorial need for combat NOT established. Without independently
        # verified objective mapping, a legitimate hit never alters quest progress.
        if not verified_tutorial_objective or not objective:
            return True
        self.db.execute('BEGIN IMMEDIATE')
        try:
            insert=self.db.execute('INSERT OR IGNORE INTO objective_events VALUES (?,?,?)',
                                   (combat_event_id,actor,objective)).rowcount
            if insert:
                self.db.execute('''INSERT INTO progress(actor,objective,count) VALUES(?,?,1)
                    ON CONFLICT(actor,objective) DO UPDATE SET count=count+1''',(actor,objective))
            self.db.execute('COMMIT')
            return True
        except Exception:
            self.db.execute('ROLLBACK')
            raise
    def count(self,actor,obj):
        row=self.db.execute('SELECT count FROM progress WHERE actor=? AND objective=?',(actor,obj)).fetchone()
        return row[0] if row else 0
    def close(self):self.db.close()

class A025Tests(unittest.TestCase):
    def test_native_exe_signatures(self):
        from os import environ
        original=environ.get('ASGARD_EXE','/mnt/data/Asgard.exe')
        if Path(original).exists():
            self.assertEqual(native_signatures(original),14)
        else:
            self.skipTest('original Asgard.exe unavailable; exact filename ASGARD_EXE')
    def test_client_outbound_fixtures(self):
        self.assertEqual(c13_attack(0x12345678).hex(),'12345678')
        self.assertEqual(c4d_start_cast(0x1234).hex(),'1234')
        self.assertEqual(c56_cast(7).hex(),'07')
        for f,x in ((c13_attack,-1),(c4d_start_cast,0x10000),(c56_cast,256)):
            with self.assertRaises(ValueError):f(x)
    def test_server_inbound_parser_fixtures(self):
        self.assertEqual(s52_cast_result(bytes.fromhex('1122334403')),(0x11223344,3))
        self.assertEqual(s1e_die(bytes.fromhex('12345678')),0x12345678)
        for p,body in ((s52_cast_result,b'\0'*4),(s1e_die,b'\0'*5)):
            with self.assertRaises(ValueError):p(body)
    def _authority(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        return str(Path(t.name)/'model.db')
    def _args(self):
        return dict(actor='alice',valid_account=True,world_generation_matches=True,
                    alive=True,target_exists=True,target_same_map=True,in_range=True,
                    skill_unlocked=True,resource_enough=True,cooldown_ready=True,
                    combat_event_id='server-authoritative-attack-1',objective='tutorial.kill',
                    verified_tutorial_objective=True)
    def test_invalid_combat_has_no_objective(self):
        a=Authority(self._authority()); self.addCleanup(a.close)
        for flag in ('valid_account','world_generation_matches','alive','target_exists','target_same_map','in_range','skill_unlocked','resource_enough','cooldown_ready'):
            kw=self._args();kw[flag]=False
            self.assertFalse(a.apply(**kw),flag)
        self.assertEqual(a.count('alice','tutorial.kill'),0)
    def test_no_unverified_tutorial_requirement(self):
        a=Authority(self._authority());self.addCleanup(a.close)
        kw=self._args();kw['verified_tutorial_objective']=False
        self.assertTrue(a.apply(**kw))
        self.assertEqual(a.count('alice','tutorial.kill'),0)
    def test_one_event_once_across_restart(self):
        path=self._authority()
        a=Authority(path)
        self.assertTrue(a.apply(**self._args()))
        self.assertTrue(a.apply(**self._args()))
        self.assertEqual(a.count('alice','tutorial.kill'),1)
        a.close()
        a=Authority(path);self.addCleanup(a.close)
        self.assertTrue(a.apply(**self._args()))
        self.assertEqual(a.count('alice','tutorial.kill'),1)
    def test_unrelated_server_event_not_counted(self):
        a=Authority(self._authority());self.addCleanup(a.close)
        kw=self._args();kw['objective']=None
        self.assertTrue(a.apply(**kw))
        self.assertEqual(a.count('alice','tutorial.kill'),0)

if __name__=='__main__':
    unittest.main(verbosity=2)
