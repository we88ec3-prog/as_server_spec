"""A005 native-static regression. Original assets stay local and uncommitted."""
import os
import unittest
from a005_roy3_collision_recovery import (
    local_candidate_gate as gate,compose_tile_flags as overlay,
    audit_map6,verify_exe,eight_neighbor_direction)

class NativeWalkCandidateTests(unittest.TestCase):
    def test_native_exe(self):
        exe=os.environ.get('ASGARD_EXE')
        if exe:
            v=verify_exe(exe)
            self.assertEqual(v['result'],'PASS')
            self.assertEqual((v['native_edges'],v['native_opcode_anchors']),(13,17))
    def test_dest_bit_zero_blocks_flag1_and17_not_bit4_alone(self):
        for flags in (1,17,513):self.assertFalse(gate(flags,0,0,0))
        for flags in (0,16,512):self.assertTrue(gate(flags,0,0,0))
    def test_direction_mask_and_source_bit3(self):
        self.assertFalse(gate(0,8,0b00001000,3))
        self.assertTrue(gate(0,8,0b00001000,2))
        self.assertTrue(gate(0,0,0b00001000,3))
        self.assertFalse(gate(0,8,0b10000000,7))
    def test_dynamic_overlay_can_reverse_base(self):
        self.assertEqual(overlay(0,1,0),1)
        self.assertEqual(overlay(17,0,1),16)
        self.assertEqual(overlay(1,1,1),0)
        self.assertFalse(gate(overlay(0,1,0),0,0,0))
        self.assertTrue(gate(overlay(1,0,1),0,0,0))
    def test_object_and_bypass_are_distinct(self):
        self.assertFalse(gate(0,0,0,0,object_lookup_is_one=True))
        self.assertTrue(gate(1,8,255,0,object_lookup_is_one=True,global_bypass=True))
    def test_invalid_inputs(self):
        for inp in [(0,0,0,8),(0,0,256,0),(-1,0,0,0)]:
            with self.assertRaises(ValueError):gate(*inp)
        with self.assertRaises(ValueError):overlay(0,-1,0)
    def test_direction_index_from_native_eight_neighbors(self):
        expected=[((0,-1),0),((1,0),1),((0,1),2),((-1,0),3),
                  ((1,-1),4),((1,1),5),((-1,1),6),((-1,-1),7)]
        for (dx,dy),value in expected:
            self.assertEqual(eight_neighbor_direction(dx,dy),value)
        with self.assertRaises(ValueError):eight_neighbor_direction(0,0)
    def test_original_map0(self):
        map0=os.environ.get('ASGARD_MAP0')
        if not map0:return
        r=audit_map6(map0)
        self.assertEqual((r['raw_bit0_clear'],r['raw_4neighbor_component_from_30_30']),(902,900))
        self.assertEqual(r['raw_tile_flags'],{0:902,17:2698})
        self.assertEqual(r['native_walkability'],'unverified')
if __name__=='__main__':unittest.main()
