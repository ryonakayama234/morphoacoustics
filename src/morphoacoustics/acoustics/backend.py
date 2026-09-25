from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np
import numpy.typing as npt

from morphoacoustics.domain.result import Provenance
from morphoacoustics.physical import Tract1DGeometry

from .segmented_tube import SegmentedTube


@dataclass(frozen=True, slots=True)
class ImpedanceRequest:
    """Fidelity-0 request for input impedance over a frequency grid."""

    frequencies_hz: npt.ArrayLike


@dataclass(frozen=True, slots=True)
class ImpedanceResponse:
    """Frequency-domain input-impedance observation for one tract snapshot.

    Response arrays are detached from caller-owned inputs and made read-only so
    the frequency grid cannot diverge from the impedance values after creation.
    """

    frequencies_hz: np.ndarray
    input_impedance_pa_s_m3: np.ndarray
    provenance: Provenance

    def __post_init__(self) -> None:
        frequencies = np.array(self.frequencies_hz, dtype=np.float64, copy=True)
        impedance = np.array(
            self.input_impedance_pa_s_m3,
            dtype=np.complex128,
            copy=True,
        )
        if frequencies.shape != impedance.shape:
            raise ValueError("frequency and impedance arrays must have identical shape")

        frequencies.setflags(write=False)
        impedance.setflags(write=False)
        object.__setattr__(self, "frequencies_hz", frequencies)
        object.__setattr__(self, "input_impedance_pa_s_m3", impedance)


@dataclass(frozen=True, slots=True)
class SegmentedTubeBackend:
    """Fidelity-0 acoustic backend for a rigid, lossless serial 1D tract.

    The outlet is an ideal pressure-release termination. Radiation impedance,
    losses, compliant walls, branches, sources, and waveform synthesis are not
    part of this backend's contract.
    """

    sound_speed_m_s: float = 343.0
    air_density_kg_m3: float = 1.21

    def __post_init__(self) -> None:
        if not isfinite(self.sound_speed_m_s) or self.sound_speed_m_s <= 0.0:
            raise ValueError("sound_speed_m_s must be finite and > 0")
        if not isfinite(self.air_density_kg_m3) or self.air_density_kg_m3 <= 0.0:
            raise ValueError("air_density_kg_m3 must be finite and > 0")

    def simulate_snapshot(
        self,
        state: Tract1DGeometry,
        request: ImpedanceRequest,
    ) -> ImpedanceResponse:
        tube = SegmentedTube.from_geometry(
            state,
            sound_speed_m_s=self.sound_speed_m_s,
            air_density_kg_m3=self.air_density_kg_m3,
        )
        frequencies = np.asarray(request.frequencies_hz, dtype=np.float64)
        impedance = tube.input_impedance(frequencies, load_impedance_pa_s_m3=0.0)
        return ImpedanceResponse(
            frequencies_hz=frequencies,
            input_impedance_pa_s_m3=impedance,
            provenance=Provenance(
                backend="segmented-tube-fidelity-0",
                backend_version="0.1",
                notes=(
                    "static snapshot",
                    "1D plane-wave propagation",
                    "rigid wall",
                    "lossless",
                    "serial tract",
                    "ideal pressure-release outlet",
                    "no source or waveform synthesis",
                ),
            ),
        )
