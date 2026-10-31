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

# Onboarding next iteration safe/native activation checks
ready = read("02-server-planning/onboarding-readiness-gates.json")
gates = ready.get("gates", [])
gate_ids = {g["id"] for g in gates}
require(ready.get("unmodified_client_required") is True, "original Asgard Client must remain unmodified")
require(ready.get("native_client_validation") == "not-run", "native Client not actually tested")
require(len(gates) == len(gate_ids) and len(gates) >= 8, "missing or duplicate onboarding gates")
require({"SAFE-01", "SAFE-02", "SAFE-03", "SAFE-04", "WIRE-01", "WIRE-02", "WORLD-01", "SCRIPT-01"} <= gate_ids,
        "missing required next iteration gate")
for gate in gates:
    key = gate["id"]
    require(gate["mode"] in {"develop-now", "needs-client-evidence", "partial-client-evidence"},
            key + " has invalid readiness")
    require(bool(gate.get("rule")), key + " missing rule")
    require(all(id in aid for id in gate["analysis"]), key + " bad A reference")
    require(all(id in ctid for id in gate["tests"]), key + " bad CT reference")
require(next(g for g in gates if g["id"] == "WIRE-01")["mode"] == "needs-client-evidence",
        "must not enable unproven C03 no-character -> NewUser UI")
for w_item in w:
    require(w_item.get("readiness_gate_source") == "02-server-planning/onboarding-readiness-gates.json",
            w_item["id"] + " missing next iteration gate source")
for scn in read("04-analysis-integration/scenarios.json")["scenarios"]:
    if scn["id"] in {"SCN-007", "SCN-008"}:
        require(scn.get("native_ui_proof_gate") == "CT-054",
                scn["id"] + " must retain native UI proof gate")
for req_item in a:
    if req_item["id"] in {"A-020", "A-022", "A-024", "A-027", "A-028"}:
        require(req_item.get("next_client_io_handoff") == "03-analysis-requests/next-client-io-evidence.md",
                req_item["id"] + " missing targeted Client I/O handoff")
test = next((v for v in ct if v["id"] == "CT-054"), None)
require(test is not None and test.get("status") == "planned" and
        test.get("native_client_validation") == "not-run",
        "CT-054 cannot be marked passed without native Client evidence")
for tag in ("R-025,", "R-026,"):
    rows = [line for line in (ROOT / "00-governance/traceability.csv").read_text(encoding="utf-8").splitlines()
            if line.startswith(tag)]
    require(len(rows) == 1 and "CT-054" in rows[0], tag + " missing traceability CT-054")
print("Onboarding readiness gates valid: %d gates, CT-054 planned, Client original." % len(gates))

# ADR-007: user-approved multiplayer map must be distinct from old per-character DEV-070 runtime
shared = read("02-server-planning/shared-map-multiplayer-contract.json")
require(shared.get("decision") == "user-approved-multiplayer-shared-map", "shared-map decision missing")
require(shared.get("native_client_modified") is False, "original Client must remain unchanged")
require(shared.get("native_client_validation") == "not-run", "shared-map native testing cannot be presumed")
require(shared.get("development_status") == "design-approved-refactor-required", "shared-map refactor must not appear implemented")
require(shared.get("map_instance_key") == ["world_id", "map_ref"], "shared map must not use per-character instance key")
require(shared.get("same_map_content_revision_must_match") is True, "shared-map version safety missing")
for ref in shared["analysis_requests"]:
    require(ref in aid, "shared-map references unknown A " + ref)
for ref in shared["work_items"]:
    require(ref in wid, "shared-map references unknown ONB " + ref)
for ref in shared["conformance"]:
    require(ref in ctid, "shared-map references unknown CT " + ref)
test = next((v for v in ct if v["id"] == "CT-055"), None)
require(test is not None and test.get("status") == "planned" and
        test.get("native_client_validation") == "not-run", "CT-055 must stay planned until real client tests")
scene = next((x for x in w if x["id"] == "ONB-05"), None)
require(scene is not None and scene.get("shared_map_contract") ==
        "02-server-planning/shared-map-multiplayer-contract.json", "ONB-05 missing shared-map decision")
require("CT-055" in scene["conformance"], "ONB-05 must track multiplayer acceptance")
for id in ("SCN-005", "SCN-011", "SCN-012"):
    scenario = next((v for v in read("04-analysis-integration/scenarios.json")["scenarios"]
                     if v["id"] == id), None)
    require(scenario is not None and scenario.get("shared_map_contract") ==
            "02-server-planning/shared-map-multiplayer-contract.md", id + " missing ADR-007")
print("Shared-map ADR-007 valid: public multiplayer scene planned, native CT-055 not-run.")

# Merge 2026-10-31: evidence lineage, CT remapping and status boundaries
EVIDENCE_IDS = {v["evidence_id"] for v in read("04-analysis-integration/evidence-index.json")["evidence"]}
require(len(EVIDENCE_IDS) == len(read("04-analysis-integration/evidence-index.json")["evidence"]),
        "duplicate evidence ids")
for x in a:
    if x["status"] == "integrated":
        require(all(e in EVIDENCE_IDS for e in x.get("evidence_ids", [])),
                x["id"] + " has evidence ID absent from shared index")
for packet in read("04-analysis-integration/packets.json")["packets"]:
    require(all(v in packet_ids for v in packet.get("related_packets", [])),
            packet["id"] + " related_packets has unknown id")
remap = read("05-conformance/ct-id-remap-roy1-roy2.json")
require(len(remap["mapping"]) == 31, "source branch CT IDs must be remapped to 26 unique main IDs")
require(len({m["main"] for m in remap["mapping"]}) == 31, "CT remap collisions")
for mapping in remap["mapping"]:
    require(mapping["main"] in ctid and mapping["source"] not in {"CT-054", "CT-055"}
            or mapping["main"] in ctid, "invalid CT remap target")
require(all(next((x for x in ct if x["id"] == m["main"]), {}).get("native_client_validation") == "not-run"
            for m in remap["mapping"]), "merging static evidence must not automatically pass native CT")
require(next(x for x in packet_ids if x == "PKT-S5F") == "PKT-S5F", "S5F monster death packet missing")
s1e = next(x for x in read("04-analysis-integration/packets.json")["packets"] if x["id"] == "PKT-S1E")
require("disputed" in s1e["layout_status"], "must not mistake S1E for confirmed S5F DieObjects")
for p in ("02-server-planning/post-roy-merge-implementation-plan.md",
          "03-analysis-requests/post-merge-analysis-queue.md",
          "05-conformance/ct-id-remap-roy1-roy2.md"):
    require((ROOT / p).is_file(), "missing integrated planning " + p)
print("Roy1/Roy2 merge evidence and CT lineage: PASS")

# Roy1 A-004 / Roy2 A-011 incremental Client I/O handoff
npc = next(x for x in a if x["id"] == "A-011")
require(npc["status"] == "integrated" and npc["handoff_status"] == "partial", "A-011 must remain integrated/partial")
require(all(f"A011-E{i:02d}" in EVIDENCE_IDS for i in range(1,9)), "A-011 missing indexed evidence")
require("PKT-S1A" in packet_ids, "A-004 Motion packet not merged")
require(all(f"CT-{i:03d}" in ctid for i in range(82,87)), "new CT-082..086 not registered")
print("Roy1 A-004 / Roy2 A-011 incremental evidence: PASS")
