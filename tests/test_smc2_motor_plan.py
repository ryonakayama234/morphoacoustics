"""SMC-2 research tests. Synthetic numeric GestureScore is NOT phonetic evidence."""
from dataclasses import fields
import pytest
from morphoacoustics import Task
from morphoacoustics.integration.shared_timeline import (
    CoordinationPlan, GestureEvent, GestureEventRef, GestureTemplate,
    PlanCompileStatus, ProsodyPlan, TimingConstraint, compile_shared_timeline,
)
from smc2_research.motor_plan import (
    MotorIntentNode, PlanStatus, SpeechMotorPlanResult,
    canonical_result_json, plan_speech_motor,
)


def _synthetic_check(plan, coordination=None, reverse=False):
    assert plan.coordination is not None and plan.timeline is not None
    templates = tuple(GestureTemplate(
        id=node.intent_id, task=Task.CONSTRICT, target="oral",
        location=0.25 if i % 2 == 0 else 0.75,
    ) for i, node in enumerate(plan.intent_graph.nodes))
    c = plan.coordination if coordination is None else coordination
    if reverse:
        templates = tuple(reversed(templates))
        c = CoordinationPlan(tuple(reversed(c.constraints)))
    return compile_shared_timeline(
        gestures=templates, coordination=c,
        prosody=ProsodyPlan(()), timeline=plan.timeline,
    )


@pytest.mark.parametrize("text,expected", [
    ("あい", ("a", "i")), ("いあ", ("i", "a")),
    ("あいあい", ("a", "i", "a", "i")), ("いあい", ("i", "a", "i")),
])
def test_compositional_phoneme_graph(text, expected):
    p = plan_speech_motor(segment_id="s1", text=text)
    assert p.status is PlanStatus.SYMBOLIC_READY
    assert tuple(n.phoneme for n in p.intent_graph.nodes) == expected
    assert len(p.intent_graph.edges) == len(expected) - 1
    assert all(text[n.start_offset:n.end_offset] in ("あ", "い") for n in p.intent_graph.nodes)
    assert all(n.mapping_status == "SYMBOLIC_MAPPED" for n in p.intent_graph.nodes)
    assert p.coordination is not None and p.timeline is not None
    assert not hasattr(p, "score") and not hasattr(p, "audio")


def test_one_kana_can_propose_two_distinct_phonemes_without_executability():
    p = plan_speech_motor(segment_id="s", text="は")
    assert [n.phoneme for n in p.intent_graph.nodes] == ["h", "a"]
    assert len(p.intent_graph.edges) == 1
    assert p.status is PlanStatus.PARTIAL_MOTOR_PLAN and p.coordination is None


@pytest.mark.parametrize("text", ["おはよう", "ありがとう"])
def test_partial_does_not_invent_contextual_japanese_or_audio(text):
    p = plan_speech_motor(segment_id="s", text=text)
    assert p.status is PlanStatus.PARTIAL_MOTOR_PLAN
    assert len(p.pronunciation_units) == len(text)
    assert p.coordination is None and p.timeline is None
    assert {"MISSING_MOTOR_GESTURE", "CONTEXTUAL_PHONOLOGY_UNRESOLVED"}.issubset(
        {d.code for d in p.diagnostics}
    )


def test_punctuation_retained_and_no_edge_crosses_boundary():
    p = plan_speech_motor(segment_id="s", text="あ、い。")
    assert [b.source_offset for b in p.boundaries] == [1, 3]
    assert [(u.start_offset, u.end_offset) for u in p.pronunciation_units] == [(0, 1), (2, 3)]
    assert p.intent_graph.edges == ()
    assert p.coordination is None


@pytest.mark.parametrize("text", ["お早う", "ア", "あ🙂", "あ い", ""])
def test_invalid_input_never_fabricates_full_plan(text):
    p = plan_speech_motor(segment_id="s", text=text)
    assert p.status is PlanStatus.INVALID_INPUT
    assert p.coordination is None and p.timeline is None
    assert all(0 <= d.start_offset <= d.end_offset <= len(text) for d in p.diagnostics)


def test_determinism_receipt_and_no_body_schema_leakage():
    p = plan_speech_motor(segment_id="s", text="あいあい", pace=1)
    q = plan_speech_motor(segment_id="s", text="あいあい", pace=1.0)
    assert p == q and canonical_result_json(p) == canonical_result_json(q)
    assert len(p.input_digest) == 64
    assert p.input_digest != plan_speech_motor(segment_id="s", text="いああい").input_digest
    forbidden = {"body_id", "organ_id", "section_index", "area_vector",
                 "f0_hz", "solver_state", "pressure_pa", "audio", "score", "waveform"}
    assert forbidden.isdisjoint({x.name for x in fields(SpeechMotorPlanResult)})
    assert forbidden.isdisjoint({x.name for x in fields(MotorIntentNode)})
    assert p.representation_kind == "SYMBOLIC_RESEARCH_ONLY"


