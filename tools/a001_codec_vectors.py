#!/usr/bin/env python3
"""A-001: synthetic BIN-derived seed 0..9 codec tests; NOT native wire captures."""
import hashlib

KEY = b"NexonInc."
MASK_SHA256 = (
    "40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880",
    "9928e9c8bc8135d230139fc07490277429a6f3ccdfb5e71d3d3c052f526baee4",
    "cd6816b77f68d70001fc3eaa4d42bdd67cb5973b3151cc5292ecc02a3daac6ab",
    "ea45b66f266752a18712d6ad62fc6a40fd26039d601e67b7d0b60da29a54bc0a",
    "6c0b229c4b4bb0d4c5b0d8be465a491b034167557629a32a363de03de899f62c",
    "65dec14522fe046d969c58f32f7bbfb486ceb48378d7b89c22b2f152b229cdba",
    "63f1ebfc2efe0b94a165ba3da8d1e0459def42b8d53d11467e45abbad1830e21",
    "9d61788315757a5a4945c92455032859e0379aa963174b9c355aec781daea37f",
    "b2dab527d5b3533b06dd606b34f65dd880cb52870326ee05eeeddc11714c5ad4",
    "80682999340209d29522e975c9eb32a2b6e03f886572536f43670daa679301ea",
)
GOLDEN_ORD2 = (
    "4c66786e684e6a6624446c7060604462703c5e74",
    "4f657b6d6b4d696527b9918d9d9db99f8dc1ddf7",
    "4c66786e684e6a6624446c7060604462703ca18b",
    "4f657b6d6b4d696527b8908c9c9cb89e8cc0a288",
    "4e647a6c6a4c686426476f7363634761733f5c76",
    "4a607e686e486c60224169756565416775395872",
    "4a607e686e486c6022416975656541677539a78d",
    "4a607e686e486c6022416975656541677539a78d",
    "4a607e686e486c60224169756565416775395872",
    "af859b8d8bad8985c7476f7363634761733f4268",
)


def masks(seed):
    if not 0 <= seed <= 9:
        raise ValueError("Only BIN-confirmed seed indexes 0..9")
    result = []
    for i in range(256):
        v = i - 128
        q = (-1 if v < 0 else 1) * (abs(v) // 8)
        values = (
            i, 128 + (-1 if i & 1 else 1) * ((i + 1) // 2),
            255 - i, 128 + (-1 if i & 1 else 1) * ((255 - i) // 2),
            (i >> 4) ** 2, (2 * i) & 255, 255 - ((2 * i) & 255),
            255 - 2 * i if i < 128 else 2 * i - 256,
            2 * i if i < 128 else 511 - 2 * i,
            255 - ((q * q) & 255),
        )
        result.append(values[seed])
    assert all(0 <= x <= 255 for x in result)
    return bytes(result)


def xor_body(body, key, ordinal, seed):
    """Symmetric body-only transform, not for plaintext exceptions."""
    if not key or not 0 <= ordinal < 256:
        raise ValueError("Need nonempty key, u8 ordinal")
    m = masks(seed)
    return bytes(
        b ^ key[i % len(key)] ^ m[ordinal] ^
        (m[(i // len(key)) & 255] if ((i // len(key)) & 255) != ordinal else 0)
        for i, b in enumerate(body)
    )


def test():
    known = bytes([0xaa, 0, 6, 0x62, 0]) + xor_body(b"aram", KEY, 0, 0)
    assert known.hex() == "aa000662002f171902"
    for seed in range(10):
        m = masks(seed)
        assert len(m) == 256 and hashlib.sha256(m).hexdigest() == MASK_SHA256[seed]
        body = bytes(range(20))
        assert xor_body(body, KEY, 2, seed).hex() == GOLDEN_ORD2[seed]
        for ordinal in (0, 1, 2, 9, 127, 255):
            body = bytes(range(255))
            assert xor_body(xor_body(body, KEY, ordinal, seed), KEY, ordinal, seed) == body
    assert "中文".encode("cp950").hex() == "a4a4a4e5"
    for s in (-1, 10, 255):
        try:
            masks(s)
        except ValueError:
            pass
        else:
            raise AssertionError("Unknown seed accepted")
    print("PASS A-001: 10 mask SHA256, 10 ordinal2 vectors, 60 roundtrips, seed0 C62, CP950")


if __name__ == "__main__":
    test()
