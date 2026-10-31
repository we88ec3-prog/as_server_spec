"""A-015 synthetic MAP coordinate, flags and malformed archive tests."""
import struct,unittest
from a015_map_coordinate import MapView,MapError,members

def make_map(w=4,h=4,flags=None,tail8=b"",tail16=b""):
    flags=([0]*(w*h)) if flags is None else flags
    d=bytearray(struct.pack("<HHHBB",1,1,2,w,h))
    d+=bytes(((w+1)//2)*((h+3)//4)*2)
    for i,f in enumerate(flags):d+=struct.pack("<HHHI",i,i+1,i+2,f)
    for blob,stride in ((b"",7),(tail8,8),(tail16,16)):
        assert len(blob)%stride==0
        d+=struct.pack("<I",len(blob)//stride)+blob
    return bytes(d)

def make_dat(m):
    start=76
    return (struct.pack("<I",2)+struct.pack("<I",start)+
            b"00000.map"+bytes(23)+struct.pack("<I",start+len(m))+
            bytes(32)+m)

class MapCoordinateTest(unittest.TestCase):
    def test_size_and_tile_block(self):
        m=MapView(make_map());self.assertEqual((m.width,m.height,m.block_bytes,m.tile_offset),(4,4,4,12))
    def test_row_major_17_memory_vs_10_disk(self):
        m=MapView(make_map(flags=list(range(16))))
        self.assertEqual([m.tile_offset_at(*p) for p in [(0,0),(3,0),(0,1),(3,3)]],
                         [12,42,52,162])
        self.assertEqual(m.tile(2,1)["layers_u16"],[6,7,8])
        self.assertEqual(m.tile(2,1)["flags_u32"],6)
    def test_bit0_bit4_are_independent(self):
        m=MapView(make_map(flags=[0,1,16,17]+[512]*12))
        self.assertEqual([(m.tile(i,0)["bit0"],m.tile(i,0)["bit4"]) for i in range(4)],
                         [(False,False),(True,False),(False,True),(True,True)])
        self.assertEqual(m.tile(0,1)["flags_u32"],512)
    def test_no_invented_collision_policy(self):
        for f in (0,1,16,17,512):
            self.assertEqual(MapView(make_map(flags=[f]*16)).tile(0,0)["walkable"],
                             "unknown-original-player-rule")
    def test_pixel_geometry_centers_and_limits(self):
        m=MapView(make_map())
        self.assertEqual([m.pixel_to_tile_candidate(*p) for p in [(0,0),(47,31),(48,32),(191,127)]],
                         [(0,0),(0,0),(1,1),(3,3)])
    def test_pixel_rejects_bad_values(self):
        m=MapView(make_map())
        for x,y in [(-1,0),(0,-1),(192,0),(0,128),(True,0),("0",0)]:
            with self.subTest(x=x,y=y),self.assertRaises(MapError):m.pixel_to_tile_candidate(x,y)
    def test_tile_rejects_bad_values(self):
        m=MapView(make_map())
        for x,y in [(4,0),(0,4),(-1,0),(0,-1),(True,0)]:
            with self.subTest(x=x,y=y),self.assertRaises(MapError):m.tile(x,y)
    def test_candidate_pixel_to_tile_flag(self):
        flags=[0]*16;flags[9]=17;m=MapView(make_map(flags=flags))
        self.assertEqual(m.tile_for_pixel_candidate(60,66)["flags_u32"],17)
    def test_byte_short_header(self):
        with self.assertRaises(MapError):MapView(b"\0"*7)
    def test_zero_width(self):
        d=bytearray(make_map());d[6]=0
        with self.assertRaises(MapError):MapView(d)
    def test_short_tile(self):
        with self.assertRaises(MapError):MapView(make_map()[:13])
    def test_tail_short_and_extra(self):
        d=make_map()
        for b in (d[:-1],d+b"x"):
            with self.assertRaises(MapError):MapView(b)
    def test_tail8_and_tail16_pixel_candidates(self):
        a=struct.pack("<HHHH",0,48,63,9)
        b=struct.pack("<HHIIHH",1,2,3,4,191,127)
        x=MapView(make_map(tail8=a,tail16=b)).tail_pixel_candidates()
        self.assertEqual([i["in_pixel_bounds"] for i in x],[1,1])
        self.assertEqual([i["x_multiple_48"] for i in x],[1,0])
    def test_tail_pixel_bounds_reject_extent(self):
        a=struct.pack("<HHHH",0,192,127,9)
        self.assertEqual(MapView(make_map(tail8=a)).tail_pixel_candidates()[0]["in_pixel_bounds"],0)
    def test_DAT_sentinel_and_header(self):
        name,m=list(members(make_dat(make_map())))[0]
        self.assertEqual((name,m.headers),("00000.map",(1,1,2)))
    def test_DAT_corrupt_sentinel(self):
        d=bytearray(make_dat(make_map()));struct.pack_into("<I",d,40,100000)
        with self.assertRaises(MapError):list(members(d))
    def test_DAT_bad_filename(self):
        d=bytearray(make_dat(make_map()));d[8:13]=b"abcde"
        with self.assertRaises(MapError):list(members(d))
    def test_every_missing_counter_byte(self):
        d=make_map()
        for n in range(1,13):
            with self.subTest(n=n),self.assertRaises(MapError):MapView(d[:-n])

if __name__=="__main__":unittest.main()
