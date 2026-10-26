"""SMC-5 S01-S12 preregistered tests; this test-only commit MUST be RED.

No source module named symbolic_bridge exists at frozen preregistration commit.
Tests use artificial Task goals and supplied phoneme hypotheses, never speech evidence.
"""
import copy
import json
from fractions import Fraction

import pytest

from test_smc4_br_ingress_preregistered import fixture, encoded
from morphoacoustics_smc.canonical_ingress import parse_canonical_request
from morphoacoustics_smc.model import Event
from morphoacoustics_smc.symbolic_bridge import compile_wire, compile_canonical, timeline_table


def f(n, d=1):
    r = Fraction(n, d)
    return {"numerator": r.numerator, "denominator": r.denominator}


def c(template, definition, lo=0, hi=1, pred=None):
    return {"template_id": template, "definition_id": definition,
            "semantic_revision": "1", "lower": f(lo), "upper": f(hi),
            "context": pred or {"op": "TRUE", "key": "", "expected": "", "operands": []},
            "priority": None, "evidence_id": "synthetic-fixture",
            "status": "SYNTHETIC_ONLY"}


def slot(name, *candidates):
    return {"slot_id": name, "candidates": list(candidates)}


def valid():
    d = fixture()
    bundles = d["motor_mapping"]["lexicon"]["bundles"]
    bundles[0]["slots"] = [
        slot("tract", c("P1-T", "tract")),
        slot("source", c("P1-S", "source")),
    ]
    bundles[1]["slots"] = [slot("tract", c("P2-T", "tract"))]
    d["coordination"]["anchors"] = [
        {"unit_id": uid, "slot_id": s, "event": event, "time_s": f(t, 10)}
        for uid, s, start, end in [("P1", "tract", 0, 6),
                                   ("P1", "source", 0, 8),
                                   ("P2", "tract", 4, 10)]
        for event, t in [("ONSET", start), ("OFFSET", end)]
    ]
    return d


def run(d):
    return compile_wire(encoded(d))


def rejected(d, code):
    r = run(d)
    assert r.plan is None
    assert r.receipt.status == "REJECTED"
    assert r.receipt.code == code
    assert r.receipt.plan_digest is None
    assert r.receipt.candidate_digest is None
    assert r.receipt.canonical_request_sha256 is not None
    return r


def test_s01_selected_path_required_slots_and_exact_timing():
    result = run(valid())
    assert result.receipt.status == "RESOLVED"
    assert result.plan is not None and len(result.plan.tasks) == 3
    assert len(result.plan.associations) == 3
    assert len(result.goals) == 3
    rows = timeline_table(result)
    assert len(rows) == 3
    assert sorted((row[1], row[2]) for row in rows) == [
        (Fraction(0), Fraction(3, 5)),
        (Fraction(0), Fraction(4, 5)),
        (Fraction(2, 5), Fraction(1)),
    ]


def test_s02_explicit_shared_many_to_many_occurrence():
    d = valid()
    d["coordination"]["shares"] = [
        {"episode_id": "shared-G", "members": [["P1", "tract"], ["P2", "tract"]]}
    ]
    # Remove duplicated anchors to avoid assigning same shared task two onset times.
    d["coordination"]["anchors"] = [
        a for a in d["coordination"]["anchors"] if a["unit_id"] != "P2"
    ]
    result = run(d)
    assert result.plan is not None and result.receipt.status == "RESOLVED"
    assert len(result.plan.tasks) == 2
    assert len(result.plan.associations) == 3
    tid1 = next(a.task_id for a in result.plan.associations if a.unit_id == "P1"
                and next(t.goal_kind for t in result.plan.tasks if t.task_id == a.task_id) == "FUNCTIONAL_TRACT")
    assert any(a.unit_id == "P2" and a.task_id == tid1 for a in result.plan.associations)
    assert result.receipt.candidate_digest is not None


def test_s03_distinct_occurrences_same_goal_never_deduplicated():
    r = run(valid())
    assert r.plan is not None
    tract = [t.task_id for t in r.plan.tasks if t.goal_kind == "FUNCTIONAL_TRACT"]
    assert len(tract) == 2 and tract[0] != tract[1]


