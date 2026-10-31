"""A-011 original Client resource ID mapping and C43 click request (decoded body).

Evidence SHA-locked Asgard.exe:
0x404331..0x4043AF library registrations; 0x4D7530/0x4D7560 animation image map;
0x479DDB..0x479DEB, 0x4A2409..0x4A2410 two known C43 producers.
No original archive content or native Client click E2E.
"""
from dataclasses import dataclass
import struct

MONSTER_IMAGE_FIRST = 0x4000
MONSTER_LIB_FIRST = 0x1F40
MONSTER_LIB_LAST = 0x1F6A
WORLD_LIB_FIRST = 0x1B58
WORLD_LIB_LAST = 0x1B6F
FRAMES_PER_MONSTER_ARCHIVE = 10
MONSTER_IMAGE_LAST = MONSTER_IMAGE_FIRST + (
    MONSTER_LIB_LAST - MONSTER_LIB_FIRST + 1) * FRAMES_PER_MONSTER_ARCHIVE - 1


@dataclass(frozen=True)
class MonsterImageRef:
    client_image_id: int
    library_id: int
    archive_name: str
    local_image_slot: int


def monster_image_ref(image_id: int) -> MonsterImageRef:
    """Client quotient/remainder mapping; numeric bounds are safe registered-pool guard.

    Formula native 0x4D7530 and 0x4D7560:
    library_id = 0x1F40 + floor((image_id-0x4000)/10)
    image_slot = (image_id-0x4000)%10
    """
    if type(image_id) is not int or not MONSTER_IMAGE_FIRST <= image_id <= MONSTER_IMAGE_LAST:
        raise ValueError("image ID outside this Client's registered Monster00..42 libraries")
    index=image_id-MONSTER_IMAGE_FIRST
    archive=index//FRAMES_PER_MONSTER_ARCHIVE
    return MonsterImageRef(image_id, MONSTER_LIB_FIRST+archive,
                           f"Monster{archive:02d}.dat",index%FRAMES_PER_MONSTER_ARCHIVE)


def world_archive_ref(library_id: int) -> str:
    """Registry World00..23, 0x404331..0x40436f; NOT monster species id."""
    if type(library_id) is not int or not WORLD_LIB_FIRST <= library_id <= WORLD_LIB_LAST:
        raise ValueError("library ID not in registered World00..23")
    return f"World{library_id-WORLD_LIB_FIRST:02d}.dat"


def c43_known_info_request(entity_key: int, kind=1, subtype=4) -> bytes:
    """Two observed UI producers 0x479dc7/0x4a23f8 use kind1/subtype4.

    A general C43 writer accepts any byte fields, but this API intentionally
    only reproduces the observed producer profile, never invents NPC click semantics.
    """
    if type(entity_key) is not int or not 0 <= entity_key <= 0xffffffff:
        raise ValueError("entity key must fit BE u32")
    if kind != 1 or subtype != 4:
        raise ValueError("unsupported producer branch; no claim all NPC clicks use C43")
    return struct.pack(">BIB",1,entity_key,4)


def known_s07_monster_object_kind(kind: int) -> bool:
    """S07 handler 0x4f1a8b/0x4f1b68/0x4f1bd1 calls MonsterObject ctor 0x4d6fa0."""
    return kind in (1,2,4)


def select_monster_local_motion(base: int, selector: int):
    """Native 0x4d6bc0: selector 0..5 => offsets 0x20,0x30,0x40 repeated.

    Labels such as walk/attack/die are NOT proven from this selector alone.
    """
    if type(base) is not int or not 0 <= base <= 0xffff:
        raise ValueError("base motion field must be uint16")
    if type(selector) is not int or not 0 <= selector <= 5:
        raise ValueError("motion selector outside demonstrated native dispatch")
    return (base + (0x20,0x30,0x40)[selector%3])&0xffff
