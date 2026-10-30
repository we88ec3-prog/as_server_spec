#!/usr/bin/env python3
"""A-024 conservative decoded-body parser and designed projection. No native E2E."""
import struct

class DecodeError(ValueError):
    pass

def read_exact(opcode, body):
    native = {
        0x5f: ('>I', ('object_or_event_u32',)),
        0x0e: ('>I', ('object_or_event_u32',)),
        0x0c: ('>IHHBB', ('object_or_event_u32','field_u16_a','field_u16_b','field_u8_a','field_u8_b'))
    }
    if opcode not in native:
        raise DecodeError("unsupported opcode")
    fmt, columns = native[opcode]
    if len(body) != struct.calcsize(fmt):
        raise DecodeError("length mismatch")
    return dict(zip(columns, struct.unpack(fmt, body)))

def read_path64(body, cap=11):
    if len(body) < 15:
        raise DecodeError("truncated path")
    obj,a,b,flag,n = struct.unpack_from('>IHHBB',body)
    if n > cap or len(body) != 15+n:
        raise DecodeError("unsafe path length")
    c,d,tail = struct.unpack_from('>HHB',body,10+n)
    return dict(object_or_event_u32=obj,field_u16_a=a,field_u16_b=b,
                field_u8_a=flag,path_count=n,path_bytes_hex=bytes(body[10:10+n]).hex(),
                field_u16_c=c,field_u16_d=d,field_u8_b=tail)

def read_draw07_known_prefix(body):
    if len(body) < 2:
        raise DecodeError("truncated S07 count")
    n=struct.unpack_from('>H',body)[0]
    if n==0 and len(body)==2:
        return dict(count=0, records=[])
    raise DecodeError("nonempty S07 record variants are not fully proven")

class Projection:
    """Only designed Server-side epoch guard; not native observed policy."""
    def __init__(self,epoch):
        self.epoch=epoch
        self.objects={}
    def spawn(self,epoch,object_id,kind):
        if epoch!=self.epoch or object_id in self.objects or kind not in ('npc','monster','other'):
            return False
        self.objects[object_id]=dict(kind=kind,alive=True)
        return True
    def move(self,epoch,object_id):
        return epoch==self.epoch and object_id in self.objects and self.objects[object_id]['alive']
    def die(self,epoch,object_id):
        if not self.move(epoch,object_id):return False
        self.objects[object_id]['alive']=False
        return True
    def remove(self,epoch,object_id):
        if epoch!=self.epoch or object_id not in self.objects:return False
        del self.objects[object_id]
        return True
    def change_map(self,epoch):
        self.epoch=epoch
        self.objects={}
