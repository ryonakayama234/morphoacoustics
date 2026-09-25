from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class TubeSection:
    """One rigid, constant-area section of a 1D serial tract."""

    length_m: float
    area_m2: float

    def __post_init__(self) -> None:
        if not isfinite(self.length_m) or self.length_m <= 0.0:
            raise ValueError("length_m must be finite and > 0")
        if not isfinite(self.area_m2) or self.area_m2 <= 0.0:
            raise ValueError("area_m2 must be finite and > 0")


@dataclass(frozen=True, slots=True)
class Tract1DGeometry:
    """Fidelity-0 physical snapshot represented by serial 1D tube sections.

    This is a backend-specific physical-state representation, not a universal
    morphology primitive. Normalized location 0 is the inlet/source side and
    1 is the outlet/radiation side. Internal section boundaries belong to the
    downstream section: intervals are [start, end), except the final section
    which also contains location 1.
    """

    cavity_id: str
    sections: tuple[TubeSection, ...]

    def __post_init__(self) -> None:
        if not self.cavity_id.strip():
            raise ValueError("cavity_id must be non-empty")
        if not self.sections:
            raise ValueError("tract geometry must contain at least one section")

    @property
    def total_length_m(self) -> float:
        return sum(section.length_m for section in self.sections)

    def axial_position_m(self, normalized_location: float) -> float:
        """Convert a normalized axial location in [0, 1] to metres."""

        self._validate_normalized_location(normalized_location)
        return normalized_location * self.total_length_m

    def section_index_at(self, normalized_location: float) -> int:
        """Return the section containing a normalized axial location in [0, 1]."""

        self._validate_normalized_location(normalized_location)
        if normalized_location == 1.0:
            return len(self.sections) - 1

        target_m = normalized_location * self.total_length_m
        cumulative_m = 0.0
        for index, section in enumerate(self.sections):
            cumulative_m += section.length_m
            if target_m < cumulative_m:
                return index
        return len(self.sections) - 1

    @staticmethod
    def _validate_normalized_location(normalized_location: float) -> None:
        if not isfinite(normalized_location) or not 0.0 <= normalized_location <= 1.0:
            raise ValueError("normalized_location must lie within [0, 1]")
