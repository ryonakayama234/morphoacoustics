"""Gate C preregistered, implementer-origin adversarial probes.

Frozen protocol: docs/GATE_C_PROTOCOL.md (commit 7705ebd752e191a545506c0a2a79d56a40efc6bf).
All timings are synthetic rational arithmetic, not phonetic measurements.
The candidate validation implementation is deliberately NOT imported here except
through its public interface.  Source timestamps are independently constructed.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction as F
from random import Random

import pytest

from morphoacoustics_smc import (
    CouplingConstraint, Event, EventAnchor, MotorTask, PronunciationUnit,
    ReportStatus, SymbolicPlan, TaskAssociation, canonical_plan_json,
    plan_digest, resolve_timing, validate_plan,
)

SEEDS = (0, 7, 23, 148, 164)
CASES_PER_SEED = 20


def _make_case(seed: int, case: int) -> tuple[
    SymbolicPlan, dict[tuple[str, Event], F]
]:
    """Construct known rational event times first; encode independent equalities later.

    Generates redundant cycles, variable positive durations, overlapping windows,
    task sharing, and association graphs with no orphan source/task nodes.
    """
    rng = Random(seed * 1009 + case)
    n_tasks = 3 + case % 6
    n_units = 2 + (case // 2) % 4
    source = "あいうえおかきくけこ"[:n_units]
    units = tuple(
        PronunciationUnit(f"P{i}", source[i], i, i + 1)
        for i in range(n_units)
    )
    tasks = tuple(
        MotorTask(f"G{i}", f"SYNTHETIC_GOAL_{i % 3}", (f"CAP_{i % 4}",))
        for i in range(n_tasks)
    )
    links = {
        (f"P{j % n_units}", f"G{j}") for j in range(n_tasks)
    }
    links.update((f"P{i}", f"G{i % n_tasks}") for i in range(n_units))
    # A shared task is referenced by TWO distinct pronunciation units.
    links.update((f"P{(j + 1) % n_units}", f"G{j}")
                 for j in range(0, n_tasks, 2))
    associations = tuple(TaskAssociation(*edge) for edge in sorted(links))
    stamps: dict[tuple[str, Event], F] = {}
    for j in range(n_tasks):
        name = f"G{j}"
        onset = F(1, 20) + F(j, 12) + F(rng.randrange(7), 997)
        offset = onset + F(rng.randrange(2, 10), 31)
        stamps[(name, Event.ONSET)] = onset
        stamps[(name, Event.OFFSET)] = offset

    constraints: list[CouplingConstraint] = []
    for j in range(n_tasks):
        name = f"G{j}"
        constraints.append(CouplingConstraint(
            name, Event.ONSET, name, Event.OFFSET,
            stamps[(name, Event.OFFSET)] - stamps[(name, Event.ONSET)]
        ))
        if j:
            prior = f"G{j - 1}"
            constraints.append(CouplingConstraint(
                prior, Event.ONSET, name, Event.ONSET,
                stamps[(name, Event.ONSET)] - stamps[(prior, Event.ONSET)]
            ))
    # Redundant independent loop, which MUST be consistent even if negative lag.
    constraints.append(CouplingConstraint(
        "G0", Event.OFFSET, f"G{n_tasks - 1}", Event.OFFSET,
        stamps[(f"G{n_tasks - 1}", Event.OFFSET)] - stamps[("G0", Event.OFFSET)]
    ))
    plan = SymbolicPlan(
        segment_id=f"gate_c_{seed}_{case}", source_text=source,
        pronunciation_units=units, tasks=tasks, associations=associations,
        couplings=tuple(constraints),
        anchors=(EventAnchor("G0", Event.ONSET, stamps[("G0", Event.ONSET)]),),
    )
    return plan, stamps


@pytest.mark.parametrize(
    "seed,case",
    [(s, i) for s in SEEDS for i in range(CASES_PER_SEED)],
    ids=[f"seed-{s}-case-{i:02d}" for s in SEEDS for i in range(CASES_PER_SEED)],
)
def test_constructive_oracle_and_metamorphic_relations(
    seed: int, case: int
) -> None:
    original, expected = _make_case(seed, case)
    assert validate_plan(original).status is ReportStatus.STRUCTURALLY_VALID
    received = resolve_timing(original)
    assert received.status is ReportStatus.RESOLVED, (seed, case, received)
    assert {(task, event): time for task, event, time in received.events} == expected

    # Reorder all collections; the original exact solution and digest must remain.
    shuffled = replace(
        original,
        pronunciation_units=tuple(reversed(original.pronunciation_units)),
        tasks=tuple(reversed(original.tasks)),
        associations=tuple(reversed(original.associations)),
        couplings=tuple(reversed(original.couplings)),
        anchors=tuple(reversed(original.anchors)),
    )
    assert canonical_plan_json(shuffled) == canonical_plan_json(original)
    assert plan_digest(shuffled) == plan_digest(original)
    assert resolve_timing(shuffled).events == received.events

    # A changed absolute origin MUST translate all times, preserving all lags.
    delta = F(1, 7)
    translated = replace(original, anchors=(
        EventAnchor("G0", Event.ONSET, expected[("G0", Event.ONSET)] + delta),
    ))
    shifted = resolve_timing(translated)
    assert shifted.status is ReportStatus.RESOLVED
    assert {(task, event): time for task, event, time in shifted.events} == {
        key: time + delta for key, time in expected.items()
    }
    assert plan_digest(translated) != plan_digest(original)

    # An inconsistent second absolute anchor is a true contradiction, not
    # mere underdetermination. One rational tick defeats floating tolerances.
    contradiction = replace(original, anchors=original.anchors + (
        EventAnchor(
            f"G{len(original.tasks) - 1}", Event.OFFSET,
            expected[(f"G{len(original.tasks) - 1}", Event.OFFSET)] + F(1, 9973),
        ),
    ))
    report = validate_plan(contradiction)
    assert report.status is ReportStatus.INVALID
    assert "CONTRADICTORY_TIMING" in {d.code for d in report.diagnostics}
    assert resolve_timing(contradiction).events == ()


def test_partial_component_stays_unresolved_not_synthesized() -> None:
    p = SymbolicPlan(
        "partial", "あ",
        (PronunciationUnit("P", "a", 0, 1),),
        (MotorTask("A", "OPEN"), MotorTask("B", "CLOSE")),
        (TaskAssociation("P", "A"), TaskAssociation("P", "B")),
        (CouplingConstraint("A", Event.ONSET, "A", Event.OFFSET, F(1, 3)),),
        (EventAnchor("A", Event.ONSET, F(1, 11)),),
    )
    assert validate_plan(p).status is ReportStatus.STRUCTURALLY_VALID
    t = resolve_timing(p)
    assert t.status is ReportStatus.INVALID
    assert t.events == ()
    assert "UNRESOLVED_EVENT" in {d.code for d in t.diagnostics}


@pytest.mark.parametrize("duration,code", [
    (F(0), "NONPOSITIVE_DURATION"),
    (F(-1, 17), "NONPOSITIVE_DURATION"),
])
def test_impossible_intervals_fail_closed(duration: F, code: str) -> None:
    p = SymbolicPlan(
        "duration", "音",
        (PronunciationUnit("P", "on", 0, 1),),
        (MotorTask("G", "ABSTRACT_GOAL"),),
        (TaskAssociation("P", "G"),),
        (CouplingConstraint("G", Event.ONSET, "G", Event.OFFSET, duration),),
        (EventAnchor("G", Event.ONSET, F(1, 5)),),
    )
    assert code in {d.code for d in validate_plan(p).diagnostics}
    assert resolve_timing(p).events == ()


def test_negative_absolute_time_is_rejected() -> None:
    p = SymbolicPlan(
        "negative", "音", (PronunciationUnit("P", "on", 0, 1),),
        (MotorTask("G", "ABSTRACT"),), (TaskAssociation("P", "G"),),
        (CouplingConstraint("G", Event.ONSET, "G", Event.OFFSET, F(1, 4)),),
        (EventAnchor("G", Event.ONSET, -F(1, 16)),),
    )
    assert "NEGATIVE_ANCHORED_TIME" in {
        d.code for d in validate_plan(p).diagnostics
    }
    assert resolve_timing(p).events == ()


def test_unicode_codepoints_and_no_reading_inference() -> None:
    # '👩‍🔬' is one displayed grapheme, THREE Python codepoints.
    raw = "あ👩‍🔬い"
    assert len(raw) == 5
    p = SymbolicPlan(
        "unicode", raw,
        (PronunciationUnit("P1", "a", 0, 1),
         PronunciationUnit("P2", "synthetic", 1, 4),
         PronunciationUnit("P3", "i", 4, 5)),
        (MotorTask("G", "UNVERIFIED"),),
        (TaskAssociation("P1", "G"), TaskAssociation("P2", "G"),
         TaskAssociation("P3", "G")),
    )
    assert validate_plan(p).status is ReportStatus.STRUCTURALLY_VALID
    assert p.source_text == raw
    assert p.source_text[p.pronunciation_units[1].start_offset:
                         p.pronunciation_units[1].end_offset] == "👩‍🔬"
    assert plan_digest(replace(p, source_text="あ👩‍🔬う")) != plan_digest(p)
    assert resolve_timing(p).events == ()


def test_malformed_runtime_source_does_not_crash_validator() -> None:
    """Adversarial boundary: Python type hints alone do not validate payloads.

    A caller can construct SymbolicPlan(source_text=None) at runtime. The
    validator's advertised fail-closed behavior should return INVALID rather
    than raise TypeError while checking unit spans. Intentionally adversarial.
    """
    baseline, _ = _make_case(0, 0)
    wrong = replace(baseline, source_text=None)  # type: ignore[arg-type]
    report = validate_plan(wrong)
    assert report.status is ReportStatus.INVALID
    assert "EMPTY_SOURCE" in {d.code for d in report.diagnostics}
    assert resolve_timing(wrong).events == ()
