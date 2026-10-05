"""Experiment 021: material-conditioned multi-mode transient realization."""

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
STIFF_SECTION_INDEX = 5

OMEGA_PER_S = 25.0
DURATIONS_S = (0.04, 0.08, 0.12, 0.20, 0.32)
PRIMARY_DURATION_S = 0.12
TRACE_STEP_S = 0.01

MATERIALS = {
    "baseline": 1.0,
    "stiff": 4.0,
}

CANDIDATE_GRID_STEP_HZ = 0.05
REFERENCE_GRID_STEP_HZ = 0.01
MODE_WINDOWS_HZ = (
    (360.0, 510.0),
    (1520.0, 1760.0),
    (2170.0, 2510.0),
)

EQUILIBRIUM_TOLERANCE = 1.0e-10
ORACLE_TOLERANCE = 1.0e-11
PROPAGATION_TOLERANCE = 1.0e-11
EVENT_CONTINUITY_TOLERANCE = 1.0e-12
SCALAR_PATH_TOLERANCE = 1.0e-12
MULTIMODE_EFFECT_MIN = 0.05
MATERIAL_EFFECT_MIN = 0.03
FREQUENCY_ORACLE_TOLERANCE_HZ = 0.05
REFERENCE_FREQUENCY_ORACLE_TOLERANCE_HZ = 0.01
DISCRIMINATION_MARGIN = 5.0

SUPPORT_DECISION = "SUPPORT_MATERIAL_CONDITIONED_MULTIMODE_TRANSIENT"
ORACLE_PATH = (
    Path(__file__).with_name("wolfram")
    / "multimode_transient_oracle.json"
)

ARTIFACT_NAMES = (
    "modal_spectrum.csv",
    "duration_summary.csv",
    "state_trace.csv",
    "physical_effects.csv",
    "resonances.csv",
    "acoustic_effects.csv",
    "decision.json",
)


@dataclass(frozen=True, slots=True)
class ScalarState:
    activation: float
    velocity_per_s: float


@dataclass(frozen=True, slots=True)
class VectorState:
    ratios: np.ndarray
    velocity_per_s: np.ndarray


class ScalarCriticallyDampedDynamics:
    def __init__(self, omega_per_s: float) -> None:
        if not math.isfinite(omega_per_s) or omega_per_s <= 0.0:
            raise ValueError("omega_per_s must be finite and > 0")
        self.omega_per_s = omega_per_s

    def advance(
        self,
        state: ScalarState,
        *,
        target: float,
        duration_s: float,
    ) -> ScalarState:
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
        return ScalarState(
            activation=target + error,
            velocity_per_s=velocity,
        )


class ModalCriticallyDampedDynamics:
    """Exact transition for the Experiment-021 reduced modal state."""

    def __init__(
        self,
        hessian: np.ndarray,
        omega_per_s: float,
    ) -> None:
        matrix = np.asarray(hessian, dtype=np.float64)
        if matrix.shape != (SECTION_COUNT, SECTION_COUNT):
            raise ValueError("unexpected Hessian shape")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("Hessian must be finite")
        if not np.allclose(
            matrix,
            matrix.T,
            rtol=0.0,
            atol=1.0e-14,
        ):
            raise ValueError("Hessian must be symmetric")
        if not math.isfinite(omega_per_s) or omega_per_s <= 0.0:
            raise ValueError("omega_per_s must be finite and > 0")

        eigenvalues, eigenvectors = np.linalg.eigh(matrix)
        if np.any(eigenvalues <= 0.0):
            raise ValueError("Hessian must be positive definite")

        self.hessian = matrix
        self.eigenvalues = eigenvalues
        self.eigenvectors = eigenvectors
        self.modal_rates_per_s = (
            omega_per_s * np.sqrt(eigenvalues)
        )

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
        velocity = np.asarray(
            state.velocity_per_s,
            dtype=np.float64,
        )
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
        name="g1c-material-conditioned-multimode-body",
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
            source="experiment-021",
            model=(
                "uniform-rest-tract-with-experiment-local-"
                "material-conditioned-multimode-dynamics"
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
                    TaskParameter(
                        "target_area",
                        TARGET_AREA_M2,
                        "m2",
                    ),
                ),
            ),
        )
    )


def _score_payload(
    score: GestureScore,
) -> dict[str, Any]:
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


def _task_intent_payload(
    score: GestureScore,
) -> dict[str, Any]:
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


def _material_stiffness(
    left_relative_stiffness: float,
) -> np.ndarray:
    stiffness = np.ones(
        SECTION_COUNT,
        dtype=np.float64,
    )
    stiffness[STIFF_SECTION_INDEX] = (
        left_relative_stiffness
    )
    return stiffness


