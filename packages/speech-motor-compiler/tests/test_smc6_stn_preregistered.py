"""SMC-6 prospective T01-T15 exact synthetic tests.

TEST-ONLY initial commit intentionally imports an absent temporal_stn module.
No real speech, morphology, organs or waveform claim.
"""
from dataclasses import replace
from fractions import Fraction
import dataclasses

from test_smc5_preregistered import valid, encoded
from morphoacoustics_smc.model import Event
from morphoacoustics_smc.symbolic_bridge import compile_wire, timeline_table
from morphoacoustics_smc.temporal_stn import (
    TemporalConstraint, TemporalScenario, analyze_temporal_wire,
)

O = Event.ONSET
F = Event.OFFSET


def original():
    data = encoded(valid())
    result = compile_wire(data)
    assert result.plan is not None and result.receipt.status == "RESOLVED"
    ids = {member: goal.task_id for goal in result.goals for member in goal.members}
    return data, result, ids


def c(name, a, b, lo, hi):
    return TemporalConstraint(name, a, b, Fraction(lo), Fraction(hi))


def ep(tid, event):
    return (tid, event)


def study(ids, *, contradiction=False):
    g1 = ids[("P1", "tract")]
    g2 = ids[("P2", "tract")]
    constraints = (
        c("s1", None, ep(g1, O), 0, 0),
        c("e1", ep(g1, O), ep(g1, F), Fraction(3, 10), Fraction(3, 10)),
        c("s2", None, ep(g2, O), Fraction(9, 50), Fraction(11, 50)),
        c("e2", ep(g2, O), ep(g2, F), Fraction(19, 100), Fraction(19, 100)),
    )
    if contradiction:
        constraints += (c("contradict", None, ep(g2, O), Fraction(7, 20), Fraction(3, 5)),)
    return TemporalScenario(
        study_id="synthetic-G1-G2", lane="RESEARCH_OVERRIDE",
        horizon_s=Fraction(3, 5), minimum_duration_s=Fraction(1, 100),
        constraints=constraints,
        replacement_policy="SMC5_EXACT_TIMING_REPLACED_FOR_SYNTHETIC_STUDY",
        replacement_reason="Compare synthetic bounded temporal choices",
    )


def event_map(r):
    return {(tid, ev): (low, high, chosen) for tid, ev, low, high, chosen in r.events}


def overlap(r, a, b):
    pair = {a, b}
    return next((mi, ma, w) for i, j, mi, ma, w in r.overlaps if {i, j} == pair)


def test_t01_nonunique_exact_event_envelope_and_joint_overlap():
    data, _, ids = original()
    r = analyze_temporal_wire(data, study(ids))
    g1, g2 = ids[("P1", "tract")], ids[("P2", "tract")]
    assert r.status == "SAT_NONUNIQUE" and r.code == "OK"
    e = event_map(r)
    assert e[(g1, O)][:2] == (Fraction(0), Fraction(0))
    assert e[(g1, F)][:2] == (Fraction(3, 10), Fraction(3, 10))
    assert e[(g2, O)][:2] == (Fraction(9, 50), Fraction(11, 50))
    assert e[(g2, F)][:2] == (Fraction(37, 100), Fraction(41, 100))
    assert e[(g2, O)][2] == Fraction(9, 50)
    assert overlap(r, g1, g2) == (Fraction(2, 25), Fraction(3, 25), Fraction(3, 25))
    assert r.receipt is not None and r.receipt.source_timing_digest


def test_t02_t03_endpoints_of_overlap():
    data, _, ids = original()
    g1, g2 = ids[("P1", "tract")], ids[("P2", "tract")]
    for onset, expected in ((Fraction(9, 50), Fraction(3, 25)), (Fraction(11, 50), Fraction(2, 25))):
        s = study(ids)
        r = analyze_temporal_wire(data, replace(
            s, constraints=s.constraints + (c("pin", None, ep(g2, O), onset, onset),)))
        assert r.status == "SAT_NONUNIQUE"  # third task still has free events
        assert overlap(r, g1, g2) == (expected, expected, expected)


def test_t04_sequential_study_different_digest():
    data, _, ids = original()
    g1, g2 = ids[("P1", "tract")], ids[("P2", "tract")]
    a = analyze_temporal_wire(data, study(ids))
    s = study(ids)
    cs = tuple(x for x in s.constraints if x.constraint_id != "s2") + (
        c("s2", None, ep(g2, O), Fraction(3, 10), Fraction(3, 10)),)
    b = analyze_temporal_wire(data, replace(s, constraints=cs))
    assert overlap(b, g1, g2) == (Fraction(0),) * 3
    assert a.receipt and b.receipt and a.receipt.study_digest != b.receipt.study_digest


def test_t05_t06_exact_unsat_negative_cycle_no_schedule():
    data, _, ids = original()
    s = study(ids, contradiction=True)
    r = analyze_temporal_wire(data, s)
    assert r.status == "UNSAT" and r.events == () and r.overlaps == ()
    assert r.negative_cycle_weight is not None and r.negative_cycle_weight < 0
    g2 = ids[("P2", "tract")]
    s = study(ids)
    zero = c("duration_zero", ep(g2, O), ep(g2, F), 0, 0)
    r = analyze_temporal_wire(data, replace(s, constraints=s.constraints + (zero,)))
    assert r.status == "UNSAT" and r.negative_cycle_weight is not None
    assert r.negative_cycle_weight < 0


