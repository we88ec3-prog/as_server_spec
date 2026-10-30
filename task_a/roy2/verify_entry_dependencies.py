#!/usr/bin/env python3
"""Verify Born's direct paper-dialog dependency without running game scripts."""
import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

from verify_born import DEFAULT_SHA, inspect

PAPER_SHA = "5b86a4b18075e8c457b36f0d6f6f4b6ad1e86c6e4b0ac9d5fb5e28795b070054"


def unpack(path, expected_sha):
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != expected_sha:
        raise ValueError(path.name + ": resource version mismatch")
    decoder = zlib.decompressobj()
    payload = decoder.decompress(blob) + decoder.flush()
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise ValueError(path.name + ": incomplete or trailing zlib stream")
    if payload[:4] != b"\x00\x01\x00\x00" or len(payload) < 6:
        raise ValueError(path.name + ": invalid wrapper")
    units = int.from_bytes(payload[4:6], "big")
    if len(payload) != 6 + 2 * units:
        raise ValueError(path.name + ": UTF-16 length mismatch")
    root = ET.fromstring(payload[6:].decode("utf-16le", errors="strict"))
    if root.tag != "script":
        raise ValueError(path.name + ": invalid XML root")
    return root, {"filename": path.name, "raw_size": len(blob),
                  "raw_sha256": expected_sha, "unpacked_size": len(payload),
                  "unpacked_sha256": hashlib.sha256(payload).hexdigest(),
                  "utf16_code_units": units}


def verify(directory):
    born, born_meta = unpack(directory / "Born.dat", DEFAULT_SHA)
    inspect(directory / "Born.dat")
    paper, paper_meta = unpack(directory / "PaperDialog.dat", PAPER_SHA)
    functions = {f.get("name"): f for f in paper.findall("function")}
    if len(paper) != 3 or set(functions) != {
        "PaperDialog_Create", "ShowIndexedHelp", "PaperDialogProc"
    }:
        raise ValueError("unexpected PaperDialog function set")
    create = functions["PaperDialog_Create"].text or ""
    show = functions["ShowIndexedHelp"].text or ""
    click = functions["PaperDialogProc"].text or ""
    checks = {
        "born_single_page": (born.find("function").text or "").count("page.Insert(msg)") == 1,
        "callback_registered": 'dialog.onControlClick = "PaperDialogProc"' in create,
        "initial_page_zero": "ShowIndexedHelp(dialog, 0)" in create,
        "cancel_and_default_ok": all('dialog.' + key + '\t= "OK"' in create
                                     for key in ("cancelControl", "defaultControl")),
        "prev_hidden_at_zero": "if (index != 0)" in show and "prev.isVisible = false" in show,
        "next_hidden_at_last": "if (index != (helpArray.count - 1))" in show and "next.isVisible\t= false" in show,
        "close_disposes": all(s in click for s in ('case "OK"', "dialog.Dispose()", "client.Dispose()")),
        "frame_dependency": 'pane.SetImage("Basic.dat", "AlertFrame.ypf", 0)' in create,
        "no_explicit_quest_or_reply": not any(s in "\n".join(f.text or "" for f in paper)
            for s in ("SendReply", "SetQuest", "SetFlag", "SpawnNpc", "CreateNPC")),
    }
    if not all(checks.values()):
        raise ValueError("dependency checks failed: " + repr(checks))
    return {"result": "PASS", "evidence_kind": "observed-static-resource",
            "resources": [born_meta, paper_meta], "checks": checks,
            "other_dependencies": ["Basic.dat/AlertFrame.ypf", "image button objects 11/12/13"],
            "other_dependencies_verified": False, "auto_trigger": "unknown",
            "resource_client_version_binding": "unverified", "native_client_validation": "not-run"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script_directory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.script_directory), ensure_ascii=False, indent=2))
    except (OSError, ValueError, ET.ParseError, zlib.error) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
