from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CavityKind(StrEnum):
    ORAL = "oral"
    NASAL = "nasal"
    PHARYNGEAL = "pharyngeal"
    TRACHEAL = "tracheal"
    AIR_SAC = "air_sac"
    GENERIC = "generic"


@dataclass(frozen=True, slots=True)
class CavitySpec:
    id: str
    kind: CavityKind = CavityKind.GENERIC

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("cavity id must be non-empty")


@dataclass(frozen=True, slots=True)
class CavityConnection:
    source_id: str
    target_id: str
    kind: str = "junction"

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.target_id.strip():
            raise ValueError("connection endpoints must be non-empty")
        if self.source_id == self.target_id:
            raise ValueError("a cavity cannot connect to itself")
        if not self.kind.strip():
            raise ValueError("connection kind must be non-empty")


@dataclass(frozen=True, slots=True)
class SourceOrganSpec:
    id: str
    cavity_id: str
    kind: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("source organ id must be non-empty")
        if not self.cavity_id.strip():
            raise ValueError("source organ cavity_id must be non-empty")
        if not self.kind.strip():
            raise ValueError("source organ kind must be non-empty")


@dataclass(frozen=True, slots=True)
class ArticulatorSpec:
    id: str
    cavity_id: str
    kind: str
    reachable_start: float = 0.0
    reachable_end: float = 1.0

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("articulator id must be non-empty")
        if not self.cavity_id.strip():
            raise ValueError("articulator cavity_id must be non-empty")
        if not self.kind.strip():
            raise ValueError("articulator kind must be non-empty")
        if not 0.0 <= self.reachable_start <= self.reachable_end <= 1.0:
            raise ValueError("reachable interval must lie within [0, 1]")


@dataclass(frozen=True, slots=True)
class CreatureSpec:
    name: str
    cavities: tuple[CavitySpec, ...]
    connections: tuple[CavityConnection, ...] = ()
    source_organs: tuple[SourceOrganSpec, ...] = ()
    articulators: tuple[ArticulatorSpec, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("creature name must be non-empty")
        if not self.cavities:
            raise ValueError("a creature must contain at least one cavity")

        cavity_ids = [cavity.id for cavity in self.cavities]
        if len(cavity_ids) != len(set(cavity_ids)):
            raise ValueError("cavity ids must be unique")

        known_cavities = set(cavity_ids)

        for connection in self.connections:
            if connection.source_id not in known_cavities:
                raise ValueError(f"unknown source cavity: {connection.source_id}")
            if connection.target_id not in known_cavities:
                raise ValueError(f"unknown target cavity: {connection.target_id}")

        source_ids = [source.id for source in self.source_organs]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source organ ids must be unique")
        for source in self.source_organs:
            if source.cavity_id not in known_cavities:
                raise ValueError(f"unknown source-organ cavity: {source.cavity_id}")

        articulator_ids = [articulator.id for articulator in self.articulators]
        if len(articulator_ids) != len(set(articulator_ids)):
            raise ValueError("articulator ids must be unique")
        for articulator in self.articulators:
            if articulator.cavity_id not in known_cavities:
                raise ValueError(f"unknown articulator cavity: {articulator.cavity_id}")
