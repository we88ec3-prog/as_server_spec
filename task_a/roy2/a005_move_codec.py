#!/usr/bin/env python3
"""A005 movement decoded-body fields and separately DESIGNED Server controls."""
import struct
class MoveError(ValueError): pass
def parse_c33(body):
    if len(body)!=3:raise MoveError("C33 requires exactly 3 bytes")
    direction,sequence,gait=body
    return {"direction_raw":direction,"sequence_raw":sequence,
            "gait_flags":gait,"sequence_mod128":sequence&127,
            "sequence_high_bit":bool(sequence&128)}
def parse_c11(body):
    if len(body)!=1:raise MoveError("C11 requires exactly 1 byte")
    return {"direction_raw":body[0]}
def parse_s0b(body):
    if len(body)!=5:raise MoveError("S0B requires exactly 5 bytes")
    x,y,seq=struct.unpack(">HHB",body)
    return {"x":x,"y":y,"status_sequence_raw":seq,
            "sequence_mod128":seq&127,"high_bit":bool(seq&128)}
def encode_s0b(x,y,seq,high_bit):
    if not all(isinstance(v,int) for v in (x,y,seq)):
        raise MoveError("not integers")
    if not(0<=x<=65535 and 0<=y<=65535 and 0<=seq<=127):
        raise MoveError("range")
    return struct.pack(">HHB",x,y,seq|(0x80 if high_bit else 0))
def observed_line_bit4(flag_u32):
    """Native 0x4B4BB0 line-test bit ONLY; NOT verified walkability."""
    return bool(flag_u32&0x10)
class DesignedMoveGate:
    """All move policy here is a Server proposal, not original Server evidence."""
    def __init__(self,map_instance,epoch,x,y,max_step=1):
        self.map_instance,self.epoch=map_instance,epoch
        self.x,self.y=x,y
        self.max_step=max_step
        self.last_seq=None
    def apply(self,epoch,seq,dest,*,speed_ok,collision_ok,direction):
        if epoch!=self.epoch:return False,"stale-epoch"
        if not 0<=direction<=7:return False,"invalid-direction"
        if not 0<=seq<=127:return False,"invalid-seq"
        if self.last_seq is not None and seq!=(self.last_seq+1)%128:
            return False,"duplicate-or-out-of-order"
        if not(0<=dest[0]<=65535 and 0<=dest[1]<=65535):
            return False,"out-of-bounds"
        if abs(dest[0]-self.x)>self.max_step or abs(dest[1]-self.y)>self.max_step:
            return False,"step-limit"
        if not speed_ok:return False,"speed"
        if not collision_ok:return False,"collision"
        self.x,self.y=dest
        self.last_seq=seq
        return True,"accepted"
    def change_map(self,map_instance,epoch,x,y):
        if epoch==self.epoch:raise ValueError("epoch must advance")
        self.map_instance,self.epoch,self.x,self.y=map_instance,epoch,x,y
        self.last_seq=None
