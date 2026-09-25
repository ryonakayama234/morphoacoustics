from morphoacoustics import (
    ArticulatorSpec,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    FeasibilityStatus,
    Gesture,
    GestureScore,
    Task,
    TaskParameter,
    Tract1DRealizer,
    TractGeometry,
    TubeSection,
)


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


def _rest_geometry() -> TractGeometry:
    return TractGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=0.017, area_m2=3e-4)
            for _ in range(10)
        ),
    )


def _constriction(location: float) -> Gesture:
    return Gesture(
        task=Task.CONSTRICT,
        onset_s=0.10,
        offset_s=0.30,
        target="oral",
        location=location,
        parameters=(TaskParameter("target_area", 2e-5, "m2"),),
    )


def test_active_constriction_changes_body_specific_geometry() -> None:
    rest = _rest_geometry()
    realizer = Tract1DRealizer(rest)

    result = realizer.realize_snapshot(
        _creature(),
        GestureScore((_constriction(0.65),)),
        time_s=0.20,
    )

    assert result.feasibility.status is FeasibilityStatus.FEASIBLE
    assert result.geometry is not None
    index = rest.section_index_at(0.65)
    assert result.geometry.sections[index].area_m2 == 2e-5
    assert result.geometry.sections[index - 1].area_m2 == 3e-4


def test_inactive_gesture_leaves_rest_geometry_unchanged() -> None:
    rest = _rest_geometry()
    result = Tract1DRealizer(rest).realize_snapshot(
        _creature(),
        GestureScore((_constriction(0.65),)),
        time_s=0.05,
    )

    assert result.feasibility.status is FeasibilityStatus.FEASIBLE
    assert result.geometry == rest


def test_unreachable_constriction_is_explicitly_infeasible() -> None:
    result = Tract1DRealizer(_rest_geometry()).realize_snapshot(
        _creature(),
        GestureScore((_constriction(0.95),)),
        time_s=0.20,
    )

    assert result.feasibility.status is FeasibilityStatus.INFEASIBLE
    assert result.geometry is None
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
    assert result.geometry is None
    assert result.feasibility.issues[0].code == "TASK_UNSUPPORTED"
