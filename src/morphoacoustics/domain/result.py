from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class FeasibilityStatus(StrEnum):
    NOT_EVALUATED = "NOT_EVALUATED"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    UNSUPPORTED = "UNSUPPORTED"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class FeasibilityIssue:
    code: str
    message: str
    gesture_index: int | None = None

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("issue code must be non-empty")
        if not self.message.strip():
            raise ValueError("issue message must be non-empty")
        if self.gesture_index is not None and self.gesture_index < 0:
            raise ValueError("gesture_index must be >= 0")


@dataclass(frozen=True, slots=True)
class FeasibilityReport:
    status: FeasibilityStatus
    issues: tuple[FeasibilityIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class TraceSeries:
    name: str
    sample_rate_hz: float
    values: tuple[float, ...]
    unit: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("trace name must be non-empty")
        if not isfinite(self.sample_rate_hz) or self.sample_rate_hz <= 0.0:
            raise ValueError("trace sample_rate_hz must be finite and > 0")
        if not self.unit.strip():
            raise ValueError("trace unit must be explicit")


@dataclass(frozen=True, slots=True)
class Provenance:
    backend: str
    backend_version: str | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.backend.strip():
            raise ValueError("backend must be non-empty")


@dataclass(frozen=True, slots=True)
class SimulationResult:
    waveform: tuple[float, ...]
    sample_rate_hz: int
    feasibility: FeasibilityReport
    traces: tuple[TraceSeries, ...] = ()
    provenance: Provenance | None = None

    def __post_init__(self) -> None:
        if self.sample_rate_hz <= 0:
            raise ValueError("sample_rate_hz must be > 0")
