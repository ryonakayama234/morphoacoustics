"""Experiment 016: same-task morphology covariance on two feasible bodies."""

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

SOUND_SPEED_M_S = 343.0
AIR_DENSITY_KG_M3 = 1.21
REST_AREA_M2 = 3.0e-4
TARGET_AREA_M2 = 2.0e-4
SECTION_COUNT = 10
GESTURE_LOCATION = 0.65
GESTURE_ONSET_S = 0.0
GESTURE_OFFSET_S = 0.3
EVALUATION_TIME_S = 0.1

M0_LENGTH_M = 0.17
LENGTH_SCALE = 1.10
M1_LENGTH_M = M0_LENGTH_M * LENGTH_SCALE
EXPECTED_FREQUENCY_SCALE = 1.0 / LENGTH_SCALE

CANDIDATE_GRID_STEP_HZ = 0.05
REFERENCE_GRID_STEP_HZ = 0.01
MODE_WINDOWS_HZ = (
    (400.0, 550.0),
    (1300.0, 1650.0),
    (2150.0, 2600.0),
)

AREA_RESIDUAL_TOLERANCE_M2 = 1.0e-15
LOCATION_RESIDUAL_TOLERANCE = 1.0e-12
PHYSICAL_SCALE_TOLERANCE = 1.0e-12
LENGTH_TOLERANCE_M = 1.0e-14
DISCRIMINATION_MARGIN = 5.0

SUPPORT_DECISION = "SUPPORT_TASK_MORPHOLOGY_COVARIANCE"
ORACLE_PATH = Path(__file__).with_name("wolfram") / "scale_covariance_oracle.json"


def _creature() -> CreatureSpec:
    return CreatureSpec(
        name="e1a-self-similar-body",
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


def _geometry(total_length_m: float) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(
                length_m=total_length_m / SECTION_COUNT,
                area_m2=REST_AREA_M2,
            )
            for _ in range(SECTION_COUNT)
        ),
    )


def _prepared(
    creature: CreatureSpec,
    *,
    label: str,
    total_length_m: float,
) -> PreparedMorphology[Tract1DGeometry]:
    return prepare_tract1d(
        creature,
        _geometry(total_length_m),
        provenance=PreparationProvenance(
            source="experiment-016",
            model="self-similar-uniform-tract",
            notes=(
                f"morphology_label={label}",
                f"total_length_m={total_length_m:.17g}",
                f"length_scale_from_m0={total_length_m / M0_LENGTH_M:.17g}",
            ),
        ),
    )


