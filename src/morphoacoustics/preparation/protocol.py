from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from morphoacoustics.domain.creature import CreatureSpec

PreparedStateT_co = TypeVar("PreparedStateT_co", covariant=True)


@dataclass(frozen=True, slots=True)
class PreparationProvenance:
    """Describe how a backend-specific rest state was obtained."""

    source: str
    model: str | None = None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("preparation source must be non-empty")
        if self.model is not None and not self.model.strip():
            raise ValueError("preparation model must be non-empty when provided")
        if any(not note.strip() for note in self.notes):
            raise ValueError("preparation notes must not contain empty entries")


@dataclass(frozen=True, slots=True)
class PreparedMorphology(Generic[PreparedStateT_co]):
    """Explicit binding between a CreatureSpec and a backend-specific rest state.

    The binding makes solver preparation inspectable without moving backend-
    specific geometry into the universal CreatureSpec schema.  Preparation
    provenance records how the numerical representation was obtained; it does
    not claim that the rest state can already be derived from CreatureSpec.
    """

    creature: CreatureSpec
    rest_state: PreparedStateT_co
    backend_id: str
    provenance: PreparationProvenance

    def __post_init__(self) -> None:
        if not self.backend_id.strip():
            raise ValueError("backend_id must be non-empty")
