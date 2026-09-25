from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.domain.geometry import TractGeometry
from morphoacoustics.domain.gesture import GestureScore
from morphoacoustics.domain.result import FeasibilityReport


@dataclass(frozen=True, slots=True)
class RealizationResult:
    """Physical realization of a gesture score at one instant in time."""

    geometry: TractGeometry | None
    feasibility: FeasibilityReport


class Realizer(Protocol):
    """Translate morphology-independent tasks into body-specific physical state."""

    def realize_snapshot(
        self,
        creature: CreatureSpec,
        score: GestureScore,
        time_s: float,
    ) -> RealizationResult:
        ...