def _difference_operator() -> np.ndarray:
    difference = np.zeros(
        (SECTION_COUNT - 1, SECTION_COUNT),
        dtype=np.float64,
    )
    for index in range(SECTION_COUNT - 1):
        difference[index, index] = -1.0
        difference[index, index + 1] = 1.0
    return difference


def _material_hessian(
    stiffness: np.ndarray,
) -> np.ndarray:
    difference = _difference_operator()
    return (
        np.diag(stiffness)
        + SMOOTHNESS_LAMBDA
        * (difference.T @ difference)
    )


def _solve_equilibrium_ratios(
    stiffness: np.ndarray,
) -> np.ndarray:
    hessian = _material_hessian(stiffness)
    target_vector = np.zeros(
        SECTION_COUNT,
        dtype=np.float64,
    )
    target_vector[TARGET_SECTION_INDEX] = 1.0

    kkt = np.zeros(
        (SECTION_COUNT + 1, SECTION_COUNT + 1),
        dtype=np.float64,
    )
    kkt[:SECTION_COUNT, :SECTION_COUNT] = hessian
    kkt[:SECTION_COUNT, SECTION_COUNT] = (
        target_vector
    )
    kkt[SECTION_COUNT, :SECTION_COUNT] = (
        target_vector
    )

    target_ratio = TARGET_AREA_M2 / REST_AREA_M2
    rhs = np.concatenate(
        (
            stiffness,
            np.array(
                [target_ratio],
                dtype=np.float64,
            ),
        )
    )
    solution = np.linalg.solve(kkt, rhs)
    return np.asarray(
        solution[:SECTION_COUNT],
        dtype=np.float64,
    )


def _r2_ratios(
    equilibrium_ratios: np.ndarray,
    state: ScalarState,
) -> tuple[np.ndarray, np.ndarray]:
    delta = (
        equilibrium_ratios
        - np.ones(SECTION_COUNT, dtype=np.float64)
    )
    return (
        np.ones(SECTION_COUNT, dtype=np.float64)
        + state.activation * delta,
        state.velocity_per_s * delta,
    )


def _physical_metrics(
    equilibrium_ratios: np.ndarray,
    ratios: np.ndarray,
) -> dict[str, float]:
    rest = np.ones(
        SECTION_COUNT,
        dtype=np.float64,
    )
    delta = equilibrium_ratios - rest
    denominator = float(delta @ delta)
    if denominator <= 0.0:
        raise ValueError("equilibrium must differ from rest")
    path_progress = float(
        delta @ (ratios - rest)
        / denominator
    )
    orthogonal = (
        (ratios - rest)
        - path_progress * delta
    )
    delta_norm = float(np.linalg.norm(delta))
    return {
        "path_progress": path_progress,
        "orthogonal_fraction": float(
            np.linalg.norm(orthogonal)
            / delta_norm
        ),
        "normalized_equilibrium_error": float(
            np.linalg.norm(
                equilibrium_ratios - ratios
            )
            / delta_norm
        ),
        "target_area_abs_error_m2": abs(
            REST_AREA_M2
            * float(ratios[TARGET_SECTION_INDEX])
            - TARGET_AREA_M2
        ),
    }


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
            for index, section in enumerate(
                rest.sections
            )
        ),
    )


def _frequency_grid(
    start_hz: float,
    stop_hz: float,
    step_hz: float,
) -> np.ndarray:
    intervals = int(
        round((stop_hz - start_hz) / step_hz)
    )
    if not math.isclose(
        start_hz + intervals * step_hz,
        stop_hz,
        rel_tol=0.0,
        abs_tol=1.0e-10,
    ):
        raise ValueError(
            "frequency window must be divisible by grid step"
        )
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
        impedance = tube.input_impedance(
            frequencies
        )
        magnitude = np.abs(impedance)
        peaks.append(
            float(
                frequencies[
                    int(np.nanargmax(magnitude))
                ]
            )
        )
    return tuple(peaks)


def _oracle_duration_row(
    oracle: dict[str, Any],
    material_name: str,
    duration_s: float,
) -> dict[str, Any]:
    for row in oracle[
        "duration_observables"
    ][material_name]:
        if math.isclose(
            float(row["duration_s"]),
            duration_s,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            return dict(row)
    raise KeyError((material_name, duration_s))


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


def _strictly_decreasing(
    values: list[float],
) -> bool:
    return all(
        values[index + 1] < values[index]
        for index in range(len(values) - 1)
    )


def _initial_gates() -> dict[str, bool | None]:
    return {
        "representation_ok": None,
        "request_validation_ok": None,
        "equilibrium_regression_ok": None,
        "multimode_oracle_ok": None,
        "state_propagation_ok": None,
        "multimode_effect_ok": None,
        "material_transient_effect_ok": None,
        "acoustic_oracle_ok": None,
        "numerically_resolved_ok": None,
    }



def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable"
    )


