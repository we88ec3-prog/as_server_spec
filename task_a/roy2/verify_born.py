#!/usr/bin/env python3
"""Offline Born.dat validator; never commits or executes original game content."""
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

DEFAULT_SHA = "992e6d78819538b9fd924bc2bf6a2ad2f2ced9eeaff4baa57c16140208aacf98"

def inspect(path):
    blob = path.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    payload = zlib.decompress(blob)
    if len(payload) < 6 or payload[:4] != b"\x00\x01\x00\x00":
        raise ValueError("invalid Script header")
    n = int.from_bytes(payload[4:6], "big")
    if len(payload) != 6 + n * 2:
        raise ValueError("UTF-16 length mismatch")
    root = ET.fromstring(payload[6:].decode("utf-16le", errors="strict"))
    funcs = root.findall("function")
    if root.tag != "script" or len(funcs) != 1 or funcs[0].get("name") != "Main":
        raise ValueError("expected exactly one Main function")
    body = funcs[0].text or ""
    # String literals can include text resembling function calls; mask them.
    code, quoted, escaped = [], False, False
    for ch in body:
        if quoted:
            code.append(" ")
            if escaped: escaped = False
            elif ch == "\\": escaped = True
            elif ch == '"': quoted = False
        elif ch == '"':
            code.append(" ")
            quoted = True
        else:
            code.append(ch)
    if quoted: raise ValueError("unterminated script string")
    calls = re.findall(r"(?<![\w.])([\w]+(?:\.[\w]+)?)\s*\(", "".join(code))
    if calls != ["client.CreateArray", "page.Insert", "PaperDialog_Create"]:
        raise ValueError("unexpected Main calls: " + repr(calls))
    if not re.search(r"\(\s*31\s*,\s*29\s*\)", body):
        raise ValueError("guidance point missing")
    if "招募員" not in body or "滑鼠" not in body:
        raise ValueError("recruiter instruction missing")
    if re.search(r"\b(?:SendReply|SetQuest|SetFlag|SpawnNpc|CreateNPC)\s*\(", "".join(code), re.I):
        raise ValueError("unexpected quest/spawn call")
    return {"result":"PASS","raw_sha256":digest,"inflated_size":len(payload),
            "utf16_code_units":n,"entry":"Main","calls":calls,
            "target":[31,29],"npc_id":"unknown","auto_trigger":"unknown"}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path", type=Path)
    p.add_argument("--sha", default=DEFAULT_SHA)
    a = p.parse_args()
    try:
        result = inspect(a.path)
        if a.sha and a.sha.lower() != result["raw_sha256"]:
            raise ValueError("wrong Born.dat SHA256 (different resource version)")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, UnicodeError, ET.ParseError, zlib.error) as e:
        print("FAIL: " + str(e), file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
