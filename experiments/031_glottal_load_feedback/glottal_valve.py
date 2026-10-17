"""Prescribed glottal AREA trajectory; never equate it with an LF flow pulse."""
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PrescribedValve:
    frequency_hz: float = 100.0
    open_quotient: float = 0.65
    max_area_m2: float = 3.0e-5
    subglottal_pressure_pa: float = 800.0

    def __post_init__(self) -> None:
        for value in (
            self.frequency_hz,
            self.open_quotient,
            self.max_area_m2,
            self.subglottal_pressure_pa,
        ):
            if not math.isfinite(value):
                raise ValueError("valve controls must be finite")
        if self.frequency_hz <= 0 or not 0 < self.open_quotient <= 1:
            raise ValueError("frequency must be positive and open quotient in (0,1]")
        if self.max_area_m2 <= 0:
            raise ValueError("maximum glottal area must be positive")

    def area_at(self, time_s: float) -> float:
        if not math.isfinite(time_s) or time_s < 0:
            raise ValueError("time must be finite and nonnegative")
        phase = (time_s * self.frequency_hz) % 1.0
        if phase <= 0.0 or phase >= self.open_quotient:
            return 0.0
        s = math.sin(math.pi * phase / self.open_quotient)
        return self.max_area_m2 * s * s
