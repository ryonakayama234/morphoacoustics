"""Experiment 022: shared-body multi-Gesture interaction."""

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
SMOOTHNESS_LAMBDA = 1.0
OMEGA_PER_S = 25.0

GESTURE_A_LOCATION = 0.65
GESTURE_A_SECTION = 6
GESTURE_A_AREA_M2 = 5.0e-5
GESTURE_A_ONSET_S = 0.0
GESTURE_A_OFFSET_S = 0.20

GESTURE_B_LOCATION = 0.45
GESTURE_B_SECTION = 4
GESTURE_B_AREA_M2 = 1.0e-4
GESTURE_B_ONSET_S = 0.08
GESTURE_B_OFFSET_S = 0.28

END_TIME_S = 0.40
PRIMARY_TIME_S = 0.20
TRACE_STEP_S = 0.01

CANDIDATE_GRID_STEP_HZ = 0.05
REFERENCE_GRID_STEP_HZ = 0.01
MODE_WINDOWS_HZ = (
    (330.0, 430.0),
    (1640.0, 1780.0),
    (2180.0, 2380.0),
)

EQUILIBRIUM_TOLERANCE = 1.0e-10
TASK_RESIDUAL_TOLERANCE = 1.0e-12
ORACLE_TOLERANCE = 1.0e-11
PROPAGATION_TOLERANCE = 1.0e-11
EVENT_CONTINUITY_TOLERANCE = 1.0e-12
NONADDITIVITY_MIN = 0.10
EQUILIBRIUM_L2_MIN = 0.10
TRANSIENT_NORMALIZED_MIN = 0.10
TRANSIENT_L2_MIN = 0.10
TRANSIENT_VELOCITY_L2_MIN = 0.5
FREQUENCY_ORACLE_TOLERANCE_HZ = 0.05
REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ = 0.01
DISCRIMINATION_MARGIN = 5.0

SUPPORT_DECISION = "SUPPORT_SHARED_BODY_MULTI_GESTURE_INTERACTION"
ORACLE_PATH = (
    Path(__file__).with_name("wolfram")
    / "shared_body_multigesture_oracle.json"
)

ARTIFACT_NAMES = (
    "equilibrium_states.csv",
    "equilibrium_effects.csv",
    "state_trace.csv",
    "event_summary.csv",
    "task_residuals.csv",
    "resonances.csv",
    "acoustic_effects.csv",
    "conflict_case.json",
    "decision.json",
)


@dataclass(frozen=True, slots=True)
class VectorState:
    ratios: np.ndarray
    velocity_per_s: np.ndarray


class ModalCriticallyDampedDynamics:
    """Exact Experiment-021 modal transition reused unchanged."""

    def __init__(self, hessian: np.ndarray, omega_per_s: float) -> None:
        matrix = np.asarray(hessian, dtype=np.float64)
        if matrix.shape != (SECTION_COUNT, SECTION_COUNT):
            raise ValueError("unexpected Hessian shape")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("Hessian must be finite")
        if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1.0e-14):
            raise ValueError("Hessian must be symmetric")
        if not math.isfinite(omega_per_s) or omega_per_s <= 0.0:
            raise ValueError("omega_per_s must be finite and > 0")

        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        if np.any(eigenvalues <= 0.0):
            raise ValueError("Hessian must be positive definite")

        self.eigenvalues = eigenvalues
        self.eigenvectors = eigenvectors
        self.modal_rates_per_s = omega_per_s * np.sqrt(eigenvalues)

    def advance(
        self,
        state: VectorState,
        *,
        target_ratios: np.ndarray,
        duration_s: float,
    ) -> VectorState:
        if not math.isfinite(duration_s) or duration_s < 0.0:
            raise ValueError("duration_s must be finite and >= 0")

        target = np.asarray(target_ratios, dtype=np.float64)
        ratios = np.asarray(state.ratios, dtype=np.float64)
        velocity = np.asarray(state.velocity_per_s, dtype=np.float64)
        if (
            target.shape != (SECTION_COUNT,)
            or ratios.shape != (SECTION_COUNT,)
            or velocity.shape != (SECTION_COUNT,)
        ):
            raise ValueError("unexpected state shape")
        if not (
            np.all(np.isfinite(target))
            and np.all(np.isfinite(ratios))
            and np.all(np.isfinite(velocity))
        ):
            raise ValueError("state must be finite")

        vectors = self.eigenvectors
        rates = self.modal_rates_per_s
        error0 = vectors.T @ (ratios - target)
        velocity0 = vectors.T @ velocity
        b = velocity0 + rates * error0
        decay = np.exp(-rates * duration_s)

        error = (error0 + b * duration_s) * decay
        modal_velocity = (
            velocity0 - rates * b * duration_s
        ) * decay
        return VectorState(
            ratios=np.asarray(
                target + vectors @ error,
                dtype=np.float64,
            ),
            velocity_per_s=np.asarray(
                vectors @ modal_velocity,
                dtype=np.float64,
            ),
        )


