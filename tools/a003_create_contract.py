#!/usr/bin/env python3
"""A-003 BIN-derived synthetic packet fixtures; owner/uniqueness model is designed."""
import sqlite3
import unittest

# Raw Asgard.exe .data VA 0x66422C: little-endian DWORDs; C04 uses low 3 bytes.
COLORS = (0x285A91, 0x6464FF, 0xFAB482, 0xFFFFB9, 0xE6B4FA,
          0x0096FF, 0x64BE82, 0x64FFD5, 0x95C8FF, 0x5A5A5A)


def rgb(index):
    if not isinstance(index, int) or not 0 <= index < len(COLORS):
        raise ValueError("invalid native UI color index")
    return COLORS[index].to_bytes(4, "little")[:3]


def encode_c02(region, fields, flag=0):
    extended = region in (2, 3, 4)
    if len(fields) != (4 if extended else 3) or not 0 <= flag <= 255:
        raise ValueError("region/field mismatch")
    result = bytearray()
    for f in fields:
        if len(f) > 255: raise ValueError("string8 length > 255")
        result += bytes([len(f)]) + f
    return bytes(result) + (bytes([flag]) if extended else b"")


def decode_c02(region, body):
    extended = region in (2, 3, 4)
    fields, pos = [], 0
    for _ in range(4 if extended else 3):
        if pos >= len(body): raise ValueError("missing length")
        count = body[pos]
        pos += 1
        if pos + count > len(body): raise ValueError("short value")
        fields.append(body[pos:pos+count]); pos += count
    flag = None
    if extended:
        if pos >= len(body): raise ValueError("short flag")
        flag = body[pos]; pos += 1
    if pos != len(body): raise ValueError("trailing bytes")
    return tuple(fields), flag


def encode_c04(sex, hair, index):
    # 0..255 is wire representability ONLY; original server enum limits unknown.
    if any(type(x) is not int or not 0 <= x <= 255 for x in (sex, hair)):
        raise ValueError("invalid u8")
    return bytes([sex, hair]) + rgb(index)


def client_first_gate(region, narrow_encoded):
    # 0x4985DC/E8 => 0x91FED0=6 or 12; 0x4B1A30 skips region0.
    return region == 0 or len(narrow_encoded) >= 12


class DesignedDB:
    """Illustrative one-character/account policy, NOT native server evidence."""
    def __init__(self):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        self.db.executescript("""
        CREATE TABLE account(id TEXT PRIMARY KEY);
        CREATE TABLE character(owner TEXT UNIQUE, name TEXT UNIQUE,
           intent TEXT NOT NULL, appearance BLOB NOT NULL);
        """)
    def create(self, owner, verified, pending_owner, name, intent, appearance):
        if not verified or owner != verified or pending_owner != owner:
            return False
        if not intent or not name or len(appearance) != 5:
            return False
        if not self.db.execute("SELECT 1 FROM account WHERE id=?", (owner,)).fetchone():
            return False
        prior = self.db.execute("SELECT name,intent,appearance FROM character WHERE owner=?", (owner,)).fetchone()
        if prior:
            return prior == (name, intent, appearance)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute("INSERT INTO character VALUES(?,?,?,?)", (owner,name,intent,appearance))
            self.db.execute("COMMIT")
            return True
        except sqlite3.IntegrityError:
            self.db.execute("ROLLBACK")
            return False


class TestA003(unittest.TestCase):
    def test_region_codecs(self):
        for region in range(5):
            vals = (b"A", b"B", b"C", b"D") if region in (2,3,4) else (b"A", b"B", b"C")
            body = encode_c02(region, vals, 3)
            self.assertEqual(decode_c02(region, body), (vals, 3 if len(vals)==4 else None))
            for bad in (body[:-1], body + b"\x00"):
                with self.assertRaises(ValueError): decode_c02(region, bad)

    def test_cp950_byte_count_and_ui_gate(self):
        s = "測試A".encode("cp950")
        self.assertEqual(len(s), 5)
        self.assertTrue(encode_c02(0, (s,b"p",b"x")).startswith(b"\x05"+s))
        self.assertTrue(client_first_gate(0,b""))
        self.assertFalse(client_first_gate(1,b"x"*11))
        self.assertTrue(client_first_gate(4,b"x"*12))

    def test_ten_colors_and_c04(self):
        self.assertEqual(len(COLORS), 10)
        self.assertEqual(rgb(0).hex(), "915a28")
        self.assertEqual(rgb(9).hex(), "5a5a5a")
        self.assertEqual(encode_c04(1,2,1).hex(), "0102ff6464")
        for bad in (-1, 10, 255):
            with self.assertRaises(ValueError): rgb(bad)

    def test_owner_and_uniqueness(self):
        d = DesignedDB(); d.db.executemany("INSERT INTO account VALUES(?)", [("alice",),("bob",)])
        a = encode_c04(1,2,1)
        self.assertFalse(d.create("alice",None,"alice","name","i",a))
        self.assertFalse(d.create("alice","bob","bob","name","i",a))
        self.assertTrue(d.create("alice","alice","alice","name","i",a))
        self.assertTrue(d.create("alice","alice","alice","name","i",a))
        self.assertFalse(d.create("alice","alice","alice","next","j",a))
        self.assertFalse(d.create("bob","bob","bob","name","b",a))
        self.assertEqual(d.db.execute("SELECT COUNT(*) FROM character").fetchone()[0],1)

    def test_late_c15_does_not_delete_committed(self):
        d=DesignedDB();d.db.execute("INSERT INTO account VALUES('alice')")
        self.assertTrue(d.create("alice","alice","alice","name","i",encode_c04(0,0,0)))
        # C15's zero-byte body cannot identify a historical committed create intent.
        self.assertEqual(d.db.execute("SELECT COUNT(*) FROM character").fetchone()[0],1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
