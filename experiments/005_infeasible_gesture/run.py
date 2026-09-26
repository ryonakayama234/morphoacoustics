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


def creature(name: str, reachable_end: float) -> CreatureSpec:
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


def geometry() -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=0.017, area_m2=3e-4)
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
                location=0.70,
                parameters=(TaskParameter("target_area", 2e-5, "m2"),),
            ),
        )
    )


def prepared(name: str, reachable_end: float):
    return prepare_tract1d(
        creature(name, reachable_end),
        geometry(),
        provenance=PreparationProvenance(
            source="experiment",
            model="uniform-tract",
            notes=(f"tongue_reachable_end={reachable_end:g}",),
        ),
    )


def main() -> None:
    gesture_score = score()
    capable = prepared("capable-body", 0.80)
    limited = prepared("limited-body", 0.55)
    realizer = Tract1DRealizer()
    backend = SegmentedTubeBackend()
    request = ImpedanceRequest(np.array([500.0]))

    capable_result = simulate_snapshot(
        morphology=capable,
        score=gesture_score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )
    limited_result = simulate_snapshot(
        morphology=limited,
        score=gesture_score,
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )

    print("capable status:", capable_result.realization.feasibility.status)
    print("capable acoustics:", capable_result.has_acoustic_result)
    print("limited status:", limited_result.realization.feasibility.status)
    print("limited acoustics:", limited_result.has_acoustic_result)
    print("limited issue:", limited_result.realization.feasibility.issues[0].code)


if __name__ == "__main__":
    main()