def _creature() -> CreatureSpec:
    return CreatureSpec(
        name="g1d-shared-body-multigesture",
        cavities=(
            CavitySpec(
                id="oral",
                kind=CavityKind.ORAL,
            ),
        ),
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
            source="experiment-022",
            model=(
                "uniform-rest-tract-with-experiment-local-"
                "shared-body-multigesture-dynamics"
            ),
            notes=(
                "production multi-Gesture and material APIs unchanged",
            ),
        ),
    )


def _gesture(
    *,
    location: float,
    target_area_m2: float,
    onset_s: float,
    offset_s: float,
) -> Gesture:
    return Gesture(
        task=Task.CONSTRICT,
        onset_s=onset_s,
        offset_s=offset_s,
        target="oral",
        location=location,
        parameters=(
            TaskParameter(
                "target_area",
                target_area_m2,
                "m2",
            ),
        ),
    )


def _gesture_a() -> Gesture:
    return _gesture(
        location=GESTURE_A_LOCATION,
        target_area_m2=GESTURE_A_AREA_M2,
        onset_s=GESTURE_A_ONSET_S,
        offset_s=GESTURE_A_OFFSET_S,
    )


def _gesture_b() -> Gesture:
    return _gesture(
        location=GESTURE_B_LOCATION,
        target_area_m2=GESTURE_B_AREA_M2,
        onset_s=GESTURE_B_ONSET_S,
        offset_s=GESTURE_B_OFFSET_S,
    )


def _conflicting_gesture() -> Gesture:
    return _gesture(
        location=GESTURE_A_LOCATION,
        target_area_m2=GESTURE_B_AREA_M2,
        onset_s=GESTURE_B_ONSET_S,
        offset_s=GESTURE_A_OFFSET_S,
    )


