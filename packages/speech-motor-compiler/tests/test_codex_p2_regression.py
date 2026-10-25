"""Codex-review P2 regression probes, added AFTER the frozen Gate C audit.

Issues are documented in PR #164 inline threads #discussion_r4365286361
and #discussion_r4365286367. The original Gate C protocol/tests are unchanged.
Synthetic task data only; no pronunciation or physical evidence.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction as F
from itertools import permutations

import pytest

from morphoacoustics_smc import (
    CouplingConstraint, Event, EventAnchor, MotorTask, PronunciationUnit,
    ReportStatus, SymbolicPlan, TaskAssociation, plan_digest,
    resolve_timing, validate_plan,
)


def _valid_plan() -> SymbolicPlan:
    return SymbolicPlan(
        segment_id="review", source_text="あ",
        pronunciation_units=(PronunciationUnit("P", "a", 0, 1),),
        tasks=(MotorTask("G", "ABSTRACT", ("SYMBOLIC_ONLY",)),),
        associations=(TaskAssociation("P", "G"),),
        couplings=(
            CouplingConstraint("G", Event.ONSET, "G", Event.OFFSET, F(1, 2)),
        ),
        anchors=(EventAnchor("G", Event.ONSET, F(1, 4)),),
    )


@pytest.mark.parametrize("field", [
    "segment_id", "source_text", "pronunciation_symbol",
    "pronunciation_unit_id", "task_goal_kind", "task_id",
    "capability_token",
])
def test_unpaired_surrogate_in_receipt_field_rejected(field: str) -> None:
    """Every otherwise-valid plan that cannot yield a UTF-8 receipt is INVALID.

    U+D800 is a lone high surrogate: JSON escape decoding can introduce it
    into a Python str, but UTF-8 rejects it. Preserve coherent references
    when mutating IDs, so the test probes Unicode rather than dangling links.
    """
    plan = _valid_plan()
    bad = "\ud800"
    if field == "segment_id":
        plan = replace(plan, segment_id=bad)
    elif field == "source_text":
        plan = replace(plan, source_text=bad)
    elif field == "pronunciation_symbol":
        plan = replace(plan, pronunciation_units=(
            replace(plan.pronunciation_units[0], symbol=bad),
        ))
    elif field == "pronunciation_unit_id":
        plan = replace(
            plan,
            pronunciation_units=(replace(plan.pronunciation_units[0], unit_id=bad),),
            associations=(TaskAssociation(bad, "G"),),
        )
    elif field == "task_goal_kind":
        plan = replace(plan, tasks=(replace(plan.tasks[0], goal_kind=bad),))
    elif field == "task_id":
        plan = replace(
            plan, tasks=(replace(plan.tasks[0], task_id=bad),),
            associations=(TaskAssociation("P", bad),),
            couplings=(replace(plan.couplings[0],
                               source_task_id=bad, target_task_id=bad),),
            anchors=(replace(plan.anchors[0], task_id=bad),),
        )
    elif field == "capability_token":
        plan = replace(plan, tasks=(
            replace(plan.tasks[0], capability_requirements=(bad,)),
        ))
    else:
        raise AssertionError(f"Unknown test field: {field}")

    report = validate_plan(plan)
    assert report.status is ReportStatus.INVALID, (field, report)
    assert "INVALID_UNICODE_SCALAR" in {d.code for d in report.diagnostics}, (
        field, report
    )
    assert resolve_timing(plan).events == ()


def test_valid_non_bmp_and_joined_unicode_remains_accepted() -> None:
    """A normal supplementary character or ZWJ sequence is not a surrogate."""
    plan = replace(
        _valid_plan(), source_text="👩‍🔬",
        pronunciation_units=(PronunciationUnit("P", "👩‍🔬", 0, 3),),
    )
    assert validate_plan(plan).status is ReportStatus.STRUCTURALLY_VALID
    assert len(plan_digest(plan)) == 64


def test_conflicting_anchors_permutation_diagnostics_are_invariant() -> None:
    """A contradictory graph has no legitimate derived signed/duration times.

    ONSET=0, OFFSET=1, OFFSET=-1 are the same exact contradictory
    equalities regardless of anchor input ordering. Never derive further
    interval or pre-zero diagnoses from arbitrary BFS traversal potentials.
    """
    base = replace(_valid_plan(), couplings=())
    anchors = (
        EventAnchor("G", Event.ONSET, F(0)),
        EventAnchor("G", Event.OFFSET, F(1)),
        EventAnchor("G", Event.OFFSET, F(-1)),
    )
    observed: set[tuple[str, ...]] = set()
    for order in permutations(anchors):
        plan = replace(base, anchors=order)
        report = validate_plan(plan)
        assert report.status is ReportStatus.INVALID
        codes = tuple(d.code for d in report.diagnostics)
        observed.add(codes)
        assert resolve_timing(plan).status is ReportStatus.INVALID
        assert resolve_timing(plan).events == ()

    assert observed == {("CONTRADICTORY_TIMING",)}, observed
