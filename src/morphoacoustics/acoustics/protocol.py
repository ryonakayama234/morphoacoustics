from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

import numpy as np
import numpy.typing as npt

from morphoacoustics.domain.result import Provenance

StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class AcousticResponse:
    """Frequency-domain acoustic observation for one physical snapshot."""

    frequencies_hz: np.ndarray
    input_impedance_pa_s_m3: np.ndarray
    provenance: Provenance

    def __post_init__(self) -> None:
        if self.frequencies_hz.shape != self.input_impedance_pa_s_m3.shape:
            raise ValueError("frequency and impedance arrays must have identical shape")


class AcousticBackend(Protocol[StateT]):
    """Evaluate acoustics for one backend-specific physical state."""

    def simulate_snapshot(
        self,
        state: StateT,
        frequencies_hz: npt.ArrayLike,
    ) -> AcousticResponse:
        ...
