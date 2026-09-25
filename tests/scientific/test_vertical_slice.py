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
    Tract1DRealizer,
    TractGeometry,
    TubeSection,
    simulate_snapshot,
)


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


def _uniform_geometry(total_length_m: float, count: int = 10) -> TractGeometry:
    return TractGeometry(
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
        time_s=0.0,
        frequencies_hz=frequencies,
    )
    assert result.input_impedance_pa_s_m3 is not None
    magnitude = np.abs(result.input_impedance_pa_s_m3)
    return float(frequencies[np.nanargmax(magnitude)])


def test_shorter_tract_moves_first_resonance_upward() -> None:
    long_peak = _first_impedance_peak_hz(0.17)
    short_peak = _first_impedance_peak_hz(0.12)

    assert long_peak < short_peak
    assert long_peak == np.testing.assert_allclose(long_peak, 343.0 / (4.0 * 0.17), rtol=0.01)


def test_same_gesture_preserves_task_but_changes_physical_scale() -> None:
    score = _constriction()
    long_result = Tract1DRealizer(_uniform_geometry(0.17)).realize_snapshot(
        _creature(), score, time_s=0.1
    )
    short_result = Tract1DRealizer(_uniform_geometry(0.12)).realize_snapshot(
        _creature(), score, time_s=0.1
    )

    assert long_result.geometry is not None
    assert short_result.geometry is not None
    assert long_result.geometry.total_length_m > short_result.geometry.total_length_m
    long_index = long_result.geometry.section_index_at(0.65)
    short_index = short_result.geometry.section_index_at(0.65)
    assert long_result.geometry.sections[long_index].area_m2 == 2e-5
    assert short_result.geometry.sections[short_index].area_m2 == 2e-5


def test_infeasible_realization_stops_before_acoustics() -> None:
    result = simulate_snapshot(
        creature=_creature(reachable_end=0.80),
        score=_constriction(location=0.95),
        realizer=Tract1DRealizer(_uniform_geometry(0.17)),
        time_s=0.1,
        frequencies_hz=np.array([500.0]),
    )

    assert not result.has_acoustic_result
    assert result.frequencies_hz is None
    assert result.input_impedance_pa_s_m3 is None
