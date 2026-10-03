"""Experiment 015: calibrate Embodiment measurement with uniform-tube scaling."""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import time
from pathlib import Path

import numpy as np

from morphoacoustics import (
    CavityKind,
    CavitySpec,
    CreatureSpec,
    GestureScore,
    simulate_snapshot,
)
from morphoacoustics.acoustics import ImpedanceRequest, SegmentedTubeBackend
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import PreparationProvenance, prepare_tract1d
from morphoacoustics.realization import Tract1DRealizer

SOUND_SPEED_M_S = 343.0
AIR_DENSITY_KG_M3 = 1.21
AREA_M2 = 3.0e-4
BASELINE_LENGTH_M = 0.17
RELATIVE_CHANGES = (-0.10, -0.05, 0.0, 0.05, 0.10)
CANDIDATE_SECTION_COUNT = 10
PARTITION_SECTION_COUNTS = (1, 10, 40)
CANDIDATE_GRID_STEP_HZ = 0.05
REFERENCE_GRID_STEP_HZ = 0.01
MODE_WINDOWS_HZ = (
    (430.0, 590.0),
    (1300.0, 1750.0),
    (2200.0, 2850.0),
)
IDENTITY_TOLERANCE_HZ = 1.0e-12
SENSITIVITY_TOLERANCE = 0.005
DISCRIMINATION_MARGIN = 5.0

ORACLE_PATH = Path(__file__).with_name("wolfram") / "embodiment_oracle.json"


def _creature() -> CreatureSpec:
    return CreatureSpec(
        name="e0-uniform-tube",
        cavities=(CavitySpec(id="oral", kind=CavityKind.ORAL),),
    )


def _geometry(length_m: float, section_count: int) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(length_m=length_m / section_count, area_m2=AREA_M2)
            for _ in range(section_count)
        ),
    )


def _frequency_grid(start_hz: float, stop_hz: float, step_hz: float) -> np.ndarray:
    intervals = int(round((stop_hz - start_hz) / step_hz))
    if not math.isclose(
        start_hz + intervals * step_hz,
        stop_hz,
        rel_tol=0.0,
        abs_tol=1.0e-10,
    ):
        raise ValueError("frequency window must be divisible by step")
    return np.linspace(start_hz, stop_hz, intervals + 1, dtype=np.float64)


def _measure_peak(
    *,
    length_m: float,
    section_count: int,
    window_hz: tuple[float, float],
    grid_step_hz: float,
) -> tuple[float, float]:
    geometry = _geometry(length_m, section_count)
    morphology = prepare_tract1d(
        _creature(),
        geometry,
        provenance=PreparationProvenance(
            source="experiment-015",
            model="uniform-tube-embodiment-calibration",
            notes=(
                f"total_length_m={length_m:.17g}",
                f"section_count={section_count}",
            ),
        ),
    )
    frequencies = _frequency_grid(window_hz[0], window_hz[1], grid_step_hz)
    result = simulate_snapshot(
        morphology=morphology,
        score=GestureScore(()),
        realizer=Tract1DRealizer(),
        acoustic_backend=SegmentedTubeBackend(
            sound_speed_m_s=SOUND_SPEED_M_S,
            air_density_kg_m3=AIR_DENSITY_KG_M3,
        ),
        acoustic_request=ImpedanceRequest(frequencies),
        time_s=0.0,
    )
    if result.acoustics is None:
        raise RuntimeError("calibration fixture unexpectedly produced no acoustics")
    if result.realization.state is None:
        raise RuntimeError("calibration fixture unexpectedly produced no physical state")

    magnitude = np.abs(result.acoustics.input_impedance_pa_s_m3)
    peak_hz = float(frequencies[int(np.nanargmax(magnitude))])
    realized_length_m = float(result.realization.state.total_length_m)
    return peak_hz, realized_length_m


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _row_lookup(
    rows: list[dict[str, object]],
    *,
    relative_change: float,
    mode: int,
) -> dict[str, object]:
    for row in rows:
        if (
            int(row["mode"]) == mode
            and math.isclose(
                float(row["relative_change"]),
                relative_change,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            )
        ):
            return row
    raise KeyError((relative_change, mode))


