from dataclasses import fields

import pytest

from morphoacoustics import Task, TaskParameter
from morphoacoustics.integration import (
    AnchorRef,
    CoordinationPlan,
    GestureEvent,
    GestureEventRef,
    GestureTemplate,
    PlanCompileStatus,
    ProsodyEvent,
    ProsodyEventKind,
    ProsodyPlan,
    ResolvedAnchor,
    ResolvedTimeline,
    TimingConstraint,
    compile_shared_timeline,
)


def _template(gesture_id: str, location: float) -> GestureTemplate:
    return GestureTemplate(
        id=gesture_id,
        task=Task.CONSTRICT,
        target="oral",
        location=location,
        parameters=(TaskParameter("target_area", 5e-5, "m2"),),
    )


def _timeline() -> ResolvedTimeline:
    return ResolvedTimeline(
        (
            ResolvedAnchor("utterance.start", 0.0, "fixture"),
            ResolvedAnchor("m2.onset", 0.20, "pronunciation:m2"),
            ResolvedAnchor("ap1.end", 0.30, "pronunciation:ap1"),
        )
    )


def _coordination(*, overlap_s: float) -> CoordinationPlan:
    a_on = GestureEventRef("A", GestureEvent.ONSET)
    a_off = GestureEventRef("A", GestureEvent.OFFSET)
    b_on = GestureEventRef("B", GestureEvent.ONSET)
    b_off = GestureEventRef("B", GestureEvent.OFFSET)
    return CoordinationPlan(
        (
            TimingConstraint(a_on, AnchorRef("utterance.start"), 0.08),
            TimingConstraint(a_off, a_on, 0.18),
            TimingConstraint(b_on, a_off, -overlap_s),
            TimingConstraint(b_off, b_on, 0.18),
        )
    )


def _compile(*, overlap_s: float):
    return compile_shared_timeline(
        gestures=(_template("A", 0.25), _template("B", 0.75)),
        coordination=_coordination(overlap_s=overlap_s),
        prosody=ProsodyPlan(()),
        timeline=_timeline(),
    )


def test_compiles_experiment_011_sequential_and_overlap_windows() -> None:
    sequential = _compile(overlap_s=0.0)
    overlap = _compile(overlap_s=0.06)

    assert sequential.status is PlanCompileStatus.VALID
    assert overlap.status is PlanCompileStatus.VALID
    assert sequential.score is not None
    assert overlap.score is not None

    assert [(g.onset_s, g.offset_s) for g in sequential.score.gestures] == pytest.approx(
        [(0.08, 0.26), (0.26, 0.44)]
    )
    assert [(g.onset_s, g.offset_s) for g in overlap.score.gestures] == pytest.approx(
        [(0.08, 0.26), (0.20, 0.38)]
    )


def test_compile_is_order_independent() -> None:
    gestures = (_template("A", 0.25), _template("B", 0.75))
    coordination = _coordination(overlap_s=0.06)

    first = compile_shared_timeline(
        gestures=gestures,
        coordination=coordination,
        prosody=ProsodyPlan(()),
        timeline=_timeline(),
    )
    second = compile_shared_timeline(
        gestures=tuple(reversed(gestures)),
        coordination=CoordinationPlan(tuple(reversed(coordination.constraints))),
        prosody=ProsodyPlan(()),
        timeline=ResolvedTimeline(tuple(reversed(_timeline().anchors))),
    )

    assert first.status is PlanCompileStatus.VALID
    assert second.status is PlanCompileStatus.VALID
    assert first.score == second.score
    assert first.resolved_events == second.resolved_events


def test_prosody_and_coordination_share_semantic_anchor_ids() -> None:
    prosody = ProsodyPlan(
        (
            ProsodyEvent("ap1.end", ProsodyEventKind.BOUNDARY, 0.8),
            ProsodyEvent("ap1.end", ProsodyEventKind.DURATION_SCALE, 1.15),
            ProsodyEvent("m2.onset", ProsodyEventKind.PROMINENCE, 0.5),
        )
    )
    result = compile_shared_timeline(
        gestures=(_template("A", 0.25), _template("B", 0.75)),
        coordination=_coordination(overlap_s=0.06),
        prosody=prosody,
        timeline=_timeline(),
    )

    assert result.status is PlanCompileStatus.VALID
    assert [(event.anchor_id, event.kind, event.time_s) for event in result.resolved_prosody] == [
        ("ap1.end", ProsodyEventKind.BOUNDARY, 0.30),
        ("ap1.end", ProsodyEventKind.DURATION_SCALE, 0.30),
        ("m2.onset", ProsodyEventKind.PROMINENCE, 0.20),
    ]


