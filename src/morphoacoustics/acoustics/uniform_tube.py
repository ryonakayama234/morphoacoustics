"""Lossless one-dimensional acoustics for a uniform rigid tube.

This module is the fidelity-0 acoustic primitive.  It intentionally models a
stationary, rigid-walled, constant-area tube with plane-wave propagation and no
losses.  The pressure/volume-velocity transfer matrix uses the ``exp(+jωt)``
Fourier convention and maps the outlet state to the inlet state.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True, slots=True)
class UniformTube:
    """A lossless uniform acoustic tube under the fidelity-0 assumptions."""

    length_m: float
    area_m2: float
    sound_speed_m_s: float = 343.0
    air_density_kg_m3: float = 1.21

    def __post_init__(self) -> None:
        _require_positive_finite("length_m", self.length_m)
        _require_positive_finite("area_m2", self.area_m2)
        _require_positive_finite("sound_speed_m_s", self.sound_speed_m_s)
        _require_positive_finite("air_density_kg_m3", self.air_density_kg_m3)

    @property
    def characteristic_impedance_pa_s_m3(self) -> float:
        """Return characteristic impedance ``rho * c / A`` for volume flow."""

        return self.air_density_kg_m3 * self.sound_speed_m_s / self.area_m2

    def quarter_wave_resonances_hz(self, count: int) -> np.ndarray:
        """Return ideal closed-open resonance frequencies.

        The glottal end is treated as acoustically closed and the outlet as an
        ideal pressure-release boundary.  Under those assumptions the modes
        occur at odd multiples of ``c / (4L)``.
        """

        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ValueError("count must be a positive integer")

        mode_index = np.arange(count, dtype=np.float64)
        odd_harmonics = 2.0 * mode_index + 1.0
        return odd_harmonics * self.sound_speed_m_s / (4.0 * self.length_m)

    def transfer_matrix(self, frequencies_hz: npt.ArrayLike) -> np.ndarray:
        """Return the pressure/volume-velocity transfer matrix.

        For each frequency, the returned matrix ``T`` satisfies

        ``[p_in, U_in]^T = T [p_out, U_out]^T``.

        Scalar input returns shape ``(2, 2)``.  Array input with shape ``S``
        returns shape ``S + (2, 2)``.
        """

        frequencies = _validated_frequencies(frequencies_hz)
        phase = 2.0 * pi * frequencies * self.length_m / self.sound_speed_m_s
        cos_phase = np.cos(phase)
        sin_phase = np.sin(phase)
        zc = self.characteristic_impedance_pa_s_m3

        matrix = np.empty(frequencies.shape + (2, 2), dtype=np.complex128)
        matrix[..., 0, 0] = cos_phase
        matrix[..., 0, 1] = 1j * zc * sin_phase
        matrix[..., 1, 0] = 1j * sin_phase / zc
        matrix[..., 1, 1] = cos_phase
        return matrix

    def input_impedance(
        self,
        frequencies_hz: npt.ArrayLike,
        load_impedance_pa_s_m3: complex | npt.ArrayLike = 0.0,
    ) -> np.ndarray:
        """Return inlet impedance for a load applied at the tube outlet.

        ``load_impedance_pa_s_m3=0`` is the fidelity-0 ideal pressure-release
        termination.  Finite array-valued loads are broadcast against the
        frequency array.
        """

        frequencies = _validated_frequencies(frequencies_hz)
        load = np.asarray(load_impedance_pa_s_m3, dtype=np.complex128)
        if np.any(~np.isfinite(load.real)) or np.any(~np.isfinite(load.imag)):
            raise ValueError("load impedance must be finite")

        matrix = self.transfer_matrix(frequencies)
        a = matrix[..., 0, 0]
        b = matrix[..., 0, 1]
        c = matrix[..., 1, 0]
        d = matrix[..., 1, 1]

        numerator = a * load + b
        denominator = c * load + d
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.asarray(numerator / denominator)


def _require_positive_finite(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and > 0")


def _validated_frequencies(frequencies_hz: npt.ArrayLike) -> np.ndarray:
    frequencies = np.asarray(frequencies_hz, dtype=np.float64)
    if np.any(~np.isfinite(frequencies)):
        raise ValueError("frequencies_hz must be finite")
    if np.any(frequencies < 0.0):
        raise ValueError("frequencies_hz must be >= 0")
    return frequencies
