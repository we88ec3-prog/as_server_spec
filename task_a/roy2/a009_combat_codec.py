"""A-009 decoded wire body subsets, verified against the original Asgard.exe native readers.

All bodies exclude AA frame, seed XOR and the opcode. No Server formulas.
"""
from dataclasses import dataclass

@dataclass
class Cursor:
    raw: bytes
    at: int = 0
    def read(self, count):
        if self.at + count > len(self.raw):
            raise ValueError(f"truncated combat body offset={self.at}, need={count}")
        chunk = self.raw[self.at:self.at+count]
        self.at += count
        return chunk
    def u8(self): return self.read(1)[0]
    def u16(self): return int.from_bytes(self.read(2), "big")
    def u32(self): return int.from_bytes(self.read(4), "big")
    def string8(self): return self.read(self.u8())
    def finish(self):
        if self.at != len(self.raw): raise ValueError("trailing combat bytes")

def c13_attack(target_opaque):
    if not isinstance(target_opaque,int) or not 0 <= target_opaque < 2**32:
        raise ValueError("target must be BE u32")
    return target_opaque.to_bytes(4, "big")

def s5f_die(body):
    c=Cursor(body); val=c.u32(); c.finish()
    return {"object_opaque":val}

def s13_damage_effect(body):
    """Native S13 reader 0x57DE90: 2 BE u32, u8, 2 BE u16, flags u8;
    bit0 extends the body; bits3,4 reinterpret existing u32, add no bytes."""
    c=Cursor(body)
    first,second=c.u32(),c.u32()
    kind=c.u8(); f34=c.u16(); f30=c.u16(); flags=c.u8()
    result={"opaque_1":first,"opaque_2":second,"kind":kind,
            "field34_u16":f34,"field30_u16":f30,"flags":flags}
    if flags & 0x08:
        result["opaque_1_split"]=[first >> 16,first & 65535]
        result["opaque_1"]=0
    if flags & 0x10:
        result["opaque_2_split"]=[second >> 16,second & 65535]
        result["opaque_2"]=0
    if flags & 0x01:
        result["extra"]={"kind":c.u8(),"fields_u16":[c.u16(),c.u16(),c.u16()],
                         "flag":c.u8(),"opaque_u32":[c.u32(),c.u32()],
                         "last_u8":c.u8()}
    c.finish()
    return result

def s3d_battle_simple(body):
    """Native S3D subtype dispatch table at 0x57CD98.
    Only small definitely identified branches: other variants fail closed.
    1,8,12: no extra; 4,5,6,10: one u8; 7: two u8; 15: two BE u32;
    3: string8, BE u32, u8 and 26 u8. All fields are opaque.
    """
    c=Cursor(body); kind=c.u8(); result={"subtype":kind}
    if kind in (1,8,12): pass
    elif kind in (4,5,6,10): result["param_u8"]=c.u8()
    elif kind==7: result["params_u8"]=[c.u8(),c.u8()]
    elif kind==15: result["params_u32"]=[c.u32(),c.u32()]
    elif kind==3:
        result["text_raw"]=c.string8()
        result["param_u32"]=c.u32()
        result["param_u8"]=c.u8()
        result["array26"]=list(c.read(26))
    else: raise ValueError("S3D complex subtype not in proven short subset")
    c.finish(); return result
