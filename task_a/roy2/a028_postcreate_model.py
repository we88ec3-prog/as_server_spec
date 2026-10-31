"""A028 original-Client-observable subset of NewUser S02 dispatch.

These are narrow synthetic state transitions inferred from SHA-locked PE code.
No claim about original Server commit, actual World connection, UI rendering
or official error-code meanings.
"""
from dataclasses import dataclass

class NativeCreationError(ValueError):
    pass

@dataclass(frozen=True)
class NewUserReaction:
    state_before: int
    state_after: int
    outgoing: tuple
    clear_ui_slots: tuple
    focus: str|None
    message_modal_candidate: bool
    login_pane_constructed: bool
    auto_c03_proven: bool = False
    world_transfer_proven: bool = False


def s02_decoded_body(raw):
    """Original S02 parser: u8 status, string8 (encoded byte length + bytes)."""
    if not isinstance(raw,(bytes,bytearray,memoryview)):
        raise NativeCreationError("S02 body must be bytes")
    b=bytes(raw)
    if len(b)<2:
        raise NativeCreationError("truncated S02")
    n=b[1]
    if len(b)!=2+n:
        raise NativeCreationError("S02 string8 truncated or trailing")
    return b[0],b[2:]


def synthetic_response(state,status,region,appearance=None,encoded_message=b""):
    """Model only branches explicitly observed at 0x4B1D60..0x4B217A.

    First success (state1D) issues C04 and state1E.
    Other-state success (including state1E) enters local UI cleanup;
    Region3 *constructs* LoginDialogPane, but that is not proof of
    visible manual-login nor automatically sending C03 or World transfer.
    Failure issues empty C15 and sets state1F; focus table is local only.
    """
    for value in (state,status,region):
        if type(value) is not int or value<0 or value>255:
            raise NativeCreationError("invalid state/status/region")
    if not isinstance(encoded_message,(bytes,bytearray)):
        raise NativeCreationError("message bytes expected")
    if len(encoded_message)>255:
        raise NativeCreationError("native string8 message byte length exceeded")
    focus={3:"first",4:"first",17:"second",18:"first",26:"first",31:"first"}.get(status)
    modal=bool(encoded_message) and not (state==0x1E and region==3)
    if status!=0:
        return NewUserReaction(state,0x1F,((0x15,b""),),(),focus,modal,False)
    if state==0x1D:
        if not isinstance(appearance,(tuple,list)) or len(appearance)!=5:
            raise NativeCreationError("C04 requires five appearance u8 values")
        if any(type(x) is not int or x<0 or x>255 for x in appearance):
            raise NativeCreationError("invalid C04 appearance byte")
        return NewUserReaction(state,0x1E,((0x04,bytes(appearance)),),(),None,modal,False)
    return NewUserReaction(state,state,(),(12,11,13,7),None,modal,region==3)
