"""Exact-version creator embodiment resolution for Performance Contract v1.

This is an integration boundary, NOT a physical solver or performance compiler.
JSON Schema validation is required at the adapter boundary; this helper separately
checks binding semantics and computes request provenance without adding runtime deps.
"""
from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import json

from morphoacoustics.integration.body_presets import (
    BindingStatus,
    BodyBindingResolution,
    BodyPresetRegistry,
    CharacterBodyBinding,
)

SCHEMA_VERSION = "performance-contract/v1"
DIGEST_ALGORITHM = "sha256-canonical-json-v1"


def _nonblank(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"INVALID:{field}:expected nonblank string")
    return value


def selected_body_binding(request: Mapping[str, object]) -> CharacterBodyBinding:
    """Refuse malformed choice; never infer a default/latest physical body."""
    if request.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("INVALID:schema_version:expected performance-contract/v1")
    character = request.get("character")
    embodiment = request.get("embodiment")
    if not isinstance(character, Mapping) or not isinstance(embodiment, Mapping):
        raise ValueError("INVALID:character_or_embodiment:expected object")
    if set(embodiment) != {"preset_id", "preset_revision"}:
        raise ValueError("INVALID:embodiment:exact preset_id and preset_revision required")
    revision = embodiment["preset_revision"]
    if type(revision) is not int or revision < 1:
        raise ValueError("INVALID:embodiment.preset_revision:expected positive integer")
    return CharacterBodyBinding(
        character_id=_nonblank(character.get("character_id"), "character.character_id"),
        preset_id=_nonblank(embodiment["preset_id"], "embodiment.preset_id"),
        preset_revision=revision,
    )


def v1_input_digest(
    request: Mapping[str, object], *, backend_id: str, backend_version: str
) -> str:
    """SHA-256 of UTF-8 sorted-key compact JSON over request and exact adapter ID/version.

    The caller supplies a JSON-schema validated request; allow_nan=False rejects
    non-JSON numeric values even when this function is called independently.
    """
    selected_body_binding(request)
    _nonblank(backend_id, "backend_id")
    _nonblank(backend_version, "backend_version")
    canonical = json.dumps(
        {"request": dict(request), "backend_id": backend_id, "backend_version": backend_version},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + sha256(canonical).hexdigest()


def resolve_v1_binding(
    request: Mapping[str, object],
    registry: BodyPresetRegistry,
    *,
    required_backend_id: str,
    backend_version: str,
) -> tuple[BodyBindingResolution, str]:
    """Resolve only an exact prevalidated preset. This executes no audio or physics."""
    binding = selected_body_binding(request)
    digest = v1_input_digest(
        request, backend_id=required_backend_id, backend_version=backend_version
    )
    return registry.resolve(binding, required_backend_id=required_backend_id), digest


def v1_resolved_embodiment(resolution: BodyBindingResolution) -> dict[str, object]:
    """Make the result's structured resolution record; no silent fallback."""
    record: dict[str, object] = {"status": resolution.status.value}
    if resolution.status is BindingStatus.BOUND:
        snapshot = resolution.snapshot
        if snapshot is None:
            raise RuntimeError("BOUND resolution requires immutable snapshot")
        record.update(
            preset_id=snapshot.preset_id,
            preset_revision=snapshot.preset_revision,
            backend_id=snapshot.backend_id,
            preparation_digest=snapshot.preparation_digest,
        )
    return record
