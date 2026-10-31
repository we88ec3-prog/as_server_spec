"""A-011 synthetic resource/client-click tests, never native GUI assertions."""
import unittest
from a011_resource_codec import (
    monster_image_ref,world_archive_ref,c43_known_info_request,
    known_s07_monster_object_kind,select_monster_local_motion
)
from a024_object_packets import draw_objects_s07

def be16(n):return n.to_bytes(2,"big")
def be32(n):return n.to_bytes(4,"big")

class ResourceMappingTest(unittest.TestCase):
    def test_monster_first(self):
        p=monster_image_ref(0x4000)
        self.assertEqual((p.library_id,p.archive_name,p.local_image_slot),(8000,"Monster00.dat",0))

    def test_monster_first_archive_end(self):
        self.assertEqual(monster_image_ref(0x4009).local_image_slot,9)

    def test_monster_next_archive(self):
        p=monster_image_ref(0x400A)
        self.assertEqual((p.library_id,p.archive_name,p.local_image_slot),(8001,"Monster01.dat",0))

    def test_monster_last_registered(self):
        p=monster_image_ref(0x41ad)
        self.assertEqual((p.library_id,p.archive_name,p.local_image_slot),(8042,"Monster42.dat",9))

    def test_monster_libraries_are_all_43(self):
        self.assertEqual([monster_image_ref(0x4000+10*i).library_id for i in range(43)],
                         list(range(8000,8043)))

    def test_monster_outside_guards(self):
        for n in (-1,0x3fff,0x41ae,65536,"0x4000",None,True):
            with self.subTest(n=n),self.assertRaises(ValueError):monster_image_ref(n)

    def test_world_registered_range(self):
        self.assertEqual(world_archive_ref(7000),"World00.dat")
        self.assertEqual(world_archive_ref(7023),"World23.dat")

    def test_world_out_of_range(self):
        for n in (6999,7024,8000,True):
            with self.subTest(n=n),self.assertRaises(ValueError):world_archive_ref(n)

    def test_s07_monster_object_type_dispatch(self):
        self.assertEqual([k for k in range(1,15) if known_s07_monster_object_kind(k)],
                         [1,2,4])

    def test_s07_type1_2_4_synthetic_object_rows(self):
        for k in (1,2,4):
            # Only assert the packet field layout and factory kind. Do NOT assert
            # sprite mapping from this synthetic row without an original asset.
            tail=bytes([1,2,3,4,5])+be16(0x4000)+be32(0)+b"\x01X"
            body=be16(1)+be16(31)+be16(29)+bytes([k])+be32(123)+be16(6)+tail
            r=draw_objects_s07(body)["rows"][0]
            self.assertEqual(r["kind"],k)
            self.assertEqual(r["variant_u16"],0x4000)

    def test_c43_two_ui_producers_shared_known_body(self):
        self.assertEqual(c43_known_info_request(0x12345678),bytes.fromhex("011234567804"))

    def test_c43_entity_id_boundary(self):
        self.assertEqual(c43_known_info_request(0),bytes.fromhex("010000000004"))
        self.assertEqual(c43_known_info_request(0xffffffff),bytes.fromhex("01ffffffff04"))

    def test_c43_invalid_producer_and_key(self):
        for args in ((-1,1,4),(2**32,1,4),(123,0,4),(123,1,5),("5",1,4)):
            with self.subTest(args=args),self.assertRaises(ValueError):
                c43_known_info_request(*args)

    def test_motion_dispatch_0_through_5(self):
        self.assertEqual([select_monster_local_motion(0x200,s) for s in range(6)],
                         [0x220,0x230,0x240,0x220,0x230,0x240])

    def test_motion_selector_rejects_unknown(self):
        for b,s in ((0,6),(0,-1),(65536,0),(-1,1)):
            with self.subTest(base=b,selector=s),self.assertRaises(ValueError):
                select_monster_local_motion(b,s)

    def test_motion_wrap_is_explicit_16bit(self):
        self.assertEqual(select_monster_local_motion(0xfff0,0),0x10)

if __name__=="__main__": unittest.main()