def _gesture_payload(gesture: Gesture) -> dict[str, Any]:
    return {
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


def _sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _difference_operator() -> np.ndarray:
    difference = np.zeros(
        (SECTION_COUNT - 1, SECTION_COUNT),
        dtype=np.float64,
    )
    for index in range(SECTION_COUNT - 1):
        difference[index, index] = -1.0
        difference[index, index + 1] = 1.0
    return difference


def _hessian() -> np.ndarray:
    difference = _difference_operator()
    return (
        np.eye(SECTION_COUNT, dtype=np.float64)
        + SMOOTHNESS_LAMBDA
        * (difference.T @ difference)
    )


def _constraint_matrix(
    constraints: tuple[tuple[int, float], ...],
) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.zeros(
        (len(constraints), SECTION_COUNT),
        dtype=np.float64,
    )
    values = np.zeros(len(constraints), dtype=np.float64)
    for row, (section_index, target_ratio) in enumerate(constraints):
        matrix[row, section_index] = 1.0
        values[row] = target_ratio
    return matrix, values


def _constraints_consistent(
    constraints: tuple[tuple[int, float], ...],
) -> tuple[bool, int, int]:
    matrix, values = _constraint_matrix(constraints)
    rank_c = int(np.linalg.matrix_rank(matrix))
    augmented = np.column_stack((matrix, values))
    rank_augmented = int(np.linalg.matrix_rank(augmented))
    return rank_c == rank_augmented, rank_c, rank_augmented


def _solve_equilibrium(
    constraints: tuple[tuple[int, float], ...],
) -> np.ndarray:
    consistent, _, _ = _constraints_consistent(constraints)
    if not consistent:
        raise ValueError("TASK_CONFLICT")

    hessian = _hessian()
    matrix, values = _constraint_matrix(constraints)
    count = len(constraints)
    kkt = np.zeros(
        (
            SECTION_COUNT + count,
            SECTION_COUNT + count,
        ),
        dtype=np.float64,
    )
    kkt[:SECTION_COUNT, :SECTION_COUNT] = hessian
    kkt[:SECTION_COUNT, SECTION_COUNT:] = matrix.T
    kkt[SECTION_COUNT:, :SECTION_COUNT] = matrix

    rhs = np.concatenate(
        (
            np.ones(SECTION_COUNT, dtype=np.float64),
            values,
        )
    )
    solution = np.linalg.solve(kkt, rhs)
    return np.asarray(solution[:SECTION_COUNT], dtype=np.float64)


def _rest_state() -> VectorState:
    return VectorState(
        ratios=np.ones(SECTION_COUNT, dtype=np.float64),
        velocity_per_s=np.zeros(SECTION_COUNT, dtype=np.float64),
    )


def _shared_state_at_time(
    dynamics: ModalCriticallyDampedDynamics,
    *,
    q_a: np.ndarray,
    q_b: np.ndarray,
    q_ab: np.ndarray,
    time_s: float,
) -> VectorState:
    state = _rest_state()
    rest = np.ones(SECTION_COUNT, dtype=np.float64)

    first = min(time_s, GESTURE_B_ONSET_S)
    state = dynamics.advance(
        state,
        target_ratios=q_a,
        duration_s=first,
    )
    if time_s <= GESTURE_B_ONSET_S:
        return state

    second_end = min(time_s, GESTURE_A_OFFSET_S)
    state = dynamics.advance(
        state,
        target_ratios=q_ab,
        duration_s=second_end - GESTURE_B_ONSET_S,
    )
    if time_s <= GESTURE_A_OFFSET_S:
        return state

    third_end = min(time_s, GESTURE_B_OFFSET_S)
    state = dynamics.advance(
        state,
        target_ratios=q_b,
        duration_s=third_end - GESTURE_A_OFFSET_S,
    )
    if time_s <= GESTURE_B_OFFSET_S:
        return state

    return dynamics.advance(
        state,
        target_ratios=rest,
        duration_s=time_s - GESTURE_B_OFFSET_S,
    )


def _single_gesture_state_at_time(
    dynamics: ModalCriticallyDampedDynamics,
    *,
    equilibrium: np.ndarray,
    onset_s: float,
    offset_s: float,
    time_s: float,
) -> VectorState:
    state = _rest_state()
    rest = np.ones(SECTION_COUNT, dtype=np.float64)
    if time_s <= onset_s:
        return state

    active_end = min(time_s, offset_s)
    state = dynamics.advance(
        state,
        target_ratios=equilibrium,
        duration_s=active_end - onset_s,
    )
    if time_s <= offset_s:
        return state

    return dynamics.advance(
        state,
        target_ratios=rest,
        duration_s=time_s - offset_s,
    )


def _null_state_at_time(
    dynamics: ModalCriticallyDampedDynamics,
    *,
    q_a: np.ndarray,
    q_b: np.ndarray,
    time_s: float,
) -> VectorState:
    state_a = _single_gesture_state_at_time(
        dynamics,
        equilibrium=q_a,
        onset_s=GESTURE_A_ONSET_S,
        offset_s=GESTURE_A_OFFSET_S,
        time_s=time_s,
    )
    state_b = _single_gesture_state_at_time(
        dynamics,
        equilibrium=q_b,
        onset_s=GESTURE_B_ONSET_S,
        offset_s=GESTURE_B_OFFSET_S,
        time_s=time_s,
    )
    return VectorState(
        ratios=(
            state_a.ratios
            + state_b.ratios
            - np.ones(SECTION_COUNT, dtype=np.float64)
        ),
        velocity_per_s=(
            state_a.velocity_per_s
            + state_b.velocity_per_s
        ),
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
                area_m2=(
                    section.area_m2
                    * float(ratios[index])
                ),
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
        magnitude = np.abs(tube.input_impedance(frequencies))
        peaks.append(
            float(
                frequencies[
                    int(np.nanargmax(magnitude))
                ]
            )
        )
    return tuple(peaks)


def _event_metrics(
    shared: VectorState,
    null: VectorState,
    scale: float,
) -> dict[str, float]:
    delta = shared.ratios - null.ratios
    return {
        "shared_null_l2": float(np.linalg.norm(delta)),
        "normalized_shared_null": float(
            np.linalg.norm(delta) / scale
        ),
        "shared_null_velocity_l2": float(
            np.linalg.norm(
                shared.velocity_per_s
                - null.velocity_per_s
            )
        ),
        "minimum_shared_ratio": float(np.min(shared.ratios)),
        "minimum_null_ratio": float(np.min(null.ratios)),
    }


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
) -> None:
    if not rows:
        return
    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)


def _initial_gates() -> dict[str, bool | None]:
    return {
        "representation_ok": None,
        "request_validation_ok": None,
        "shared_equilibrium_oracle_ok": None,
        "independent_overlay_null_falsified": None,
        "state_propagation_ok": None,
        "shared_body_transient_ok": None,
        "task_conflict_rejected": None,
        "acoustic_oracle_ok": None,
        "numerically_resolved_ok": None,
    }


