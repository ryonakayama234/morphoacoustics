from morphoacoustics import ArticulatorSpec, CavityKind, CavitySpec, CreatureSpec
from morphoacoustics.integration import (
    BindingStatus,
    BodyPresetRegistry,
    CharacterBodyBinding,
    make_body_preset,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d


def prepared_body(name: str, area_m2: float):
    creature = CreatureSpec(
        name=name,
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
        articulators=(
            ArticulatorSpec(
                id="tongue",
                cavity_id="oral",
                kind="tongue",
                reachable_start=0.0,
                reachable_end=1.0,
            ),
        ),
    )
    geometry = Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=0.017, area_m2=area_m2)
            for _ in range(10)
        ),
    )
    return prepare_tract1d(
        creature,
        geometry,
        provenance=PreparationProvenance(
            source="test-fixture",
            model="uniform-tract",
            notes=(f"area_m2={area_m2:g}",),
        ),
    )


def test_same_character_can_bind_to_two_distinct_bodies_without_identity_change() -> None:
    wide = make_body_preset(
        preset_id="human-wide",
        revision=1,
        prepared=prepared_body("wide-body", 3e-4),
    )
    narrow = make_body_preset(
        preset_id="human-narrow",
        revision=1,
        prepared=prepared_body("narrow-body", 2e-4),
    )
    registry = BodyPresetRegistry((wide, narrow))

    wide_result = registry.resolve(
        CharacterBodyBinding("char_mio", "human-wide", 1),
        required_backend_id="fidelity0.tract1d",
    )
    narrow_result = registry.resolve(
        CharacterBodyBinding("char_mio", "human-narrow", 1),
        required_backend_id="fidelity0.tract1d",
    )

    assert wide_result.status is BindingStatus.BOUND
    assert narrow_result.status is BindingStatus.BOUND
    assert wide_result.snapshot is not None
    assert narrow_result.snapshot is not None
    assert wide_result.snapshot.character_id == narrow_result.snapshot.character_id == "char_mio"
    assert wide_result.snapshot.preparation_digest != narrow_result.snapshot.preparation_digest


def test_exact_revision_snapshot_does_not_follow_later_preset_revision() -> None:
    revision_1 = make_body_preset(
        preset_id="mio-demo-body",
        revision=1,
        prepared=prepared_body("demo-r1", 3e-4),
    )
    revision_2 = make_body_preset(
        preset_id="mio-demo-body",
        revision=2,
        prepared=prepared_body("demo-r2", 2.5e-4),
    )
    registry = BodyPresetRegistry((revision_1, revision_2))

    old = registry.resolve(CharacterBodyBinding("char_mio", "mio-demo-body", 1))
    new = registry.resolve(CharacterBodyBinding("char_mio", "mio-demo-body", 2))

    assert old.snapshot is not None
    assert new.snapshot is not None
    assert old.snapshot.preset_revision == 1
    assert new.snapshot.preset_revision == 2
    assert old.snapshot.preparation_digest == revision_1.preparation_digest
    assert old.snapshot.preparation_digest != new.snapshot.preparation_digest


def test_missing_revision_and_backend_mismatch_are_distinct_diagnostics() -> None:
    preset = make_body_preset(
        preset_id="mio-demo-body",
        revision=2,
        prepared=prepared_body("demo", 3e-4),
    )
    registry = BodyPresetRegistry((preset,))

    missing = registry.resolve(CharacterBodyBinding("char_mio", "missing", 1))
    mismatch = registry.resolve(CharacterBodyBinding("char_mio", "mio-demo-body", 1))
    backend = registry.resolve(
        CharacterBodyBinding("char_mio", "mio-demo-body", 2),
        required_backend_id="another.backend",
    )

    assert missing.status is BindingStatus.MISSING_PRESET
    assert missing.issues[0].code == "BODY_PRESET_MISSING"
    assert mismatch.status is BindingStatus.REVISION_MISMATCH
    assert mismatch.issues[0].code == "BODY_PRESET_REVISION_MISMATCH"
    assert backend.status is BindingStatus.UNSUPPORTED_BACKEND
    assert backend.issues[0].code == "BODY_PRESET_BACKEND_UNSUPPORTED"


def test_artifact_ref_contains_exact_preset_revision_backend_and_digest() -> None:
    preset = make_body_preset(
        preset_id="mio-demo-body",
        revision=3,
        prepared=prepared_body("demo", 3e-4),
    )
    result = BodyPresetRegistry((preset,)).resolve(
        CharacterBodyBinding("char_mio", "mio-demo-body", 3)
    )

    assert result.snapshot is not None
    ref = result.snapshot.artifact_ref
    assert ref.startswith("body-binding://mio-demo-body/r3?")
    assert "backend=fidelity0.tract1d" in ref
    assert "sha256=" in ref
