"""CC-B1 *experimental* rest-area BodyRevision preparation (NOT production API).

Pure, bounded preparation only: no renderer, Take, v1 registry or arbitrary
organ-graph capability is introduced. Scientific Gate A/B remain independent.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
from math import isfinite

from morphoacoustics.integration.body_presets import BodyPreset, preparation_digest
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation.protocol import PreparationProvenance, PreparedMorphology
from morphoacoustics.preparation.tract1d import TRACT1D_BACKEND_ID, prepare_tract1d

SCHEMA = "research.cc-b1.body-revision-prototype/v0"
MIN_RATIO = 0.90
MAX_RATIO = 1.10
SECTION_COUNT = 16
SECTION_LENGTH_M = 0.01


class RevisionStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    INVALID = "INVALID"
    UNSUPPORTED = "UNSUPPORTED"
    REVISION_MISMATCH = "REVISION_MISMATCH"
    NUMERICALLY_UNRESOLVED = "NUMERICALLY_UNRESOLVED"


@dataclass(frozen=True, slots=True)
class RestAreaEditIntent:
    """Absolute SI rest-area edit; never gesture area, sound gain or UI pixels."""

    base_preset_id: str
    base_revision: int
    base_preparation_digest: str
    cavity_id: str
    section_index: int
    area_m2: float


@dataclass(frozen=True, slots=True)
class BodyRevision:
    """Proposed immutable derived body, not a registered v1 BodyPreset or Take."""

    revision_id: str
    parent_preset_id: str
    parent_revision: int
    parent_preparation_digest: str
    changed_section_index: int
    original_area_m2: float
    edited_area_m2: float
    edit_digest: str
    preparation_digest: str
    prepared: PreparedMorphology[Tract1DGeometry]

    def receipt(self) -> dict[str, object]:
        """Structured serializable receipt; registry/storage are separate Gates."""
        return {
            "schema": SCHEMA,
            "revision_id": self.revision_id,
            "parent": {
                "preset_id": self.parent_preset_id,
                "revision": self.parent_revision,
                "preparation_digest": self.parent_preparation_digest,
            },
            "edit": {
                "cavity_id": self.prepared.rest_state.cavity_id,
                "section_index": self.changed_section_index,
                "previous_area_m2": self.original_area_m2,
                "new_area_m2": self.edited_area_m2,
            },
            "edit_digest": self.edit_digest,
            "preparation_digest": self.preparation_digest,
            "backend_id": self.prepared.backend_id,
        }


@dataclass(frozen=True, slots=True)
class RevisionResult:
    status: RevisionStatus
    revision: BodyRevision | None = None
    code: str | None = None
    message: str | None = None

    @property
    def accepted(self) -> bool:
        return self.status is RevisionStatus.ACCEPTED


def _refuse(status: RevisionStatus, code: str, message: str) -> RevisionResult:
    return RevisionResult(status=status, code=code, message=message)


def _canonical_sha256(payload: dict[str, object]) -> str:
    raw = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + sha256(raw).hexdigest()


def prepare_rest_area_revision(
    base: BodyPreset, intent: RestAreaEditIntent
) -> RevisionResult:
    """Prepare exactly one bounded 16-section rigid 1D rest-area intervention.

    A failed edit returns a typed refusal and never constructs a new body.
    The caller must resolve and authenticate the baseline preset independently.
    """
    if (
        not isinstance(intent.base_preset_id, str)
        or not intent.base_preset_id.strip()
        or type(intent.base_revision) is not int
        or intent.base_revision <= 0
        or not isinstance(intent.base_preparation_digest, str)
        or not intent.base_preparation_digest.startswith("sha256:")
        or not isinstance(intent.cavity_id, str)
        or not intent.cavity_id.strip()
        or type(intent.section_index) is not int
        or not isinstance(intent.area_m2, (int, float))
        or isinstance(intent.area_m2, bool)
        or not isfinite(intent.area_m2)
        or intent.area_m2 <= 0
    ):
        return _refuse(RevisionStatus.INVALID, "EDIT_INVALID", "Malformed or nonphysical SI rest-area edit")
    if (base.preset_id != intent.base_preset_id
            or base.revision != intent.base_revision
            or base.preparation_digest != intent.base_preparation_digest):
        return _refuse(RevisionStatus.REVISION_MISMATCH, "BASE_REVISION_MISMATCH", "Exact base identity/digest mismatch")
    if preparation_digest(base.prepared) != base.preparation_digest:
        return _refuse(RevisionStatus.INVALID, "BASE_TAMPERED", "Stored baseline digest fails content verification")

    geometry = base.prepared.rest_state
    if (
        base.prepared.backend_id != TRACT1D_BACKEND_ID
        or not isinstance(geometry, Tract1DGeometry)
        or geometry.cavity_id != intent.cavity_id
        or len(geometry.sections) != SECTION_COUNT
        or any(section.length_m != SECTION_LENGTH_M for section in geometry.sections)
        or len(base.prepared.creature.cavities) != 1
        or bool(base.prepared.creature.connections)
    ):
        return _refuse(RevisionStatus.UNSUPPORTED, "EDIT_CAPABILITY_UNSUPPORTED",
                       "Prototype supports only an isolated 16 x 10 mm serial 1D cavity")
    if not 0 <= intent.section_index < SECTION_COUNT:
        return _refuse(RevisionStatus.INVALID, "SECTION_INDEX_INVALID", "Section index must be 0..15")

    old = geometry.sections[intent.section_index].area_m2
    new = float(intent.area_m2)
    if new == old:
        return _refuse(RevisionStatus.INVALID, "NO_OP", "No geometry change: no new revision")
    if not MIN_RATIO <= new / old <= MAX_RATIO:
        return _refuse(RevisionStatus.UNSUPPORTED, "EDIT_RANGE_UNSUPPORTED",
                       "Rest area must be within the prototype's ±10% exploration envelope")

    edit_payload: dict[str, object] = {
        "schema": SCHEMA,
        "parent_preset_id": base.preset_id,
        "parent_revision": base.revision,
        "parent_digest": base.preparation_digest,
        "cavity_id": geometry.cavity_id,
        "section_index": intent.section_index,
        "old_area_m2": old,
        "new_area_m2": new,
    }
    edit_digest = _canonical_sha256(edit_payload)
    sections = tuple(
        TubeSection(s.length_m, new if i == intent.section_index else s.area_m2)
        for i, s in enumerate(geometry.sections)
    )
    derived = prepare_tract1d(
        base.prepared.creature,
        Tract1DGeometry(cavity_id=geometry.cavity_id, sections=sections),
        provenance=PreparationProvenance(
            source=SCHEMA,
            model="bounded-serial-tract-rest-area",
            notes=("parent=" + base.preset_id, "parent-revision=" + str(base.revision),
                   "parent-digest=" + base.preparation_digest, "edit-digest=" + edit_digest),
        ),
    )
    digest = preparation_digest(derived)
    revision = BodyRevision(
        revision_id="cc-b1-" + edit_digest.removeprefix("sha256:"),
        parent_preset_id=base.preset_id,
        parent_revision=base.revision,
        parent_preparation_digest=base.preparation_digest,
        changed_section_index=intent.section_index,
        original_area_m2=old,
        edited_area_m2=new,
        edit_digest=edit_digest,
        preparation_digest=digest,
        prepared=derived,
    )
    return RevisionResult(status=RevisionStatus.ACCEPTED, revision=revision)
