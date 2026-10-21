"""SMC-1 research checks: no result is a validated physical/phonetic speech claim."""
from dataclasses import fields

import pytest

from morphoacoustics import Task, TaskParameter
from morphoacoustics.integration.shared_timeline import (
    CoordinationPlan, GestureEvent, GestureEventRef, GestureTemplate,
    PlanCompileStatus, ProsodyPlan, TimingConstraint, compile_shared_timeline,
)
from smc1_research.speech_motor_candidate import (
    CANDIDATE_VERSION, CandidateStatus, MotorIntentSlot,
    ScriptMotorCandidate, plan_kana_motor_candidate,
)


def _synthetic_fixture(candidate):
    """Synthetic two-CONSTRICT test adapter, emphatically NOT /a/ /i/ physics."""
    assert candidate.coordination is not None
    assert candidate.timeline is not None
    return compile_shared_timeline(
        gestures=tuple(
            GestureTemplate(
                id=slot.gesture_id, task=Task.CONSTRICT, target="oral",
                location=0.25 if i % 2 == 0 else 0.75,
                parameters=(TaskParameter("target_area", 5e-5, "m2"),),
            )
            for i, slot in enumerate(candidate.slots)
        ),
        coordination=candidate.coordination,
        prosody=ProsodyPlan(()),
        timeline=candidate.timeline,
    )


def test_ai_retains_source_and_symbolic_provenance() -> None:
    p = plan_kana_motor_candidate(segment_id="s1", text="あい")
    assert p.status is CandidateStatus.COORDINATION_RESEARCH_READY
    assert p.compiler_version == CANDIDATE_VERSION
    assert [(u.kana, u.phonemes, u.source_offset) for u in p.units] == [
        ("あ", ("a",), 0), ("い", ("i",), 1)
    ]
    assert [s.symbolic_intent for s in p.slots] == [
        "A_LIKE_INTENT", "I_LIKE_INTENT"
    ]
    assert p.diagnostics == ()
    assert not hasattr(p, "score")


def test_exact_011_timing_reproduced_only_by_synthetic_adapter() -> None:
    p = plan_kana_motor_candidate(segment_id="s1", text="あい")
    result = _synthetic_fixture(p)
    assert result.status is PlanCompileStatus.VALID
    assert result.score is not None
    assert [(g.onset_s, g.offset_s) for g in result.score.gestures] == pytest.approx([
        (0.08, 0.26), (0.20, 0.38)
    ])
    assert p.timing_policy is not None


def test_repeated_vowels_are_one_coordination_graph_not_concat() -> None:
    p = plan_kana_motor_candidate(segment_id="s7", text="あいあい")
    result = _synthetic_fixture(p)
    assert result.status is PlanCompileStatus.VALID
    assert result.score is not None
    assert [(g.onset_s, g.offset_s) for g in result.score.gestures] == pytest.approx([
        (0.08, 0.26), (0.20, 0.38), (0.32, 0.50), (0.44, 0.62)
    ])


@pytest.mark.parametrize("text", ["おはよう", "ありがとう"])
def test_unrealized_words_keep_all_known_units_and_refuse_score(text: str) -> None:
    p = plan_kana_motor_candidate(segment_id="s3", text=text)
    assert p.status is CandidateStatus.PARTIAL_MOTOR_PLAN
    assert "".join(unit.kana for unit in p.units) == text
    assert len(p.slots) == len(text)
    assert p.coordination is None
    assert p.timeline is None
    assert "MISSING_MOTOR_GESTURE" in {d.code for d in p.diagnostics}
    assert "CONTEXTUAL_PHONOLOGY_UNRESOLVED" in {d.code for d in p.diagnostics}


def test_unsupported_kanji_is_not_silently_pronounced_or_replaced() -> None:
    p = plan_kana_motor_candidate(segment_id="s5", text="お早う")
    assert p.status is CandidateStatus.INVALID_INPUT
    assert [(d.code, d.source_offset) for d in p.diagnostics if
            d.code == "UNSUPPORTED_CHARACTER"] == [("UNSUPPORTED_CHARACTER", 1)]
    assert p.coordination is None
    assert "".join(u.kana for u in p.units) != p.source_text


def test_punctuation_keeps_source_offset_but_does_not_invent_pause() -> None:
    p = plan_kana_motor_candidate(segment_id="s2", text="あ、い。")
    assert p.status is CandidateStatus.PARTIAL_MOTOR_PLAN
    assert [(b.symbol, b.source_offset) for b in p.boundaries] == [
        ("、", 1), ("。", 3)
    ]
    assert [u.source_offset for u in p.units] == [0, 2]
    assert p.coordination is None


def test_empty_and_non_text_cannot_emit_plan() -> None:
    p = plan_kana_motor_candidate(segment_id="s1", text="")
    assert p.status is CandidateStatus.INVALID_INPUT
    assert p.coordination is None
    with pytest.raises(ValueError, match="segment_id"):
        plan_kana_motor_candidate(segment_id=" ", text="あ")
    with pytest.raises(TypeError, match="text must"):
        plan_kana_motor_candidate(segment_id="s", text=None)  # type: ignore[arg-type]


def test_strict_determinism_and_no_body_solver_fields() -> None:
    one = plan_kana_motor_candidate(segment_id="s1", text="あいあい")
    two = plan_kana_motor_candidate(segment_id="s1", text="あいあい")
    assert one == two
    forbidden = {"body_id", "section_index", "waveform", "pressure_pa",
                 "source_parameter", "f0_hz", "solver_state"}
    assert forbidden.isdisjoint({f.name for f in fields(ScriptMotorCandidate)})
    assert forbidden.isdisjoint({f.name for f in fields(MotorIntentSlot)})


def test_contradictory_user_timing_fails_closed_in_inherited_solver() -> None:
    p = plan_kana_motor_candidate(segment_id="s1", text="あい")
    assert p.coordination is not None
    c = CoordinationPlan(p.coordination.constraints + (
        TimingConstraint(GestureEventRef(p.slots[1].gesture_id, GestureEvent.ONSET),
                         GestureEventRef(p.slots[0].gesture_id, GestureEvent.OFFSET),
                         0.0),
    ))
    result = compile_shared_timeline(
        gestures=tuple(
            GestureTemplate(id=slot.gesture_id, task=Task.CONSTRICT, target="oral",
                            location=0.25 if i == 0 else 0.75)
            for i, slot in enumerate(p.slots)
        ),
        coordination=c, prosody=ProsodyPlan(()), timeline=p.timeline,
    )
    assert result.status is PlanCompileStatus.INVALID
    assert result.score is None
    assert "CONTRADICTORY_TIMING" in {d.code for d in result.diagnostics}
