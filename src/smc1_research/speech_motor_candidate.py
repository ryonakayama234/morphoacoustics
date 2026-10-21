"""SMC-1 exploratory kana-to-motor-intent planning; never an audio/physical API.

This module produces immutable pronunciation *candidates* and symbolic intents,
not body-executable GestureScores. Do not infer physical feasibility from READY.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from morphoacoustics.integration.shared_timeline import (
    AnchorRef,
    CoordinationPlan,
    GestureEvent,
    GestureEventRef,
    ResolvedAnchor,
    ResolvedTimeline,
    TimingConstraint,
)

CANDIDATE_VERSION = "smc1-kana-motor-candidate/v0"
TIMING_POLICY = "experiment011-derived-synthetic-overlap/v0"
# Orthographic kana decoding only: not a validated contextual pronunciation model.
_KANA_PHONEMES: dict[str, tuple[str, ...]] = {
    "あ": ("a",), "い": ("i",), "お": ("o",),
    "は": ("h", "a"), "よ": ("j", "o"), "う": ("u",),
    "り": ("ɾ", "i"), "が": ("g", "a"), "と": ("t", "o"),
}
# These are *symbolic* task-intent labels, NOT calibrated physical Gesture templates.
_SYMBOLIC_INTENTS = {"あ": "A_LIKE_INTENT", "い": "I_LIKE_INTENT"}
_BOUNDARIES = {"、", "。"}


class CandidateStatus(StrEnum):
    COORDINATION_RESEARCH_READY = "COORDINATION_RESEARCH_READY"
    PARTIAL_MOTOR_PLAN = "PARTIAL_MOTOR_PLAN"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass(frozen=True, slots=True)
class PronunciationUnit:
    unit_id: str
    kana: str
    phonemes: tuple[str, ...]
    source_offset: int


@dataclass(frozen=True, slots=True)
class MotorIntentSlot:
    unit_id: str
    gesture_id: str
    symbolic_intent: str | None
    source_offset: int


@dataclass(frozen=True, slots=True)
class ScriptBoundary:
    symbol: str
    source_offset: int


@dataclass(frozen=True, slots=True)
class MotorDiagnostic:
    code: str
    source_offset: int
    detail: str


@dataclass(frozen=True, slots=True)
class ScriptMotorCandidate:
    segment_id: str
    source_text: str
    units: tuple[PronunciationUnit, ...]
    slots: tuple[MotorIntentSlot, ...]
    boundaries: tuple[ScriptBoundary, ...]
    diagnostics: tuple[MotorDiagnostic, ...]
    status: CandidateStatus
    coordination: CoordinationPlan | None
    timeline: ResolvedTimeline | None
    compiler_version: str = CANDIDATE_VERSION
    timing_policy: str | None = None


def plan_kana_motor_candidate(*, segment_id: str, text: str) -> ScriptMotorCandidate:
    """Decode a *small* hiragana subset, retaining every undecidable position.

    The optional CoordinationPlan is a synthetic timing-fixture candidate only.
    It cannot be fed to a body without an independently reviewed Gesture mapping.
    """
    if not segment_id.strip():
        raise ValueError("segment_id must not be blank")
    if not isinstance(text, str):
        raise TypeError("text must be str")
    units: list[PronunciationUnit] = []
    slots: list[MotorIntentSlot] = []
    boundaries: list[ScriptBoundary] = []
    diagnostics: list[MotorDiagnostic] = []

    if not text:
        diagnostics.append(MotorDiagnostic("EMPTY_SCRIPT", 0, "empty segment"))
    for offset, char in enumerate(text):
        if char in _BOUNDARIES:
            boundaries.append(ScriptBoundary(char, offset))
            diagnostics.append(MotorDiagnostic(
                "BOUNDARY_TIMING_UNRESOLVED", offset,
                "punctuation retained; pause and prosody not inferred",
            ))
            continue
        phonemes = _KANA_PHONEMES.get(char)
        if phonemes is None:
            diagnostics.append(MotorDiagnostic(
                "UNSUPPORTED_CHARACTER", offset,
                f"no explicit orthographic mapping for U+{ord(char):04X}",
            ))
            continue
        index = len(units)
        unit_id = f"{segment_id}.unit{index}"
        units.append(PronunciationUnit(unit_id, char, phonemes, offset))
        intent = _SYMBOLIC_INTENTS.get(char)
        slots.append(MotorIntentSlot(unit_id, f"{unit_id}.motor", intent, offset))
        if intent is None:
            diagnostics.append(MotorDiagnostic(
                "MISSING_MOTOR_GESTURE", offset,
                "no validated body-independent motor primitive for this kana unit",
            ))

    # A contextual vowel sequence cannot be inferred by concatenating
    # single-kana phonemes. Keep the uncertainty instead of inventing /o:/.
    for index in range(len(text) - 1):
        if text[index:index + 2] in ("よう", "とう"):
            diagnostics.append(MotorDiagnostic(
                "CONTEXTUAL_PHONOLOGY_UNRESOLVED", index,
                "orthographic phonemes are not a validated long-vowel analysis",
            ))

    invalid = any(
        item.code in ("EMPTY_SCRIPT", "UNSUPPORTED_CHARACTER")
        for item in diagnostics
    )
    if invalid:
        status = CandidateStatus.INVALID_INPUT
    elif diagnostics:
        status = CandidateStatus.PARTIAL_MOTOR_PLAN
    else:
        status = CandidateStatus.COORDINATION_RESEARCH_READY

    coordination: CoordinationPlan | None = None
    timeline: ResolvedTimeline | None = None
    timing_policy: str | None = None
    if status is CandidateStatus.COORDINATION_RESEARCH_READY:
        constraints: list[TimingConstraint] = []
        previous: GestureEventRef | None = None
        for index, slot in enumerate(slots):
            onset = GestureEventRef(slot.gesture_id, GestureEvent.ONSET)
            end_event = GestureEventRef(slot.gesture_id, GestureEvent.OFFSET)
            if index == 0:
                constraints.append(
                    TimingConstraint(onset, AnchorRef(f"{segment_id}.start"), 0.08)
                )
            else:
                assert previous is not None
                # Derived from Exp011 two-CONSTRICT timing *as a numeric fixture*.
                # Not a phonetic assertion about /a/ or /i/.
                constraints.append(TimingConstraint(onset, previous, -0.06))
            constraints.append(TimingConstraint(end_event, onset, 0.18))
            previous = end_event
        coordination = CoordinationPlan(tuple(constraints))
        timeline = ResolvedTimeline(
            (ResolvedAnchor(f"{segment_id}.start", 0.0, "smc1:synthetic"),)
        )
        timing_policy = TIMING_POLICY

    return ScriptMotorCandidate(
        segment_id=segment_id,
        source_text=text,
        units=tuple(units),
        slots=tuple(slots),
        boundaries=tuple(boundaries),
        diagnostics=tuple(diagnostics),
        status=status,
        coordination=coordination,
        timeline=timeline,
        timing_policy=timing_policy,
    )
