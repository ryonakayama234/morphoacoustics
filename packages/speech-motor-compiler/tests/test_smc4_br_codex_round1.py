"""First external GitHub Codex P2 regression for source 78327ae.

Test-only RED commit before code fixes: typed-key canonical collection order
and aggregate GoalSlot cap with empty candidate arrays.
"""
import json

from morphoacoustics_smc.canonical_ingress import parse_canonical_request
from test_smc4_br_ingress_preregistered import fixture, encoded


def test_codex1_alternative_paths_sorted_by_path_id_not_json_field_text():
    d = fixture()
    d["pronunciation"]["paths"][1]["complete"] = False
    r = parse_canonical_request(encoded(d))
    assert r.request is not None
    paths = json.loads(r.request.canonical_bytes)["pronunciation"]["paths"]
    assert [p["path_id"] for p in paths] == ["p1", "p2"]


def test_codex1_1025_empty_slots_exceeds_total_slot_candidate_budget():
    d = fixture()
    x = d["motor_mapping"]["lexicon"]["bundles"]
    x[0]["slots"] = [{"slot_id": f"s{i:04d}", "candidates": []}
                      for i in range(1024)]
    x[1]["slots"] = [{"slot_id": "another", "candidates": []}]
    r = parse_canonical_request(encoded(d))
    assert r.request is None
    assert r.receipt.canonical_request_sha256 is None
    assert r.receipt.ingress_status == "REJECTED"
