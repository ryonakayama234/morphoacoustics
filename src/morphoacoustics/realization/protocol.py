from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.domain.gesture import GestureScore
from morphoacoustics.domain.result import FeasibilityReport

StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class RealizationResult(Generic[StateT]):
    """Physical realization of a gesture score at one instant in time."""

    state: StateT | None
    feasibility: FeasibilityReport


class Realizer(Protocol[StateT]):
    """Translate morphology-independent tasks into backend-specific physical state."""

    def realize_snapshot(
        self,
        creature: CreatureSpec,
        score: GestureScore,
        time_s: float,
    ) -> RealizationResult[StateT]:
        ...
