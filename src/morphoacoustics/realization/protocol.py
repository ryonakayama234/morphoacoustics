from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.domain.gesture import GestureScore
from morphoacoustics.domain.result import FeasibilityReport, FeasibilityStatus

StateT_co = TypeVar("StateT_co", covariant=True)


@dataclass(frozen=True, slots=True)
class RealizationResult(Generic[StateT_co]):
    """Physical realization of a gesture score at one instant in time."""

    state: StateT_co | None
    feasibility: FeasibilityReport

    def __post_init__(self) -> None:
        has_state = self.state is not None
        is_feasible = self.feasibility.status is FeasibilityStatus.FEASIBLE
        if has_state != is_feasible:
            raise ValueError(
                "FEASIBLE realization must contain state; all other statuses must not"
            )


class Realizer(Protocol[StateT_co]):
    """Translate morphology-independent tasks into backend-specific physical state."""

    def realize_snapshot(
        self,
        creature: CreatureSpec,
        score: GestureScore,
        time_s: float,
    ) -> RealizationResult[StateT_co]:
        ...