def _persist_decision(
    *,
    output_dir: Path,
    decision_name: str,
    gates: dict[str, bool | None],
    diagnostics: dict[str, Any],
    started: float,
) -> dict[str, Any]:
    decision: dict[str, Any] = {
        "decision": decision_name,
        "issue": 49,
        "experiment": 21,
        "research_question": (
            "whether an experiment-local material-conditioned "
            "multi-mode transient falsifies the scalar-path null "
            "under one unchanged CONSTRICT task"
        ),
        "claim_scope": (
            "10-section reduced fixture; not biological tissue, "
            "general Task Dynamics, muscle actuation, FEM/XPBD/FSI, "
            "or multi-Gesture competition"
        ),
        **gates,
        **diagnostics,
        "parameters": {
            "omega_per_s": OMEGA_PER_S,
            "durations_s": list(DURATIONS_S),
            "primary_duration_s": (
                PRIMARY_DURATION_S
            ),
            "tract_length_m": TRACT_LENGTH_M,
            "section_count": SECTION_COUNT,
            "rest_area_m2": REST_AREA_M2,
            "gesture_location": GESTURE_LOCATION,
            "target_section_index": (
                TARGET_SECTION_INDEX
            ),
            "target_area_m2": TARGET_AREA_M2,
            "smoothness_lambda": (
                SMOOTHNESS_LAMBDA
            ),
            "candidate_grid_step_hz": (
                CANDIDATE_GRID_STEP_HZ
            ),
            "reference_grid_step_hz": (
                REFERENCE_GRID_STEP_HZ
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
            default=_json_default,
        )
        + "\n",
        encoding="utf-8",
    )
    return decision


def _vector_state_at_time(
    dynamics: ModalCriticallyDampedDynamics,
    *,
    equilibrium_ratios: np.ndarray,
    duration_s: float,
    time_s: float,
) -> tuple[VectorState, float]:
    initial = VectorState(
        ratios=np.ones(
            SECTION_COUNT,
            dtype=np.float64,
        ),
        velocity_per_s=np.zeros(
            SECTION_COUNT,
            dtype=np.float64,
        ),
    )
    if time_s < duration_s:
        return (
            dynamics.advance(
                initial,
                target_ratios=equilibrium_ratios,
                duration_s=time_s,
            ),
            1.0,
        )

    at_offset = dynamics.advance(
        initial,
        target_ratios=equilibrium_ratios,
        duration_s=duration_s,
    )
    return (
        dynamics.advance(
            at_offset,
            target_ratios=np.ones(
                SECTION_COUNT,
                dtype=np.float64,
            ),
            duration_s=time_s - duration_s,
        ),
        0.0,
    )


def _scalar_state_at_time(
    dynamics: ScalarCriticallyDampedDynamics,
    *,
    duration_s: float,
    time_s: float,
) -> tuple[ScalarState, float]:
    initial = ScalarState(0.0, 0.0)
    if time_s < duration_s:
        return (
            dynamics.advance(
                initial,
                target=1.0,
                duration_s=time_s,
            ),
            1.0,
        )

    at_offset = dynamics.advance(
        initial,
        target=1.0,
        duration_s=duration_s,
    )
    return (
        dynamics.advance(
            at_offset,
            target=0.0,
            duration_s=time_s - duration_s,
        ),
        0.0,
    )


def run(output_dir: Path) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )
    for filename in ARTIFACT_NAMES:
        path = output_dir / filename
        if path.exists():
            path.unlink()

    oracle = json.loads(
        ORACLE_PATH.read_text(
            encoding="utf-8"
        )
    )
    gates = _initial_gates()
    diagnostics: dict[str, Any] = {
        "oracle_version": oracle[
            "oracle_version"
        ],
    }

    creature = _creature()
    morphology = _prepared(creature)
    validator = Tract1DRealizer()

    task_intent_hashes: set[str] = set()
    full_score_hashes: dict[str, str] = {}
    request_validation_ok = True
    representation_ok = True
    forbidden_representation_terms = (
        "hessian",
        "eigen",
        "modal",
        "velocity",
        "area_vector",
        "resonance",
        "waveform",
    )

    for duration_s in DURATIONS_S:
        score = _score(duration_s)
        task_payload = _task_intent_payload(
            score
        )
        task_intent_hashes.add(
            _sha256(task_payload)
        )
        full_score_hashes[
            f"{duration_s:.2f}"
        ] = _sha256(
            _score_payload(score)
        )
        serialized_task = json.dumps(
            task_payload,
            sort_keys=True,
        ).lower()
        representation_ok = (
            representation_ok
            and not any(
                term in serialized_task
                for term
                in forbidden_representation_terms
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

    representation_ok = (
        representation_ok
        and len(task_intent_hashes) == 1
    )
    gates["representation_ok"] = (
        representation_ok
    )
    diagnostics[
        "task_intent_sha256"
    ] = (
        next(iter(task_intent_hashes))
        if task_intent_hashes
        else None
    )
    diagnostics[
        "full_score_sha256_by_duration"
    ] = full_score_hashes

    if not representation_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name="REPRESENTATION_LEAK",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    gates["request_validation_ok"] = (
        request_validation_ok
    )
    if not request_validation_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name="TASK_REQUEST_INVALID",
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    material_data: dict[
        str,
        dict[str, Any],
    ] = {}
    modal_rows: list[
        dict[str, Any]
    ] = []
    max_equilibrium_error = 0.0
    equilibrium_regression_ok = True

    for material_name, stiff_value in (
        MATERIALS.items()
    ):
        stiffness = _material_stiffness(
            stiff_value
        )
        hessian = _material_hessian(
            stiffness
        )
        equilibrium = (
            _solve_equilibrium_ratios(
                stiffness
            )
        )
        oracle_material = oracle[
            "materials"
        ][material_name]
        oracle_equilibrium = np.asarray(
            oracle_material[
                "equilibrium_ratios"
            ],
            dtype=np.float64,
        )
        equilibrium_error = float(
            np.max(
                np.abs(
                    equilibrium
                    - oracle_equilibrium
                )
            )
        )
        max_equilibrium_error = max(
            max_equilibrium_error,
            equilibrium_error,
        )
        target_residual = abs(
            float(
                equilibrium[
                    TARGET_SECTION_INDEX
                ]
            )
            - (
                TARGET_AREA_M2
                / REST_AREA_M2
            )
        )
        equilibrium_regression_ok = (
            equilibrium_regression_ok
            and equilibrium_error
            <= EQUILIBRIUM_TOLERANCE
            and target_residual
            <= EQUILIBRIUM_TOLERANCE
        )

        dynamics = (
            ModalCriticallyDampedDynamics(
                hessian,
                OMEGA_PER_S,
            )
        )
        delta = (
            equilibrium
            - np.ones(
                SECTION_COUNT,
                dtype=np.float64,
            )
        )
        participation_abs = np.abs(
            dynamics.eigenvectors.T @ delta
        )
        oracle_eigenvalues = np.asarray(
            oracle_material[
                "hessian_eigenvalues"
            ],
            dtype=np.float64,
        )
        oracle_rates = np.asarray(
            oracle_material[
                "modal_rates_per_s"
            ],
            dtype=np.float64,
        )
        for mode_index in range(
            SECTION_COUNT
        ):
            modal_rows.append(
                {
                    "material": (
                        material_name
                    ),
                    "mode": (
                        mode_index + 1
                    ),
                    "eigenvalue": float(
                        dynamics.eigenvalues[
                            mode_index
                        ]
                    ),
                    "oracle_eigenvalue": float(
                        oracle_eigenvalues[
                            mode_index
                        ]
                    ),
                    "eigenvalue_abs_error": abs(
                        float(
                            dynamics.eigenvalues[
                                mode_index
                            ]
                        )
                        - float(
                            oracle_eigenvalues[
                                mode_index
                            ]
                        )
                    ),
                    "modal_rate_per_s": float(
                        dynamics.modal_rates_per_s[
                            mode_index
                        ]
                    ),
                    "oracle_modal_rate_per_s": float(
                        oracle_rates[
                            mode_index
                        ]
                    ),
                    "modal_rate_abs_error_per_s": abs(
                        float(
                            dynamics.modal_rates_per_s[
                                mode_index
                            ]
                        )
                        - float(
                            oracle_rates[
                                mode_index
                            ]
                        )
                    ),
                    "equilibrium_participation_abs": float(
                        participation_abs[
                            mode_index
                        ]
                    ),
                }
            )

        material_data[
            material_name
        ] = {
            "stiffness": stiffness,
            "hessian": hessian,
            "equilibrium": equilibrium,
            "dynamics": dynamics,
            "oracle_eigenvalues": (
                oracle_eigenvalues
            ),
            "oracle_rates": oracle_rates,
        }

    _write_csv(
        output_dir / "modal_spectrum.csv",
        modal_rows,
    )
    diagnostics[
        "max_equilibrium_state_abs_error"
    ] = max_equilibrium_error
    gates[
        "equilibrium_regression_ok"
    ] = equilibrium_regression_ok
    if not equilibrium_regression_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name=(
                "EQUILIBRIUM_REGRESSION_FAILED"
            ),
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    max_modal_oracle_error = 0.0
    duration_rows: list[
        dict[str, Any]
    ] = []
    primary_states: dict[
        str,
        dict[str, tuple[np.ndarray, np.ndarray]]
    ] = {}
    r3_errors_by_material: dict[
        str,
        list[float],
    ] = {}
    r3_dperp_by_material: dict[
        str,
        list[float],
    ] = {}
    scalar_dynamics = (
        ScalarCriticallyDampedDynamics(
            OMEGA_PER_S
        )
    )

    for material_name, data in (
        material_data.items()
    ):
        equilibrium = data["equilibrium"]
        dynamics = data["dynamics"]
        eigen_error = float(
            np.max(
                np.abs(
                    dynamics.eigenvalues
                    - data[
                        "oracle_eigenvalues"
                    ]
                )
            )
        )
        rate_error = float(
            np.max(
                np.abs(
                    dynamics.modal_rates_per_s
                    - data[
                        "oracle_rates"
                    ]
                )
            )
        )
        max_modal_oracle_error = max(
            max_modal_oracle_error,
            eigen_error,
            rate_error,
        )
        r3_errors_by_material[
            material_name
        ] = []
        r3_dperp_by_material[
            material_name
        ] = []

        initial_vector = VectorState(
            ratios=np.ones(
                SECTION_COUNT,
                dtype=np.float64,
            ),
            velocity_per_s=np.zeros(
                SECTION_COUNT,
                dtype=np.float64,
            ),
        )
        initial_scalar = ScalarState(
            0.0,
            0.0,
        )

        for duration_s in DURATIONS_S:
            r2_state = (
                scalar_dynamics.advance(
                    initial_scalar,
                    target=1.0,
                    duration_s=duration_s,
                )
            )
            (
                r2_ratios,
                r2_velocity,
            ) = _r2_ratios(
                equilibrium,
                r2_state,
            )
            r2_metrics = _physical_metrics(
                equilibrium,
                r2_ratios,
            )

            r3_state = dynamics.advance(
                initial_vector,
                target_ratios=equilibrium,
                duration_s=duration_s,
            )
            r3_metrics = _physical_metrics(
                equilibrium,
                r3_state.ratios,
            )
            r3_errors_by_material[
                material_name
            ].append(
                r3_metrics[
                    "normalized_equilibrium_error"
                ]
            )
            r3_dperp_by_material[
                material_name
            ].append(
                r3_metrics[
                    "orthogonal_fraction"
                ]
            )

            oracle_row = (
                _oracle_duration_row(
                    oracle,
                    material_name,
                    duration_s,
                )
            )
            local_metric_error = max(
                abs(
                    r3_metrics[key]
                    - float(
                        oracle_row[key]
                    )
                )
                for key in (
                    "path_progress",
                    "orthogonal_fraction",
                    "normalized_equilibrium_error",
                    "target_area_abs_error_m2",
                )
            )
            max_modal_oracle_error = max(
                max_modal_oracle_error,
                local_metric_error,
            )

            r2_row = {
                "material": material_name,
                "model": "R2",
                "duration_s": duration_s,
                **r2_metrics,
                "physical_l2_from_rest": float(
                    np.linalg.norm(
                        r2_ratios
                        - np.ones(
                            SECTION_COUNT
                        )
                    )
                ),
                "physical_l2_to_equilibrium": float(
                    np.linalg.norm(
                        r2_ratios
                        - equilibrium
                    )
                ),
                "r2_vs_r3_l2": float(
                    np.linalg.norm(
                        r2_ratios
                        - r3_state.ratios
                    )
                ),
            }
            r3_row = {
                "material": material_name,
                "model": "R3",
                "duration_s": duration_s,
                **r3_metrics,
                "physical_l2_from_rest": float(
                    np.linalg.norm(
                        r3_state.ratios
                        - np.ones(
                            SECTION_COUNT
                        )
                    )
                ),
                "physical_l2_to_equilibrium": float(
                    np.linalg.norm(
                        r3_state.ratios
                        - equilibrium
                    )
                ),
                "r2_vs_r3_l2": float(
                    np.linalg.norm(
                        r2_ratios
                        - r3_state.ratios
                    )
                ),
            }
            duration_rows.extend(
                (r2_row, r3_row)
            )

            if math.isclose(
                duration_s,
                PRIMARY_DURATION_S,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                primary_states[
                    material_name
                ] = {
                    "R2": (
                        r2_ratios,
                        r2_velocity,
                    ),
                    "R3": (
                        r3_state.ratios,
                        r3_state.velocity_per_s,
                    ),
                }
                primary_oracle = oracle[
                    "primary_120ms"
                ][material_name]["R3"]
                primary_q_error = float(
                    np.max(
                        np.abs(
                            r3_state.ratios
                            - np.asarray(
                                primary_oracle[
                                    "q"
                                ],
                                dtype=np.float64,
                            )
                        )
                    )
                )
                primary_v_error = float(
                    np.max(
                        np.abs(
                            r3_state.velocity_per_s
                            - np.asarray(
                                primary_oracle[
                                    "qdot_per_s"
                                ],
                                dtype=np.float64,
                            )
                        )
                    )
                )
                max_modal_oracle_error = max(
                    max_modal_oracle_error,
                    primary_q_error,
                    primary_v_error,
                )

    _write_csv(
        output_dir / "duration_summary.csv",
        duration_rows,
    )
    multimode_oracle_ok = (
        max_modal_oracle_error
        <= ORACLE_TOLERANCE
    )
    diagnostics[
        "max_multimode_oracle_abs_error"
    ] = max_modal_oracle_error
    gates[
        "multimode_oracle_ok"
    ] = multimode_oracle_ok
    if not multimode_oracle_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name=(
                "MULTIMODE_ORACLE_MISMATCH"
            ),
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    max_split_error = 0.0
    max_event_jump = 0.0
    state_propagation_ok = True

    for material_name, data in (
        material_data.items()
    ):
        equilibrium = data["equilibrium"]
        dynamics = data["dynamics"]
        initial = VectorState(
            ratios=np.ones(
                SECTION_COUNT,
                dtype=np.float64,
            ),
            velocity_per_s=np.zeros(
                SECTION_COUNT,
                dtype=np.float64,
            ),
        )
        for duration_s in DURATIONS_S:
            single = dynamics.advance(
                initial,
                target_ratios=equilibrium,
                duration_s=duration_s,
            )
            split = initial
            for _ in range(4):
                split = dynamics.advance(
                    split,
                    target_ratios=equilibrium,
                    duration_s=(
                        duration_s / 4.0
                    ),
                )
            split_error = max(
                float(
                    np.max(
                        np.abs(
                            split.ratios
                            - single.ratios
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            split.velocity_per_s
                            - single.velocity_per_s
                        )
                    )
                ),
            )
            max_split_error = max(
                max_split_error,
                split_error,
            )

            onset_plus = dynamics.advance(
                initial,
                target_ratios=equilibrium,
                duration_s=0.0,
            )
            offset_plus = dynamics.advance(
                single,
                target_ratios=np.ones(
                    SECTION_COUNT,
                    dtype=np.float64,
                ),
                duration_s=0.0,
            )
            event_jump = max(
                float(
                    np.max(
                        np.abs(
                            onset_plus.ratios
                            - initial.ratios
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            onset_plus.velocity_per_s
                            - initial.velocity_per_s
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            offset_plus.ratios
                            - single.ratios
                        )
                    )
                ),
                float(
                    np.max(
                        np.abs(
                            offset_plus.velocity_per_s
                            - single.velocity_per_s
                        )
                    )
                ),
            )
            max_event_jump = max(
                max_event_jump,
                event_jump,
            )
            state_propagation_ok = (
                state_propagation_ok
                and split_error
                <= PROPAGATION_TOLERANCE
                and event_jump
                <= EVENT_CONTINUITY_TOLERANCE
                and np.all(
                    np.isfinite(
                        single.ratios
                    )
                )
                and np.all(
                    np.isfinite(
                        single.velocity_per_s
                    )
                )
            )

    diagnostics[
        "max_split_propagation_abs_error"
    ] = max_split_error
    diagnostics[
        "max_zero_duration_event_state_jump"
    ] = max_event_jump
    gates[
        "state_propagation_ok"
    ] = state_propagation_ok
    if not state_propagation_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name=(
                "STATE_PROPAGATION_FAILED"
            ),
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    trace_rows: list[
        dict[str, Any]
    ] = []
    for material_name, data in (
        material_data.items()
    ):
        equilibrium = data["equilibrium"]
        dynamics = data["dynamics"]
        for duration_s in DURATIONS_S:
            sample_count = int(
                round(
                    duration_s
                    / TRACE_STEP_S
                )
            )
            for sample_index in range(
                sample_count + 1
            ):
                trace_time = (
                    sample_index
                    * TRACE_STEP_S
                )
                vector_state, event_target = (
                    _vector_state_at_time(
                        dynamics,
                        equilibrium_ratios=(
                            equilibrium
                        ),
                        duration_s=duration_s,
                        time_s=trace_time,
                    )
                )
                scalar_state, scalar_target = (
                    _scalar_state_at_time(
                        scalar_dynamics,
                        duration_s=duration_s,
                        time_s=trace_time,
                    )
                )
                (
                    scalar_ratios,
                    scalar_velocity,
                ) = _r2_ratios(
                    equilibrium,
                    scalar_state,
                )
                for model, ratios, velocity, target in (
                    (
                        "R2",
                        scalar_ratios,
                        scalar_velocity,
                        scalar_target,
                    ),
                    (
                        "R3",
                        vector_state.ratios,
                        vector_state.velocity_per_s,
                        event_target,
                    ),
                ):
                    for section_index in range(
                        SECTION_COUNT
                    ):
                        trace_rows.append(
                            {
                                "material": (
                                    material_name
                                ),
                                "model": model,
                                "duration_s": (
                                    duration_s
                                ),
                                "time_s": (
                                    trace_time
                                ),
                                "event_target": (
                                    target
                                ),
                                "section_index": (
                                    section_index
                                ),
                                "area_ratio": float(
                                    ratios[
                                        section_index
                                    ]
                                ),
                                "velocity_ratio_per_s": float(
                                    velocity[
                                        section_index
                                    ]
                                ),
                            }
                        )
    _write_csv(
        output_dir / "state_trace.csv",
        trace_rows,
    )

    primary_metrics: dict[
        str,
        dict[str, dict[str, float]],
    ] = {}
    physical_effect_rows: list[
        dict[str, Any]
    ] = []
    for material_name, data in (
        material_data.items()
    ):
        equilibrium = data["equilibrium"]
        primary_metrics[
            material_name
        ] = {}
        for model in ("R2", "R3"):
            ratios = primary_states[
                material_name
            ][model][0]
            metrics = _physical_metrics(
                equilibrium,
                ratios,
            )
            primary_metrics[
                material_name
            ][model] = metrics
            physical_effect_rows.append(
                {
                    "material": (
                        material_name
                    ),
                    "model": model,
                    "duration_s": (
                        PRIMARY_DURATION_S
                    ),
                    **metrics,
                    "r2_vs_r3_l2": float(
                        np.linalg.norm(
                            primary_states[
                                material_name
                            ]["R3"][0]
                            - primary_states[
                                material_name
                            ]["R2"][0]
                        )
                    ),
                }
            )

    _write_csv(
        output_dir / "physical_effects.csv",
        physical_effect_rows,
    )

    multimode_effect_ok = all(
        (
            primary_metrics[
                material_name
            ]["R2"][
                "orthogonal_fraction"
            ]
            <= SCALAR_PATH_TOLERANCE
            and primary_metrics[
                material_name
            ]["R3"][
                "orthogonal_fraction"
            ]
            > MULTIMODE_EFFECT_MIN
        )
        for material_name in MATERIALS
    )
    gates[
        "multimode_effect_ok"
    ] = multimode_effect_ok
    if not multimode_effect_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name=(
                "MULTIMODE_EFFECT_UNRESOLVED"
            ),
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    r2_material_delta = (
        primary_metrics["stiff"]["R2"][
            "normalized_equilibrium_error"
        ]
        - primary_metrics["baseline"]["R2"][
            "normalized_equilibrium_error"
        ]
    )
    r3_material_delta = (
        primary_metrics["stiff"]["R3"][
            "normalized_equilibrium_error"
        ]
        - primary_metrics["baseline"]["R3"][
            "normalized_equilibrium_error"
        ]
    )
    oracle_r3_delta = (
        float(
            oracle["primary_120ms"][
                "stiff"
            ]["R3"][
                "normalized_equilibrium_error"
            ]
        )
        - float(
            oracle["primary_120ms"][
                "baseline"
            ]["R3"][
                "normalized_equilibrium_error"
            ]
        )
    )
    secondary_duration_trends_ok = (
        all(
            _strictly_decreasing(
                r3_errors_by_material[
                    material_name
                ]
            )
            for material_name in MATERIALS
        )
        and all(
            _strictly_decreasing(
                r3_dperp_by_material[
                    material_name
                ]
            )
            for material_name in MATERIALS
        )
        and all(
            stiff_error < baseline_error
            for stiff_error, baseline_error
            in zip(
                r3_errors_by_material[
                    "stiff"
                ],
                r3_errors_by_material[
                    "baseline"
                ],
                strict=True,
            )
        )
    )
    material_transient_effect_ok = (
        abs(r2_material_delta)
        <= SCALAR_PATH_TOLERANCE
        and abs(
            r3_material_delta
            - oracle_r3_delta
        )
        <= ORACLE_TOLERANCE
        and r3_material_delta < 0.0
        and abs(r3_material_delta)
        > MATERIAL_EFFECT_MIN
    )
    diagnostics[
        "r2_primary_material_delta_normalized_error"
    ] = r2_material_delta
    diagnostics[
        "r3_primary_material_delta_normalized_error"
    ] = r3_material_delta
    diagnostics[
        "oracle_r3_primary_material_delta_normalized_error"
    ] = oracle_r3_delta
    diagnostics[
        "secondary_duration_trends_ok"
    ] = secondary_duration_trends_ok
    gates[
        "material_transient_effect_ok"
    ] = material_transient_effect_ok
    if not material_transient_effect_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name=(
                "MATERIAL_TRANSIENT_EFFECT_UNRESOLVED"
            ),
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    resonance_rows: list[
        dict[str, Any]
    ] = []
    acoustic_effect_rows: list[
        dict[str, Any]
    ] = []
    peak_data: dict[
        str,
        dict[str, dict[str, tuple[float, ...]]],
    ] = {}
    max_candidate_peak_error = 0.0
    max_reference_peak_error = 0.0
    acoustic_oracle_ok = True

    for material_name in MATERIALS:
        peak_data[
            material_name
        ] = {}
        for model in ("R2", "R3"):
            ratios = primary_states[
                material_name
            ][model][0]
            geometry = _geometry_from_ratios(
                morphology.rest_state,
                ratios,
            )
            candidate_peaks = (
                _measure_resonances(
                    geometry,
                    CANDIDATE_GRID_STEP_HZ,
                )
            )
            reference_peaks = (
                _measure_resonances(
                    geometry,
                    REFERENCE_GRID_STEP_HZ,
                )
            )
            oracle_key = (
                f"{model}_resonances_hz"
            )
            oracle_peaks = tuple(
                float(value)
                for value in oracle[
                    "primary_acoustic"
                ][material_name][oracle_key]
            )
            peak_data[
                material_name
            ][model] = {
                "candidate": candidate_peaks,
                "reference": reference_peaks,
                "oracle": oracle_peaks,
            }

            for mode, (
                candidate_hz,
                reference_hz,
                oracle_hz,
            ) in enumerate(
                zip(
                    candidate_peaks,
                    reference_peaks,
                    oracle_peaks,
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
                resonance_rows.append(
                    {
                        "material": (
                            material_name
                        ),
                        "model": model,
                        "mode": mode,
                        "candidate_hz": (
                            candidate_hz
                        ),
                        "reference_hz": (
                            reference_hz
                        ),
                        "oracle_hz": (
                            oracle_hz
                        ),
                        "candidate_abs_error_hz": (
                            candidate_error
                        ),
                        "reference_abs_error_hz": (
                            reference_error
                        ),
                    }
                )

    _write_csv(
        output_dir / "resonances.csv",
        resonance_rows,
    )
    diagnostics[
        "max_candidate_peak_error_hz"
    ] = max_candidate_peak_error
    diagnostics[
        "max_reference_peak_error_hz"
    ] = max_reference_peak_error
    gates[
        "acoustic_oracle_ok"
    ] = acoustic_oracle_ok
    if not acoustic_oracle_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name=(
                "ACOUSTIC_ORACLE_MISMATCH"
            ),
            gates=gates,
            diagnostics=diagnostics,
            started=started,
        )

    numerically_resolved_ok = True
    minimum_effect_over_floor = math.inf
    for material_name in MATERIALS:
        oracle_shifts = tuple(
            float(value)
            for value in oracle[
                "primary_acoustic"
            ][material_name][
                "R3_minus_R2_hz"
            ]
        )
        for mode_index in range(3):
            r2_candidate = peak_data[
                material_name
            ]["R2"]["candidate"][
                mode_index
            ]
            r3_candidate = peak_data[
                material_name
            ]["R3"]["candidate"][
                mode_index
            ]
            r2_reference = peak_data[
                material_name
            ]["R2"]["reference"][
                mode_index
            ]
            r3_reference = peak_data[
                material_name
            ]["R3"]["reference"][
                mode_index
            ]
            observed_shift = (
                r3_candidate - r2_candidate
            )
            oracle_shift = oracle_shifts[
                mode_index
            ]
            local_floor = max(
                CANDIDATE_GRID_STEP_HZ,
                abs(
                    r2_candidate
                    - r2_reference
                ),
                abs(
                    r3_candidate
                    - r3_reference
                ),
            )
            effect_over_floor = (
                abs(observed_shift)
                / local_floor
            )
            minimum_effect_over_floor = min(
                minimum_effect_over_floor,
                effect_over_floor,
            )
            same_sign = (
                observed_shift
                * oracle_shift
                > 0.0
            )
            numerically_resolved_ok = (
                numerically_resolved_ok
                and same_sign
                and effect_over_floor
                > DISCRIMINATION_MARGIN
            )
            acoustic_effect_rows.append(
                {
                    "material": (
                        material_name
                    ),
                    "mode": (
                        mode_index + 1
                    ),
                    "observed_r3_minus_r2_hz": (
                        observed_shift
                    ),
                    "oracle_r3_minus_r2_hz": (
                        oracle_shift
                    ),
                    "same_sign": (
                        same_sign
                    ),
                    "local_numerical_floor_hz": (
                        local_floor
                    ),
                    "effect_over_floor": (
                        effect_over_floor
                    ),
                }
            )

    _write_csv(
        output_dir / "acoustic_effects.csv",
        acoustic_effect_rows,
    )
    diagnostics[
        "minimum_acoustic_effect_over_floor"
    ] = minimum_effect_over_floor
    gates[
        "numerically_resolved_ok"
    ] = numerically_resolved_ok
    if not numerically_resolved_ok:
        return _persist_decision(
            output_dir=output_dir,
            decision_name=(
                "NUMERICALLY_UNRESOLVED"
            ),
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(
            "experiment-021-output"
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
