#!/usr/bin/env python3
"""A-029: SHA-locked original CChangePasswordPacket and LoginDialogPane code path.

Static observations are not native GUI execution. The synthetic password policy
is for the NEW server, not a claim about the original game server.
Never capture, print, or store real passwords in this test.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import struct
import unittest

EXPECTED_EXE_SHA = "db3df616f68b9f32163abc4b88de9d310562b2ddfe955aaa5ba7fcff729e1145"
IMAGE_BASE = 0x400000
# First byte address is native VA (the .text section happens to map file VA-0x400000).
ANCHORS = {
    "constructor_opcode_C26": (0x571a29, "6a26"),
    "constructor_vtable_CChangePassword": (0x571a3c, "c7067c376100"),
    "writer_field_1_account": (0x571ac4, "8d7e18"),
    "writer_field_2_old_password": (0x571ad9, "8dbe18020000"),
    "writer_field_3_new_password": (0x571af1, "8dbe2a020000"),
    "writer_three_string8_helpers": (0x571b04, "e8a796eeff"),
    "ui_construct_C26": (0x4a8ab1, "e85a8f0c00"),
    "ui_copy_control_8_account": (0x4a8ad1, "6a08"),
    "ui_copy_control_9_old": (0x4a8aec, "556a09"),
    "ui_copy_control_10_new": (0x4a8b09, "6a0a"),
    "ui_copy_control_11_confirmation": (0x4a8b23, "6a0b"),
    "ui_compare_new_confirmation": (0x4a8b39, "e824bf1000"),
    "ui_compare_old_new": (0x4a8bf4, "e869be1000"),
    "ui_enqueue_C26": (0x4a8d05, "e896fb0c00"),
    "generic_S02_packet_dispatch": (0x4a967a, "83fa68"),
    "generic_S02_callback_thunk": (0x4a9694, "e9c7f6ffff"),
    "generic_S02_read_status_byte": (0x4a8da2, "0fb64524"),
    "generic_S02_status_jump_table": (0x4a8daf, "0fb688e48f4a00"),
    "generic_S02_feedback_label": (0x4a8e85, "83c026"),
}
RTTI_NAME = b".?AVCChangePasswordPacket@@"
SRC_NAME = "packet\\cchangepassword.cpp".encode("utf-16le")


def verify_native_binary(path: str | Path) -> int:
    raw = Path(path).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_EXE_SHA:
        raise ValueError("Asgard.exe SHA256 mismatch; no cross-version inference")
    for name, (va, sig) in ANCHORS.items():
        expected = bytes.fromhex(sig)
        off = va - IMAGE_BASE
        if raw[off:off + len(expected)] != expected:
            raise ValueError("x86 native anchor mismatch: %s @ VA 0x%x" % (name, va))
    if RTTI_NAME not in raw or SRC_NAME not in raw:
        raise ValueError("CChangePasswordPacket RTTI / source path identity missing")
    return len(ANCHORS)


def string8(text: str, *, codepage="cp950") -> bytes:
    if not isinstance(text, str) or "\0" in text:
        raise ValueError("invalid string8")
    encoded = text.encode(codepage, "strict")
    if len(encoded) > 255:
        raise ValueError("string8 exceeds encoded u8 byte length")
    return bytes([len(encoded)]) + encoded


def synthetic_c26_body(account: str, old_password: str, new_password: str, *, codepage="cp950") -> bytes:
    """Synthetic exact writer field sequence, no opcode or framing included."""
    return b"".join(string8(x, codepage=codepage) for x in (account, old_password, new_password))


def decode_c26_body(body: bytes, *, codepage="cp950") -> tuple[str, str, str]:
    if not isinstance(body, bytes):
        raise ValueError("body must be bytes")
    off = 0
    out: list[str] = []
    for _ in range(3):
        if off >= len(body):
            raise ValueError("missing string8 byte length")
        n = body[off]
        off += 1
        if len(body) - off < n:
            raise ValueError("truncated string8")
        try:
            out.append(body[off:off+n].decode(codepage, "strict"))
        except UnicodeError as err:
            raise ValueError("invalid string8 encoding") from err
        off += n
    if off != len(body):
        raise ValueError("trailing bytes")
    return tuple(out)  # type: ignore[return-value]


def native_ui_submit_gate(old: str, new: str, confirm: str) -> str:
    """Only compare operations proven at VA 0x4a8b33 and 0x4a8bf4."""
    if new != confirm:
        return "reject-local-confirm-mismatch"  # source call shows message index 0x4d
    if old == new:
        return "reject-local-old-equals-new"  # message index 0x5d
    return "send-C26"


def designed_server_policy(new: str) -> bool:
    """Server-designed 4..8 ASCII alphanumeric, not native Client proof."""
    return 4 <= len(new) <= 8 and new.isascii() and new.isalnum()


class Tests(unittest.TestCase):
    def test_original_exe_19_signatures(self):
        path = getattr(Tests, "exe", None)
        if path is None:
            self.skipTest("Pass original Asgard.exe path to enable native static signatures")
        self.assertEqual(verify_native_binary(path), 19)

    def test_synthetic_three_string_fixture(self):
        self.assertEqual(synthetic_c26_body("Test01", "Old123", "New456").hex(),
                         "06546573743031064f6c64313233064e6577343536")

    def test_roundtrip(self):
        for fields in (("a", "b", "c"), ("Test01", "Old123", "New456"),
                       ("測試", "old4", "NEW5"), ("", "", "")):
            self.assertEqual(decode_c26_body(synthetic_c26_body(*fields)), fields)

    def test_confirmation_is_not_on_wire(self):
        self.assertEqual(synthetic_c26_body("A", "B", "C").count(b"\x01"), 3)
        self.assertEqual(len(decode_c26_body(synthetic_c26_body("A", "B", "C"))), 3)

    def test_native_confirm_mismatch(self):
        self.assertEqual(native_ui_submit_gate("OLD1", "NEW2", "NEW3"),
                         "reject-local-confirm-mismatch")

    def test_native_old_equals_new(self):
        self.assertEqual(native_ui_submit_gate("OLD1", "OLD1", "OLD1"),
                         "reject-local-old-equals-new")

    def test_native_ok_is_intent_not_server_acceptance(self):
        self.assertEqual(native_ui_submit_gate("OLD1", "NEW2", "NEW2"), "send-C26")

    def test_truncated_fixtures(self):
        raw = synthetic_c26_body("A", "B", "C")
        for i in range(len(raw)):
            with self.subTest(i=i), self.assertRaises(ValueError):
                decode_c26_body(raw[:i])

    def test_trailing_bytes_rejected(self):
        with self.assertRaises(ValueError):
            decode_c26_body(synthetic_c26_body("A", "B", "C") + b"\x00")

    def test_invalid_encoding(self):
        with self.assertRaises(ValueError):
            decode_c26_body(b"\x01\x81\x00\x00")

    def test_null_or_overlong_rejected(self):
        for value in ("a\0b", "a" * 256):
            with self.assertRaises(ValueError):
                string8(value)

    def test_enc_length_not_utf16_code_units(self):
        self.assertEqual(string8("測試")[0], 4)

    def test_server_design_4_to_8_ascii(self):
        for value in ("Ab12", "Z" * 8, "abcd5"):
            self.assertTrue(designed_server_policy(value))
        for value in ("abc", "A" * 9, "abc_", "測試AB", "a b c", ""):
            self.assertFalse(designed_server_policy(value))

    def test_password_confirm_not_credential_proof(self):
        self.assertEqual(native_ui_submit_gate("WRONG", "GOOD1", "GOOD1"), "send-C26")
        self.assertTrue(designed_server_policy("GOOD1"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("exe", type=Path, nargs="?", help="Local original Asgard.exe (never uploaded)")
    args = parser.parse_args()
    if args.exe is not None:
        Tests.exe = args.exe
    unittest.main(argv=["a029_native_probe"], verbosity=2)