def _central_log_sensitivity(
    lower_hz: float,
    upper_hz: float,
    epsilon: float,
) -> float:
    return float(
        (math.log(upper_hz) - math.log(lower_hz))
        / (math.log(1.0 + epsilon) - math.log(1.0 - epsilon))
    )


def run(output_dir: Path) -> dict[str, object]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))

    oracle_points = {
        round(float(point["relative_change"]), 8): point
        for point in oracle["sweep"]
    }

    sweep_rows: list[dict[str, object]] = []
    for relative_change in RELATIVE_CHANGES:
        point = oracle_points[round(relative_change, 8)]
        length_m = BASELINE_LENGTH_M * (1.0 + relative_change)
        if not math.isclose(
            length_m,
            float(point["length_m"]),
            rel_tol=0.0,
            abs_tol=1.0e-14,
        ):
            raise RuntimeError("Python sweep length disagrees with Wolfram oracle")

        for mode, window_hz in enumerate(MODE_WINDOWS_HZ, start=1):
            candidate_hz, candidate_realized_length_m = _measure_peak(
                length_m=length_m,
                section_count=CANDIDATE_SECTION_COUNT,
                window_hz=window_hz,
                grid_step_hz=CANDIDATE_GRID_STEP_HZ,
            )
            reference_hz, reference_realized_length_m = _measure_peak(
                length_m=length_m,
                section_count=CANDIDATE_SECTION_COUNT,
                window_hz=window_hz,
                grid_step_hz=REFERENCE_GRID_STEP_HZ,
            )
            oracle_hz = float(point["modes_hz"][mode - 1])
            sweep_rows.append(
                {
                    "relative_change": relative_change,
                    "length_m": length_m,
                    "mode": mode,
                    "oracle_hz": oracle_hz,
                    "candidate_peak_hz": candidate_hz,
                    "reference_peak_hz": reference_hz,
                    "candidate_abs_error_hz": abs(candidate_hz - oracle_hz),
                    "reference_abs_error_hz": abs(reference_hz - oracle_hz),
                    "candidate_vs_reference_abs_delta_hz": abs(
                        candidate_hz - reference_hz
                    ),
                    "candidate_realized_length_m": candidate_realized_length_m,
                    "reference_realized_length_m": reference_realized_length_m,
                }
            )

    _write_csv(output_dir / "sweep.csv", sweep_rows)

    identity_peaks: list[float] = []
    for _ in range(2):
        peak_hz, _ = _measure_peak(
            length_m=BASELINE_LENGTH_M,
            section_count=CANDIDATE_SECTION_COUNT,
            window_hz=MODE_WINDOWS_HZ[0],
            grid_step_hz=CANDIDATE_GRID_STEP_HZ,
        )
        identity_peaks.append(peak_hz)
    identity_delta_hz = abs(identity_peaks[1] - identity_peaks[0])

    partition_rows: list[dict[str, object]] = []
    baseline_candidate_by_mode = {
        mode: float(
            _row_lookup(sweep_rows, relative_change=0.0, mode=mode)[
                "candidate_peak_hz"
            ]
        )
        for mode in range(1, 4)
    }
    for section_count in PARTITION_SECTION_COUNTS:
        for mode, window_hz in enumerate(MODE_WINDOWS_HZ, start=1):
            peak_hz, realized_length_m = _measure_peak(
                length_m=BASELINE_LENGTH_M,
                section_count=section_count,
                window_hz=window_hz,
                grid_step_hz=CANDIDATE_GRID_STEP_HZ,
            )
            partition_rows.append(
                {
                    "section_count": section_count,
                    "mode": mode,
                    "peak_hz": peak_hz,
                    "baseline_10_section_peak_hz": baseline_candidate_by_mode[mode],
                    "abs_delta_vs_10_section_hz": abs(
                        peak_hz - baseline_candidate_by_mode[mode]
                    ),
                    "realized_length_m": realized_length_m,
                }
            )
    _write_csv(output_dir / "partition_control.csv", partition_rows)

    numerical_floor_by_mode: dict[int, float] = {}
    for mode in range(1, 4):
        grid_floor = max(
            float(row["candidate_vs_reference_abs_delta_hz"])
            for row in sweep_rows
            if int(row["mode"]) == mode
        )
        partition_floor = max(
            float(row["abs_delta_vs_10_section_hz"])
            for row in partition_rows
            if int(row["mode"]) == mode
        )
        numerical_floor_by_mode[mode] = max(
            CANDIDATE_GRID_STEP_HZ,
            grid_floor,
            partition_floor,
        )

    sensitivity_rows: list[dict[str, object]] = []
    for epsilon in (0.05, 0.10):
        oracle_key = (
            "central_log_sensitivity_eps_0_05"
            if math.isclose(epsilon, 0.05)
            else "central_log_sensitivity_eps_0_10"
        )
        for mode in range(1, 4):
            shorter = _row_lookup(
                sweep_rows,
                relative_change=-epsilon,
                mode=mode,
            )
            longer = _row_lookup(
                sweep_rows,
                relative_change=epsilon,
                mode=mode,
            )
            measured = _central_log_sensitivity(
                lower_hz=float(shorter["candidate_peak_hz"]),
                upper_hz=float(longer["candidate_peak_hz"]),
                epsilon=epsilon,
            )
            oracle_sensitivity = float(oracle[oracle_key][mode - 1])
            sensitivity_rows.append(
                {
                    "epsilon": epsilon,
                    "mode": mode,
                    "measured_log_sensitivity": measured,
                    "oracle_log_sensitivity": oracle_sensitivity,
                    "abs_error": abs(measured - oracle_sensitivity),
                }
            )
    _write_csv(output_dir / "sensitivity.csv", sensitivity_rows)

    effect_rows: list[dict[str, object]] = []
    for relative_change in RELATIVE_CHANGES:
        if math.isclose(relative_change, 0.0, abs_tol=1.0e-12):
            continue
        for mode in range(1, 4):
            row = _row_lookup(
                sweep_rows,
                relative_change=relative_change,
                mode=mode,
            )
            effect_hz = abs(
                float(row["candidate_peak_hz"]) - baseline_candidate_by_mode[mode]
            )
            floor_hz = numerical_floor_by_mode[mode]
            effect_rows.append(
                {
                    "relative_change": relative_change,
                    "mode": mode,
                    "morphology_effect_hz": effect_hz,
                    "numerical_floor_hz": floor_hz,
                    "effect_over_numerical_floor": effect_hz / floor_hz,
                }
            )
    _write_csv(output_dir / "effect_vs_numerical.csv", effect_rows)

    candidate_oracle_ok = all(
        float(row["candidate_abs_error_hz"]) <= CANDIDATE_GRID_STEP_HZ + 1.0e-12
        for row in sweep_rows
    )
    reference_oracle_ok = all(
        float(row["reference_abs_error_hz"]) <= REFERENCE_GRID_STEP_HZ + 1.0e-12
        for row in sweep_rows
    )
    identity_ok = identity_delta_hz <= IDENTITY_TOLERANCE_HZ
    sensitivity_ok = all(
        float(row["abs_error"]) <= SENSITIVITY_TOLERANCE
        for row in sensitivity_rows
    )
    partition_ok = all(
        float(row["abs_delta_vs_10_section_hz"])
        <= CANDIDATE_GRID_STEP_HZ + 1.0e-12
        for row in partition_rows
    )
    discrimination_ok = all(
        float(row["effect_over_numerical_floor"]) > DISCRIMINATION_MARGIN
        for row in effect_rows
    )
    finite_ok = all(
        math.isfinite(float(row[key]))
        for row in sweep_rows
        for key in (
            "oracle_hz",
            "candidate_peak_hz",
            "reference_peak_hz",
            "candidate_realized_length_m",
            "reference_realized_length_m",
        )
    )
    realized_length_ok = all(
        math.isclose(
            float(row["candidate_realized_length_m"]),
            float(row["length_m"]),
            rel_tol=0.0,
            abs_tol=1.0e-14,
        )
        and math.isclose(
            float(row["reference_realized_length_m"]),
            float(row["length_m"]),
            rel_tol=0.0,
            abs_tol=1.0e-14,
        )
        for row in sweep_rows
    )

    monotonic_ok = True
    for mode in range(1, 4):
        ordered = sorted(
            (
                float(row["length_m"]),
                float(row["candidate_peak_hz"]),
            )
            for row in sweep_rows
            if int(row["mode"]) == mode
        )
        monotonic_ok = monotonic_ok and all(
            ordered[index + 1][1] < ordered[index][1]
            for index in range(len(ordered) - 1)
        )

    supported = all(
        (
            identity_ok,
            finite_ok,
            realized_length_ok,
            candidate_oracle_ok,
            reference_oracle_ok,
            monotonic_ok,
            sensitivity_ok,
            partition_ok,
            discrimination_ok,
        )
    )
    decision_name = (
        "SUPPORT_EMBODIMENT_MEASUREMENT"
        if supported
        else "MEASUREMENT_UNCALIBRATED"
    )

    decision: dict[str, object] = {
        "decision": decision_name,
        "issue": 40,
        "research_question": (
            "whether the Fidelity-0 observer can recover the known tract-length "
            "resonance sensitivity and separate it from its numerical floor"
        ),
        "claim_scope": "E0 measurement calibration only",
        "model_class": (
            "rigid lossless closed-open 1D segmented transmission line; "
            "empty GestureScore; no source or waveform"
        ),
        "intervention": {
            "parameter": "prepared_tract_total_length_m",
            "baseline": BASELINE_LENGTH_M,
            "relative_changes": list(RELATIVE_CHANGES),
            "fixed_area_m2": AREA_M2,
            "gesture_score": "empty-and-identical",
            "creature_spec": "fixed-e0-uniform-tube",
        },
        "observer": {
            "candidate_grid_step_hz": CANDIDATE_GRID_STEP_HZ,
            "reference_grid_step_hz": REFERENCE_GRID_STEP_HZ,
            "mode_windows_hz": [list(window) for window in MODE_WINDOWS_HZ],
        },
        "identity_control": {
            "peaks_hz": identity_peaks,
            "abs_delta_hz": identity_delta_hz,
            "tolerance_hz": IDENTITY_TOLERANCE_HZ,
            "pass": identity_ok,
        },
        "numerical_floor_hz_by_mode": {
            str(mode): floor for mode, floor in numerical_floor_by_mode.items()
        },
        "gates": {
            "finite_peak_and_trace_quantities": finite_ok,
            "realized_length_matches_intervention": realized_length_ok,
            "candidate_peak_matches_wolfram_oracle": candidate_oracle_ok,
            "reference_peak_matches_wolfram_oracle": reference_oracle_ok,
            "monotone_inverse_length_response": monotonic_ok,
            "log_sensitivity_matches_minus_one": sensitivity_ok,
            "section_partition_invariance": partition_ok,
            "effect_exceeds_5x_numerical_floor": discrimination_ok,
        },
        "wolfram_oracle": oracle,
        "causal_trace": {
            "morphology_delta": "prepared 1D tract total length only",
            "prepared_state": "uniform equal-area serial sections",
            "realization": "empty GestureScore leaves prepared geometry unchanged",
            "acoustic_state": "input impedance under ideal pressure-release outlet",
            "observation": "first three resonance peak frequencies",
        },
        "limitations": [
            "calibrates a backend-specific prepared geometry axis, not a universal CreatureSpec morphology parameter",
            "uniform lossless tube only",
            "section-count control is partition invariance, not FEM/mesh convergence",
            "frequency-grid extraction dominates the declared numerical floor",
            "no task realization beyond an empty GestureScore",
            "no source, waveform, perception, naturalness, or phonetic claim",
        ],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-015-output"),
    )
    args = parser.parse_args()
    decision = run(args.output_dir)
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    if decision["decision"] != "SUPPORT_EMBODIMENT_MEASUREMENT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
