#!/usr/bin/env python3
"""A-016: SQLite synthetic crash/replay/ledger contract. Not original Server."""
import hashlib
import os
import sqlite3
import tempfile


def digest(b):
    return hashlib.sha256(b).hexdigest()


class Server:
    def __init__(self, file):
        self.db = sqlite3.connect(file, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS account(id TEXT PRIMARY KEY, generation INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS char(account TEXT PRIMARY KEY, intent TEXT NOT NULL,
            body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS grant(token TEXT PRIMARY KEY, account TEXT NOT NULL,
            gen INTEGER NOT NULL, consumed INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, payload TEXT);
        CREATE TABLE IF NOT EXISTS wallet(id TEXT PRIMARY KEY, amount INTEGER NOT NULL CHECK(amount>=0));
        CREATE TABLE IF NOT EXISTS trade(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS reward(char TEXT, objective TEXT,
            PRIMARY KEY(char,objective));
        """)
        self.loading = {}
        self.movement = {}

    def account(self, name):
        self.db.execute("INSERT OR IGNORE INTO account(id) VALUES(?)", (name,))

    def create(self, owner, authorized, intent, body):
        if not authorized or len(body) != 5:
            return False
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            old = self.db.execute("SELECT intent,body FROM char WHERE account=?",
                                  (owner,)).fetchone()
            if old:
                return old == (intent, digest(body))
            if not self.db.execute("SELECT 1 FROM account WHERE id=?", (owner,)).fetchone():
                return False
            self.db.execute("INSERT INTO char VALUES(?,?,?)", (owner, intent, digest(body)))
            self.db.execute("INSERT INTO outbox VALUES(?,?)", ("create:"+owner, "S02 success after commit"))
        return True

    def issue(self, owner, token):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute("UPDATE account SET generation=generation+1 WHERE id=?", (owner,))
            gen = self.db.execute("SELECT generation FROM account WHERE id=?",
                                  (owner,)).fetchone()[0]
            self.db.execute("INSERT INTO grant VALUES(?,?,?,0)", (digest(token), owner, gen))
        return gen

    def consume(self, owner, token, gen):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            cur = self.db.execute("""
                UPDATE grant SET consumed=1 WHERE token=? AND account=? AND gen=?
                AND consumed=0 AND EXISTS(SELECT 1 FROM account
                WHERE id=? AND generation=?)""", (digest(token), owner, gen, owner, gen))
        return cur.rowcount == 1

    def load(self, socket, epoch, pair, ambiguous=False):
        self.loading[socket] = (epoch, pair, ambiguous)

    def crc(self, socket, epoch, pair):
        # epoch is internal, NOT in the original two-u16 C35 body.
        current = self.loading.get(socket)
        if current != (epoch, pair, False):
            return False
        del self.loading[socket]
        return True

    def move(self, session, gen, seq, direction, gait):
        key = (session, gen)
        if not 0 <= seq < 128:
            return False
        state = self.movement.setdefault(key, {"next": seq, "last": None})
        body = (seq, direction, gait)
        if body == state["last"]:
            return "cached-ack"
        if seq != state["next"]:
            return False
        state["last"] = body
        state["next"] = (seq + 1) & 127
        return "new-ack"

    def transfer(self, key, src, dst, amount):
        if src == dst or amount <= 0:
            return False
        hashval = digest(f"{src}|{dst}|{amount}".encode())
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            old = self.db.execute("SELECT payload FROM trade WHERE id=?", (key,)).fetchone()
            if old:
                return old[0] == hashval
            out = self.db.execute("UPDATE wallet SET amount=amount-? WHERE id=? AND amount>=?",
                                  (amount, src, amount))
            if out.rowcount != 1:
                return False
            if self.db.execute("UPDATE wallet SET amount=amount+? WHERE id=?",
                               (amount, dst)).rowcount != 1:
                raise ValueError("bad destination")
            self.db.execute("INSERT INTO trade VALUES(?,?)", (key, hashval))
            self.db.execute("INSERT INTO outbox VALUES(?,?)", ("trade:"+key, "notify once"))
        return True

    def award(self, character, objective):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            return self.db.execute("INSERT OR IGNORE INTO reward VALUES(?,?)",
                                   (character, objective)).rowcount == 1

    def close(self):
        self.db.close()


def test():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "a016.sqlite")
        s = Server(path)
        s.account("alice")
        body = bytes.fromhex("0102112233")
        assert not s.create("alice", False, "c1", body)
        assert s.create("alice", True, "c1", body)
        assert s.create("alice", True, "c1", body)
        assert not s.create("alice", True, "c2", body)
        assert not s.create("alice", True, "c1", bytes.fromhex("0103112233"))
        gen = s.issue("alice", b"opaque")
        assert s.consume("alice", b"opaque", gen)
        assert not s.consume("alice", b"opaque", gen)
        s.load("socket", 1, (0x1234, 0xABCD))
        assert not s.crc("socket", 2, (0x1234, 0xABCD))
        assert not s.crc("socket", 1, (0x1234, 0))
        assert s.crc("socket", 1, (0x1234, 0xABCD))
        assert not s.crc("socket", 1, (0x1234, 0xABCD))
        assert s.move("socket", gen, 127, 1, 1) == "new-ack"
        assert s.move("socket", gen, 127, 1, 1) == "cached-ack"
        assert s.move("socket", gen, 0, 1, 1) == "new-ack"
        s.db.execute("INSERT INTO wallet VALUES('a',100)")
        s.db.execute("INSERT INTO wallet VALUES('b',20)")
        assert s.transfer("t1", "a", "b", 30)
        assert s.transfer("t1", "a", "b", 30)
        assert not s.transfer("t1", "a", "b", 50)
        assert s.award("alice", "one")
        assert not s.award("alice", "one")
        s.close()  # crash/reopen: volatile loading/movement lost
        s = Server(path)
        assert s.db.execute("SELECT count(*) FROM char").fetchone()[0] == 1
        assert s.db.execute("SELECT payload FROM outbox WHERE id='create:alice'").fetchone()
        assert s.db.execute("SELECT amount FROM wallet WHERE id='a'").fetchone()[0] == 70
        assert s.db.execute("SELECT amount FROM wallet WHERE id='b'").fetchone()[0] == 50
        assert not s.award("alice", "one")
        assert not s.consume("alice", b"opaque", gen)
        assert not s.crc("socket", 1, (0x1234, 0xABCD))
        s.load("new_socket", 2, (0x1234, 0xABCD), ambiguous=True)
        assert not s.crc("new_socket", 2, (0x1234, 0xABCD))
        s.close()
    print("PASS A-016 synthetic SQLite crash/reopen, outbox, grant, C35, C33, trade/reward once")


if __name__ == "__main__":
    test()
