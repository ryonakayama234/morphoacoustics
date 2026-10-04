"""Experiment 020: stateful finite-time task realization (G1-B)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import time
from dataclasses import dataclass
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
)
from morphoacoustics.acoustics import SegmentedTube
from morphoacoustics.physical import Tract1DGeometry, TubeSection
from morphoacoustics.preparation import (
    PreparationProvenance,
    PreparedMorphology,
    prepare_tract1d,
)
from morphoacoustics.realization import Tract1DRealizer

TRACT_LENGTH_M = 0.17
SECTION_COUNT = 10
REST_AREA_M2 = 3.0e-4
GESTURE_LOCATION = 0.65
TARGET_SECTION_INDEX = 6
TARGET_AREA_M2 = 5.0e-5
SMOOTHNESS_LAMBDA = 1.0

OMEGA_PER_S = 25.0
DURATIONS_S = (0.04, 0.08, 0.12, 0.20, 0.32)
POST_RELEASE_TIMES_S = (0.05, 0.10)
TRACE_STEP_S = 0.01

CANDIDATE_GRID_STEP_HZ = 0.05
REFERENCE_GRID_STEP_HZ = 0.01
MODE_WINDOWS_HZ = (
    (360.0, 510.0),
    (1520.0, 1760.0),
    (2170.0, 2510.0),
)

STATE_ORACLE_TOLERANCE = 1.0e-10
DYNAMIC_ORACLE_TOLERANCE = 1.0e-12
PROPAGATION_TOLERANCE = 1.0e-12
FREQUENCY_ORACLE_TOLERANCE_HZ = 0.05
REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ = 0.01
DISCRIMINATION_MARGIN = 5.0
SHORT_DURATION_ERROR_MIN = 0.50
LONG_DURATION_ERROR_MAX = 0.005
MEMORY_MIN_ACTIVATION = 0.10

SUPPORT_DECISION = "SUPPORT_STATEFUL_FINITE_TIME_REALIZATION"
ORACLE_PATH = (
    Path(__file__).with_name("wolfram") / "stateful_dynamics_oracle.json"
)


@dataclass(frozen=True, slots=True)
class DynamicTaskState:
    """Experiment-local scalar task state."""

    activation: float
    velocity_per_s: float


class CriticallyDampedTaskDynamics:
    """Exact state transition for a reduced critically damped task variable."""

    def __init__(self, omega_per_s: float) -> None:
        if not math.isfinite(omega_per_s) or omega_per_s <= 0.0:
            raise ValueError("omega_per_s must be finite and > 0")
        self.omega_per_s = omega_per_s

    def advance(
        self,
        state: DynamicTaskState,
        *,
        target: float,
        duration_s: float,
    ) -> DynamicTaskState:
        if not math.isfinite(target):
            raise ValueError("target must be finite")
        if not math.isfinite(duration_s) or duration_s < 0.0:
            raise ValueError("duration_s must be finite and >= 0")

        omega = self.omega_per_s
        error0 = state.activation - target
        b = state.velocity_per_s + omega * error0
        decay = math.exp(-omega * duration_s)

        error = (error0 + b * duration_s) * decay
        velocity = (
            state.velocity_per_s
            - omega * b * duration_s
        ) * decay

        return DynamicTaskState(
            activation=target + error,
            velocity_per_s=velocity,
        )


def _creature() -> CreatureSpec:
    return CreatureSpec(
        name="g1b-stateful-finite-time-body",
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


def _geometry() -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id="oral",
        sections=tuple(
            TubeSection(
                length_m=TRACT_LENGTH_M / SECTION_COUNT,
                area_m2=REST_AREA_M2,
            )
            for _ in range(SECTION_COUNT)
        ),
    )


def _prepared(
    creature: CreatureSpec,
) -> PreparedMorphology[Tract1DGeometry]:
    return prepare_tract1d(
        creature,
        _geometry(),
        provenance=PreparationProvenance(
            source="experiment-020",
            model=(
                "uniform-rest-tract-with-experiment-local-stateful-task-dynamics"
            ),
            notes=(
                "production temporal and material schemas intentionally unchanged",
            ),
        ),
    )


def _score(duration_s: float) -> GestureScore:
    return GestureScore(
        (
            Gesture(
                task=Task.CONSTRICT,
                onset_s=0.0,
                offset_s=duration_s,
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


def _task_intent_payload(score: GestureScore) -> dict[str, Any]:
    return {
        "gestures": [
            {
                "task": gesture.task.value,
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


def _sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _solve_r1_equilibrium_ratios() -> np.ndarray:
    stiffness = np.ones(SECTION_COUNT, dtype=np.float64)
    difference = np.zeros(
        (SECTION_COUNT - 1, SECTION_COUNT),
        dtype=np.float64,
    )
    for index in range(SECTION_COUNT - 1):
        difference[index, index] = -1.0
        difference[index, index + 1] = 1.0

    hessian = (
        np.diag(stiffness)
        + SMOOTHNESS_LAMBDA * (difference.T @ difference)
    )
    target_vector = np.zeros(SECTION_COUNT, dtype=np.float64)
    target_vector[TARGET_SECTION_INDEX] = 1.0

    kkt = np.zeros(
        (SECTION_COUNT + 1, SECTION_COUNT + 1),
        dtype=np.float64,
    )
    kkt[:SECTION_COUNT, :SECTION_COUNT] = hessian
    kkt[:SECTION_COUNT, SECTION_COUNT] = target_vector
    kkt[SECTION_COUNT, :SECTION_COUNT] = target_vector

    target_ratio = TARGET_AREA_M2 / REST_AREA_M2
    rhs = np.concatenate(
        (stiffness, np.array([target_ratio], dtype=np.float64))
    )
    solution = np.linalg.solve(kkt, rhs)
    return np.asarray(solution[:SECTION_COUNT], dtype=np.float64)


def _dynamic_ratios(
    equilibrium_ratios: np.ndarray,
    activation: float,
) -> np.ndarray:
    return (
        np.ones(SECTION_COUNT, dtype=np.float64)
        + activation
        * (
            equilibrium_ratios
            - np.ones(SECTION_COUNT, dtype=np.float64)
        )
    )


def _geometry_from_ratios(
    rest: Tract1DGeometry,
    ratios: np.ndarray,
) -> Tract1DGeometry:
    return Tract1DGeometry(
        cavity_id=rest.cavity_id,
        sections=tuple(
            TubeSection(
                length_m=section.length_m,
                area_m2=section.area_m2 * float(ratios[index]),
            )
            for index, section in enumerate(rest.sections)
        ),
    )


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
    return np.linspace(
        start_hz,
        stop_hz,
        intervals + 1,
        dtype=np.float64,
    )


def _measure_resonances(
    state: Tract1DGeometry,
    grid_step_hz: float,
) -> tuple[float, ...]:
    tube = SegmentedTube.from_geometry(state)
    peaks: list[float] = []

    for start_hz, stop_hz in MODE_WINDOWS_HZ:
        frequencies = _frequency_grid(
            start_hz,
            stop_hz,
            grid_step_hz,
        )
        impedance = tube.input_impedance(frequencies)
        magnitude = np.abs(impedance)
        peaks.append(
            float(frequencies[int(np.nanargmax(magnitude))])
        )

    return tuple(peaks)


def _oracle_row(
    oracle: dict[str, Any],
    duration_s: float,
) -> dict[str, Any]:
    for row in oracle["duration_rows"]:
        if math.isclose(
            float(row["duration_s"]),
            duration_s,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            return dict(row)
    raise KeyError(duration_s)


def _state_at_time(
    dynamics: CriticallyDampedTaskDynamics,
    *,
    duration_s: float,
    time_s: float,
) -> DynamicTaskState:
    initial = DynamicTaskState(0.0, 0.0)
    if time_s <= duration_s:
        return dynamics.advance(
            initial,
            target=1.0,
            duration_s=time_s,
        )

    at_offset = dynamics.advance(
        initial,
        target=1.0,
        duration_s=duration_s,
    )
    return dynamics.advance(
        at_offset,
        target=0.0,
        duration_s=time_s - duration_s,
    )


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    if not rows:
        raise ValueError("cannot write empty CSV")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)


def _strictly_increasing(values: list[float]) -> bool:
    return all(
        values[index + 1] > values[index]
        for index in range(len(values) - 1)
    )


def _strictly_decreasing(values: list[float]) -> bool:
    return all(
        values[index + 1] < values[index]
        for index in range(len(values) - 1)
    )


def _failure_decision(
    *,
    representation_ok: bool,
    request_validation_ok: bool,
    r1_regression_ok: bool,
    dynamic_oracle_ok: bool,
    propagation_ok: bool,
    continuity_ok: bool,
    duration_ordering_ok: bool,
    memory_ok: bool,
    acoustic_oracle_ok: bool,
    discrimination_ok: bool,
) -> str:
    if not representation_ok:
        return "REPRESENTATION_LEAK"
    if not request_validation_ok:
        return "TASK_REQUEST_INVALID"
    if not r1_regression_ok:
        return "R1_REGRESSION"
    if not dynamic_oracle_ok:
        return "DYNAMIC_ORACLE_MISMATCH"
    if not propagation_ok:
        return "DYNAMIC_PROPAGATION_INCONSISTENT"
    if not continuity_ok:
        return "EVENT_CONTINUITY_FAILED"
    if not duration_ordering_ok:
        return "DURATION_ORDERING_FAILED"
    if not memory_ok:
        return "STATE_MEMORY_FAILED"
    if not acoustic_oracle_ok:
        return "ACOUSTIC_ORACLE_MISMATCH"
    if not discrimination_ok:
        return "MODEL_DISCRIMINATION_UNRESOLVED"
    return SUPPORT_DECISION


def run(output_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)

    for filename in (
        "duration_summary.csv",
        "state_trace.csv",
        "resonances.csv",
        "effects.csv",
        "decision.json",
    ):
        path = output_dir / filename
        if path.exists():
            path.unlink()

    oracle = json.loads(
        ORACLE_PATH.read_text(encoding="utf-8")
    )
    creature = _creature()
    morphology = _prepared(creature)
    dynamics = CriticallyDampedTaskDynamics(OMEGA_PER_S)

    equilibrium_ratios = _solve_r1_equilibrium_ratios()
    oracle_equilibrium = np.asarray(
        oracle["r1_equilibrium_state_ratio"],
        dtype=np.float64,
    )
    equilibrium_state_error = float(
        np.max(
            np.abs(
                equilibrium_ratios
                - oracle_equilibrium
            )
        )
    )

    equilibrium_geometry = _geometry_from_ratios(
        morphology.rest_state,
        equilibrium_ratios,
    )
    equilibrium_candidate_peaks = _measure_resonances(
        equilibrium_geometry,
        CANDIDATE_GRID_STEP_HZ,
    )
    equilibrium_reference_peaks = _measure_resonances(
        equilibrium_geometry,
        REFERENCE_GRID_STEP_HZ,
    )
    equilibrium_oracle_peaks = tuple(
        float(value)
        for value in oracle["r1_equilibrium_resonances_hz"]
    )

    equilibrium_peak_candidate_error = max(
        abs(measured - expected)
        for measured, expected in zip(
            equilibrium_candidate_peaks,
            equilibrium_oracle_peaks,
            strict=True,
        )
    )
    equilibrium_peak_reference_error = max(
        abs(measured - expected)
        for measured, expected in zip(
            equilibrium_reference_peaks,
            equilibrium_oracle_peaks,
            strict=True,
        )
    )

    r1_regression_ok = (
        equilibrium_state_error <= STATE_ORACLE_TOLERANCE
        and equilibrium_peak_candidate_error
        <= FREQUENCY_ORACLE_TOLERANCE_HZ
        and equilibrium_peak_reference_error
        <= REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ
        and abs(
            equilibrium_geometry.sections[
                TARGET_SECTION_INDEX
            ].area_m2
            - TARGET_AREA_M2
        )
        <= 1.0e-18
    )

    validator = Tract1DRealizer()
    task_intent_hashes: set[str] = set()
    representation_ok = True
    request_validation_ok = True

    duration_rows: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []
    resonance_rows: list[dict[str, Any]] = []
    effect_rows: list[dict[str, Any]] = []

    activations: list[float] = []
    task_errors: list[float] = []
    geometry_distances: list[float] = []
    release_50_activations: list[float] = []
    release_100_activations: list[float] = []
    acoustic_distances_by_mode: dict[int, list[float]] = {
        1: [],
        2: [],
        3: [],
    }

    max_dynamic_oracle_error = 0.0
    max_split_propagation_error = 0.0
    max_event_state_jump = 0.0
    max_candidate_peak_error = 0.0
    max_reference_peak_error = 0.0
    minimum_effect_over_floor = math.inf
    dynamic_oracle_ok = True
    propagation_ok = True
    continuity_ok = True
    acoustic_oracle_ok = True
    discrimination_ok = True

    initial = DynamicTaskState(0.0, 0.0)

    for duration_s in DURATIONS_S:
        score = _score(duration_s)
        full_payload = _score_payload(score)
        task_payload = _task_intent_payload(score)
        task_intent_hash = _sha256(task_payload)
        full_score_hash = _sha256(full_payload)
        task_intent_hashes.add(task_intent_hash)

        gesture = score.gestures[0]
        representation_ok = (
            representation_ok
            and math.isclose(
                gesture.onset_s,
                0.0,
                rel_tol=0.0,
                abs_tol=0.0,
            )
            and math.isclose(
                gesture.offset_s,
                duration_s,
                rel_tol=0.0,
                abs_tol=1.0e-15,
            )
            and gesture.task is Task.CONSTRICT
            and gesture.target == "oral"
            and math.isclose(
                float(gesture.location or -1.0),
                GESTURE_LOCATION,
                rel_tol=0.0,
                abs_tol=1.0e-15,
            )
        )

        validation = validator.realize_snapshot(
            morphology,
            score,
            duration_s / 2.0,
        )
        request_validation_ok = (
            request_validation_ok
            and validation.feasibility.status
            is FeasibilityStatus.FEASIBLE
            and validation.state is not None
            and morphology.rest_state.section_index_at(
                GESTURE_LOCATION
            )
            == TARGET_SECTION_INDEX
        )

        offset_minus = dynamics.advance(
            initial,
            target=1.0,
            duration_s=duration_s,
        )
        offset_plus = DynamicTaskState(
            activation=offset_minus.activation,
            velocity_per_s=offset_minus.velocity_per_s,
        )
        release_50 = dynamics.advance(
            offset_plus,
            target=0.0,
            duration_s=POST_RELEASE_TIMES_S[0],
        )
        release_100 = dynamics.advance(
            offset_plus,
            target=0.0,
            duration_s=POST_RELEASE_TIMES_S[1],
        )

        split = initial
        for _ in range(4):
            split = dynamics.advance(
                split,
                target=1.0,
                duration_s=duration_s / 4.0,
            )
        split_error = max(
            abs(
                split.activation
                - offset_minus.activation
            ),
            abs(
                split.velocity_per_s
                - offset_minus.velocity_per_s
            ),
        )
        max_split_propagation_error = max(
            max_split_propagation_error,
            split_error,
        )
        propagation_ok = (
            propagation_ok
            and split_error <= PROPAGATION_TOLERANCE
        )

        event_jump = max(
            abs(
                offset_plus.activation
                - offset_minus.activation
            ),
            abs(
                offset_plus.velocity_per_s
                - offset_minus.velocity_per_s
            ),
        )
        max_event_state_jump = max(
            max_event_state_jump,
            event_jump,
        )
        continuity_ok = (
            continuity_ok
            and event_jump <= DYNAMIC_ORACLE_TOLERANCE
        )

        oracle_row = _oracle_row(
            oracle,
            duration_s,
        )
        dynamic_pairs = (
            (
                offset_minus.activation,
                float(
                    oracle_row[
                        "activation_offset_minus"
                    ]
                ),
            ),
            (
                offset_minus.velocity_per_s,
                float(
                    oracle_row[
                        "velocity_offset_minus_per_s"
                    ]
                ),
            ),
            (
                1.0 - offset_minus.activation,
                float(
                    oracle_row[
                        "task_error_fraction_offset_minus"
                    ]
                ),
            ),
            (
                release_50.activation,
                float(
                    oracle_row[
                        "release_50ms_activation"
                    ]
                ),
            ),
            (
                release_50.velocity_per_s,
                float(
                    oracle_row[
                        "release_50ms_velocity_per_s"
                    ]
                ),
            ),
            (
                release_100.activation,
                float(
                    oracle_row[
                        "release_100ms_activation"
                    ]
                ),
            ),
            (
                release_100.velocity_per_s,
                float(
                    oracle_row[
                        "release_100ms_velocity_per_s"
                    ]
                ),
            ),
        )
        local_dynamic_error = max(
            abs(measured - expected)
            for measured, expected
            in dynamic_pairs
        )
        max_dynamic_oracle_error = max(
            max_dynamic_oracle_error,
            local_dynamic_error,
        )
        dynamic_oracle_ok = (
            dynamic_oracle_ok
            and local_dynamic_error
            <= DYNAMIC_ORACLE_TOLERANCE
        )

        dynamic_ratios = _dynamic_ratios(
            equilibrium_ratios,
            offset_minus.activation,
        )
        dynamic_geometry = _geometry_from_ratios(
            morphology.rest_state,
            dynamic_ratios,
        )
        target_area_at_offset = (
            dynamic_geometry.sections[
                TARGET_SECTION_INDEX
            ].area_m2
        )
        task_error_fraction = (
            1.0 - offset_minus.activation
        )
        geometry_distance = float(
            np.linalg.norm(
                dynamic_ratios - equilibrium_ratios
            )
        )

        activations.append(
            offset_minus.activation
        )
        task_errors.append(
            task_error_fraction
        )
        geometry_distances.append(
            geometry_distance
        )
        release_50_activations.append(
            release_50.activation
        )
        release_100_activations.append(
            release_100.activation
        )

        candidate_peaks = _measure_resonances(
            dynamic_geometry,
            CANDIDATE_GRID_STEP_HZ,
        )
        reference_peaks = _measure_resonances(
            dynamic_geometry,
            REFERENCE_GRID_STEP_HZ,
        )
        oracle_peaks = tuple(
            float(value)
            for value
            in oracle_row[
                "resonances_hz_offset_minus"
            ]
        )

        for mode, (
            candidate_hz,
            reference_hz,
            oracle_hz,
            r1_candidate_hz,
            r1_reference_hz,
            r1_oracle_hz,
        ) in enumerate(
            zip(
                candidate_peaks,
                reference_peaks,
                oracle_peaks,
                equilibrium_candidate_peaks,
                equilibrium_reference_peaks,
                equilibrium_oracle_peaks,
                strict=True,
            ),
            start=1,
        ):
            candidate_error = abs(
                candidate_hz - oracle_hz
            )
            reference_error = abs(
                reference_hz - oracle_hz
            )
            max_candidate_peak_error = max(
                max_candidate_peak_error,
                candidate_error,
            )
            max_reference_peak_error = max(
                max_reference_peak_error,
                reference_error,
            )
            acoustic_oracle_ok = (
                acoustic_oracle_ok
                and candidate_error
                <= FREQUENCY_ORACLE_TOLERANCE_HZ
                and reference_error
                <= REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ
            )

            local_floor = max(
                CANDIDATE_GRID_STEP_HZ,
                abs(
                    candidate_hz
                    - reference_hz
                ),
                abs(
                    r1_candidate_hz
                    - r1_reference_hz
                ),
            )
            observed_shift = (
                candidate_hz
                - r1_candidate_hz
            )
            oracle_shift = (
                oracle_hz
                - r1_oracle_hz
            )
            effect = abs(observed_shift)
            effect_over_floor = (
                effect / local_floor
            )
            minimum_effect_over_floor = min(
                minimum_effect_over_floor,
                effect_over_floor,
            )
            acoustic_distances_by_mode[
                mode
            ].append(effect)

            same_sign = (
                observed_shift == 0.0
                and oracle_shift == 0.0
            ) or (
                observed_shift * oracle_shift > 0.0
            )
            discrimination_ok = (
                discrimination_ok
                and effect_over_floor
                > DISCRIMINATION_MARGIN
                and same_sign
            )

            resonance_rows.append(
                {
                    "duration_s": duration_s,
                    "duration_ms": duration_s * 1000.0,
                    "mode": mode,
                    "candidate_peak_hz": candidate_hz,
                    "reference_peak_hz": reference_hz,
                    "oracle_peak_hz": oracle_hz,
                    "candidate_abs_error_hz": candidate_error,
                    "reference_abs_error_hz": reference_error,
                    "r1_equilibrium_candidate_hz": (
                        r1_candidate_hz
                    ),
                    "r1_equilibrium_reference_hz": (
                        r1_reference_hz
                    ),
                }
            )
            effect_rows.append(
                {
                    "duration_s": duration_s,
                    "duration_ms": duration_s * 1000.0,
                    "mode": mode,
                    "r2_candidate_hz": candidate_hz,
                    "r1_equilibrium_candidate_hz": (
                        r1_candidate_hz
                    ),
                    "observed_shift_from_r1_hz": (
                        observed_shift
                    ),
                    "oracle_shift_from_r1_hz": (
                        oracle_shift
                    ),
                    "numerical_floor_hz": local_floor,
                    "effect_over_floor": (
                        effect_over_floor
                    ),
                }
            )

        duration_rows.append(
            {
                "duration_s": duration_s,
                "duration_ms": duration_s * 1000.0,
                "omegaT": OMEGA_PER_S * duration_s,
                "task_intent_sha256": (
                    task_intent_hash
                ),
                "score_sha256": full_score_hash,
                "r1_task_error_fraction": 0.0,
                "r2_activation_offset_minus": (
                    offset_minus.activation
                ),
                "r2_velocity_offset_minus_per_s": (
                    offset_minus.velocity_per_s
                ),
                "r2_task_error_fraction_offset_minus": (
                    task_error_fraction
                ),
                "r2_target_area_m2_offset_minus": (
                    target_area_at_offset
                ),
                "r2_target_area_abs_error_m2": abs(
                    target_area_at_offset
                    - TARGET_AREA_M2
                ),
                "r2_geometry_l2_distance_from_r1": (
                    geometry_distance
                ),
                "offset_event_activation_jump": (
                    offset_plus.activation
                    - offset_minus.activation
                ),
                "offset_event_velocity_jump_per_s": (
                    offset_plus.velocity_per_s
                    - offset_minus.velocity_per_s
                ),
                "release_50ms_activation": (
                    release_50.activation
                ),
                "release_50ms_velocity_per_s": (
                    release_50.velocity_per_s
                ),
                "release_100ms_activation": (
                    release_100.activation
                ),
                "release_100ms_velocity_per_s": (
                    release_100.velocity_per_s
                ),
                "split_propagation_max_error": (
                    split_error
                ),
                "dynamic_oracle_max_error": (
                    local_dynamic_error
                ),
            }
        )

        max_trace_time = (
            duration_s
            + POST_RELEASE_TIMES_S[-1]
        )
        sample_count = int(
            round(
                max_trace_time
                / TRACE_STEP_S
            )
        )
        for sample_index in range(
            sample_count + 1
        ):
            trace_time = (
                sample_index * TRACE_STEP_S
            )
            state = _state_at_time(
                dynamics,
                duration_s=duration_s,
                time_s=trace_time,
            )
            target = (
                1.0
                if trace_time <= duration_s
                else 0.0
            )
            trace_rows.append(
                {
                    "duration_s": duration_s,
                    "time_s": trace_time,
                    "event_target": target,
                    "activation": (
                        state.activation
                    ),
                    "velocity_per_s": (
                        state.velocity_per_s
                    ),
                }
            )

    representation_ok = (
        representation_ok
        and len(task_intent_hashes) == 1
    )

    duration_ordering_ok = (
        _strictly_increasing(activations)
        and _strictly_decreasing(task_errors)
        and _strictly_decreasing(
            geometry_distances
        )
        and task_errors[0]
        > SHORT_DURATION_ERROR_MIN
        and task_errors[-1]
        < LONG_DURATION_ERROR_MAX
        and all(
            _strictly_decreasing(
                acoustic_distances_by_mode[mode]
            )
            for mode in (1, 2, 3)
        )
    )

    memory_ok = (
        min(release_50_activations)
        > MEMORY_MIN_ACTIVATION
        and min(release_100_activations)
        > MEMORY_MIN_ACTIVATION
        and _strictly_increasing(
            release_50_activations
        )
        and _strictly_increasing(
            release_100_activations
        )
    )

    _write_csv(
        output_dir / "duration_summary.csv",
        duration_rows,
    )
    _write_csv(
        output_dir / "state_trace.csv",
        trace_rows,
    )
    _write_csv(
        output_dir / "resonances.csv",
        resonance_rows,
    )
    _write_csv(
        output_dir / "effects.csv",
        effect_rows,
    )

    decision_name = _failure_decision(
        representation_ok=representation_ok,
        request_validation_ok=(
            request_validation_ok
        ),
        r1_regression_ok=r1_regression_ok,
        dynamic_oracle_ok=dynamic_oracle_ok,
        propagation_ok=propagation_ok,
        continuity_ok=continuity_ok,
        duration_ordering_ok=(
            duration_ordering_ok
        ),
        memory_ok=memory_ok,
        acoustic_oracle_ok=acoustic_oracle_ok,
        discrimination_ok=discrimination_ok,
    )

    decision: dict[str, Any] = {
        "decision": decision_name,
        "issue": 40,
        "experiment": 20,
        "research_question": (
            "whether a stateful finite-time task model makes "
            "duration-dependent predictions that differ from and "
            "converge toward the Experiment-019 quasi-static R1 reference"
        ),
        "claim_scope": (
            "single scalar critically damped experiment-local task state; "
            "not biological tissue, muscle, force, or general Task Dynamics"
        ),
        "representation_ok": (
            representation_ok
        ),
        "request_validation_ok": (
            request_validation_ok
        ),
        "r1_regression_ok": (
            r1_regression_ok
        ),
        "dynamic_oracle_ok": (
            dynamic_oracle_ok
        ),
        "propagation_ok": propagation_ok,
        "continuity_ok": continuity_ok,
        "duration_ordering_ok": (
            duration_ordering_ok
        ),
        "memory_ok": memory_ok,
        "acoustic_oracle_ok": (
            acoustic_oracle_ok
        ),
        "discrimination_ok": (
            discrimination_ok
        ),
        "task_intent_sha256": (
            next(iter(task_intent_hashes))
            if task_intent_hashes
            else None
        ),
        "r1_equilibrium_state_max_abs_error": (
            equilibrium_state_error
        ),
        "r1_equilibrium_candidate_peak_max_error_hz": (
            equilibrium_peak_candidate_error
        ),
        "r1_equilibrium_reference_peak_max_error_hz": (
            equilibrium_peak_reference_error
        ),
        "max_dynamic_oracle_error": (
            max_dynamic_oracle_error
        ),
        "max_split_propagation_error": (
            max_split_propagation_error
        ),
        "max_offset_event_state_jump": (
            max_event_state_jump
        ),
        "max_candidate_peak_error_hz": (
            max_candidate_peak_error
        ),
        "max_reference_peak_error_hz": (
            max_reference_peak_error
        ),
        "minimum_effect_over_floor": (
            minimum_effect_over_floor
        ),
        "short_duration_task_error_fraction": (
            task_errors[0]
        ),
        "long_duration_task_error_fraction": (
            task_errors[-1]
        ),
        "minimum_release_50ms_activation": (
            min(release_50_activations)
        ),
        "minimum_release_100ms_activation": (
            min(release_100_activations)
        ),
        "oracle_settling_95_ms": float(
            oracle["settling_95_ms"]
        ),
        "oracle_settling_99_ms": float(
            oracle["settling_99_ms"]
        ),
        "parameters": {
            "omega_per_s": OMEGA_PER_S,
            "durations_s": list(
                DURATIONS_S
            ),
            "post_release_times_s": list(
                POST_RELEASE_TIMES_S
            ),
            "tract_length_m": (
                TRACT_LENGTH_M
            ),
            "section_count": (
                SECTION_COUNT
            ),
            "rest_area_m2": REST_AREA_M2,
            "gesture_location": (
                GESTURE_LOCATION
            ),
            "target_section_index": (
                TARGET_SECTION_INDEX
            ),
            "target_area_m2": (
                TARGET_AREA_M2
            ),
            "smoothness_lambda": (
                SMOOTHNESS_LAMBDA
            ),
            "candidate_grid_step_hz": (
                CANDIDATE_GRID_STEP_HZ
            ),
            "reference_grid_step_hz": (
                REFERENCE_GRID_STEP_HZ
            ),
            "discrimination_margin": (
                DISCRIMINATION_MARGIN
            ),
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "elapsed_s": (
            time.perf_counter() - started
        ),
    }

    (
        output_dir / "decision.json"
    ).write_text(
        json.dumps(
            decision,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "experiment-020-output"
        ),
    )
    args = parser.parse_args()
    decision = run(args.output_dir)
    print(
        json.dumps(
            decision,
            indent=2,
            sort_keys=True,
        )
    )
    if (
        decision["decision"]
        != SUPPORT_DECISION
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
