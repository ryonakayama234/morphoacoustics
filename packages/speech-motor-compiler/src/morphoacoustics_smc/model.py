"""Unadopted, body-neutral symbolic IR. No organ or waveform state."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

SCHEMA_VERSION = "smc3-symbolic-plan/v0"
REPRESENTATION_KIND = "SYMBOLIC_RESEARCH_ONLY"


class Event(StrEnum):
    ONSET = "ONSET"
    OFFSET = "OFFSET"


class ReportStatus(StrEnum):
    STRUCTURALLY_VALID = "STRUCTURALLY_VALID"
    INVALID = "INVALID"
    RESOLVED = "RESOLVED"


@dataclass(frozen=True, slots=True)
class PronunciationUnit:
    unit_id: str
    symbol: str  # caller-supplied hypothesis, not generated reading
    start_offset: int  # Unicode Python codepoint, inclusive
    end_offset: int  # exclusive


@dataclass(frozen=True, slots=True)
class MotorTask:
    task_id: str
    goal_kind: str  # body-independent symbolic task, not an organ location
    capability_requirements: tuple[str, ...] = ()  # unverified by SMC


@dataclass(frozen=True, slots=True)
class TaskAssociation:
    unit_id: str
    task_id: str


@dataclass(frozen=True, slots=True)
class CouplingConstraint:
    source_task_id: str
    source_event: Event
    target_task_id: str
    target_event: Event
    lag_s: Fraction  # exact synthetic event equality


@dataclass(frozen=True, slots=True)
class EventAnchor:
    task_id: str
    event: Event
    time_s: Fraction  # absolute synthetic time relative to local zero


@dataclass(frozen=True, slots=True)
class SymbolicPlan:
    segment_id: str
    source_text: str
    pronunciation_units: tuple[PronunciationUnit, ...]
    tasks: tuple[MotorTask, ...]
    associations: tuple[TaskAssociation, ...]
    couplings: tuple[CouplingConstraint, ...] = ()
    anchors: tuple[EventAnchor, ...] = ()
    schema_version: str = SCHEMA_VERSION
    representation_kind: str = REPRESENTATION_KIND


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    subject_id: str
    detail: str


@dataclass(frozen=True, slots=True)
class ValidationReport:
    status: ReportStatus
    diagnostics: tuple[Diagnostic, ...]


@dataclass(frozen=True, slots=True)
class TimingReport:
    status: ReportStatus
    # Frozen serializable triples; never a physical GestureScore.
    events: tuple[tuple[str, Event, Fraction], ...]
    diagnostics: tuple[Diagnostic, ...]