def test_s04_canonical_permutation_equivalence():
    d = valid()
    a = run(d)
    d["motor_mapping"]["lexicon"]["bundles"].reverse()
    d["motor_mapping"]["lexicon"]["definitions"].reverse()
    for bundle in d["motor_mapping"]["lexicon"]["bundles"]:
        bundle["slots"].reverse()
    d["coordination"]["anchors"].reverse()
    b = compile_wire(json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    assert a.receipt.canonical_request_sha256 == b.receipt.canonical_request_sha256
    assert a.receipt.plan_digest == b.receipt.plan_digest
    assert a.receipt.candidate_digest == b.receipt.candidate_digest
    assert a.receipt.submission_sha256 != b.receipt.submission_sha256


def test_s05_unselected_path_cannot_be_compiled():
    d = valid()
    a = run(d)
    d["pronunciation"]["paths"][1]["units"][0]["symbol"] = "alt"
    b = run(d)
    assert a.plan is not None and b.plan is not None
    assert a.receipt.plan_digest == b.receipt.plan_digest
    assert a.receipt.candidate_digest != b.receipt.candidate_digest


def test_s06_unmapped_ambiguous_unknown_priority_and_scope():
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"] = d["motor_mapping"]["lexicon"]["bundles"][:1]
    rejected(d, "UNMAPPED")
    d = valid()
    other = copy.deepcopy(d["motor_mapping"]["lexicon"]["bundles"][0])
    other["bundle_id"] = "BA2"
    d["motor_mapping"]["lexicon"]["bundles"].append(other)
    rejected(d, "AMBIGUOUS")
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"][0]["slots"][0]["candidates"].append(c("P1-other", "tract"))
    rejected(d, "AMBIGUOUS")
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"][0]["context"] = {
        "op": "EQ", "key": "missing", "expected": "x", "operands": []}
    rejected(d, "INSUFFICIENT_CONTEXT")
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"][0]["priority"] = 1
    rejected(d, "UNSUPPORTED_SELECTION_POLICY")
    d = valid()
    b = d["motor_mapping"]["lexicon"]["bundles"][0]
    b["target_scope_kind"] = "MULTI_UNIT"
    b["target_unit_ids"] = ["P1", "P2"]
    rejected(d, "UNSUPPORTED_MAPPING_SCOPE")


def test_s07_dangling_definition_incompatible_sharing_goal_intersection():
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"][0]["slots"][0]["candidates"][0]["definition_id"] = "unknown"
    rejected(d, "UNKNOWN_DEFINITION")
    d = valid()
    d["coordination"]["shares"] = [{"episode_id": "share", "members": [["P1", "tract"], ["P2", "tract"]]}]
    d["coordination"]["anchors"] = [a for a in d["coordination"]["anchors"] if a["unit_id"] != "P2"]
    d["motor_mapping"]["lexicon"]["bundles"][1]["slots"][0]["candidates"][0]["lower"] = f(2)
    d["motor_mapping"]["lexicon"]["bundles"][1]["slots"][0]["candidates"][0]["upper"] = f(3)
    rejected(d, "INCOMPATIBLE_SHARE")
    d = valid()
    d["coordination"]["shares"] = [{"episode_id": "share", "members": [["P1", "tract"], ["P2", "tract"]]}]
    d["coordination"]["anchors"] = [a for a in d["coordination"]["anchors"] if a["unit_id"] != "P2"]
    d["motor_mapping"]["lexicon"]["bundles"][0]["slots"][0]["candidates"][0]["lower"] = f(1,2)
    d["motor_mapping"]["lexicon"]["bundles"][1]["slots"][0]["candidates"][0]["upper"] = f(3,4)
    r = run(d)
    assert r.plan is not None
    shared = next(goal for goal in r.goals if len(goal.members) == 2)
    assert shared.lower == Fraction(1,2) and shared.upper == Fraction(3,4)


def test_s08_timing_contradiction_nonpositive_unanchored():
    d = valid()
    d["coordination"]["anchors"][1]["time_s"] = f(0)
    rejected(d, "NONPOSITIVE_DURATION")
    d = valid()
    d["coordination"]["anchors"][0]["time_s"] = f(9,10)
    rejected(d, "NONPOSITIVE_DURATION")
    d = valid()
    d["coordination"]["anchors"] = d["coordination"]["anchors"][:1]
    rejected(d, "UNRESOLVED_TIMING")
    d = valid()
    d["coordination"]["relations"] = [
        {"from_unit": "P1", "from_slot": "tract", "from_event": "ONSET",
         "to_unit": "P2", "to_slot": "tract", "to_event": "ONSET", "lag_s": f(0)}
    ]
    rejected(d, "CONTRADICTORY_TIMING")


