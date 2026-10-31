#!/usr/bin/env python3
"""A-008 conservative MSVC RTTI inventory; never guesses wire layouts."""
import argparse
import hashlib
from pathlib import Path

SHA = 'db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
NAMES = ('Status', 'StatusDialog', 'ExpBarDialog', 'SStatusPacket',
         'SMapStatusPacket', 'SAddLastingSpellPacket',
         'SRemoveLastingSpellPacket', 'CAddAbilityPacket',
         'SDamageEffectPacket', 'SBattlePacket')

def scan(path):
    b = Path(path).read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    assert sha == SHA, f'Unexpected EXE profile: {sha}'
    for name in NAMES:
        token = ('.?AV' + name + '@@').encode('ascii') + b'\0'
        at = b.find(token)
        assert at >= 0, f'Missing RTTI: {name}'
        assert b.find(token, at + 1) == -1, f'Ambiguous RTTI: {name}'
        print(f'{name:28s} file_offset=0x{at:06X} RTTI=yes; opcode/layout=UNKNOWN')
    print('A-008 static RTTI probe PASS; no native parser, GUI or wire validation claimed')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('exe', help='path to original Asgard.exe')
    scan(ap.parse_args().exe)
