"""A-031 native C10→C25 handoff profiles, strictly original decoded bodies.

Original Asgard.exe SHA256:
db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145

C10 writer 0x5773E0 is raw token bytes; no nested length.
C25 CBillingInfoPacket ctor 0x5712E0, writer 0x571420:
only region==3 writes three native wide-to-encoded string8 fields, sources
[global 0x66D100]+0x0c,+0x20c,+0x40e in sender 0x4A8478.
Do not interpret these fields as credential/character identities.
"""
class PacketError(ValueError):
    pass


def c10_raw_token(token: bytes) -> bytes:
    """Decoded C10 body is the unchanged transfer token (no added length)."""
    if not isinstance(token, (bytes, bytearray)) or not 0 < len(token) <= 255:
        raise PacketError("transfer token must be 1..255 bytes")
    return bytes(token)


def c25_region3_encoded(fields):
    """Native profile region3: three 1-byte-length + encoded raw bytes.

    Input must already be language-profile encoded: original 0x45B1B0 uses
    Client's active codepage; do not force CP950 on another region/build.
    This helper models the wire only, not a guaranteed real UI sender.
    """
    if not isinstance(fields, (list, tuple)) or len(fields) != 3:
        raise PacketError("expected exactly three encoded native fields")
    out=bytearray()
    for f in fields:
        if not isinstance(f, (bytes, bytearray)) or len(f) > 255:
            raise PacketError("string8 field must have <=255 encoded bytes")
        out.append(len(f))
        out.extend(f)
    return bytes(out)


def parse_c25_region3(body):
    if not isinstance(body, (bytes, bytearray, memoryview)):
        raise PacketError("invalid C25 decoded body")
    buf=bytes(body);offset=0;res=[]
    for _ in range(3):
        if offset>=len(buf):
            raise PacketError("truncated string8 length")
        length=buf[offset];offset+=1
        if offset+length>len(buf):
            raise PacketError("truncated string8 payload")
        res.append(buf[offset:offset+length])
        offset+=length
    if offset!=len(buf):
        raise PacketError("trailing C25 bytes")
    return tuple(res)


def c25_native_codec_for_region(region):
    """This binary's known C25 writer emits THREE string8 only if region 3.

    For non-3, ctor exists but native serializer emits zero bytes. All four
    *discovered direct producers* guard region==3, so do not demand C25 from
    non-3 clients. An empty possible packet body is NOT proof it is sent.
    """
    if type(region) is not int or not 0 <= region <= 255:
        raise PacketError("region out of range")
    return "three-string8" if region == 3 else "empty-body-if-called-no-known-producer"


def native_world_send_profile(region, transfer_token, billing_fields=None):
    """Descriptive safe fixture, NOT a model of Server's original auth policy.

    0x4A8415/0x4A8446 send C10; in region3 0x4A8478/0x4A84F3 send
    C25 on the same callback; 0x52FB5B/0x52FB8C then 0x52FBD6/
    0x52FC4B show a second post-C10 route.
    """
    c10=c10_raw_token(transfer_token)
    c25=[]
    if c25_native_codec_for_region(region)=="three-string8":
        if billing_fields is None:
            raise PacketError("region3 requires three original field bytes")
        c25=[(0x25,c25_region3_encoded(billing_fields))]
    elif billing_fields is not None:
        raise PacketError("no native C25 sender proven for non-region3")
    return [(0x10,c10)]+c25