def test_exp011_oracle_and_order_invariance_only_in_synthetic_fixture():
    p = plan_speech_motor(segment_id="s", text="あいあい")
    a, b = _synthetic_check(p), _synthetic_check(p, reverse=True)
    assert a.status is PlanCompileStatus.VALID and b.status is PlanCompileStatus.VALID
    assert a.score is not None and b.score is not None
    assert [(g.onset_s, g.offset_s) for g in a.score.gestures] == pytest.approx(
        [(0.08, 0.26), (0.20, 0.38), (0.32, 0.50), (0.44, 0.62)]
    )
    assert a.score == b.score


@pytest.mark.parametrize("speed", [0.5, 1.0, 2.0])
def test_pace_only_scales_synthetic_time(speed):
    p = plan_speech_motor(segment_id="s", text="あい", pace=speed)
    r = _synthetic_check(p)
    assert r.score is not None
    assert [(g.onset_s, g.offset_s) for g in r.score.gestures] == pytest.approx([
        (0.08 / speed, 0.26 / speed), (0.20 / speed, 0.38 / speed)
    ])


def test_contradiction_fails_closed_in_inherited_solver():
    p = plan_speech_motor(segment_id="s", text="あい")
    assert p.coordination is not None
    a, b = p.intent_graph.nodes
    bad = CoordinationPlan(p.coordination.constraints + (TimingConstraint(
        GestureEventRef(b.intent_id, GestureEvent.ONSET),
        GestureEventRef(a.intent_id, GestureEvent.OFFSET), 0.0,
    ),))
    r = _synthetic_check(p, coordination=bad)
    assert r.status is PlanCompileStatus.INVALID and r.score is None
    assert "CONTRADICTORY_TIMING" in {x.code for x in r.diagnostics}


def test_unanchored_event_fails_closed_in_inherited_solver():
    p = plan_speech_motor(segment_id="s", text="あい")
    assert p.coordination is not None
    second = p.intent_graph.nodes[1].intent_id
    orphan = CoordinationPlan(tuple(
        c for c in p.coordination.constraints if c.subject.gesture_id != second
    ))
    r = _synthetic_check(p, coordination=orphan)
    assert r.status is PlanCompileStatus.INVALID and r.score is None
    assert "UNRESOLVED_EVENT" in {x.code for x in r.diagnostics}


@pytest.mark.parametrize("speed", [float("nan"), float("inf"), 0, -1, 0.49, 2.01])
def test_invalid_speed(speed):
    with pytest.raises(ValueError):
        plan_speech_motor(segment_id="s", text="あい", pace=speed)


@pytest.mark.parametrize("speed", [True, "1", None])
def test_speed_type(speed):
    with pytest.raises(TypeError):
        plan_speech_motor(segment_id="s", text="あい", pace=speed)


def test_bad_script_types():
    with pytest.raises(TypeError):
        plan_speech_motor(segment_id="s", text=None)
    with pytest.raises(ValueError):
        plan_speech_motor(segment_id=" ", text="あ")


def test_unknown_synthetic_gesture_reference_fails_closed():
    from morphoacoustics.integration.shared_timeline import AnchorRef
    p = plan_speech_motor(segment_id="s", text="あい")
    assert p.coordination is not None
    bad = CoordinationPlan(p.coordination.constraints + (TimingConstraint(
        GestureEventRef("missing-gesture-id", GestureEvent.ONSET),
        AnchorRef("s.start"), 0.0,
    ),))
    r = _synthetic_check(p, coordination=bad)
    assert r.status is PlanCompileStatus.INVALID and r.score is None
    assert "UNKNOWN_GESTURE" in {x.code for x in r.diagnostics}


def test_lexical_edges_are_not_physical_nonoverlap_constraints():
    p = plan_speech_motor(segment_id="s", text="あい")
    assert len(p.intent_graph.edges) == 1
    assert p.intent_graph.edges[0].relation_kind == "LEXICAL_NEXT"
    assert p.coordination is not None
    r = _synthetic_check(p)
    assert r.score is not None
    assert r.score.gestures[1].onset_s < r.score.gestures[0].offset_s


def test_unknown_between_known_units_breaks_lexical_edge():
    p = plan_speech_motor(segment_id="s", text="あ🙂い")
    assert p.status is PlanStatus.INVALID_INPUT
    assert len(p.intent_graph.nodes) == 2
    assert p.intent_graph.edges == ()
    assert [n.start_offset for n in p.intent_graph.nodes] == [0, 2]