def test_t07_t08_exact_smc5_compatibility_is_immutable():
    data, original_result, ids = original()
    s = TemporalScenario(
        study_id="compatibility", lane="COMPATIBILITY",
        horizon_s=Fraction(2), minimum_duration_s=Fraction(1, 100),
        constraints=(),
    )
    a = analyze_temporal_wire(data, s)
    assert a.status == "SAT_UNIQUE"
    assert {(i, ev): chosen for i, ev, _, _, chosen in a.events} == {
        (tid, ev): t for tid, start, end in timeline_table(original_result)
        for ev, t in ((O, start), (F, end))
    }
    assert all(lo == hi == chosen for _, _, lo, hi, chosen in a.events)
    assert a.receipt and a.receipt.source_candidate_digest == original_result.receipt.candidate_digest
    g2 = ids[("P2", "tract")]
    contrary = c("bad_extra", None, ep(g2, O), Fraction(1, 10), Fraction(1, 10))
    b = analyze_temporal_wire(data, replace(s, constraints=(contrary,)))
    assert b.status == "UNSAT" and b.events == ()


def test_t09_explicit_override_and_original_digest_kept():
    data, _, ids = original()
    a = analyze_temporal_wire(data, study(ids))
    assert a.receipt and a.receipt.source_candidate_digest and a.receipt.source_timing_digest
    broken = replace(study(ids), replacement_policy=None)
    b = analyze_temporal_wire(data, broken)
    assert b.status == "REJECTED" and b.events == ()
    assert b.code == "MISSING_EXPLICIT_TIMING_OVERRIDE"
    broken = replace(study(ids), replacement_reason=" ")
    assert analyze_temporal_wire(data, broken).status == "REJECTED"


def test_t10_constraint_permutation_same_study_replay():
    data, _, ids = original()
    s = study(ids)
    a = analyze_temporal_wire(data, s)
    b = analyze_temporal_wire(data, replace(s, constraints=tuple(reversed(s.constraints))))
    assert a == b
    assert a.receipt and a.receipt.study_digest and a.receipt.witness_digest


def test_t11_smc5_shared_task_one_temporal_occurrence():
    d = valid()
    d["coordination"]["shares"] = [
        {"episode_id": "shared-G", "members": [["P1", "tract"], ["P2", "tract"]]}]
    d["coordination"]["anchors"] = [a for a in d["coordination"]["anchors"] if a["unit_id"] != "P2"]
    data = encoded(d)
    smc5 = compile_wire(data)
    assert smc5.plan is not None
    s = TemporalScenario("shared", "COMPATIBILITY", Fraction(2), Fraction(1, 100), ())
    r = analyze_temporal_wire(data, s)
    assert r.status == "SAT_UNIQUE"
    assert len(r.events) == 2 * len(smc5.plan.tasks)
    assert len({(tid, ev) for tid, ev, *_ in r.events}) == len(r.events)
    assert len(r.overlaps) == 1


def test_t12_bad_ids_endpoints_types_and_duplicates():
    data, _, ids = original()
    s = study(ids)
    for extra in (
        c("s1", None, ep(ids[("P1", "tract")], O), 0, 0),
        c("unknown", None, ep("forged-task", O), 0, 0),
    ):
        r = analyze_temporal_wire(data, replace(s, constraints=s.constraints + (extra,)))
        assert r.status == "REJECTED" and r.events == ()
    bad = replace(s, constraints=s.constraints + (
        TemporalConstraint("float", None, ep(ids[("P1", "tract")], O), 0.1, 0.2),))
    assert analyze_temporal_wire(data, bad).status == "REJECTED"
    assert analyze_temporal_wire({"forged": True}, s).status == "REJECTED"


def test_t13_horizon_duration_resource_and_unsupported_refusals():
    data, _, ids = original()
    s = study(ids)
    invalid = (
        replace(s, horizon_s=Fraction(0)),
        replace(s, minimum_duration_s=Fraction(0)),
        replace(s, horizon_s=Fraction(11)),
        replace(s, constraints=s.constraints + (
            c("oversized", None, ep(ids[("P1", "tract")], O), 0, Fraction(10**10)),)),
        replace(s, lane="UNKNOWN"),
    )
    for case in invalid:
        r = analyze_temporal_wire(data, case)
        assert r.status == "REJECTED" and r.events == ()


def test_t14_monotonic_hard_constraint_intervention():
    data, _, ids = original()
    g2 = ids[("P2", "tract")]
    s = study(ids)
    a = analyze_temporal_wire(data, s)
    b = analyze_temporal_wire(data, replace(
        s, constraints=s.constraints + (
            c("narrow", None, ep(g2, O), Fraction(1, 5), Fraction(11, 50)),)))
    ea, eb = event_map(a), event_map(b)
    for event in ea:
        assert eb[event][0] >= ea[event][0]
        assert eb[event][1] <= ea[event][1]


def test_t15_independent_direct_fixture_and_no_body_leakage():
    data, _, ids = original()
    r = analyze_temporal_wire(data, study(ids))
    assert r.status == "SAT_NONUNIQUE"
    # Hand-derived independent oracle, without invoking solver helpers.
    assert Fraction(3, 10) - Fraction(11, 50) == Fraction(2, 25)
    assert Fraction(3, 10) - Fraction(9, 50) == Fraction(3, 25)
    for f in dataclasses.fields(type(r)):
        assert f.name not in {"morphology", "organ", "actuator", "waveform", "pressure", "f0"}
