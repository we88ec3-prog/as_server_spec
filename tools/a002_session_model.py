#!/usr/bin/env python3
"""A-002 synthetic Server policy model, NOT a recovered original-server algorithm.

Run: python3 tools/a002_session_model.py
"""
from dataclasses import dataclass


@dataclass
class Grant:
    account: str
    character: str
    generation: int
    deadline: int
    consumed: bool = False


class SessionModel:
    """Designed single-active-world policy: a newly authenticated login wins."""

    def __init__(self, credentials, ttl=60):
        self.credentials = dict(credentials)
        self.generation = {k: 0 for k in credentials}
        self.grants = {}
        self.active_world = {}
        self.now = 0
        self.next_token = 0
        self.ttl = ttl

    def login(self, account, password, character):
        # A failed login cannot revoke the older session.
        if self.credentials.get(account) != password:
            return None
        self.generation[account] += 1
        gen = self.generation[account]
        self.active_world.pop(account, None)
        self.next_token += 1
        token = f"synthetic-token-{self.next_token}"
        self.grants[token] = Grant(account, character, gen, self.now + self.ttl)
        return token

    def close_login_socket(self, account):
        # Transfer switches TCP sockets: the grant remains usable until expiry.
        pass

    def enter_world(self, token, account, character):
        grant = self.grants.get(token)
        if (not grant or grant.consumed or self.now >= grant.deadline
                or grant.account != account or grant.character != character
                or self.generation.get(account) != grant.generation):
            return False
        grant.consumed = True
        self.active_world[account] = (character, grant.generation)
        return True

    def action(self, account, generation):
        return (self.active_world.get(account) is not None
                and self.active_world[account][1] == generation
                and self.generation[account] == generation)

    def disconnect_world(self, account, generation):
        # Old socket close must never remove the new generation.
        if self.active_world.get(account, (None, None))[1] == generation:
            del self.active_world[account]

    def crash(self):
        # Fail closed for volatile grants and connections. Persistent characters unaffected.
        self.grants.clear()
        self.active_world.clear()


def test():
    m = SessionModel({"alice": "secret", "bob": "secret2"})
    assert m.login("alice", "bad", "char-a") is None
    a1 = m.login("alice", "secret", "char-a")
    assert a1 and m.generation["alice"] == 1
    m.close_login_socket("alice")
    assert not m.enter_world(a1, "bob", "char-a")
    assert not m.enter_world(a1, "alice", "wrong-character")
    assert m.enter_world(a1, "alice", "char-a")
    assert not m.enter_world(a1, "alice", "char-a")
    assert m.action("alice", 1)
    assert m.login("alice", "bad", "char-a") is None and m.action("alice", 1)
    a2 = m.login("alice", "secret", "char-a")
    assert not m.action("alice", 1)
    assert not m.enter_world(a1, "alice", "char-a")
    assert m.enter_world(a2, "alice", "char-a")
    m.disconnect_world("alice", 1)
    assert m.action("alice", 2)  # old connection cannot remove new world
    a3 = m.login("alice", "secret", "char-a")
    m.now += m.ttl
    assert not m.enter_world(a3, "alice", "char-a")  # expiry boundary
    a4 = m.login("alice", "secret", "char-a")
    m.crash()
    assert not m.enter_world(a4, "alice", "char-a")
    assert m.login("bob", "secret2", "char-b") is not None
    print("PASS A-002 designed model: bad-password, one-shot, cross-owner, generation,"
          " stale-close, handoff-disconnect, expiry, crash")


if __name__ == "__main__":
    test()
