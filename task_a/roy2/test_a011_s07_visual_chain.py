"""Synthetic S07 visual-source tests; never claim original monster sprite render."""
import unittest
from a011_s07_visual_chain import project_s07_visuals, c43_known_three_mode_ui_request
from a024_object_packets import PacketError


def row(kind, image=0x4000, obj=0x01020304, variant=0x9999, flags=0,
        name=b"N", x=31, y=29):
    h = (x.to_bytes(2,"big")+y.to_bytes(2,"big")+bytes([kind])+
         obj.to_bytes(4,"big")+image.to_bytes(2,"big"))
    if kind in (1,2,4):
        return (h+b"\x01\x02\x03\x04\x05"+variant.to_bytes(2,"big")+
                flags.to_bytes(4,"big")+bytes([len(name)])+name)
    if kind == 13:
        return h+bytes([len(name)])+name
    if kind == 3:
        return h+b"\x01\x02\x03\x04\x05"+bytes([len(name)])+name
    if kind == 14:
        return h+b"\x01\x02\x03\x04"
    return h


def packet(*rows):
    return len(rows).to_bytes(2,"big")+b"".join(rows)


class A011VisualChainTests(unittest.TestCase):
    def test_01_empty(self):
        self.assertEqual(project_s07_visuals(b"\x00\x00"),())
    def test_02_first_monster_image(self):
        o=project_s07_visuals(packet(row(1)))[0]
        self.assertEqual((o.image_id,o.archive,o.slot,o.image_library),(0x4000,"Monster00.dat",0,8000))
        self.assertEqual((o.x,o.y,o.scene_object_ref),(31,29,0x01020304))
    def test_03_archive00_last(self):
        self.assertEqual(project_s07_visuals(packet(row(1,image=0x4009)))[0].slot,9)
    def test_04_archive01_first(self):
        o=project_s07_visuals(packet(row(2,image=0x400a)))[0]
        self.assertEqual((o.archive,o.slot),("Monster01.dat",0))
    def test_05_archive42_last(self):
        o=project_s07_visuals(packet(row(4,image=0x41ad)))[0]
        self.assertEqual((o.archive,o.slot,o.image_library),("Monster42.dat",9,8042))
    def test_06_all_kinds_visual_source(self):
        o=project_s07_visuals(packet(*(row(k,image=0x402a) for k in (1,2,4))))
        self.assertEqual([x.kind for x in o],[1,2,4])
        self.assertEqual([x.archive for x in o],["Monster04.dat"]*3)
        self.assertEqual([x.slot for x in o],[2]*3)
    def test_07_variant_is_not_image(self):
        o=project_s07_visuals(packet(row(1,image=0x4003,variant=0x41ad)))[0]
        self.assertEqual((o.archive,o.slot,o.variant_u16_not_image_id),("Monster00.dat",3,0x41ad))
    def test_08_object_ref_is_not_image(self):
        o=project_s07_visuals(packet(row(2,image=0x400a,obj=0x4000)))[0]
        self.assertEqual((o.archive,o.scene_object_ref),("Monster01.dat",0x4000))
    def test_09_outside_known_image_range(self):
        for n in (0,0x3fff,0x41ae,0x8000,0xffff):
            with self.subTest(image=n):
                o=project_s07_visuals(packet(row(1,image=n)))[0]
                self.assertIsNone(o.archive)
                self.assertIsNone(o.slot)
                self.assertEqual(o.mapping_status,"unresolved-image-namespace")
    def test_10_other_s07_kinds_not_monster_factory(self):
        for kind in (3,5,6,7,8,9,10,11,12,13,14):
            with self.subTest(kind=kind):
                self.assertEqual(project_s07_visuals(packet(row(kind))),())
    def test_11_mixed_rows(self):
        v=project_s07_visuals(packet(row(3),row(2,image=0x4012),row(14),row(4,image=0x4007)))
        self.assertEqual([(x.kind,x.archive,x.slot) for x in v],
                         [(2,"Monster01.dat",8),(4,"Monster00.dat",7)])
    def test_12_raw_cp950_name_not_required_for_image(self):
        self.assertEqual(project_s07_visuals(packet(row(1,name=b"\xa4\xa4")))[0].image_id,0x4000)
    def test_13_truncation_rejected(self):
        payload=packet(row(1))
        for n in range(len(payload)):
            with self.subTest(at=n),self.assertRaises(PacketError):
                project_s07_visuals(payload[:n])
    def test_14_trailing_bytes_rejected(self):
        with self.assertRaises(PacketError):
            project_s07_visuals(packet(row(1))+b"x")
    def test_15_invalid_kind_rejected(self):
        with self.assertRaises(PacketError):
            project_s07_visuals(packet(row(15)))
    def test_16_designed_count_guard(self):
        with self.assertRaises(PacketError):
            project_s07_visuals(packet(row(1),row(1)),max_records=1)
    def test_17_exhaust_registered_banks(self):
        o=project_s07_visuals(packet(*(row(1,image=0x4000+i) for i in range(430))))
        self.assertEqual(len(o),430)
        self.assertEqual({x.archive for x in o},{f"Monster{i:02d}.dat" for i in range(43)})
        self.assertEqual({x.slot for x in o},set(range(10)))
    def test_18_world_library_id_is_not_image(self):
        o=project_s07_visuals(packet(row(1,image=7000)))[0]
        self.assertIsNone(o.archive)
        self.assertNotEqual(o.image_id,o.scene_object_ref)

    def test_19_three_ui_c43_branch_opcodes(self):
        actual=[c43_known_three_mode_ui_request(0x12345678,n).hex() for n in range(3)]
        self.assertEqual(actual,["011234567804","011234567810","011234567840"])

    def test_20_three_ui_c43_unsigned_ref_bounds(self):
        self.assertEqual(c43_known_three_mode_ui_request(0,0).hex(),"010000000004")
        self.assertEqual(c43_known_three_mode_ui_request(0xffffffff,2).hex(),"01ffffffff40")

    def test_21_three_ui_c43_reject_unknown_mode(self):
        for n in (-1,3,4,0x10,True,"0"):
            with self.subTest(mode=n),self.assertRaises(ValueError):
                c43_known_three_mode_ui_request(99,n)

    def test_22_three_ui_c43_reject_bad_ref(self):
        for n in (-1,0x100000000,None,True,"100"):
            with self.subTest(ref=n),self.assertRaises(ValueError):
                c43_known_three_mode_ui_request(n,1)

    def test_23_three_ui_modes_have_same_scene_ref(self):
        self.assertEqual({c43_known_three_mode_ui_request(2,n)[1:5] for n in range(3)},
                         {b"\\x00\\x00\\x00\\x02"})


if __name__ == "__main__":
    unittest.main()
