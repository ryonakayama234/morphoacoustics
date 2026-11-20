"""Predeclared synthetic research tests. NOT Japanese speech or physical evidence."""
from dataclasses import fields, replace
from fractions import Fraction

import pytest

from morphoacoustics_smc import (
    CouplingConstraint, Event, EventAnchor, MotorTask, PronunciationUnit,
    ReportStatus, SymbolicPlan, TaskAssociation, canonical_plan_json,
    plan_digest, resolve_timing, validate_plan,
)

F = Fraction


def fixture() -> SymbolicPlan:
    return SymbolicPlan(
        segment_id="s1", source_text="あい",
        pronunciation_units=(
            PronunciationUnit("P1", "a", 0, 1),
            PronunciationUnit("P2", "i", 1, 2),
        ),
        tasks=(
            MotorTask("G1", "GOAL_A", ("CAP_A",)),
            MotorTask("G2", "GOAL_SHARED", ("CAP_SHARED",)),
            MotorTask("G3", "GOAL_B"),
        ),
        associations=(
            TaskAssociation("P1", "G1"), TaskAssociation("P1", "G2"),
            TaskAssociation("P2", "G2"), TaskAssociation("P2", "G3"),
        ),
    )


def timed() -> SymbolicPlan:
    p = fixture()
    # Exact rational event windows:
    # G1 2/25..13/50; G2 1/5..33/100; G3 29/100..27/50.
    return replace(p, anchors=(EventAnchor("G1", Event.ONSET, F(2, 25)),),
                   couplings=(
                       CouplingConstraint("G1", Event.ONSET, "G1", Event.OFFSET, F(9, 50)),
                       CouplingConstraint("G1", Event.OFFSET, "G2", Event.ONSET, -F(3, 50)),
                       CouplingConstraint("G2", Event.ONSET, "G2", Event.OFFSET, F(13, 100)),
                       CouplingConstraint("G2", Event.OFFSET, "G3", Event.ONSET, -F(1, 25)),
                       CouplingConstraint("G3", Event.ONSET, "G3", Event.OFFSET, F(1, 4)),
                   ))


def codes(plan: SymbolicPlan) -> set[str]:
    return {d.code for d in validate_plan(plan).diagnostics}


def test_one_shared_task_reused_without_duplication():
    p = fixture()
    assert validate_plan(p).status is ReportStatus.STRUCTURALLY_VALID
    assert len(p.tasks) == 3
    assert sum(a.task_id == "G2" for a in p.associations) == 2
    assert len({t.task_id for t in p.tasks}) == 3
    assert {a.unit_id for a in p.associations if a.task_id == "G2"} == {"P1", "P2"}
    assert resolve_timing(p).status is ReportStatus.INVALID  # timing unanchored


def test_exact_rational_windows_and_overlap():
    r = resolve_timing(timed())
    assert r.status is ReportStatus.RESOLVED
    stamps = {(tid, ev): val for tid, ev, val in r.events}
    assert [stamps[("G1", Event.ONSET)], stamps[("G1", Event.OFFSET)]] == [F(2, 25), F(13, 50)]
    assert [stamps[("G2", Event.ONSET)], stamps[("G2", Event.OFFSET)]] == [F(1, 5), F(33, 100)]
    assert [stamps[("G3", Event.ONSET)], stamps[("G3", Event.OFFSET)]] == [F(29, 100), F(27, 50)]
    assert stamps[("G1", Event.OFFSET)] - stamps[("G2", Event.ONSET)] == F(3, 50)
    assert stamps[("G2", Event.OFFSET)] - stamps[("G3", Event.ONSET)] == F(1, 25)
    assert all(type(value) is Fraction for _, _, value in r.events)


def test_contradictory_two_anchors_fail_closed():
    p = timed()
    p = replace(p, anchors=p.anchors + (
        EventAnchor("G3", Event.ONSET, F(8, 25)),
    ))
    assert "CONTRADICTORY_TIMING" in codes(p)
    assert resolve_timing(p).events == ()


