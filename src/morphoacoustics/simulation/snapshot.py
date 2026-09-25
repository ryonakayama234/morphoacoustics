from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from morphoacoustics.acoustics.protocol import AcousticBackend
from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.domain.gesture import GestureScore
from morphoacoustics.domain.result import FeasibilityStatus
from morphoacoustics.realization.protocol import RealizationResult, Realizer

StateT = TypeVar("StateT")
RequestT = TypeVar("RequestT")
ObservationT = TypeVar("ObservationT")


@dataclass(frozen=True, slots=True)
class SnapshotSimulationResult(Generic[StateT, ObservationT]):
    """One-time physical realization plus an optional acoustic observation."""

    realization: RealizationResult[StateT]
    acoustics: ObservationT | None

    @property
    def has_acoustic_result(self) -> bool:
        return self.acoustics is not None


def simulate_snapshot(
    *,
    creature: CreatureSpec,
    score: GestureScore,
    realizer: Realizer[StateT],
    acoustic_backend: AcousticBackend[StateT, RequestT, ObservationT],
    acoustic_request: RequestT,
    time_s: float,
) -> SnapshotSimulationResult[StateT, ObservationT]:
    """Run one causal snapshot without assuming a specific fidelity backend.

    Realization happens first. If realization is infeasible, unsupported, or
    invalid, acoustics are not evaluated. Otherwise the realized physical state
    and opaque acoustic request are passed to the supplied backend.
    """

    realization = realizer.realize_snapshot(creature, score, time_s)
    if realization.feasibility.status is not FeasibilityStatus.FEASIBLE:
        return SnapshotSimulationResult(realization=realization, acoustics=None)

    state = realization.state
    if state is None:  # Defensive guard; RealizationResult enforces this invariant.
        raise RuntimeError("FEASIBLE realization must contain a physical state")

    acoustics = acoustic_backend.simulate_snapshot(
        state,
        acoustic_request,
    )
    return SnapshotSimulationResult(realization=realization, acoustics=acoustics)
