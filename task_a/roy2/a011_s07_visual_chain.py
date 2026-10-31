"""A-011: original S07 kind1/2/4 visual source to MonsterImageLib.

Original Asgard.exe: packet reader 0x57E456 row+0x0C -> World handler
0x4F1A7F descriptor -> MonsterObject 0x4D6FA0 copies the descriptor
and 0x4D2340 dereferences its first u16 into 0x4D7530/0x4D7560.
The S07 variant_u16 row+0x222 is NOT the image ID; it is passed as
a separate constructor argument, converted to float at 0x4D7056.
Original MonsterXX DAT/DOI members and native GUI remain unverified.
"""
from dataclasses import dataclass

from a011_resource_codec import (
    MONSTER_IMAGE_FIRST,
    MONSTER_IMAGE_LAST,
    monster_image_ref,
)
from a024_object_packets import draw_objects_s07

MONSTER_OBJECT_KINDS = frozenset((1, 2, 4))


@dataclass(frozen=True)
class S07Visual:
    x: int
    y: int
    kind: int
    scene_object_ref: int
    image_id: int
    variant_u16_not_image_id: int
    image_library: int | None
    archive: str | None
    slot: int | None
    mapping_status: str


def project_s07_visuals(decoded_body: bytes, *, max_records=1024):
    """Project the proven MonsterObject image field from decoded S07.

    Out-of-pool values remain unresolved, not invalid Client packets.
    The 0x4000..0x41AD bounds are a designed guard from registered banks.
    """
    packet = draw_objects_s07(decoded_body, max_records=max_records)
    visuals = []
    for row in packet["rows"]:
        if row["kind"] not in MONSTER_OBJECT_KINDS:
            continue
        image_id = row["field_c"]
        ref = (
            monster_image_ref(image_id)
            if MONSTER_IMAGE_FIRST <= image_id <= MONSTER_IMAGE_LAST
            else None
        )
        visuals.append(
            S07Visual(
                x=row["x_or_field_a"],
                y=row["y_or_field_b"],
                kind=row["kind"],
                scene_object_ref=row["object_key_candidate"],
                image_id=image_id,
                variant_u16_not_image_id=row["variant_u16"],
                image_library=ref.library_id if ref else None,
                archive=ref.archive_name if ref else None,
                slot=ref.local_image_slot if ref else None,
                mapping_status=(
                    "registered-monster-archive-formula-only"
                    if ref
                    else "unresolved-image-namespace"
                ),
            )
        )
    return tuple(visuals)