@pytest.mark.parametrize("bad,expected", [
    (lambda p: replace(p, associations=p.associations + (TaskAssociation("P1", "missing"),)), "UNKNOWN_ASSOCIATION_ENDPOINT"),
    (lambda p: replace(p, associations=p.associations + (TaskAssociation("P1", "G1"),)), "DUPLICATE_ASSOCIATION"),
    (lambda p: replace(p, tasks=p.tasks + (MotorTask("G2", "GOAL_SHARED"),)), "INVALID_OR_DUPLICATE_TASK_ID"),
    (lambda p: replace(p, pronunciation_units=p.pronunciation_units + (PronunciationUnit("P2", "i", 1, 2),)), "INVALID_OR_DUPLICATE_UNIT_ID"),
    (lambda p: replace(p, pronunciation_units=(PronunciationUnit("P1", "a", 5, 6), p.pronunciation_units[1])), "INVALID_SOURCE_SPAN"),
    (lambda p: replace(p, source_text=""), "EMPTY_SOURCE"),
    (lambda p: replace(p, pronunciation_units=()), "NO_PRONUNCIATION"),
    (lambda p: replace(p, associations=p.associations[:-1]), "ORPHAN_TASK"),
    (lambda p: replace(p, couplings=(CouplingConstraint("G1", Event.ONSET, "missing", Event.OFFSET, F(1)),)), "UNKNOWN_COUPLING_ENDPOINT"),
    (lambda p: replace(p, couplings=(CouplingConstraint("G1", "BAD", "G2", Event.ONSET, F(1)),)), "INVALID_EVENT"),
    (lambda p: replace(p, couplings=(CouplingConstraint("G1", Event.ONSET, "G2", Event.ONSET, 0.1),)), "INVALID_LAG"),
    (lambda p: replace(p, anchors=(EventAnchor("missing", Event.ONSET, F(0)),)), "UNKNOWN_ANCHOR_ENDPOINT"),
    (lambda p: replace(p, couplings=(CouplingConstraint("G1", Event.ONSET, "G1", Event.OFFSET, -F(1, 10)),)), "NONPOSITIVE_DURATION"),
])
def test_negative_probes_do_not_become_ready(bad, expected):
    p = bad(fixture())
    assert expected in codes(p)
    assert resolve_timing(p).events == ()


def test_unverified_capability_is_not_executable_status():
    p = fixture()
    assert p.tasks[0].capability_requirements == ("CAP_A",)
    assert validate_plan(p).status is ReportStatus.STRUCTURALLY_VALID
    forbidden = {"body_id", "organ_id", "area_vector", "pressure_pa", "f0_hz",
                 "score", "audio", "waveform", "solver_state", "gesture_score"}
    assert forbidden.isdisjoint({f.name for f in fields(SymbolicPlan)})
    assert not hasattr(p, "audio") and not hasattr(p, "score")


def test_no_automatic_reading_guess_from_kanji():
    p = replace(fixture(), source_text="漢", pronunciation_units=(),
                associations=(), tasks=())
    assert {"NO_PRONUNCIATION", "NO_MOTOR_TASKS"}.issubset(codes(p))


def test_reordered_semantic_plan_has_same_digest_and_unicode_unchanged():
    p = timed()
    reversed_plan = replace(
        p, pronunciation_units=tuple(reversed(p.pronunciation_units)),
        tasks=tuple(reversed(p.tasks)),
        associations=tuple(reversed(p.associations)),
        couplings=tuple(reversed(p.couplings)),
        anchors=tuple(reversed(p.anchors)),
    )
    assert canonical_plan_json(p) == canonical_plan_json(reversed_plan)
    assert plan_digest(p) == plan_digest(reversed_plan)
    assert plan_digest(p) != plan_digest(replace(p, source_text="いあ"))
    assert '"source_text":"あい"' in canonical_plan_json(p)


def test_no_core_dependency():
    import morphoacoustics_smc
    assert morphoacoustics_smc.__name__ == "morphoacoustics_smc"
    assert "morphoacoustics" not in morphoacoustics_smc.__dict__


def test_unresolved_event_is_explicit():
    p = replace(timed(), couplings=timed().couplings[:-1])
    r = resolve_timing(p)
    assert r.status is ReportStatus.INVALID and r.events == ()
    assert "UNRESOLVED_EVENT" in {d.code for d in r.diagnostics}
