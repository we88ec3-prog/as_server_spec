#!/usr/bin/env python3
"""A-005 roy3: verify native C33 producer/S0B consumer instruction chain.

Original EXE only. Does not prove successful native GUI walk or original Server speed policy.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"

# (callsite VA, destination VA); direct x86 E8/E9, independently disassembled.
EDGES = {
    0x557DB2: 0x573B40,  # C33 ctor
    0x557DE6: 0x5788A0,  # enqueue packet
    0x557B41: 0x4B63F0,  # first local destination filter
    0x4B63FD: 0x4EA900,  # scene-object lookup (not MAP collision proof)
    0x557B9B: 0x4BE470,  # local route builder
    0x557C1F: 0x4B4920,  # per-waypoint tile lookup
    0x555B07: 0x5718B0,  # C11 direction packet ctor (event)
    0x555EAE: 0x5718B0,  # C11 packet ctor (sync)
    0x4F1606: 0x558670,  # S0B handler routing (alternate)
    0x4F4904: 0x558670,  # S0B dispatch jump
    0x46D813: 0x4B4BB0,  # native bit4 segment predicate caller
    0x46D8D3: 0x4B4BB0,
    0x46DB0E: 0x4B4BB0,
}
# Code windows keep claim tightly scoped to direct instructions and branch guards.
WINDOWS = {
    0x557DCA: bytes.fromhex("88 48 24 8a 95 18 05 00 00 88 50 25"),
    0x557DDE: bytes.fromhex("80 c9 80 88 48 26"),
    0x557DF3: bytes.fromhex("25 7f 00 00 80"),
    0x557DFF: bytes.fromhex("88 85 18 05 00 00"),
    0x558678: bytes.fromhex("8a 47 28 84 c0"),
    0x558682: bytes.fromhex("0f 88 f6 00 00 00"),
    0x558689: bytes.fromhex("25 7f 00 00 80"),
    0x558695: bytes.fromhex("0f b6 8e 18 05 00 00 3b c8"),
    0x5586AB: bytes.fromhex("0f b7 47 26 0f b7 4f 24"),
    0x55877F: bytes.fromhex("25 7f 00 00 80"),
    0x55878B: bytes.fromhex("0f b6 8e 18 05 00 00 3b c8"),
    0x5587C9: bytes.fromhex("0f b7 47 24"),
    0x5587DA: bytes.fromhex("0f b7 57 26"),
    0x5588E3: bytes.fromhex("0f b7 57 26"),
    0x5588ED: bytes.fromhex("0f b7 57 24"),
}

class AuditError(ValueError): pass

def make_va_reader(data):
    if data[:2] != b"MZ": raise AuditError("not MZ")
    pe, = struct.unpack_from("<I", data, 0x3c)
    if data[pe:pe+4] != b"PE\0\0": raise AuditError("not PE")
    count, = struct.unpack_from("<H", data, pe+6)
    opt = pe+24
    if struct.unpack_from("<H",data,opt)[0] != 0x10b: raise AuditError("not PE32")
    base, = struct.unpack_from("<I",data,opt+28)
    sect = opt+struct.unpack_from("<H",data,pe+20)[0]
    ranges=[]
    for i in range(count):
        start=sect+40*i
        vsize,rva,rsize,raw=struct.unpack_from("<IIII",data,start+8)
        ranges.append((base+rva, min(vsize,rsize), raw))
    def read(va,size):
        for vma,length,raw in ranges:
            if vma <= va and va+size <= vma+length:
                return data[raw+va-vma:raw+va-vma+size]
        raise AuditError(f"VA {va:x} not file-backed")
    return read

def check_original(path):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA:
        raise AuditError("unknown client SHA")
    read = make_va_reader(data)
    for call,target in EDGES.items():
        opcode,delta=struct.unpack("<Bi",read(call,5))
        if opcode not in (0xe8,0xe9) or call+5+delta!=target:
            raise AuditError(f"native call or jump mismatch {call:x}")
    for va,expected in WINDOWS.items():
        if read(va,len(expected))!=expected:
            raise AuditError(f"native instruction mismatch {va:x}")
    return {"client_sha256":EXPECTED_SHA,"call_or_jump_edges":len(EDGES),
            "instruction_windows":len(WINDOWS),"offline_native_static":"PASS",
            "native_client_e2e":"not-run","native_player_walkability":"unknown"}

def classify_s0b(sequence_byte, client_next_sequence, *, predicted_xy=None, authoritative_xy=None):
    """Limited static branch model, not packet replay or fully emulated animation.

    0x558670: status high bit chooses two branches; both require
    (seq_low7 + 1) & 127 to equal Client's current NEXT sequence.
    """
    if not (0 <= sequence_byte <= 255 and 0 <= client_next_sequence <= 127):
        raise ValueError("invalid byte or client sequence")
    ack_next=((sequence_byte&0x7f)+1)&0x7f
    if ack_next != client_next_sequence:
        return "stale-or-out-of-order"
    if not (sequence_byte&0x80):
        return "clear-high-bit-authoritative-reposition-stop-path"
    if predicted_xy is None or authoritative_xy is None:
        return "set-high-bit-needs-prediction-check"
    if predicted_xy == authoritative_xy:
        return "set-high-bit-prediction-matched"
    return "set-high-bit-authoritative-rebase"

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("exe",type=Path)
    args=ap.parse_args()
    print(json.dumps(check_original(args.exe),indent=2))
