#!/usr/bin/env python3
"""Validate separation of A research handoff, DEV implementation and Client CT gates."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise SystemExit("INVALID WORK GATE: " + message)

a = read("03-analysis-requests/requests.json")["requests"]
w = read("02-server-planning/work-items.json")["work_items"]
ct = read("05-conformance/vectors.json")["vectors"]
r = read("01-server-requirements/requirements.json")["requirements"]
sid = {x["id"] for x in read("04-analysis-integration/scenarios.json")["scenarios"]}
aid = {x["id"] for x in a}
rid = {x["id"] for x in r}
ctid = {x["id"] for x in ct}
wid = {x["id"] for x in w}
require(len(aid) == len(a), "duplicate A IDs")
require(len(wid) == len(w), "duplicate ONB IDs")
for item in a:
    key = item["id"]
    require(item.get("completion_policy") == "A-EVIDENCE-HANDOFF-v1", key + " must adopt evidence-first handoff")
    require(item.get("handoff_status") in {"not-started", "partial", "ready", "blocked"}, key + " invalid handoff")
    require(item.get("native_client_validation") in {"not-run", "pending", "passed", "failed"}, key + " invalid client validation")
    require(item.get("status") in {"open", "scoped", "analyzing", "review", "integrated", "blocked"}, key + " invalid research status")
    require(bool(item.get("method") and item.get("deliverable")), key + " missing method/deliverable")
    require(all(p in rid for p in item.get("requirements", [])), key + " has unknown requirement")
    require(all(dep in aid and dep != key for dep in item.get("dependencies", [])), key + " has invalid A dependency")
    if item["status"] == "integrated":
        require(item["handoff_status"] in {"ready", "partial"}, key + " integrated but not reviewed for handoff")
        require(bool(item.get("evidence_ids")), key + " integrated with no evidence IDs")
    if item["status"] == "blocked":
        require(item["handoff_status"] in {"blocked", "partial"}, key + " blocked state mismatch")
for item in w:
    key = item["id"]
    require(item.get("completion_policy") == "DEV-CT-SPLIT-v1", key + " conflates DEV with Client CT")
    require(item.get("client_acceptance_owner") == "DEV/CT", key + " invalid validation owner")
    require(item.get("implementation_status") is not None, key + " missing implementation status")
    require(item.get("client_acceptance") is not None, key + " missing CT status")
    require(all(p in aid for p in item.get("analysis_requests", [])), key + " unknown A")
    require(all(p in rid for p in item.get("requirements", [])), key + " unknown R")
    require(all(p in sid for p in item.get("scenarios", [])), key + " unknown SCN")
    require(all(p in ctid for p in item.get("conformance", [])), key + " unknown CT")
    require(all(p in wid and p != key for p in item.get("depends_on", [])), key + " invalid ONB dependency")

def has_cycle(nodes, edges):
    gray, black = set(), set()
    def walk(node):
        if node in gray: return True
        if node in black: return False
        gray.add(node)
        if any(walk(dep) for dep in edges[node]): return True
        gray.remove(node)
        black.add(node)
        return False
    return any(walk(n) for n in nodes if n not in black)

require(not has_cycle(aid, {x["id"]: x.get("dependencies", []) for x in a}), "A→A dependency cycle")
require(not has_cycle(wid, {x["id"]: x.get("depends_on", []) for x in w}), "ONB→ONB dependency cycle")
print(f"Phase gates valid: {len(a)} A tasks, {len(w)} DEV work items, {len(ct)} CT vectors; native Client tests remain independent.")


# v2 work ownership and Client I/O handoff checks
TRACK_REQUIRED = {
    "client-io": ["trigger", "client_sends", "client_receives", "client_reaction", "evidence", "unknowns"],
    "resource-analysis": ["format", "provenance", "client_usage", "unknowns"],
    "server-design": ["policy", "invariants", "failure_modes", "validation"],
}
require((ROOT / "00-governance/task-ownership-and-client-io.md").is_file(), "missing work ownership standard")
require((ROOT / "03-analysis-requests/client-io-handoff-standard.md").is_file(), "missing Client I/O standard")
for item in a:
    key = item["id"]
    track = item.get("handoff_track")
    require(track in TRACK_REQUIRED, key + " missing/invalid handoff_track")
    require(item.get("handoff_requirements") == TRACK_REQUIRED[track], key + " missing required "+str(track)+" handoff fields")
    document = item.get("handoff_document")
    require(isinstance(document, str) and document.endswith(".md") and (ROOT / document).is_file(), key + " missing handoff document")
    require(bool(item.get("client_server_boundary")), key + " missing Client/Server responsibility gate")
require({x["id"] for x in a if x["handoff_track"] == "server-design"} == {"A-016", "A-017", "A-018"}, "Server-designed analyses must remain explicitly separate")
require({x["id"] for x in a if x["handoff_track"] == "resource-analysis"} == {"A-015"}, "A-015 must remain resource research")
print("Client I/O boundary valid: every A-XX has an explicit research track, deliverable schema and owner.")


# v2 Server Client I/O flow matrix: existence and grounded cross-references
MATRIX = read("02-server-planning/client-io-flow-matrix.json")
packet_ids = {x["id"] for x in read("04-analysis-integration/packets.json")["packets"]}
flows = MATRIX["flows"]
flow_ids = {f["id"] for f in flows}
require(len(flows) == len(flow_ids) and len(flows) >= 6, "invalid or missing Client I/O flow identities")
for f in flows:
    key = f["id"]
    require(f["native_client_validation"] in {"not-run", "pending", "passed", "failed"}, key + " invalid Client validation")
    require(bool(f["client_trigger"] and f["client_reaction"] and f["server_decisions"]), key + " missing Client event or Server ownership")
    require(all(p in packet_ids for p in f["client_send"] + f["server_to_client"]), key + " references unknown packet")
    require(all(i in aid for i in f["evidence"]), key + " references unknown A")
    require(all(i in sid for i in f["scenarios"]), key + " references unknown scenario")
    require(all(i in ctid for i in f["tests"]), key + " references unknown CT")
    require(all(i in wid for i in f["work_items"]), key + " references unknown ONB")
    require(bool(f["unknowns"]), key + " must document remaining unknowns")
for item in w:
    key = item["id"]
    require(item.get("client_contract_source") == "02-server-planning/client-io-flow-matrix.json", key + " missing Client IO matrix")
    linked = item.get("client_io_flows", [])
    require(bool(linked) and all(x in flow_ids for x in linked), key + " unknown Client I/O flow")
    require(all(key in next(f for f in flows if f["id"] == x)["work_items"] for x in linked), key + " mismatched ONB/flow link")
    require(bool(item.get("authority_policy_source") and item.get("native_ct_gate")), key + " missing Server authority or Client CT gate")
print("Client I/O flows valid: %d flows; all packet, A, SCN, CT and ONB links resolved." % len(flows))
