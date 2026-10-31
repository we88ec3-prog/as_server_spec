"""A-024 original-client decoded-body parser, static source Asgard.exe SHA db3df616...

S07 row dispatch proven from 0x57E45A jump table at 0x57E5D4/0x57E5E8.
Other small packet readers from MSVC RTTI/vtables. No Server AI inferred.
"""
import struct


class PacketError(ValueError):
    pass


class Reader:
    def __init__(self, data):
        self.data = bytes(data)
        self.pos = 0

    def take(self, n):
        if n < 0 or self.pos + n > len(self.data):
            raise PacketError("truncated decoded body")
        result = self.data[self.pos:self.pos+n]
        self.pos += n
        return result

    def u8(self):
        return self.take(1)[0]

    def u16(self):
        return int.from_bytes(self.take(2), "big")

    def u32(self):
        return int.from_bytes(self.take(4), "big")

    def string8(self):
        return self.take(self.u8())  # raw CP950 bytes, not chars

    def finish(self):
        if self.pos != len(self.data):
            raise PacketError("unexpected trailing decoded bytes")


def draw_objects_s07(body, *, max_records=1024):
    """S07, all 1..14 native row branch layouts. Max is a designed guard."""
    r = Reader(body)
    count = r.u16()
    if count > max_records:
        raise PacketError("unsafe record count (designed guard)")
    rows = []
    for _ in range(count):
        row = dict(x_or_field_a=r.u16(), y_or_field_b=r.u16(),
                   kind=r.u8(), object_key_candidate=r.u32(), field_c=r.u16())
        kind = row["kind"]
        if kind in (1, 2, 4):
            row["variant5"] = list(r.take(5))
            row["variant_u16"] = r.u16()
            flags = row["variant_flags_u32"] = r.u32()
            if flags & 0x01:
                row["optional_u8x3"] = list(r.take(3))
            if flags & 0x02:
                row["optional_u8"] = r.u8()
            if flags & 0x10:
                row["optional_u16"] = r.u16()
            row["name_raw_cp950"] = r.string8()
        elif kind == 3:
            row["variant5"] = list(r.take(5))
            row["name_raw_cp950"] = r.string8()
        elif 5 <= kind <= 12:
            pass  # native jump table directly returns to row loop
        elif kind == 13:
            row["name_raw_cp950"] = r.string8()
        elif kind == 14:
            row["variant2"] = list(r.take(2))
            row["variant_u16"] = r.u16()
        else:
            raise PacketError("unsupported nonstandard S07 kind (native fallthrough unknown)")
        rows.append(row)
    r.finish()
    return {"count": count, "rows": rows}


def decode_s3c_show_object_info(body):
    r = Reader(body)
    value = dict(object_key_candidate=r.u32(), options=list(r.take(3)))
    r.finish()
    return value


def decode_s34_info_reply(body):
    """S34 subtype 6 or native default; subtype 11 dynamic groups excluded."""
    r = Reader(body)
    kind = r.u8()
    result = dict(subtype=kind, object_key_candidate=r.u32(), flags=r.u8())
    if kind == 6:
        result["subtype6"] = dict(field_u16=r.u16(), first_u8=r.u8(),
                                  field_u32=r.u32(), tail_u8=list(r.take(3)))
    elif kind == 11:
        raise PacketError("S34 subtype 11 dynamic payload not yet covered")
    r.finish()
    return result


def decode_s62_add_action(body):
    r = Reader(body)
    result = dict(tag_a=r.u8(), tag_b=r.u8(), field_u16=r.u16(),
                  option_u8=list(r.take(3)), texts_raw_cp950=[r.string8() for _ in range(4)],
                  extra_u8=r.u8(), extra_u16=r.u16(), final_u8=r.u8())
    r.finish()
    return result


def decode_s63_remove_action(body):
    r = Reader(body)
    result = {"tag_a": r.u8(), "tag_b": r.u8()}
    r.finish()
    return result


def decode_s29_effect(body):
    r = Reader(body)
    result = dict(opaque_u32=[r.u32(), r.u32()],
                  opaque_u16=[r.u16(), r.u16()], kind_or_flags=r.u8())
    r.finish()
    return result