def _persist_decision(
    *,
    output_dir: Path,
    decision_name: str,
    gates: dict[str, bool | None],
    diagnostics: dict[str, Any],
    started: float,
) -> dict[str, Any]:
    decision = {
        "decision": decision_name,
        "issue": 51,
        "experiment": 22,
        "research_question": (
            "whether two overlapping task-level CONSTRICT Gestures "
            "acting on one stateful reduced body falsify an "
            "independent-state superposition null"
        ),
        "claim_scope": (
            "10-section reduced fixture; not natural coarticulation, "
            "biological articulator competition, general Task Dynamics, "
            "muscle actuation, FEM/XPBD/FSI, or production API"
        ),
        **gates,
        **diagnostics,
        "parameters": {
            "tract_length_m": TRACT_LENGTH_M,
            "section_count": SECTION_COUNT,
            "rest_area_m2": REST_AREA_M2,
            "smoothness_lambda": SMOOTHNESS_LAMBDA,
            "omega_per_s": OMEGA_PER_S,
            "primary_time_s": PRIMARY_TIME_S,
            "candidate_grid_step_hz": CANDIDATE_GRID_STEP_HZ,
            "reference_grid_step_hz": REFERENCE_GRID_STEP_HZ,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "elapsed_s": time.perf_counter() - started,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(
            decision,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return decision


def _fail(
    *,
    output_dir: Path,
    failure: str,
    gates: dict[str, bool | None],
    diagnostics: dict[str, Any],
    started: float,
) -> dict[str, Any]:
    return _persist_decision(
        output_dir=output_dir,
        decision_name=failure,
        gates=gates,
        diagnostics=diagnostics,
        started=started,
    )


def run(output_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename in ARTIFACT_NAMES:
        path = output_dir / filename
        if path.exists():
            path.unlink()

    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    gates = _initial_gates()
    diagnostics: dict[str, Any] = {
        "oracle_version": oracle["oracle_version"],
    }

    creature = _creature()
    morphology = _prepared(creature)
    validator = Tract1DRealizer()

    gesture_a = _gesture_a()
    gesture_b = _gesture_b()
    conflict_gesture = _conflicting_gesture()

    forbidden_terms = (
        "section_index",
        "hessian",
        "eigen",
        "modal",
        "velocity",
        "area_vector",
        "resonance",
        "waveform",
    )
    gesture_payloads = {
        "a": _gesture_payload(gesture_a),
        "b": _gesture_payload(gesture_b),
    }
    representation_ok = all(
        not any(
            term in json.dumps(payload, sort_keys=True).lower()
            for term in forbidden_terms
        )
        for payload in gesture_payloads.values()
    )
    gates["representation_ok"] = representation_ok
    diagnostics["gesture_sha256"] = {
        name: _sha256(payload)
        for name, payload in gesture_payloads.items()
    }
    if not representation_ok:
        return _fail(
            output_dir=output_dir,
            failure="REPRESENTATION_LEAK",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    score_a = GestureScore((gesture_a,))
    score_b = GestureScore((gesture_b,))
    score_conflict = GestureScore((conflict_gesture,))
    validations = (
        validator.realize_snapshot(
            morphology,
            score_a,
            (GESTURE_A_ONSET_S + GESTURE_A_OFFSET_S) / 2.0,
        ),
        validator.realize_snapshot(
            morphology,
            score_b,
            (GESTURE_B_ONSET_S + GESTURE_B_OFFSET_S) / 2.0,
        ),
        validator.realize_snapshot(
            morphology,
            score_conflict,
            (GESTURE_B_ONSET_S + GESTURE_A_OFFSET_S) / 2.0,
        ),
    )
    request_validation_ok = all(
        item.feasibility.status is FeasibilityStatus.FEASIBLE
        and item.state is not None
        for item in validations
    )
    request_validation_ok = (
        request_validation_ok
        and morphology.rest_state.section_index_at(
            GESTURE_A_LOCATION
        )
        == GESTURE_A_SECTION
        and morphology.rest_state.section_index_at(
            GESTURE_B_LOCATION
        )
        == GESTURE_B_SECTION
    )

    constraints_a = (
        (
            GESTURE_A_SECTION,
            GESTURE_A_AREA_M2 / REST_AREA_M2,
        ),
    )
    constraints_b = (
        (
            GESTURE_B_SECTION,
            GESTURE_B_AREA_M2 / REST_AREA_M2,
        ),
    )
    constraints_ab = constraints_a + constraints_b
    compatible, rank_c, rank_augmented = _constraints_consistent(
        constraints_ab
    )
    request_validation_ok = (
        request_validation_ok
        and compatible
        and rank_c == int(
            oracle["constraint_consistency"]["compatible_rank_c"]
        )
        and rank_augmented
        == int(
            oracle["constraint_consistency"][
                "compatible_rank_augmented"
            ]
        )
    )
    gates["request_validation_ok"] = request_validation_ok
    if not request_validation_ok:
        return _fail(
            output_dir=output_dir,
            failure="TASK_REQUEST_INVALID",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    q_a = _solve_equilibrium(constraints_a)
    q_b = _solve_equilibrium(constraints_b)
    q_ab = _solve_equilibrium(constraints_ab)
    rest = np.ones(SECTION_COUNT, dtype=np.float64)
    q_overlay = q_a + q_b - rest

    oracle_eq = oracle["equilibria"]
    equilibrium_pairs = {
        "a": (q_a, np.asarray(oracle_eq["a"], dtype=np.float64)),
        "b": (q_b, np.asarray(oracle_eq["b"], dtype=np.float64)),
        "shared_ab": (
            q_ab,
            np.asarray(oracle_eq["shared_ab"], dtype=np.float64),
        ),
        "independent_overlay_ab": (
            q_overlay,
            np.asarray(
                oracle_eq["independent_overlay_ab"],
                dtype=np.float64,
            ),
        ),
    }
    equilibrium_rows: list[dict[str, Any]] = []
    max_equilibrium_error = 0.0
    for name, (candidate, reference) in equilibrium_pairs.items():
        for index in range(SECTION_COUNT):
            error = abs(float(candidate[index] - reference[index]))
            max_equilibrium_error = max(
                max_equilibrium_error,
                error,
            )
            equilibrium_rows.append(
                {
                    "condition": name,
                    "section_index": index,
                    "candidate_ratio": float(candidate[index]),
                    "wolfram_ratio": float(reference[index]),
                    "abs_error": error,
                }
            )
    _write_csv(
        output_dir / "equilibrium_states.csv",
        equilibrium_rows,
    )

    shared_task_residuals = np.asarray(
        [
            q_ab[GESTURE_A_SECTION]
            - GESTURE_A_AREA_M2 / REST_AREA_M2,
            q_ab[GESTURE_B_SECTION]
            - GESTURE_B_AREA_M2 / REST_AREA_M2,
        ],
        dtype=np.float64,
    )
    overlay_task_residuals = np.asarray(
        [
            q_overlay[GESTURE_A_SECTION]
            - GESTURE_A_AREA_M2 / REST_AREA_M2,
            q_overlay[GESTURE_B_SECTION]
            - GESTURE_B_AREA_M2 / REST_AREA_M2,
        ],
        dtype=np.float64,
    )
    oracle_shared_residuals = np.asarray(
        oracle_eq["shared_task_residuals"],
        dtype=np.float64,
    )
    oracle_overlay_residuals = np.asarray(
        oracle_eq["overlay_task_residuals"],
        dtype=np.float64,
    )
    max_task_residual = float(
        np.max(np.abs(shared_task_residuals))
    )
    residual_oracle_error = float(
        max(
            np.max(
                np.abs(
                    shared_task_residuals
                    - oracle_shared_residuals
                )
            ),
            np.max(
                np.abs(
                    overlay_task_residuals
                    - oracle_overlay_residuals
                )
            ),
        )
    )
    shared_equilibrium_oracle_ok = (
        max_equilibrium_error <= EQUILIBRIUM_TOLERANCE
        and max_task_residual <= TASK_RESIDUAL_TOLERANCE
        and residual_oracle_error <= EQUILIBRIUM_TOLERANCE
    )
    gates["shared_equilibrium_oracle_ok"] = (
        shared_equilibrium_oracle_ok
    )
    diagnostics["max_equilibrium_oracle_error"] = (
        max_equilibrium_error
    )
    diagnostics["max_shared_task_residual"] = max_task_residual
    if not shared_equilibrium_oracle_ok:
        return _fail(
            output_dir=output_dir,
            failure="SHARED_EQUILIBRIUM_ORACLE_MISMATCH",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    scale = float(np.linalg.norm(q_ab - rest))
    equilibrium_l2 = float(np.linalg.norm(q_ab - q_overlay))
    normalized_nonadditivity = equilibrium_l2 / scale
    nonadditivity_oracle_error = abs(
        normalized_nonadditivity
        - float(oracle_eq["normalized_nonadditivity"])
    )
    equilibrium_l2_oracle_error = abs(
        equilibrium_l2
        - float(oracle_eq["shared_overlay_l2"])
    )
    independent_overlay_null_falsified = (
        normalized_nonadditivity > NONADDITIVITY_MIN
        and equilibrium_l2 > EQUILIBRIUM_L2_MIN
        and nonadditivity_oracle_error <= ORACLE_TOLERANCE
        and equilibrium_l2_oracle_error <= ORACLE_TOLERANCE
        and max_task_residual <= TASK_RESIDUAL_TOLERANCE
        and float(np.max(np.abs(overlay_task_residuals)))
        > 1.0e-3
    )
    gates["independent_overlay_null_falsified"] = (
        independent_overlay_null_falsified
    )
    _write_csv(
        output_dir / "equilibrium_effects.csv",
        [
            {
                "shared_overlay_l2": equilibrium_l2,
                "wolfram_shared_overlay_l2": float(
                    oracle_eq["shared_overlay_l2"]
                ),
                "normalized_nonadditivity": normalized_nonadditivity,
                "wolfram_normalized_nonadditivity": float(
                    oracle_eq["normalized_nonadditivity"]
                ),
                "minimum_shared_ratio": float(np.min(q_ab)),
                "minimum_overlay_ratio": float(np.min(q_overlay)),
            }
        ],
    )
    _write_csv(
        output_dir / "task_residuals.csv",
        [
            {
                "condition": "shared_ab",
                "gesture_a_residual": float(shared_task_residuals[0]),
                "gesture_b_residual": float(shared_task_residuals[1]),
            },
            {
                "condition": "independent_overlay_ab",
                "gesture_a_residual": float(overlay_task_residuals[0]),
                "gesture_b_residual": float(overlay_task_residuals[1]),
            },
        ],
    )
    if not independent_overlay_null_falsified:
        return _fail(
            output_dir=output_dir,
            failure="INDEPENDENT_OVERLAY_NULL_NOT_FALSIFIED",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    minimum_equilibrium_ratio = min(
        float(np.min(q_a)),
        float(np.min(q_b)),
        float(np.min(q_ab)),
        float(np.min(q_overlay)),
    )
    if minimum_equilibrium_ratio <= 0.0:
        gates["request_validation_ok"] = False
        diagnostics["minimum_equilibrium_ratio"] = (
            minimum_equilibrium_ratio
        )
        return _fail(
            output_dir=output_dir,
            failure="STATE_DOMAIN_VIOLATION",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    dynamics = ModalCriticallyDampedDynamics(
        _hessian(),
        OMEGA_PER_S,
    )
    s80 = _shared_state_at_time(
        dynamics,
        q_a=q_a,
        q_b=q_b,
        q_ab=q_ab,
        time_s=GESTURE_B_ONSET_S,
    )
    overlap_single = dynamics.advance(
        s80,
        target_ratios=q_ab,
        duration_s=(
            GESTURE_A_OFFSET_S
            - GESTURE_B_ONSET_S
        ),
    )
    overlap_split = dynamics.advance(
        dynamics.advance(
            s80,
            target_ratios=q_ab,
            duration_s=0.05,
        ),
        target_ratios=q_ab,
        duration_s=0.07,
    )
    split_error = max(
        float(
            np.max(
                np.abs(
                    overlap_single.ratios
                    - overlap_split.ratios
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    overlap_single.velocity_per_s
                    - overlap_split.velocity_per_s
                )
            )
        ),
    )
    switch_state = dynamics.advance(
        overlap_single,
        target_ratios=q_b,
        duration_s=0.0,
    )
    switch_jump = max(
        float(
            np.max(
                np.abs(
                    switch_state.ratios
                    - overlap_single.ratios
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    switch_state.velocity_per_s
                    - overlap_single.velocity_per_s
                )
            )
        ),
    )
    n80 = _null_state_at_time(
        dynamics,
        q_a=q_a,
        q_b=q_b,
        time_s=GESTURE_B_ONSET_S,
    )
    pre_overlap_match = max(
        float(np.max(np.abs(s80.ratios - n80.ratios))),
        float(
            np.max(
                np.abs(
                    s80.velocity_per_s
                    - n80.velocity_per_s
                )
            )
        ),
    )
    state_propagation_ok = (
        split_error <= PROPAGATION_TOLERANCE
        and switch_jump <= EVENT_CONTINUITY_TOLERANCE
        and pre_overlap_match <= ORACLE_TOLERANCE
    )
    gates["state_propagation_ok"] = state_propagation_ok
    diagnostics["max_split_propagation_error"] = split_error
    diagnostics["max_zero_duration_switch_jump"] = switch_jump
    diagnostics["pre_overlap_shared_null_error"] = pre_overlap_match
    if not state_propagation_ok:
        return _fail(
            output_dir=output_dir,
            failure="STATE_PROPAGATION_FAILED",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    trace_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    event_times = (
        GESTURE_B_ONSET_S,
        GESTURE_A_OFFSET_S,
        GESTURE_B_OFFSET_S,
        END_TIME_S,
    )
    oracle_events = {
        round(float(row["time_s"]), 8): row
        for row in oracle["events"]
    }
    max_event_oracle_error = 0.0
    minimum_shared_trace_ratio = math.inf

    trace_count = int(round(END_TIME_S / TRACE_STEP_S))
    for step in range(trace_count + 1):
        time_s = min(step * TRACE_STEP_S, END_TIME_S)
        shared = _shared_state_at_time(
            dynamics,
            q_a=q_a,
            q_b=q_b,
            q_ab=q_ab,
            time_s=time_s,
        )
        null = _null_state_at_time(
            dynamics,
            q_a=q_a,
            q_b=q_b,
            time_s=time_s,
        )
        metrics = _event_metrics(shared, null, scale)
        minimum_shared_trace_ratio = min(
            minimum_shared_trace_ratio,
            metrics["minimum_shared_ratio"],
        )
        row: dict[str, Any] = {
            "time_s": time_s,
            **metrics,
        }
        for index in range(SECTION_COUNT):
            row[f"shared_q_{index}"] = float(shared.ratios[index])
            row[f"null_q_{index}"] = float(null.ratios[index])
        trace_rows.append(row)

    for time_s in event_times:
        shared = _shared_state_at_time(
            dynamics,
            q_a=q_a,
            q_b=q_b,
            q_ab=q_ab,
            time_s=time_s,
        )
        null = _null_state_at_time(
            dynamics,
            q_a=q_a,
            q_b=q_b,
            time_s=time_s,
        )
        metrics = _event_metrics(shared, null, scale)
        oracle_row = oracle_events[round(time_s, 8)]
        errors = [
            abs(
                metrics[key]
                - float(oracle_row[key])
            )
            for key in (
                "shared_null_l2",
                "normalized_shared_null",
                "shared_null_velocity_l2",
                "minimum_shared_ratio",
                "minimum_null_ratio",
            )
        ]
        row_error = max(errors)
        max_event_oracle_error = max(
            max_event_oracle_error,
            row_error,
        )
        event_rows.append(
            {
                "time_s": time_s,
                **metrics,
                "max_wolfram_metric_error": row_error,
            }
        )

    _write_csv(output_dir / "state_trace.csv", trace_rows)
    _write_csv(output_dir / "event_summary.csv", event_rows)

    primary_shared = _shared_state_at_time(
        dynamics,
        q_a=q_a,
        q_b=q_b,
        q_ab=q_ab,
        time_s=PRIMARY_TIME_S,
    )
    primary_null = _null_state_at_time(
        dynamics,
        q_a=q_a,
        q_b=q_b,
        time_s=PRIMARY_TIME_S,
    )
    oracle_primary = oracle["primary_200ms"]
    primary_oracle_error = max(
        float(
            np.max(
                np.abs(
                    primary_shared.ratios
                    - np.asarray(
                        oracle_primary["shared_q"],
                        dtype=np.float64,
                    )
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    primary_shared.velocity_per_s
                    - np.asarray(
                        oracle_primary["shared_qdot_per_s"],
                        dtype=np.float64,
                    )
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    primary_null.ratios
                    - np.asarray(
                        oracle_primary["null_q"],
                        dtype=np.float64,
                    )
                )
            )
        ),
        float(
            np.max(
                np.abs(
                    primary_null.velocity_per_s
                    - np.asarray(
                        oracle_primary["null_qdot_per_s"],
                        dtype=np.float64,
                    )
                )
            )
        ),
        max_event_oracle_error,
    )
    primary_metrics = _event_metrics(
        primary_shared,
        primary_null,
        scale,
    )
    shared_body_transient_ok = (
        primary_oracle_error <= ORACLE_TOLERANCE
        and primary_metrics["normalized_shared_null"]
        > TRANSIENT_NORMALIZED_MIN
        and primary_metrics["shared_null_l2"]
        > TRANSIENT_L2_MIN
        and primary_metrics["shared_null_velocity_l2"]
        > TRANSIENT_VELOCITY_L2_MIN
        and minimum_shared_trace_ratio > 0.0
    )
    gates["shared_body_transient_ok"] = shared_body_transient_ok
    diagnostics["max_transient_oracle_error"] = primary_oracle_error
    diagnostics["primary_normalized_shared_null"] = (
        primary_metrics["normalized_shared_null"]
    )
    diagnostics["primary_shared_null_l2"] = (
        primary_metrics["shared_null_l2"]
    )
    diagnostics["primary_shared_null_velocity_l2"] = (
        primary_metrics["shared_null_velocity_l2"]
    )
    if not shared_body_transient_ok:
        return _fail(
            output_dir=output_dir,
            failure="SHARED_BODY_TRANSIENT_UNRESOLVED",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    conflict_constraints = (
        (
            GESTURE_A_SECTION,
            GESTURE_A_AREA_M2 / REST_AREA_M2,
        ),
        (
            GESTURE_A_SECTION,
            GESTURE_B_AREA_M2 / REST_AREA_M2,
        ),
    )
    conflict_consistent, conflict_rank_c, conflict_rank_augmented = (
        _constraints_consistent(conflict_constraints)
    )
    oracle_conflict = oracle["constraint_consistency"]
    conflict_rejected = (
        not conflict_consistent
        and conflict_rank_c
        == int(oracle_conflict["conflict_rank_c"])
        and conflict_rank_augmented
        == int(oracle_conflict["conflict_rank_augmented"])
    )
    conflict_case = {
        "diagnostic": (
            "TASK_CONFLICT"
            if conflict_rejected
            else "CONFLICT_NOT_DETECTED"
        ),
        "rank_c": conflict_rank_c,
        "rank_augmented": conflict_rank_augmented,
        "target_gap": abs(
            GESTURE_B_AREA_M2 / REST_AREA_M2
            - GESTURE_A_AREA_M2 / REST_AREA_M2
        ),
        "dynamics_called": False,
        "acoustics_called": False,
        "last_wins_used": False,
        "averaging_used": False,
        "target_coercion_used": False,
    }
    (output_dir / "conflict_case.json").write_text(
        json.dumps(
            conflict_case,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    gates["task_conflict_rejected"] = conflict_rejected
    if not conflict_rejected:
        return _fail(
            output_dir=output_dir,
            failure="TASK_CONFLICT_NOT_REJECTED",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    rest_geometry = morphology.rest_state
    primary_states = {
        "shared": primary_shared.ratios,
        "null": primary_null.ratios,
    }
    oracle_acoustic = oracle["primary_acoustic"]
    oracle_roots = {
        "shared": tuple(
            float(value)
            for value in oracle_acoustic["shared_resonances_hz"]
        ),
        "null": tuple(
            float(value)
            for value in oracle_acoustic["null_resonances_hz"]
        ),
    }
    candidate_roots: dict[str, tuple[float, ...]] = {}
    reference_roots: dict[str, tuple[float, ...]] = {}
    resonance_rows: list[dict[str, Any]] = []
    max_candidate_acoustic_error = 0.0
    max_reference_acoustic_error = 0.0

    for condition, ratios in primary_states.items():
        geometry = _geometry_from_ratios(
            rest_geometry,
            ratios,
        )
        candidate = _measure_resonances(
            geometry,
            CANDIDATE_GRID_STEP_HZ,
        )
        reference = _measure_resonances(
            geometry,
            REFERENCE_GRID_STEP_HZ,
        )
        candidate_roots[condition] = candidate
        reference_roots[condition] = reference
        for mode, oracle_root in enumerate(
            oracle_roots[condition],
            start=1,
        ):
            candidate_error = abs(
                candidate[mode - 1] - oracle_root
            )
            reference_error = abs(
                reference[mode - 1] - oracle_root
            )
            max_candidate_acoustic_error = max(
                max_candidate_acoustic_error,
                candidate_error,
            )
            max_reference_acoustic_error = max(
                max_reference_acoustic_error,
                reference_error,
            )
            resonance_rows.append(
                {
                    "condition": condition,
                    "mode": mode,
                    "candidate_hz": candidate[mode - 1],
                    "reference_hz": reference[mode - 1],
                    "wolfram_hz": oracle_root,
                    "candidate_abs_error_hz": candidate_error,
                    "reference_abs_error_hz": reference_error,
                }
            )

    _write_csv(output_dir / "resonances.csv", resonance_rows)
    acoustic_oracle_ok = (
        max_candidate_acoustic_error
        <= FREQUENCY_ORACLE_TOLERANCE_HZ
        and max_reference_acoustic_error
        <= REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ
    )
    gates["acoustic_oracle_ok"] = acoustic_oracle_ok
    diagnostics["max_candidate_acoustic_oracle_error_hz"] = (
        max_candidate_acoustic_error
    )
    diagnostics["max_reference_acoustic_oracle_error_hz"] = (
        max_reference_acoustic_error
    )
    if not acoustic_oracle_ok:
        return _fail(
            output_dir=output_dir,
            failure="ACOUSTIC_ORACLE_MISMATCH",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    acoustic_rows: list[dict[str, Any]] = []
    numerically_resolved_ok = True
    minimum_effect_to_floor = math.inf
    oracle_shifts = tuple(
        float(value)
        for value in oracle_acoustic["shared_minus_null_hz"]
    )
    for mode in range(3):
        candidate_effect = (
            candidate_roots["shared"][mode]
            - candidate_roots["null"][mode]
        )
        reference_effect = (
            reference_roots["shared"][mode]
            - reference_roots["null"][mode]
        )
        local_floor = max(
            CANDIDATE_GRID_STEP_HZ,
            abs(
                candidate_roots["shared"][mode]
                - reference_roots["shared"][mode]
            ),
            abs(
                candidate_roots["null"][mode]
                - reference_roots["null"][mode]
            ),
        )
        ratio = abs(candidate_effect) / local_floor
        minimum_effect_to_floor = min(
            minimum_effect_to_floor,
            ratio,
        )
        sign_ok = (
            math.copysign(1.0, candidate_effect)
            == math.copysign(1.0, oracle_shifts[mode])
        )
        numerically_resolved_ok = (
            numerically_resolved_ok
            and sign_ok
            and ratio > DISCRIMINATION_MARGIN
        )
        acoustic_rows.append(
            {
                "mode": mode + 1,
                "candidate_effect_hz": candidate_effect,
                "reference_effect_hz": reference_effect,
                "wolfram_effect_hz": oracle_shifts[mode],
                "numerical_floor_hz": local_floor,
                "effect_to_floor": ratio,
                "sign_ok": sign_ok,
            }
        )

    _write_csv(
        output_dir / "acoustic_effects.csv",
        acoustic_rows,
    )
    gates["numerically_resolved_ok"] = numerically_resolved_ok
    diagnostics["minimum_acoustic_effect_to_floor"] = (
        minimum_effect_to_floor
    )
    if not numerically_resolved_ok:
        return _fail(
            output_dir=output_dir,
            failure="NUMERICALLY_UNRESOLVED",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    return _persist_decision(
        output_dir=output_dir,
        decision_name=SUPPORT_DECISION,
        gates=gates,
        diagnostics=diagnostics,
        started=started,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiment-022-output"),
    )
    args = parser.parse_args()
    decision = run(args.output_dir)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0 if decision["decision"] == SUPPORT_DECISION else 1


if __name__ == "__main__":
    raise SystemExit(main())
