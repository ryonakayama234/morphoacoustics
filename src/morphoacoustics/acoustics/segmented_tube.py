from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from morphoacoustics.domain.geometry import TractGeometry

from .uniform_tube import UniformTube, _validated_frequencies


@dataclass(frozen=True, slots=True)
class SegmentedTube:
    """Lossless serial composition of uniform 1D tube sections."""

    sections: tuple[UniformTube, ...]

    def __post_init__(self) -> None:
        if not self.sections:
            raise ValueError("segmented tube must contain at least one section")

    @classmethod
    def from_geometry(
        cls,
        geometry: TractGeometry,
        *,
        sound_speed_m_s: float = 343.0,
        air_density_kg_m3: float = 1.21,
    ) -> SegmentedTube:
        return cls(
            sections=tuple(
                UniformTube(
                    length_m=section.length_m,
                    area_m2=section.area_m2,
                    sound_speed_m_s=sound_speed_m_s,
                    air_density_kg_m3=air_density_kg_m3,
                )
                for section in geometry.sections
            )
        )

    @property
    def total_length_m(self) -> float:
        return sum(section.length_m for section in self.sections)

    def transfer_matrix(self, frequencies_hz: npt.ArrayLike) -> np.ndarray:
        frequencies = _validated_frequencies(frequencies_hz)
        total = np.broadcast_to(
            np.eye(2, dtype=np.complex128),
            frequencies.shape + (2, 2),
        ).copy()

        for section in self.sections:
            total = np.matmul(total, section.transfer_matrix(frequencies))
        return total

    def input_impedance(
        self,
        frequencies_hz: npt.ArrayLike,
        load_impedance_pa_s_m3: complex | npt.ArrayLike = 0.0,
    ) -> np.ndarray:
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