def _canonical_score() -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=GESTURE_ONSET_S,
                offset_s=GESTURE_OFFSET_S,
                target="oral",
                location=GESTURE_LOCATION,
                parameters=(
                    TaskParameter(
                        "target_area",
                        TARGET_AREA_M2,
                        "m2",
                    ),
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
    canonical = json.dumps(
        _score_payload(score),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


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
        raise ValueError("frequency window must be divisible by step")
    return np.linspace(start_hz, stop_hz, intervals + 1, dtype=np.float64)


def _measure_condition(
    *,
    morphology: PreparedMorphology[Tract1DGeometry],
    score: GestureScore,
    grid_step_hz: float,
) -> dict[str, Any]:
    backend = SegmentedTubeBackend(
        sound_speed_m_s=SOUND_SPEED_M_S,
        air_density_kg_m3=AIR_DENSITY_KG_M3,
    )
    realizer = Tract1DRealizer()

    peaks_hz: list[float] = []
    state: Tract1DGeometry | None = None
    status: FeasibilityStatus | None = None
    issues: list[dict[str, Any]] = []

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
            issues = [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "gesture_index": issue.gesture_index,
                }
                for issue in result.realization.feasibility.issues
            ]
        elif current_status is not status:
            raise RuntimeError("realization status changed across observer windows")

        if current_status is not FeasibilityStatus.FEASIBLE:
            return {
                "status": current_status.value,
                "issues": issues,
                "peaks_hz": [],
                "state": None,
                "score_sha256": _score_sha256(score),
            }

        if result.realization.state is None:
            raise RuntimeError("FEASIBLE realization returned no state")
        if result.acoustics is None:
            raise RuntimeError("FEASIBLE realization returned no acoustics")

        if state is None:
            state = result.realization.state
        elif result.realization.state != state:
            raise RuntimeError("physical realization changed across observer windows")

        magnitude = np.abs(result.acoustics.input_impedance_pa_s_m3)
        peak_hz = float(frequencies[int(np.nanargmax(magnitude))])
        peaks_hz.append(peak_hz)

    if status is None or state is None:
        raise RuntimeError("condition produced no measurement")

    return {
        "status": status.value,
        "issues": issues,
        "peaks_hz": peaks_hz,
        "state": state,
        "score_sha256": _score_sha256(score),
    }


def _section_center(
    geometry: Tract1DGeometry,
    section_index: int,
) -> tuple[float, float]:
    start_m = sum(
        section.length_m for section in geometry.sections[:section_index]
    )
    section = geometry.sections[section_index]
    center_m = start_m + 0.5 * section.length_m
    center_normalized = center_m / geometry.total_length_m
    return center_normalized, center_m


def _task_residual_row(
    *,
    label: str,
    morphology: PreparedMorphology[Tract1DGeometry],
    candidate: dict[str, Any],
    reference: dict[str, Any],
    score: GestureScore,
) -> dict[str, Any]:
    state = candidate["state"]
    reference_state = reference["state"]
    if not isinstance(state, Tract1DGeometry):
        raise RuntimeError("task residual requires a realized candidate state")
    if not isinstance(reference_state, Tract1DGeometry):
        raise RuntimeError("task residual requires a realized reference state")

    gesture = score.gestures[0]
    target_area = gesture.parameter("target_area")
    if gesture.location is None or target_area is None:
        raise RuntimeError("canonical CONSTRICT score is incomplete")

    section_index = morphology.rest_state.section_index_at(gesture.location)
    center_normalized, center_m = _section_center(state, section_index)

    modified_indices = tuple(
        index
        for index, (rest_section, realized_section) in enumerate(
            zip(morphology.rest_state.sections, state.sections, strict=True)
        )
        if not math.isclose(
            rest_section.area_m2,
            realized_section.area_m2,
            rel_tol=0.0,
            abs_tol=1.0e-18,
        )
        or not math.isclose(
            rest_section.length_m,
            realized_section.length_m,
            rel_tol=0.0,
            abs_tol=1.0e-18,
        )
    )

    return {
        "morphology": label,
        "score_sha256": candidate["score_sha256"],
        "candidate_reference_state_equal": state == reference_state,
        "target_location_normalized": gesture.location,
        "target_area_m2": target_area.value,
        "selected_section_index": section_index,
        "modified_section_indices": ",".join(str(index) for index in modified_indices),
        "realized_area_m2": state.sections[section_index].area_m2,
        "area_residual_m2": abs(
            state.sections[section_index].area_m2 - target_area.value
        ),
        "realized_center_normalized": center_normalized,
        "location_residual_normalized": abs(
            center_normalized - gesture.location
        ),
        "realized_center_m": center_m,
        "realized_section_length_m": state.sections[section_index].length_m,
        "realized_total_length_m": state.total_length_m,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _log_uncertainty_bound(frequency_hz: float, floor_hz: float) -> float:
    if not 0.0 < floor_hz < frequency_hz:
        raise ValueError("log uncertainty requires 0 < floor < frequency")
    return math.log(frequency_hz / (frequency_hz - floor_hz))


def _failure_decision(
    *,
    measurement_ok: bool,
    representation_ok: bool,
    task_ok: bool,
    physical_ok: bool,
    effects_ok: bool,
    scale_ok: bool,
    transfer_ok: bool,
) -> str:
    if not measurement_ok:
        return "MEASUREMENT_REGRESSION"
    if not representation_ok:
        return "REPRESENTATION_LEAK"
    if not task_ok:
        return "TASK_REALIZATION_FAILED"
    if not physical_ok:
        return "PHYSICAL_REALIZATION_INCONSISTENT"
    if not effects_ok:
        return "MORPHOLOGY_EFFECT_UNRESOLVED"
    if not scale_ok:
        return "SCALE_COVARIANCE_FAILED"
    if not transfer_ok:
        return "TASK_TRANSFER_FAILED"
    return SUPPORT_DECISION


def run(output_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))

    creature = _creature()
    m0 = _prepared(
        creature,
        label="M0",
        total_length_m=M0_LENGTH_M,
    )
    m1 = _prepared(
        creature,
        label="M1",
        total_length_m=M1_LENGTH_M,
    )

    rest_score = GestureScore(())
    canonical_score = _canonical_score()
    canonical_hash_before = _score_sha256(canonical_score)

    condition_specs = {
        "M0_rest": (m0, rest_score, "M0", "rest"),
        "M0_gesture": (m0, canonical_score, "M0", "gesture"),
        "M1_rest": (m1, rest_score, "M1", "rest"),
        "M1_gesture": (m1, canonical_score, "M1", "gesture"),
    }

    measurements: dict[str, dict[str, Any]] = {}
    for label, (morphology, score, _, _) in condition_specs.items():
        measurements[label] = {
            "candidate": _measure_condition(
                morphology=morphology,
                score=score,
                grid_step_hz=CANDIDATE_GRID_STEP_HZ,
            ),
            "reference": _measure_condition(
                morphology=morphology,
                score=score,
                grid_step_hz=REFERENCE_GRID_STEP_HZ,
            ),
        }

    canonical_hash_after = _score_sha256(canonical_score)
    gesture_hashes = {
        measurements["M0_gesture"]["candidate"]["score_sha256"],
        measurements["M1_gesture"]["candidate"]["score_sha256"],
        measurements["M0_gesture"]["reference"]["score_sha256"],
        measurements["M1_gesture"]["reference"]["score_sha256"],
    }
    representation_ok = (
        canonical_hash_before == canonical_hash_after
        and gesture_hashes == {canonical_hash_before}
    )

    feasibility_ok = all(
        measurement[observer]["status"] == FeasibilityStatus.FEASIBLE.value
        and len(measurement[observer]["peaks_hz"]) == 3
        for measurement in measurements.values()
        for observer in ("candidate", "reference")
    )

    condition_rows: list[dict[str, Any]] = []
    floors: dict[tuple[str, int], float] = {}
    candidate_oracle_ok = feasibility_ok
    reference_oracle_ok = feasibility_ok
    finite_ok = feasibility_ok

    for label, (_, _, morphology_label, task_condition) in condition_specs.items():
        candidate = measurements[label]["candidate"]
        reference = measurements[label]["reference"]
        oracle_modes = oracle["conditions"][label]

        for mode in range(1, 4):
            candidate_peak = (
                float(candidate["peaks_hz"][mode - 1])
                if feasibility_ok
                else None
            )
            reference_peak = (
                float(reference["peaks_hz"][mode - 1])
                if feasibility_ok
                else None
            )
            oracle_hz = float(oracle_modes[mode - 1])

            if candidate_peak is None or reference_peak is None:
                floor_hz = None
                candidate_error = None
                reference_error = None
                observer_delta = None
            else:
                candidate_error = abs(candidate_peak - oracle_hz)
                reference_error = abs(reference_peak - oracle_hz)
                observer_delta = abs(candidate_peak - reference_peak)
                floor_hz = max(CANDIDATE_GRID_STEP_HZ, observer_delta)
                floors[(label, mode)] = floor_hz

                candidate_oracle_ok = (
                    candidate_oracle_ok
                    and candidate_error <= CANDIDATE_GRID_STEP_HZ + 1.0e-12
                )
                reference_oracle_ok = (
                    reference_oracle_ok
                    and reference_error <= REFERENCE_GRID_STEP_HZ + 1.0e-12
                )
                finite_ok = (
                    finite_ok
                    and math.isfinite(candidate_peak)
                    and math.isfinite(reference_peak)
                    and math.isfinite(oracle_hz)
                )

            condition_rows.append(
                {
                    "condition": label,
                    "morphology": morphology_label,
                    "task_condition": task_condition,
                    "mode": mode,
                    "candidate_status": candidate["status"],
                    "reference_status": reference["status"],
                    "score_sha256": candidate["score_sha256"],
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

    measurement_ok = (
        feasibility_ok
        and finite_ok
        and candidate_oracle_ok
        and reference_oracle_ok
    )

    task_rows: list[dict[str, Any]] = []
    task_ok = feasibility_ok
    physical_ok = feasibility_ok
    morphology_axis_ok = (
        m0.creature is m1.creature
        and len(m0.rest_state.sections) == len(m1.rest_state.sections) == SECTION_COUNT
        and all(
            math.isclose(
                section0.area_m2,
                section1.area_m2,
                rel_tol=0.0,
                abs_tol=1.0e-18,
            )
            for section0, section1 in zip(
                m0.rest_state.sections,
                m1.rest_state.sections,
                strict=True,
            )
        )
        and all(
            math.isclose(
                section1.length_m / section0.length_m,
                LENGTH_SCALE,
                rel_tol=0.0,
                abs_tol=PHYSICAL_SCALE_TOLERANCE,
            )
            for section0, section1 in zip(
                m0.rest_state.sections,
                m1.rest_state.sections,
                strict=True,
            )
        )
        and math.isclose(
            m1.rest_state.total_length_m / m0.rest_state.total_length_m,
            LENGTH_SCALE,
            rel_tol=0.0,
            abs_tol=PHYSICAL_SCALE_TOLERANCE,
        )
    )

    if feasibility_ok:
        task_rows = [
            _task_residual_row(
                label="M0",
                morphology=m0,
                candidate=measurements["M0_gesture"]["candidate"],
                reference=measurements["M0_gesture"]["reference"],
                score=canonical_score,
            ),
            _task_residual_row(
                label="M1",
                morphology=m1,
                candidate=measurements["M1_gesture"]["candidate"],
                reference=measurements["M1_gesture"]["reference"],
                score=canonical_score,
            ),
        ]
        _write_csv(output_dir / "task_residuals.csv", task_rows)

        task_ok = all(
            bool(row["candidate_reference_state_equal"])
            and int(row["selected_section_index"]) == 6
            and str(row["modified_section_indices"]) == "6"
            and float(row["area_residual_m2"]) <= AREA_RESIDUAL_TOLERANCE_M2
            and float(row["location_residual_normalized"])
            <= LOCATION_RESIDUAL_TOLERANCE
            for row in task_rows
        )

        m0_task, m1_task = task_rows
        axial_scale = (
            float(m1_task["realized_center_m"])
            / float(m0_task["realized_center_m"])
        )
        section_length_scale = (
            float(m1_task["realized_section_length_m"])
            / float(m0_task["realized_section_length_m"])
        )

        oracle_axial = oracle["physical_prediction"]["target_axial_position_m"]
        oracle_section_lengths = oracle["physical_prediction"][
            "constricted_section_length_m"
        ]
        physical_oracle_ok = (
            math.isclose(
                float(m0_task["realized_center_m"]),
                float(oracle_axial[0]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            )
            and math.isclose(
                float(m1_task["realized_center_m"]),
                float(oracle_axial[1]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            )
            and math.isclose(
                float(m0_task["realized_section_length_m"]),
                float(oracle_section_lengths[0]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            )
            and math.isclose(
                float(m1_task["realized_section_length_m"]),
                float(oracle_section_lengths[1]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            )
        )

        realized_length_ok = (
            math.isclose(
                float(m0_task["realized_total_length_m"]),
                M0_LENGTH_M,
                rel_tol=0.0,
                abs_tol=LENGTH_TOLERANCE_M,
            )
            and math.isclose(
                float(m1_task["realized_total_length_m"]),
                M1_LENGTH_M,
                rel_tol=0.0,
                abs_tol=LENGTH_TOLERANCE_M,
            )
        )

        physical_ok = (
            morphology_axis_ok
            and physical_oracle_ok
            and realized_length_ok
            and math.isclose(
                axial_scale,
                LENGTH_SCALE,
                rel_tol=0.0,
                abs_tol=PHYSICAL_SCALE_TOLERANCE,
            )
            and math.isclose(
                section_length_scale,
                LENGTH_SCALE,
                rel_tol=0.0,
                abs_tol=PHYSICAL_SCALE_TOLERANCE,
            )
        )
    else:
        axial_scale = None
        section_length_scale = None
        physical_oracle_ok = False
        realized_length_ok = False

    effects_rows: list[dict[str, Any]] = []
    covariance_rows: list[dict[str, Any]] = []
    effects_ok = feasibility_ok
    scale_ok = feasibility_ok
    transfer_ok = feasibility_ok

    if feasibility_ok:
        peaks = {
            label: [
                float(value)
                for value in measurements[label]["candidate"]["peaks_hz"]
            ]
            for label in condition_specs
        }

        for mode in range(1, 4):
            index = mode - 1

            for task_condition in ("rest", "gesture"):
                label0 = f"M0_{task_condition}"
                label1 = f"M1_{task_condition}"
                floor_hz = max(
                    floors[(label0, mode)],
                    floors[(label1, mode)],
                )
                effect_hz = abs(peaks[label1][index] - peaks[label0][index])
                effect_over_floor = effect_hz / floor_hz
                effects_rows.append(
                    {
                        "effect_family": "morphology",
                        "scope": task_condition,
                        "mode": mode,
                        "effect_hz": effect_hz,
                        "numerical_floor_hz": floor_hz,
                        "effect_over_floor": effect_over_floor,
                    }
                )
                effects_ok = (
                    effects_ok
                    and effect_over_floor > DISCRIMINATION_MARGIN
                )

            for morphology_label in ("M0", "M1"):
                rest_label = f"{morphology_label}_rest"
                gesture_label = f"{morphology_label}_gesture"
                floor_hz = max(
                    floors[(rest_label, mode)],
                    floors[(gesture_label, mode)],
                )
                effect_hz = abs(
                    peaks[gesture_label][index] - peaks[rest_label][index]
                )
                effect_over_floor = effect_hz / floor_hz
                effects_rows.append(
                    {
                        "effect_family": "gesture",
                        "scope": morphology_label,
                        "mode": mode,
                        "effect_hz": effect_hz,
                        "numerical_floor_hz": floor_hz,
                        "effect_over_floor": effect_over_floor,
                    }
                )
                effects_ok = (
                    effects_ok
                    and effect_over_floor > DISCRIMINATION_MARGIN
                )

            rest_scale_residual = abs(
                peaks["M1_rest"][index]
                - peaks["M0_rest"][index] / LENGTH_SCALE
            )
            rest_scale_budget = (
                floors[("M1_rest", mode)]
                + floors[("M0_rest", mode)] / LENGTH_SCALE
            )
            gesture_scale_residual = abs(
                peaks["M1_gesture"][index]
                - peaks["M0_gesture"][index] / LENGTH_SCALE
            )
            gesture_scale_budget = (
                floors[("M1_gesture", mode)]
                + floors[("M0_gesture", mode)] / LENGTH_SCALE
            )

            log_effect_m0 = math.log(
                peaks["M0_gesture"][index] / peaks["M0_rest"][index]
            )
            log_effect_m1 = math.log(
                peaks["M1_gesture"][index] / peaks["M1_rest"][index]
            )
            log_effect_difference = abs(log_effect_m1 - log_effect_m0)
            log_uncertainty_budget = sum(
                _log_uncertainty_bound(
                    peaks[label][index],
                    floors[(label, mode)],
                )
                for label in (
                    "M0_rest",
                    "M0_gesture",
                    "M1_rest",
                    "M1_gesture",
                )
            )

            covariance_rows.append(
                {
                    "mode": mode,
                    "expected_frequency_scale": EXPECTED_FREQUENCY_SCALE,
                    "rest_frequency_ratio_m1_over_m0": (
                        peaks["M1_rest"][index] / peaks["M0_rest"][index]
                    ),
                    "rest_scale_residual_hz": rest_scale_residual,
                    "rest_scale_budget_hz": rest_scale_budget,
                    "gesture_frequency_ratio_m1_over_m0": (
                        peaks["M1_gesture"][index]
                        / peaks["M0_gesture"][index]
                    ),
                    "gesture_scale_residual_hz": gesture_scale_residual,
                    "gesture_scale_budget_hz": gesture_scale_budget,
                    "log_gesture_effect_m0": log_effect_m0,
                    "log_gesture_effect_m1": log_effect_m1,
                    "abs_log_effect_difference": log_effect_difference,
                    "log_uncertainty_budget": log_uncertainty_budget,
                }
            )

            scale_ok = (
                scale_ok
                and rest_scale_residual <= rest_scale_budget + 1.0e-12
                and gesture_scale_residual <= gesture_scale_budget + 1.0e-12
            )
            transfer_ok = (
                transfer_ok
                and log_effect_difference
                <= log_uncertainty_budget + 1.0e-15
            )

        _write_csv(output_dir / "effects.csv", effects_rows)
        _write_csv(output_dir / "covariance.csv", covariance_rows)

    decision_name = _failure_decision(
        measurement_ok=measurement_ok,
        representation_ok=representation_ok,
        task_ok=task_ok,
        physical_ok=physical_ok,
        effects_ok=effects_ok,
        scale_ok=scale_ok,
        transfer_ok=transfer_ok,
    )

    decision: dict[str, Any] = {
        "decision": decision_name,
        "issue": 40,
        "experiment": 16,
        "research_question": (
            "whether one unchanged non-empty task-level CONSTRICT Gesture "
            "transfers across a 10% prepared-tract length intervention while "
            "preserving predicted dimensionless acoustic task effects"
        ),
        "claim_scope": (
            "self-similar Fidelity-0 prepared-morphology covariance only"
        ),
        "canonical_gesture": _score_payload(canonical_score),
        "representation": {
            "score_sha256_before": canonical_hash_before,
            "score_sha256_after": canonical_hash_after,
            "gesture_condition_hashes": sorted(gesture_hashes),
            "unchanged_and_identical_across_bodies": representation_ok,
        },
        "morphology_intervention": {
            "m0_length_m": M0_LENGTH_M,
            "m1_length_m": M1_LENGTH_M,
            "length_scale_m1_over_m0": LENGTH_SCALE,
            "expected_frequency_scale_m1_over_m0": EXPECTED_FREQUENCY_SCALE,
            "same_creature_object": m0.creature is m1.creature,
            "same_section_count": (
                len(m0.rest_state.sections)
                == len(m1.rest_state.sections)
                == SECTION_COUNT
            ),
            "same_rest_areas": all(
                section0.area_m2 == section1.area_m2
                for section0, section1 in zip(
                    m0.rest_state.sections,
                    m1.rest_state.sections,
                    strict=True,
                )
            ),
            "one_dimensional_axis_check": morphology_axis_ok,
        },
        "physical_realization": {
            "axial_center_scale_m1_over_m0": axial_scale,
            "section_length_scale_m1_over_m0": section_length_scale,
            "physical_oracle_match": physical_oracle_ok,
            "realized_total_length_match": realized_length_ok,
        },
        "observer": {
            "candidate_grid_step_hz": CANDIDATE_GRID_STEP_HZ,
            "reference_grid_step_hz": REFERENCE_GRID_STEP_HZ,
            "mode_windows_hz": [list(window) for window in MODE_WINDOWS_HZ],
            "section_count_not_used_as_numerical_control": True,
        },
        "gates": {
            "feasibility_all_four_conditions": feasibility_ok,
            "finite_peaks": finite_ok,
            "candidate_peaks_match_wolfram_oracle": candidate_oracle_ok,
            "reference_peaks_match_wolfram_oracle": reference_oracle_ok,
            "representation_invariant": representation_ok,
            "task_residuals_within_tolerance": task_ok,
            "physical_realization_scales_with_body": physical_ok,
            "morphology_and_gesture_effects_exceed_5x_floor": effects_ok,
            "absolute_frequency_scale_covariance": scale_ok,
            "dimensionless_task_effect_preserved": transfer_ok,
        },
        "summary_metrics": {
            "minimum_effect_over_floor": (
                min(float(row["effect_over_floor"]) for row in effects_rows)
                if effects_rows
                else None
            ),
            "maximum_rest_scale_residual_hz": (
                max(
                    float(row["rest_scale_residual_hz"])
                    for row in covariance_rows
                )
                if covariance_rows
                else None
            ),
            "maximum_gesture_scale_residual_hz": (
                max(
                    float(row["gesture_scale_residual_hz"])
                    for row in covariance_rows
                )
                if covariance_rows
                else None
            ),
            "maximum_abs_log_effect_difference": (
                max(
                    float(row["abs_log_effect_difference"])
                    for row in covariance_rows
                )
                if covariance_rows
                else None
            ),
            "minimum_log_uncertainty_budget": (
                min(
                    float(row["log_uncertainty_budget"])
                    for row in covariance_rows
                )
                if covariance_rows
                else None
            ),
        },
        "wolfram_oracle": oracle,
        "limitations": [
            "tract length remains a backend-specific prepared-geometry axis rather than a universal CreatureSpec parameter",
            "self-similar uniform 1D geometry only",
            "CONSTRICT changes one whole Fidelity-0 section rather than a continuous tissue region",
            "no source, waveform, perception, phonetic identity, material mechanics, or source-filter coupling claim",
            "scale covariance is expected specifically because this fixture is geometrically self-similar",
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
        default=Path("experiment-016-output"),
    )
    args = parser.parse_args()

    decision = run(args.output_dir)
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    if decision["decision"] != SUPPORT_DECISION:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
