#!/usr/bin/env python3
"""A005: only synthetic vectors; original static PE probes are separate."""
import struct
import unittest
from a005_collision_probe import audit_archive_bytes
from a005_move_codec import (MoveError,parse_c33,parse_c11,parse_s0b,
                            encode_s0b,observed_line_bit4,DesignedMoveGate)

class A005MoveTests(unittest.TestCase):
    def test_c33_three_u8(self):
        self.assertEqual(parse_c33(b"\x01\x7f\x01")["sequence_mod128"],127)
        self.assertTrue(parse_c33(b"\x01\x80\x01")["sequence_high_bit"])
    def test_c11_one_u8(self):
        self.assertEqual(parse_c11(b"\x07")["direction_raw"],7)
    def test_s0b_coords_and_byte_bitfields(self):
        body=bytes.fromhex("000b000aff")
        self.assertEqual(parse_s0b(body)["sequence_mod128"],127)
        self.assertEqual(encode_s0b(11,10,127,True),body)
    def test_bad_fixed_size(self):
        for decoder,body in ((parse_c33,b"\x01\x00\x01"),(parse_c11,b"\x07"),
                             (parse_s0b,b"\x00"*5)):
            for item in (body[:-1],body+b"\x00"):
                with self.assertRaises(MoveError):decoder(item)
    def test_sequence_127_to_0_and_duplicate(self):
        gate=DesignedMoveGate("map",1,10,10)
        args=dict(speed_ok=True,collision_ok=True,direction=1)
        self.assertTrue(gate.apply(1,127,(11,10),**args)[0])
        self.assertFalse(gate.apply(1,127,(12,10),**args)[0])
        self.assertTrue(gate.apply(1,0,(12,10),**args)[0])
    def test_server_speed_collision_are_designed(self):
        gate=DesignedMoveGate("map",1,10,10)
        for key in ("speed_ok","collision_ok"):
            kwargs=dict(speed_ok=True,collision_ok=True,direction=0)
            kwargs[key]=False
            self.assertFalse(gate.apply(1,0,(11,10),**kwargs)[0])
        self.assertEqual((gate.x,gate.y,gate.last_seq),(10,10,None))
    def test_stale_epoch(self):
        gate=DesignedMoveGate("map",1,10,10)
        kwargs=dict(speed_ok=True,collision_ok=True,direction=0)
        self.assertFalse(gate.apply(0,0,(11,10),**kwargs)[0])
        gate.change_map("new",2,0,0)
        self.assertFalse(gate.apply(1,0,(1,0),**kwargs)[0])
    def test_line_mask_does_not_establish_walk_rule(self):
        self.assertFalse(observed_line_bit4(0))
        self.assertFalse(observed_line_bit4(1))
        self.assertTrue(observed_line_bit4(16))
        self.assertTrue(observed_line_bit4(17))
        self.assertFalse(observed_line_bit4(512))
    def test_synthetic_archive_and_bad_tail(self):
        w,h=2,4
        flags=[0,1,16,17,512,0,0,0]
        tile=b"".join(struct.pack("<HHHI",0,0,0,v) for v in flags)
        payload=struct.pack("<HHHBB",1,1,1,w,h)+b"\x00\x00"+tile+b"\x00"*12
        start=4+36*2
        name=b"00000.map\x00"+bytes(22)
        original=struct.pack("<I",2)+struct.pack("<I",start)+name+struct.pack("<I",start+len(payload))+bytes(32)+payload
        obj=audit_archive_bytes(original)
        self.assertEqual(obj["tiles"],8)
        self.assertEqual(obj["bit4_tiles"],2)
        self.assertEqual(obj["bit9_tiles"],1)
        with self.assertRaises(ValueError):audit_archive_bytes(original[:-2])
    def test_bounds_direction_and_step_limit(self):
        gate=DesignedMoveGate("map",1,0,0)
        kw=dict(speed_ok=True,collision_ok=True,direction=0)
        self.assertFalse(gate.apply(1,0,(-1,0),**kw)[0])
        self.assertFalse(gate.apply(1,0,(20,0),**kw)[0])
        self.assertFalse(gate.apply(1,0,(1,0),speed_ok=True,collision_ok=True,direction=9)[0])

if __name__=="__main__":
    unittest.main()
