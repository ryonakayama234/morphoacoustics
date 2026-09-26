import pytest

from morphoacoustics import (
    CavityConnection,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    PreparationProvenance,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import TRACT1D_BACKEND_ID, prepare_tract1d


def _geometry(cavity_id: str = "oral") -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id=cavity_id,
        sections=(TubeSection(length_m=0.17, area_m2=3e-4),),
    )


def test_prepare_tract1d_binds_creature_state_and_provenance() -> None:
    creature = CreatureSpec(
        name="human-prototype",
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
    )
    provenance = PreparationProvenance(
        source="manual",
        model="uniform-tract-v0",
        notes=("17 cm reference geometry",),
    )

    prepared = prepare_tract1d(
        creature,
        _geometry(),
        provenance=provenance,
    )

    assert prepared.creature is creature
    assert prepared.rest_state == _geometry()
    assert prepared.backend_id == TRACT1D_BACKEND_ID
    assert prepared.provenance == provenance


def test_prepare_tract1d_rejects_geometry_for_unknown_cavity() -> None:
    creature = CreatureSpec(
        name="human-prototype",
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
    )

    with pytest.raises(ValueError, match="is not in creature"):
        prepare_tract1d(creature, _geometry(cavity_id="nasal"))


def test_preparation_does_not_hide_backend_capability_limits() -> None:
    creature = CreatureSpec(
        name="branched",
        cavities=(
            CavitySpec(id="oral", kind=CavityKind.ORAL),
            CavitySpec(id="nasal", kind=CavityKind.NASAL),
        ),
        connections=(CavityConnection(source_id="oral", target_id="nasal"),),
    )

    prepared = prepare_tract1d(creature, _geometry())

    assert prepared.creature.connections == creature.connections
