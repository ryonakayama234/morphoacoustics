"""CC-A1 v1 schema, negative controls and immutable creator↔body binding."""
from __future__ import annotations

from copy import deepcopy
import json
import runpy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from morphoacoustics import CavityKind, CavitySpec, CreatureSpec
from morphoacoustics.integration.body_presets import BindingStatus, BodyPresetRegistry, make_body_preset
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d

ROOT = Path(__file__).resolve().parents[1] / "contracts" / "performance"

# External draft contract helper is deliberately not an installed Core module.
# Load it from the checked-out contract path without mutating sys.path or the
# adopted limited-live package source-inventory attestation.
_semantics = runpy.run_path(str(ROOT / "v1" / "semantic_validation.py"))
resolve_v1_binding = _semantics["resolve_v1_binding"]
selected_body_binding = _semantics["selected_body_binding"]
v1_input_digest = _semantics["v1_input_digest"]
v1_resolved_embodiment = _semantics["v1_resolved_embodiment"]


def document(version: str, name: str) -> dict:
    return json.loads((ROOT / version / name).read_text(encoding="utf-8"))


def registry_schemas() -> Registry:
    entries = []
    for version, names in [
        ("v0", ("common", "character", "script", "direction", "performance-request", "performance-result")),
        ("v1", ("common", "performance-request", "performance-result")),
    ]:
        for name in names:
            schema = document(version, name + ".schema.json")
            Draft202012Validator.check_schema(schema)
            entries.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(entries)


def validate(name: str, payload: dict) -> None:
    Draft202012Validator(document("v1", name + ".schema.json"), registry=registry_schemas()).validate(payload)


def request() -> dict:
    return document("v1", "examples/request.json")


def _body(name: str, area: float):
    creature = CreatureSpec(name=name, cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),))
    geom = Tract1DGeometry(
        cavity_id="oral",
        sections=(TubeSection(length_m=0.017, area_m2=area),),
    )
    return prepare_tract1d(
        creature, geom,
        provenance=PreparationProvenance(source="fixture", model="fixed-1d"),
    )


def _registry() -> BodyPresetRegistry:
    return BodyPresetRegistry((
        make_body_preset(preset_id="human-wide", revision=1, prepared=_body("wide", 3e-4)),
        make_body_preset(preset_id="human-narrow", revision=1, prepared=_body("narrow", 2e-4)),
        make_body_preset(preset_id="human-wide", revision=2, prepared=_body("wide-v2", 3.5e-4)),
    ))


def test_v1_positive_examples_compile_with_v0_creative_snapshots() -> None:
    validate("performance-request", request())
    validate("performance-result", document("v1", "examples/result.fixture.json"))
    validate("performance-result", document("v1", "examples/result.revision-mismatch.json"))
    assert request()["character"]["schema_version"] == "performance-contract/v0"
    assert request()["direction"]["schema_version"] == "performance-contract/v0"


@pytest.mark.parametrize("bad_choice", [
    {"preset_id": "human-wide", "preset_revision": "latest"},
    {"preset_id": "human-wide", "preset_revision": 0},
    {"preset_id": "human-wide", "preset_revision": True},
    {"preset_id": " ", "preset_revision": 1},
    {"preset_id": "human-wide"},
    {"preset_id": "human-wide", "preset_revision": 1, "tract_area": 0.5},
])
def test_invalid_choice_rejected_by_schema_and_semantic_gate(bad_choice: dict) -> None:
    item = request()
    item["embodiment"] = bad_choice
    with pytest.raises(Exception):
        validate("performance-request", item)
    with pytest.raises(ValueError, match="INVALID"):
        selected_body_binding(item)


def test_v1_cannot_pass_as_v0_or_inject_physics_into_character() -> None:
    q = request()
    with pytest.raises(Exception):
        Draft202012Validator(
            document("v0", "performance-request.schema.json"),
            registry=registry_schemas(),
        ).validate(q)
    q["character"]["tract_geometry"] = {"area_m2": 0.0003}
    with pytest.raises(Exception):
        validate("performance-request", q)


