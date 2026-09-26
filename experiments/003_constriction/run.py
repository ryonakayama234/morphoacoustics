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


def creature() -> CreatureSpec:
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


def rest_geometry() -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=0.017, area_m2=3e-4)
            for _ in range(10)
        ),
    )


def score(location: float) -> GestureScore:
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


def main() -> None:
    geometry = rest_geometry()
    morphology = prepare_tract1d(
        creature(),
        geometry,
        provenance=PreparationProvenance(
            source="experiment",
            model="simple-human-uniform-tract",
        ),
    )
    frequencies = np.linspace(200.0, 2000.0, 1801)
    backend = SegmentedTubeBackend()
    request = ImpedanceRequest(frequencies)
    realizer = Tract1DRealizer()

    reachable = simulate_snapshot(
        morphology=morphology,
        score=score(0.65),
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )
    index = geometry.section_index_at(0.65)
    assert reachable.realization.state is not None
    print("reachable status:", reachable.realization.feasibility.status)
    print("constricted section:", index)
    print("rest area m2:", geometry.sections[index].area_m2)
    print("realized area m2:", reachable.realization.state.sections[index].area_m2)
    print("acoustics evaluated:", reachable.has_acoustic_result)

    unreachable = simulate_snapshot(
        morphology=morphology,
        score=score(0.95),
        realizer=realizer,
        acoustic_backend=backend,
        acoustic_request=request,
        time_s=0.1,
    )
    print("unreachable status:", unreachable.realization.feasibility.status)
    print("issue:", unreachable.realization.feasibility.issues[0].code)
    print("acoustics evaluated:", unreachable.has_acoustic_result)


if __name__ == "__main__":
    main()
