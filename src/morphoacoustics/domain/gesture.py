from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class Task(StrEnum):
    CONSTRICT = "CONSTRICT"
    OPEN = "OPEN"
    PHONATE = "PHONATE"
    PRESSURIZE = "PRESSURIZE"


@dataclass(frozen=True, slots=True)
class TaskParameter:
    name: str
    value: float
    unit: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("parameter name must be non-empty")
        if not isfinite(self.value):
            raise ValueError("parameter value must be finite")
        if not self.unit.strip():
            raise ValueError("parameter unit must be explicit")


@dataclass(frozen=True, slots=True)
class Gesture:
    task: Task
    onset_s: float
    offset_s: float
    target: str | None = None
    location: float | None = None
    parameters: tuple[TaskParameter, ...] = ()

    def __post_init__(self) -> None:
        if not isfinite(self.onset_s) or self.onset_s < 0.0:
            raise ValueError("onset_s must be finite and >= 0")
        if not isfinite(self.offset_s) or self.offset_s <= self.onset_s:
            raise ValueError("offset_s must be finite and greater than onset_s")
        if self.target is not None and not self.target.strip():
            raise ValueError("target must be non-empty when provided")
        if self.location is not None and not 0.0 <= self.location <= 1.0:
            raise ValueError("normalized gesture location must lie within [0, 1]")

        names = [parameter.name for parameter in self.parameters]
        if len(names) != len(set(names)):
            raise ValueError("gesture parameter names must be unique")

    def parameter(self, name: str) -> TaskParameter | None:
        return next((p for p in self.parameters if p.name == name), None)


@dataclass(frozen=True, slots=True)
class GestureScore:
    gestures: tuple[Gesture, ...]

    @property
    def duration_s(self) -> float:
        if not self.gestures:
            return 0.0
        return max(gesture.offset_s for gesture in self.gestures)
