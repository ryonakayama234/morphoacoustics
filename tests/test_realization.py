from itertools import permutations

import pytest

from morphoacoustics import (
    ArticulatorSpec,
    CavityConnection,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    FeasibilityReport,
    FeasibilityStatus,
    Gesture,
    GestureScore,
    Task,
    TaskParameter,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparedMorphology, prepare_tract1d
from morphoacoustics.realization import RealizationResult, Tract1DRealizer


def _creature() -> CreatureSpec:
    return CreatureSpec(
        name="simple-human",
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
        articulators=(
            ArticulatorSpec(
                id="tongue",
                cavity_id="oral",
                kind="tongue",
                reachable_start=0.30,
                reachable_end=0.80,
            ),
        ),
    )


def _rest_geometry(cavity_id: str = "oral") -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id=cavity_id,
        sections=tuple(
            TubeSection(length_m=0.017, area_m2=3e-4)
            for _ in range(10)
        ),
    )


def _prepared(
    creature: CreatureSpec | None = None,
    geometry: Tract1DGeometry | None = None,
) -> PreparedMorphology[Tract1DGeometry]:
    return prepare_tract1d(
        creature or _creature(),
        geometry or _rest_geometry(),
    )


def _constriction(location: float, area_m2: float = 2e-5) -> Gesture:
    return Gesture(
        task=Task.CONSTRICT,
        onset_s=0.10,
        offset_s=0.30,
        target="oral",
        location=location,
        parameters=(TaskParameter("target_area", area_m2, "m2"),),
    )


def test_active_constriction_changes_body_specific_geometry() -> None:
    prepared = _prepared()
    result = Tract1DRealizer().realize_snapshot(
        prepared,
        GestureScore((_constriction(0.65),)),
        time_s=0.20,
    )

    assert result.feasibility.status is FeasibilityStatus.FEASIBLE
    assert result.state is not None
    assert result.state.sections[6].area_m2 == 2e-5
    assert result.state.sections[5].area_m2 == 3e-4
    assert result.state.sections[7].area_m2 == 3e-4


def test_inactive_gesture_leaves_rest_geometry_unchanged() -> None:
    rest = _rest_geometry()
    result = Tract1DRealizer().realize_snapshot(
        _prepared(geometry=rest),
        GestureScore((_constriction(0.65),)),
        time_s=0.05,
    )

    assert result.feasibility.status is FeasibilityStatus.FEASIBLE
    assert result.state == rest


def test_unreachable_constriction_is_explicitly_infeasible() -> None:
    result = Tract1DRealizer().realize_snapshot(
        _prepared(),
        GestureScore((_constriction(0.95),)),
        time_s=0.20,
    )

    assert result.feasibility.status is FeasibilityStatus.INFEASIBLE
    assert result.state is None
    assert result.feasibility.issues[0].code == "LOCATION_UNREACHABLE"


def test_active_unsupported_task_is_reported_not_approximated() -> None:
    phonate = Gesture(
        task=Task.PHONATE,
        onset_s=0.0,
        offset_s=0.2,
    )
    result = Tract1DRealizer().realize_snapshot(
        _prepared(),
        GestureScore((phonate,)),
        time_s=0.1,
    )

    assert result.feasibility.status is FeasibilityStatus.UNSUPPORTED
    assert result.state is None
    assert result.feasibility.issues[0].code == "TASK_UNSUPPORTED"


def test_prepared_backend_mismatch_is_invalid() -> None:
    prepared = _prepared()
    mismatched = PreparedMorphology(
        creature=prepared.creature,
        rest_state=prepared.rest_state,
        backend_id="other.backend",
        provenance=prepared.provenance,
    )

    result = Tract1DRealizer().realize_snapshot(
        mismatched,
        GestureScore(()),
        time_s=0.0,
    )

    assert result.feasibility.status is FeasibilityStatus.INVALID
    assert result.state is None
    assert result.feasibility.issues[0].code == "PREPARED_BACKEND_MISMATCH"


