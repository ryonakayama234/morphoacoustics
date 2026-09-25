from __future__ import annotations

import numpy as np

from morphoacoustics import (
    CavityKind,
    CavitySpec,
    CreatureSpec,
    GestureScore,
    simulate_snapshot,
)
from morphoacoustics.acoustics import (
    ImpedanceRequest,
    SegmentedTubeBackend,
)
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.realization import Tract1DRealizer


def geometry(length_m: float, count: int = 10) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=length_m / count, area_m2=3e-4)
            for _ in range(count)
        ),
    )


def first_peak_hz(length_m: float) -> float:
    creature = CreatureSpec(
        name=f"uniform-{length_m:.2f}m",
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
    )
    frequencies = np.linspace(300.0, 900.0, 6001)
    result = simulate_snapshot(
        creature=creature,
        score=GestureScore(()),
        realizer=Tract1DRealizer(geometry(length_m)),
        acoustic_backend=SegmentedTubeBackend(),
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.0,
    )
    assert result.acoustics is not None
    return float(
        frequencies[
            np.nanargmax(np.abs(result.acoustics.input_impedance_pa_s_m3))
        ]
    )


def main() -> None:
    for length_m in (0.17, 0.12):
        measured = first_peak_hz(length_m)
        analytic = 343.0 / (4.0 * length_m)
        error_pct = 100.0 * abs(measured - analytic) / analytic
        print(
            f"L={length_m:.2f} m  measured={measured:.2f} Hz  "
            f"analytic={analytic:.2f} Hz  error={error_pct:.3f}%"
        )


if __name__ == "__main__":
    main()
