"""Experiment 018: non-self-similar local-area morphology sensitivity sweep."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import time
from pathlib import Path
from typing import Any

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
from morphoacoustics.preparation import (
    PreparationProvenance,
    PreparedMorphology,
    prepare_tract1d,
)
from morphoacoustics.realization import Tract1DRealizer

TRACT_LENGTH_M = 0.17
SECTION_COUNT = 10
BASELINE_AREA_M2 = 3.0e-4
INTERVENTION_SECTION_INDEX = 0
GESTURE_LOCATION = 0.65
GESTURE_SECTION_INDEX = 6
TARGET_AREA_M2 = 2.0e-4
RELATIVE_CHANGES = (-0.10, -0.05, 0.0, 0.05, 0.10)
EVALUATION_TIME_S = 0.1

CANDIDATE_GRID_STEP_HZ = 0.05
REFERENCE_GRID_STEP_HZ = 0.01
MODE_WINDOWS_HZ = (
    (470.0, 520.0),
    (1480.0, 1600.0),
    (2400.0, 2570.0),
)

AREA_TOLERANCE_M2 = 1.0e-18
SENSITIVITY_TOLERANCE = 0.001
REFERENCE_SENSITIVITY_TOLERANCE = 0.0002
DISCRIMINATION_MARGIN = 5.0

SUPPORT_DECISION = "SUPPORT_LOCAL_AREA_MORPHOLOGY_SENSITIVITY"
ORACLE_PATH = (
    Path(__file__).with_name("wolfram") / "local_area_sensitivity_oracle.json"
)


def _creature() -> CreatureSpec:
    return CreatureSpec(
        name="e1c-local-area-body",
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


def _geometry(relative_change: float) -> Tract1DGeometry:
    sections: list[TubeSection] = []
    for index in range(SECTION_COUNT):
        area = BASELINE_AREA_M2
        if index == INTERVENTION_SECTION_INDEX:
            area *= 1.0 + relative_change
        sections.append(
            TubeSection(
                length_m=TRACT_LENGTH_M / SECTION_COUNT,
                area_m2=area,
            )
        )
    return Tract1DGeometry(cavity_id="oral", sections=tuple(sections))


def _prepared(
    creature: CreatureSpec,
    relative_change: float,
) -> PreparedMorphology[Tract1DGeometry]:
    return prepare_tract1d(
        creature,
        _geometry(relative_change),
        provenance=PreparationProvenance(
            source="experiment-018",
            model="single-section-rest-area-sweep",
            notes=(
                f"intervention_section_index={INTERVENTION_SECTION_INDEX}",
                f"relative_area_change={relative_change:.17g}",
            ),
        ),
    )


def _canonical_score() -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=0.0,
                offset_s=0.3,
                target="oral",
                location=GESTURE_LOCATION,
                parameters=(
                    TaskParameter("target_area", TARGET_AREA_M2, "m2"),
                ),
            ),
        )
    )


def _score_payload(score: GestureScore) -> dict[str, Any]:
    return {
        "gestures": [
            {
                "task": gesture.task.value,
                "onset_s": gesture.onset_s,
                "offset_s": gesture.offset_s,
                "target": gesture.target,
                "location": gesture.location,
                "parameters": [
                    {
                        "name": parameter.name,
                        "value": parameter.value,
                        "unit": parameter.unit,
                    }
                    for parameter in gesture.parameters
                ],
            }
            for gesture in score.gestures
        ]
    }


def _score_sha256(score: GestureScore) -> str:
    payload = json.dumps(
        _score_payload(score),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _frequency_grid(
    start_hz: float,
    stop_hz: float,
    step_hz: float,
) -> np.ndarray:
    intervals = int(round((stop_hz - start_hz) / step_hz))
    if not math.isclose(
        start_hz + intervals * step_hz,
        stop_hz,
        rel_tol=0.0,
        abs_tol=1.0e-10,
    ):
        raise ValueError("frequency window must be divisible by grid step")
    return np.linspace(start_hz, stop_hz, intervals + 1, dtype=np.float64)


def _measure(
    *,
    morphology: PreparedMorphology[Tract1DGeometry],
    score: GestureScore,
    grid_step_hz: float,
) -> dict[str, Any]:
    backend = SegmentedTubeBackend()
    realizer = Tract1DRealizer()

    state: Tract1DGeometry | None = None
    status: FeasibilityStatus | None = None
    issues: tuple[dict[str, Any], ...] = ()
    peaks_hz: list[float] = []

    for window_hz in MODE_WINDOWS_HZ:
        frequencies = _frequency_grid(
            window_hz[0],
            window_hz[1],
            grid_step_hz,
        )
        result = simulate_snapshot(
            morphology=morphology,
            score=score,
            realizer=realizer,
            acoustic_backend=backend,
            acoustic_request=ImpedanceRequest(frequencies),
            time_s=EVALUATION_TIME_S,
        )

        current_status = result.realization.feasibility.status
        if status is None:
            status = current_status
            issues = tuple(
                {
                    "code": issue.code,
                    "message": issue.message,
                    "gesture_index": issue.gesture_index,
                }
                for issue in result.realization.feasibility.issues
            )
        elif current_status is not status:
            raise RuntimeError("status changed across observer windows")

        if current_status is not FeasibilityStatus.FEASIBLE:
            return {
                "status": current_status,
                "issues": issues,
                "state": None,
                "peaks_hz": (),
            }

        if result.realization.state is None or result.acoustics is None:
            raise RuntimeError("FEASIBLE condition lacks state or acoustics")

        if state is None:
            state = result.realization.state
        elif result.realization.state != state:
            raise RuntimeError("realized state changed across observer windows")

        magnitude = np.abs(result.acoustics.input_impedance_pa_s_m3)
        peak_hz = float(frequencies[int(np.nanargmax(magnitude))])
        peaks_hz.append(peak_hz)

    if status is None or state is None:
        raise RuntimeError("condition produced no measurement")

    return {
        "status": status,
        "issues": issues,
        "state": state,
        "peaks_hz": tuple(peaks_hz),
    }


def _modified_indices(
    prepared: Tract1DGeometry,
    realized: Tract1DGeometry,
) -> tuple[int, ...]:
    return tuple(
        index
        for index, (before, after) in enumerate(
            zip(prepared.sections, realized.sections, strict=True)
        )
        if before != after
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _oracle_index(relative_change: float) -> int:
    for index, value in enumerate(RELATIVE_CHANGES):
        if math.isclose(
            value,
            relative_change,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            return index
    raise KeyError(relative_change)


def _central_log_sensitivity(
    negative_hz: float,
    positive_hz: float,
    epsilon: float,
) -> float:
    return (
        math.log(positive_hz) - math.log(negative_hz)
    ) / (
        math.log(1.0 + epsilon) - math.log(1.0 - epsilon)
    )


def _log_frequency_uncertainty_bound(
    frequency_hz: float,
    floor_hz: float,
) -> float:
    if not 0.0 < floor_hz < frequency_hz:
        raise ValueError("log uncertainty requires 0 < floor < frequency")
    return math.log(frequency_hz / (frequency_hz - floor_hz))


def _sensitivity_uncertainty_bound(
    *,
    negative_hz: float,
    positive_hz: float,
    negative_floor_hz: float,
    positive_floor_hz: float,
    epsilon: float,
) -> float:
    denominator = abs(
        math.log(1.0 + epsilon) - math.log(1.0 - epsilon)
    )
    return (
        _log_frequency_uncertainty_bound(
            negative_hz,
            negative_floor_hz,
        )
        + _log_frequency_uncertainty_bound(
            positive_hz,
            positive_floor_hz,
        )
    ) / denominator


def _condition_key(task_condition: str, relative_change: float) -> tuple[str, float]:
    return (task_condition, round(relative_change, 8))


def _failure_decision(
    *,
    representation_ok: bool,
    morphology_ok: bool,
    invalid_present: bool,
    unsupported_present: bool,
    task_ok: bool,
    measurement_ok: bool,
    effects_ok: bool,
    monotonic_ok: bool,
    direction_ok: bool,
    sensitivity_ok: bool,
) -> str:
    if not representation_ok:
        return "REPRESENTATION_LEAK"
    if not morphology_ok:
        return "CAUSAL_TRACE_INCONSISTENT"
    if invalid_present:
        return "INVALID_REQUEST_REGRESSION"
    if unsupported_present:
        return "BACKEND_UNSUPPORTED"
    if not task_ok:
        return "TASK_REALIZATION_FAILED"
    if not measurement_ok:
        return "MEASUREMENT_REGRESSION"
    if not effects_ok:
        return "NUMERICALLY_UNRESOLVED"
    if not monotonic_ok:
        return "MONOTONICITY_FAILED"
    if not direction_ok:
        return "SENSITIVITY_DIRECTION_FAILED"
    if not sensitivity_ok:
        return "SENSITIVITY_ORACLE_MISMATCH"
    return SUPPORT_DECISION


def run(output_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename in (
        "conditions.csv",
        "task_residuals.csv",
        "effects.csv",
        "sensitivity.csv",
        "nonlinearity.csv",
        "decision.json",
    ):
        path = output_dir / filename
        if path.exists():
            path.unlink()

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    creature = _creature()
    score = _canonical_score()
    rest_score = GestureScore(())
    score_hash_before = _score_sha256(score)

    morphologies = {
        round(relative_change, 8): _prepared(creature, relative_change)
        for relative_change in RELATIVE_CHANGES
    }

    morphology_ok = True
    for relative_change in RELATIVE_CHANGES:
        morphology = morphologies[round(relative_change, 8)]
        expected_area = BASELINE_AREA_M2 * (1.0 + relative_change)
        morphology_ok = morphology_ok and morphology.creature is creature
        morphology_ok = morphology_ok and math.isclose(
            morphology.rest_state.total_length_m,
            TRACT_LENGTH_M,
            rel_tol=0.0,
            abs_tol=1.0e-14,
        )
        for index, section in enumerate(morphology.rest_state.sections):
            expected = (
                expected_area
                if index == INTERVENTION_SECTION_INDEX
                else BASELINE_AREA_M2
            )
            morphology_ok = morphology_ok and math.isclose(
                section.area_m2,
                expected,
                rel_tol=0.0,
                abs_tol=AREA_TOLERANCE_M2,
            )
            morphology_ok = morphology_ok and math.isclose(
                section.length_m,
                TRACT_LENGTH_M / SECTION_COUNT,
                rel_tol=0.0,
                abs_tol=1.0e-15,
            )

    measurements: dict[tuple[str, float], dict[str, Any]] = {}
    score_hashes: set[str] = set()

    for relative_change in RELATIVE_CHANGES:
        morphology = morphologies[round(relative_change, 8)]
        for task_condition, condition_score in (
            ("rest", rest_score),
            ("gesture", score),
        ):
            candidate = _measure(
                morphology=morphology,
                score=condition_score,
                grid_step_hz=CANDIDATE_GRID_STEP_HZ,
            )
            reference = _measure(
                morphology=morphology,
                score=condition_score,
                grid_step_hz=REFERENCE_GRID_STEP_HZ,
            )
            measurements[_condition_key(task_condition, relative_change)] = {
                "candidate": candidate,
                "reference": reference,
            }
            if task_condition == "gesture":
                score_hashes.add(_score_sha256(score))

    score_hash_after = _score_sha256(score)
    representation_ok = (
        score_hash_before == score_hash_after
        and score_hashes == {score_hash_before}
    )

    condition_rows: list[dict[str, Any]] = []
    floors: dict[tuple[str, float, int], float] = {}
    invalid_present = False
    unsupported_present = False
    all_feasible = True
    candidate_oracle_ok = True
    reference_oracle_ok = True
    finite_peaks_ok = True

    for relative_change in RELATIVE_CHANGES:
        oracle_index = _oracle_index(relative_change)
        area_m2 = BASELINE_AREA_M2 * (1.0 + relative_change)

        for task_condition in ("rest", "gesture"):
            measurement = measurements[
                _condition_key(task_condition, relative_change)
            ]
            candidate = measurement["candidate"]
            reference = measurement["reference"]

            statuses = (candidate["status"], reference["status"])
            invalid_present = invalid_present or any(
                status is FeasibilityStatus.INVALID for status in statuses
            )
            unsupported_present = unsupported_present or any(
                status is FeasibilityStatus.UNSUPPORTED for status in statuses
            )
            all_feasible = all_feasible and all(
                status is FeasibilityStatus.FEASIBLE for status in statuses
            )

            oracle_modes = oracle[
                "rest_resonances_hz"
                if task_condition == "rest"
                else "gesture_resonances_hz"
            ][oracle_index]

            for mode in range(1, 4):
                if (
                    candidate["status"] is FeasibilityStatus.FEASIBLE
                    and reference["status"] is FeasibilityStatus.FEASIBLE
                ):
                    candidate_peak = float(candidate["peaks_hz"][mode - 1])
                    reference_peak = float(reference["peaks_hz"][mode - 1])
                    oracle_hz = float(oracle_modes[mode - 1])
                    candidate_error = abs(candidate_peak - oracle_hz)
                    reference_error = abs(reference_peak - oracle_hz)
                    observer_delta = abs(candidate_peak - reference_peak)
                    floor_hz = max(CANDIDATE_GRID_STEP_HZ, observer_delta)
                    floors[(task_condition, round(relative_change, 8), mode)] = (
                        floor_hz
                    )

                    finite_peaks_ok = (
                        finite_peaks_ok
                        and math.isfinite(candidate_peak)
                        and math.isfinite(reference_peak)
                        and math.isfinite(oracle_hz)
                    )
                    candidate_oracle_ok = (
                        candidate_oracle_ok
                        and candidate_error
                        <= CANDIDATE_GRID_STEP_HZ + 1.0e-12
                    )
                    reference_oracle_ok = (
                        reference_oracle_ok
                        and reference_error
                        <= REFERENCE_GRID_STEP_HZ + 1.0e-12
                    )
                else:
                    candidate_peak = None
                    reference_peak = None
                    oracle_hz = float(oracle_modes[mode - 1])
                    candidate_error = None
                    reference_error = None
                    observer_delta = None
                    floor_hz = None

                condition_rows.append(
                    {
                        "relative_change": relative_change,
                        "intervention_section_area_m2": area_m2,
                        "task_condition": task_condition,
                        "mode": mode,
                        "candidate_status": candidate["status"].value,
                        "reference_status": reference["status"].value,
                        "oracle_hz": oracle_hz,
                        "candidate_peak_hz": candidate_peak,
                        "reference_peak_hz": reference_peak,
                        "candidate_abs_error_hz": candidate_error,
                        "reference_abs_error_hz": reference_error,
                        "candidate_vs_reference_abs_delta_hz": observer_delta,
                        "numerical_floor_hz": floor_hz,
                    }
                )

    _write_csv(output_dir / "conditions.csv", condition_rows)

    task_rows: list[dict[str, Any]] = []
    task_ok = all_feasible
    if all_feasible:
        for relative_change in RELATIVE_CHANGES:
            morphology = morphologies[round(relative_change, 8)]
            measurement = measurements[
                _condition_key("gesture", relative_change)
            ]
            candidate_state = measurement["candidate"]["state"]
            reference_state = measurement["reference"]["state"]
            if not isinstance(candidate_state, Tract1DGeometry):
                raise RuntimeError("gesture candidate lacks Tract1DGeometry")
            if not isinstance(reference_state, Tract1DGeometry):
                raise RuntimeError("gesture reference lacks Tract1DGeometry")

            selected_index = morphology.rest_state.section_index_at(
                GESTURE_LOCATION
            )
            modified = _modified_indices(
                morphology.rest_state,
                candidate_state,
            )
            target_area = score.gestures[0].parameter("target_area")
            if target_area is None:
                raise RuntimeError("canonical score lacks target_area")

            area_residual = abs(
                candidate_state.sections[selected_index].area_m2
                - target_area.value
            )
            intervention_area_residual = abs(
                candidate_state.sections[INTERVENTION_SECTION_INDEX].area_m2
                - morphology.rest_state.sections[
                    INTERVENTION_SECTION_INDEX
                ].area_m2
            )

            row = {
                "relative_change": relative_change,
                "score_sha256": score_hash_before,
                "candidate_reference_state_equal": (
                    candidate_state == reference_state
                ),
                "selected_section_index": selected_index,
                "modified_section_indices": ",".join(
                    str(index) for index in modified
                ),
                "target_area_m2": target_area.value,
                "realized_target_area_m2": (
                    candidate_state.sections[selected_index].area_m2
                ),
                "target_area_residual_m2": area_residual,
                "prepared_intervention_area_m2": (
                    morphology.rest_state.sections[
                        INTERVENTION_SECTION_INDEX
                    ].area_m2
                ),
                "realized_intervention_area_m2": (
                    candidate_state.sections[
                        INTERVENTION_SECTION_INDEX
                    ].area_m2
                ),
                "intervention_area_residual_m2": (
                    intervention_area_residual
                ),
            }
            task_rows.append(row)

            task_ok = (
                task_ok
                and bool(row["candidate_reference_state_equal"])
                and selected_index == GESTURE_SECTION_INDEX
                and modified == (GESTURE_SECTION_INDEX,)
                and area_residual <= AREA_TOLERANCE_M2
                and intervention_area_residual <= AREA_TOLERANCE_M2
            )

        _write_csv(output_dir / "task_residuals.csv", task_rows)

    measurement_ok = (
        all_feasible
        and finite_peaks_ok
        and candidate_oracle_ok
        and reference_oracle_ok
    )

    candidate_peaks: dict[tuple[str, float, int], float] = {}
    reference_peaks: dict[tuple[str, float, int], float] = {}
    if all_feasible:
        for row in condition_rows:
            task_condition = str(row["task_condition"])
            relative_change = round(float(row["relative_change"]), 8)
            mode = int(row["mode"])
            candidate_peaks[(task_condition, relative_change, mode)] = float(
                row["candidate_peak_hz"]
            )
            reference_peaks[(task_condition, relative_change, mode)] = float(
                row["reference_peak_hz"]
            )

    effects_rows: list[dict[str, Any]] = []
    effects_ok = all_feasible
    if all_feasible:
        for task_condition in ("rest", "gesture"):
            for relative_change in RELATIVE_CHANGES:
                if math.isclose(relative_change, 0.0, abs_tol=1.0e-12):
                    continue
                for mode in range(1, 4):
                    baseline_hz = candidate_peaks[
                        (task_condition, 0.0, mode)
                    ]
                    candidate_hz = candidate_peaks[
                        (task_condition, round(relative_change, 8), mode)
                    ]
                    floor_hz = max(
                        floors[(task_condition, 0.0, mode)],
                        floors[
                            (
                                task_condition,
                                round(relative_change, 8),
                                mode,
                            )
                        ],
                    )
                    effect_hz = abs(candidate_hz - baseline_hz)
                    ratio = effect_hz / floor_hz
                    effects_rows.append(
                        {
                            "task_condition": task_condition,
                            "relative_change": relative_change,
                            "mode": mode,
                            "baseline_hz": baseline_hz,
                            "candidate_hz": candidate_hz,
                            "effect_hz": effect_hz,
                            "numerical_floor_hz": floor_hz,
                            "effect_over_floor": ratio,
                        }
                    )
                    effects_ok = (
                        effects_ok and ratio > DISCRIMINATION_MARGIN
                    )
        _write_csv(output_dir / "effects.csv", effects_rows)

    monotonic_ok = all_feasible
    if all_feasible:
        for task_condition in ("rest", "gesture"):
            for mode in range(1, 4):
                trace = [
                    candidate_peaks[
                        (task_condition, round(relative_change, 8), mode)
                    ]
                    for relative_change in RELATIVE_CHANGES
                ]
                monotonic_ok = monotonic_ok and all(
                    trace[index + 1] < trace[index]
                    for index in range(len(trace) - 1)
                )

    sensitivity_rows: list[dict[str, Any]] = []
    direction_ok = all_feasible
    sensitivity_ok = all_feasible

    if all_feasible:
        for task_condition in ("rest", "gesture"):
            for epsilon in (0.05, 0.10):
                oracle_key = (
                    f"{task_condition}_sensitivity_eps_0_05"
                    if math.isclose(epsilon, 0.05)
                    else f"{task_condition}_sensitivity_eps_0_10"
                )
                for mode in range(1, 4):
                    candidate_s = _central_log_sensitivity(
                        candidate_peaks[
                            (task_condition, round(-epsilon, 8), mode)
                        ],
                        candidate_peaks[
                            (task_condition, round(epsilon, 8), mode)
                        ],
                        epsilon,
                    )
                    reference_s = _central_log_sensitivity(
                        reference_peaks[
                            (task_condition, round(-epsilon, 8), mode)
                        ],
                        reference_peaks[
                            (task_condition, round(epsilon, 8), mode)
                        ],
                        epsilon,
                    )
                    oracle_s = float(oracle[oracle_key][mode - 1])
                    candidate_error = abs(candidate_s - oracle_s)
                    reference_error = abs(reference_s - oracle_s)

                    sensitivity_rows.append(
                        {
                            "task_condition": task_condition,
                            "epsilon": epsilon,
                            "mode": mode,
                            "candidate_sensitivity": candidate_s,
                            "reference_sensitivity": reference_s,
                            "oracle_sensitivity": oracle_s,
                            "candidate_abs_error": candidate_error,
                            "reference_abs_error": reference_error,
                        }
                    )

                    direction_ok = (
                        direction_ok
                        and candidate_s < 0.0
                        and reference_s < 0.0
                    )
                    sensitivity_ok = (
                        sensitivity_ok
                        and candidate_error <= SENSITIVITY_TOLERANCE
                        and reference_error
                        <= REFERENCE_SENSITIVITY_TOLERANCE
                    )

        _write_csv(output_dir / "sensitivity.csv", sensitivity_rows)

    nonlinearity_rows: list[dict[str, Any]] = []
    if sensitivity_rows:
        def _find_sensitivity(
            task_condition: str,
            epsilon: float,
            mode: int,
        ) -> dict[str, Any]:
            for row in sensitivity_rows:
                if (
                    row["task_condition"] == task_condition
                    and math.isclose(
                        float(row["epsilon"]),
                        epsilon,
                        abs_tol=1.0e-12,
                    )
                    and int(row["mode"]) == mode
                ):
                    return row
            raise KeyError((task_condition, epsilon, mode))

        for task_condition in ("rest", "gesture"):
            oracle_n_key = (
                "rest_abs_nonlinearity"
                if task_condition == "rest"
                else "gesture_abs_nonlinearity"
            )
            for mode in range(1, 4):
                row5 = _find_sensitivity(task_condition, 0.05, mode)
                row10 = _find_sensitivity(task_condition, 0.10, mode)

                candidate_n = abs(
                    float(row10["candidate_sensitivity"])
                    - float(row5["candidate_sensitivity"])
                )
                reference_n = abs(
                    float(row10["reference_sensitivity"])
                    - float(row5["reference_sensitivity"])
                )
                oracle_n = float(oracle[oracle_n_key][mode - 1])
                uncertainty_5 = _sensitivity_uncertainty_bound(
                    negative_hz=candidate_peaks[
                        (task_condition, -0.05, mode)
                    ],
                    positive_hz=candidate_peaks[
                        (task_condition, 0.05, mode)
                    ],
                    negative_floor_hz=floors[
                        (task_condition, -0.05, mode)
                    ],
                    positive_floor_hz=floors[
                        (task_condition, 0.05, mode)
                    ],
                    epsilon=0.05,
                )
                uncertainty_10 = _sensitivity_uncertainty_bound(
                    negative_hz=candidate_peaks[
                        (task_condition, -0.10, mode)
                    ],
                    positive_hz=candidate_peaks[
                        (task_condition, 0.10, mode)
                    ],
                    negative_floor_hz=floors[
                        (task_condition, -0.10, mode)
                    ],
                    positive_floor_hz=floors[
                        (task_condition, 0.10, mode)
                    ],
                    epsilon=0.10,
                )
                sensitivity_observer_floor = uncertainty_5 + uncertainty_10
                resolution_ratio = oracle_n / sensitivity_observer_floor
                classification = (
                    "RESOLVED_AT_5X"
                    if resolution_ratio > DISCRIMINATION_MARGIN
                    else "BELOW_5X_OBSERVER_FLOOR"
                )

                nonlinearity_rows.append(
                    {
                        "task_condition": task_condition,
                        "mode": mode,
                        "candidate_abs_s10_minus_s5": candidate_n,
                        "reference_abs_s10_minus_s5": reference_n,
                        "oracle_abs_s10_minus_s5": oracle_n,
                        "sensitivity_uncertainty_bound_eps_0_05": uncertainty_5,
                        "sensitivity_uncertainty_bound_eps_0_10": uncertainty_10,
                        "sensitivity_observer_floor": (
                            sensitivity_observer_floor
                        ),
                        "oracle_nonlinearity_over_floor": resolution_ratio,
                        "classification": classification,
                    }
                )

        _write_csv(output_dir / "nonlinearity.csv", nonlinearity_rows)

    decision_name = _failure_decision(
        representation_ok=representation_ok,
        morphology_ok=morphology_ok,
        invalid_present=invalid_present,
        unsupported_present=unsupported_present,
        task_ok=task_ok,
        measurement_ok=measurement_ok,
        effects_ok=effects_ok,
        monotonic_ok=monotonic_ok,
        direction_ok=direction_ok,
        sensitivity_ok=sensitivity_ok,
    )

    decision: dict[str, Any] = {
        "decision": decision_name,
        "issue": 40,
        "experiment": 18,
        "research_question": (
            "whether one unchanged task preserves realization while a "
            "non-self-similar section-0 rest-area sweep produces resolved, "
            "monotone, independently predicted resonance sensitivity"
        ),
        "claim_scope": (
            "Fidelity-0 single-section prepared-area sensitivity only"
        ),
        "canonical_gesture": _score_payload(score),
        "representation": {
            "score_sha256_before": score_hash_before,
            "score_sha256_after": score_hash_after,
            "unchanged_across_gesture_conditions": representation_ok,
        },
        "morphology_intervention": {
            "parameter": "prepared_rest_section_0_area_m2",
            "baseline_area_m2": BASELINE_AREA_M2,
            "relative_changes": list(RELATIVE_CHANGES),
            "intervention_section_index": INTERVENTION_SECTION_INDEX,
            "gesture_section_index": GESTURE_SECTION_INDEX,
            "isolated_axis_check": morphology_ok,
        },
        "observer": {
            "candidate_grid_step_hz": CANDIDATE_GRID_STEP_HZ,
            "reference_grid_step_hz": REFERENCE_GRID_STEP_HZ,
            "mode_windows_hz": [list(window) for window in MODE_WINDOWS_HZ],
        },
        "gates": {
            "representation_invariant": representation_ok,
            "morphology_intervention_isolated": morphology_ok,
            "no_invalid_status": not invalid_present,
            "no_unsupported_status": not unsupported_present,
            "all_conditions_feasible": all_feasible,
            "gesture_task_residuals_preserved": task_ok,
            "candidate_peaks_match_wolfram_oracle": candidate_oracle_ok,
            "reference_peaks_match_wolfram_oracle": reference_oracle_ok,
            "all_nonzero_effects_exceed_5x_floor": effects_ok,
            "all_sweep_traces_monotone_decreasing": monotonic_ok,
            "all_sensitivity_directions_negative": direction_ok,
            "sensitivity_magnitudes_match_wolfram_oracle": sensitivity_ok,
        },
        "summary_metrics": {
            "minimum_effect_over_floor": (
                min(
                    float(row["effect_over_floor"])
                    for row in effects_rows
                )
                if effects_rows
                else None
            ),
            "maximum_candidate_peak_error_hz": max(
                (
                    float(row["candidate_abs_error_hz"])
                    for row in condition_rows
                    if row["candidate_abs_error_hz"] is not None
                ),
                default=None,
            ),
            "maximum_reference_peak_error_hz": max(
                (
                    float(row["reference_abs_error_hz"])
                    for row in condition_rows
                    if row["reference_abs_error_hz"] is not None
                ),
                default=None,
            ),
            "maximum_candidate_sensitivity_error": (
                max(
                    float(row["candidate_abs_error"])
                    for row in sensitivity_rows
                )
                if sensitivity_rows
                else None
            ),
            "maximum_reference_sensitivity_error": (
                max(
                    float(row["reference_abs_error"])
                    for row in sensitivity_rows
                )
                if sensitivity_rows
                else None
            ),
            "resolved_nonlinearity_count": sum(
                row["classification"] == "RESOLVED_AT_5X"
                for row in nonlinearity_rows
            ),
            "nonlinearity_diagnostic_count": len(nonlinearity_rows),
        },
        "causal_trace": {
            "morphology_delta": (
                "prepared section-0 rest area only, five-point sweep"
            ),
            "task": (
                "unchanged CONSTRICT location=0.65 target_area=2e-4 m2"
            ),
            "task_realization": (
                "section 6 only; section-0 body intervention preserved"
            ),
            "acoustic_observation": (
                "first three segmented-tube input-impedance resonances"
            ),
            "sensitivity": (
                "central log derivative with respect to section-0 rest area"
            ),
        },
        "wolfram_oracle": oracle,
        "limitations": [
            "single rigid lossless 1D local-area axis only",
            "prepared morphology area is backend-specific, not yet a universal CreatureSpec anatomy field",
            "one whole section is the intervention support at Fidelity-0",
            "nonlinear departure is diagnostic and may remain below observer resolution",
            "no phonetic identity, waveform, perception, tissue mechanics, material, source-filter coupling, or FSI claim",
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
        default=Path("experiment-018-output"),
    )
    args = parser.parse_args()

    decision = run(args.output_dir)
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    if decision["decision"] != SUPPORT_DECISION:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
