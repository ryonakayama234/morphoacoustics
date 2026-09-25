from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from morphoacoustics.acoustics.segmented_tube import SegmentedTube
from morphoacoustics.domain.creature import CreatureSpec
from morphoacoustics.domain.gesture import GestureScore
from morphoacoustics.realization.protocol import RealizationResult, Realizer


@dataclass(frozen=True, slots=True)
class AcousticSnapshotResult:
    """One-time geometry realization plus its fidelity-0 acoustic response."""

    realization: RealizationResult
    frequencies_hz: np.ndarray | None
    input_impedance_pa_s_m3: np.ndarray | None

    @property
    def has_acoustic_result(self) -> bool:
        return self.input_impedance_pa_s_m3 is not None


def simulate_snapshot(
    *,
    creature: CreatureSpec,
    score: GestureScore,
    realizer: Realizer,
    time_s: float,
    frequencies_hz: npt.ArrayLike,
) -> AcousticSnapshotResult:
    """Run the first complete causal slice without synthesizing a waveform.

    If physical realization fails or is unsupported, acoustics are not run.
    """

    realization = realizer.realize_snapshot(creature, score, time_s)
    if realization.geometry is None:
        return AcousticSnapshotResult(
            realization=realization,
            frequencies_hz=None,
            input_impedance_pa_s_m3=None,
        )

    tube = SegmentedTube.from_geometry(realization.geometry)
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    impedance = tube.input_impedance(frequencies)
    return AcousticSnapshotResult(
        realization=realization,
        frequencies_hz=frequencies,
        input_impedance_pa_s_m3=impedance,
    )
