#!/usr/bin/env python3
"""A-022 SHA-locked original MAP C35 census; derived metadata only.

Asgard.exe VA 0x4B2EC0, 0x43E0A0. Offline static reconstruction, NOT
a captured original-client C35 packet. Do not use raw MAP file CRC.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import struct

EXE_SHA = 'db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145'
ARCHIVES = {
    'Map0.dat': ('dcaf8ab51f138fe9f5f26fa5dbfbd11b49a23df4b15da4ae7945d21f89f77761', 288),
    'Map1.dat': ('8681dc75ef2517ffa02ca6aa3c2d849a412544d250b659ae2b9a38189055487b', 184),
    'Map2.dat': ('5320a09576ad2199853a2613a00e65c2181e25c8c3b4f5a3d88099ef04893bcb', 22),
}


class InvalidResource(ValueError):
    pass


def native_table(exe):
    if hashlib.sha256(exe).hexdigest() != EXE_SHA:
        raise InvalidResource('Asgard.exe SHA mismatch')
    # VA 0x664720, PE raw offset 0x264720 for this SHA-locked image.
    table = struct.unpack_from('<256H', exe, 0x264720)
    if table[:3] != (0, 0x1021, 0x2042):
        raise InvalidResource('CRC table signature mismatch')
    return table


def feed(crc, sequence, table):
    for value in sequence:
        crc = (table[(crc >> 8) & 255] ^ (crc << 8) ^ value) & 65535
    return crc


def read_members(data, library):
    if len(data) < 76:
        raise InvalidResource('DAT too short')
    slots, = struct.unpack_from('<I', data)
    if not 2 <= slots <= 200000 or 4 + 36 * slots > len(data):
        raise InvalidResource('DAT slot count invalid')
    offsets = [struct.unpack_from('<I', data, 4 + 36 * i)[0] for i in range(slots)]
    if offsets[0] != 4 + 36 * slots or offsets[-1] != len(data) or any(
        a >= b for a, b in zip(offsets, offsets[1:])
    ):
        raise InvalidResource('DAT offsets/sentinel invalid')
    seen = set()
    for i in range(slots - 1):
        name = data[8 + 36*i:40 + 36*i].split(b'\x00')[0]
        if not re.fullmatch(rb'[0-9]{5}\.map', name):
            raise InvalidResource('unexpected member name')
        map_ref = int(name[:5])
        if map_ref // 10000 != library or map_ref in seen or map_ref > 65535:
            raise InvalidResource('wrong library or duplicate map_ref')
        seen.add(map_ref)
        yield map_ref, memoryview(data)[offsets[i]:offsets[i+1]]


def native_c35(payload, table):
    """Emulate 0x4B2EC0: blocks, tiles, normalized 7/8/16B tails."""
    data = memoryview(payload)
    if len(data) < 20:
        raise InvalidResource('MAP too short')
    h0, h1, h2, w, h = struct.unpack_from('<HHHBB', data)
    if not w or not h:
        raise InvalidResource('MAP zero dimensions')
    tile_end = 8 + ((w+1)//2) * ((h+3)//4) * 2 + w * h * 10
    if tile_end > len(data):
        raise InvalidResource('MAP truncated block or tile')
    crc = feed(0, data[8:tile_end], table)
    offset = tile_end
    counts = []
    for stride in (7, 8, 16):
        if offset + 4 > len(data):
            raise InvalidResource('MAP truncated record count')
        count, = struct.unpack_from('<I', data, offset)
        offset += 4
        if count > (len(data) - offset) // stride:
            raise InvalidResource('MAP truncated records')
        counts.append(count)
        for j in range(count):
            p = offset + j * stride
            if stride == 7:
                flag, u, x, y = struct.unpack_from('<BHhh', data, p)
                canonical = bytes((int(flag != 0),)) + struct.pack('<Hii', u, x, y)
            elif stride == 8:
                canonical = data[p:p+8]
            else:
                a, b = struct.unpack_from('<HH', data, p)
                canonical = (struct.pack('<H', a) +
                             bytes((int(b != 0), int(data[p+3] != 0), data[p+4])) +
                             data[p+8:p+16].tobytes())
            crc = feed(crc, canonical, table)
        offset += count * stride
    if offset != len(data):
        raise InvalidResource('MAP trailing bytes')
    return {'width':w, 'height':h, 'header_word':h2, 'checksum':crc,
            'c35_be_hex':struct.pack('>HH', h2, crc).hex().upper(),
            'tail_counts_7_8_16':counts}


def census(exe_path, map_dir):
    table = native_table(Path(exe_path).read_bytes())
    maps = []
    for library, (name, (expect_sha, expect_count)) in enumerate(ARCHIVES.items()):
        blob = (Path(map_dir)/name).read_bytes()
        if hashlib.sha256(blob).hexdigest() != expect_sha:
            raise InvalidResource(f'{name} SHA mismatch')
        entries = list(read_members(blob, library))
        if len(entries) != expect_count:
            raise InvalidResource(f'{name} unexpected count')
        for map_ref, payload in entries:
            info = native_c35(payload, table)
            maps.append({'map_ref':map_ref, 'archive':name,
                         'payload_sha256':hashlib.sha256(payload).hexdigest(), **info})
    pairs, payloads = defaultdict(list), defaultdict(list)
    for record in maps:
        pairs[record['c35_be_hex']].append(record)
        payloads[record['payload_sha256']].append(record)
    collisions = {pair:sorted(set(m['payload_sha256'] for m in group))
                  for pair, group in pairs.items()
                  if len(set(m['payload_sha256'] for m in group)) > 1}
    summary = {
        'source':'original static executable + original resource reconstruction; no native C35 capture',
        'native_client_validation':'not-run',
        'exe_sha256':EXE_SHA,
        'archives_sha256':{name:spec[0] for name,spec in ARCHIVES.items()},
        'map_count':len(maps),
        'unique_map_payloads':len(payloads),
        'unique_c35_pairs':len(pairs),
        'repeated_c35_groups':sum(len(group)>1 for group in pairs.values()),
        'map_ids_in_repeated_pairs':sum(len(group) for group in pairs.values() if len(group)>1),
        'different_payload_same_c35_groups':len(collisions),
        'different_payload_same_c35':collisions,
        'player_walkability':'unknown',
        'official_tutorial_map_and_spawn':'unknown'
    }
    if len(maps) != 494:
        raise InvalidResource('expected 494 original MAP members')
    return summary, sorted(maps, key=lambda m:m['map_ref'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe',type=Path,required=True)
    parser.add_argument('--map-dir',type=Path,required=True)
    parser.add_argument('--json',type=Path,help='optional metadata-only full 494-map manifest')
    args = parser.parse_args()
    try:
        summary, maps = census(args.exe, args.map_dir)
        if args.json:
            args.json.write_text(json.dumps({'summary':summary,'maps':maps},
                                 ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(summary,ensure_ascii=False,indent=2))
    except (InvalidResource, OSError, struct.error) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
