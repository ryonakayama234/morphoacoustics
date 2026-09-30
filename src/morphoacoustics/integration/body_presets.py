from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json

from morphoacoustics.physical import Tract1DGeometry
from morphoacoustics.preparation import PreparedMorphology


@dataclass(frozen=True, slots=True)
class BodyPreset:
    """One immutable, versioned prepared-body preset for an integration backend."""

    preset_id: str
    revision: int
    prepared: PreparedMorphology[Tract1DGeometry]
    preparation_digest: str

    def __post_init__(self) -> None:
        if not self.preset_id.strip():
            raise ValueError("preset_id must be non-empty")
        if self.revision <= 0:
            raise ValueError("preset revision must be > 0")
        if not self.preparation_digest.startswith("sha256:"):
            raise ValueError("preparation_digest must be a sha256 digest")


@dataclass(frozen=True, slots=True)
class CharacterBodyBinding:
    """Integration-layer mapping from creative identity to one preset revision."""

    character_id: str
    preset_id: str
    preset_revision: int

    def __post_init__(self) -> None:
        if not self.character_id.strip():
            raise ValueError("character_id must be non-empty")
        if not self.preset_id.strip():
            raise ValueError("preset_id must be non-empty")
        if self.preset_revision <= 0:
            raise ValueError("preset_revision must be > 0")


class BindingStatus(StrEnum):
    BOUND = "BOUND"
    MISSING_PRESET = "MISSING_PRESET"
    REVISION_MISMATCH = "REVISION_MISMATCH"
    UNSUPPORTED_BACKEND = "UNSUPPORTED_BACKEND"


@dataclass(frozen=True, slots=True)
class BindingIssue:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class BodyBindingSnapshot:
    """Historical integration snapshot suitable for Take/result provenance."""

    character_id: str
    preset_id: str
    preset_revision: int
    backend_id: str
    preparation_digest: str

    @property
    def artifact_ref(self) -> str:
        digest = self.preparation_digest.removeprefix("sha256:")
        return (
            f"body-binding://{self.preset_id}/r{self.preset_revision}"
            f"?backend={self.backend_id}&sha256={digest}"
        )


@dataclass(frozen=True, slots=True)
class BodyBindingResolution:
    status: BindingStatus
    preset: BodyPreset | None = None
    snapshot: BodyBindingSnapshot | None = None
    issues: tuple[BindingIssue, ...] = ()

    @property
    def is_bound(self) -> bool:
        return self.status is BindingStatus.BOUND


class BodyPresetRegistry:
    """Exact-revision registry; mutable aliases are intentionally not supported."""

    def __init__(self, presets: tuple[BodyPreset, ...]) -> None:
        entries: dict[tuple[str, int], BodyPreset] = {}
        revisions_by_id: dict[str, set[int]] = {}
        for preset in presets:
            key = (preset.preset_id, preset.revision)
            if key in entries:
                raise ValueError(f"duplicate body preset revision: {key}")
            entries[key] = preset
            revisions_by_id.setdefault(preset.preset_id, set()).add(preset.revision)
        self._entries = entries
        self._revisions_by_id = {
            preset_id: frozenset(revisions)
            for preset_id, revisions in revisions_by_id.items()
        }

    def resolve(
        self,
        binding: CharacterBodyBinding,
        *,
        required_backend_id: str | None = None,
    ) -> BodyBindingResolution:
        key = (binding.preset_id, binding.preset_revision)
        preset = self._entries.get(key)
        if preset is None:
            known_revisions = self._revisions_by_id.get(binding.preset_id)
            if known_revisions:
                return BodyBindingResolution(
                    status=BindingStatus.REVISION_MISMATCH,
                    issues=(
                        BindingIssue(
                            code="BODY_PRESET_REVISION_MISMATCH",
                            message=(
                                f"body preset {binding.preset_id!r} has revisions "
                                f"{sorted(known_revisions)}, not revision {binding.preset_revision}"
                            ),
                        ),
                    ),
                )
            return BodyBindingResolution(
                status=BindingStatus.MISSING_PRESET,
                issues=(
                    BindingIssue(
                        code="BODY_PRESET_MISSING",
                        message=f"unknown body preset: {binding.preset_id!r}",
                    ),
                ),
            )

        if required_backend_id is not None and preset.prepared.backend_id != required_backend_id:
            return BodyBindingResolution(
                status=BindingStatus.UNSUPPORTED_BACKEND,
                issues=(
                    BindingIssue(
                        code="BODY_PRESET_BACKEND_UNSUPPORTED",
                        message=(
                            f"body preset {binding.preset_id!r} revision {binding.preset_revision} "
                            f"was prepared for {preset.prepared.backend_id!r}, not "
                            f"{required_backend_id!r}"
                        ),
                    ),
                ),
            )

        snapshot = BodyBindingSnapshot(
            character_id=binding.character_id,
            preset_id=preset.preset_id,
            preset_revision=preset.revision,
            backend_id=preset.prepared.backend_id,
            preparation_digest=preset.preparation_digest,
        )
        return BodyBindingResolution(
            status=BindingStatus.BOUND,
            preset=preset,
            snapshot=snapshot,
        )


def _prepared_payload(prepared: PreparedMorphology[Tract1DGeometry]) -> dict[str, object]:
    creature = prepared.creature
    geometry = prepared.rest_state
    return {
        "backend_id": prepared.backend_id,
        "creature": {
            "name": creature.name,
            "cavities": [
                {"id": cavity.id, "kind": str(cavity.kind)}
                for cavity in creature.cavities
            ],
            "connections": [
                {
                    "source_id": connection.source_id,
                    "target_id": connection.target_id,
                    "kind": connection.kind,
                }
                for connection in creature.connections
            ],
            "source_organs": [
                {
                    "id": source.id,
                    "cavity_id": source.cavity_id,
                    "kind": source.kind,
                }
                for source in creature.source_organs
            ],
            "articulators": [
                {
                    "id": articulator.id,
                    "cavity_id": articulator.cavity_id,
                    "kind": articulator.kind,
                    "reachable_start": articulator.reachable_start,
                    "reachable_end": articulator.reachable_end,
                }
                for articulator in creature.articulators
            ],
        },
        "rest_state": {
            "cavity_id": geometry.cavity_id,
            "sections": [
                {"length_m": section.length_m, "area_m2": section.area_m2}
                for section in geometry.sections
            ],
        },
        "preparation": {
            "source": prepared.provenance.source,
            "model": prepared.provenance.model,
            "notes": list(prepared.provenance.notes),
        },
    }


def preparation_digest(prepared: PreparedMorphology[Tract1DGeometry]) -> str:
    canonical = json.dumps(
        _prepared_payload(prepared),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{sha256(canonical).hexdigest()}"


def make_body_preset(
    *,
    preset_id: str,
    revision: int,
    prepared: PreparedMorphology[Tract1DGeometry],
) -> BodyPreset:
    return BodyPreset(
        preset_id=preset_id,
        revision=revision,
        prepared=prepared,
        preparation_digest=preparation_digest(prepared),
    )