def test_request_digest_includes_body_revision_and_backend_version() -> None:
    first = request()
    clone = deepcopy(first)
    assert v1_input_digest(first, backend_id="fidelity0.tract1d", backend_version="v1") == v1_input_digest(
        clone, backend_id="fidelity0.tract1d", backend_version="v1"
    )
    clone["embodiment"]["preset_id"] = "human-narrow"
    assert v1_input_digest(first, backend_id="fidelity0.tract1d", backend_version="v1") != v1_input_digest(
        clone, backend_id="fidelity0.tract1d", backend_version="v1"
    )
    clone = deepcopy(first)
    clone["embodiment"]["preset_revision"] = 2
    assert v1_input_digest(first, backend_id="fidelity0.tract1d", backend_version="v1") != v1_input_digest(
        clone, backend_id="fidelity0.tract1d", backend_version="v1"
    )
    assert v1_input_digest(first, backend_id="fidelity0.tract1d", backend_version="v1") != v1_input_digest(
        first, backend_id="fidelity0.tract1d", backend_version="v2"
    )


def test_exact_binding_and_old_take_meaning_survive_catalog_update() -> None:
    q = request()
    registry = _registry()
    old, old_digest = resolve_v1_binding(q, registry, required_backend_id="fidelity0.tract1d", backend_version="v1")
    assert old.status is BindingStatus.BOUND
    old_record = v1_resolved_embodiment(old)
    assert old_record["preset_revision"] == 1
    q2 = deepcopy(q)
    q2["embodiment"]["preset_revision"] = 2
    new, new_digest = resolve_v1_binding(q2, registry, required_backend_id="fidelity0.tract1d", backend_version="v1")
    assert new.status is BindingStatus.BOUND
    assert old_record["preparation_digest"] != v1_resolved_embodiment(new)["preparation_digest"]
    assert old_digest != new_digest
    assert v1_resolved_embodiment(old) == old_record
    # Replacing catalog with an r2-only registry does not alter recorded r1 evidence.
    later = BodyPresetRegistry((make_body_preset(preset_id="human-wide", revision=2, prepared=_body("later", 4e-4)),))
    prior, _ = resolve_v1_binding(q, later, required_backend_id="fidelity0.tract1d", backend_version="v1")
    assert prior.status is BindingStatus.REVISION_MISMATCH
    assert v1_resolved_embodiment(old) == old_record


def test_missing_revision_and_unsupported_backend_have_distinct_records() -> None:
    registry = _registry()
    q = request()
    q["embodiment"]["preset_id"] = "missing"
    absent, _ = resolve_v1_binding(q, registry, required_backend_id="fidelity0.tract1d", backend_version="v1")
    assert v1_resolved_embodiment(absent) == {"status": "MISSING_PRESET"}
    q["embodiment"] = {"preset_id": "human-wide", "preset_revision": 9}
    mismatch, _ = resolve_v1_binding(q, registry, required_backend_id="fidelity0.tract1d", backend_version="v1")
    assert v1_resolved_embodiment(mismatch) == {"status": "REVISION_MISMATCH"}
    q["embodiment"]["preset_revision"] = 1
    incompatible, _ = resolve_v1_binding(q, registry, required_backend_id="nonexistent.backend", backend_version="v1")
    assert v1_resolved_embodiment(incompatible) == {"status": "UNSUPPORTED_BACKEND"}


def test_result_requires_complete_bound_provenance_but_not_for_refusal() -> None:
    result = document("v1", "examples/result.fixture.json")
    result["realization_outcome"] = "FEASIBLE"
    validate("performance-result", result)
    del result["embodiment"]["preparation_digest"]
    with pytest.raises(Exception):
        validate("performance-result", result)
    result = document("v1", "examples/result.revision-mismatch.json")
    result["realization_outcome"] = "INFEASIBLE"
    with pytest.raises(Exception):
        validate("performance-result", result)  # physical infeasibility requires bound body
    result["realization_outcome"] = "UNSUPPORTED"
    validate("performance-result", result)


def test_refusal_cannot_falsely_claim_resolved_digest() -> None:
    result = document("v1", "examples/result.revision-mismatch.json")
    result["embodiment"]["preparation_digest"] = "sha256:" + "a" * 64
    with pytest.raises(Exception):
        validate("performance-result", result)
