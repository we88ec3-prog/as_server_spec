#!/usr/bin/env python3
"""Offline A-023 byte evidence and synthetic body checks; no Client execution."""
import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

from verify_entry_dependencies import verify as verify_dependencies

CLIENT_SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
# Bounded original-byte evidence, not a complete disassembly or source dump.
SIGNATURES = {
    0x586410: "515356578bf1e89549edff8bce884618e88b49edff",
    0x586462: "8bcee8474aedff8bce89861c020000e83a4aedff8bce898620020000e82d49edff",
    0x5864FD: "8bcee8dc48edff6acc6689862c020000",
    0x5867BC: "626458008a655800b6675800b66758002d665800",
    0x52C464: "558bcee8c4f8ffff",
    0x52BE8B: "e8905dffff",
    0x52C014: "e8878fffff",
    0x525090: "6858dd6000",
    0x5250B8: "ff502c",
    0x5268C6: "c6462404",
    0x5268F4: "e8a71f05008d4ff4e84f2bffff",
    0x519479: "8b873c02000085c07574",
    0x5194CE: "c6462402",
    0x521CFB: "c7873c02000000000000",
    0x45AACD: "b901000000c70080595f00894810894814",
    0x4984FA: "a37ce46600",
    0x60855C: "04000000a803000002000000",
    0x615A10: "00000000963007772c610eeeba51099919c46d07",
}


def verify_binary(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != CLIENT_SHA:
        raise ValueError("wrong Client SHA256")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    base = struct.unpack_from("<I", data, pe + 52)[0]
    sections = []
    for index in range(count):
        offset = pe + 24 + optional_size + index * 40
        _, rva, size, raw = struct.unpack_from("<IIII", data, offset + 8)
        sections.append((base + rva, size, raw))
    for address, expected in SIGNATURES.items():
        match = bytes.fromhex(expected)
        for start, size, raw in sections:
            if start <= address and address + len(match) <= start + size:
                position = raw + address - start
                if data[position:position + len(match)] != match:
                    raise ValueError("byte evidence mismatch: " + hex(address))
                break
        else:
            raise ValueError("unmapped byte evidence: " + hex(address))
    return {"sha256": CLIENT_SHA, "verified_byte_spans": len(SIGNATURES),
            "literal_Born_ascii_or_utf16": any(
                name in data for name in (b"Born", "Born".encode("utf-16le")))}


class BodyReader:
    def __init__(self, body):
        self.body, self.position = body, 0

    def take(self, size):
        if self.position + size > len(self.body):
            raise ValueError("truncated body")
        value = self.body[self.position:self.position + size]
        self.position += size
        return value

    def uint(self, size):
        return int.from_bytes(self.take(size), "big")

    def string8(self):
        return self.take(self.uint(1)).decode("cp950", errors="strict")

    def done(self):
        if self.position != len(self.body):
            raise ValueError("trailing body bytes (strict offline contract)")


def parse_start(body):
    reader = BodyReader(body)
    if (reader.uint(1), reader.uint(1)) != (1, 0):
        raise ValueError("expected S44 type1/subtype0 start")
    result = {"script": reader.string8(), "context": reader.uint(4),
              "crc32": reader.uint(4)}
    result["dependencies"] = [
        {"script": reader.string8(), "crc32": reader.uint(4)}
        for _ in range(reader.uint(1))]
    result["parameters"] = [
        [reader.string8(), reader.string8()] for _ in range(reader.uint(2))]
    reader.done()
    return result


def string8(text):
    encoded = text.encode("cp950", errors="strict")
    if len(encoded) > 255:
        raise ValueError("string8 exceeds byte length")
    return bytes([len(encoded)]) + encoded


def resource_crc(path):
    payload = zlib.decompress(path.read_bytes())
    version, units = struct.unpack(">HI", payload[:6])
    if version != 1 or len(payload) != 6 + units * 2:
        raise ValueError("invalid native Script wrapper")
    encoded = payload[6:].decode("utf-16le").encode("cp950", errors="strict")
    return zlib.crc32(encoded)


def verify(client, directory):
    binary = verify_binary(client)
    verify_dependencies(directory)
    born_crc = resource_crc(directory / "Born.dat")
    paper_crc = resource_crc(directory / "PaperDialog.dat")
    # Explicitly designed context token, not an original-server observation.
    context = 0x11223344
    body = (b"\x01\x00" + string8("Born") + struct.pack(">II", context, born_crc)
            + b"\x01" + string8("PaperDialog") + struct.pack(">IH", paper_crc, 0))
    if body.hex() != "010004426f726e112233441d87b0c0010b50617065724469616c6f67f870c5740000":
        raise ValueError("fixed start vector mismatch")
    parsed = parse_start(body)
    assert parsed == {"script": "Born", "context": context, "crc32": born_crc,
                      "dependencies": [{"script": "PaperDialog", "crc32": paper_crc}],
                      "parameters": []}
    rejected = 0
    for size in range(len(body)):
        try:
            parse_start(body[:size])
        except ValueError:
            rejected += 1
        else:
            raise ValueError("truncated start accepted at " + str(size))
    for invalid in [body + b"\x00", b"\x01\x03" + body[2:],
                    b"\x02\x00" + body[2:]]:
        try:
            parse_start(invalid)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid start accepted")
    return {"result": "PASS", "kind": "offline-static-and-synthetic",
            "binary": binary, "codepage_condition": "LanguageMan index 4 / CP950",
            "born_crc32_cp950": f"{born_crc:08x}",
            "paper_crc32_cp950": f"{paper_crc:08x}",
            "synthetic_s44_start_body_hex": body.hex(),
            "decoded_start": parsed,
            "synthetic_close_bodies_hex": [
                (bytes([subtype]) + string8("Born") + struct.pack(">I", context)).hex()
                for subtype in (4, 2)],
            "negative_body_cases_rejected": rejected,
            "native_client_validation": "not-run",
            "original_server_first_login_policy": "unknown"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("client", type=Path)
    parser.add_argument("script_directory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.client, args.script_directory), ensure_ascii=False, indent=2))
    except (OSError, ValueError, struct.error, zlib.error) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
