#!/usr/bin/env python3
"""A-017 synthetic management contract tests; not original Asgard admin protocol."""
import hashlib
import json
import sqlite3
import unittest

PERMISSIONS = {
    "observer": {"ops.read"},
    "support": {"ops.read", "account.suspend", "account.unsuspend"},
    "game_master": {"ops.read", "character.teleport", "character.adjust", "item.grant"},
    "admin": {"ops.read", "account.provision", "account.suspend", "account.unsuspend",
              "character.teleport", "character.adjust", "item.grant"},
}
SAFE = {"target_id", "map_id", "reason_code", "duration_days", "delta", "item_id", "quantity"}

class Management:
    def __init__(self):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        self.db.executescript("""
            CREATE TABLE accounts(id TEXT PRIMARY KEY, suspended_until TEXT, status TEXT DEFAULT 'active', version INTEGER DEFAULT 0);
            CREATE TABLE chars(id TEXT PRIMARY KEY, map_id INTEGER NOT NULL, level INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE grants(id TEXT PRIMARY KEY, char_id TEXT, item_id INTEGER, quantity INTEGER);
            CREATE TABLE intents(actor TEXT, key TEXT, operation TEXT, digest TEXT, result TEXT, PRIMARY KEY(actor,key));
            CREATE TABLE audit(seq INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT, operation TEXT, target_id TEXT, request_id TEXT, decision TEXT, reason TEXT, safe_json TEXT);
        """)

    def dispatch(self, *, actor, role, action, request_id, params, source="127.0.0.1", authenticated=True):
        # Always store an allowlisted view, including when an operation is denied.
        safe = {k: params[k] for k in SAFE if k in params}
        safe_json = json.dumps(safe, sort_keys=True, ensure_ascii=False)
        target = str(params.get("target_id", ""))
        def log(decision, reason):
            self.db.execute("INSERT INTO audit(actor,operation,target_id,request_id,decision,reason,safe_json) VALUES(?,?,?,?,?,?,?)",
                            (actor, action, target, request_id, decision, reason, safe_json))
        if not authenticated or not actor:
            log("denied", "unauthenticated")
            return "denied"
        if action not in PERMISSIONS.get(role, ()):
            log("denied", "forbidden")
            return "denied"
        if not request_id or not source:
            log("denied", "bad_request")
            return "denied"
        payload_digest = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()
        existing = self.db.execute("SELECT operation,digest,result FROM intents WHERE actor=? AND key=?",
                                   (actor, request_id)).fetchone()
        if existing:
            result = existing[2] if existing[:2] == (action, payload_digest) else "conflict"
            log("replayed" if result != "conflict" else "denied", result)
            return result
        if not params.get("reason_code"):
            log("denied", "reason_required")
            return "denied"
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if action == "account.provision":
                cur = self.db.execute("INSERT OR IGNORE INTO accounts(id) VALUES(?)", (target,))
                result = "applied" if cur.rowcount else "conflict"
            elif action == "account.suspend":
                days = params.get("duration_days")
                if days != "permanent" and (not isinstance(days, int) or not 1 <= days <= 3650):
                    result = "invalid_duration"
                else:
                    cur = self.db.execute("UPDATE accounts SET status='suspended',suspended_until=?,version=version+1 WHERE id=?",
                                          (str(days), target))
                    result = "applied" if cur.rowcount else "not_found"
            elif action == "account.unsuspend":
                cur = self.db.execute("UPDATE accounts SET status='active',suspended_until=NULL,version=version+1 WHERE id=?", (target,))
                result = "applied" if cur.rowcount else "not_found"
            elif action == "character.teleport":
                dest = params.get("map_id")
                if not isinstance(dest, int) or dest < 0: result = "invalid_map"
                else:
                    cur = self.db.execute("UPDATE chars SET map_id=?,version=version+1 WHERE id=?", (dest, target))
                    result = "applied" if cur.rowcount else "not_found"
            elif action == "character.adjust":
                delta = params.get("delta")
                if not isinstance(delta, int) or not -10 <= delta <= 10: result = "invalid_adjustment"
                else:
                    cur = self.db.execute("UPDATE chars SET level=level+?,version=version+1 WHERE id=? AND level+? BETWEEN 1 AND 99", (delta, target, delta))
                    result = "applied" if cur.rowcount else "invalid_or_not_found"
            elif action == "item.grant":
                item = params.get("item_id"); qty = params.get("quantity")
                if not isinstance(item, int) or item < 0 or not isinstance(qty, int) or not 1 <= qty <= 99: result = "invalid_item"
                elif not self.db.execute("SELECT 1 FROM chars WHERE id=?", (target,)).fetchone(): result = "not_found"
                else:
                    self.db.execute("INSERT INTO grants VALUES(?,?,?,?)", (actor+":"+request_id,target,item,qty))
                    result = "applied"
            else: result = "not_implemented"
            self.db.execute("INSERT INTO intents VALUES(?,?,?,?,?)", (actor,request_id,action,payload_digest,result))
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            log("error", "domain_exception")
            raise
        log("allowed" if result == "applied" else "denied", result)
        return result

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.m = Management()
        self.m.db.execute("INSERT INTO accounts(id) VALUES('u')")
        self.m.db.execute("INSERT INTO chars(id,map_id,level) VALUES('c',1,10)")
    def call(self, role, action, key, **params):
        return self.m.dispatch(actor="a",role=role,action=action,request_id=key,params={"reason_code":"support-case", **params})
    def test_permissions_and_identity(self):
        self.assertEqual(self.call("observer","item.grant","a",target_id="c",item_id=1,quantity=3),"denied")
        self.assertEqual(self.m.dispatch(actor="",role="admin",action="item.grant",request_id="a",params={"target_id":"c"}),"denied")
        self.assertEqual(self.m.db.execute("SELECT count(*) FROM grants").fetchone()[0],0)
    def test_one_shot_item_grant(self):
        d=dict(target_id="c",item_id=44,quantity=3)
        self.assertEqual(self.call("game_master","item.grant","issue7",**d),"applied")
        self.assertEqual(self.call("game_master","item.grant","issue7",**d),"applied")
        self.assertEqual(self.call("game_master","item.grant","issue7",target_id="c",item_id=44,quantity=8),"conflict")
        self.assertEqual(self.m.db.execute("SELECT count(*) FROM grants").fetchone()[0],1)
    def test_ban_and_unban(self):
        self.assertEqual(self.call("support","account.suspend","b1",target_id="u",duration_days="permanent"),"applied")
        self.assertEqual(self.m.db.execute("SELECT status FROM accounts WHERE id='u'").fetchone()[0],"suspended")
        self.assertEqual(self.call("support","account.unsuspend","b2",target_id="u"),"applied")
    def test_teleport_and_adjustment(self):
        self.assertEqual(self.call("game_master","character.teleport","t1",target_id="c",map_id=2),"applied")
        self.assertEqual(self.call("game_master","character.adjust","l1",target_id="c",delta=3),"applied")
        self.assertEqual(self.m.db.execute("SELECT map_id,level FROM chars WHERE id='c'").fetchone(),(2,13))
    def test_no_sensitive_body_in_audit(self):
        self.m.dispatch(actor="a",role="support",action="account.suspend",request_id="redact",params={"target_id":"u","reason_code":"x","duration_days":2,"password":"SECRET","transfer_token":"SECRET"})
        a="".join(str(r) for r in self.m.db.execute("SELECT * FROM audit"))
        self.assertNotIn("SECRET", a)
        self.assertNotIn("password", a)
        self.assertNotIn("transfer_token", a)

if __name__ == "__main__":
    unittest.main(verbosity=1)
