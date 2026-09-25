import numpy as np

from morphoacoustics import (
    ArticulatorSpec,
    CavityKind,
    CavitySpec,
    CreatureSpec,
    Gesture,
    GestureScore,
    Task,
    TaskParameter,
    simulate_snapshot,
)
from morphoacoustics.acoustics import ImpedanceRequest, SegmentedTubeBackend
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.realization import Tract1DRealizer


def _creature(reachable_end: float = 0.80) -> CreatureSpec:
    return CreatureSpec(
        name="prototype",
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


def _uniform_geometry(total_length_m: float, count: int = 10) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=total_length_m / count, area_m2=3e-4)
            for _ in range(count)
        ),
    )


def _constriction(location: float = 0.65) -> GestureScore:
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


def _first_impedance_peak_hz(length_m: float) -> float:
    frequencies = np.linspace(300.0, 900.0, 6001)
    result = simulate_snapshot(
        creature=_creature(),
        score=GestureScore(()),
        realizer=Tract1DRealizer(_uniform_geometry(length_m)),
        acoustic_backend=SegmentedTubeBackend(),
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.0,
    )
    assert result.acoustics is not None
    magnitude = np.abs(result.acoustics.input_impedance_pa_s_m3)
    return float(frequencies[np.nanargmax(magnitude)])


def test_shorter_tract_moves_first_resonance_upward() -> None:
    long_peak = _first_impedance_peak_hz(0.17)
    short_peak = _first_impedance_peak_hz(0.12)

    assert long_peak < short_peak
    np.testing.assert_allclose(long_peak, 343.0 / (4.0 * 0.17), rtol=0.01)
    np.testing.assert_allclose(short_peak, 343.0 / (4.0 * 0.12), rtol=0.01)


def test_constriction_changes_acoustic_response() -> None:
    frequencies = np.linspace(250.0, 1800.0, 256)
    geometry = _uniform_geometry(0.17)
    backend = SegmentedTubeBackend()

    rest = simulate_snapshot(
        creature=_creature(),
        score=GestureScore(()),
        realizer=Tract1DRealizer(geometry),
        acoustic_backend=backend,
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.1,
    )
    constricted = simulate_snapshot(
        creature=_creature(),
        score=_constriction(),
        realizer=Tract1DRealizer(geometry),
        acoustic_backend=backend,
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.1,
    )

    assert rest.acoustics is not None
    assert constricted.acoustics is not None
    assert not np.allclose(
        rest.acoustics.input_impedance_pa_s_m3,
        constricted.acoustics.input_impedance_pa_s_m3,
        rtol=1e-9,
        atol=1e-6,
    )


def test_same_task_changes_physical_realization_and_acoustics_with_morphology() -> None:
    score = _constriction()
    long_geometry = _uniform_geometry(0.17)
    short_geometry = _uniform_geometry(0.12)
    frequencies = np.array([350.0, 700.0, 1100.0])
    backend = SegmentedTubeBackend()

    long_result = simulate_snapshot(
        creature=_creature(),
        score=score,
        realizer=Tract1DRealizer(long_geometry),
        acoustic_backend=backend,
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.1,
    )
    short_result = simulate_snapshot(
        creature=_creature(),
        score=score,
        realizer=Tract1DRealizer(short_geometry),
        acoustic_backend=backend,
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.1,
    )

    assert long_result.realization.state is not None
    assert short_result.realization.state is not None
    assert long_result.acoustics is not None
    assert short_result.acoustics is not None

    assert long_geometry.axial_position_m(0.65) > short_geometry.axial_position_m(0.65)
    assert long_result.realization.state.sections[6].area_m2 == 2e-5
    assert short_result.realization.state.sections[6].area_m2 == 2e-5
    assert not np.allclose(
        long_result.acoustics.input_impedance_pa_s_m3,
        short_result.acoustics.input_impedance_pa_s_m3,
        rtol=1e-9,
        atol=1e-6,
    )


def test_infeasible_realization_stops_before_acoustics() -> None:
    result = simulate_snapshot(
        creature=_creature(reachable_end=0.80),
        score=_constriction(location=0.95),
        realizer=Tract1DRealizer(_uniform_geometry(0.17)),
        acoustic_backend=SegmentedTubeBackend(),
        acoustic_request=ImpedanceRequest(np.array([500.0])),
        time_s=0.1,
    )

    assert not result.has_acoustic_result
    assert result.acoustics is None
