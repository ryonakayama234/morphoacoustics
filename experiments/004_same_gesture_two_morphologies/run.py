from __future__ import annotations

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
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d
from morphoacoustics.realization import Tract1DRealizer


def creature(name: str) -> CreatureSpec:
    return CreatureSpec(
        name=name,
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


def geometry(total_length_m: float) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=total_length_m / 10.0, area_m2=3e-4)
            for _ in range(10)
        ),
    )


def score() -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=0.0,
                offset_s=0.3,
                target="oral",
                location=0.65,
                parameters=(TaskParameter("target_area", 2e-5, "m2"),),
            ),
        )
    )


def prepared(name: str, total_length_m: float):
    return prepare_tract1d(
        creature(name),
        geometry(total_length_m),
        provenance=PreparationProvenance(
            source="experiment",
            model="uniform-tract",
            notes=(f"total_length_m={total_length_m:g}",),
        ),
    )


def main() -> None:
    gesture_score = score()
    long_body = prepared("long-human", 0.17)
    short_body = prepared("short-human", 0.12)
    frequencies = np.array([350.0, 700.0, 1100.0])
    backend = SegmentedTubeBackend()
    realizer = Tract1DRealizer()
    request = ImpedanceRequest(frequencies)

    long_result = simulate_snapshot(
        morphology=long_body,
        score=gesture_score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )
    short_result = simulate_snapshot(
        morphology=short_body,
        score=gesture_score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )

    assert long_result.realization.state is not None
    assert short_result.realization.state is not None
    assert long_result.acoustics is not None
    assert short_result.acoustics is not None

    print("gesture normalized location:", gesture_score.gestures[0].location)
    print("long axial position m:", long_body.rest_state.axial_position_m(0.65))
    print("short axial position m:", short_body.rest_state.axial_position_m(0.65))
    print("long status:", long_result.realization.feasibility.status)
    print("short status:", short_result.realization.feasibility.status)
    print(
        "same acoustic response:",
        np.allclose(
            long_result.acoustics.input_impedance_pa_s_m3,
            short_result.acoustics.input_impedance_pa_s_m3,
        ),
    )


if __name__ == "__main__":
    main()