def test_unknown_anchor_is_explicitly_invalid() -> None:
    result = compile_shared_timeline(
        gestures=(_template("A", 0.25),),
        coordination=CoordinationPlan(
            (
                TimingConstraint(
                    GestureEventRef("A", GestureEvent.ONSET),
                    AnchorRef("missing"),
                    0.0,
                ),
                TimingConstraint(
                    GestureEventRef("A", GestureEvent.OFFSET),
                    GestureEventRef("A", GestureEvent.ONSET),
                    0.18,
                ),
            )
        ),
        prosody=ProsodyPlan(()),
        timeline=_timeline(),
    )

    assert result.status is PlanCompileStatus.INVALID
    assert result.score is None
    assert "UNKNOWN_ANCHOR" in {diagnostic.code for diagnostic in result.diagnostics}


def test_contradictory_timing_is_explicitly_invalid() -> None:
    onset = GestureEventRef("A", GestureEvent.ONSET)
    offset = GestureEventRef("A", GestureEvent.OFFSET)
    result = compile_shared_timeline(
        gestures=(_template("A", 0.25),),
        coordination=CoordinationPlan(
            (
                TimingConstraint(onset, AnchorRef("utterance.start"), 0.08),
                TimingConstraint(onset, AnchorRef("utterance.start"), 0.09),
                TimingConstraint(offset, onset, 0.18),
            )
        ),
        prosody=ProsodyPlan(()),
        timeline=_timeline(),
    )

    assert result.status is PlanCompileStatus.INVALID
    assert "CONTRADICTORY_TIMING" in {
        diagnostic.code for diagnostic in result.diagnostics
    }


def test_unanchored_relative_component_is_not_silently_zeroed() -> None:
    onset = GestureEventRef("A", GestureEvent.ONSET)
    offset = GestureEventRef("A", GestureEvent.OFFSET)
    result = compile_shared_timeline(
        gestures=(_template("A", 0.25),),
        coordination=CoordinationPlan(
            (
                TimingConstraint(offset, onset, 0.18),
            )
        ),
        prosody=ProsodyPlan(()),
        timeline=_timeline(),
    )

    assert result.status is PlanCompileStatus.INVALID
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "UNRESOLVED_EVENT"
    }


def test_invalid_resolved_gesture_window_is_reported() -> None:
    onset = GestureEventRef("A", GestureEvent.ONSET)
    offset = GestureEventRef("A", GestureEvent.OFFSET)
    result = compile_shared_timeline(
        gestures=(_template("A", 0.25),),
        coordination=CoordinationPlan(
            (
                TimingConstraint(onset, AnchorRef("utterance.start"), 0.20),
                TimingConstraint(offset, onset, -0.10),
            )
        ),
        prosody=ProsodyPlan(()),
        timeline=_timeline(),
    )

    assert result.status is PlanCompileStatus.INVALID
    assert "INVALID_GESTURE_WINDOW" in {
        diagnostic.code for diagnostic in result.diagnostics
    }


def test_candidate_models_keep_physics_and_raw_f0_out_of_plans() -> None:
    gesture_fields = {field.name for field in fields(GestureTemplate)}
    prosody_fields = {field.name for field in fields(ProsodyEvent)}

    assert {"onset_s", "offset_s", "section_index", "body_id"} & gesture_fields == set()
    assert {"f0_hz", "waveform", "source_parameter", "body_id"} & prosody_fields == set()


def test_duration_scale_must_be_positive() -> None:
    with pytest.raises(ValueError, match="duration_scale"):
        ProsodyEvent("ap1.end", ProsodyEventKind.DURATION_SCALE, 0.0)
