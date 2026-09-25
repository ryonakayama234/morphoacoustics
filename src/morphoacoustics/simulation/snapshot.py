from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

import numpy.typing as npt

from morphoacoustics.acoustics.protocol import AcousticBackend, AcousticResponse
from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.domain.gesture import GestureScore
from morphoacoustics.realization.protocol import RealizationResult, Realizer

StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class SnapshotSimulationResult(Generic[StateT]):
    """One-time physical realization plus an optional acoustic observation."""

    realization: RealizationResult[StateT]
    acoustics: AcousticResponse | None

    @property
    def has_acoustic_result(self) -> bool:
        return self.acoustics is not None


def simulate_snapshot(
    *,
    creature: CreatureSpec,
    score: GestureScore,
    realizer: Realizer[StateT],
    acoustic_backend: AcousticBackend[StateT],
    time_s: float,
    frequencies_hz: npt.ArrayLike,
) -> SnapshotSimulationResult[StateT]:
    """Run one causal snapshot without assuming a specific fidelity backend.

    Realization happens first. If realization is infeasible, unsupported, or
    invalid, acoustics are not evaluated. Otherwise the realized physical state
    is passed to the supplied acoustic backend.
    """

    realization = realizer.realize_snapshot(creature, score, time_s)
    if realization.state is None:
        return SnapshotSimulationResult(realization=realization, acoustics=None)

    acoustics = acoustic_backend.simulate_snapshot(realization.state, frequencies_hz)
    return SnapshotSimulationResult(realization=realization, acoustics=acoustics)
