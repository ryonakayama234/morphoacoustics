import numpy as np

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
    simulate_snapshot,
)
from morphoacoustics.acoustics import ImpedanceRequest, SegmentedTubeBackend
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d
from morphoacoustics.realization import Tract1DRealizer


def _creature(name: str, reachable_end: float = 0.80) -> CreatureSpec:
    return CreatureSpec(
        name=name,
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
        articulators=(
            ArticulatorSpec(
                id="tongue",
                cavity_id="oral",
                kind="tongue",
                reachable_start=0.30,
                reachable_end=reachable_end,
            ),
        ),
    )


def _geometry(total_length_m: float) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=total_length_m / 10.0, area_m2=3e-4)
            for _ in range(10)
        ),
    )


def _score(location: float = 0.65) -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=0.0,
                offset_s=0.3,
                target="oral",
                location=location,
                parameters=(TaskParameter("target_area", 2e-5, "m2"),),
            ),
        )
    )


def _prepared(name: str, length_m: float, reachable_end: float = 0.80):
    return prepare_tract1d(
        _creature(name, reachable_end=reachable_end),
        _geometry(length_m),
        provenance=PreparationProvenance(
            source="scientific-test",
            model="uniform-tract",
            notes=(f"total_length_m={length_m:g}",),
        ),
    )


def test_same_gesture_preserves_task_but_changes_physical_realization_and_acoustics() -> None:
    score = _score(location=0.65)
    long_body = _prepared("long-human", 0.17)
    short_body = _prepared("short-human", 0.12)
    frequencies = np.array([350.0, 700.0, 1100.0])
    backend = SegmentedTubeBackend()
    realizer = Tract1DRealizer()

    long_result = simulate_snapshot(
        morphology=long_body,
        score=score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.1,
    )
    short_result = simulate_snapshot(
        morphology=short_body,
        score=score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.1,
    )

    assert long_result.realization.feasibility.status is FeasibilityStatus.FEASIBLE
    assert short_result.realization.feasibility.status is FeasibilityStatus.FEASIBLE
    assert long_result.realization.state is not None
    assert short_result.realization.state is not None
    assert long_result.acoustics is not None
    assert short_result.acoustics is not None

    assert score.gestures[0].location == 0.65
    assert long_body.rest_state.axial_position_m(0.65) == 0.1105
    assert short_body.rest_state.axial_position_m(0.65) == 0.078
    assert long_result.realization.state.sections[6].area_m2 == 2e-5
    assert short_result.realization.state.sections[6].area_m2 == 2e-5
    assert not np.allclose(
        long_result.acoustics.input_impedance_pa_s_m3,
        short_result.acoustics.input_impedance_pa_s_m3,
        rtol=1e-9,
        atol=1e-6,
    )


def test_same_gesture_can_be_feasible_for_one_body_and_infeasible_for_another() -> None:
    score = _score(location=0.70)
    capable = _prepared("capable-body", 0.17, reachable_end=0.80)
    limited = _prepared("limited-body", 0.17, reachable_end=0.55)
    backend = SegmentedTubeBackend()
    request = ImpedanceRequest(np.array([500.0]))
    realizer = Tract1DRealizer()

    capable_result = simulate_snapshot(
        morphology=capable,
        score=score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )
    limited_result = simulate_snapshot(
        morphology=limited,
        score=score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )

    assert capable_result.realization.feasibility.status is FeasibilityStatus.FEASIBLE
    assert capable_result.has_acoustic_result
    assert limited_result.realization.feasibility.status is FeasibilityStatus.INFEASIBLE
    assert not limited_result.has_acoustic_result
    assert limited_result.realization.feasibility.issues[0].code == "LOCATION_UNREACHABLE"
