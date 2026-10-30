"""A-024 synthetic, private-free Client body/model tests."""
import struct
import unittest
from a024_npc_codec import read_exact,read_path64,read_draw07_known_prefix,DecodeError,Projection

class PacketTests(unittest.TestCase):
    def test_die_remove(self):
        for op in (0x5f,0x0e):
            self.assertEqual(read_exact(op,bytes.fromhex('12345678'))['object_or_event_u32'],0x12345678)
            for bad in (b'',b'\0'*3,b'\0'*5):
                with self.assertRaises(DecodeError):read_exact(op,bad)
    def test_move_fixed(self):
        data=struct.pack('>IHHBB',123456,45,78,2,3)
        self.assertEqual(read_exact(0x0c,data)['field_u16_b'],78)
        with self.assertRaises(DecodeError):read_exact(0x0c,data+b'x')
    def test_path64(self):
        data=struct.pack('>IHHBB',123456,45,78,2,3)+bytes([1,2,3])+struct.pack('>HHB',40,80,4)
        self.assertEqual(read_path64(data)['path_bytes_hex'],'010203')
        for bad in (data[:-1],data+b'x'):
            with self.assertRaises(DecodeError):read_path64(bad)
        unsafe=struct.pack('>IHHBB',1,2,3,4,12)+bytes(12)+struct.pack('>HHB',0,0,1)
        with self.assertRaises(DecodeError):read_path64(unsafe)
    def test_draw07_no_guessed_rows(self):
        self.assertEqual(read_draw07_known_prefix(b'\0\0')['count'],0)
        for bad in (b'',b'\0',b'\0\1',b'\0\0x'):
            with self.assertRaises(DecodeError):read_draw07_known_prefix(bad)
    def test_epoch_lifecycle(self):
        w=Projection(7)
        self.assertTrue(w.spawn(7,111,'monster'))
        self.assertFalse(w.spawn(7,111,'monster'))
        self.assertFalse(w.move(6,111))
        self.assertTrue(w.move(7,111))
        self.assertTrue(w.die(7,111))
        self.assertFalse(w.die(7,111))
        self.assertFalse(w.remove(6,111))
        self.assertTrue(w.remove(7,111))
        self.assertFalse(w.remove(7,111))
        self.assertTrue(w.spawn(7,222,'npc'))
        w.change_map(8)
        self.assertEqual(w.objects,{})
        self.assertFalse(w.spawn(7,333,'monster'))
    def test_unknown_opcode(self):
        with self.assertRaises(DecodeError):read_exact(0xff,b'')

if __name__=='__main__':unittest.main()
