"""Preregistered A01-A09 CVI/SMC research preflight; never a body/speech oracle."""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from pathlib import Path
import json
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SMC_TESTS = PROJECT_ROOT / "packages" / "speech-motor-compiler" / "tests"
sys.path.insert(0, str(SMC_TESTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_smc5_preregistered import encoded, valid  # synthetic fixture, not language data
from morphoacoustics_smc.symbolic_bridge import compile_wire, timeline_table
from morphoacoustics_smc.temporal_stn import (
    TemporalConstraint, TemporalScenario, analyze_temporal_wire,
)
from morphoacoustics_smc.model import Event

from binding_preflight import audit_smc_core_binding


def test_a01_a03_formal_go_semantic_stop_no_body_fallback():
    r = audit_smc_core_binding(encoded(valid()))
    assert r.stage_a == "FORMAL_AUTHENTICATED"
    assert r.stage_b == "UNMAPPED_SEMANTICS"
    assert r.reason == "NO_EVIDENCED_PHYSICAL_TASK_BINDING"
    assert len(r.tasks) == 3
    assert len({x.task_id for x in r.tasks}) == 3
    assert len(r.exact_events) == 6
    assert r.canonical_request_sha256 and r.candidate_digest and r.source_timing_digest
    assert all(isinstance(row[2], Fraction) for row in r.exact_events)
    assert r.mapped_physical_tasks == ()
    assert r.physical_trace_ref is None
    assert r.acoustic_trace_ref is None
    assert r.physical_coverage == (0, 3)


def test_a02_actual_definition_fields_are_authenticated_not_guessed():
    r = audit_smc_core_binding(encoded(valid()))
    tracts = [t for t in r.tasks if t.definition_id == "tract"]
    source = [t for t in r.tasks if t.definition_id == "source"]
    assert len(tracts) == 2 and len(source) == 1
    assert all((t.variable, t.value_domain, t.applicability_domain) ==
               ("tract", "open_closed", "synthetic") for t in tracts)
    assert all(t.capabilities == ("contact", "flow") for t in tracts)
    assert (source[0].variable, source[0].value_domain, source[0].applicability_domain) == (
        "source", "active_inactive", "synthetic")
    assert all(t.lower <= t.upper for t in r.tasks)
    assert r.stage_b == "UNMAPPED_SEMANTICS"


@pytest.mark.parametrize("raw", [b"not-json", b"{}", {"fake": True}, b"\xff"])
def test_a04_rejected_ingress_no_schedule_or_core_payload(raw):
    r = audit_smc_core_binding(raw)
    assert r.stage_a == "REJECTED"
    assert r.stage_b == "NOT_RUN"
    assert r.tasks == () and r.exact_events == () and r.mapped_physical_tasks == ()
    assert r.physical_trace_ref is None and r.acoustic_trace_ref is None


def test_a04_smc_timing_rejects_incomplete_schedule():
    d = valid()
    d["coordination"]["anchors"] = d["coordination"]["anchors"][:1]
    r = audit_smc_core_binding(encoded(d))
    assert r.stage_a == "REJECTED" and r.tasks == ()
    assert r.stage_b == "NOT_RUN"


def test_a05_shared_task_compiled_and_counted_once():
    d = valid()
    d["coordination"]["shares"] = [
        {"episode_id": "shared-G", "members": [["P1", "tract"], ["P2", "tract"]]}
    ]
    d["coordination"]["anchors"] = [
        a for a in d["coordination"]["anchors"] if a["unit_id"] != "P2"
    ]
    r = audit_smc_core_binding(encoded(d))
    assert r.stage_a == "FORMAL_AUTHENTICATED"
    assert len(r.tasks) == 2 and r.physical_coverage == (0, 2)
    assert len(r.exact_events) == 4
    assert sum(len(x.members) == 2 for x in r.tasks) == 1


def test_a06_canonical_declaration_permutation_is_invariant():
    a = valid()
    b = valid()
    b["motor_mapping"]["lexicon"]["definitions"].reverse()
    b["motor_mapping"]["lexicon"]["bundles"].reverse()
    for bundle in b["motor_mapping"]["lexicon"]["bundles"]:
        bundle["slots"].reverse()
    b["coordination"]["anchors"].reverse()
    r1 = audit_smc_core_binding(encoded(a))
    r2 = audit_smc_core_binding(json.dumps(b, sort_keys=True, ensure_ascii=False).encode())
    assert r1.canonical_request_sha256 == r2.canonical_request_sha256
    assert r1.candidate_digest == r2.candidate_digest
    assert r1.source_timing_digest == r2.source_timing_digest
    assert r1.tasks == r2.tasks and r1.exact_events == r2.exact_events


def test_a07_smc6_compatibility_time_contradiction_has_no_witness():
    raw = encoded(valid())
    original = compile_wire(raw)
    tid, onset, _ = timeline_table(original)[0]
    opposite = Fraction(1, 10) if onset != Fraction(1, 10) else Fraction(2, 10)
    s = TemporalScenario("bad", "COMPATIBILITY", Fraction(2), Fraction(1, 100), (
        TemporalConstraint("contradict", None, (tid, Event.ONSET), opposite, opposite),
    ))
    result = analyze_temporal_wire(raw, s)
    assert result.status == "UNSAT"
    assert result.events == ()
    assert result.receipt and result.receipt.witness_digest is None


def test_a08_no_caller_invented_core_mapping_accepted():
    raw = encoded(valid())
    with pytest.raises(TypeError):
        audit_smc_core_binding(raw, {"tract": "CONSTRICT", "unit": "m"})  # type: ignore[call-arg]
    assert audit_smc_core_binding(raw).stage_b == "UNMAPPED_SEMANTICS"


def test_a09_actual_core_gesture_names_are_not_mapping_evidence():
    from morphoacoustics.domain.gesture import Task  # separate Core package
    assert Task.CONSTRICT.value == "CONSTRICT"
    r = audit_smc_core_binding(encoded(valid()))
    assert r.stage_b == "UNMAPPED_SEMANTICS"
    assert not hasattr(r, "waveform") and not hasattr(r, "take_ref")
