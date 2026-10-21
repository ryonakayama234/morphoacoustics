"""SMC-2 standalone symbolic speech motor planning. Never a physical or audio API."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import StrEnum
from hashlib import sha256
from json import dumps
from math import isfinite

from morphoacoustics.integration.shared_timeline import (
    AnchorRef, CoordinationPlan, GestureEvent, GestureEventRef,
    ResolvedAnchor, ResolvedTimeline, TimingConstraint,
)

COMPILER_VERSION = "smc2-motor-plan/v0"
TIMING_POLICY = "experiment011-derived-synthetic-overlap/v0"
REPRESENTATION_KIND = "SYMBOLIC_RESEARCH_ONLY"
_KANA: dict[str, tuple[str, ...]] = {
    "あ": ("a",), "い": ("i",), "お": ("o",), "は": ("h", "a"),
    "よ": ("j", "o"), "う": ("u",), "り": ("ɾ", "i"),
    "が": ("g", "a"), "と": ("t", "o"),
}
_INTENT = {"a": "A_LIKE_INTENT", "i": "I_LIKE_INTENT"}
_BOUNDARIES = {"、", "。"}


class PlanStatus(StrEnum):
    SYMBOLIC_READY = "SYMBOLIC_READY"
    PARTIAL_MOTOR_PLAN = "PARTIAL_MOTOR_PLAN"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass(frozen=True, slots=True)
class PronunciationUnit:
    unit_id: str
    orthography: str
    provisional_phonemes: tuple[str, ...]
    start_offset: int
    end_offset: int


@dataclass(frozen=True, slots=True)
class MotorIntentNode:
    intent_id: str
    unit_id: str
    phoneme: str
    semantic_intent: str | None
    start_offset: int
    end_offset: int
    mapping_status: str


@dataclass(frozen=True, slots=True)
class IntentEdge:
    from_intent_id: str
    to_intent_id: str
    relation_kind: str = "LEXICAL_NEXT"


@dataclass(frozen=True, slots=True)
class MotorIntentGraph:
    nodes: tuple[MotorIntentNode, ...]
    edges: tuple[IntentEdge, ...]


@dataclass(frozen=True, slots=True)
class ScriptBoundary:
    symbol: str
    source_offset: int


@dataclass(frozen=True, slots=True)
class MotorDiagnostic:
    code: str
    start_offset: int
    end_offset: int
    detail: str


@dataclass(frozen=True, slots=True)
class SpeechMotorPlanResult:
    segment_id: str
    source_text: str
    pronunciation_units: tuple[PronunciationUnit, ...]
    intent_graph: MotorIntentGraph
    boundaries: tuple[ScriptBoundary, ...]
    diagnostics: tuple[MotorDiagnostic, ...]
    status: PlanStatus
    coordination: CoordinationPlan | None
    timeline: ResolvedTimeline | None
    input_digest: str
    pace: float
    compiler_version: str = COMPILER_VERSION
    timing_policy: str = TIMING_POLICY
    representation_kind: str = REPRESENTATION_KIND


def _json(data: object) -> str:
    return dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_result_json(result: SpeechMotorPlanResult) -> str:
    """Deterministic research serialization; not an adopted public JSON Schema."""
    return _json(asdict(result))


def plan_speech_motor(*, segment_id: str, text: str, pace: float = 1.0) -> SpeechMotorPlanResult:
    """Return symbolic proposals, never a GestureScore or waveform.

    Unicode source spans are Python-codepoint [start,end), never byte offsets.
    """
    if not isinstance(segment_id, str) or not segment_id.strip():
        raise ValueError("segment_id must be nonblank")
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if isinstance(pace, bool) or not isinstance(pace, (int, float)):
        raise TypeError("pace must be numeric")
    speed = float(pace)
    if not isfinite(speed) or not 0.5 <= speed <= 2.0:
        raise ValueError("pace must be finite in [0.5,2]")

    units: list[PronunciationUnit] = []
    nodes: list[MotorIntentNode] = []
    edges: list[IntentEdge] = []
    boundaries: list[ScriptBoundary] = []
    diagnostics: list[MotorDiagnostic] = []
    if not text:
        diagnostics.append(MotorDiagnostic("EMPTY_SCRIPT", 0, 0, "empty segment"))
    previous: MotorIntentNode | None = None
    for pos, char in enumerate(text):
        if char in _BOUNDARIES:
            boundaries.append(ScriptBoundary(char, pos))
            diagnostics.append(MotorDiagnostic("BOUNDARY_TIMING_UNRESOLVED", pos, pos + 1,
                                               "punctuation retained without assumed pause"))
            previous = None
            continue
        phonemes = _KANA.get(char)
        if phonemes is None:
            diagnostics.append(MotorDiagnostic("UNSUPPORTED_CHARACTER", pos, pos + 1,
                                               f"no mapping for U+{ord(char):04X}"))
            previous = None
            continue
        unit_id = f"{segment_id}.unit{len(units)}"
        units.append(PronunciationUnit(unit_id, char, phonemes, pos, pos + 1))
        for index, phoneme in enumerate(phonemes):
            symbol = _INTENT.get(phoneme)
            node = MotorIntentNode(
                f"{unit_id}.phoneme{index}.motor", unit_id, phoneme, symbol,
                pos, pos + 1, "SYMBOLIC_MAPPED" if symbol else "UNRESOLVED",
            )
            if previous is not None and (previous.unit_id == unit_id or previous.end_offset == pos):
                edges.append(IntentEdge(previous.intent_id, node.intent_id))
            nodes.append(node)
            previous = node
            if symbol is None:
                diagnostics.append(MotorDiagnostic(
                    "MISSING_MOTOR_GESTURE", pos, pos + 1,
                    f"phoneme {phoneme}: no tested symbolic motor inventory entry",
                ))

    for pos in range(len(text) - 1):
        if text[pos:pos + 2] in ("よう", "とう"):
            diagnostics.append(MotorDiagnostic(
                "CONTEXTUAL_PHONOLOGY_UNRESOLVED", pos, pos + 2,
                "long-vowel context not resolved by orthographic units",
            ))
    diagnostics.sort(key=lambda x: (x.start_offset, x.end_offset, x.code, x.detail))
    if any(x.code in ("UNSUPPORTED_CHARACTER", "EMPTY_SCRIPT") for x in diagnostics):
        status = PlanStatus.INVALID_INPUT
    elif diagnostics:
        status = PlanStatus.PARTIAL_MOTOR_PLAN
    else:
        status = PlanStatus.SYMBOLIC_READY

    coordination: CoordinationPlan | None = None
    timeline: ResolvedTimeline | None = None
    if status is PlanStatus.SYMBOLIC_READY:
        constraints: list[TimingConstraint] = []
        previous_end: GestureEventRef | None = None
        for node in nodes:
            start = GestureEventRef(node.intent_id, GestureEvent.ONSET)
            end = GestureEventRef(node.intent_id, GestureEvent.OFFSET)
            if previous_end is None:
                constraints.append(TimingConstraint(start, AnchorRef(f"{segment_id}.start"), 0.08 / speed))
            else:
                constraints.append(TimingConstraint(start, previous_end, -0.06 / speed))
            constraints.append(TimingConstraint(end, start, 0.18 / speed))
            previous_end = end
        coordination = CoordinationPlan(tuple(constraints))
        timeline = ResolvedTimeline((
            ResolvedAnchor(f"{segment_id}.start", 0.0, "smc2:synthetic"),
        ))

    input_digest = sha256(_json({
        "compiler_version": COMPILER_VERSION, "timing_policy": TIMING_POLICY,
        "segment_id": segment_id, "text": text, "pace": speed,
    }).encode("utf-8")).hexdigest()
    return SpeechMotorPlanResult(
        segment_id, text, tuple(units), MotorIntentGraph(tuple(nodes), tuple(edges)),
        tuple(boundaries), tuple(diagnostics), status, coordination, timeline,
        input_digest, speed,
    )
