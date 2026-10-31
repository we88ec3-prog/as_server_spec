"""A-006 synthetic S05/S33/S04 profile tests; native GUI not-run."""
import struct
import unittest
from a006_look_probe import (AppearanceError,parse_s05_profile,
                             parse_s33_profile,encode_s04,anchor,changed_fields)

def s05(hair=b'\xe6\x60\x30',cloth=b'\xff\x00\xff',flags=0):
    b=bytearray(29)
    struct.pack_into('>I',b,0,0x10203040)
    b[4]=1
    struct.pack_into('>H',b,7,101)
    b[9]=3
    b[10:13]=hair
    b[14:17]=b'\xff\xff\xff'
    b[18:21]=b'\xff\xff\xff'
    struct.pack_into('>I',b,21,flags)
    b[25:28]=cloth
    return bytes(b)

def s33(name='測試',hair=b'\xe6\x60\x30',cloth=b'\x28\x78\xc8',flags=0):
    encoded=name.encode('cp950')
    b=bytearray(42+len(encoded))
    struct.pack_into('>HHBI',b,0,10,20,2,0x10203040)
    b[9]=1
    struct.pack_into('>H',b,12,101)
    b[14]=3
    b[15:18]=hair
    b[19:22]=b'\xff\xff\xff'
    b[23:26]=b'\xff\xff\xff'
    struct.pack_into('>I',b,26,flags)
    b[30:33]=cloth
    b[34]=len(encoded)
    b[35:35+len(encoded)]=encoded
    b[-3:-1]=struct.pack('>H',100)
    return bytes(b)

class A006LookTests(unittest.TestCase):
    def test_s05_base_29(self):
        value=parse_s05_profile(s05())
        self.assertEqual(value['clothing_id'],101)
        self.assertEqual(value['object_id'],0x10203040)
    def test_s05_color_independence(self):
        a=parse_s05_profile(s05(flags=0x1000,cloth=b'\x28\x78\xc8'))
        b=parse_s05_profile(s05(hair=b'\x00\x40\x20',flags=0x1000,cloth=b'\x28\x78\xc8'))
        self.assertEqual(changed_fields(a,b),{'hair_rgb'})
        self.assertEqual(a['clothing_rgb'],b['clothing_rgb'])
    def test_s05_invalid_flags_and_length(self):
        for bad in (s05(flags=1),s05(flags=0x10),
                    s05(cloth=b'\x00\x00\x00'),s05()[:-1],s05()+b'\x00'):
            with self.assertRaises(AppearanceError):parse_s05_profile(bad)
    def test_s33_name_and_offsets(self):
        value=parse_s33_profile(s33())
        self.assertEqual((value['x'],value['y'],value['direction'],value['name']),
                         (10,20,2,'測試'))
        self.assertEqual(value['hair_rgb'],b'\xe6\x60\x30')
        self.assertEqual(value['clothing_rgb'],b'\x28\x78\xc8')
    def test_s33_color_separation(self):
        a=parse_s33_profile(s33())
        b=parse_s33_profile(s33(cloth=b'\x40\x30\x20'))
        self.assertEqual(changed_fields(a,b),{'clothing_rgb'})
    def test_s33_optional_unknown_fail_closed(self):
        for bad in (s33(flags=1),s33(flags=0x2000),
                    s33()[:-1],s33()+b'\x00'):
            with self.assertRaises(AppearanceError):parse_s33_profile(bad)
    def test_s33_bad_cp950(self):
        value=bytearray(s33(name='A'))
        value[35]=0xff
        with self.assertRaises(AppearanceError):parse_s33_profile(bytes(value))
    def test_s04_8_9_center(self):
        self.assertEqual(encode_s04(10,20,8,9),bytes.fromhex('000a001400080009'))
        for x,y in ((10,20),(50,100),(0,0)):
            self.assertEqual(anchor(x,y,8,9),(400,300))
    def test_s04_9_9_off_center(self):
        self.assertEqual(anchor(10,20,9,9),(448,300))
        self.assertEqual(anchor(10,20,8,8),(400,268))
    def test_s04_does_not_mutate_world(self):
        self.assertEqual(encode_s04(10,20,8,9)[:4],encode_s04(10,20,9,9)[:4])
        for args in ((-1,0,8,9),(0,65536,8,9)):
            with self.assertRaises(AppearanceError):encode_s04(*args)

if __name__=='__main__':
    unittest.main()