def test_s09_source_unicode_and_no_physical_state():
    r = run(valid())
    assert r.plan is not None and r.plan.source_text == "甲乙"
    assert [(u.start_offset, u.end_offset) for u in r.plan.pronunciation_units] == [(0,1),(1,2)]
    assert not any(hasattr(r.plan, key) for key in ("morphology", "organ", "waveform", "pressure", "f0"))


def test_s10_mapping_refusal_preserves_ingress_evidence():
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"] = []
    r = rejected(d, "UNMAPPED")
    assert r.receipt.submission_sha256 and r.receipt.canonical_request_sha256
    bad = compile_wire(b"not json")
    assert bad.receipt.stage == "INGRESS" and bad.receipt.canonical_request_sha256 is None


def test_s11_goal_revision_changes_candidate_digest_even_if_graph_constant():
    d = valid()
    a = run(d)
    d["motor_mapping"]["lexicon"]["bundles"][0]["slots"][0]["candidates"][0]["upper"] = f(2)
    b = run(d)
    assert a.plan is not None and b.plan is not None
    assert a.receipt.plan_digest == b.receipt.plan_digest
    assert a.receipt.candidate_digest != b.receipt.candidate_digest


def test_s12_ingress_required_and_no_python_graph_ingress():
    accepted = parse_canonical_request(encoded(valid()))
    assert accepted.request is not None
    r = compile_canonical(accepted.request)
    assert r.plan is not None
    bad = compile_wire(valid())
    assert bad.plan is None and bad.receipt.stage == "INGRESS"

def test_s12a_stage_specific_timing_and_mapping_failure_receipts():
    d = valid()
    d["coordination"]["anchors"][1]["time_s"] = f(0)
    r = rejected(d, "NONPOSITIVE_DURATION")
    assert r.receipt.stage == "TIMING"
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"] = []
    r = rejected(d, "UNMAPPED")
    assert r.receipt.stage == "MAPPING"
    d = valid()
    d["coordination"]["relations"].append({
        "from_unit": "P1", "from_slot": "tract", "from_event": "ONSET",
        "to_unit": "P9", "to_slot": "tract", "to_event": "ONSET",
        "lag_s": f(0),
    })
    r = rejected(d, "UNKNOWN_TIMING_MEMBER")
    assert r.receipt.stage == "COORDINATION"


def test_s12b_share_duplicate_resolved_anchor_refused():
    d = valid()
    d["coordination"]["shares"] = [
        {"episode_id": "shared", "members": [["P1", "tract"], ["P2", "tract"]]}
    ]
    r = rejected(d, "DUPLICATE_COORDINATION")
    assert r.receipt.stage == "COORDINATION"


def test_s12c_strong_kleene_context_false_overrides_missing():
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"][0]["context"] = {
        "op": "AND", "key": "", "expected": "", "operands": [
            {"op": "FALSE", "key": "", "expected": "", "operands": []},
            {"op": "EQ", "key": "missing", "expected": "value", "operands": []},
        ],
    }
    rejected(d, "UNMAPPED")
    d = valid()
    d["motor_mapping"]["lexicon"]["bundles"][0]["context"] = {
        "op": "OR", "key": "", "expected": "", "operands": [
            {"op": "TRUE", "key": "", "expected": "", "operands": []},
            {"op": "EQ", "key": "missing", "expected": "value", "operands": []},
        ],
    }
    assert run(d).plan is not None


def test_codex_p2_graph_stage_for_wellformed_wire_bad_symbolic_id():
    """Codex review #211 P2: graph error must never masquerade as mapping."""
    d = valid()
    d["segment"]["segment_id"] = " "
    result = rejected(d, "INVALID_SEGMENT_ID")
    assert result.receipt.stage == "GRAPH"
    assert result.receipt.plan_digest is None
    d = valid()
    selected = d["pronunciation"]["paths"][0]["units"][0]
    selected["unit_id"] = " "
    b = d["motor_mapping"]["lexicon"]["bundles"][0]
    b["unit_id"] = " "
    b["target_unit_ids"] = [" "]
    for a in d["coordination"]["anchors"]:
        if a["unit_id"] == "P1":
            a["unit_id"] = " "
    result = rejected(d, "INVALID_OR_DUPLICATE_UNIT_ID")
    assert result.receipt.stage == "GRAPH"
