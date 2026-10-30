"""A-004 conservative decoded Client body codec, S33 flags=0 profile only."""
import struct
class PacketError(ValueError): pass
def _read(data,fmt):
    if len(data)!=struct.calcsize(fmt): raise PacketError("invalid length")
    return struct.unpack(fmt,data)
def parse_s06(data):
    oid,a,b=_read(data,">IHH")
    return dict(opaque_u32=oid,field_u16_a=a,field_u16_b=b)
def parse_s11(data):
    oid,direction=_read(data,">IB")
    return dict(opaque_u32=oid,direction=direction)
def parse_s0e(data):
    (oid,)=_read(data,">I")
    return dict(opaque_u32=oid)
def parse_s0b(data):
    x,y,seq=_read(data,">HHB")
    return dict(x=x,y=y,sequence_low7=seq&127,status_bit7=bool(seq&128))
def parse_s33_zero_flags(data,codepage="cp950"):
    if len(data)<42: raise PacketError("truncated S33")
    x,y,facing,oid=struct.unpack_from(">HHBI",data,0)
    flags=struct.unpack_from(">I",data,26)[0]
    if flags: raise PacketError("unsupported optional S33 flags")
    n=data[34]
    if n==0 or len(data)!=42+n: raise PacketError("invalid string8 or trailing data")
    try: name=data[35:35+n].decode(codepage,"strict")
    except UnicodeError as e: raise PacketError("invalid name bytes") from e
    return dict(object_id=oid,x=x,y=y,facing=facing,name=name,flags=flags,look_raw=data[9:34].hex())
class VisibilityProjection:
    """Designed model, not original Client behavior: never trust stale epoch."""
    def __init__(self,map_instance,epoch,self_id):
        self.map_instance,self.epoch,self.self_id=map_instance,epoch,self_id
        self.humans={}
        self.retired_ids=set()
    def spawn_or_refresh(self,epoch,human):
        oid=human["object_id"]
        if epoch!=self.epoch or oid in (0,self.self_id) or oid in self.retired_ids: return False
        self.humans[oid]=dict(human)
        return True
    def remote_position(self,epoch,oid,x,y):
        if epoch!=self.epoch or oid not in self.humans: return False
        self.humans[oid].update(x=x,y=y)
        return True
    def remote_direction(self,epoch,oid,facing):
        if epoch!=self.epoch or oid not in self.humans: return False
        self.humans[oid]["facing"]=facing
        return True
    def remove(self,epoch,oid):
        if epoch!=self.epoch or oid not in self.humans: return False
        del self.humans[oid]
        self.retired_ids.add(oid)
        return True
    def reenter(self,map_instance,epoch):
        if epoch==self.epoch: raise ValueError("epoch must change")
        self.map_instance,self.epoch=map_instance,epoch
        self.humans.clear()
        self.retired_ids.clear()
