from morphoacoustics import (
    ArticulatorSpec,
    CavityConnection,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    FeasibilityStatus,
    Gesture,
    GestureScore,
    Task,
    TaskParameter,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.realization import Tract1DRealizer


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
    rest = _rest_geometry()
    result = Tract1DRealizer(rest).realize_snapshot(
        _creature(),
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
    result = Tract1DRealizer(rest).realize_snapshot(
        _creature(),
        GestureScore((_constriction(0.65),)),
        time_s=0.05,
    )

    assert result.feasibility.status is FeasibilityStatus.FEASIBLE
    assert result.state == rest


def test_unreachable_constriction_is_explicitly_infeasible() -> None:
    result = Tract1DRealizer(_rest_geometry()).realize_snapshot(
        _creature(),
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
    result = Tract1DRealizer(_rest_geometry()).realize_snapshot(
        _creature(),
        GestureScore((phonate,)),
        time_s=0.1,
    )

    assert result.feasibility.status is FeasibilityStatus.UNSUPPORTED
    assert result.state is None
    assert result.feasibility.issues[0].code == "TASK_UNSUPPORTED"


def test_invalid_target_area_is_not_reported_as_physical_infeasibility() -> None:
    result = Tract1DRealizer(_rest_geometry()).realize_snapshot(
        _creature(),
        GestureScore((_constriction(0.65, area_m2=-1e-5),)),
        time_s=0.20,
    )

    assert result.feasibility.status is FeasibilityStatus.INVALID
    assert result.state is None
    assert result.feasibility.issues[0].code == "NONPOSITIVE_TARGET_AREA"


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

    result = Tract1DRealizer(_rest_geometry()).realize_snapshot(
        creature,
        GestureScore(()),
        time_s=0.0,
    )

    assert result.feasibility.status is FeasibilityStatus.UNSUPPORTED
    assert result.state is None
    assert result.feasibility.issues[0].code == "CONNECTED_CAVITY_UNSUPPORTED"


def test_simultaneous_constrictions_are_order_independent() -> None:
    tighter = _constriction(0.65, area_m2=1e-5)
    looser = _constriction(0.65, area_m2=2e-5)
    realizer = Tract1DRealizer(_rest_geometry())

    first = realizer.realize_snapshot(
        _creature(), GestureScore((tighter, looser)), time_s=0.20
    )
    second = realizer.realize_snapshot(
        _creature(), GestureScore((looser, tighter)), time_s=0.20
    )

    assert first.feasibility.status is FeasibilityStatus.FEASIBLE
    assert second.feasibility.status is FeasibilityStatus.FEASIBLE
    assert first.state == second.state
    assert first.state is not None
    assert first.state.sections[6].area_m2 == 1e-5