def test_invalid_target_area_is_not_reported_as_physical_infeasibility() -> None:
    result = Tract1DRealizer().realize_snapshot(
        _prepared(),
        GestureScore((_constriction(0.65, area_m2=-1e-5),)),
        time_s=0.20,
    )

    assert result.feasibility.status is FeasibilityStatus.INVALID
    assert result.state is None
    assert result.feasibility.issues[0].code == "NONPOSITIVE_TARGET_AREA"


def test_invalid_request_takes_precedence_over_unreachable_morphology() -> None:
    result = Tract1DRealizer().realize_snapshot(
        _prepared(),
        GestureScore((_constriction(0.95, area_m2=-1e-5),)),
        time_s=0.20,
    )

    assert result.feasibility.status is FeasibilityStatus.INVALID
    assert result.state is None
    assert result.feasibility.issues[0].code == "NONPOSITIVE_TARGET_AREA"


def test_failure_classification_is_independent_of_gesture_order() -> None:
    unreachable = _constriction(0.95)
    unsupported = Gesture(task=Task.PHONATE, onset_s=0.10, offset_s=0.30)
    invalid = _constriction(0.65, area_m2=-1e-5)
    realizer = Tract1DRealizer()
    prepared = _prepared()

    for gesture_order in permutations((unreachable, unsupported, invalid)):
        result = realizer.realize_snapshot(
            prepared, GestureScore(gesture_order), time_s=0.20
        )
        assert result.feasibility.status is FeasibilityStatus.INVALID
        assert result.state is None
        assert [issue.code for issue in result.feasibility.issues] == [
            "NONPOSITIVE_TARGET_AREA"
        ]

    for gesture_order in permutations((unreachable, unsupported)):
        result = realizer.realize_snapshot(
            prepared, GestureScore(gesture_order), time_s=0.20
        )
        assert result.feasibility.status is FeasibilityStatus.UNSUPPORTED
        assert result.state is None
        assert [issue.code for issue in result.feasibility.issues] == ["TASK_UNSUPPORTED"]


def test_connected_cavity_is_explicitly_unsupported_by_fidelity0() -> None:
    creature = CreatureSpec(
        name="branched",
        cavities=(
            CavitySpec(id="oral", kind=CavityKind.ORAL),
            CavitySpec(id="nasal", kind=CavityKind.NASAL),
        ),
        connections=(CavityConnection(source_id="oral", target_id="nasal"),),
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

    result = Tract1DRealizer().realize_snapshot(
        _prepared(creature=creature),
        GestureScore(()),
        time_s=0.0,
    )

    assert result.feasibility.status is FeasibilityStatus.UNSUPPORTED
    assert result.state is None
    assert result.feasibility.issues[0].code == "CONNECTED_CAVITY_UNSUPPORTED"


def test_simultaneous_constrictions_are_order_independent() -> None:
    tighter = _constriction(0.65, area_m2=1e-5)
    looser = _constriction(0.65, area_m2=2e-5)
    realizer = Tract1DRealizer()
    prepared = _prepared()

    first = realizer.realize_snapshot(
        prepared, GestureScore((tighter, looser)), time_s=0.20
    )
    second = realizer.realize_snapshot(
        prepared, GestureScore((looser, tighter)), time_s=0.20
    )

    assert first.feasibility.status is FeasibilityStatus.FEASIBLE
    assert second.feasibility.status is FeasibilityStatus.FEASIBLE
    assert first.state == second.state
    assert first.state is not None
    assert first.state.sections[6].area_m2 == 1e-5


def test_realization_result_requires_state_exactly_when_feasible() -> None:
    with pytest.raises(ValueError, match="FEASIBLE realization must contain state"):
        RealizationResult[Tract1DGeometry](
            state=None,
            feasibility=FeasibilityReport(status=FeasibilityStatus.FEASIBLE),
        )

    with pytest.raises(ValueError, match="FEASIBLE realization must contain state"):
        RealizationResult(
            state=_rest_geometry(),
            feasibility=FeasibilityReport(status=FeasibilityStatus.INFEASIBLE),
        )
